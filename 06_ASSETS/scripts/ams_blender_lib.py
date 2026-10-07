"""
ams_blender_lib - shared helpers for every asset/scene builder in this studio.

Works under a REAL Blender python (`blender -b -P script.py`) and under the
structural stub at tools/blender_stub (for local testing without Blender).
Scripts that import this module must only use the API surface implemented in
tools/blender_stub/bpy/__init__.py.

Conventions:
  * 24 fps, 1920x1080 (16:9), sRGB - from MASTER_CONFIG target_spec.
  * one collection per layer: SCnn_ENV / SCnn_CHARS / SCnn_PROPS / SCnn_LIGHTS / SCnn_CAM.
  * assets are built once into their own collection and reused (no duplication).
  * units: metres. WICK is 0.40 m tall.
"""

import json
import math
import os

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

FPS = 24
RES_X = 1920
RES_Y = 1080


# ---------------------------------------------------------------------- #
# data access
# ---------------------------------------------------------------------- #
def load_shot_list() -> dict:
    with open(os.path.join(ROOT, "02_SCREENPLAY", "SHOT_LIST.json"), encoding="utf-8") as f:
        return json.load(f)


def scene_record(scene_id: str) -> dict:
    j = load_shot_list()
    return next(s for s in j["scenes"] if s["scene_id"] == scene_id)


# ---------------------------------------------------------------------- #
# scene configuration
# ---------------------------------------------------------------------- #
def configure_scene(scene_id: str):
    sc = scene_record(scene_id)
    scene = bpy.context.scene
    scene.name = scene_id
    scene.frame_start = int(sc["frame_in"])
    scene.frame_end = int(sc["frame_out"])
    scene.render.fps = FPS
    scene.render.resolution_x = RES_X
    scene.render.resolution_y = RES_Y
    scene.render.resolution_percentage = 100
    return scene


def new_coll(name: str):
    coll = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if coll not in list(bpy.context.scene.collection.children):
        bpy.context.scene.collection.children.link(coll)
    return coll


def set_world(color, strength=1.0):
    scene = bpy.context.scene
    world = scene.world or bpy.data.worlds.new("AMS_world")
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    bg = nt.nodes.new("ShaderNodeBackground")
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg.inputs["Color"].default_value = (*color, 1.0)
    bg.inputs["Strength"].default_value = strength
    nt.links.new(bg.outputs[0], out.inputs[0])
    return world


# ---------------------------------------------------------------------- #
# geometry primitives (pure from_pydata; no bpy.ops, no bmesh)
# ---------------------------------------------------------------------- #
def _obj(name, verts, faces, coll, mat=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    if mat is not None:
        me.materials.append(mat)
    return ob


def add_box(coll, name, sx=1.0, sy=1.0, sz=1.0, loc=(0, 0, 0), rot=(0, 0, 0), mat=None):
    x, y, z = sx / 2, sy / 2, sz / 2
    v = [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
         (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]
    f = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    ob = _obj(name, v, f, coll, mat)
    ob.location = loc
    ob.rotation_euler = rot
    return ob


def add_cyl(coll, name, r=0.5, depth=1.0, verts=16, loc=(0, 0, 0), rot=(0, 0, 0), mat=None):
    n = max(3, int(verts))
    h = depth / 2
    bot = [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n), -h) for i in range(n)]
    top = [(x, y, h) for (x, y, _) in bot]
    v = bot + top
    f = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
    f += [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    ob = _obj(name, v, f, coll, mat)
    ob.location = loc
    ob.rotation_euler = rot
    return ob


def add_cone(coll, name, r1=0.5, r2=0.0, depth=1.0, verts=12, loc=(0, 0, 0), rot=(0, 0, 0), mat=None):
    n = max(3, int(verts))
    h = depth / 2
    bot = [(r1 * math.cos(2 * math.pi * i / n), r1 * math.sin(2 * math.pi * i / n), -h) for i in range(n)]
    v = list(bot)
    f = [tuple(range(n - 1, -1, -1))]
    if r2 > 1e-6:
        top = [(r2 * math.cos(2 * math.pi * i / n), r2 * math.sin(2 * math.pi * i / n), h) for i in range(n)]
        v += top
        f.append(tuple(range(n, 2 * n)))
        f += [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    else:
        v.append((0, 0, h))
        f += [(i, (i + 1) % n, n) for i in range(n)]
    ob = _obj(name, v, f, coll, mat)
    ob.location = loc
    ob.rotation_euler = rot
    return ob


def add_sphere(coll, name, r=0.5, seg=12, rings=6, loc=(0, 0, 0), mat=None):
    v = [(0, 0, r), (0, 0, -r)]
    f = []
    for j in range(1, rings):
        phi = math.pi * j / rings
        for i in range(seg):
            th = 2 * math.pi * i / seg
            v.append((r * math.sin(phi) * math.cos(th), r * math.sin(phi) * math.sin(th), r * math.cos(phi)))
    for i in range(seg):
        f.append((0, 2 + (i + 1) % seg, 2 + i))
    for j in range(rings - 2):
        base = 2 + j * seg
        for i in range(seg):
            f.append((base + i, base + (i + 1) % seg, base + seg + (i + 1) % seg, base + seg + i))
    base = 2 + (rings - 2) * seg
    for i in range(seg):
        f.append((base + i, base + (i + 1) % seg, 1))
    ob = _obj(name, v, f, coll, mat)
    ob.location = loc
    return ob


def add_disc(coll, name, r=0.5, verts=24, loc=(0, 0, 0), rot=(0, 0, 0), mat=None):
    n = max(3, int(verts))
    v = [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n), 0) for i in range(n)]
    v.append((0, 0, 0))
    f = [(i, (i + 1) % n, n) for i in range(n)]
    ob = _obj(name, v, f, coll, mat)
    ob.location = loc
    ob.rotation_euler = rot
    return ob


def add_plane(coll, name, size=1.0, loc=(0, 0, 0), mat=None):
    s = size / 2
    v = [(-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)]
    ob = _obj(name, v, [(0, 1, 2, 3)], coll, mat)
    ob.location = loc
    return ob


def add_tube(coll, name, points, radius=0.02, sides=6, mat=None):
    """sweep a circular cross-section along a polyline (springs, rails, coils)."""
    pts = [tuple(p) for p in points]
    if len(pts) < 2:
        raise ValueError("tube needs >=2 points")
    v, f = [], []
    for k, p in enumerate(pts):
        a = pts[max(0, k - 1)]
        b = pts[min(len(pts) - 1, k + 1)]
        dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
        L = math.sqrt(dx * dx + dy * dy + dz * dz) or 1.0
        tx, ty, tz = dx / L, dy / L, dz / L
        ux, uy, uz = (1, 0, 0) if abs(tx) < 0.9 else (0, 1, 0)
        # side = t x u
        sx, sy, sz = ty * uz - tz * uy, tz * ux - tx * uz, tx * uy - ty * ux
        SL = math.sqrt(sx * sx + sy * sy + sz * sz) or 1.0
        sx, sy, sz = sx / SL, sy / SL, sz / SL
        # up2 = s x t
        wx, wy, wz = sy * tz - sz * ty, sz * tx - sx * tz, sx * ty - sy * tx
        for i in range(sides):
            th = 2 * math.pi * i / sides
            ox = (sx * math.cos(th) + wx * math.sin(th)) * radius
            oy = (sy * math.cos(th) + wy * math.sin(th)) * radius
            oz = (sz * math.cos(th) + wz * math.sin(th)) * radius
            v.append((p[0] + ox, p[1] + oy, p[2] + oz))
    n = sides
    for k in range(len(pts) - 1):
        for i in range(n):
            f.append((k * n + i, k * n + (i + 1) % n, (k + 1) * n + (i + 1) % n, (k + 1) * n + i))
    ob = _obj(name, v, f, coll, mat)
    return ob


def add_ring(coll, name, radius=0.1, tube=0.02, seg=16, sides=6, loc=(0, 0, 0), rot=(0, 0, 0), mat=None):
    pts = [(radius * math.cos(2 * math.pi * i / seg), radius * math.sin(2 * math.pi * i / seg), 0)
           for i in range(seg)]
    pts.append(pts[0])
    ob = add_tube(coll, name, pts, radius=tube, sides=sides, mat=mat)
    ob.location = loc
    ob.rotation_euler = rot
    return ob


def add_empty(coll, name, loc=(0, 0, 0), size=0.1):
    ob = bpy.data.objects.new(name, None)
    ob.empty_display_size = size
    ob.location = loc
    coll.objects.link(ob)
    return ob


# ---------------------------------------------------------------------- #
# lights / camera
# ---------------------------------------------------------------------- #
def add_light(coll, name, ltype, energy=100.0, color=(1, 1, 1), loc=(0, 0, 1),
              rot=(0, 0, 0), size=1.0, spot_size=1.0):
    li = bpy.data.lights.new(name, ltype)
    li.energy = energy
    li.color = color
    if ltype == "AREA":
        li.size = size
    elif ltype in ("POINT", "SPOT"):
        li.shadow_soft_size = size
    else:  # SUN
        li.angle = 0.05
    if ltype == "SPOT":
        li.spot_size = spot_size
    ob = bpy.data.objects.new(name, li)
    ob.location = loc
    ob.rotation_euler = rot
    coll.objects.link(ob)
    return ob


def add_camera(coll, name, lens=50.0, loc=(0, -5, 1.5), rot=(math.radians(90), 0, 0)):
    ca = bpy.data.cameras.new(name)
    ca.lens = lens
    ca.clip_end = 5000.0
    ob = bpy.data.objects.new(name, ca)
    ob.location = loc
    ob.rotation_euler = rot
    coll.objects.link(ob)
    bpy.context.scene.camera = ob
    return ob


def parent(child, parent_ob):
    child.parent = parent_ob
    parent_ob.children.append(child)


def instance_hierarchy(root, coll, loc=(0, 0, 0), rot=(0, 0, 0), scale=1.0, suffix=""):
    """Linked duplicate of an asset hierarchy: new objects SHARE the source
    mesh data (true instancing - geometry is stored once and reused)."""
    made = {}

    def clone(ob):
        if ob.data is not None:
            c = bpy.data.objects.new(ob.name + suffix, ob.data)
        else:
            c = bpy.data.objects.new(ob.name + suffix, None)
            c.empty_display_size = ob.empty_display_size
        c.location = ob.location
        c.rotation_euler = ob.rotation_euler
        c.scale = ob.scale
        coll.objects.link(c)
        made[id(ob)] = c
        return c

    top = clone(root)
    stack = [root]
    while stack:
        p = stack.pop()
        for ch in p.children:
            cc = clone(ch)
            cc.parent = made[id(p)]
            made[id(p)].children.append(cc)
            stack.append(ch)
    top.location = (root.location[0] + loc[0], root.location[1] + loc[1], root.location[2] + loc[2])
    top.rotation_euler = rot
    top.scale = (scale, scale, scale)
    return top


def save_blend_if_real(path_rel_to_root):
    """Only fires under a real Blender binary (stub has no bpy.app)."""
    if getattr(bpy, "app", None) is not None:
        out = os.path.join(ROOT, path_rel_to_root)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=out)
        return out
    return None
