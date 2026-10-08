"""
Emit one standalone animation script per shot into
07_ANIMATION/SHOT_ANIMATION/anim_<SHOT>.py.

Each script builds ONLY its scene and keys ONLY its shot's frame range -
the film is never animated in one operation. Under real Blender it saves
07_ANIMATION/SHOT_ANIMATION/<SHOT>.blend.

Run:  python3 07_ANIMATION/scripts/write_anim_scripts.py
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "07_ANIMATION", "SHOT_ANIMATION")

TEMPLATE = '''#!/usr/bin/env python3
"""
Shot animation: {sid} (scene {scene}, frames {f0}-{f1} @24fps).
Direction: {note}

Run under Blender:  blender -b -P {fname}
Local structural test: python3 07_ANIMATION/scripts/run_anim_tests.py
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "06_ASSETS", "scripts"))
sys.path.insert(0, os.path.join(ROOT, "06_ASSETS", "materials"))
sys.path.insert(0, os.path.join(ROOT, "07_ANIMATION", "scripts"))

import ams_blender_lib as L
import shot_runner

REC = next(s for s in json.load(
    open(os.path.join(ROOT, "02_SCREENPLAY", "SHOT_LIST.json"), encoding="utf-8"))["shots"]
    if s["shot_id"] == "{sid}")

SUMMARY = shot_runner.build_shot("{sid}", REC)
L.save_blend_if_real(os.path.join("07_ANIMATION", "SHOT_ANIMATION", "{sid}.blend"))

if __name__ == "__main__":
    print("ANIMATED {sid}:", SUMMARY["keys"], "keys over frames",
          SUMMARY["frame_start"], "-", SUMMARY["frame_end"])
'''


def main():
    os.makedirs(OUT, exist_ok=True)
    j = json.load(open(os.path.join(ROOT, "02_SCREENPLAY", "SHOT_LIST.json"), encoding="utf-8"))
    from shot_specs import SPECS
    for s in j["shots"]:
        sid = s["shot_id"]
        assert sid in SPECS, f"no animation spec for {sid}"
        fname = f"anim_{sid}.py"
        with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
            f.write(TEMPLATE.format(sid=sid, scene=s["scene_id"], f0=s["frame_in"],
                                    f1=s["frame_out"], fname=fname,
                                    note=SPECS[sid]["note"].replace('"', "'")))
    print(f"wrote {len(j['shots'])} shot animation scripts")


if __name__ == "__main__":
    main()
