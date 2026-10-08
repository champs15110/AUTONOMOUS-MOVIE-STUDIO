"""
Minimal structural stand-in for the `bpy` module.

PURPOSE: lets the procedural builder scripts in 06_ASSETS run on machines without
Blender so their Python logic (scene graph construction, frame ranges, render
settings, collection layout, material node wiring) is executed and asserted by
06_ASSETS/scripts/run_build_tests.py. It implements only the API surface the
studio's builders use. It performs NO rendering and NO geometry evaluation beyond
index validation of from_pydata.

HONESTY: passing the stub harness proves the scripts are logically coherent and
structurally correct; it does NOT prove they render correctly in real Blender.
The stub intentionally has no `bpy.app`, so save-to-.blend calls in the builders
are skipped here and only fire under a real Blender binary (cloud render layer).
"""

import os


class _KeyframePoint:
    def __init__(self, co):
        self.co = tuple(co)
        self.interpolation = "BEZIER"
        self.handle_left_type = "AUTO_CLAMPED"
        self.handle_right_type = "AUTO_CLAMPED"


class _FCurve:
    def __init__(self, data_path, array_index):
        self.data_path = data_path
        self.array_index = array_index
        self.keyframe_points = []


class _Action:
    def __init__(self):
        self.fcurves = []


class _AnimData:
    def __init__(self):
        self.action = _Action()


class Keyable:
    """Minimal animation_data/keyframe_insert matching the bpy API subset."""

    def _anim(self):
        ad = getattr(self, "_animation_data", None)
        if ad is None:
            ad = self._animation_data = _AnimData()
        return ad

    @property
    def animation_data(self):
        return self._anim()

    def keyframe_insert(self, data_path, index=-1, frame=0):
        value = getattr(self, data_path)
        if isinstance(value, (int, float)):
            chans = {0: float(value)}
        else:
            chans = {i: float(value[i]) for i in range(len(value))
                     if index in (-1, i)}
        ad = self._anim()
        for i, v in chans.items():
            fc = next((f for f in ad.action.fcurves
                       if f.data_path == data_path and f.array_index == i), None)
            if fc is None:
                fc = _FCurve(data_path, i)
                ad.action.fcurves.append(fc)
            fc.keyframe_points.append(_KeyframePoint((frame, v)))
        return True


class _Socket:
    def __init__(self, name):
        self.name = name
        self.default_value = None
        self.links = []


class _Sockets:
    """name-addressable socket bag; auto-creates sockets so scripts written for
    Blender 3.x/4.x input-name differences both resolve."""
    def __init__(self):
        self._d = {}

    def __getitem__(self, key):
        if key not in self._d:
            self._d[key] = _Socket(key)
        return self._d[key]

    def __contains__(self, key):
        return True

    def get(self, key, default=None):
        return self[key]


class _Node:
    def __init__(self, ntype, name):
        self.type = ntype
        self.name = name
        self.inputs = _Sockets()
        self.outputs = _Sockets()
        self.image = None
        self.location = (0.0, 0.0)


class _Nodes:
    def __init__(self):
        self._items = []

    def new(self, ntype, name=None):
        n = _Node(ntype, name or f"{ntype}.{len(self._items):03d}")
        self._items.append(n)
        return n

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def get(self, name):
        for n in self._items:
            if n.name == name:
                return n
        return None


class _Links:
    def __init__(self):
        self._items = []

    def new(self, a, b):
        self._items.append((a, b))
        return (a, b)

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)


class NodeTree:
    def __init__(self):
        self.nodes = _Nodes()
        self.links = _Links()


class _MeshMaterials:
    def __init__(self):
        self._items = []

    def append(self, mat):
        self._items.append(mat)

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)


class Mesh:
    def __init__(self, name):
        self.name = name
        self.vertices = []
        self.polygons = []
        self.materials = _MeshMaterials()

    def from_pydata(self, verts, edges, faces):
        nv = len(verts)
        for f in faces:
            for i in f:
                if not (0 <= i < nv):
                    raise IndexError(f"mesh {self.name}: face index {i} out of range (nv={nv})")
        self.vertices = [tuple(v) for v in verts]
        self.polygons = [tuple(f) for f in faces]

    def update(self):
        pass

    def validate(self):
        return True


class Object(Keyable):
    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.location = (0.0, 0.0, 0.0)
        self.rotation_euler = (0.0, 0.0, 0.0)
        self.scale = (1.0, 1.0, 1.0)
        self.parent = None
        self.children = []
        self.hide_render = False
        self.empty_display_size = 0.1

    def __repr__(self):
        return f"<Object {self.name}>"


class Light(Keyable):
    def __init__(self, name, ltype):
        if ltype not in ("POINT", "SUN", "SPOT", "AREA"):
            raise ValueError(f"unknown light type {ltype}")
        self.name = name
        self.type = ltype
        self.energy = 1000.0
        self.color = (1.0, 1.0, 1.0)
        self.size = 1.0
        self.spot_size = 1.0
        self.spot_blend = 0.3
        self.angle = 0.1
        self.shadow_soft_size = 0.1


class Camera:
    def __init__(self, name):
        self.name = name
        self.lens = 50.0
        self.clip_end = 1000.0
        self.sensor_width = 36.0


class Image:
    def __init__(self, name, filepath):
        self.name = name
        self.filepath = filepath
        self.size = (0, 0)


class Material:
    def __init__(self, name):
        self.name = name
        self.use_nodes = False
        self.node_tree = NodeTree()
        self.diffuse_color = (0.8, 0.8, 0.8, 1.0)


class World:
    def __init__(self, name):
        self.name = name
        self.use_nodes = False
        self.node_tree = NodeTree()


class _ObjBag:
    def __init__(self):
        self._items = []

    def link(self, obj):
        if obj not in self._items:
            self._items.append(obj)

    def unlink(self, obj):
        if obj in self._items:
            self._items.remove(obj)

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)


class Collection:
    def __init__(self, name):
        self.name = name
        self.objects = _ObjBag()
        self.children = _ObjBag()


class Render:
    def __init__(self):
        self.fps = 24
        self.resolution_x = 1280
        self.resolution_y = 720
        self.resolution_percentage = 100
        self.filepath = ""
        self.engine = "BLENDER_EEVEE_NEXT"


class Scene:
    def __init__(self, name="Scene"):
        self.name = name
        self.frame_start = 1
        self.frame_end = 1
        self.render = Render()
        self.camera = None
        self.world = None
        self.collection = Collection("Scene Collection")


class _Registry:
    def __init__(self, factory, *fargs):
        self._factory = factory
        self._fargs = fargs
        self._items = []

    def new(self, name, *args):
        obj = self._factory(name, *args)
        self._items.append(obj)
        return obj

    def get(self, name):
        for o in self._items:
            if o.name == name:
                return o
        return None

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)


class _Images(_Registry):
    def load(self, filepath, check_existing=True):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"bpy.data.images.load: missing {filepath}")
        img = Image(os.path.basename(filepath), filepath)
        self._items.append(img)
        return img


class _Objects(_Registry):
    def new(self, name, data=None):
        obj = Object(name, data)
        self._items.append(obj)
        return obj


class _Data:
    def __init__(self):
        self.collections = _Registry(Collection)
        self.meshes = _Registry(Mesh)
        self.materials = _Registry(Material)
        self.lights = _Registry(Light)
        self.cameras = _Registry(Camera)
        self.worlds = _Registry(World)
        self.images = _Images(Image, "x")
        self.objects = _Objects(Object)


def _reset():
    global data, context
    data = _Data()

    class _Ctx:
        scene = Scene()

    context = _Ctx()


_reset()
