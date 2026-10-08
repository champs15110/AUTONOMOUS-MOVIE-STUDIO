#!/usr/bin/env python3
"""
camera_nudge - FINAL QC fix for ERR-0004: search a minimal camera nudge per
occlusion-defective shot so the subject's line of sight clears while the
framing window, screen direction and motivation stay authored.

Real-bpy evaluation via cam_runner.build_shot_camera summaries (same values
the T07 harness checks). Writes 12_QC/scripts/nudge_patches.json; the patch
is applied to shot_cams.py by apply_nudges.py, then write_cam_scripts.py +
run_camera_tests.py + occlusion_audit.py re-verify.

Run: LD_LIBRARY_PATH=/tmp/glstub python3 12_QC/scripts/camera_nudge.py
"""
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in ("06_ASSETS/scripts", "06_ASSETS/materials", "07_ANIMATION/scripts",
          "08_CAMERA/scripts", "09_LIGHTING_VFX/scripts", "11_RENDER/scripts"):
    sys.path.insert(0, os.path.join(ROOT, p))

import bpy  # noqa: E402
import mathutils  # noqa: E402
from bpy_extras.object_utils import world_to_camera_view  # noqa: E402
import cam_runner  # noqa: E402
import cam_lib as CL  # noqa: E402
import shot_cams  # noqa: E402

SHOTS = {s["shot_id"]: s for s in json.load(
    open(os.path.join(ROOT, "02_SCREENPLAY", "SHOT_LIST.json"),
         encoding="utf-8"))["shots"]}
AUD = json.load(open(os.path.join(ROOT, "11_RENDER",
                                  "CAMERA_OCCLUSION_AUDIT.json"),
                     encoding="utf-8"))
DEF = {}
for d in AUD["defects"]:
    DEF.setdefault(d["shot_id"], []).append(d["subject"])


def clear_frac(tok):
    sc = bpy.context.scene
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    cl = cam.matrix_world.translation
    seen = clear = 0
    for o in bpy.data.objects:
        if not (o.name.startswith(f"{tok}_") or o.name == f"CHAR_{tok}"):
            continue
        if o.data is None or not hasattr(o.data, "vertices") or \
                o.name.endswith(".001"):
            continue
        verts = list(o.data.vertices)
        for v in verts[::max(1, len(verts) // 24)]:
            wp = o.matrix_world @ v.co
            co = world_to_camera_view(sc, cam, wp)
            if not (0.0 <= co.x <= 1.0 and 0.0 <= co.y <= 1.0 and co.z > 0):
                continue
            seen += 1
            d = wp - cl
            length = d.length
            d.normalize()
            origin = cl.copy()
            ok = False
            for _ in range(6):
                hit, loc, nrm, idx, hob, mmw = sc.ray_cast(dg, origin, d)
                if not hit or hob is None:
                    ok = True
                    break
                if "FOG" in hob.name or hob.name.startswith("BEAM_"):
                    origin = loc + d * 0.05
                    continue
                if hob.name.startswith(tok) or \
                        (loc - cl).length >= length * 0.95:
                    ok = True
                break
            clear += ok
            if seen >= 48:
                return clear / seen
    return (clear / seen) if seen else 0.0


def candidates(sid, base):
    """ordered by perturbation size; yields patched specs"""
    if "loc" in base:
        loc = mathutils.Vector(base["loc"])
        tgt = mathutils.Vector(base["target"])
        view = (tgt - loc).normalized()
        lat = view.cross(mathutils.Vector((0, 0, 1))).normalized()
        for m in (0.2, -0.2, 0.35, -0.35, 0.5, -0.5):
            c = copy.deepcopy(base)
            c["loc"] = tuple(round(x, 2) for x in (loc + lat * m))
            yield c
        for dz in (0.25, 0.5, 0.75):
            c = copy.deepcopy(base)
            c["loc"] = (round(loc.x, 2), round(loc.y, 2), round(loc.z + dz, 2))
            yield c
        for m in (0.35, -0.35):
            c = copy.deepcopy(base)
            c["loc"] = tuple(round(x, 2) for x in (loc + lat * m))
            c["loc"] = (c["loc"][0], c["loc"][1], round(loc.z + 0.25, 2))
            yield c
    else:
        for daz in (10, -10, 20, -20, 30, -30, 45, -45):
            c = copy.deepcopy(base)
            c["az"] = base.get("az", 0) + daz
            yield c
        for dh in (0.25, 0.5):
            c = copy.deepcopy(base)
            c["h"] = base.get("h", 0) + dh
            yield c
        for daz in (20, -20, 30, -30):
            for dh in (0.25, 0.5):
                c = copy.deepcopy(base)
                c["az"] = base.get("az", 0) + daz
                c["h"] = base.get("h", 0) + dh
                yield c
        for dd in (-0.4, 0.4):
            c = copy.deepcopy(base)
            c["dist"] = base.get("dist", 2.0) + dd
            yield c


def screen_dir_ok(sid, summary, spec):
    if spec.get("reverse") or spec.get("exempt"):
        return True
    rx, ry, _ = CL.right_vec(summary["cam_rot_end"])
    return rx > 0  # frame right must be +X (sea) per master axis


patches, unfixed = {}, []
for sid in sorted(DEF):
    toks = DEF[sid]
    base = shot_cams.SHOT_CAMS[sid]
    rec = SHOTS[sid]
    chosen = None
    for cand in candidates(sid, base):
        shot_cams.SHOT_CAMS[sid] = cand
        if bpy.data.objects:
            bpy.ops.wm.read_factory_settings(use_empty=True)
        try:
            summary = cam_runner.build_shot_camera(sid, rec, with_anim=True)
        except Exception as e:  # noqa: BLE001
            print(sid, "build fail", e)
            continue
        sc = bpy.context.scene
        sc.frame_set((rec["frame_in"] + rec["frame_out"]) // 2)
        lo, hi = cand["scale"]
        if not (lo <= summary["scale_frac"] <= hi):
            continue
        if not screen_dir_ok(sid, summary, cand):
            continue
        worst = min(clear_frac(t) for t in toks)
        if worst >= 0.8:
            chosen = (cand, worst, summary["scale_frac"])
            break
    if chosen:
        patches[sid] = dict(spec=chosen[0], clear=round(chosen[1], 2),
                            scale_frac=round(chosen[2], 3))
        print(sid, "FIXED clear", chosen[1], "scale", chosen[2])
    else:
        shot_cams.SHOT_CAMS[sid] = base
        unfixed.append(sid)
        print(sid, "UNFIXED in candidate set")

json.dump(dict(patches=patches, unfixed=unfixed),
          open(os.path.join(HERE, "nudge_patches.json"), "w"), indent=2)
print("fixed", len(patches), "unfixed", unfixed)
