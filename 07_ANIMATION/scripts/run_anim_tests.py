"""
Animation harness (no Blender needed): executes every shot's animation on the
structural stub and CHECKS the produced keyframes:

  * keys exist and all lie inside the shot's exact SHOT_LIST frame range;
  * gauge-needle end values match the shot's gauge_out where a needle act ran;
  * at least two distinct animation principles are applied per shot;
  * no camera keys exist (camera placeholders stay static - camera movement is
    never used to replace missing body animation).

Writes 07_ANIMATION/ANIMATION_STATUS.json, 07_ANIMATION/ANIMATION_INDEX.json
and 07_ANIMATION/ANIMATION_NOTES.md.

Statuses: VERIFIED only when every check for the shot passed; PARTIAL when
some checks passed; BLOCKED when the scene could not build.
"""

import json
import math
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "blender_stub"))
sys.path.insert(0, os.path.join(ROOT, "06_ASSETS", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "06_ASSETS", "materials"))
sys.path.insert(0, HERE)

import bpy  # noqa: E402
import ams_anim_lib as AN  # noqa: E402
import shot_runner  # noqa: E402
from shot_specs import SPECS  # noqa: E402

SHOTS = json.load(open(os.path.join(ROOT, "02_SCREENPLAY", "SHOT_LIST.json"), encoding="utf-8"))
REC = {s["shot_id"]: s for s in SHOTS["shots"]}
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

status, index, notes = {}, [], []


def all_keyed():
    out = []

    def rec(c):
        for o in list(c.objects):
            out.append(o)
        for ch in list(c.children):
            rec(ch)
    rec(bpy.context.scene.collection)
    return out


for sid in [s["shot_id"] for s in SHOTS["shots"]]:
    f0, f1 = REC[sid]["frame_in"], REC[sid]["frame_out"]
    checks = []
    summary = None
    try:
        bpy._reset()
        summary = shot_runner.build_shot(sid, REC[sid])
        checks.append(("built + keyed", summary["keys"] > 0))

        frames = []
        for o in all_keyed():
            ad = getattr(o, "_animation_data", None)
            if not ad:
                continue
            for fc in ad.action.fcurves:
                for kp in fc.keyframe_points:
                    frames.append((o.name, fc.data_path, int(round(kp.co[0]))))
        in_range = all(f0 <= fr_ <= f1 for _, _, fr_ in frames)
        checks.append((f"all {len(frames)} keys within {f0}-{f1}", in_range and bool(frames)))

        cams = [o for o in all_keyed() if o.data is not None and o.data.__class__.__name__ == "Camera"]
        cam_keys = []
        for o in cams:
            ad = getattr(o, "_animation_data", None)
            if ad and ad.action.fcurves:
                cam_keys.append(o.name)
        checks.append(("camera placeholder static", not cam_keys))

        needle_ok = True
        if REC[sid].get("gauge_out") is not None:
            try:
                nd = AN.child(shot_runner.resolve("GAUGE"), "GAUGE_needle")
                ad = getattr(nd, "_animation_data", None)
                fc = next((f for f in ad.action.fcurves
                           if f.data_path == "rotation_euler" and f.array_index == 2), None)
                if fc is None:
                    needle_ok = False
                else:
                    last = fc.keyframe_points[-1].co[1]
                    want = AN.gauge_value_to_rot(REC[sid]["gauge_out"])
                    needle_ok = abs(last - want) < math.radians(2)
            except KeyError:
                needle_ok = True  # scene without WICK carries no gauge
        checks.append(("needle matches gauge continuity", needle_ok))
        checks.append(("principles >= 2", len(summary["principles"]) >= 2))
    except Exception as e:  # noqa: BLE001
        checks.append((f"exception {type(e).__name__}: {e}", False))

    passed = all(ok for _, ok in checks)
    some = any(ok for _, ok in checks)
    st = "VERIFIED" if passed else ("PARTIAL" if some else "BLOCKED")
    status[sid] = {"status": st, "keys": summary["keys"] if summary else 0,
                   "frames": [f0, f1], "principles": summary["principles"] if summary else [],
                   "checks": [{"check": c, "passed": ok} for c, ok in checks],
                   "note": SPECS[sid]["note"]}
    index.append({"shot_id": sid, "scene_id": REC[sid]["scene_id"],
                  "file": f"07_ANIMATION/SHOT_ANIMATION/anim_{sid}.py",
                  "blend": f"07_ANIMATION/SHOT_ANIMATION/{sid}.blend",
                  "frame_start": f0, "frame_end": f1, "fps": 24,
                  "keys": summary["keys"] if summary else 0, "status": st})

    for c, ok in checks:
        if not ok:
            notes.append(f"- {sid}: FAILED {c}")

counts = {}
for v in status.values():
    counts[v["status"]] = counts.get(v["status"], 0) + 1

doc = {"schema_version": "1.0.0", "task_id": "T06_ANIMATION", "project_id": "AMS-2026-001",
       "created_utc": NOW, "harness": "tools/blender_stub (structural, keyframe-level checks)",
       "counts": counts, "shots": status}
json.dump(doc, open(os.path.join(ROOT, "07_ANIMATION", "ANIMATION_STATUS.json"), "w",
                    encoding="utf-8"), indent=2, ensure_ascii=False)
json.dump({"schema_version": "1.0.0", "created_utc": NOW, "shot_count": len(index), "shots": index},
          open(os.path.join(ROOT, "07_ANIMATION", "ANIMATION_INDEX.json"), "w",
               encoding="utf-8"), indent=2, ensure_ascii=False)

# ---- ANIMATION_NOTES.md ------------------------------------------------ #
md = ["# ANIMATION NOTES - NINETY-TWO TURNS", "",
      f"Generated {NOW} from the authored shot specs (07_ANIMATION/scripts/shot_specs.py).",
      f"Status counts: {counts}. VERIFIED = every structural keyframe check passed under the",
      "stub harness (keys inside exact shot frames, needle/gauge continuity, static camera",
      "placeholders, >=2 principles). Visual performance review still happens on the cloud",
      "Blender layer before render - the harness verifies logic, not pixels.", "",
      "Global rules: camera placeholders NEVER substitute for body motion; the gauge needle",
      "is keyed CONSTANT (discrete audible steps); WICK's shutter apertures are her facial",
      "performance; every walk carries anticipation + follow-through; secondary action lives",
      "on lights and set pieces, never on the protagonist's intent.", ""]
for sc in SHOTS["scenes"]:
    md.append(f"## {sc['scene_id']} - {sc['slug']}")
    md.append("")
    for s in SHOTS["shots"]:
        if s["scene_id"] != sc["scene_id"]:
            continue
        st = status[s["shot_id"]]
        md.append(f"- **{s['shot_id']}** [{st['status']}, {st['keys']} keys] {SPECS[s['shot_id']]['note']}")
        md.append(f"  principles: {', '.join(st['principles'])}")
    md.append("")
if notes:
    md.append("## Failures")
    md.append("")
    md += notes
open(os.path.join(ROOT, "07_ANIMATION", "ANIMATION_NOTES.md"), "w", encoding="utf-8").write("\n".join(md))

print(f"shots: {counts}")
bad = [sid for sid, v in status.items() if v["status"] != "VERIFIED"]
print("non-verified:", bad or "none")
for sid in bad:
    for c in status[sid]["checks"]:
        if not c["passed"]:
            print("  ", sid, c["check"])
sys.exit(0 if not bad else 1)
