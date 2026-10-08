#!/usr/bin/env python3
"""
Shot camera: SC06_SH004 (scene SC06, frames 4201-4344 @24fps).
Interior 18mm: she enters; tilt up the stair and keep tilting. The tower is a vertical promise.

Run under Blender:  blender -b -P cam_SC06_SH004.py
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
    if s["shot_id"] == "SC06_SH004")

SUMMARY = cam_runner.build_shot_camera("SC06_SH004", REC)
L.save_blend_if_real(os.path.join("08_CAMERA", "SHOT_CAMERAS", "SC06_SH004.blend"))

if __name__ == "__main__":
    print("CAMERA SC06_SH004:", SUMMARY["lens"], "mm |", SUMMARY["motion"], "|",
          SUMMARY["keys"], "keys | frames", SUMMARY["frames"][0], "-", SUMMARY["frames"][1])
