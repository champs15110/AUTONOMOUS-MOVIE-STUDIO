"""
Local validation harness for the Blender pipeline on machines WITHOUT Blender.

Puts tools/blender_stub on sys.path so `import bpy` resolves to the structural
stub, then EXECUTES the real builder code:
  * every material builder,
  * every prop / character / environment builder,
  * all ten scene builders (frame range, fps, 1920x1080, camera, lights,
    collection layout checked against 02_SCREENPLAY/SHOT_LIST.json),
  * the instancing mechanism (linked duplicates must share mesh data).

Writes 06_ASSETS/BUILD_TEST_RESULTS.json consumed by build_manifests.py.

HONESTY: this proves the Python logic is coherent; it does not prove render
correctness in real Blender. That happens on the cloud render layer.

Run:  python3 06_ASSETS/scripts/run_build_tests.py
"""

import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "blender_stub"))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "06_ASSETS", "materials"))

import bpy  # noqa: E402  (stub)
import ams_assets as A  # noqa: E402
import ams_materials as M  # noqa: E402
import ams_blender_lib as L  # noqa: E402

SHOTS = json.load(open(os.path.join(ROOT, "02_SCREENPLAY", "SHOT_LIST.json"), encoding="utf-8"))
SC_REC = {s["scene_id"]: s for s in SHOTS["scenes"]}

results = {"utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "harness": "tools/blender_stub (structural, no rendering)", "checks": []}


def check(name, fn):
    try:
        detail = fn()
        results["checks"].append({"name": name, "status": "PASS", "detail": detail})
        return True
    except Exception as e:  # noqa: BLE001
        results["checks"].append({"name": name, "status": "FAIL", "detail": f"{type(e).__name__}: {e}"})
        return False


def objs(coll):
    return list(coll.objects)


# ---- materials -------------------------------------------------------- #
for mid, fn in M._BUILDERS.items():
    check(f"material {mid}", lambda fn=fn, mid=mid: f"{len(fn().node_tree.nodes)} nodes")

# ---- textures --------------------------------------------------------- #
for tex in ("gauge_dial.png", "noise_tile.png"):
    def run_tex(tex=tex):
        p = os.path.join(ROOT, "06_ASSETS", "textures", tex)
        assert os.path.exists(p), f"missing {p}"
        return f"{os.path.getsize(p)} bytes"
    check(f"texture {tex}", run_tex)

# ---- standalone asset builds ------------------------------------------ #
PROP_TESTS = [("PROP_KEY", A.build_prop_KEY), ("PROP_GAUGE", A.build_prop_GAUGE),
              ("PROP_MAINSPRING", A.build_prop_MAINSPRING), ("PROP_POLE", A.build_prop_POLE),
              ("PROP_PILLAR", A.build_prop_PILLAR), ("PROP_LAMP", A.build_prop_LAMP),
              ("PROP_SPARK", A.build_prop_SPARK), ("PROP_DOOR", A.build_prop_DOOR),
              ("PROP_STAIR", A.build_prop_STAIR), ("PROP_SOCKET", A.build_prop_SOCKET),
              ("PROP_BURNER", A.build_prop_BURNER), ("PROP_BELLBUOY", A.build_prop_BELLBUOY),
              ("PROP_STALL", A.build_prop_STALL), ("PROP_RAIL", A.build_prop_RAIL)]
for pid, fn in PROP_TESTS:
    def run_prop(fn=fn, pid=pid):
        c = bpy.data.collections.new(f"T_{pid}")
        root = fn(c)
        n = len(objs(c))
        assert n >= 2, f"{pid} too few objects"
        assert root.children, f"{pid} root has no children"
        return f"{n} objects"
    check(f"asset {pid}", run_prop)

for cid, fn, kw in [("CHAR_WICK", A.build_char_WICK, {}),
                    ("CHAR_WICK_shell", A.build_char_WICK, dict(include_key=False, eyes_dark=True)),
                    ("CHAR_SHIP", A.build_char_SHIP, {}),
                    ("CHAR_CHILD", A.build_char_CHILD, dict(holding_key=True))]:
    def run_char(fn=fn, kw=kw, cid=cid):
        c = bpy.data.collections.new(f"T_{cid}")
        root = fn(c, **kw)
        n = len(objs(c))
        assert n >= 6, f"{cid} too few objects"
        return f"{n} objects"
    check(f"asset {cid}", run_char)

for eid, fn in [("LOC_PLAZA", A.build_env_PLAZA), ("LOC_STREETS", A.build_env_STREETS),
                ("LOC_TOWER", A.build_env_TOWER)]:
    def run_env(fn=fn, eid=eid):
        c = bpy.data.collections.new(f"T_{eid}")
        lm = fn(c)
        n = len(objs(c))
        assert n >= 6, f"{eid} too few objects"
        assert isinstance(lm, dict) and lm, "no landmarks"
        return f"{n} objects, landmarks {sorted(lm)}"
    check(f"asset {eid}", run_env)

# ---- instancing shares mesh data -------------------------------------- #
def run_instancing():
    c = bpy.data.collections.new("T_INST")
    src = A.build_prop_LAMP(c, loc=(0, 0, 0), lit=False)
    dup = None
    src_post = next(o for o in objs(c) if o.name == "LAMP_post")
    dup = L.instance_hierarchy(src, c, loc=(3, 0, 0), suffix=".I0")
    dup_post = next(o for o in objs(c) if o.name == "LAMP_post.I0")
    assert dup_post.data is src_post.data, "instance does not share mesh data"
    return "linked duplicate shares mesh data"
check("instancing mechanism", run_instancing)

# ---- scenes ----------------------------------------------------------- #
for sid in [s["scene_id"] for s in SHOTS["scenes"]]:
    def run_scene(sid=sid):
        bpy._reset()
        # re-import ams modules see fresh bpy data
        summ = A.build_scene(sid)
        rec = SC_REC[sid]
        assert summ["fps"] == 24, "fps"
        assert summ["res"] == (1920, 1080), "resolution not 16:9 1080p"
        assert summ["frame_start"] == rec["frame_in"], "frame_in"
        assert summ["frame_end"] == rec["frame_out"], "frame_out"
        assert summ["camera_set"], "no camera"
        assert summ["objects"][f"{sid}_ENV"] >= 5, "environment empty"
        assert summ["objects"][f"{sid}_CHARS"] >= 1, "no characters"
        assert summ["objects"][f"{sid}_LIGHTS"] >= 1, "no lights"
        assert summ["objects"][f"{sid}_CAM"] == 1, "camera placeholder count"
        return (f"frames {summ['frame_start']}-{summ['frame_end']}, "
                f"objects {summ['objects']}, lights ok, camera ok")
    check(f"scene {sid}", run_scene)

fails = [c for c in results["checks"] if c["status"] == "FAIL"]
results["total"] = len(results["checks"])
results["passed"] = len(results["checks"]) - len(fails)
results["failed"] = len(fails)
results["overall"] = "PASS" if not fails else "FAIL"

out = os.path.join(ROOT, "06_ASSETS", "BUILD_TEST_RESULTS.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
print(f"{results['passed']}/{results['total']} checks passed -> {out}")
for c in fails:
    print("FAIL:", c["name"], c["detail"])
sys.exit(0 if not fails else 1)
