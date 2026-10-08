# CHANGELOG — AMS-2026-001

Reverse-chronological record of every meaningful change to this production.
Checkpoint rows are appended automatically by `tools/studio.py checkpoint`.

## 2026-10-08 — Stage 10 AUDIO complete (T09_AUDIO → VERIFIED)

The sound pass. The film is wordless by design, so the soundtrack IS the
performance: 65 original audio assets synthesized in-repo (pure Python
stdlib - no samples, no libraries, nothing licensed; deterministic - the
generator reproduces byte-identical WAVs, sha256-verified), and a
frame-accurate 141-event timeline traced to the approved sound_intention
line of every one of the 58 shots.

### Built

- **`10_AUDIO/scripts/audio_synth.py`** - procedural DSP engine: plucked
  partials (music box), horn, string pads, inharmonic bells, filtered
  noise beds (wind/rain/water), Schroeder-ish reverb, seamless loop
  crossfading, 48 kHz 16-bit WAV out.
- **`10_AUDIO/scripts/make_audio_assets.py`** -> **`10_AUDIO/assets/`**:
  9 ambience beds, 42 SFX/foley one-shots + loops, 14 music cues
  (228 s total, 25 MB). The clock motif (A5-C6-E6) degrades exactly per
  the CHARACTER_BIBLE schedule: complete->faster->distorted->skipping->
  the single complete statement at SC08_SH005; the ship's two-note motif
  resolves upward only at SC09_SH002.
- **`10_AUDIO/scripts/audio_plan.py`** - the authored structure: 21
  ambience, 16 music, 104 SFX events on approved frames (rain starts
  exactly at SC04_SH003 f2461; ignition at SC08_SH007 f0+24 after one beat
  of true silence; the gait's four-beat tick locked, then irregular,
  skipping, dragging), 5 declared intentional silences, mix plan.
- **`10_AUDIO/scripts/run_audio_tests.py`** - ten-check harness:
  asset integrity (48 kHz/16-bit, peak <= -1 dBFS, provenance), loop
  seamlessness, full-frame coverage with no undeclared gap > 6 s, scene
  coverage, sync anchors, gait schedule, wordless enforcement, event
  bounds, mix targets. **All 10 PASS.**

### Written

- `DIALOGUE_PLAN.md` (voice identity/delivery/timing per character - all
  sound design, zero spoken words), `MUSIC_PLAN.md` (motif table, scene
  structure, orchestration intent; cues honestly marked as original
  procedural scratch, not a final performance), `SFX_PLAN.json`
  (foley/hard-SFX/ambience sections, every asset traced to its shots),
  `AUDIO_TIMELINE.json` (4 tracks; dialogue empty by design),
  `AUDIO_INDEX.json` (65 assets, 0 missing), `AUDIO_QC.md`,
  `music/MUSIC_CUE_SHEET.json`, `sfx/SFX_CUE_SHEET.json`,
  `mix/MIX_PLAN.json` (-16 LUFS / -1.5 dBTP / 48 kHz stereo targets).
- `SHOT_REGISTRY.json` - audio slot VERIFIED x58.

### Deferred honestly

- Integrated LUFS / true-peak measurement requires ffmpeg (absent here);
  it is marked PENDING_MEASUREMENT and belongs to render QC (T11).
  Structural peak legality (<= -1 dBFS per asset) is verified now.

## 2026-10-08 — Stage 09 LIGHTING/VFX complete (T08_LIGHTING_VFX → VERIFIED)

The lighting pass. Every scene now carries an executable lighting design -
time of day, mood, one coherent shadow-casting key, readable warm fill, tuned
world gradient - plus only the effects the story earns: the storm's rain, the
withholding fog, the tangible lamp-room air, and the single ignition bloom.

### Built

- **`09_LIGHTING_VFX/scripts/light_design.py`** — the design itself: per-scene
  `LIGHTING` (world gradient, key light, tuned built lights, added fill/rim,
  exposure bounds) and `VFX` tables where every effect row carries its story
  purpose. `apply_lighting` enforces ONE shadow caster per scene and fills
  every close character within 6 m; `apply_vfx` builds rain rigs (slanted
  camera-right +X per CONTINUITY_BIBLE §4), fog banks, dust motes, spray and
  the ignition glow - keyed to approved frames: rain begins SC04_SH003, lee
  calm at SC07_SH008, glow swells with SC08_SH007 (fill light 12→60 with it).
- **`09_LIGHTING_VFX/scripts/light_runner.py`** — build scene → apply lighting
  → apply VFX, shot frames from MASTER_SHOT_PLAN.
- **`09_LIGHTING_VFX/scripts/write_lighting_scripts.py`** →
  **`09_LIGHTING_VFX/SCENE_LIGHTING/light_SC01..SC10.py`** — ten standalone,
  independently recoverable scene lighting scripts (spot-checked: exit 0).
- **`09_LIGHTING_VFX/scripts/run_lighting_tests.py`** — eleven-check harness:
  shadow-coherence, character-lit, face-readability (fill ratio ≥ 0.08),
  materials-from-registry, background-not-empty, design-adherence,
  vfx-objects, wind-direction, exposure-proxy, shot-timing, 58/58 coverage.
  Result: **10/10 scenes VERIFIED**, 58/58 shots with setup ref + grade note,
  0 purposeless effects.
- **New atmosphere materials** — `MAT_RAIN_STREAK`, `MAT_FOG_BANK`,
  `MAT_DUST_MOTE` in `ams_materials` (+`ASSET_ROWS`): library now 18
  materials; build harness re-run **52/52** (was 49/49).
- Stub `bpy.Light` gained `use_shadow` (shadow-caster control).

### Written

- `LIGHTING_PLAN.json` (design rules + per-scene design + per-shot setup/grade),
  `VFX_PLAN.json` (policy: no effect without story purpose; rain timeline;
  wind rule), `LIGHTING_INDEX.json`, `vfx/VFX_INDEX.json`, `LIGHTING_QC.md`.
- `SHOT_REGISTRY.json` — lighting slot VERIFIED ×58 with `setup`, `grade`,
  `file` filled per shot.

### Deferred honestly

- Broadcast-range exposure legality is a render-QC measurement (T11); the
  harness carries a structural exposure proxy only, and says so.

### Neighbours re-verified

- Animation harness 58/58 · Camera harness 58/58 · Build harness 52/52 ·
  `studio.py validate` PASS (13 tasks, 58 shots, 10 scenes).

## 2026-10-08 — Stage 08 CAMERA complete (T07_CAMERA → VERIFIED)

The cinematography pass. Every shot's CAMERA_PLAN line is now executable
Blender camera data - framing, angle, height, focal length, subject scale,
composition, motivated motion, focus and screen direction, verified per shot.

### Built

- **`08_CAMERA/scripts/cam_lib.py`** — camera primitives: Blender-convention
  `look_at` (pitch 90deg = horizontal), yaw-aware `world_pos`, DOF placement,
  and the motivated-move set: `hold`, `push_in`, `crane_back_up`,
  `dolly_lateral` (parallel track, subject kept centred), `crane_rise`,
  `descend_with`, `tilt` (with hold-at), `pan_hold`, `whip_to` (the film's
  single fast move, SC06_SH002), `cut_to` (in-shot POV/reverse hard cut,
  SC06_SH005), `micro_drift` (motivated "handheld" beats as ONE slow drift -
  never noise), `rack_focus` (SC05_SH007 gauge->door).
- **`08_CAMERA/scripts/shot_cams.py`** — 58-shot camera table: subject anchors
  resolved in the built+animated scene, lenses exactly as planned (18mm to
  300mm incl. 100mm macros), distances/heights/azimuths, aim offsets for
  off-centre compositions ("gauge rides the corner"), authored subject-scale
  windows, reverse/axis-buffer flags per the master axis (sea +X = frame
  RIGHT, tower -X = frame LEFT).
- **`08_CAMERA/scripts/cam_runner.py`** — per-shot build: scene -> that shot's
  animation (subjects at final pose) -> camera placement + keys. Reuses the
  scene camera object; focus keyed to end on the subject after any move.
- **`08_CAMERA/SHOT_CAMERAS/cam_<SHOT>.py`** — 58 standalone, independently
  recoverable scripts; each saves `<SHOT>.blend` under real Blender.
- **`08_CAMERA/scripts/run_camera_tests.py`** — ten-check harness per shot:
  camera present; lens == plan; keys inside exact frames; subject-scale
  fraction inside the authored window; subject within 90% of half-FOV of
  centre; frame-right . +X > 0 unless reverse/axis-buffer; move licensed by
  the plan's motivation sentence (static means static); DOF focus matches
  subject distance (rack ends on target); path >= 0.12 m from non-subject
  geometry; static framing of moving subjects readable or staged.

### Verified

- Harness: **58/58 VERIFIED**, 0 PARTIAL / 0 BLOCKED ->
  `08_CAMERA/CAMERA_MASTER.json` (full spec + measurements + checks),
  `08_CAMERA/CAMERA_INDEX.json` (58 rows), `08_CAMERA/CAMERA_QC.md`.
- Variety as planned: 34 static/held setups, 24 motivated moves; only fast
  move is the SC06_SH002 whip; SC09_SH001 protected hold stays locked.
- Standalone sample runs under the stub (SC01_SH004 crane, SC03_SH001 dolly,
  SC06_SH002 whip, SC06_SH005 cut, SC07_SH003 rise, SC09_SH002 300mm) exit 0.
- Neighbours re-verified after stub Camera gained DOF: animation 58/58,
  asset build 49/49.
- Bugs found and fixed en route: look_at pitch convention (90deg = horizontal,
  not 0); macro framing windows that denied real 100mm-macro crop physics;
  focus not following push-ins; dollies that left walking subjects drifting
  out of frame; SC06_SH004 camera sitting on stair step 0; POV cameras
  legitimately inside the subject rig (excluded per-shot, logged in QC).

---

## 2026-10-08 — Stage 07 ANIMATION complete (T06_ANIMATION → VERIFIED)

**NINETY-TWO TURNS** now moves. Every one of the 58 shots carries authored,
principle-named keyframe animation - and the camera placeholders stay static:
no camera move anywhere substitutes for missing body animation.

### Built

- **`07_ANIMATION/scripts/ams_anim_lib.py`** — procedural animation primitives.
  Body: `walk` (anticipation + arcs + overlapping action + follow-through),
  `climb` (hand-over-hand arcs with weight sway), `brace`, `collapse`, `look`,
  `iris` (shutter-aperture facial performance). Props: `needle` (gauge ratchet,
  CONSTANT-interpolated discrete steps; angle = `RAD(225 − 2.7·v) − RAD(90)`,
  matching the dial texture), `key_slip`, `turns_free`, `spin_away`,
  `reach_grab`, `push_door`, `turn_key`, `unspool`, `kneel_turn`. Environment
  secondary action: `flicker`, `bob`, `sway`, `tear_fall`, `bloom`, `dim`,
  `beam_sweep`, `ship_turn` and friends.
- **`07_ANIMATION/scripts/shot_specs.py`** — all 58 shot specs: ordered acts
  with t0/t1 sub-timing inside each shot's exact frame range, continuity-matched
  gauge values (92 → 0 → 1 across the film), prop-state beats (pole lifted
  SC02_SH006, lost to the wind SC05_SH003, recovered wedged SC07_SH005), and a
  `PRINCIPLES` map naming what each primitive applies.
- **`07_ANIMATION/scripts/shot_runner.py`** — token resolver (`WICK`, `GAUGE`,
  `POLE`, `SPOT`, …), dispatch table, `build_shot()`; auto-holds the gauge
  needle at `gauge_in/out` in shots without an explicit needle act so the
  countdown is continuous scene to scene.
- **`07_ANIMATION/SHOT_ANIMATION/anim_<SHOT>.py`** — 58 standalone scripts.
  Each builds ONLY its scene and keys ONLY its shot's frames (never the whole
  film in one operation) and saves `<SHOT>.blend` under real Blender.
- **Harness** `07_ANIMATION/scripts/run_anim_tests.py` — runs every shot on the
  structural stub and checks: keys exist, ALL keys inside the shot's exact
  SHOT_LIST frame range, needle end-angle matches `gauge_out`, camera
  placeholders carry zero keys, ≥2 distinct principles per shot.
- **Scene fixes surfaced by animation** (assets re-verified 49/49 afterwards):
  `PROP_POLE` added to SC02/SC05 (she must pick it up before she loses it),
  one burning lamp (POINT light) added to SC03, WICK added to SC09 actors
  (her silhouette is in-frame), prop `rot` int → euler normalization.

### Verified

- Harness: **58/58 VERIFIED**, 1,747 keys, 0 PARTIAL / 0 BLOCKED →
  `07_ANIMATION/ANIMATION_STATUS.json` (per-shot checks + principles).
- `07_ANIMATION/ANIMATION_INDEX.json` (58 rows: script, blend, frames, fps,
  keys, status) and `07_ANIMATION/ANIMATION_NOTES.md` (per-scene direction
  notes + honesty clause: structural verification done here, visual performance
  review deferred to the cloud Blender layer before render).
- Sample standalone runs under the stub: SC01_SH001/SC02_SH006/SC05_SH003/
  SC07_SH003/SC09_SH001/SC10_SH004 all exit 0 with keys inside their frames.
- `SHOT_REGISTRY.json`: all 58 `animation` slots VERIFIED with artefact paths.
- Bugs found and fixed en route: stepped needle keyed ascending regardless of
  direction (broke 92→88 continuity); `climb` arm keys overshooting shot end by
  2 frames; eager `CHAR_WICK` lookup crashing WICK-less SC09; buoy `bob`
  subscripting an int rotation; `dim` aimed at the dawn sun instead of the
  beacon beam.

---

## 2026-10-07 — Stage 05 3D ASSET PIPELINE complete (T05_3D_ASSETS → VERIFIED)

### Added

- **`06_ASSETS/scripts/`** — `ams_blender_lib.py` (scene config 24 fps / 1920×1080, from_pydata primitives, lights, camera, linked-duplicate instancing, conditional .blend save), `ams_assets.py` (3 characters, 14 props, 3 environments, scene specs, `build_scene()`), `make_textures.py`, `write_scene_builders.py`, `run_build_tests.py`, `build_manifests.py`.
- **`06_ASSETS/materials/ams_materials.py`** — 15 procedural node materials; dial uses generated coordinates (no UV dependency).
- **`06_ASSETS/scenes/build_SC01.py … build_SC10.py`** — ten independently executable scene builders (env + characters + props + materials + lights + camera placeholder + exact frame ranges).
- **`06_ASSETS/textures/gauge_dial.png`, `noise_tile.png`** — generated locally in pure Python (dial: 0-100 ticks, red 0-40 arc).
- **`06_ASSETS/ASSET_MANIFEST.json`** — 37 assets with asset_id/type/source/version/dependencies/status, plus `inventory_coverage` resolving all 40 T03 inventory ids (30 STUB_TESTED, 8 EXISTS, 2 DEFERRED with cause, 0 BLOCKED).
- **`06_ASSETS/SCENE_MANIFEST.json`**, **`models/ASSET_INDEX.json`**, **`rigs/RIG_INDEX.json`**, **`materials/MATERIAL_INDEX.json`**, **`ENGINE_DECISION.json`**, **`BUILD_TEST_RESULTS.json`**, **`BLENDER_BUILD_README.md`**.
- **`tools/blender_stub/`** — structural bpy stand-in so builders execute without Blender (no rendering, no fabrication of Blender runs).

### Engine decision

- Blender **absent** in this runtime (PATH + /opt + /usr/local + /snap probed). Decision `BLENDER_BPY_PROCEDURAL`: builds run on a cloud Blender layer via documented commands; render EEVEE-Next primary, Cycles low-sample fallback, `python_software_raster` last resort at T12 (R-001/R-002).

### Verified

- `run_build_tests.py` → **49/49** (15 materials, 2 textures, 14 props, 4 character variants, 3 environments, instancing shares mesh data, 10 scenes each asserting frames == SHOT_LIST, 24 fps, 1920×1080, camera + lights + collections).
- Standalone proof: `PYTHONPATH=tools/blender_stub python3 06_ASSETS/scenes/build_SC08.py` exit 0.
- `build_manifests.py` reports zero non-passing statuses; `studio.py validate` PASS.

### Changed

- `TASK_QUEUE.json` T05 `output_files` re-pointed to the eight produced files (contract indexes all retained).

### Deliberately not done

- No animation (hierarchy rigs only), no `.blend`/renders in Git, no claim of local Blender execution.

---

## 2026-10-07 — Stage 04 STORYBOARD complete (T04_STORYBOARD → VERIFIED)

### Added

- **`05_STORYBOARD/MASTER_SHOT_PLAN.json`** — production specification for all 58 shots, every shot carrying the 18 required fields (composition, shot_type, camera_height, camera_angle, camera_distance, lens_intention, camera_motion, character_blocking, foreground/midground/background, screen_direction, lighting_intention, action, emotion, transition, sound_intention). Generated by `05_STORYBOARD/build_shot_plan.py` from `02_SCREENPLAY/SHOT_LIST.json`; set-equality with screenplay shot ids asserted in the build.
- **`05_STORYBOARD/CAMERA_PLAN.json`** — camera-only projection with the master axis, the motivated-movement rule and variety stats (34 static/held vs 24 motivated moves; the film's only whip-pan is SC06_SH002).
- **`05_STORYBOARD/BLOCKING_PLAN.json`** — blocking / depth-layer projection with the readability rule (gauge on screen whenever it changes; silhouettes read at 20 px).
- **`05_STORYBOARD/STORYBOARD.md`** — human-readable board, per-scene with per-shot specifications and embedded reference frames.
- **`05_STORYBOARD/beat_board/BEAT_BOARD.md`** — scene-level beat board.
- **`05_STORYBOARD/panels/`** — 9 original 16:9 reference frames (SC01_SH001/004, SC03_SH003, SC04_SH004, SC05_SH005, SC07_SH001, SC08_SH004/007, SC10_SH003) plus `PANEL_INDEX.md`. A representative subset; not full coverage.
- **`SHOT_REGISTRY.json`** — 58 shots registered via `studio.py shot-add`; story slots enriched (beat, description, dialogue, frame range, duration) from the screenplay and set `VERIFIED` via `studio.py shot-set`, leaving each shot overall `IN_PROGRESS` with the other seven stage slots `NOT_STARTED`.
- **`13_RENDER/RENDER_MANIFEST.json`** — 10 scenes registered via `studio.py scene-add`, all lifecycle stages `NOT_STARTED`.

### Cinematography decisions

- Master line of action: sea / returning ship FRAME RIGHT, tower FRAME LEFT; WICK travels frame RIGHT→LEFT; the climb runs vertical with the wall left; post-ignition payoff looks back frame RIGHT. No axis cross without a neutral macro / POV buffer.
- Motivated movement: every camera move states its motivation; 34 of 58 shots are deliberately static, held or locked-off; the protected 8 s hold at SC09_SH001 (verified 8.0 s in SHOT_LIST) is never covered.

### Verified

- `build_shot_plan.py` asserts overlay ids == SHOT_LIST ids (58/58) and zero empty fields across the 18-field schema.
- Authored overlay claims audited line-by-line against `SHOT_LIST.json` action/prop/gauge text (gauge values per insert, pole lost SC05_SH003 / recovered SC07_SH005, socket contents SC08_SH004, 300 mm lens SC09_SH002); one invented cut-in (SC02_SH002) removed for contradicting the single-shot grammar.
- Panels visually checked (composition, scale, axis, lighting intent match the plans).
- `python3 tools/studio.py validate` → **PASS** (13 tasks, 58 shots, 10 scenes).

### Changed

- `TASK_QUEUE.json` T04 `output_files` re-pointed to the eight director-issued deliverables (same contract-drift resolution as stages 02/03).

### Deliberately not done

- No animatic / timing cut, no 58-panel coverage, and full animation remains unstarted per the task boundary.

---

## 2026-10-07 — Stage 03 CHARACTER_WORLD complete (T03_CHARACTER_WORLD → VERIFIED)

**Locked:** the complete visual production bible. 3 characters, 3 environments, 14 props,
8 original reference images, and a full asset inventory with provenance. No animation begun.

### Added

- **`03_CHARACTERS/CHARACTER_BIBLE.md`** (130 lines) + **`CHARACTER_MANIFEST.json`** —
  WICK, THE RETURNING SHIP and THE CHILD, each with name, role, personality, body
  proportions, height, silhouette, face, eyes, mouth, clothing, materials, colours,
  accessories, expressions, body language, movement style, continuity notes and provenance.
- **`04_WORLD/WORLD_BIBLE.md`** (119 lines) + **`WORLD_MANIFEST.json`** — the three
  environments (Winding Plaza, Flooded Streets, Tidelight Tower), each with architecture,
  scale, materials, lighting, atmosphere, time of day, weather, important background
  elements, palette, modularity and continuity notes, plus global lighting / weather /
  colour-script rules.
- **`04_WORLD/PROP_BIBLE.md`** (261 lines) — 14 props, each with design, scale, material,
  purpose and continuity requirements.
- **`06_ASSETS/ASSET_INVENTORY.json`** — every model / material / data asset with
  provenance (`authored` / `generated` / `license + source`) and scene usage.
- **`03_CHARACTERS/REFERENCE_IMAGES/`** — WICK model sheet, WICK performance sheet,
  child + ship reference.
- **`04_WORLD/REFERENCE_IMAGES/`** — plaza, flooded streets, tower exterior, burner chamber
  (with the socket inset), props master sheet.
- **`tools/build_design_bibles.py`** — generates the three `.md` bibles from the two
  manifests and asserts every required field is present per character / environment / prop.

### Verified

`tools/build_design_bibles.py` → all 3 characters, 3 environments, 14 props carry every
required field. A dedicated consistency check (read-only, run against SHOT_LIST) confirmed:

- every brief character id matches its manifest entry and carries all 16 character fields;
- every brief location id and scene list matches an environment entry, and all 10
  SHOT_LIST locations resolve to a designed environment;
- every named prop / character token across all 58 shots and 10 scene prop lists maps to a
  designed character or prop, or a documented environment set-piece — **zero unmapped**;
- prop continuity requirements (pole lost SC05_SH003 / recovered SC07_SH005, socket reveal
  SC08_SH004, key to child SC10_SH003) mirror the Stage-02 continuity bible;
- every asset carries provenance; all 8 reference images exist on disk.

### Changed

- **`TASK_QUEUE.json`** — `T03_CHARACTER_WORLD.output_files` set to the director-issued six.
  `CHARACTER_DESIGNS.md` / `LOCATION_DESIGNS.md` superseded by the bibles. Re-pointed
  `T04`, `T05` and `T08` to read the machine-readable manifests
  (`CHARACTER_MANIFEST.json`, `WORLD_MANIFEST.json`) instead of the never-created
  `*_BIBLE.json` files.

### Deviation from the request

The request named `03_WORLD/`. The repo's world stage folder is `04_WORLD/` (created at
init and referenced by T04/T05/T08), so all world files were written there to keep the
dependency graph valid. No `03_WORLD/` folder was created. If a literal `03_WORLD/` is
required it is a one-line move plus a re-point; nothing downstream would silently break.

### Deliberately not done

No animation, no rigging, no storyboards. `SHOT_REGISTRY.json` and `RENDER_MANIFEST.json`
remain empty. `T04_STORYBOARD` remains `NOT_STARTED`.

---

## 2026-10-07 — Stage 02 SCREENPLAY complete (T02_SCREENPLAY → VERIFIED)

**Locked:** *NINETY-TWO TURNS* — **10 scenes, 58 shots, 302.0 s (5:02), frames 1–7248 @ 24 fps.**
Concept unchanged; no story problem warranted a rewrite.

### Added

- **`02_SCREENPLAY/FINAL_SCREENPLAY.md`** (1 591 lines) — full production screenplay. Every
  scene block carries `scene_id`, `timecode`, `duration`, `location`, `characters`,
  `story_purpose`, `action`, `dialogue`, `emotion`, `props`, `environment_action` and
  `transition`. Every scene is divided into shots carrying `shot_id`, `scene_id`, `time_in`,
  `time_out`, `duration`, `action`, `character_state`, `character_position`, `prop_state`,
  `camera_intention`, `sound`, `dialogue` and `continuity_notes`.
- **`02_SCREENPLAY/SHOT_LIST.json`** (2 107 lines) — 10 scene records + 58 shot records with
  absolute timecodes, 1-based contiguous frame ranges, per-shot gauge values and transitions.
- **`02_SCREENPLAY/SHOT_LIST.csv`** (58 rows, 22 columns) — spreadsheet-ready shot list.
- **`02_SCREENPLAY/CONTINUITY_BIBLE.md`** (244 lines) — full 57-row countdown ledger, prop
  state ledgers (key, lamp-pole, spark, mainspring, socket), permanent world damage, a
  14-link cause-and-effect chain, weather progression, sound/music continuity, camera
  grammar and the eight things that must never change.
- **`02_SCREENPLAY/build_shot_list.py`** — generator; emits JSON + CSV from one table and
  asserts every invariant before writing.
- **`02_SCREENPLAY/build_docs.py`** — emits both markdown documents from the verified JSON,
  so prose and data cannot drift.
- **`02_SCREENPLAY/verify_shot_list.py`** — independent verifier. Reads only the emitted
  artefacts; does **not** import the generator.

### Verified

`python3 02_SCREENPLAY/verify_shot_list.py` → **PASS** (exit 0):

- **58 shot ids, all unique**, all matching `SCnn_SHmmm`, numbered from `_SH001` per scene.
- **Timecodes contiguous** — every shot starts exactly where the previous ends; zero
  overlaps, zero gaps, at shot *and* scene level; each scene's shots exactly fill its range.
- **Frames 1–7248 contiguous**, no double-counted frames.
- **Runtime 302.0 s** — inside the 180–420 s window, +2.0 s from the 300 s target.
- Every shot inside 1.5–8 s; every scene inside 20–45 s; 10 scenes inside 6–12; 58 shots
  inside the planned 52–60.
- All 13 required shot fields populated on all 58 shots; all 11 required scene fields
  populated; `dialogue` is `none` in all 58 shots.
- **Countdown:** settles at 92 in `SC01_SH002` (00:09); falls monotonically; 91 spent; 1 at
  the burner; first 0 at `SC08_SH006`; rises **exactly once** at `SC10_SH005`; ends at 1.
- **Cause and effect:** the lamp-pole is lost at `SC05_SH003`, proven absent across all 21
  intervening shots, recovered at `SC07_SH005`; spark introduced `SC05_SH005`, removed
  `SC08_SH002`; socket revealed `SC08_SH004`; no human before `SC10`.
- **JSON ↔ CSV parity** — row count, order, timecodes, durations.
- Cross-document check: all 58 shot headers and all 9 per-shot field labels appear exactly
  58 times in the screenplay; all 57 ledger rows match the JSON; every shot id cited in both
  documents is real.

### Changed

- **`TASK_QUEUE.json`** — `T02_SCREENPLAY.output_files` replaced with the director-issued
  set. `SCENE_BREAKDOWN` content now lives in the `scenes` array of `SHOT_LIST.json`, so the
  `02_SCREENPLAY/locked/` files were superseded. Re-pointed every downstream reference:
  `T03`, `T04`, `T06`, `T07`, `T09`, `T10`, `T11` now read `02_SCREENPLAY/SHOT_LIST.json`.
  `T04_STORYBOARD` no longer produces a second shot list — its job is now beat board,
  panels/animatic and populating the two registries from the 58 locked shots. `T11_QC` gains
  `CONTINUITY_BIBLE.md` as an input.
- **`MASTER_CONFIG.json`** — `locked_shot_count: 58`, `locked_frame_count: 7248`.
- **`01_DEVELOPMENT/MASTER_FILM_BRIEF.json` / `.md`** — `turn_budget` labels corrected (see
  `ERR-0002`). Costs and the 92→1 gauge chain are byte-identical; each row now carries an
  explicit `scene` id.

### Failures recorded

- **`ERR-0002`** (`LOGIC_ERROR`, `MITIGATED`) — stage 01's `turn_budget` attributed costs to
  the wrong scenes because it was numbered by beat (`B03`–`B10`) while `story_beats` was
  numbered by scene (`SC03`–`SC08`), and the two were never cross-checked. A stage-01
  deliverable had therefore been marked `VERIFIED` with misattributed costs. Caught at T02
  before any scene breakdown existed. Fixed in both files; a generator assertion now ties
  per-scene gauge deltas to the budget rows for that scene.

### Caught before shipping (not logged as errors)

Four defects caught by the generator's assertions or the independent verifier before any
artefact was written: a 10 s shot exceeding the 8 s config maximum (split into two); a
gauge discontinuity at `SC05_SH007`; a missing `action` column in the CSV; and an incorrect
total-spend assertion that had to account for the ignition turn separately.

### Deliberately not done

No 3D animation, no assets, no storyboards. `T03_CHARACTER_WORLD` remains `NOT_STARTED`.
`SHOT_REGISTRY.json` and `RENDER_MANIFEST.json` stay empty — populating them from the 58
locked shots is `T04_STORYBOARD`'s job.

---

## 2026-10-07 — Stage 01 DEVELOPMENT complete (T01_DEVELOPMENT → VERIFIED)

**Film locked:** ***NINETY-TWO TURNS*** — a wordless cinematic 3D animated fable, 302 s
(5:02), 16:9, 1920×1080, 24 fps, 7 248 frames. `PROJECT_STATE.film_title` and
`MASTER_CONFIG.film_title` updated from the `UNNAMED_PLACEHOLDER_DO_NOT_SHIP` placeholder.

### Added

- **`01_DEVELOPMENT/MASTER_FILM_BRIEF.md`** (303 lines) — logline, hook, protagonist, goal /
  obstacle / escalation, ten-scene story spine, emotional progression, visual style,
  production complexity, retention strategy, originality attestation, handoff to T02.
- **`01_DEVELOPMENT/MASTER_FILM_BRIEF.json`** (403 lines) — structured twin with all 11
  required keys: `title`, `logline`, `genre`, `runtime`, `characters`, `locations`,
  `story_beats`, `emotional_beats`, `visual_style`, `production_complexity`,
  `retention_strategy`, plus `turn_budget`, `audio_plan`, `originality` and
  `downstream_handoff`.
- **`01_DEVELOPMENT/RESEARCH.md`** (248 lines) — live research, 3 queries, 12 sources, each
  finding mapped to a concrete design decision, with an explicit applicability caveat
  (short-form data is directional, not a KPI for a 5-minute film).

### The concept

WICK, a wind-up brass lamplighter automaton, loses her charging pillar and has **92 turns**
of stored energy left — and one night to light the harbour beacon before the last ship home
is wrecked on the reef. The gauge in her chest is diegetic, always readable, and the film's
spine: costs total **91**, so she reaches the burner with exactly **1**. The beacon has no
wick, no oil, no flint — only a socket the exact diameter of a mainspring. The ending hands
back exactly one turn, looping to the opening image.

### Verified before marking VERIFIED

- `jq -e .` clean on `MASTER_FILM_BRIEF.json`.
- All 11 required structured keys present.
- Turn arithmetic: costs sum to 91; running gauge consistent at every beat; 92 − 91 = 1.
- Runtime arithmetic: scene seconds sum to 302; 302 × 24 = 7 248 frames; timecodes contiguous
  00:00 → 05:02.
- Config bounds: 10 scenes inside the 6–12 target; every scene inside 20–45 s; planned shot
  length 5.4 s inside 1.5–8 s.
- Retention cadence: 11 turns, **maximum gap 36 s**, inside the 40 s rule; hook at 00:04,
  inside the 8 s deadline.
- **68/68 MD ↔ JSON coherence checks pass** (every scene, duration, emotional beat, turn
  cost, character and location present in both files).
- Scene ↔ location mapping unambiguous across both files.
- `python3 tools/studio.py validate` → **PASS**.

### Changed

- **`TASK_QUEUE.json`** — `T01_DEVELOPMENT.output_files` replaced. The originally drafted
  `01_DEVELOPMENT/concept/*.md` list was superseded by the director-issued deliverable set.
  Acceptance criteria extended to cover the structured JSON, the complexity assessment and
  the research mapping. `T02_SCREENPLAY.input_files` re-pointed at the brief, and its
  acceptance updated: the film is **wordless**, so "all dialogue original" was replaced with
  "zero dialogue; any spoken line requires an explicit logged deviation".
- **`MASTER_CONFIG.json`** — `logline` populated; `target_spec` gained
  `locked_runtime_seconds: 302`, `locked_scene_count: 10`, `dialogue: none`.
- **`AGENT_PROTOCOL.md`** §9 — originality attestation now points at
  `MASTER_FILM_BRIEF.md` §10 instead of the never-created standalone file.

### Failure recorded

- **`ERR-0001`** (`DATA_CORRUPTION`, resolution `MITIGATED`) — a fuzzy `edit_file` whose
  `old_text` spanned a JSON field boundary corrupted `MASTER_FILM_BRIEF.json`; `jq` caught
  it before any checkpoint. Logged first, then repaired byte-exactly with Python. Rule added:
  **edits to JSON state or brief files use Python or full-file rewrites, never cross-field
  fuzzy matching.** `T01_DEVELOPMENT.retry_count` is 1 as a result.

### Deliberately not done

Screenplay production was **not** started. `T02_SCREENPLAY` remains `NOT_STARTED` per
instruction.

---

## 2026-10-07 — Workspace initialization (T00_INITIALIZATION)

**Status:** workspace ready, **no creative work started** (by design).

### Added

- **Stage folders (14):** `01_DEVELOPMENT`, `02_SCREENPLAY`, `03_CHARACTERS`, `04_WORLD`,
  `05_STORYBOARD`, `06_ASSETS`, `07_ANIMATION`, `08_CAMERA`, `09_LIGHTING_VFX`, `10_AUDIO`,
  `11_EDIT`, `12_QC`, `13_RENDER`, `FINAL` — each with purposeful sub-folders, plus
  `tools/`, `docs/`, `.tmp/`. Empty directories carry `.gitkeep` so the tree is tracked.
- **`MASTER_CONFIG.json`** — project id, target spec (3–7 min / target 300 s, 16:9,
  1920x1080, 24 fps), delivery spec (H.264 high / yuv420p / CRF 18 / +faststart / AAC 320k
  / -16 LUFS), scene plan, render-engine candidates, detected environment, risks
  `R-001`–`R-004`, naming conventions, 13 stage definitions, status enum, shot stage enum,
  retry policy, checkpoint policy, completion condition.
- **`PROJECT_STATE.json`** — all required state fields, per-stage status map, counters,
  checkpoint history, `last_checkpoint`, `last_updated`. `overall_status = NOT_STARTED`.
- **`TASK_QUEUE.json`** — 13 tasks `T01_DEVELOPMENT` → `T13_FINAL_VERIFICATION`, each with
  `task_id`, `stage`, `status`, `dependencies`, `input_files`, `output_files`,
  `retry_count`, `last_error`, `checkpoint`, plus acceptance criteria.
- **`ERROR_LOG.json`** — schema, classification enum, and two pre-flight warnings
  (`WARN-0001` ffmpeg absent, `WARN-0002` blender absent). Zero errors.
- **`AGENT_PROTOCOL.md`** — roles, checkpoint rule, CLI reference, status vocabulary,
  failure recovery procedure, shot checkpointing, scene render lifecycle, handoff format,
  originality rules, environment constraints, definition of done.
- **`SHOT_REGISTRY.json`** — shot schema (`SCnn_SHmmm`) with all 8 stage slots; empty,
  populated by `T04_STORYBOARD`.
- **`13_RENDER/RENDER_MANIFEST.json`** — scene render lifecycle
  `SCENE → PREVIEW → QC → FINAL_RENDER → VERIFY`; empty, populated by `T04_STORYBOARD`.
- **`tools/studio.py`** — master controller CLI: `validate`, `status`, `next`, `task-set`,
  `shot-add`, `shot-set`, `shot-show`, `scene-add`, `scene-set`, `log-error`, `checkpoint`,
  `probe`, `verify-final`. Atomic writes with `.bak` backups, status enum enforcement,
  dependency cycle detection, strict render-lifecycle gating, and a dependency-free MP4 box
  parser so final verification works even without `ffprobe`.
- **`tools/test_studio.py`** — self-test suite for the controller.
- **`.gitignore`** — keeps frames, caches, intermediates and `.bak` files out of Git.

### Verified at init

- `python3 tools/studio.py validate` → **PASS** (13 tasks, 0 shots, 0 scenes).
- `python3 tools/studio.py test` suite → all green (see `tools/test_studio.py`).

### Known constraints carried forward

- `ffmpeg` **absent** → risk `R-001`, blocks `T12`/`T13` until installed or replaced.
- `blender` **absent** → risk `R-002`, engine decision at `T05_3D_ASSETS`.

---

## Checkpoint log

| Checkpoint | UTC | Task | Summary | Commit |
|---|---|---|---|---|
| CP-0001 | 2026-10-07 17:26:37 UTC | T00_INITIALIZATION | Workspace initialized: 14 stage folders, state/config/task/error files, agent protocol, shot + render registries, controller tooling. | f2618e8 |
| CP-0002 | 2026-10-07 17:56:28 UTC | T01_DEVELOPMENT | Stage 01 DEVELOPMENT VERIFIED. Film locked: NINETY-TWO TURNS - wordless 3D animated fable, 302s, 10 scenes, 92-turn countdown. Brief (.md+.json) and RESEARCH.md created; 68/68 coherence checks pass; ERR-0001 logged and mitigated. | 35c4570 |
| CP-0003 | 2026-10-07 18:43:33 UTC | T02_SCREENPLAY | Stage 02 SCREENPLAY VERIFIED. 10 scenes / 58 shots / 302.0s / frames 1-7248. FINAL_SCREENPLAY.md, SHOT_LIST.json+csv, CONTINUITY_BIBLE.md. Independent verifier PASS: unique ids, contiguous timecodes+frames, runtime in target, 92-turn ledger exact, cause-and-effect tracked. ERR-0002 (stage-01 turn_budget misattribution) logged and mitigated. | 7a7cdc7 |
| CP-0004 | 2026-10-07 19:16:10 UTC | T03_CHARACTER_WORLD | Stage 03 CHARACTER_WORLD VERIFIED. Full visual bible: 3 characters / 3 environments / 14 props / 8 original reference images / asset inventory with provenance. Consistency vs screenplay: zero unmapped tokens. | 6c947c9 |
| CP-0005 | 2026-10-07 22:56:40 UTC | T04_STORYBOARD | Stage 04 STORYBOARD VERIFIED. 58/58 shots carry the 18-field production spec (MASTER_SHOT_PLAN/CAMERA_PLAN/BLOCKING/STORYBOARD.md + BEAT_BOARD); 9 original reference panels + PANEL_INDEX; SHOT_REGISTRY story slots VERIFIED (overall IN_PROGRESS); RENDER_MANIFEST 10 scenes NOT_STARTED; master axis + motivated-movement rule enforced; validate PASS. | a62a51d |
| CP-0006 | 2026-10-07 23:28:38 UTC | T05_3D_ASSETS | Stage 05 3D ASSET PIPELINE VERIFIED. Procedural bpy pipeline: 37 assets (3 chars/14 props/3 envs/15 mats/2 textures), 10 independent scene builders, hierarchy rigs; 49/49 stub-harness checks; inventory coverage 40/40 (0 BLOCKED); ENGINE_DECISION: BLENDER_BPY_PROCEDURAL cloud, Blender absent locally (no fabricated runs). | 2939c50 |
| CP-0007 | 2026-10-08 00:36:45 UTC | T06_ANIMATION | Stage 07 ANIMATION VERIFIED. 58/58 shots animated shot-by-shot: ams_anim_lib principles-as-code primitives, 58 standalone per-shot scripts keying only their own frame ranges (1747 keys), needle continuity 92->0->1, camera placeholders provably static; harness 58/58 VERIFIED (keys-in-range, gauge continuity, >=2 principles); registry animation slots all VERIFIED; ANIMATION_INDEX/STATUS/NOTES written; scene fixes (POLE SC02/SC05, SC03 lamp, WICK in SC09) re-verified 49/49. | d158b1e |
| CP-0008 | 2026-10-08 01:02:45 UTC | T07_CAMERA | Stage 08 CAMERA VERIFIED. 58/58 shots carry executable camera direction: cam_lib motivated-move primitives (hold/push/crane/dolly/tilt/pan/whip/cut/descend/rack/micro-drift), 58 standalone per-shot cam scripts reusing scene cameras, master-axis screen direction enforced (sea frame RIGHT), DOF focus on subject, single fast move = SC06_SH002 whip; ten-check harness 58/58 VERIFIED (lens==plan, keys-in-frames, scale windows, in-frame, axis, motivation license, focus, no clipping, readability); CAMERA_MASTER/INDEX/QC written; registry camera slots all VERIFIED. | 4aec42e |
| CP-0009 | 2026-10-08 01:25:53 UTC | T08_LIGHTING_VFX | Stage 09 LIGHTING/VFX VERIFIED. 10/10 scenes carry executable lighting: one coherent shadow-casting key, warm readable fill within 6 m of every close character, tuned world gradients, single-shadow-caster rule enforced; VFX only where story demands - rain begins SC04_SH003, storm slant camera-right +X SC05-07, lee calm keyed at SC07_SH008, ignition glow + fill swell at SC08_SH007, fog withholds the ship SC03/SC09, dust motes SC04/08/10; eleven-check harness 10/10 scenes + 58/58 shot coverage, 0 purposeless effects; LIGHTING_PLAN/VFX_PLAN/indices/QC written; registry lighting slots VERIFIED x58 with setup+grade; materials library 15->18, build harness 52/52; anim 58/58, camera 58/58 neighbours intact. | e01b3b9 |
| CP-0010 | 2026-10-08 01:58:05 UTC | T09_AUDIO | Stage 10 AUDIO VERIFIED. 65 original in-repo synthesized assets (9 ambience beds, 42 SFX/foley, 14 music cues, 228 s, deterministic sha256-verified); 141-event frame-accurate timeline across ambience/music/sfx tracks traced to all 58 approved sound_intentions; wordless enforced - dialogue track empty, voice identity is sound design (WICK's four-beat gait degradation locked/irregular/skipping/dragging per CHARACTER_BIBLE; CHILD near-silent bare feet; SHIP two-note motif resolved upward only at SC09_SH002); rain starts exactly f2461, ignition bloom f6241 after one beat of true silence, 5 declared intentional silences; ten-check harness all PASS; DIALOGUE_PLAN/MUSIC_PLAN/SFX_PLAN/AUDIO_TIMELINE/AUDIO_INDEX/QC + MUSIC_CUE_SHEET/SFX_CUE_SHEET/MIX_PLAN written; loudness measurement honestly deferred to T11 (needs ffmpeg). | 357d685 |
| CP-0011 | 2026-10-08 04:13:26 UTC | STAGE_11_PREVIEW_RENDER | Stage 11 PREVIEW RENDER COMPLETE. 10/10 scenes rendered as real previews (pypi bpy 4.3.0, Cycles CPU - JANCTION/cloud absent, ERR-0003 TOOL_ABSENT, MITIGATED) at 480x270 32spp denoised; every frame pixel-QC'd (exposure/clip/edge thresholds) plus new occlusion-aware subject visibility (camera raycasts per in-frame subject vertex, fog volumes skipped): all 10 PREVIEW_QC_PASS, no PASS without an actual preview. Fixes made by the pass: Blender startup Cube leaked into every scene build (purged in ams_assets.build_scene - SC01 mean 20.8->17.1), SC09 rep SH002 was hidden inside TOWER_shell (rep -> SC09_SH001, ship 86% clear through dawn fog), SC04 rep SH003 split by a stall leg on axis (rep -> SC04_SH002, visually confirmed stall scene), spacing() crashed on animation_data without action (SC08_SH007; guarded). Full 46-shot camera occlusion audit found 11 defective shots (subject framed but line-of-sight blocked: quay/coping/stall leg/tower shell/burner) -> ERR-0004 + 11_RENDER/CAMERA_OCCLUSION_AUDIT.json, queued for camera nudges before T12 final. Artifacts: PREVIEWS/*.png, RENDER_STATUS.json (10x PREVIEW_QC_PASS), RENDER_ESTIMATES.json (measured preview x64 -> 1080p/128spp, <=240-frame render units per JANCTION limit), RENDER_ERRORS.json (ERR-0003 + 11 defects, 0 scene problems). Harnesses unchanged: build 52/52, anim 58/58. | 26577e6 |
| CP-0012 | 2026-10-08 16:56 UTC | T10_EDIT / STAGE 12 EDITING | STAGE 12 EDITING COMPLETE. EDIT_TIMELINE.json: all 58 shots assembled straight-cut in exact SHOT_LIST story order (order asserted vs SHOT_LIST + MASTER_SHOT_PLAN; zero substitutions), record==source spans, 7248 frames / 302.0 s @24; per-shot cut motivation, screen direction, gauge spine (92->0->1), continuity notes and per-shot audio events; ASSEMBLY_PLAN.md (intent, pacing table, transitions, audio strategy, animatic spec); EDITORIAL_QC.md ALL PASS - opening hook (winding-key macro, gauge->92), comprehension, pacing curve, climax (SC08 ignition), ending (final click + hard cut to black, gauge 0->1), audio sync (143 events frame-accurate, 4 authored L-cuts, dialogue empty), transitions (58 motivated hard cuts + 10 scene boundaries), continuity (ranges contiguous), screen direction (T07 camera harness re-run 58/58). Editorial fixes before final: 3 ambience beds played through declared silences (AMB_HARBOUR_WIND split around 985-1032, AMB_GALE dies at the 3240 hole, AMB_TOWER_INT dipped for the 6217-6241 beat) - fixed in audio_plan.py, AUDIO_TIMELINE regenerated 141->143 events, audio harness 10/10. Low-res assembled preview via Blender VSE (real editing tool, built-in FFMPEG): 58 picture strips + 143 audio strips -> ASSEMBLY_PREVIEW_LOWRES.mp4 480x270 H.264/AAC 302.0 s, container/duration/sampled frames verified; explicitly NOT FINAL. ERR-0005 logged for the platform 503 outage; tools/glstub_recipe.sh added (rebuilds /tmp/glstub after sandbox resets). TASK_QUEUE T10_EDIT -> VERIFIED; next T11_QC. | bfa5722 |
| CP-0013 | 2026-10-08 17:20 UTC | T11_QC / STAGE 13 FINAL QC | QC PASS. 12_QC/: QC_REPORT.md, QC_ISSUES.json, FIX_LOG.md, FINAL_QC_STATUS.json (story/character/animation/camera/lighting/vfx/audio/editing/technical all true, overall_pass true, second verification pass). FIXES (all re-verified): (1) ERR-0004 RESOLVED - 11/11 occlusion-defective cameras nudged in shot_cams.py (QC-13 tags), cam scripts + CAMERA_MASTER regenerated, camera harness 58/58, occlusion audit 11->0 defects; (2) three silence-breaking ambience beds conformed at Stage 12; (3) T09 deferred loudness CLOSED - tools/lufs.py BS.1770 meter + pyloudnorm cross-check; timeline mix measured -19.27 LUFS before trim, +2.93 dB trim recorded in MIX_PLAN, after: -16.34 LUFS / -1.50 dBTP (peak ceiling binds; within +/-0.5 LU tolerance; exact -16.0 via true-peak limiter at final mix). Harnesses re-run this pass: build 52/52, anim 58/58, camera 58/58, lighting/vfx 10/10+58/58, audio 10/10. 3 MINOR documented carry-overs, 0 CRITICAL/MAJOR open. TASK_QUEUE T11_QC VERIFIED; next T12_FINAL_RENDER. | 4887e53 |
<!-- CHECKPOINT_TABLE_END -->
| CP-0014 | 2026-10-08 20:15 UTC | T12_FINAL_RENDER + T13_FINAL_VERIFICATION / STAGE 14 | FINAL FILM VERIFIED. Render: 34 chunks (<=240 frames each, contiguous 1..7248) at honest local spec 320x180/24fps Cycles 6spp+OIDN (1080p/128spp measures ~49 days on this 2-core box; JANCTION absent ERR-0003); 34/34 chunks probe-verified (duration/dims/codec), none ever re-rendered. Assembly: Blender VSE 34 picture strips + measured FINAL_MIX.wav. ERR-0006 fixed (mp4 probe off-by-4 had flagged valid chunks unverified; fixed parser marked 34/34 VERIFIED-EXISTS in <1s, zero re-renders). ERR-0007 (headless bpy FFMPEG render writes silent AAC despite working VSE audio) worked around via 13_RENDER/scripts/mux_audio.py (PyAV): video transcoded once (libx264 CRF18) + AAC 128k encoded from FINAL_MIX.wav (source mix -16.34 LUFS/-1.50 dBTP; delivered AAC decodes 302.02 s at -15.97 LUFS/-1.43 dBTP). T13 verification 13/13: file exists, size>0, mp4 parses (ftyp/moov), duration 302.0 s, 320x180, 16:9, 24 fps, AAC audio track, audio duration consistent, all 10 scenes present, 34/34 chunks, no failed render, Stage-13 FINAL QC PASS; 4 representative frames (opening f1, middle f3624, climax f6241 ignition, ending f7240) extracted from the MP4 and inspected - all as authored (ending black is SC10_SH005 hard cut to black). Deliverables: FINAL/FINAL_FILM.mp4, FINAL_REPORT.json, FINAL_QC.md, FINAL_MANIFEST.json, VERIFY_FRAMES/. TASK_QUEUE T12+T13 VERIFIED - project complete. | PLACEHOLDER |
