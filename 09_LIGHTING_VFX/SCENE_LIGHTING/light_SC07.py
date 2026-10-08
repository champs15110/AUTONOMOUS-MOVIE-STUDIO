#!/usr/bin/env python3
"""
Scene lighting + VFX: SC07 - gale, lee of the tower.
Mood: storm-white, near-monochrome; the lee is calm
Key: SC07_SUN_0 (single shadow caster). World: (0.08, 0.09, 0.11) @ 0.7.
Effects: RAIN_SC07, SPRAY_SC07.

Run under Blender:  blender -b -P light_SC07.py
Local structural test: python3 09_LIGHTING_VFX/scripts/run_lighting_tests.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "06_ASSETS", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "06_ASSETS", "materials"))
sys.path.insert(0, os.path.join(ROOT, "09_LIGHTING_VFX", "scripts"))

import ams_blender_lib as L
import light_runner

SUMMARY = light_runner.build_scene_lighting("SC07")
L.save_blend_if_real(os.path.join("09_LIGHTING_VFX", "SCENE_LIGHTING", "SC07.blend"))

if __name__ == "__main__":
    print("LIGHTING SC07:", SUMMARY["time"], "|", SUMMARY["lights"], "lights |",
          "shadow:", SUMMARY["shadow_casters"], "| vfx:", SUMMARY["vfx"],
          "| frames", SUMMARY["frames"][0], "-", SUMMARY["frames"][1])
