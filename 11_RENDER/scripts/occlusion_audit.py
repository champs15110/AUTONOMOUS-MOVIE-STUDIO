#!/usr/bin/env python3
"""
occlusion_audit - Stage 11 preview-stage audit of EVERY shot camera.

T07 camera verification proved projection/framing but never tested whether
something sits between lens and subject (SC04_SH001 hides behind street
coping, SC04_SH003 behind a stall leg - both found by preview QC raycasts).
For each shot: build the scene at the shot midpoint, raycast camera ->
sampled in-frame subject vertices, skip atmospheric fog volumes, and report
the clear-line-of-sight fraction per subject.

Writes 11_RENDER/CAMERA_OCCLUSION_AUDIT.json.
Run:  LD_LIBRARY_PATH=/tmp/glstub python3 11_RENDER/scripts/occlusion_audit.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in ("06_ASSETS/scripts", "06_ASSETS/materials", "07_ANIMATION/scripts",
          "08_CAMERA/scripts", "09_LIGHTING_VFX/scripts", "11_RENDER/scripts"):
    sys.path.insert(0, os.path.join(ROOT, p))

import bpy  # noqa: E402
from bpy_extras.object_utils import world_to_camera_view  # noqa: E402
import preview_render as PR  # noqa: E402
from datetime import datetime, timezone  # noqa: E402

OUT = os.path.join(ROOT, "11_RENDER", "CAMERA_OCCLUSION_AUDIT.json")


def audit_shot(scene_id, shot_id, sh):
    if bpy.data.objects:
        bpy.ops.wm.read_factory_settings(use_empty=True)
    PR.build(scene_id, shot_id)
    sc = bpy.context.scene
    sc.frame_set((sh["frame_in"] + sh["frame_out"]) // 2)
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    cl = cam.matrix_world.translation
    out = {}
    for tok in ("WICK", "CHILD", "SHIP"):
        objs = [o for o in bpy.data.objects
                if (o.name.startswith(f"{tok}_") or o.name == f"CHAR_{tok}")
                and o.data is not None and hasattr(o.data, "vertices")
                and not o.name.endswith(".001")]
        seen = clear = 0
        blockers = {}
        for o in objs:
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
                is_clear = False
                for _ in range(6):  # skip fog volumes
                    hit, loc, nrm, idx, hob, mmw = sc.ray_cast(dg, origin, d)
                    if not hit or hob is None:
                        is_clear = True
                        break
                    if "FOG" in hob.name or hob.name.startswith("BEAM_"):
                        origin = loc + d * 0.05
                        continue
                    if hob.name.startswith(tok) or (loc - cl).length >= length * 0.95:
                        is_clear = True
                    else:
                        blockers[hob.name] = blockers.get(hob.name, 0) + 1
                    break
                clear += is_clear
        if seen:
            out[tok] = dict(in_frame=seen,
                            clear_frac=round(clear / seen, 2),
                            blockers=blockers)
    return out


def main():
    sl = json.load(open(os.path.join(ROOT, "02_SCREENPLAY", "SHOT_LIST.json"),
                        encoding="utf-8"))
    results, defects = {}, []
    for sh in sl["shots"]:
        sid, scene = sh["shot_id"], sh["scene_id"]
        try:
            r = audit_shot(scene, sid, sh)
        except Exception as e:  # noqa: BLE001
            r = {"error": str(e)[-200:]}
        results[sid] = r
        worst = None
        for tok, v in r.items():
            if tok == "error":
                continue
            if v["in_frame"] >= 20 and v["clear_frac"] < 0.5:
                worst = (tok, v)
        if worst:
            flag = "DEFECT"
        elif "error" in r:
            flag = "ERROR"
        elif not r:
            flag = "no-in-frame-samples"  # macro/insert shots: preview QC uses fg-prop check
        else:
            flag = "ok"
        print(sid, flag, json.dumps(r) if flag in ("DEFECT", "ERROR") else
              {t: v["clear_frac"] for t, v in r.items()})
        if worst:
            defects.append(dict(shot_id=sid, scene_id=scene,
                                subject=worst[0], clear_frac=worst[1]["clear_frac"],
                                blockers=worst[1]["blockers"],
                                note="subject in frame but line of sight "
                                     "blocked - fix camera before final render"))
    json.dump(dict(schema_version=1,
                   generated=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                   method="raycast camera->in-frame subject vertices, fog "
                          "volumes skipped, clear = first hit is subject or beyond",
                   threshold_defect="clear_frac < 0.5 with >= 20 in-frame samples",
                   shots=results, defects=defects),
              open(OUT, "w"), indent=2)
    print("defects:", [d["shot_id"] for d in defects], "->", OUT)


if __name__ == "__main__":
    main()
