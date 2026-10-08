#!/usr/bin/env python3
"""
Scene lighting + VFX: SC08 - night, lamp room interior.
Mood: her glow only — then the ignition bloom
Key: SC08_POINT_0 (single shadow caster). World: (0.01, 0.015, 0.025) @ 0.25.
Effects: DUST_SC08, IGNITION_GLOW.

Run under Blender:  blender -b -P light_SC08.py
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

SUMMARY = light_runner.build_scene_lighting("SC08")
L.save_blend_if_real(os.path.join("09_LIGHTING_VFX", "SCENE_LIGHTING", "SC08.blend"))

if __name__ == "__main__":
    print("LIGHTING SC08:", SUMMARY["time"], "|", SUMMARY["lights"], "lights |",
          "shadow:", SUMMARY["shadow_casters"], "| vfx:", SUMMARY["vfx"],
          "| frames", SUMMARY["frames"][0], "-", SUMMARY["frames"][1])
