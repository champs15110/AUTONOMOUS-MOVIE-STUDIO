# CHANGELOG — AMS-2026-001

Reverse-chronological record of every meaningful change to this production.
Checkpoint rows are appended automatically by `tools/studio.py checkpoint`.

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
<!-- CHECKPOINT_TABLE_END -->
