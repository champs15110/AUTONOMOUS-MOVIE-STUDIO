#!/usr/bin/env python3
"""
Shot animation: SC02_SH003 (scene SC02, frames 1033-1176 @24fps).
Direction: The ship: a ponderous bob; the running light is the only urgency.

Run under Blender:  blender -b -P anim_SC02_SH003.py
Local structural test: python3 07_ANIMATION/scripts/run_anim_tests.py
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "06_ASSETS", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "06_ASSETS", "materials"))
sys.path.insert(0, os.path.join(ROOT, "07_ANIMATION", "scripts"))

import ams_blender_lib as L
import shot_runner

REC = next(s for s in json.load(
    open(os.path.join(ROOT, "02_SCREENPLAY", "SHOT_LIST.json"), encoding="utf-8"))["shots"]
    if s["shot_id"] == "SC02_SH003")

SUMMARY = shot_runner.build_shot("SC02_SH003", REC)
L.save_blend_if_real(os.path.join("07_ANIMATION", "SHOT_ANIMATION", "SC02_SH003.blend"))

if __name__ == "__main__":
    print("ANIMATED SC02_SH003:", SUMMARY["keys"], "keys over frames",
          SUMMARY["frame_start"], "-", SUMMARY["frame_end"])
