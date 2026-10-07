#!/usr/bin/env python3
"""
Standalone Blender scene builder for SC04 - THE FLOODED STREET.

Frames 2209-2928 at 24 fps, 1920x1080 (16:9), from 02_SCREENPLAY/SHOT_LIST.json.
Independent: builds environment, characters, props, materials, lights, camera
placeholder and render settings by itself. No other scene needs to exist.

Run under Blender:   blender -b -P build_SC04.py
Test without Blender: python3 06_ASSETS/scripts/run_build_tests.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
sys.path.insert(0, os.path.join(HERE, "..", "materials"))

import ams_assets
import ams_blender_lib as L

SUMMARY = ams_assets.build_scene("SC04")
L.save_blend_if_real(os.path.join("06_ASSETS", "blender", "scenes", "SC04.blend"))

if __name__ == "__main__":
    print("BUILT SC04:", SUMMARY)
