"""
Emit one standalone camera script per shot into 08_CAMERA/SHOT_CAMERAS/cam_<SHOT>.py.

Each script builds the shot's scene, runs its animation (subjects at final
pose) and applies that shot's camera direction only - independently
recoverable. Under real Blender it saves 08_CAMERA/SHOT_CAMERAS/<SHOT>.blend.

Run:  python3 08_CAMERA/scripts/write_cam_scripts.py
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "08_CAMERA", "SHOT_CAMERAS")
sys.path.insert(0, HERE)

TEMPLATE = '''#!/usr/bin/env python3
"""
Shot camera: {sid} (scene {scene}, frames {f0}-{f1} @24fps).
{note}

Run under Blender:  blender -b -P {fname}
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
    if s["shot_id"] == "{sid}")

SUMMARY = cam_runner.build_shot_camera("{sid}", REC)
L.save_blend_if_real(os.path.join("08_CAMERA", "SHOT_CAMERAS", "{sid}.blend"))

if __name__ == "__main__":
    print("CAMERA {sid}:", SUMMARY["lens"], "mm |", SUMMARY["motion"], "|",
          SUMMARY["keys"], "keys | frames", SUMMARY["frames"][0], "-", SUMMARY["frames"][1])
'''


def main():
    os.makedirs(OUT, exist_ok=True)
    from shot_cams import SHOT_CAMS
    j = json.load(open(os.path.join(ROOT, "02_SCREENPLAY", "SHOT_LIST.json"), encoding="utf-8"))
    for s in j["shots"]:
        sid = s["shot_id"]
        assert sid in SHOT_CAMS, f"no camera spec for {sid}"
        fname = f"cam_{sid}.py"
        with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
            f.write(TEMPLATE.format(sid=sid, scene=s["scene_id"], f0=s["frame_in"],
                                    f1=s["frame_out"], fname=fname,
                                    note=SHOT_CAMS[sid]["note"].replace('"', "'")))
    print(f"wrote {len(j['shots'])} shot camera scripts")


if __name__ == "__main__":
    main()
