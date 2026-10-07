# AGENT PROTOCOL — AUTONOMOUS MOVIE STUDIO

**Project:** AMS-2026-001 · **Role of this document:** binding rules for every agent
that touches this repository.

Read this before doing anything. Then read `PROJECT_STATE.json` and `TASK_QUEUE.json`.

---

## 0. Prime directives

1. **The repository is the source of truth.** Conversation memory is never authoritative.
   If it is not written to a file in this repo, it did not happen.
2. **Never lose completed work.** Preserve every successful output before attempting any
   recovery.
3. **Never restart completed work unnecessarily.** Check status before redoing anything.
4. **The project is not complete because a plan exists.** It is complete only when
   `FINAL/FINAL_FILM.mp4` exists and has passed technical verification.
5. **Never blindly repeat a failed command.** Change the approach, then retry.

---

## 1. Roles

| Role | Responsibility |
|---|---|
| **Master Controller** | State, stages, tasks, checkpoints, recovery, validation, file organisation, handoffs. Owns `PROJECT_STATE.json`, `TASK_QUEUE.json`, `ERROR_LOG.json`. |
| **Story Agent** | Premise, screenplay, story spine → `01_DEVELOPMENT`, `02_SCREENPLAY` |
| **Design Agent** | Characters, world, asset inventory → `03_CHARACTERS`, `04_WORLD`, `06_ASSETS/ASSET_INVENTORY.json` |
| **Board Agent** | Beats, shot list, shot + render registries → `05_STORYBOARD` |
| **3D Agent** | Models, rigs, materials, engine decision → `06_ASSETS` |
| **Animation Agent** | Per-shot animation → `07_ANIMATION` |
| **Camera Agent** | Per-shot camera → `08_CAMERA` |
| **Lighting/VFX Agent** | Lighting, VFX, grades → `09_LIGHTING_VFX` |
| **Audio Agent** | Music, SFX, voice, mix → `10_AUDIO` |
| **Edit Agent** | Timeline, EDL, conform → `11_EDIT` |
| **QC Agent** | Technical + continuity QC → `12_QC` |
| **Render Agent** | Scene renders + final assembly → `13_RENDER`, `FINAL` |

Agents never edit state files by hand. They request changes through the controller CLI
(section 3), or the Master Controller applies them.

---

## 2. Checkpoint rule (mandatory)

After **every** meaningful successful operation:

1. **Verify the output** — the file exists, is non-empty, and is what was asked for.
   For media, actually probe it. Do not assume.
2. **Update `PROJECT_STATE.json`**
3. **Update `TASK_QUEUE.json`**
4. **Update `CHANGELOG.md`**
5. **Save/commit the checkpoint**

```bash
python3 tools/studio.py checkpoint --task-id T04_STORYBOARD \
  --summary "Shot list locked: 34 shots across 8 scenes" --commit
```

The CLI writes atomically (temp file + `os.replace`) and keeps a `.bak` of the previous
version of each file it touches, so a crashed write cannot corrupt state.

**Recovery after a crash:** re-read the state files, run
`python3 tools/studio.py validate`, then `python3 tools/studio.py next`. Resume from the
first task that is not `VERIFIED`/`COMPLETE`.

---

## 3. Controller CLI

```
python3 tools/studio.py validate                     # integrity check, exit 1 on failure
python3 tools/studio.py status                       # human-readable state dump
python3 tools/studio.py next                         # next actionable task + acceptance criteria
python3 tools/studio.py task-set T02_SCREENPLAY --status IN_PROGRESS
python3 tools/studio.py task-set T02_SCREENPLAY --status VERIFIED --checkpoint-id CP-0007
python3 tools/studio.py shot-add SC01 --count 4      # registers SC01_SH001..SH004
python3 tools/studio.py shot-set SC01_SH002 --stage animation --status VERIFIED \
        --artefact 07_ANIMATION/blocking/SC01_SH002_anim.json
python3 tools/studio.py shot-show                    # shot x stage matrix
python3 tools/studio.py scene-add SC01 --title "Cold open"
python3 tools/studio.py scene-set SC01 --lifecycle PREVIEW --status VERIFIED \
        --artefact 13_RENDER/previews/SC01_preview.mp4
python3 tools/studio.py log-error --task-id T05_3D_ASSETS --classification TOOL_ABSENT \
        --command "blender --version" --error-text "command not found" \
        --cause "Blender not installed in runtime" --preserved "all 03/04/05 outputs" \
        --recovery "switch to python_software_raster fallback" --mark-failed
python3 tools/studio.py checkpoint --task-id T05_3D_ASSETS --summary "..." --commit
python3 tools/studio.py probe 13_RENDER/previews/SC01_preview.mp4
python3 tools/studio.py verify-final                 # the only completion gate
```

`validate` enforces: required fields present, statuses inside the enum, dependencies exist
and are acyclic, counters agree with the registries, `failed_tasks`/`blocked_tasks` agree
with actual task statuses, and the completion gate (no `COMPLETE` without a real verified
MP4). **Run it before and after any large change.**

---

## 4. Status vocabulary

`NOT_STARTED · IN_PROGRESS · PARTIAL · READY · VERIFIED · FAILED · BLOCKED · COMPLETE`

| Status | Meaning |
|---|---|
| `NOT_STARTED` | Nothing done |
| `IN_PROGRESS` | Underway, no deliverable yet |
| `PARTIAL` | Some deliverables exist, not all |
| `READY` | Deliverables exist, awaiting verification |
| `VERIFIED` | Deliverables exist **and** were checked |
| `FAILED` | Attempt failed; error recorded |
| `BLOCKED` | Cannot proceed; cause recorded; needs a different approach |
| `COMPLETE` | Reserved for the finished project / final artefact |

Only `VERIFIED` and `COMPLETE` count as done for dependency purposes.

---

## 5. Failure recovery procedure

On **any** failure:

1. **Capture the exact error** — full stderr/exception, plus the exact command.
2. **Write it to `ERROR_LOG.json`** via `log-error`. Nothing else first.
3. **Classify it:** `MISSING_DEPENDENCY · BAD_INPUT · RESOURCE_EXHAUSTED · TIMEOUT ·
   PERMISSION · LOGIC_ERROR · DATA_CORRUPTION · NETWORK · TOOL_ABSENT · UNKNOWN`
4. **Identify the probable cause** and record it.
5. **Record what was preserved** — the artefacts that survive and must not be touched.
6. **Attempt a different recovery.** Different tool, different parameters, different
   approach, or a documented fallback. Re-running the identical failed command is not
   recovery.
7. **Retry only when appropriate.** Max 3 retries per task (`MASTER_CONFIG.retry_policy`);
   each retry increments `retry_count`.
8. **Preserve successful outputs** — never delete a verified artefact to "start clean".
9. **Mark `BLOCKED`** when genuinely impossible, with the cause in `last_error`, and
   escalate in `CHANGELOG.md`. Move on to work that is not dependent on it.

---

## 6. Shot checkpointing

Every shot has a unique id: `SCnn_SHmmm` — e.g. `SC01_SH001`, `SC01_SH002`, `SC01_SH003`.

`SHOT_REGISTRY.json` tracks **eight** stage slots per shot:

`story · assets · animation · camera · lighting · audio · render · QC`

* A shot is `VERIFIED` only when **all eight** slots are `VERIFIED`.
* Verified shots appear in `PROJECT_STATE.completed_shots`; failed ones in `failed_shots`.
* Frame ranges inside a scene must be contiguous and non-overlapping.
* Work and checkpoint **per shot**, never per stage in bulk. A shot that fails is retried
  alone; its siblings are never redone.

---

## 7. Render checkpointing

**Never render a 3–7 minute film as one job.** The unit of render is the **scene**.

Each scene in `13_RENDER/RENDER_MANIFEST.json` moves through a strictly ordered lifecycle
(the CLI refuses to skip a step):

```
SCENE  →  PREVIEW  →  QC  →  FINAL_RENDER  →  VERIFY
```

| Step | Meaning | Gate to next |
|---|---|---|
| `SCENE` | Scene assembled, frame range known | artefact recorded |
| `PREVIEW` | Fast low-res render produced | preview file on disk |
| `QC` | Preview inspected, issues resolved | QC pass recorded |
| `FINAL_RENDER` | Full-quality scene render | render file on disk |
| `VERIFY` | Duration/frame count/resolution checked | probed values match spec |

Rules:

* A scene may enter `FINAL_RENDER` only after `PREVIEW` passed `QC`.
* **If a scene fails, re-render that scene alone.** Verified scene outputs are never
  regenerated.
* The master assembly is built **only** from scenes whose `VERIFY` is `VERIFIED`.
* Verified scenes are listed in `PROJECT_STATE.verified_scenes`.

---

## 8. Handoff format

When an agent finishes a unit of work it must leave:

1. The output file(s) declared in `TASK_QUEUE.json → output_files`.
2. Status moved via the controller CLI.
3. A `HANDOFF_<TASK_ID>.md` in the stage folder containing: what was produced, what was
   verified (with the command and its actual output), what remains, and any warnings the
   next agent must respect.
4. A checkpoint.

An agent must **not** claim `VERIFIED` for anything it did not actually open and check.

---

## 9. Originality

* Original characters, original story, original dialogue, original designs.
* No copyrighted characters, stories, dialogue, scenes or distinctive designs. No near-
  copies, no "in the style of <named franchise>" as a build instruction.
* Every asset carries provenance in its index (`generated` / `authored` / `license + source`).
* `01_DEVELOPMENT/MASTER_FILM_BRIEF.md` §10 (mirrored in `MASTER_FILM_BRIEF.json → originality`)
  carries the signed-off originality attestation. It is a required T01 deliverable.

---

## 10. Environment constraints

* **No local GPU.** All rendering must be CPU-only.
* **No Kaggle.** No dependency on external notebook platforms.
* **No paid APIs.**
* Detected at init (`2026-10-07`): `git`, `python3 3.11.2`, `node v22.22.3`, `gh`, `jq`
  present. **`ffmpeg` absent. `blender` absent.** Tracked as risks `R-001` / `R-002` in
  `MASTER_CONFIG.json` and warnings `WARN-0001` / `WARN-0002` in `ERROR_LOG.json`.
  Resolve or build a fallback before `T12_FINAL_RENDER`.

---

## 11. Definition of done

```
FINAL/FINAL_FILM.mp4  exists
                    + valid playable MP4
                    + 180–420 s (target 300 s)
                    + 1920x1080, 16:9, 24 fps
                    + H.264 / yuv420p, AAC audio, +faststart
                    + audio present throughout, loudness in spec
                    + 12_QC/reports/FINAL_VERIFICATION.json records PASS
```

Produced by `python3 tools/studio.py verify-final`. Until that command returns `PASS`,
the project is **not** complete — regardless of how much work exists.
