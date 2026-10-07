# CHANGELOG — AMS-2026-001

Reverse-chronological record of every meaningful change to this production.
Checkpoint rows are appended automatically by `tools/studio.py checkpoint`.

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
<!-- CHECKPOINT_TABLE_END -->
