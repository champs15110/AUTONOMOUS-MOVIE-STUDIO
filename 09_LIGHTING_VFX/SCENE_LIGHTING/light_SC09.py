#!/usr/bin/env python3
"""
Scene lighting + VFX: SC09 - pre-dawn, clearing.
Mood: beacon amber sweeps; rain turns to light
Key: SC09_SUN_1 (single shadow caster). World: (0.13, 0.12, 0.14) @ 0.8.
Effects: BEAM_FOG_SC09, DRIZZLE_SC09.

Run under Blender:  blender -b -P light_SC09.py
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

SUMMARY = light_runner.build_scene_lighting("SC09")
L.save_blend_if_real(os.path.join("09_LIGHTING_VFX", "SCENE_LIGHTING", "SC09.blend"))

if __name__ == "__main__":
    print("LIGHTING SC09:", SUMMARY["time"], "|", SUMMARY["lights"], "lights |",
          "shadow:", SUMMARY["shadow_casters"], "| vfx:", SUMMARY["vfx"],
          "| frames", SUMMARY["frames"][0], "-", SUMMARY["frames"][1])
