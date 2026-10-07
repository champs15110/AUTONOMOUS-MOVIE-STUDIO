"""
Emit one standalone, independently executable Blender builder per scene into
06_ASSETS/scenes/build_SCnn.py.

Each generated script:
  * resolves its imports relative to itself (runs from any cwd),
  * builds the scene via ams_assets.build_scene(scene_id),
  * saves 06_ASSETS/blender/scenes/SCnn.blend ONLY under a real Blender binary
    (save is skipped under the stub harness).

Run:  python3 06_ASSETS/scripts/write_scene_builders.py
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "06_ASSETS", "scenes")

TEMPLATE = '''#!/usr/bin/env python3
"""
Standalone Blender scene builder for {sid} - {slug}.

Frames {f0}-{f1} at 24 fps, 1920x1080 (16:9), from 02_SCREENPLAY/SHOT_LIST.json.
Independent: builds environment, characters, props, materials, lights, camera
placeholder and render settings by itself. No other scene needs to exist.

Run under Blender:   blender -b -P {fname}
Test without Blender: python3 06_ASSETS/scripts/run_build_tests.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
sys.path.insert(0, os.path.join(HERE, "..", "materials"))

import ams_assets
import ams_blender_lib as L

SUMMARY = ams_assets.build_scene("{sid}")
L.save_blend_if_real(os.path.join("06_ASSETS", "blender", "scenes", "{sid}.blend"))

if __name__ == "__main__":
    print("BUILT {sid}:", SUMMARY)
'''


def main():
    os.makedirs(OUT, exist_ok=True)
    j = json.load(open(os.path.join(ROOT, "02_SCREENPLAY", "SHOT_LIST.json"), encoding="utf-8"))
    for sc in j["scenes"]:
        sid = sc["scene_id"]
        fname = f"build_{sid}.py"
        with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
            f.write(TEMPLATE.format(sid=sid, slug=sc["slug"], f0=sc["frame_in"],
                                    f1=sc["frame_out"], fname=fname))
        print("wrote", fname)


if __name__ == "__main__":
    main()
