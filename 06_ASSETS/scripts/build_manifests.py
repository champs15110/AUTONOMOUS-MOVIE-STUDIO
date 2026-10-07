"""
Generate the Stage 05 pipeline manifests from the asset registry and the REAL
local test results (06_ASSETS/BUILD_TEST_RESULTS.json):

  06_ASSETS/ASSET_MANIFEST.json      - every asset: id/type/source/version/deps/status
  06_ASSETS/SCENE_MANIFEST.json      - every scene: builder/frames/fps/res/assets/status
  06_ASSETS/models/ASSET_INDEX.json  - model index (characters/props/environments)
  06_ASSETS/rigs/RIG_INDEX.json      - procedural hierarchy rig index
  06_ASSETS/materials/MATERIAL_INDEX.json - material index
  06_ASSETS/ENGINE_DECISION.json     - render/build engine decision with honest evidence

Statuses are never asserted by hand: an asset/scene is STUB_TESTED only if the
harness check for it passed; textures are GENERATED_LOCAL.

Run:  python3 06_ASSETS/scripts/build_manifests.py
"""

import json
import os
import shutil
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "blender_stub"))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "06_ASSETS", "materials"))

import ams_assets as A  # noqa: E402

NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
RES = json.load(open(os.path.join(ROOT, "06_ASSETS", "BUILD_TEST_RESULTS.json"), encoding="utf-8"))
SHOTS = json.load(open(os.path.join(ROOT, "02_SCREENPLAY", "SHOT_LIST.json"), encoding="utf-8"))
SC_REC = {s["scene_id"]: s for s in SHOTS["scenes"]}

PASS = {c["name"]: c for c in RES["checks"] if c["status"] == "PASS"}


def status_for(key):
    """key like 'asset PROP_KEY' / 'material MAT_X' / 'texture x.png' / 'scene SC01'"""
    return "STUB_TESTED" if key in PASS else "FAILED_LOCAL_HARNESS"


# ---------------------------------------------------------------------- #
# ASSET_MANIFEST
# ---------------------------------------------------------------------- #
assets = []
for aid, atype, source, deps in A.ASSET_ROWS:
    if atype == "texture":
        fname = "gauge_dial.png" if "GAUGE" in aid else "noise_tile.png"
        st = "GENERATED_LOCAL" if os.path.exists(os.path.join(ROOT, "06_ASSETS", "textures", fname)) else "MISSING"
        key = f"texture {fname}"
        st = status_for(key) if key in PASS or key in {c["name"] for c in RES["checks"]} else st
        if key in PASS:
            st = "GENERATED_LOCAL+STUB_TESTED"
    elif atype == "material":
        st = status_for(f"material {aid}")
    else:
        st = status_for(f"asset {aid}")
    assets.append({
        "asset_id": aid,
        "asset_type": atype,
        "source": source,
        "version": "1.0.0",
        "dependencies": deps,
        "status": st,
    })

manifest = {
    "schema_version": "1.0.0",
    "task_id": "T05_3D_ASSETS",
    "project_id": "AMS-2026-001",
    "film_title": SHOTS["film_title"],
    "created_utc": NOW,
    "populated_by": "06_ASSETS/scripts/build_manifests.py",
    "local_validation": RES["harness"],
    "test_results": "06_ASSETS/BUILD_TEST_RESULTS.json",
    "asset_count": len(assets),
    "assets": assets,
}
json.dump(manifest, open(os.path.join(ROOT, "06_ASSETS", "ASSET_MANIFEST.json"), "w",
          encoding="utf-8"), indent=2, ensure_ascii=False)

# ---------------------------------------------------------------------- #
# SCENE_MANIFEST
# ---------------------------------------------------------------------- #
scenes = []
for sc in SHOTS["scenes"]:
    sid = sc["scene_id"]
    spec = A.SCENE_SPECS[sid]
    used = [f"LOC_{spec['env']}"]
    used += [f"CHAR_{n}" for n, _k, _l, _r in spec["actors"]]
    used += [pid for pid, _k, _l, _r in spec["props"]]
    scenes.append({
        "scene_id": sid,
        "title": sc["slug"],
        "builder": f"06_ASSETS/scenes/build_{sid}.py",
        "independent": True,
        "frame_start": sc["frame_in"],
        "frame_end": sc["frame_out"],
        "fps": 24,
        "resolution": [1920, 1080],
        "aspect_ratio": "16:9",
        "collections": [f"{sid}_ENV", f"{sid}_CHARS", f"{sid}_PROPS", f"{sid}_LIGHTS", f"{sid}_CAM"],
        "assets_used": sorted(set(used)),
        "lights": len(spec["lights"]),
        "camera_placeholder": f"CAM_{sid}_placeholder",
        "blend_output": f"06_ASSETS/blender/scenes/{sid}.blend",
        "status": status_for(f"scene {sid}"),
        "test_detail": PASS.get(f"scene {sid}", {}).get("detail"),
    })

sman = {
    "schema_version": "1.0.0",
    "task_id": "T05_3D_ASSETS",
    "project_id": "AMS-2026-001",
    "created_utc": NOW,
    "local_validation": RES["harness"],
    "scene_count": len(scenes),
    "scenes": scenes,
}
json.dump(sman, open(os.path.join(ROOT, "06_ASSETS", "SCENE_MANIFEST.json"), "w",
          encoding="utf-8"), indent=2, ensure_ascii=False)

# ---------------------------------------------------------------------- #
# indexes
# ---------------------------------------------------------------------- #
os.makedirs(os.path.join(ROOT, "06_ASSETS", "models"), exist_ok=True)
os.makedirs(os.path.join(ROOT, "06_ASSETS", "rigs"), exist_ok=True)
os.makedirs(os.path.join(ROOT, "06_ASSETS", "blender"), exist_ok=True)

models = [a for a in assets if a["asset_type"] in ("character", "prop", "environment")]
json.dump({"schema_version": "1.0.0", "created_utc": NOW,
           "note": "Models are procedural bpy builders; no binary model files are produced locally. blend outputs land in 06_ASSETS/blender/scenes/ on the cloud layer.",
           "model_count": len(models), "models": models},
          open(os.path.join(ROOT, "06_ASSETS", "models", "ASSET_INDEX.json"), "w",
               encoding="utf-8"), indent=2, ensure_ascii=False)

rigs = [{"rig_id": r[0], "character": r[1], "source": r[2], "hierarchy": r[3],
         "type": "procedural_parent_hierarchy", "version": "1.0.0",
         "status": status_for(f"asset {r[1]}")} for r in A.RIGS]
json.dump({"schema_version": "1.0.0", "created_utc": NOW,
           "note": "Rigs are hierarchy-based (parent/child pivots). Full deformation rigs are a later animation-stage concern; no animation has been authored yet.",
           "rig_count": len(rigs), "rigs": rigs},
          open(os.path.join(ROOT, "06_ASSETS", "rigs", "RIG_INDEX.json"), "w",
               encoding="utf-8"), indent=2, ensure_ascii=False)

mats = [a for a in assets if a["asset_type"] == "material"]
json.dump({"schema_version": "1.0.0", "created_utc": NOW,
           "builders": "06_ASSETS/materials/ams_materials.py",
           "material_count": len(mats), "materials": mats},
          open(os.path.join(ROOT, "06_ASSETS", "materials", "MATERIAL_INDEX.json"), "w",
               encoding="utf-8"), indent=2, ensure_ascii=False)

# ---------------------------------------------------------------------- #
# ENGINE_DECISION
# ---------------------------------------------------------------------- #
blender_path = shutil.which("blender")
probe_dirs = [d for d in ("/opt", "/usr/local", "/snap", "/usr")
              if os.path.isdir(d) and any("blender" in n.lower() for n in os.listdir(d))]
decision = {
    "schema_version": "1.0.0",
    "task_id": "T05_3D_ASSETS",
    "created_utc": NOW,
    "decision": "BLENDER_BPY_PROCEDURAL",
    "summary": ("Build engine: Blender via procedural .bpy scripts (this repo). Blender is NOT "
                "installed in this runtime, so local execution is proven through the structural "
                "stub harness; real execution happens on a cloud Blender/render layer with the "
                "documented commands. Render engine: EEVEE-Next primary on the cloud layer, "
                "Cycles with denoising + low samples as quality fallback; the T12 assembly keeps "
                "the pre-existing python_software_raster fallback if no cloud layer materialises "
                "(risks R-001/R-002)."),
    "blender_local": {
        "available": blender_path is not None,
        "which": blender_path,
        "searched": ["PATH (shutil.which)", "/opt", "/usr/local", "/snap"],
        "found_dirs": probe_dirs,
    },
    "local_validation": {
        "harness": RES["harness"],
        "command": "python3 06_ASSETS/scripts/run_build_tests.py",
        "checks_total": RES["total"],
        "checks_passed": RES["passed"],
        "overall": RES["overall"],
        "results_file": "06_ASSETS/BUILD_TEST_RESULTS.json",
        "standalone_scene_run": "PYTHONPATH=tools/blender_stub python3 06_ASSETS/scenes/build_SC08.py (executed, exit 0)",
    },
    "cloud_execution": {
        "build_scene": "blender -b -P 06_ASSETS/scenes/build_SCnn.py   # saves 06_ASSETS/blender/scenes/SCnn.blend",
        "test_local_without_blender": "PYTHONPATH=tools/blender_stub python3 06_ASSETS/scenes/build_SCnn.py",
        "render_preview": "blender -b 06_ASSETS/blender/scenes/SCnn.blend -o //preview_#### -s <start> -e <end> -a",
    },
    "render_engine": {"primary": "BLENDER_EEVEE_NEXT", "fallback": "CYCLES_low_samples_denoised",
                      "last_resort": "python_software_raster (T12, R-001)"},
    "risks": ["R-001 ffmpeg absent locally", "R-002 blender absent locally"],
    "honesty_note": ("No Blender execution is claimed locally. STUB_TESTED means the builder logic "
                     "ran under the structural harness; visual/render correctness is unverified "
                     "until the cloud layer runs the same scripts."),
}
json.dump(decision, open(os.path.join(ROOT, "06_ASSETS", "ENGINE_DECISION.json"), "w",
          encoding="utf-8"), indent=2, ensure_ascii=False)

# ---------------------------------------------------------------------- #
# inventory coverage (acceptance: every T03-inventoried asset resolves or
# carries an explicit BLOCKED/DEFERRED entry with cause)
# ---------------------------------------------------------------------- #
INV = json.load(open(os.path.join(ROOT, "06_ASSETS", "ASSET_INVENTORY.json"), encoding="utf-8"))
status_by_id = {a["asset_id"]: a["status"] for a in assets}

MODEL_MAP = {
    "ASSET_MODEL_WICK": "CHAR_WICK", "ASSET_MODEL_SHIP": "CHAR_SHIP", "ASSET_MODEL_CHILD": "CHAR_CHILD",
    "ASSET_MODEL_PILLAR": "PROP_PILLAR", "ASSET_MODEL_LAMPPOST": "PROP_LAMP",
    "ASSET_MODEL_PLAZA_KIT": "LOC_PLAZA", "ASSET_MODEL_STREETS_KIT": "LOC_STREETS",
    "ASSET_MODEL_GANTRY": "LOC_STREETS", "ASSET_MODEL_STALL": "PROP_STALL", "ASSET_MODEL_RAIL": "PROP_RAIL",
    "ASSET_MODEL_TOWER": "LOC_TOWER", "ASSET_MODEL_STAIR": "PROP_STAIR", "ASSET_MODEL_DOOR": "PROP_DOOR",
    "ASSET_MODEL_BURNER": "PROP_BURNER", "ASSET_MODEL_SOCKET": "PROP_SOCKET", "ASSET_MODEL_KEY": "PROP_KEY",
    "ASSET_MODEL_GAUGE": "PROP_GAUGE", "ASSET_MODEL_MAINSPRING": "PROP_MAINSPRING",
    "ASSET_MODEL_POLE": "PROP_POLE", "ASSET_MODEL_SPARK": "PROP_SPARK", "ASSET_MODEL_BELLBUOY": "PROP_BELLBUOY",
}
MAT_MAP = {
    "MAT_BRASS_AGED": "MAT_BRASS_AGED", "MAT_VERDIGRIS": "MAT_BRASS_AGED",
    "MAT_IRON_RUSTED": "MAT_IRON_RUSTED", "MAT_STONE_WET": "MAT_STONE_BARNACLE",
    "MAT_WATER": "MAT_WATER_DARK", "MAT_GLASS_CHEST": "MAT_GLASS_DRUM",
    "MAT_EMBER": "MAT_SPARK_GLOW", "MAT_AMBER_LIGHT": "MAT_AMBER_GLOW", "MAT_OILSKIN": "MAT_CLOTH_COAT",
}
DEFERRED = {
    "ANIM_GAUGE_NEEDLE": ("T06_ANIMATION", "animation channel, not a build asset; needle geometry exists in PROP_GAUGE"),
    "GAIT_RHYTHM_TRACK": ("T09_AUDIO", "audio/animation timing data, not a 3D build asset"),
}

coverage = []
for x in INV["assets"]:
    iid, kind, path = x["asset_id"], x["kind"], x.get("path")
    if kind == "model":
        rid = MODEL_MAP[iid]
        os.makedirs(os.path.join(ROOT, path.rstrip("/")), exist_ok=True)
        with open(os.path.join(ROOT, path.rstrip("/"), ".gitkeep"), "a"):
            pass
        coverage.append({"inventory_id": iid, "kind": kind, "resolution": "RESOLVED_BY_BUILDER",
                         "resolved_to": rid, "status": status_by_id[rid],
                         "note": "procedural bpy builder is the source of truth; dir is the cloud export slot"})
    elif kind == "material":
        rid = MAT_MAP[iid]
        coverage.append({"inventory_id": iid, "kind": kind, "resolution": "RESOLVED_BY_BUILDER",
                         "resolved_to": rid, "status": status_by_id[rid],
                         "note": "T03 material name mapped to the procedural node material"})
    elif kind == "reference_image":
        ok = os.path.exists(os.path.join(ROOT, path))
        coverage.append({"inventory_id": iid, "kind": kind, "resolution": "EXISTS",
                         "resolved_to": path, "status": "EXISTS" if ok else "BLOCKED",
                         "note": "reference image from Stage 03" if ok else "missing file"})
    elif iid in DEFERRED:
        task, cause = DEFERRED[iid]
        coverage.append({"inventory_id": iid, "kind": kind, "resolution": "DEFERRED",
                         "resolved_to": task, "status": "DEFERRED", "note": cause})
    else:
        coverage.append({"inventory_id": iid, "kind": kind, "resolution": "BLOCKED",
                         "resolved_to": None, "status": "BLOCKED", "note": "unmapped inventory entry"})

unresolved = [c["inventory_id"] for c in coverage if c["status"] == "BLOCKED"]
manifest["inventory_coverage"] = coverage
manifest["inventory_unresolved"] = unresolved
json.dump(manifest, open(os.path.join(ROOT, "06_ASSETS", "ASSET_MANIFEST.json"), "w",
          encoding="utf-8"), indent=2, ensure_ascii=False)

print("manifests written:",
      "ASSET_MANIFEST", len(assets), "+ coverage", len(coverage),
      "| SCENE_MANIFEST", len(scenes),
      "| models", len(models), "| rigs", len(rigs), "| materials", len(mats))
bad = [a["asset_id"] for a in assets if "FAIL" in a["status"]] + \
      [s["scene_id"] for s in scenes if "FAIL" in s["status"]] + unresolved
print("non-passing statuses:", bad or "none")
