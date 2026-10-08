#!/usr/bin/env python3
"""Stage 09 lighting + VFX design — NINETY-TWO TURNS.

Every entry in LIGHTING and VFX below carries a story purpose. There are no
decorative effects in this film: rain marks the storm's arrival, fog withholds
the horizon, dust motes make the lamp-room air tangible, spray is the sea
attacking the gallery, and the single ignition glow is the one miraculous
moment the whole film earns.

Design rules (checked by run_lighting_tests.py):
  * one shadow-casting light per scene (the planned key) — coherent shadows;
  * every character scene gets a warm fill so faces stay readable;
  * wind is camera-right (+X) in the storm scenes, per CONTINUITY_BIBLE §4;
  * rain begins exactly at SC04_SH003 and thins to drizzle by SC09;
  * the world shader is never black — depth comes from gradient, not void;
  * all materials come from the registered 06_ASSETS library (18 entries).

apply_lighting(scene_id) tunes the scene's built lights and adds fill;
apply_vfx(scene_id, shot_frames, scene_frames) builds the effect objects
with shot-timed animation. Both are deterministic (fixed seeds).
"""
import math
import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
STUB_DIR = REPO_ROOT / "tools" / "blender_stub"
AMS_SCRIPTS = REPO_ROOT / "06_ASSETS" / "scripts"
AMS_MATERIALS = REPO_ROOT / "06_ASSETS" / "materials"
CAM_SCRIPTS = REPO_ROOT / "08_CAMERA" / "scripts"
for _p in (str(STUB_DIR), str(AMS_SCRIPTS), str(AMS_MATERIALS), str(CAM_SCRIPTS)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import bpy  # noqa: E402
import ams_blender_lib as L  # noqa: E402
import ams_materials as MATS  # noqa: E402

RAD = math.radians


# ---------------------------------------------------------------- lighting ---

LIGHTING = {
    "SC01": dict(
        time="dusk, still sea", mood="lonely ritual; the world withheld",
        world=((0.06, 0.10, 0.13), 0.55),
        key="SC01_SUN_0", shadow_casters=("SC01_SUN_0",),
        tune={"SC01_SUN_0": dict(energy=2.2, angle=0.09, use_shadow=True),
              "SC01_POINT_1": dict(use_shadow=False)},
        add=[("SC01_FILL", "POINT", 10, (1.0, 0.75, 0.5), (1.4, -1.8, 1.0))],
        exposure=(0.5, 60.0)),
    "SC02": dict(
        time="dusk, first swell", mood="the sea begins to speak",
        world=((0.06, 0.10, 0.14), 0.60),
        key="SC02_SUN_0", shadow_casters=("SC02_SUN_0",),
        tune={"SC02_SUN_0": dict(energy=2.0, angle=0.10, use_shadow=True),
              "SC02_POINT_1": dict(use_shadow=False),
              "SC02_POINT_2": dict(use_shadow=False, shadow_soft_size=2.0)},
        add=[("SC02_FILL", "POINT", 12, (1.0, 0.78, 0.55), (-1.4, 1.6, 1.1))],
        exposure=(0.5, 60.0)),
    "SC03": dict(
        time="dusk, swell", mood="the horizon withheld — fog holds the ship back",
        world=((0.10, 0.12, 0.16), 0.70),
        key="SC03_SUN_0", shadow_casters=("SC03_SUN_0",),
        tune={"SC03_SUN_0": dict(energy=3.0, angle=0.10, use_shadow=True),
              "SC03_POINT_1": dict(use_shadow=False)},
        add=[("SC03_FILL", "POINT", 14, (1.0, 0.80, 0.55), (0.6, -1.6, 1.0))],
        exposure=(0.5, 60.0)),
    "SC04": dict(
        time="dusk, storm front arrives", mood="the light goes cold; the rain starts",
        world=((0.07, 0.09, 0.12), 0.65),
        key="SC04_SUN_0", shadow_casters=("SC04_SUN_0",),
        tune={"SC04_SUN_0": dict(energy=4.0, angle=0.12, use_shadow=True),
              "SC04_POINT_1": dict(use_shadow=False)},
        add=[("SC04_FILL", "POINT", 12, (0.85, 0.80, 0.75), (1.2, -1.6, 1.2))],
        exposure=(0.5, 60.0)),
    "SC05": dict(
        time="storm, gallery", mood="she climbs into the weather",
        world=((0.05, 0.06, 0.08), 0.55),
        key="SC05_SUN_0", shadow_casters=("SC05_SUN_0",),
        tune={"SC05_SUN_0": dict(energy=4.0, angle=0.12, use_shadow=True),
              "SC05_POINT_1": dict(use_shadow=False)},
        add=[("SC05_FILL", "POINT", 40, (1.0, 0.72, 0.40), (0.8, 2.0, 2.6))],
        exposure=(0.5, 60.0)),
    "SC06": dict(
        time="storm, tower door and lower stair", mood="the door at last — rain hammers the plating",
        world=((0.04, 0.05, 0.07), 0.50),
        key="SC06_SUN_0", shadow_casters=("SC06_SUN_0",),
        tune={"SC06_SUN_0": dict(energy=5.0, angle=0.13, use_shadow=True),
              "SC06_POINT_1": dict(use_shadow=False)},
        add=[("SC06_FILL", "POINT", 15, (1.0, 0.75, 0.50), (2.0, -1.2, 1.4))],
        exposure=(0.5, 60.0)),
    "SC07": dict(
        time="gale, lee of the tower", mood="storm-white, near-monochrome; the lee is calm",
        world=((0.08, 0.09, 0.11), 0.70),
        key="SC07_SUN_0", shadow_casters=("SC07_SUN_0",),
        tune={"SC07_SUN_0": dict(energy=8.0, angle=0.13, use_shadow=True),
              "SC07_POINT_1": dict(use_shadow=False)},
        add=[("SC07_FILL", "POINT", 40, (0.90, 0.92, 1.00), (-2.2, 0.6, 2.6)),
             ("SC07_BACK", "POINT", 25, (0.70, 0.80, 1.00), (3.5, -1.0, 1.0))],
        exposure=(0.5, 60.0)),
    "SC08": dict(
        time="night, lamp room interior", mood="her glow only — then the ignition bloom",
        world=((0.010, 0.015, 0.025), 0.25),
        key="SC08_POINT_0", shadow_casters=("SC08_POINT_0",),
        tune={"SC08_POINT_0": dict(energy=15.0, use_shadow=True),
              "SC08_AREA_1": dict(use_shadow=False)},
        add=[("SC08_FILL", "POINT", 12, (1.00, 0.80, 0.55), (0.9, -0.8, 12.9))],
        exposure=(0.5, 60.0)),
    "SC09": dict(
        time="pre-dawn, clearing", mood="beacon amber sweeps; rain turns to light",
        world=((0.13, 0.12, 0.14), 0.80),
        key="SC09_SUN_1", shadow_casters=("SC09_SUN_1",),
        tune={"SC09_SUN_1": dict(energy=3.0, angle=0.12, use_shadow=True),
              "SC09_SPOT_0": dict(use_shadow=False, shadow_soft_size=1.5)},
        add=[("SC09_FILL", "POINT", 50, (1.00, 0.85, 0.70), (3.0, 2.0, 11.5))],
        exposure=(0.5, 60.0)),
    "SC10": dict(
        time="dawn, calm sea", mood="rose-gold stillness; the loop warms",
        world=((0.16, 0.14, 0.13), 0.90),
        key="SC10_SUN_0", shadow_casters=("SC10_SUN_0",),
        tune={"SC10_SUN_0": dict(energy=4.0, angle=0.10, use_shadow=True)},
        add=[("SC10_FILL", "POINT", 12, (1.00, 0.85, 0.75), (-0.6, 1.2, 12.8))],
        exposure=(0.5, 60.0)),
}


# --------------------------------------------------------------------- vfx ---

VFX = {
    "SC03": [
        dict(id="FOG_SC03", kind="fog", purpose="the horizon withheld — she cannot see the ship",
             shots="scene-wide", center=(-1.0, 3.5, 0.45), size=(12.0, 10.0, 0.8), drift=0.35),
    ],
    "SC04": [
        dict(id="RAIN_SC04", kind="rain", purpose="the storm front arrives — rain begins exactly here",
             start_shot="SC04_SH003", center=(-2.0, 1.5), top=3.5, count=60, slant_deg=12,
             note="cloud held off (scale ~0) until SH003, then ramps in over 12 frames"),
        dict(id="SILT_SC04", kind="motes", purpose="silt she disturbs at the base — the work is physical",
             shots="scene-wide", center=(-2.0, 1.6, 0.15), radius=2.0, count=36,
             mote_r=0.004, drift=(0.10, 0.06, 0.10)),
    ],
    "SC05": [
        dict(id="RAIN_SC05", kind="rain", purpose="full storm — wind camera-right per continuity bible",
             shots="scene-wide", center=(0.0, 4.5), top=5.5, count=90, slant_deg=62),
        dict(id="SPRAY_SC05", kind="spray", purpose="sea attacking the gallery — she climbs through it",
             shots="scene-wide", center=(0.0, 4.5, -0.3), radius=2.2, count=26, rise=0.30),
    ],
    "SC06": [
        dict(id="RAIN_SC06", kind="rain", purpose="rain on the lamp-room glass — the world outside kept out",
             shots="scene-wide", center=(2.5, 0.0), top=4.5, count=80, slant_deg=62),
    ],
    "SC07": [
        dict(id="RAIN_SC07", kind="rain", purpose="gale sheets — then the lee is calm at SH008",
             shots="scene-wide", center=(2.5, 0.0), top=10.0, count=100, slant_deg=72,
             calm_shot="SC07_SH008",
             note="cloud scale-z eases to 0.15 at SC07_SH008: the lee-side calm is story"),
        dict(id="SPRAY_SC07", kind="spray", purpose="breaking water on the lee rocks",
             shots="scene-wide", center=(4.5, 2.0, 0.8), radius=3.0, count=30, rise=0.45),
    ],
    "SC08": [
        dict(id="DUST_SC08", kind="motes", purpose="lamp-room air made tangible in her glow",
             shots="scene-wide", center=(0.6, 0.0, 12.9), radius=1.5, count=40,
             mote_r=0.005, drift=(0.05, 0.04, 0.20)),
        dict(id="IGNITION_GLOW", kind="glow", purpose="the one miraculous moment the film earns",
             shot="SC08_SH007", center=(0.0, 0.0, 13.4), radius=0.35, end_scale=3.5,
             note="sphere scales 0.01 -> 3.5 over the ignition act; SC08_FILL swells 12 -> 60 with it"),
    ],
    "SC09": [
        dict(id="BEAM_FOG_SC09", kind="fog", purpose="the beacon beam becomes visible — dawn finds the fog",
             shots="scene-wide", center=(8.0, 3.0, 9.5), size=(24.0, 16.0, 8.0), drift=0.5),
        dict(id="DRIZZLE_SC09", kind="rain", purpose="rain thinning to drizzle — the storm is leaving",
             shots="scene-wide", center=(0.0, 0.0), top=8.0, count=28, slant_deg=8),
    ],
    "SC10": [
        dict(id="DUST_SC10", kind="motes", purpose="gold motes settle — dawn calm closes the loop",
             shots="scene-wide", center=(0.8, 0.0, 12.6), radius=1.8, count=36,
             mote_r=0.005, drift=(0.08, 0.05, 0.12)),
    ],
}

SCENES = tuple(sorted(LIGHTING))


# ------------------------------------------------------------------ helpers ---

def all_objects():
    out = []

    def rec(c):
        for o in list(c.objects):
            out.append(o)
        for ch in list(c.children):
            rec(ch)
    rec(bpy.context.scene.collection)
    return out


def _scene_lights(scene_id):
    out = []
    for o in all_objects():
        if o.name.startswith(scene_id) and o.data is not None and hasattr(o.data, "energy"):
            out.append(o)
    return out


_AXIS = {"x": 0, "y": 1, "z": 2}


def _kf(owner, data_path, comp, value, frame, interp="BEZIER"):
    """Key one channel: set value, insert keyframe, tag interpolation."""
    idx = -1 if comp is None else _AXIS[comp]
    cur = getattr(owner, data_path)
    if comp is None:
        setattr(owner, data_path, value)
    else:
        seq = list(cur)
        seq[idx] = value
        setattr(owner, data_path, seq)
    owner.keyframe_insert(data_path, index=idx, frame=frame)
    fc = next(f for f in owner.animation_data.action.fcurves
              if f.data_path == data_path and f.array_index == max(idx, 0))
    fc.keyframe_points[-1].interpolation = interp


def _tune_world(color, strength):
    """Retune the existing world Background node (build_scene already made one)."""
    w = bpy.context.scene.world
    for n in w.node_tree.nodes:
        if ("Color" in n.inputs and "Strength" in n.inputs
                and n.inputs["Color"].default_value is not None
                and n.inputs["Strength"].default_value is not None):
            n.inputs["Color"].default_value = (*color, 1.0)
            n.inputs["Strength"].default_value = strength
            return
    L.set_world(color, strength)  # no background node yet - create one


def _mat(mid):
    return MATS._BUILDERS[mid]()


# ----------------------------------------------------------------- lighting ---

def apply_lighting(scene_id):
    """Tune built lights, add fill/rim, set world. Returns measured inventory."""
    spec = LIGHTING[scene_id]
    lights = {o.name: o for o in _scene_lights(scene_id)}
    missing = [n for n in spec["tune"] if n not in lights]
    if missing:
        raise KeyError(f"{scene_id}: lights missing from built scene: {missing}")
    for name, tune in spec["tune"].items():
        ld = lights[name].data
        for k, v in tune.items():
            setattr(ld, k, v)
    coll = L.new_coll(f"{scene_id}_LIGHTS_FX")
    for name, ltype, energy, color, loc in spec["add"]:
        lo = L.add_light(coll, name, ltype, energy, color, loc)
        lo.data.use_shadow = False  # fills never cast — one shadow caster per scene
    world_color, world_strength = spec["world"]
    _tune_world(world_color, world_strength)
    inventory = []
    for o in _scene_lights(scene_id):
        inventory.append(dict(name=o.name, type=type(o.data).__name__.upper(),
                              energy=round(o.data.energy, 3),
                              use_shadow=bool(o.data.use_shadow),
                              location=[round(v, 3) for v in o.location]))
    return inventory


# ---------------------------------------------------------------------- vfx ---

def apply_vfx(scene_id, shot_frames, scene_frames):
    """Build effect objects for the scene, keyed to shot timing. Deterministic."""
    f_start, f_end = scene_frames
    rnd = random.Random(1000 + int(scene_id[2:]))
    coll = L.new_coll(f"{scene_id}_VFX")
    made = []
    for entry in VFX.get(scene_id, []):
        kind = entry["kind"]
        if kind == "rain":
            cx, cy = entry["center"]
            top, count, slant = entry["top"], entry["count"], entry["slant_deg"]
            root = L.add_empty(coll, entry["id"], loc=(cx, cy, 0.0))
            area = entry.get("area", (10.0, 10.0))
            for i in range(count):
                px = rnd.uniform(-area[0] / 2, area[0] / 2)
                py = rnd.uniform(-area[1] / 2, area[1] / 2)
                pz = rnd.uniform(0.0, top)
                ln = 0.28 + rnd.uniform(0.0, 0.25)
                st = L.add_box(coll, f"{entry['id']}_s{i:03d}", 0.006, 0.006, ln,
                               loc=(px, py, pz), rot=(0.0, RAD(slant), 0.0),
                               mat=_mat("MAT_RAIN_STREAK"))
                L.parent(st, root)
            # the whole cloud falls through the set (linear wrap handled by shader)
            _kf(root, "location", "z", 0.0, f_start, "LINEAR")
            _kf(root, "location", "z", -top, f_end, "LINEAR")
            if entry.get("start_shot"):
                f0 = shot_frames[entry["start_shot"]][0]
                for axis in ("x", "y", "z"):
                    _kf(root, "scale", axis, 0.001 if axis == "z" else 1.0, f_start, "CONSTANT")
                    _kf(root, "scale", axis, 1.0, f0 + 12, "CONSTANT")
            if entry.get("calm_shot"):
                f0 = shot_frames[entry["calm_shot"]][0]
                _kf(root, "scale", "z", 1.0, f0 - 1, "CONSTANT")
                _kf(root, "scale", "z", 0.15, f0 + 30, "BEZIER")
            made.append(dict(entry=entry, object=entry["id"], count=count,
                             slant_deg=slant, top=top))
        elif kind == "fog":
            cx, cy, cz = entry["center"]
            sx, sy, sz = entry["size"]
            box = L.add_box(coll, entry["id"], sx, sy, sz, loc=(cx, cy, cz),
                            mat=_mat("MAT_FOG_BANK"))
            d = entry["drift"]
            _kf(box, "location", "x", cx - d, f_start, "BEZIER")
            _kf(box, "location", "x", cx + d, f_end, "BEZIER")
            made.append(dict(entry=entry, object=entry["id"], count=1,
                             size=[sx, sy, sz], drift=d))
        elif kind == "motes":
            cx, cy, cz = entry["center"]
            root = L.add_empty(coll, entry["id"], loc=(cx, cy, cz))
            for i in range(entry["count"]):
                r = entry["radius"]
                px = rnd.uniform(-r, r)
                py = rnd.uniform(-r, r)
                pz = rnd.uniform(-r * 0.6, r * 0.6)
                mo = L.add_sphere(coll, f"{entry['id']}_m{i:03d}",
                                  entry["mote_r"] * rnd.uniform(0.6, 1.4),
                                  loc=(px, py, pz), mat=_mat("MAT_DUST_MOTE"))
                L.parent(mo, root)
            dx, dy, dz = entry["drift"]
            _kf(root, "location", "x", cx - dx, f_start, "BEZIER")
            _kf(root, "location", "x", cx + dx, f_end, "BEZIER")
            _kf(root, "location", "z", cz - dz * 0.5, f_start, "BEZIER")
            _kf(root, "location", "z", cz + dz, f_end, "BEZIER")
            made.append(dict(entry=entry, object=entry["id"], count=entry["count"]))
        elif kind == "spray":
            cx, cy, cz = entry["center"]
            root = L.add_empty(coll, entry["id"], loc=(cx, cy, cz))
            for i in range(entry["count"]):
                r = entry["radius"]
                px = rnd.uniform(-r, r)
                py = rnd.uniform(-r, r)
                pz = rnd.uniform(-0.4, 0.4)
                dr = L.add_sphere(coll, f"{entry['id']}_d{i:03d}",
                                  rnd.uniform(0.012, 0.035),
                                  loc=(px, py, pz), mat=_mat("MAT_RAIN_STREAK"))
                L.parent(dr, root)
            rise = entry["rise"]
            n = 4
            span = (f_end - f_start) / n
            for i in range(n + 1):
                f = f_start + i * span
                z = cz + (rise if i % 2 == 1 else 0.0)
                _kf(root, "location", "z", z, f, "LINEAR")
            made.append(dict(entry=entry, object=entry["id"], count=entry["count"],
                             rise=rise))
        elif kind == "glow":
            cx, cy, cz = entry["center"]
            sph = L.add_sphere(coll, entry["id"], entry["radius"], loc=(cx, cy, cz),
                               mat=_mat("MAT_AMBER_GLOW"))
            f0 = shot_frames[entry["shot"]][0]
            for axis in ("x", "y", "z"):
                _kf(sph, "scale", axis, 0.01, f_start, "CONSTANT")
                _kf(sph, "scale", axis, 0.01, f0, "CONSTANT")
                _kf(sph, "scale", axis, entry["end_scale"], f0 + 18, "BEZIER")
            # motivated practical swell: the fill light blooms with ignition
            fill = [o for o in all_objects() if o.name == "SC08_FILL"]
            if fill:
                _kf(fill[0].data, "energy", None, 12.0, f0, "CONSTANT")
                _kf(fill[0].data, "energy", None, 60.0, f0 + 18, "BEZIER")
            made.append(dict(entry=entry, object=entry["id"], count=1,
                             shot=entry["shot"], end_scale=entry["end_scale"]))
        else:  # pragma: no cover - defensive
            raise ValueError(f"unknown vfx kind {kind}")
    return made
