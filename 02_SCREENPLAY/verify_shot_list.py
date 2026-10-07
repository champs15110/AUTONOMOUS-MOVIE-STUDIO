#!/usr/bin/env python3
"""
Independent verifier for the Stage 02 screenplay artefacts.

Reads ONLY the emitted files (SHOT_LIST.json / SHOT_LIST.csv) plus MASTER_CONFIG.json and
the brief - it deliberately does not import build_shot_list.py, so it checks the shipped
artefacts rather than the code that produced them.

Run:  python3 02_SCREENPLAY/verify_shot_list.py
Exit: 0 = PASS, 1 = FAIL
"""

from __future__ import annotations

import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

REQ_SHOT = ["shot_id", "scene_id", "time_in", "time_out", "duration", "action",
            "character_state", "character_position", "prop_state", "camera_intention",
            "sound", "dialogue", "continuity_notes"]
REQ_SCENE = ["scene_id", "time_in", "time_out", "duration", "location", "characters",
             "story_purpose", "emotion", "props", "environment_action", "transition"]

fails: list[str] = []


def ck(cond: bool, label: str, extra: str = "") -> None:
    print(("  OK   " if cond else "  FAIL ") + label + (f"   {extra}" if extra else ""))
    if not cond:
        fails.append(label)


def main() -> int:
    J = json.load(open(os.path.join(HERE, "SHOT_LIST.json"), encoding="utf-8"))
    R = list(csv.DictReader(open(os.path.join(HERE, "SHOT_LIST.csv"), encoding="utf-8")))
    CFG = json.load(open(os.path.join(ROOT, "MASTER_CONFIG.json"), encoding="utf-8"))
    B = json.load(open(os.path.join(ROOT, "01_DEVELOPMENT", "MASTER_FILM_BRIEF.json"),
                       encoding="utf-8"))
    sh, sc = J["shots"], J["scenes"]
    sec = sorted(sh, key=lambda s: s["time_in_seconds"])

    print("=== 1. SHOT ID UNIQUENESS ===")
    ids = [s["shot_id"] for s in sh]
    ck(len(ids) == len(set(ids)), f"{len(ids)} shot ids, all unique")
    dups = sorted({i for i in ids if ids.count(i) > 1})
    ck(not dups, "no duplicates", str(dups))
    ck(all(re.fullmatch(r"SC\d{2}_SH\d{3}", i) for i in ids), "all ids match SCnn_SHmmm")
    per: dict[str, list[int]] = {}
    for s in sh:
        per.setdefault(s["scene_id"], []).append(int(s["shot_id"][-3:]))
    ck(all(v == list(range(1, len(v) + 1)) for v in per.values()),
       "numbering contiguous from _SH001 inside every scene")
    ck(sorted(per) == [s["scene_id"] for s in sc], "shot scenes match the scene table")

    print("\n=== 2. TIMECODES: NO OVERLAPS, NO GAPS ===")
    gaps = [(a["shot_id"], b["shot_id"]) for a, b in zip(sec, sec[1:])
            if abs(a["time_out_seconds"] - b["time_in_seconds"]) > 1e-9]
    ck(not gaps, "every shot starts exactly where the previous one ends", str(gaps))
    ck(all(s["time_out_seconds"] > s["time_in_seconds"] for s in sh),
       "every shot has positive duration")
    ck(abs(sec[0]["time_in_seconds"]) < 1e-9, "film starts at 00:00.000")
    ck(abs(sec[-1]["time_out_seconds"] - B["runtime"]["target_seconds"]) < 1e-9,
       "film ends at the locked runtime", sec[-1]["time_out"])
    ck(all(abs((s["time_out_seconds"] - s["time_in_seconds"]) - s["duration"]) < 1e-9
           for s in sh), "duration == time_out - time_in for every shot")
    # scene level
    scs = sorted(sc, key=lambda s: s["time_in_seconds"])
    sgaps = [(a["scene_id"], b["scene_id"]) for a, b in zip(scs, scs[1:])
             if abs(a["time_out_seconds"] - b["time_in_seconds"]) > 1e-9]
    ck(not sgaps, "scenes contiguous across the film", str(sgaps))
    for s in sc:
        own = [x for x in sh if x["scene_id"] == s["scene_id"]]
        ck(abs(min(x["time_in_seconds"] for x in own) - s["time_in_seconds"]) < 1e-9
           and abs(max(x["time_out_seconds"] for x in own) - s["time_out_seconds"]) < 1e-9,
           f'{s["scene_id"]}: its shots exactly fill its timecode range')

    print("\n=== 3. FRAMES ===")
    ck(sec[0]["frame_in"] == 1, "first frame is 1")
    ck(sec[-1]["frame_out"] == B["runtime"]["total_frames"],
       f'last frame is {B["runtime"]["total_frames"]}')
    fb = [(a["shot_id"], b["shot_id"]) for a, b in zip(sec, sec[1:])
          if a["frame_out"] + 1 != b["frame_in"]]
    ck(not fb, "frame ranges contiguous - no gaps, no double-counted frames", str(fb))
    ck(all(s["frame_out"] - s["frame_in"] + 1 == s["frame_count"] for s in sh),
       "frame_count == frame_out - frame_in + 1")

    print("\n=== 4. RUNTIME vs TARGET ===")
    t = J["total_runtime_seconds"]
    ts = CFG["target_spec"]["duration_seconds"]
    ck(abs(t - B["runtime"]["target_seconds"]) < 1e-9, f"total runtime {t}s")
    ck(ts["min"] <= t <= ts["max"], f"inside the {ts['min']}-{ts['max']}s delivery window")
    ck(abs(t - ts["target"]) <= 5, f"within 5s of the {ts['target']}s target",
       f"delta={t - ts['target']:+.1f}s")
    ck(abs(sum(s["duration"] for s in sh) - t) < 1e-9, "shot durations sum to the runtime")
    ck(abs(sum(s["duration"] for s in sc) - t) < 1e-9, "scene durations sum to the runtime")

    print("\n=== 5. MASTER_CONFIG BOUNDS ===")
    q = CFG["scene_plan"]["target_shot_seconds"]
    oob = [s["shot_id"] for s in sh if not (q["min"] <= s["duration"] <= q["max"])]
    ck(not oob, f"every shot inside {q['min']}-{q['max']}s", str(oob))
    e = CFG["scene_plan"]["target_scene_seconds"]
    oob2 = [s["scene_id"] for s in sc if not (e["min"] <= s["duration"] <= e["max"])]
    ck(not oob2, f"every scene inside {e['min']}-{e['max']}s", str(oob2))
    n = CFG["scene_plan"]["target_scene_count"]
    ck(n["min"] <= J["scene_count"] <= n["max"],
       f'{J["scene_count"]} scenes inside {n["min"]}-{n["max"]}')
    pr = B["production_complexity"]["planned_shot_range"]
    ck(pr[0] <= J["shot_count"] <= pr[1], f'{J["shot_count"]} shots inside planned {pr}')

    print("\n=== 6. REQUIRED SHOT FIELDS ===")
    miss = [(s["shot_id"], f) for s in sh for f in REQ_SHOT if not str(s.get(f, "")).strip()]
    ck(not miss, f"all {len(REQ_SHOT)} required fields populated on all {len(sh)} shots",
       str(miss[:3]))
    ck(all(s["dialogue"] == "none" for s in sh), "zero dialogue - the film is wordless")

    print("\n=== 7. REQUIRED SCENE FIELDS ===")
    smiss = [(s["scene_id"], f) for s in sc for f in REQ_SCENE
             if not (s.get(f) if isinstance(s.get(f), list) else str(s.get(f, "")).strip())]
    ck(not smiss, f"all {len(REQ_SCENE)} required scene fields populated", str(smiss))
    ck(all(s["shot_count"] == len(s["shot_ids"]) for s in sc), "scene shot lists complete")
    ck(sum(s["shot_count"] for s in sc) == len(sh), "scene shot counts sum to total shots")

    print("\n=== 8. CONTINUITY: THE 92-TURN COUNTDOWN ===")
    ck(sh[0]["gauge_in"] is None and sh[0]["gauge_out"] is None,
       "SC01_SH001 gauge unset - the needle is still winding")
    ck(sh[1]["gauge_out"] == 92,
       f'needle settles at 92 in {sh[1]["shot_id"]} at {sh[1]["time_out"]} (hook deadline 00:08)')
    tail = sh[1:]
    ck(all(isinstance(s["gauge_out"], int) for s in tail),
       "every shot from the settle onward has an integer gauge - no gaps in the countdown")
    ck(all(isinstance(s["gauge_in"], int) for s in sh[2:]),
       "every shot after the settle shot also has an integer gauge_in")
    ck(all(a["gauge_out"] == b["gauge_in"] for a, b in zip(tail, tail[1:])),
       f"gauge continuous across all {len(tail) - 1} adjacent pairs")
    rises = [(a["shot_id"], b["shot_id"], a["gauge_out"], b["gauge_out"])
             for a, b in zip(tail, tail[1:]) if b["gauge_out"] > a["gauge_out"]]
    ck(len(rises) == 1 and rises[0][1] == "SC10_SH005",
       "the gauge rises exactly once in the film - the single turn at the end", str(rises))
    ck(J["turn_budget_summary"]["spent"] == 91, "effort spend totals 91 turns")
    ck(J["turn_budget_summary"]["at_burner"] == 1, "exactly 1 turn remains at the burner")
    zero = [s["shot_id"] for s in sh if s["gauge_out"] == 0]
    ck(zero and zero[0] == "SC08_SH006", "gauge first reaches 0 at the ignition", str(zero[:1]))
    ck(sh[-1]["gauge_out"] == 1, "film ends at gauge 1")

    print("\n=== 9. STORY CONTINUITY - CAUSE AND EFFECT ===")
    by = {s["shot_id"]: s for s in sh}
    ck("LOST" in by["SC05_SH003"]["prop_state"], "the lamp-pole is explicitly LOST in SC05_SH003")
    absent = [s["shot_id"] for s in sh
              if "SC05_SH003" < s["shot_id"] < "SC07_SH005"
              and "lamp-pole" in "; ".join(s["characters"])]
    ck(not absent, "the pole does not reappear between its loss and its recovery", str(absent))
    ck("RECOVERED" in by["SC07_SH005"]["prop_state"], "the pole is explicitly RECOVERED in SC07_SH005")
    ck("the spark" in "; ".join(by["SC05_SH005"]["characters"]),
       "the spark is introduced in SC05_SH005")
    ck("REMOVED" in by["SC08_SH002"]["prop_state"],
       "the spark leaves her chest in SC08_SH002")
    ck("socket" in by["SC08_SH004"]["prop_state"].lower(),
       "the socket is revealed in SC08_SH004")
    ck("mainspring" in "; ".join(by["SC08_SH006"]["characters"]).lower(),
       "the mainspring is installed in SC08_SH006")
    ck(by["SC10_SH005"]["camera_intention"].startswith("Macro"),
       "the closing shot is a macro, mirroring the opening")
    ck("SC01_SH001" in by["SC10_SH004"]["continuity_notes"],
       "the loop shot names the opening shot it mirrors")
    ck("THE CHILD" in "; ".join(by["SC10_SH002"]["characters"]),
       "the child appears only in SC10")
    kids = [s["shot_id"] for s in sh if "THE CHILD" in "; ".join(s["characters"])]
    ck(all(k.startswith("SC10") for k in kids), "no human appears before SC10", str(kids))

    print("\n=== 10. JSON <-> CSV PARITY ===")
    ck(len(R) == len(sh), f"CSV rows {len(R)} == JSON shots {len(sh)}")
    ck([r["shot_id"] for r in R] == ids, "CSV shot order matches JSON exactly")
    mism = [r["shot_id"] for r, s in zip(R, sh)
            if r["time_in"] != s["time_in"] or r["time_out"] != s["time_out"]
            or r["duration"] != str(s["duration"])]
    ck(not mism, "CSV timecodes and durations match JSON", str(mism))
    ck(all(r["dialogue"] == "none" for r in R), "CSV dialogue column all 'none'")
    ck(all(r[f].strip() for r in R for f in
           ["action", "character_state", "character_position", "prop_state",
            "camera_intention", "sound", "continuity_notes"]),
       "no empty narrative cells in the CSV")

    print("\n" + "=" * 60)
    if fails:
        print(f"VERIFICATION: FAIL ({len(fails)})")
        for f in fails:
            print(f"   x {f}")
        return 1
    print("VERIFICATION: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
