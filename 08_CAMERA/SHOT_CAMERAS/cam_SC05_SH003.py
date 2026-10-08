#!/usr/bin/env python3
"""
Shot camera: SC05_SH003 (scene SC05, frames 3181-3288 @24fps).
Follows the pole out of frame with a pan, then holds on the water. The loss gets one clean move, then silence.

Run under Blender:  blender -b -P cam_SC05_SH003.py
Local structural test: python3 08_CAMERA/scripts/run_camera_tests.py
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "06_ASSETS", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "06_ASSETS", "materials"))
sys.path.insert(0, os.path.join(ROOT, "07_ANIMATION", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "08_CAMERA", "scripts"))

import ams_blender_lib as L
import cam_runner

REC = next(s for s in json.load(
    open(os.path.join(ROOT, "02_SCREENPLAY", "SHOT_LIST.json"), encoding="utf-8"))["shots"]
    if s["shot_id"] == "SC05_SH003")

SUMMARY = cam_runner.build_shot_camera("SC05_SH003", REC)
L.save_blend_if_real(os.path.join("08_CAMERA", "SHOT_CAMERAS", "SC05_SH003.blend"))

if __name__ == "__main__":
    print("CAMERA SC05_SH003:", SUMMARY["lens"], "mm |", SUMMARY["motion"], "|",
          SUMMARY["keys"], "keys | frames", SUMMARY["frames"][0], "-", SUMMARY["frames"][1])
