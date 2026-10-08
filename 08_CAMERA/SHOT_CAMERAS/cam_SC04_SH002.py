#!/usr/bin/env python3
"""
Shot camera: SC04_SH002 (scene SC04, frames 2329-2460 @24fps).
Medium at her height. Motivated instability: ONE slow 3cm drift - the effort feels unstable without fake shake.

Run under Blender:  blender -b -P cam_SC04_SH002.py
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
    if s["shot_id"] == "SC04_SH002")

SUMMARY = cam_runner.build_shot_camera("SC04_SH002", REC)
L.save_blend_if_real(os.path.join("08_CAMERA", "SHOT_CAMERAS", "SC04_SH002.blend"))

if __name__ == "__main__":
    print("CAMERA SC04_SH002:", SUMMARY["lens"], "mm |", SUMMARY["motion"], "|",
          SUMMARY["keys"], "keys | frames", SUMMARY["frames"][0], "-", SUMMARY["frames"][1])
