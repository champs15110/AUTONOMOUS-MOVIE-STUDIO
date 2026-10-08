"""
Camera QC harness (no Blender needed): executes every shot's camera direction
on the structural stub and CHECKS it against the authored CAMERA_PLAN:

  1. camera present          - scene.camera set for the shot
  2. lens                    - focal length equals the plan's lens_intention
  3. timing                  - every camera keyframe inside the shot's frames
  4. subject scale           - projected subject-height fraction inside the
                               authored framing window (framing/FOV check)
  5. in-frame                - subject angular offset < 90% of half vertical FOV
  6. screen direction        - frame-right . (+X sea) > 0 unless the plan
                               marks the setup reverse or an axis buffer
  7. motivated motion        - the executed move type is licensed by the
                               plan's camera_motion sentence (no un-motivated
                               moves; static means static)
  8. focus                   - DOF enabled; focus distance matches the
                               subject distance (rack pulls end on target)
  9. no clipping             - camera path >= 0.12 m from every non-subject,
                               non-light object origin
 10. readability             - static framing of a moving subject stays wide
                               enough, unless the plan stages an exit/entry

Writes 08_CAMERA/CAMERA_MASTER.json, 08_CAMERA/CAMERA_INDEX.json and
08_CAMERA/CAMERA_QC.md. VERIFIED only when all ten checks pass.
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
sys.path.insert(0, os.path.join(ROOT, "07_ANIMATION", "scripts"))
sys.path.insert(0, HERE)

import bpy  # noqa: E402
import cam_lib as CL  # noqa: E402
import cam_runner  # noqa: E402
from shot_cams import SHOT_CAMS  # noqa: E402

PLAN = {s["shot_id"]: s for s in
        json.load(open(os.path.join(ROOT, "05_STORYBOARD", "CAMERA_PLAN.json"),
                       encoding="utf-8"))["shots"]}
SHOTS = json.load(open(os.path.join(ROOT, "02_SCREENPLAY", "SHOT_LIST.json"),
                       encoding="utf-8"))
REC = {s["shot_id"]: s for s in SHOTS["shots"]}
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# plan sentence -> licensed cam_lib moves (checked in order; static is the fallback)
MOTION_LICENSE = [
    (r"whip", {"whip"}),
    (r"rack", {"rack"}),
    (r"pov then reverse", {"cut_to"}),
    (r"goes under", {"descend"}),
    (r"handheld", {"micro_drift"}),
    (r"rising track", {"crane_rise", "dolly"}),
    (r"push(-in)?\b", {"push_in", "crane_back_up", "crane_rise"}),
    (r"crane", {"crane_back_up", "crane_rise"}),
    (r"tracking", {"dolly", "crane_rise"}),
    (r"dolly", {"dolly"}),
    (r"tilt", {"tilt_to"}),
    (r"follow(s|ing)?\b", {"pan_hold", "tilt_to", "dolly", "crane_rise", "push_in"}),
]

fails = []
master, index = [], []


def all_objects():
    out = []

    def rec(c):
        for o in list(c.objects):
            out.append(o)
        for ch in list(c.children):
            rec(ch)
    rec(bpy.context.scene.collection)
    return out


def licensed_moves(text):
    import re
    t = text.lower()
    for kw, allowed in MOTION_LICENSE:
        if re.search(r"\b" + kw, t):
            return allowed, kw
    return {"hold"}, "static-fallback"


def subject_subtree(tok):
    """Exclude the subject's whole rig: macro cameras legitimately sit
    centimetres from the body the detail belongs to."""
    try:
        root = cam_runner.resolve_object(tok)
    except KeyError:
        return set()
    top = root
    while top.parent is not None:
        top = top.parent
    if top.name.startswith("CHAR_"):
        root = top
    out, stack = set(), [root]
    while stack:
        o = stack.pop()
        out.add(o.name)
        stack.extend(list(o.children))
    return out


for sid in [s["shot_id"] for s in SHOTS["shots"]]:
    f0, f1 = REC[sid]["frame_in"], REC[sid]["frame_out"]
    spec = SHOT_CAMS[sid]
    checks, summary = [], None
    try:
        bpy._reset()
        summary = cam_runner.build_shot_camera(sid, REC[sid])
        cam = bpy.context.scene.camera
        checks.append(("camera present", cam is not None))

        want_lens = int("".join(ch for ch in PLAN[sid]["lens_intention"]
                                if ch.isdigit())[:3])
        checks.append((f"lens {summary['lens']:.0f}mm == plan {want_lens}mm",
                       abs(summary["lens"] - want_lens) < 0.5))

        frames = []
        ad = getattr(cam, "_animation_data", None)
        if ad:
            for fc in ad.action.fcurves:
                for kp in fc.keyframe_points:
                    frames.append(int(round(kp.co[0])))
        checks.append((f"all {len(frames)} camera keys within {f0}-{f1}",
                       bool(frames) and all(f0 <= fr <= f1 for fr in frames)))

        lo, hi = spec["scale"]
        checks.append((f"subject scale {summary['scale_frac']:.3f} in [{lo}, {hi}]",
                       lo <= summary["scale_frac"] <= hi))

        st_pt = summary["subject_true"]
        dx, dy, dz = (st_pt[i] - summary["cam_loc_end"][i] for i in range(3))
        d = math.sqrt(dx * dx + dy * dy + dz * dz) or 1e-9
        fx, fy, fz = CL.forward(summary["cam_rot_end"])
        cosang = max(-1.0, min(1.0, (dx * fx + dy * fy + dz * fz) / d))
        ang = math.degrees(math.acos(cosang))
        half_v = math.degrees(CL.vfov(summary["lens"])) / 2
        checks.append((f"subject in frame ({ang:.1f}deg < {0.9 * half_v:.1f}deg)",
                       ang < 0.9 * half_v))

        rx, ry, _ = CL.right_vec(summary["cam_rot_end"])
        if spec.get("reverse") or spec.get("exempt"):
            checks.append(("screen direction (reverse/axis-buffer, exempt)", True))
        else:
            checks.append((f"screen direction sea-frame-right (dot {rx:+.2f})", rx > 0))

        allowed, kw = licensed_moves(PLAN[sid]["camera_motion"])
        checks.append((f"motion '{summary['motion']}' licensed by plan ('{kw}')",
                       summary["motion"] in allowed))

        if summary["motion"] == "rack":
            tgt = math.dist(summary["cam_loc_end"],
                            cam_runner.resolve_point(spec["motion"][1]))
            checks.append((f"rack focus ends at target ({summary['focus_end']:.2f}m ~ {tgt:.2f}m)",
                           abs(summary["focus_end"] - tgt) < 0.25 * tgt + 0.1))
        else:
            fd = summary["focus_end"]
            dd = summary["dist_final"]
            checks.append((f"focus {fd:.2f}m ~ subject {dd:.2f}m",
                           cam.data.dof.use_dof and abs(fd - dd) < 0.25 * dd + 0.05))

        excluded = subject_subtree(spec.get("subj", "")) | {cam.name}
        if spec.get("exclude"):
            excluded |= subject_subtree(spec["exclude"])
        clip_ok, worst = True, 9e9
        for pos in summary["path"]:
            for o in all_objects():
                if o.name in excluded or o.data is None:
                    continue
                if hasattr(o.data, "energy"):        # lights are not geometry
                    continue
                wp = CL.world_pos(o)
                dd = math.dist(pos, wp)
                worst = min(worst, dd)
                if dd < 0.12:
                    clip_ok = False
        checks.append((f"no clipping (min {worst:.2f}m to geometry)", clip_ok))

        if summary["motion"] == "hold" and not spec.get("exempt"):
            from shot_specs import SPECS
            MOVERS = {"walk", "climb", "stutter", "drop_under", "collapse",
                      "kneel_turn", "push_door", "brace", "lift_pole", "carry_pole"}
            moves = any(a[0] in MOVERS for a in SPECS[sid]["acts"])
            plan_t = PLAN[sid]["camera_motion"].lower()
            staged = any(w in plan_t for w in ("exit", "enter", "cross", "collapse",
                                               "hesitat", "rises past", "provides the motion"))
            checks.append(("readability (static framing wide enough or staged exit)",
                           (not moves) or summary["scale_frac"] <= 0.9 or staged))
        else:
            checks.append(("readability (moving camera tracks the action)", True))
    except Exception as e:  # noqa: BLE001
        checks.append((f"exception {type(e).__name__}: {e}", False))

    passed = all(ok for _, ok in checks)
    some = any(ok for _, ok in checks)
    st = "VERIFIED" if passed else ("PARTIAL" if some else "BLOCKED")
    row = {"shot_id": sid, "scene_id": REC[sid]["scene_id"], "status": st,
           "framing": {"lens_mm": summary["lens"] if summary else None,
                       "fstop": summary["fstop"] if summary else None,
                       "subject_scale_fraction": round(summary["scale_frac"], 4) if summary else None,
                       "dist_to_subject_m": round(summary["dist_final"], 3) if summary else None},
           "camera_end": {"loc": [round(v, 3) for v in summary["cam_loc_end"]] if summary else None,
                          "rot_deg": [round(math.degrees(v), 2) for v in summary["cam_rot_end"]] if summary else None},
           "motion": summary["motion"] if summary else None,
           "frames": [f0, f1], "keys": summary["keys"] if summary else 0,
           "plan": {k: PLAN[sid][k] for k in ("shot_type", "lens_intention", "camera_height",
                                              "camera_motion", "composition", "screen_direction")},
           "direction_note": spec["note"],
           "checks": [{"check": c, "passed": ok} for c, ok in checks]}
    master.append(row)
    index.append({"shot_id": sid, "scene_id": REC[sid]["scene_id"],
                  "file": f"08_CAMERA/SHOT_CAMERAS/cam_{sid}.py",
                  "blend": f"08_CAMERA/SHOT_CAMERAS/{sid}.blend",
                  "lens_mm": summary["lens"] if summary else None,
                  "motion": summary["motion"] if summary else None,
                  "frame_start": f0, "frame_end": f1, "status": st})
    for c, ok in checks:
        if not ok:
            fails.append(f"{sid}: {c}")

counts = {}
for r in master:
    counts[r["status"]] = counts.get(r["status"], 0) + 1

json.dump({"schema_version": "1.0.0", "task_id": "T07_CAMERA", "project_id": "AMS-2026-001",
           "created_utc": NOW,
           "master_axis": json.load(open(os.path.join(ROOT, "05_STORYBOARD", "CAMERA_PLAN.json"),
                                         encoding="utf-8"))["master_axis"],
           "counts": counts, "shots": master},
          open(os.path.join(ROOT, "08_CAMERA", "CAMERA_MASTER.json"), "w",
               encoding="utf-8"), indent=2, ensure_ascii=False)
json.dump({"schema_version": "1.0.0", "created_utc": NOW, "shot_count": len(index),
           "shots": index},
          open(os.path.join(ROOT, "08_CAMERA", "CAMERA_INDEX.json"), "w",
               encoding="utf-8"), indent=2, ensure_ascii=False)

# ---------------- CAMERA_QC.md ---------------- #
md = ["# CAMERA QC - NINETY-TWO TURNS", "",
      f"Generated {NOW} by 08_CAMERA/scripts/run_camera_tests.py (structural stub).",
      f"Status counts: {counts}. VERIFIED = all ten checks passed for the shot.", "",
      "## Method", "",
      "Every shot is built (scene + its animation, subjects at final pose) and its",
      "camera executed from 08_CAMERA/scripts/shot_cams.py via cam_lib primitives.",
      "Checks: camera present; lens == CAMERA_PLAN intention; all camera keys inside",
      "the shot's exact frames; projected subject-scale fraction inside the authored",
      "framing window; subject within 90% of half the vertical FOV of frame centre;",
      "frame-right dot",
      "+X (sea frame right) unless the plan marks reverse/axis-buffer; executed move",
      "licensed by the plan's motivation sentence; DOF focus matches subject distance",
      "(rack pulls end on target); camera path >= 0.12 m from non-subject geometry;",
      "static framing of moving subjects wide enough unless an exit/entry is staged.",
      "",
      "Honesty: this verifies camera LOGIC and geometry structurally. Framing taste",
      "and final composition get a visual pass on the cloud Blender layer before",
      "render, same as animation.", "",
      "## Per-shot results", "",
      "| shot | lens | move | scale frac | dist m | status |",
      "|---|---|---|---|---|---|"]
for r in master:
    fr = r["framing"]
    lens = f"{fr['lens_mm']:.0f}mm" if fr["lens_mm"] else "-"
    frac = fr["subject_scale_fraction"] if fr["subject_scale_fraction"] is not None else "-"
    dist = fr["dist_to_subject_m"] if fr["dist_to_subject_m"] is not None else "-"
    md.append(f"| {r['shot_id']} | {lens} | {r['motion']} | {frac} | {dist} | {r['status']} |")
if fails:
    md += ["", "## Failures", ""] + [f"- {f}" for f in fails]
open(os.path.join(ROOT, "08_CAMERA", "CAMERA_QC.md"), "w", encoding="utf-8").write("\n".join(md))

print(f"shots: {counts}")
print("failures:")
for f in fails:
    print("  ", f)
sys.exit(0 if not fails else 1)
