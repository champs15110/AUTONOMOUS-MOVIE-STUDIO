"""
ams_assets - procedural asset + scene builders for NINETY-TWO TURNS.

Every builder is pure bpy Python (from_pydata geometry, node materials) so the
same file runs under a real Blender binary on the cloud render layer and under
the structural stub (tools/blender_stub) for local validation.

Scale: metres. WICK = 0.40 m. Master axis: sea/ship +X (frame right when the
placeholder camera looks +Y), tower landmark -X.
"""

import math

import bpy

import ams_blender_lib as L
import ams_materials as MATS

RAD = math.radians


def mat(mid):
    return MATS._BUILDERS[mid]()


def _root(coll, name, loc=(0, 0, 0)):
    return L.add_empty(coll, name, loc, size=0.15)


def _attach(root, *obs):
    for o in obs:
        L.parent(o, root)


# ---------------------------------------------------------------------- #
# props
# ---------------------------------------------------------------------- #
def build_prop_KEY(coll, loc=(0, 0, 0), rot=(0, 0, 0)):
    r = _root(coll, "PROP_KEY", loc)
    r.rotation_euler = rot
    shaft = L.add_cyl(coll, "KEY_shaft", r=0.007, depth=0.07, verts=8,
                      rot=(RAD(90), 0, 0), mat=mat("MAT_BRASS_POLISHED"))
    bow = L.add_ring(coll, "KEY_bow", radius=0.02, tube=0.006, seg=12, sides=6,
                     loc=(0, 0.045, 0), rot=(RAD(90), 0, 0), mat=mat("MAT_BRASS_POLISHED"))
    t1 = L.add_box(coll, "KEY_tooth1", 0.008, 0.012, 0.012, loc=(0.01, -0.03, 0), mat=mat("MAT_BRASS_POLISHED"))
    t2 = L.add_box(coll, "KEY_tooth2", 0.008, 0.01, 0.01, loc=(0.01, -0.02, 0), mat=mat("MAT_BRASS_POLISHED"))
    _attach(r, shaft, bow, t1, t2)
    return r


def build_prop_GAUGE(coll, loc=(0, 0, 0), rot=(RAD(90), 0, 0)):
    r = _root(coll, "PROP_GAUGE", loc)
    r.rotation_euler = rot
    dial = L.add_disc(coll, "GAUGE_dial", r=0.045, verts=24, mat=mat("MAT_GAUGE_DIAL"))
    rim = L.add_ring(coll, "GAUGE_rim", radius=0.048, tube=0.006, seg=20, sides=6, mat=mat("MAT_BRASS_AGED"))
    needle = L.add_box(coll, "GAUGE_needle", 0.006, 0.038, 0.003, loc=(0, 0.012, 0.004), mat=mat("MAT_IRON_RUSTED"))
    _attach(r, dial, rim, needle)
    return r


def build_prop_MAINSPRING(coll, loc=(0, 0, 0)):
    r = _root(coll, "PROP_MAINSPRING", loc)
    pts = [(0.032 * math.cos(t), 0.0016 * t, 0.032 * math.sin(t))
           for t in [i * 0.5 for i in range(38)]]
    coil = L.add_tube(coll, "MAINSPRING_coil", pts, radius=0.004, sides=6, mat=mat("MAT_BRASS_POLISHED"))
    _attach(r, coil)
    return r


def build_prop_POLE(coll, loc=(0, 0, 0), rot=(0, 0, 0), lit=False):
    r = _root(coll, "PROP_POLE", loc)
    r.rotation_euler = rot
    shaft = L.add_cyl(coll, "POLE_shaft", r=0.012, depth=0.95, verts=8, loc=(0, 0, 0.475), mat=mat("MAT_IRON_RUSTED"))
    head = L.add_cone(coll, "POLE_head", r1=0.06, r2=0.02, depth=0.09, verts=8, loc=(0, 0, 0.97), mat=mat("MAT_IRON_RUSTED"))
    flame = L.add_sphere(coll, "POLE_flame", r=0.028, seg=8, rings=4, loc=(0, 0, 0.96),
                         mat=mat("MAT_AMBER_GLOW") if lit else mat("MAT_WOOD_ROTTED"))
    _attach(r, shaft, head, flame)
    return r


def build_prop_PILLAR(coll, loc=(0, 0, 0)):
    r = _root(coll, "PROP_PILLAR", loc)
    base = L.add_cone(coll, "PILLAR_base", r1=0.2, r2=0.14, depth=0.15, verts=12, loc=(0, 0, 0.075), mat=mat("MAT_BRASS_AGED"))
    col = L.add_cyl(coll, "PILLAR_column", r=0.12, depth=1.0, verts=12, loc=(0, 0, 0.62), mat=mat("MAT_BRASS_AGED"))
    sock = L.add_cyl(coll, "PILLAR_socket", r=0.03, depth=0.05, verts=8, loc=(0, 0, 1.14), mat=mat("MAT_BRASS_POLISHED"))
    _attach(r, base, col, sock)
    return r


def build_prop_LAMP(coll, loc=(0, 0, 0), lit=False):
    r = _root(coll, "PROP_LAMP", loc)
    post = L.add_cyl(coll, "LAMP_post", r=0.03, depth=1.6, verts=8, loc=(0, 0, 0.8), mat=mat("MAT_IRON_RUSTED"))
    head = L.add_box(coll, "LAMP_head", 0.14, 0.14, 0.18, loc=(0, 0, 1.68), mat=mat("MAT_IRON_RUSTED"))
    flame = L.add_sphere(coll, "LAMP_flame", r=0.04, seg=8, rings=4, loc=(0, 0, 1.66),
                         mat=mat("MAT_AMBER_GLOW") if lit else mat("MAT_WOOD_ROTTED"))
    _attach(r, post, head, flame)
    return r


def build_prop_SPARK(coll, loc=(0, 0, 0)):
    r = _root(coll, "PROP_SPARK", loc)
    core = L.add_sphere(coll, "SPARK_core", r=0.016, seg=8, rings=4, mat=mat("MAT_SPARK_GLOW"))
    shell = L.add_sphere(coll, "SPARK_glass", r=0.028, seg=10, rings=5, mat=mat("MAT_GLASS_DRUM"))
    _attach(r, core, shell)
    return r


def build_prop_DOOR(coll, loc=(0, 0, 0), rot=(0, 0, 0)):
    r = _root(coll, "PROP_DOOR", loc)
    r.rotation_euler = rot
    slab = L.add_box(coll, "DOOR_slab", 1.3, 0.16, 2.3, loc=(0, 0, 1.15), mat=mat("MAT_IRON_RUSTED"))
    h1 = L.add_box(coll, "DOOR_hinge1", 0.3, 0.06, 0.12, loc=(-0.6, -0.1, 1.8), mat=mat("MAT_IRON_RUSTED"))
    h2 = L.add_box(coll, "DOOR_hinge2", 0.3, 0.06, 0.12, loc=(-0.6, -0.1, 0.5), mat=mat("MAT_IRON_RUSTED"))
    ring = L.add_ring(coll, "DOOR_ring", radius=0.09, tube=0.015, seg=12, sides=6,
                      loc=(0.4, -0.12, 1.1), rot=(RAD(90), 0, 0), mat=mat("MAT_IRON_RUSTED"))
    _attach(r, slab, h1, h2, ring)
    return r


def build_prop_STAIR(coll, loc=(0, 0, 0), steps=14):
    r = _root(coll, "PROP_STAIR", loc)
    obs = []
    for i in range(steps):
        a = i * 0.5
        z = 0.22 * i
        st = L.add_box(coll, f"STAIR_step{i:02d}", 0.9, 0.35, 0.05,
                       loc=(1.6 * math.cos(a), 1.6 * math.sin(a), z),
                       rot=(0, 0, a + RAD(90)), mat=mat("MAT_IRON_RUSTED"))
        obs.append(st)
    _attach(r, *obs)
    return r


def build_prop_SOCKET(coll, loc=(0, 0, 0)):
    r = _root(coll, "PROP_SOCKET", loc)
    cup = L.add_cyl(coll, "SOCKET_cup", r=0.035, depth=0.07, verts=12, loc=(0, 0, 0.035), mat=mat("MAT_BRASS_POLISHED"))
    hole = L.add_disc(coll, "SOCKET_hole", r=0.028, verts=12, loc=(0, 0, 0.071), mat=mat("MAT_IRON_RUSTED"))
    _attach(r, cup, hole)
    return r


def build_prop_BURNER(coll, loc=(0, 0, 0)):
    r = _root(coll, "PROP_BURNER", loc)
    body = L.add_cyl(coll, "BURNER_body", r=0.55, depth=0.9, verts=16, loc=(0, 0, 0.45), mat=mat("MAT_IRON_RUSTED"))
    dome = L.add_cone(coll, "BURNER_dome", r1=0.55, r2=0.15, depth=0.5, verts=16, loc=(0, 0, 1.1), mat=mat("MAT_BRASS_AGED"))
    collar = L.add_ring(coll, "BURNER_collar", radius=0.2, tube=0.03, seg=16, sides=6, loc=(0, 0, 1.36), mat=mat("MAT_BRASS_AGED"))
    sock = L.add_cyl(coll, "BURNER_socket", r=0.035, depth=0.07, verts=12, loc=(0, 0, 1.38), mat=mat("MAT_BRASS_POLISHED"))
    _attach(r, body, dome, collar, sock)
    return r


def build_prop_BELLBUOY(coll, loc=(0, 0, 0)):
    r = _root(coll, "PROP_BELLBUOY", loc)
    body = L.add_cone(coll, "BUOY_body", r1=0.28, r2=0.12, depth=0.6, verts=10, loc=(0, 0, 0.3), mat=mat("MAT_IRON_RUSTED"))
    bell = L.add_cone(coll, "BUOY_bell", r1=0.09, r2=0.02, depth=0.12, verts=8, loc=(0, 0, 0.72), mat=mat("MAT_BRASS_AGED"))
    _attach(r, body, bell)
    return r


def build_prop_STALL(coll, loc=(0, 0, 0), rot=(0, 0, 0)):
    r = _root(coll, "PROP_STALL", loc)
    r.rotation_euler = rot
    legs = [L.add_cyl(coll, f"STALL_leg{i}", r=0.03, depth=0.7, verts=6,
                      loc=(dx, dy, 0.35), mat=mat("MAT_WOOD_ROTTED"))
            for i, (dx, dy) in enumerate([(-0.6, -0.4), (0.6, -0.4), (-0.6, 0.4), (0.6, 0.4)])]
    top = L.add_box(coll, "STALL_top", 1.5, 1.0, 0.05, loc=(0, 0, 0.72), rot=(RAD(8), 0, 0), mat=mat("MAT_WOOD_ROTTED"))
    _attach(r, *legs, top)
    return r


def build_prop_RAIL(coll, loc=(0, 0, 0), rot=(0, 0, 0), length=3.0):
    r = _root(coll, "PROP_RAIL", loc)
    r.rotation_euler = rot
    bar = L.add_tube(coll, "RAIL_bar", [(0, 0, 0.5), (length, 0, 0.5)], radius=0.025, sides=6, mat=mat("MAT_IRON_RUSTED"))
    posts = [L.add_cyl(coll, f"RAIL_post{i}", r=0.02, depth=0.5, verts=6,
                       loc=(length * i / 4, 0, 0.25), mat=mat("MAT_IRON_RUSTED")) for i in range(5)]
    _attach(r, bar, *posts)
    return r


# ---------------------------------------------------------------------- #
# characters
# ---------------------------------------------------------------------- #
def build_char_WICK(coll, loc=(0, 0, 0), rot_z=0.0, include_key=True,
                    include_spark=False, eyes_dark=False):
    r = _root(coll, "CHAR_WICK", loc)
    r.rotation_euler = (0, 0, rot_z)
    brass, polished = mat("MAT_BRASS_AGED"), mat("MAT_BRASS_POLISHED")
    parts = [
        L.add_cyl(coll, "WICK_legL", r=0.015, depth=0.10, verts=8, loc=(-0.03, 0, 0.05), mat=brass),
        L.add_cyl(coll, "WICK_legR", r=0.015, depth=0.10, verts=8, loc=(0.03, 0, 0.05), mat=brass),
        L.add_box(coll, "WICK_footL", 0.04, 0.07, 0.02, loc=(-0.03, -0.012, 0.01), mat=brass),
        L.add_box(coll, "WICK_footR", 0.04, 0.07, 0.02, loc=(0.03, -0.012, 0.01), mat=brass),
        L.add_cyl(coll, "WICK_torso", r=0.07, depth=0.16, verts=14, loc=(0, 0, 0.18), mat=brass),
        L.add_cyl(coll, "WICK_chest_glass", r=0.058, depth=0.05, verts=14,
                  rot=(RAD(90), 0, 0), loc=(0, -0.062, 0.20), mat=mat("MAT_GLASS_DRUM")),
        L.add_sphere(coll, "WICK_head", r=0.05, seg=12, rings=6, loc=(0, 0, 0.315), mat=brass),
        L.add_disc(coll, "WICK_eyeL", r=0.016, verts=12, rot=(RAD(90), 0, 0),
                   loc=(-0.022, -0.045, 0.32), mat=mat("MAT_IRON_RUSTED") if eyes_dark else mat("MAT_EYE_SHUTTER")),
        L.add_disc(coll, "WICK_eyeR", r=0.016, verts=12, rot=(RAD(90), 0, 0),
                   loc=(0.022, -0.045, 0.32), mat=mat("MAT_IRON_RUSTED") if eyes_dark else mat("MAT_EYE_SHUTTER")),
        L.add_cyl(coll, "WICK_armL", r=0.012, depth=0.13, verts=8, loc=(-0.085, 0, 0.22), rot=(0, RAD(18), 0), mat=brass),
        L.add_cyl(coll, "WICK_armR", r=0.012, depth=0.13, verts=8, loc=(0.085, 0, 0.22), rot=(0, RAD(-18), 0), mat=brass),
        L.add_sphere(coll, "WICK_shoulderL", r=0.02, seg=8, rings=4, loc=(-0.078, 0, 0.26), mat=brass),
        L.add_sphere(coll, "WICK_shoulderR", r=0.02, seg=8, rings=4, loc=(0.078, 0, 0.26), mat=brass),
    ]
    pts = [(0.03 * math.cos(t), -0.062, 0.20 + 0.03 * math.sin(t) + 0.0012 * t)
           for t in [i * 0.55 for i in range(20)]]
    parts.append(L.add_tube(coll, "WICK_coil", pts, radius=0.0035, sides=6, mat=polished))
    gauge = build_prop_GAUGE(coll, loc=(0, -0.095, 0.20))
    parts.append(gauge)
    if include_spark:
        parts.append(build_prop_SPARK(coll, loc=(0, -0.06, 0.20)))
    if include_key:
        parts.append(build_prop_KEY(coll, loc=(0, 0.085, 0.20), rot=(RAD(90), 0, 0)))
    _attach(r, *parts)
    return r


def build_char_SHIP(coll, loc=(0, 0, 0), rot_z=0.0):
    r = _root(coll, "CHAR_SHIP", loc)
    r.rotation_euler = (0, 0, rot_z)
    hull = L.add_box(coll, "SHIP_hull", 2.6, 0.7, 0.4, loc=(0, 0, 0.2), mat=mat("MAT_WOOD_ROTTED"))
    bow = L.add_cone(coll, "SHIP_bow", r1=0.35, r2=0.02, depth=0.8, verts=8,
                     rot=(0, RAD(-90), 0), loc=(1.6, 0, 0.25), mat=mat("MAT_WOOD_ROTTED"))
    mast = L.add_cyl(coll, "SHIP_mast", r=0.04, depth=1.8, verts=8, loc=(0, 0, 1.2), mat=mat("MAT_WOOD_ROTTED"))
    sail = L.add_plane(coll, "SHIP_sail", size=1.2, loc=(0, 0, 1.4), mat=mat("MAT_ROPE_HEMP"))
    sail.rotation_euler = (RAD(90), 0, RAD(90))
    light = L.add_sphere(coll, "SHIP_running_light", r=0.05, seg=8, rings=4, loc=(0, 0, 2.1), mat=mat("MAT_AMBER_GLOW"))
    _attach(r, hull, bow, mast, sail, light)
    return r


def build_char_CHILD(coll, loc=(0, 0, 0), rot_z=0.0, holding_key=False):
    r = _root(coll, "CHAR_CHILD", loc)
    r.rotation_euler = (0, 0, rot_z)
    coat = L.add_cone(coll, "CHILD_coat", r1=0.17, r2=0.09, depth=0.55, verts=12, loc=(0, 0, 0.33), mat=mat("MAT_CLOTH_COAT"))
    head = L.add_sphere(coll, "CHILD_head", r=0.11, seg=12, rings=6, loc=(0, 0, 0.72), mat=mat("MAT_SKIN_CHILD"))
    armL = L.add_cyl(coll, "CHILD_armL", r=0.03, depth=0.35, verts=8, loc=(-0.17, 0, 0.45), rot=(0, RAD(15), 0), mat=mat("MAT_CLOTH_COAT"))
    armR = L.add_cyl(coll, "CHILD_armR", r=0.03, depth=0.35, verts=8, loc=(0.17, 0, 0.45), rot=(0, RAD(-15), 0), mat=mat("MAT_CLOTH_COAT"))
    legL = L.add_cyl(coll, "CHILD_legL", r=0.03, depth=0.14, verts=8, loc=(-0.06, 0, 0.07), mat=mat("MAT_SKIN_CHILD"))
    legR = L.add_cyl(coll, "CHILD_legR", r=0.03, depth=0.14, verts=8, loc=(0.06, 0, 0.07), mat=mat("MAT_SKIN_CHILD"))
    parts = [coat, head, armL, armR, legL, legR]
    if holding_key:
        parts.append(build_prop_KEY(coll, loc=(0.2, -0.12, 0.5), rot=(RAD(60), 0, 0)))
    _attach(r, *parts)
    return r


# ---------------------------------------------------------------------- #
# environments
# ---------------------------------------------------------------------- #
def build_env_PLAZA(coll):
    quay = L.add_plane(coll, "PLAZA_quay", size=14, loc=(0, 2, 0), mat=mat("MAT_STONE_BARNACLE"))
    sea = L.add_plane(coll, "PLAZA_sea", size=60, loc=(26, 0, -0.35), mat=mat("MAT_WATER_DARK"))
    pillar = build_prop_PILLAR(coll, loc=(0, 1.5, 0))
    lit = build_prop_LAMP(coll, loc=(2.5, 1.0, 0), lit=True)
    unlit0 = build_prop_LAMP(coll, loc=(-2.0, 0.5, 0), lit=False)
    lamps = [L.instance_hierarchy(unlit0, coll, loc=(dx, dy, 0), suffix=f".I{i}")
             for i, (dx, dy) in enumerate([(-3.5, 0.2), (-5.0, 0.0), (-6.5, -0.2)])]
    roofs = [L.add_box(coll, f"PLAZA_roof{i}", 2.2, 1.6, 0.8, loc=(8 + i * 2.6, -3 + i * 2.2, -0.35),
                       rot=(0, 0, i), mat=mat("MAT_WOOD_ROTTED")) for i in range(5)]
    tower = L.add_cyl(coll, "PLAZA_tower_silhouette", r=1.8, depth=16, verts=12,
                      loc=(-30, 10, 7.5), mat=mat("MAT_IRON_RUSTED"))
    return {"pillar": (0, 1.5, 0), "lit_lamp": (2.5, 1.0, 1.66), "quay_edge_x": 4.0, "tower": (-30, 10, 0)}


def build_env_STREETS(coll):
    water = L.add_plane(coll, "STREETS_water", size=40, loc=(0, 4, 0.0), mat=mat("MAT_WATER_DARK"))
    roofs = [L.add_box(coll, f"STREETS_roof{i}", 2.4, 1.8, 0.9, loc=(-4 + i * 3.0, 6 + (i % 2) * 3, -0.2),
                       rot=(0, 0, i * 0.7), mat=mat("MAT_WOOD_ROTTED")) for i in range(4)]
    stall = build_prop_STALL(coll, loc=(-2, 2, 0.05))
    rail = build_prop_RAIL(coll, loc=(-1.5, -1.0, 0.2), length=4.0)
    coping = L.add_box(coll, "STREETS_coping", 8, 0.4, 0.6, loc=(0, -3.2, 0.3), mat=mat("MAT_STONE_BARNACLE"))
    walk = L.add_box(coll, "STREETS_gantry_walk", 7, 0.8, 0.06, loc=(0, 4.5, 0.8), mat=mat("MAT_IRON_RUSTED"))
    railL = build_prop_RAIL(coll, loc=(-3.2, 4.15, 0.8), length=6.4)
    railR = build_prop_RAIL(coll, loc=(-3.2, 4.85, 0.8), length=6.4)
    return {"stall": (-2, 2, 0), "gantry": (0, 4.5, 0.83), "coping": (0, -3.2, 0.6)}


def build_env_TOWER(coll, beacon_lit=False):
    floor = L.add_disc(coll, "TOWER_floor", r=3.0, verts=24, loc=(0, 0, 0), mat=mat("MAT_STONE_BARNACLE"))
    shell = L.add_cyl(coll, "TOWER_shell", r=2.2, depth=14, verts=16, loc=(0, 0, 7), mat=mat("MAT_IRON_RUSTED"))
    door = build_prop_DOOR(coll, loc=(2.15, 0, 0), rot=(0, 0, RAD(90)))
    stair = build_prop_STAIR(coll, loc=(0, 0, 0.2), steps=14)
    galrail = L.add_ring(coll, "TOWER_gallery_rail", radius=2.0, tube=0.03, seg=20, sides=6, loc=(0, 0, 13.5), mat=mat("MAT_IRON_RUSTED"))
    chamber = L.add_disc(coll, "TOWER_chamber_floor", r=2.1, verts=20, loc=(0, 0, 12.0), mat=mat("MAT_IRON_RUSTED"))
    burner = build_prop_BURNER(coll, loc=(0, 0, 12.0))
    beacon = L.add_sphere(coll, "TOWER_beacon", r=0.4, seg=12, rings=6, loc=(0, 0, 14.2),
                          mat=mat("MAT_WHITEGOLD") if beacon_lit else mat("MAT_GLASS_DRUM"))
    return {"door": (2.15, 0, 0), "chamber": (0, 0, 12.0), "burner_top": (0, 0, 13.4),
            "gallery": (0, 0, 13.5), "beacon": (0, 0, 14.2)}


# ---------------------------------------------------------------------- #
# scene specs  (master axis: sea/ship +X, tower -X)
# ---------------------------------------------------------------------- #
SCENE_SPECS = {
    "SC01": dict(env="PLAZA", world=(0.05, 0.09, 0.11), world_strength=0.6,
        lights=[("SUN", 2.0, (0.5, 0.8, 0.9), (-6, -6, 5), (RAD(55), 0, RAD(-45))),
                ("POINT", 50.0, (1.0, 0.55, 0.2), (2.5, 1.0, 1.7))],
        actors=[("WICK", dict(), (0.3, -0.5, 0), 0.0)],
        props=[("PROP_POLE", dict(), (0.9, -0.6, 0.02), (0, RAD(90), 0))],
        camera=dict(lens=24, loc=(0.3, -7, 2.6), rot=(RAD(75), 0, 0))),
    "SC02": dict(env="PLAZA", world=(0.05, 0.09, 0.11), world_strength=0.6,
        lights=[("SUN", 2.0, (0.5, 0.8, 0.9), (-6, -6, 5), (RAD(55), 0, RAD(-45))),
                ("POINT", 50.0, (1.0, 0.55, 0.2), (2.5, 1.0, 1.7)),
                ("POINT", 2000.0, (1.0, 0.6, 0.25), (60, 30, 2))],
        actors=[("WICK", dict(), (0, 1.2, 0), 0.0), ("SHIP", dict(), (60, 30, -0.3), RAD(-35))],
        props=[("PROP_BELLBUOY", dict(), (12, 8, -0.3), 0),
               ("PROP_POLE", dict(), (0.9, 1.0, 0.02), (0, RAD(90), 0))],
        camera=dict(lens=50, loc=(0, -5, 1.4), rot=(RAD(85), 0, 0))),
    "SC03": dict(env="PLAZA", world=(0.08, 0.10, 0.10), world_strength=0.8,
        lights=[("SUN", 3.0, (1.0, 0.75, 0.5), (5, -8, 6), (RAD(60), 0, RAD(30))),
                ("POINT", 60.0, (1.0, 0.55, 0.2), (-3.2, 2.0, 2.6))],
        actors=[("WICK", dict(), (-1.5, 0.5, 0), RAD(-90))],
        props=[("PROP_POLE", dict(), (-1.5, 0.5, 0.0), (0, 0, 0))],
        camera=dict(lens=24, loc=(0, -9, 7), rot=(RAD(58), 0, 0))),
    "SC04": dict(env="STREETS", world=(0.04, 0.06, 0.08), world_strength=0.7,
        lights=[("SUN", 4.0, (0.5, 0.6, 0.7), (3, -5, 7), (RAD(40), 0, RAD(20))),
                ("POINT", 10.0, (1.0, 0.6, 0.2), (-2, 1.3, 0.5))],
        actors=[("WICK", dict(), (-2, 1.6, 0.15), 0.0)],
        props=[("PROP_POLE", dict(), (-2, 1.6, 0.0), (0, 0, 0))],
        camera=dict(lens=24, loc=(-2, -4, 1.0), rot=(RAD(80), 0, 0))),
    "SC05": dict(env="STREETS", world=(0.04, 0.06, 0.08), world_strength=0.7,
        lights=[("SUN", 4.0, (0.5, 0.6, 0.7), (3, -5, 7), (RAD(40), 0, RAD(20))),
                ("POINT", 20.0, (1.0, 0.62, 0.18), (0, 4.3, 1.1))],
        actors=[("WICK", dict(include_spark=True), (0, 4.5, 0.83), RAD(-90))],
        props=[("PROP_POLE", dict(), (0.9, 4.6, 0.85), (0, RAD(80), 0))],
        camera=dict(lens=28, loc=(0, -1, 1.6), rot=(RAD(80), 0, 0))),
    "SC06": dict(env="TOWER", world=(0.04, 0.06, 0.08), world_strength=0.7,
        lights=[("SUN", 5.0, (0.55, 0.65, 0.75), (8, -4, 8), (RAD(50), 0, RAD(60))),
                ("POINT", 10.0, (1.0, 0.6, 0.2), (2.6, 0, 0.4))],
        actors=[("WICK", dict(include_spark=True), (2.9, 0, 0), RAD(90))],
        props=[],
        camera=dict(lens=24, loc=(7, 0, 1.0), rot=(RAD(85), 0, RAD(90)))),
    "SC07": dict(env="TOWER", world=(0.05, 0.06, 0.08), world_strength=0.9,
        lights=[("SUN", 8.0, (0.9, 0.95, 1.0), (6, 4, 12), (RAD(35), 0, RAD(140))),
                ("POINT", 15.0, (1.0, 0.62, 0.18), (2.3, 0, 6.2))],
        actors=[("WICK", dict(include_spark=True), (2.25, 0, 6.0), RAD(90))],
        props=[("PROP_POLE", dict(), (2.35, 0.2, 5.4), (RAD(20), RAD(10), 0))],
        camera=dict(lens=24, loc=(9, -3, 7), rot=(RAD(85), 0, RAD(70)))),
    "SC08": dict(env="TOWER", world=(0.01, 0.01, 0.012), world_strength=0.3,
        lights=[("POINT", 15.0, (1.0, 0.6, 0.2), (0.9, 0, 12.4)),
                ("AREA", 2000.0, (1.0, 0.85, 0.55), (0, 0, 14.0))],
        actors=[("WICK", dict(include_spark=True), (0.9, 0, 12.0), RAD(90))],
        props=[("PROP_POLE", dict(), (1.3, -0.4, 12.0), (0, RAD(80), 0))],
        camera=dict(lens=18, loc=(2.0, -1.2, 12.6), rot=(RAD(85), 0, RAD(60)))),
    "SC09": dict(env="TOWER", beacon_lit=True, world=(0.10, 0.08, 0.07), world_strength=0.8,
        lights=[("SPOT", 5000.0, (1.0, 0.85, 0.55), (0, 0, 14.2), (RAD(90), 0, RAD(-90)), 0.5),
                ("SUN", 3.0, (1.0, 0.6, 0.4), (10, -6, 2), (RAD(80), 0, RAD(60)))],
        actors=[("SHIP", dict(), (60, 20, -0.3), RAD(-90)),
                ("WICK", dict(include_spark=True), (0.9, 0, 12.0), RAD(90))],
        props=[("PROP_BELLBUOY", dict(), (14, 6, -0.3), 0)],
        camera=dict(lens=35, loc=(-5, 0, 14.6), rot=(RAD(88), 0, RAD(-90)))),
    "SC10": dict(env="TOWER", world=(0.12, 0.08, 0.07), world_strength=0.9,
        lights=[("SUN", 4.0, (1.0, 0.65, 0.45), (6, -4, 15), (RAD(50), 0, RAD(55)))],
        actors=[("WICK", dict(include_key=False, eyes_dark=True), (0.6, 0, 12.0), RAD(105)),
                ("CHILD", dict(holding_key=True), (1.3, -0.7, 12.0), RAD(35))],
        props=[("PROP_POLE", dict(), (0.75, 0.15, 12.0), (0, RAD(85), 0))],
        camera=dict(lens=50, loc=(3.0, -2.0, 12.8), rot=(RAD(80), 0, RAD(55)))),
}

# ---------------------------------------------------------------------- #
# asset registry rows (consumed by build_manifests.py)
# ---------------------------------------------------------------------- #
SRC = "06_ASSETS/scripts/ams_assets.py#"
MSRC = "06_ASSETS/materials/ams_materials.py#"

ASSET_ROWS = [
    ("TEX_GAUGE_DIAL", "texture", "06_ASSETS/scripts/make_textures.py", []),
    ("TEX_NOISE_TILE", "texture", "06_ASSETS/scripts/make_textures.py", []),
    ("MAT_BRASS_AGED", "material", MSRC + "build_brass_aged", ["TEX_NOISE_TILE"]),
    ("MAT_BRASS_POLISHED", "material", MSRC + "build_brass_polished", []),
    ("MAT_IRON_RUSTED", "material", MSRC + "build_iron_rusted", ["TEX_NOISE_TILE"]),
    ("MAT_GLASS_DRUM", "material", MSRC + "build_glass_drum", []),
    ("MAT_WATER_DARK", "material", MSRC + "build_water_dark", ["TEX_NOISE_TILE"]),
    ("MAT_STONE_BARNACLE", "material", MSRC + "build_stone_barnacle", ["TEX_NOISE_TILE"]),
    ("MAT_WOOD_ROTTED", "material", MSRC + "build_wood_rotted", ["TEX_NOISE_TILE"]),
    ("MAT_ROPE_HEMP", "material", MSRC + "build_rope_hemp", []),
    ("MAT_CLOTH_COAT", "material", MSRC + "build_cloth_coat", []),
    ("MAT_SKIN_CHILD", "material", MSRC + "build_skin_child", []),
    ("MAT_AMBER_GLOW", "material", MSRC + "build_amber_glow", []),
    ("MAT_SPARK_GLOW", "material", MSRC + "build_spark_glow", []),
    ("MAT_WHITEGOLD", "material", MSRC + "build_whitegold", []),
    ("MAT_EYE_SHUTTER", "material", MSRC + "build_eye_shutter", []),
    ("MAT_GAUGE_DIAL", "material", MSRC + "build_gauge_dial", ["TEX_GAUGE_DIAL"]),
    ("PROP_KEY", "prop", SRC + "build_prop_KEY", ["MAT_BRASS_POLISHED"]),
    ("PROP_GAUGE", "prop", SRC + "build_prop_GAUGE", ["MAT_GAUGE_DIAL", "MAT_BRASS_AGED", "MAT_IRON_RUSTED"]),
    ("PROP_MAINSPRING", "prop", SRC + "build_prop_MAINSPRING", ["MAT_BRASS_POLISHED"]),
    ("PROP_POLE", "prop", SRC + "build_prop_POLE", ["MAT_IRON_RUSTED", "MAT_AMBER_GLOW", "MAT_WOOD_ROTTED"]),
    ("PROP_PILLAR", "prop", SRC + "build_prop_PILLAR", ["MAT_BRASS_AGED", "MAT_BRASS_POLISHED"]),
    ("PROP_LAMP", "prop", SRC + "build_prop_LAMP", ["MAT_IRON_RUSTED", "MAT_AMBER_GLOW", "MAT_WOOD_ROTTED"]),
    ("PROP_SPARK", "prop", SRC + "build_prop_SPARK", ["MAT_SPARK_GLOW", "MAT_GLASS_DRUM"]),
    ("PROP_DOOR", "prop", SRC + "build_prop_DOOR", ["MAT_IRON_RUSTED"]),
    ("PROP_STAIR", "prop", SRC + "build_prop_STAIR", ["MAT_IRON_RUSTED"]),
    ("PROP_SOCKET", "prop", SRC + "build_prop_SOCKET", ["MAT_BRASS_POLISHED", "MAT_IRON_RUSTED"]),
    ("PROP_BURNER", "prop", SRC + "build_prop_BURNER", ["MAT_IRON_RUSTED", "MAT_BRASS_AGED", "MAT_BRASS_POLISHED"]),
    ("PROP_BELLBUOY", "prop", SRC + "build_prop_BELLBUOY", ["MAT_IRON_RUSTED", "MAT_BRASS_AGED"]),
    ("PROP_STALL", "prop", SRC + "build_prop_STALL", ["MAT_WOOD_ROTTED"]),
    ("PROP_RAIL", "prop", SRC + "build_prop_RAIL", ["MAT_IRON_RUSTED"]),
    ("CHAR_WICK", "character", SRC + "build_char_WICK",
     ["MAT_BRASS_AGED", "MAT_BRASS_POLISHED", "MAT_GLASS_DRUM", "MAT_GAUGE_DIAL",
      "MAT_EYE_SHUTTER", "MAT_IRON_RUSTED", "PROP_KEY", "PROP_GAUGE", "PROP_SPARK"]),
    ("CHAR_SHIP", "character", SRC + "build_char_SHIP", ["MAT_WOOD_ROTTED", "MAT_ROPE_HEMP", "MAT_AMBER_GLOW"]),
    ("CHAR_CHILD", "character", SRC + "build_char_CHILD", ["MAT_CLOTH_COAT", "MAT_SKIN_CHILD", "PROP_KEY"]),
    ("LOC_PLAZA", "environment", SRC + "build_env_PLAZA",
     ["PROP_PILLAR", "PROP_LAMP", "MAT_STONE_BARNACLE", "MAT_WATER_DARK", "MAT_WOOD_ROTTED", "MAT_IRON_RUSTED"]),
    ("LOC_STREETS", "environment", SRC + "build_env_STREETS",
     ["PROP_STALL", "PROP_RAIL", "MAT_WATER_DARK", "MAT_WOOD_ROTTED", "MAT_STONE_BARNACLE", "MAT_IRON_RUSTED"]),
    ("LOC_TOWER", "environment", SRC + "build_env_TOWER",
     ["PROP_DOOR", "PROP_STAIR", "PROP_BURNER", "MAT_IRON_RUSTED", "MAT_STONE_BARNACLE", "MAT_WHITEGOLD", "MAT_GLASS_DRUM"]),
]

RIGS = [
    ("RIG_WICK", "CHAR_WICK", SRC + "build_char_WICK",
     ["CHAR_WICK(root)", "WICK_torso", "WICK_head", "WICK_eyeL", "WICK_eyeR",
      "WICK_armL", "WICK_armR", "WICK_legL", "WICK_legR", "PROP_KEY(back mount)"]),
    ("RIG_SHIP", "CHAR_SHIP", SRC + "build_char_SHIP",
     ["CHAR_SHIP(root)", "SHIP_hull", "SHIP_mast", "SHIP_sail"]),
    ("RIG_CHILD", "CHAR_CHILD", SRC + "build_char_CHILD",
     ["CHAR_CHILD(root)", "CHILD_coat", "CHILD_head", "CHILD_armL", "CHILD_armR",
      "CHILD_legL", "CHILD_legR"]),
]

CHAR_BUILDERS = {"WICK": build_char_WICK, "SHIP": build_char_SHIP, "CHILD": build_char_CHILD}
PROP_BUILDERS = {
    "PROP_KEY": build_prop_KEY, "PROP_GAUGE": build_prop_GAUGE, "PROP_MAINSPRING": build_prop_MAINSPRING,
    "PROP_POLE": build_prop_POLE, "PROP_PILLAR": build_prop_PILLAR, "PROP_LAMP": build_prop_LAMP,
    "PROP_SPARK": build_prop_SPARK, "PROP_DOOR": build_prop_DOOR, "PROP_STAIR": build_prop_STAIR,
    "PROP_SOCKET": build_prop_SOCKET, "PROP_BURNER": build_prop_BURNER, "PROP_BELLBUOY": build_prop_BELLBUOY,
    "PROP_STALL": build_prop_STALL, "PROP_RAIL": build_prop_RAIL,
}
ENV_BUILDERS = {"PLAZA": build_env_PLAZA, "STREETS": build_env_STREETS, "TOWER": build_env_TOWER}


# ---------------------------------------------------------------------- #
# scene orchestrator
# ---------------------------------------------------------------------- #
def build_scene(scene_id):
    spec = SCENE_SPECS[scene_id]
    L.configure_scene(scene_id)
    env_c = L.new_coll(f"{scene_id}_ENV")
    char_c = L.new_coll(f"{scene_id}_CHARS")
    prop_c = L.new_coll(f"{scene_id}_PROPS")
    light_c = L.new_coll(f"{scene_id}_LIGHTS")
    cam_c = L.new_coll(f"{scene_id}_CAM")

    env_kw = {"beacon_lit": True} if spec.get("beacon_lit") and spec["env"] == "TOWER" else {}
    ENV_BUILDERS[spec["env"]](env_c, **env_kw)

    for name, kw, loc, rotz in spec["actors"]:
        CHAR_BUILDERS[name](char_c, loc=loc, rot_z=rotz, **kw)
    for pid, kw, loc, rot in spec["props"]:
        ob = PROP_BUILDERS[pid](prop_c, loc=loc, **({k: v for k, v in kw.items()}))
        ob.rotation_euler = rot if isinstance(rot, tuple) else (0, 0, float(rot))

    for li in spec["lights"]:
        ltype, energy, color, loc = li[0], li[1], li[2], li[3]
        rot = li[4] if len(li) > 4 else (0, 0, 0)
        spot = li[5] if len(li) > 5 else 1.0
        L.add_light(light_c, f"{scene_id}_{ltype}_{len(list(light_c.objects))}",
                    ltype, energy=energy, color=color, loc=loc, rot=rot, spot_size=spot)

    L.add_camera(cam_c, f"CAM_{scene_id}_placeholder", **spec["camera"])
    L.set_world(spec["world"], spec.get("world_strength", 1.0))

    scene = bpy.context.scene
    return {
        "scene_id": scene_id,
        "frame_start": scene.frame_start, "frame_end": scene.frame_end,
        "fps": scene.render.fps,
        "res": (scene.render.resolution_x, scene.render.resolution_y),
        "objects": {c.name: len(list(c.objects)) for c in
                    (env_c, char_c, prop_c, light_c, cam_c)},
        "camera_set": scene.camera is not None,
    }
