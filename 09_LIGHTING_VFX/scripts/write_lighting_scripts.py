"""
Emit one standalone lighting/VFX script per scene into
09_LIGHTING_VFX/SCENE_LIGHTING/light_<SCENE>.py.

Each script rebuilds the scene from the 06_ASSETS library, applies that
scene's lighting design and VFX only - independently recoverable. Under real
Blender it saves 09_LIGHTING_VFX/SCENE_LIGHTING/<SCENE>.blend.

Run:  python3 09_LIGHTING_VFX/scripts/write_lighting_scripts.py
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "09_LIGHTING_VFX", "SCENE_LIGHTING")
sys.path.insert(0, HERE)

TEMPLATE = '''#!/usr/bin/env python3
"""
Scene lighting + VFX: {sid} - {time}.
Mood: {mood}
Key: {key} (single shadow caster). World: {world}.
Effects: {effects}.

Run under Blender:  blender -b -P light_{sid}.py
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

SUMMARY = light_runner.build_scene_lighting("{sid}")
L.save_blend_if_real(os.path.join("09_LIGHTING_VFX", "SCENE_LIGHTING", "{sid}.blend"))

if __name__ == "__main__":
    print("LIGHTING {sid}:", SUMMARY["time"], "|", SUMMARY["lights"], "lights |",
          "shadow:", SUMMARY["shadow_casters"], "| vfx:", SUMMARY["vfx"],
          "| frames", SUMMARY["frames"][0], "-", SUMMARY["frames"][1])
'''


def main():
    os.makedirs(OUT, exist_ok=True)
    import light_design as LD
    written = []
    for sid in LD.SCENES:
        spec = LD.LIGHTING[sid]
        effects = ", ".join(e["id"] for e in LD.VFX.get(sid, [])) or "none"
        world = f"{spec['world'][0]} @ {spec['world'][1]}"
        text = TEMPLATE.format(sid=sid, time=spec["time"], mood=spec["mood"],
                               key=spec["key"], world=world, effects=effects)
        path = os.path.join(OUT, f"light_{sid}.py")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        written.append(path)
    print(f"wrote {len(written)} lighting scripts ->", OUT)
    for p in written:
        print(" ", os.path.relpath(p, ROOT))


if __name__ == "__main__":
    main()
