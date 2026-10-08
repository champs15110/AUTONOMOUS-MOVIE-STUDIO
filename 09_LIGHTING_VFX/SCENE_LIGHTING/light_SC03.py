#!/usr/bin/env python3
"""
Scene lighting + VFX: SC03 - dusk, swell.
Mood: the horizon withheld — fog holds the ship back
Key: SC03_SUN_0 (single shadow caster). World: (0.1, 0.12, 0.16) @ 0.7.
Effects: FOG_SC03.

Run under Blender:  blender -b -P light_SC03.py
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

SUMMARY = light_runner.build_scene_lighting("SC03")
L.save_blend_if_real(os.path.join("09_LIGHTING_VFX", "SCENE_LIGHTING", "SC03.blend"))

if __name__ == "__main__":
    print("LIGHTING SC03:", SUMMARY["time"], "|", SUMMARY["lights"], "lights |",
          "shadow:", SUMMARY["shadow_casters"], "| vfx:", SUMMARY["vfx"],
          "| frames", SUMMARY["frames"][0], "-", SUMMARY["frames"][1])
