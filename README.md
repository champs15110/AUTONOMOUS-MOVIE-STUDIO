# AUTONOMOUS MOVIE STUDIO

An autonomous production system that takes one original 3D animated film from premise to
verified `FINAL/FINAL_FILM.mp4`.

**Project:** AMS-2026-001 · **Target:** 3–7 min (≈5 min) · 16:9 · 1920x1080 · 24 fps ·
cinematic 3D animation · original characters and story.

---

## Read these first

| File | Purpose |
|---|---|
| `AGENT_PROTOCOL.md` | Binding rules: checkpointing, failure recovery, shot and render checkpointing, handoffs, definition of done |
| `PROJECT_STATE.json` | Where the project is right now |
| `TASK_QUEUE.json` | The 13-stage task graph with dependencies and acceptance criteria |
| `MASTER_CONFIG.json` | Target spec, delivery spec, pipeline, risks, policies |
| `ERROR_LOG.json` | Every failure, classified, with recovery attempted |
| `CHANGELOG.md` | Everything that has changed, plus the checkpoint log |
| `SHOT_REGISTRY.json` | Per-shot status across story/assets/animation/camera/lighting/audio/render/QC |
| `13_RENDER/RENDER_MANIFEST.json` | Per-scene render lifecycle `SCENE → PREVIEW → QC → FINAL_RENDER → VERIFY` |

The repository is the source of truth. Conversation memory is never authoritative.

---

## Repository layout

```
01_DEVELOPMENT/     concept, story spine, tone, originality attestation
02_SCREENPLAY/      drafts and the locked screenplay + scene breakdown
03_CHARACTERS/      bios, designs, model sheets
04_WORLD/           locations, props, palettes
05_STORYBOARD/      beat board, panels, animatic, shot list
06_ASSETS/          models, textures, rigs, materials, asset inventory
07_ANIMATION/       layout, blocking, polish, sim
08_CAMERA/          rigs, lenses, moves
09_LIGHTING_VFX/    lighting, vfx, compositing
10_AUDIO/           music, sfx, voice, mix
11_EDIT/            timeline, conform, subtitles
12_QC/              reports, technical checks, continuity
13_RENDER/          scenes, previews, frames, final
FINAL/              FINAL_FILM.mp4 and delivery notes
tools/              master controller CLI + self-tests
```

---

## Controller CLI

```bash
python3 tools/studio.py validate     # integrity check (exit 1 on failure)
python3 tools/studio.py status       # where the project stands
python3 tools/studio.py next         # next actionable task + acceptance criteria
python3 tools/test_studio.py -v      # run the controller self-test suite
```

Full command reference is in `AGENT_PROTOCOL.md` §3.

---

## Status

**Initialized. No creative work started.** Next task: `T01_DEVELOPMENT`.

Completion is gated on `FINAL/FINAL_FILM.mp4` existing and passing
`python3 tools/studio.py verify-final`. Until that returns `PASS`, the project is not done.

---

## Constraints

No local GPU. No Kaggle. No paid APIs. All assets original — no copyrighted characters,
stories, dialogue, scenes or distinctive designs.
