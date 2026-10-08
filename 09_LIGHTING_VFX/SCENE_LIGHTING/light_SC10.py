#!/usr/bin/env python3
"""
Scene lighting + VFX: SC10 - dawn, calm sea.
Mood: rose-gold stillness; the loop warms
Key: SC10_SUN_0 (single shadow caster). World: (0.16, 0.14, 0.13) @ 0.9.
Effects: DUST_SC10.

Run under Blender:  blender -b -P light_SC10.py
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

SUMMARY = light_runner.build_scene_lighting("SC10")
L.save_blend_if_real(os.path.join("09_LIGHTING_VFX", "SCENE_LIGHTING", "SC10.blend"))

if __name__ == "__main__":
    print("LIGHTING SC10:", SUMMARY["time"], "|", SUMMARY["lights"], "lights |",
          "shadow:", SUMMARY["shadow_casters"], "| vfx:", SUMMARY["vfx"],
          "| frames", SUMMARY["frames"][0], "-", SUMMARY["frames"][1])
