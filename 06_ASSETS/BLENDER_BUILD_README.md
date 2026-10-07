# BLENDER BUILD README — NINETY-TWO TURNS (Stage 05 / T05_3D_ASSETS)

This directory contains a **real, executable, procedural Blender production
pipeline**. Every model, material, rig and scene is Python (`bpy`) code — no
binary assets are hand-authored — so the whole film's 3D side can be rebuilt
from text on any Blender ≥ 3.x, locally or on a cloud render layer.

**Honesty boundary:** Blender is **not installed in this runtime** (checked
`PATH`, `/opt`, `/usr/local`, `/snap` — see `ENGINE_DECISION.json`). Therefore:

* locally we execute the builders through a **structural stub** of `bpy`
  (`tools/blender_stub/`) that validates scene-graph logic, frame ranges,
  render settings, collection layout and instancing;
* no `.blend` file, render or visual result is claimed to have been produced
  here. Visual correctness is verified only when the same scripts run on a
  real Blender binary.

## Layout

| Path | Contents |
|---|---|
| `scripts/ams_blender_lib.py` | shared helpers: scene config (24 fps, 1920×1080), primitives (`from_pydata` only — no `bpy.ops`), lights, camera, instancing, conditional `.blend` save |
| `scripts/ams_assets.py` | 3 characters, 14 props, 3 environments, scene specs, `build_scene()` orchestrator, asset/rig registry |
| `scripts/make_textures.py` | pure-Python PNG generator: `textures/gauge_dial.png` (0–100 dial, red 0–40 arc), `textures/noise_tile.png` |
| `scripts/write_scene_builders.py` | emits the ten standalone `scenes/build_SCnn.py` scripts |
| `scripts/run_build_tests.py` | local harness (stub bpy) — 49 checks, writes `BUILD_TEST_RESULTS.json` |
| `scripts/build_manifests.py` | regenerates every manifest/index + `ENGINE_DECISION.json` from registry + test results |
| `materials/ams_materials.py` | 15 procedural node materials (Principled/emission/noise-bump; dial uses generated coords, no UVs needed) |
| `scenes/build_SC01..10.py` | **independently executable** per-scene builders |
| `models/`, `rigs/`, `textures/` | indexes + generated textures; model dirs are cloud export slots |
| `blender/` | output slot for cloud-built `.blend` files (`blender/scenes/SCnn.blend`) |

## Run locally without Blender (structural validation)

```bash
python3 06_ASSETS/scripts/make_textures.py          # regenerate textures
python3 06_ASSETS/scripts/run_build_tests.py        # 49/49 checks
PYTHONPATH=tools/blender_stub python3 06_ASSETS/scenes/build_SC08.py   # any scene
python3 06_ASSETS/scripts/build_manifests.py        # regenerate manifests
```

## Run on a real Blender (cloud render layer)

```bash
blender -b -P 06_ASSETS/scenes/build_SC01.py        # builds + saves 06_ASSETS/blender/scenes/SC01.blend
# … one invocation per scene; scenes never depend on each other …
blender -b 06_ASSETS/blender/scenes/SC01.blend -o //preview_#### -s 1 -e 768 -a
```

The save step is automatic: `ams_blender_lib.save_blend_if_real()` fires only
when a real `bpy.app` exists and is skipped under the stub.

## Scene contract (every scene, verified by the harness)

* characters, props, environment, materials, lights, camera placeholder;
* frame range **exactly** the scene's `frame_in..frame_out` from
  `02_SCREENPLAY/SHOT_LIST.json` (contiguous across the film, 1–7248);
* 24 fps; 1920×1080 (16:9); world colour from the colour script.

## Reuse, not duplication

* Asset builders are single sources of truth; repeating set pieces (lamp
  posts, railings) are **linked duplicates** sharing mesh data
  (`lib.instance_hierarchy` — the harness asserts data sharing).
* Materials are memoised per Blender session; props composed inside characters
  (WICK's gauge/key/spark) reuse the prop builders.

## Manifests & engine decision

* `ASSET_MANIFEST.json` — 37 assets (2 textures, 15 materials, 14 props,
  3 characters, 3 environments) each with asset_id / asset_type / source /
  version / dependencies / status, **plus** `inventory_coverage` resolving all
  40 T03 inventory ids (30 builders STUB_TESTED, 8 reference images EXISTS,
  2 DEFERRED with cause: `ANIM_GAUGE_NEEDLE`→T06, `GAIT_RHYTHM_TRACK`→T09).
* `SCENE_MANIFEST.json` — 10 scenes, builder path, frames, fps, resolution,
  collections, assets used, lights, status.
* `models/ASSET_INDEX.json`, `rigs/RIG_INDEX.json`, `materials/MATERIAL_INDEX.json`.
* `ENGINE_DECISION.json` — build engine **BLENDER_BPY_PROCEDURAL** (cloud),
  render EEVEE-Next primary / Cycles fallback / `python_software_raster`
  last resort at T12 (risks R-001/R-002), with the executed local evidence.

## Deliberately not done yet

* no animation (hierarchy rigs only; deformation/keys are T06);
* no renders, no `.blend` files in Git (cloud outputs land in `blender/`);
* stub harness proves logic, not pixels — first real-Blender pass must be
  logged as a checkpoint before any render-stage claim.
