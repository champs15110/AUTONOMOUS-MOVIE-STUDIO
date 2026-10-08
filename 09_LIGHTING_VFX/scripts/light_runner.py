"""
light_runner - executes one scene's lighting + VFX design on its built scene.

Sequence per scene (independently recoverable):
  1. build the scene            (ams_assets.build_scene - env/chars/props/lights)
  2. tune lights + add fills    (light_design.apply_lighting - one shadow caster)
  3. build + key VFX objects    (light_design.apply_vfx - shot-timed, seeded)

Shot frame ranges come from 05_STORYBOARD/MASTER_SHOT_PLAN.json so rain
ignition (SC04_SH003), the lee calm (SC07_SH008) and the ignition glow
(SC08_SH007) land on the exact approved frames.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

import light_design as LD  # noqa: E402  (imports first: sets sys.path)
import ams_assets  # noqa: E402

_plan = json.load(open(os.path.join(ROOT, "05_STORYBOARD", "MASTER_SHOT_PLAN.json"),
                       encoding="utf-8"))
SHOT_FRAMES = {s["shot_id"]: (int(s["frame_in"]), int(s["frame_out"]))
               for s in _plan["shots"]}
SHOT_GRADE = {s["shot_id"]: s["lighting_intention"].split(" | ")[0].strip()
              for s in _plan["shots"]}
SHOT_SCENE = {s["shot_id"]: s["scene_id"] for s in _plan["shots"]}


def build_scene_lighting(scene_id):
    summ = ams_assets.build_scene(scene_id)
    frames = (summ["frame_start"], summ["frame_end"])
    inv = LD.apply_lighting(scene_id)
    made = LD.apply_vfx(scene_id, SHOT_FRAMES, frames)
    return dict(
        scene_id=scene_id,
        frames=frames,
        time=LD.LIGHTING[scene_id]["time"],
        mood=LD.LIGHTING[scene_id]["mood"],
        lights=len(inv),
        shadow_casters=[i["name"] for i in inv if i["use_shadow"]],
        world=dict(color=list(LD.LIGHTING[scene_id]["world"][0]),
                   strength=LD.LIGHTING[scene_id]["world"][1]),
        vfx=[m["entry"]["id"] for m in made] or ["none"],
        objects=len(LD.all_objects()),
    )
