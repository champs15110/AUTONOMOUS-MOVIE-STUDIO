#!/usr/bin/env python3
"""
preview_render - one scene's preview under REAL Blender (bpy module, CPU).

No local GPU; the preferred JANCTION/cloud backend is not configured in this
runtime (see RENDER_ERRORS.json / ERROR_LOG ERR-0003), so the fallback
renderer of record is the pypi `bpy` module with Cycles CPU - real frames,
honestly labelled PREVIEW.

Per scene:
  1-5  pre-flight checks (scene scripts, camera, frame range, assets, files)
  6    submit preview render (Cycles CPU, 480x270, 32 samples, one frame at
       the scene's representative shot midpoint - far inside any 240-frame
       job limit)
  7-8  inspect the returned frame (pixels + occlusion-aware subject
       visibility) and record problems
  9    fix obvious technical problems (macro fstop, measured exposure
       pull-up), then re-preview exactly once after a meaningful fix

Run:  LD_LIBRARY_PATH=/tmp/glstub python3 preview_render.py --scene SC01
"""
import argparse
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for _p in ("06_ASSETS/scripts", "06_ASSETS/materials", "07_ANIMATION/scripts",
           "08_CAMERA/scripts", "09_LIGHTING_VFX/scripts"):
    sys.path.insert(0, os.path.join(ROOT, _p))

import bpy  # noqa: E402
import mathutils  # noqa: E402
import cam_runner  # noqa: E402
import light_design as LD  # noqa: E402
from bpy_extras.object_utils import world_to_camera_view  # noqa: E402

OUT = os.path.join(ROOT, "11_RENDER")
PREVIEWS = os.path.join(OUT, "PREVIEWS")

# representative shot per scene (frame midpoint rendered)
REPRESENTATIVE = {
    "SC01": "SC01_SH004", "SC02": "SC02_SH003", "SC03": "SC03_SH003",
    "SC04": "SC04_SH002", "SC05": "SC05_SH005", "SC06": "SC06_SH002",
    "SC07": "SC07_SH003", "SC08": "SC08_SH005", "SC09": "SC09_SH001",
    "SC10": "SC10_SH004",
}

SHOT_LIST = json.load(open(os.path.join(ROOT, "02_SCREENPLAY", "SHOT_LIST.json"),
                           encoding="utf-8"))
SCENES = {s["scene_id"]: s for s in SHOT_LIST["scenes"]}
SHOTS = {s["shot_id"]: s for s in SHOT_LIST["shots"]}
PLAN = json.load(open(os.path.join(ROOT, "05_STORYBOARD", "MASTER_SHOT_PLAN.json"),
                      encoding="utf-8"))
PLAN_SHOTS = {s["shot_id"]: s for s in PLAN["shots"]}
SCENE_MAN = json.load(open(os.path.join(ROOT, "06_ASSETS", "SCENE_MANIFEST.json"),
                           encoding="utf-8"))


def preflight(scene_id):
    """Checks 1-5 from the render brief. Returns (ok, details)."""
    problems = []
    shot_id = REPRESENTATIVE[scene_id]
    # 1 scene / scripts exist
    for path in (os.path.join(ROOT, "09_LIGHTING_VFX", "SCENE_LIGHTING",
                              f"light_{scene_id}.py"),
                 os.path.join(ROOT, "08_CAMERA", "SHOT_CAMERAS",
                              f"cam_{shot_id}.py")):
        if not os.path.exists(path):
            problems.append(f"missing {os.path.relpath(path, ROOT)}")
    # 2 camera exists (CAMERA_MASTER carries every shot)
    try:
        cam_master = json.load(open(os.path.join(ROOT, "08_CAMERA",
                                                 "CAMERA_MASTER.json")))
        if not any(c.get("shot_id") == shot_id for c in cam_master["shots"]):
            problems.append(f"no camera entry for {shot_id}")
    except Exception as e:  # noqa: BLE001
        problems.append(f"CAMERA_MASTER unreadable: {e}")
    # 3 frame range
    sc, sh = SCENES[scene_id], SHOTS[shot_id]
    if not (1 <= sc["frame_in"] <= sc["frame_out"] <= 7248):
        problems.append("scene frame range out of bounds")
    if not (sc["frame_in"] <= sh["frame_in"] <= sh["frame_out"] <= sc["frame_out"]):
        problems.append("shot frame range out of scene range")
    # 4 assets
    scen = next((s for s in SCENE_MAN.get("scenes", [])
                 if s.get("scene_id") == scene_id), None)
    if scen is None or not scen.get("independent"):
        problems.append("SCENE_MANIFEST has no independent scene entry")
    # 5 required files
    for path in (os.path.join(ROOT, "09_LIGHTING_VFX", "LIGHTING_PLAN.json"),
                 os.path.join(ROOT, "09_LIGHTING_VFX", "VFX_PLAN.json"),
                 os.path.join(ROOT, "06_ASSETS", "SCENE_MANIFEST.json"),
                 os.path.join(ROOT, "08_CAMERA", "CAMERA_MASTER.json"),
                 os.path.join(ROOT, "07_ANIMATION", "ANIMATION_STATUS.json"),
                 os.path.join(ROOT, "PROJECT_STATE.json")):
        if not os.path.exists(path):
            problems.append(f"missing input {os.path.relpath(path, ROOT)}")
    return (not problems, problems)


def build(scene_id, shot_id):
    rec = SHOTS[shot_id]
    cam_runner.build_shot_camera(shot_id, rec, with_anim=True)
    sc = bpy.context.scene
    inv = LD.apply_lighting(scene_id)
    sf = {s["shot_id"]: (s["frame_in"], s["frame_out"]) for s in PLAN["shots"]}
    LD.apply_vfx(scene_id, sf, (sc.frame_start, sc.frame_end))
    return inv


def char_anchor(tok):
    for nm in (f"{tok}_head", f"{tok}_torso", f"CHAR_{tok}"):
        ob = bpy.data.objects.get(nm)
        if ob is not None:
            return ob
    return None


def technical_compensation(shot_id):
    """Render-stage fixes for obvious technical problems (always recorded):
    macro shots need a smaller aperture for readable DOF; fill lights tuned
    for mid distance over-expose 10 cm ECUs - normalize against the plan's
    exposure bounds (T08 high = 60); SPOT beacons count only inside their cone."""
    adj = {}
    cam = bpy.context.scene.camera
    if cam is None:
        return adj
    anchor = char_anchor("WICK") or char_anchor("CHILD")
    if anchor is None:
        return adj
    bpy.context.view_layer.update()
    d = (cam.matrix_world.translation - anchor.matrix_world.translation).length
    if d < 0.4:
        dof = cam.data.dof
        cur = getattr(dof, "aperture_fstop", None)
        if cur is not None and cur < 8.0:
            dof.aperture_fstop = 8.0
            adj["macro_fstop"] = f"{cur:.2f} -> 8.0 (DOF unreadable at {d:.2f} m)"
    e = 0.0
    for ob in bpy.data.objects:
        if ob.data is not None and hasattr(ob.data, "energy"):
            ld = ob.data
            dl = (ob.matrix_world.translation -
                  anchor.matrix_world.translation).length
            if ld.type == "SUN":
                e = max(e, ld.energy)
            else:
                if ld.type == "SPOT":
                    to_s = (anchor.matrix_world.translation -
                            ob.matrix_world.translation).normalized()
                    axis = (ob.matrix_world.to_quaternion() @
                            mathutils.Vector((0, 0, -1))).normalized()
                    if axis.dot(to_s) < math.cos(ld.spot_size / 2):
                        continue
                e += ld.energy / max(0.5, dl) ** 2
    if e > 60.0:
        stop = max(-4.0, -math.log2(e / 60.0))
        bpy.context.scene.view_settings.exposure = stop
        adj["exposure_stops"] = round(stop, 2)
    return adj


def inspect(path):
    """Pixel stats + occlusion-aware subject visibility on the PNG."""
    from PIL import Image
    im = Image.open(path).convert("L")
    px = list(im.getdata())
    n = len(px)
    mean = sum(px) / n
    nonblack = 100.0 * sum(1 for v in px if v > 8) / n
    clipped = 100.0 * sum(1 for v in px if v > 250) / n
    edges = sum(1 for i in range(1, n) if abs(px[i] - px[i - 1]) > 12) / n

    sc = bpy.context.scene
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    cl = cam.matrix_world.translation

    def inframe_frac(ob, samples=300):
        verts = list(getattr(ob.data, "vertices", []))
        if not verts:
            return 0.0
        step = max(1, len(verts) // samples)
        mw = ob.matrix_world
        hit = tot = 0
        for v in verts[::step]:
            co = world_to_camera_view(sc, cam, mw @ v.co)
            tot += 1
            if 0.0 <= co.x <= 1.0 and 0.0 <= co.y <= 1.0 and co.z > 0:
                hit += 1
        return hit / tot if tot else 0.0

    def rig_objs(tok):
        return [o for o in bpy.data.objects
                if o.name.startswith(f"{tok}_") or o.name == f"CHAR_{tok}"]

    vis = {t: round(max([inframe_frac(o) for o in rig_objs(t)], default=0.0), 2)
           for t in ("WICK", "CHILD", "SHIP")}

    def really_visible(tok):
        """of the in-frame sampled verts (stride-sampled like rig_frac), the
        share with a clear camera ray (occlusion-aware)"""
        seen = clear = 0
        for o in rig_objs(tok):
            verts = list(getattr(o.data, "vertices", []))
            if not verts:
                continue
            step = max(1, len(verts) // 60)
            mw = o.matrix_world
            for v in verts[::step]:
                wp = mw @ v.co
                co = world_to_camera_view(sc, cam, wp)
                if not (0.0 <= co.x <= 1.0 and 0.0 <= co.y <= 1.0 and co.z > 0):
                    continue
                seen += 1
                d = wp - cl
                length = d.length
                d.normalize()
                # skip atmospheric volumes (fog boxes): they are not occluders
                origin = cl.copy()
                hob = None
                clear_ray = False
                for _ in range(6):
                    hit, loc, nrm, idx, hob, mmw = sc.ray_cast(dg, origin, d)
                    if not hit or hob is None:
                        clear_ray = True
                        break
                    if "FOG" in hob.name or hob.name.startswith("BEAM_"):
                        origin = loc + d * 0.05
                        continue
                    if hob.name.startswith(tok) or \
                            (loc - cl).length >= length * 0.95:
                        clear_ray = True
                    break
                if clear_ray:
                    clear += 1
                if seen >= 48:
                    return clear / seen
        return (clear / seen) if seen else 0.0

    vis_seen = {t: round(really_visible(t), 2) for t in vis}
    char_seen = any(f >= 0.15 for f in vis_seen.values())

    fg_subject = False
    if not char_seen:
        for o in bpy.data.objects:
            if o.data is None or not hasattr(o.data, "vertices"):
                continue
            if (o.matrix_world.translation - cl).length < 0.5 \
                    and inframe_frac(o) >= 0.1:
                fg_subject = True
                break

    problems = []
    if nonblack < 20:
        problems.append(f"near-black frame (nonblack {nonblack:.1f}%)")
    if clipped > 25:
        problems.append(f"blown frame (clipped {clipped:.1f}%)")
    if edges < 0.0005:
        problems.append("flat frame - no visible geometry edges")
    if not char_seen and not fg_subject:
        problems.append(f"no subject projects into frame: {vis_seen}")
    return dict(mean=round(mean, 1), nonblack_pct=round(nonblack, 1),
                clipped_pct=round(clipped, 2), edge_density=round(edges, 4),
                subject_in_frame=vis, subject_visible=vis_seen,
                foreground_prop_subject=fg_subject, problems=problems)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", required=True)
    ap.add_argument("--res", nargs=2, type=int, default=(480, 270))
    ap.add_argument("--spp", type=int, default=32)
    a = ap.parse_args()
    scene_id = a.scene
    shot_id = REPRESENTATIVE[scene_id]
    os.makedirs(PREVIEWS, exist_ok=True)
    status = dict(scene_id=scene_id, representative_shot=shot_id,
                  renderer="bpy " + bpy.app.version_string + " / CYCLES CPU",
                  status="PREVIEW_PENDING", submitted_utc=None,
                  rendered_utc=None, preview_file=None, checks={},
                  problems=[], qc=None, render_seconds=None)

    ok, problems = preflight(scene_id)
    status["checks"] = {"preflight": ok}
    status["problems"] += problems
    if not ok:
        status["status"] = "PREVIEW_FAILED"
        print(json.dumps(status))
        return 1

    t0 = time.time()
    build(scene_id, shot_id)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = a.spp
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = a.res
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    mid = (SHOTS[shot_id]["frame_in"] + SHOTS[shot_id]["frame_out"]) // 2
    sc.frame_set(mid)
    out_png = os.path.join(PREVIEWS, f"{scene_id}_preview.png")
    sc.render.filepath = out_png
    status["status"] = "PREVIEW_RENDERED"
    from datetime import datetime, timezone
    status["submitted_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    status["technical_adjustments"] = technical_compensation(shot_id)
    bpy.ops.render.render(write_still=True)
    status["rendered_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    status["render_seconds"] = round(time.time() - t0, 1)
    status["preview_file"] = os.path.relpath(out_png, ROOT)
    status["frame"] = mid

    qc = inspect(out_png)
    # measured per-shot exposure: extreme under-exposure is a technical fault
    # (dawn scene rendering near-black) - pull up once, then re-preview
    if qc["mean"] < 12:
        pull = min(5.0, math.log2(40.0 / max(1.0, qc["mean"])))
        sc.view_settings.exposure = sc.view_settings.exposure + pull
        status["technical_adjustments"]["exposure_pull_stops"] = round(pull, 2)
        bpy.ops.render.render(write_still=True)
        qc = inspect(out_png)
    status["qc"] = qc
    status["problems"] += qc["problems"]
    status["status"] = "PREVIEW_QC_PASS" if not status["problems"] else "PREVIEW_QC_FAIL"
    print(json.dumps(status))
    return 0 if status["status"] == "PREVIEW_QC_PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
