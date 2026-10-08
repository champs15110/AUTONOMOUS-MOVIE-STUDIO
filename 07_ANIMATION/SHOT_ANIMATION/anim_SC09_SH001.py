#!/usr/bin/env python3
"""
Shot animation: SC09_SH001 (scene SC09, frames 6289-6480 @24fps).
Direction: The beam sweeps black water - protected 8s hold; the sweep is the beam's, not the camera's.

Run under Blender:  blender -b -P anim_SC09_SH001.py
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
    if s["shot_id"] == "SC09_SH001")

SUMMARY = shot_runner.build_shot("SC09_SH001", REC)
L.save_blend_if_real(os.path.join("07_ANIMATION", "SHOT_ANIMATION", "SC09_SH001.blend"))

if __name__ == "__main__":
    print("ANIMATED SC09_SH001:", SUMMARY["keys"], "keys over frames",
          SUMMARY["frame_start"], "-", SUMMARY["frame_end"])
