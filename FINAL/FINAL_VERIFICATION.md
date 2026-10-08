# FINAL VERIFICATION — NINETY-TWO TURNS (STEP 16, INDEPENDENT)

Generated 2026-10-08 21:36 UTC by the Independent Final MP4 Verification
Agent (separate from the rendering agent, per AGENT_PROTOCOL §12).
Target: `FINAL/FINAL_FILM.mp4`. No production was restarted, nothing was
regenerated or repaired; prior success claims were NOT trusted — every
number below was re-measured this pass.

Tools: PyAV 18.1.0 (inspection + full decode + frame extraction), pure-python
PNG writer, `tools/lufs.py` (BS.1770) + pyloudnorm cross-check.
ffprobe/ffmpeg CLI not installed in sandbox (PyAV used as the available
equivalent); chunk mp4s (gitignored) were lost in a sandbox reset and were
NOT re-rendered per Step 16 rules.

## Verdict: **FAILED** — `FINAL MP4 NOT VERIFIED`

One critical content defect (SC10, below). Everything else passes.

## 1. File / container / streams — PASS (one documented deviation)

| Check | Result | Measured |
|---|---|---|
| exists / readable / size>0 | PASS | 7,354,432 bytes |
| container | PASS | mp4 (mov,mp4,m4a,3gp,3g2,mj2), 302.016 s |
| video codec | PASS | H.264 High, yuv420p |
| resolution | PASS w/ deviation | 320x180 = declared final spec; MASTER_CONFIG target is 1920x1080 (ERR-0003: no cloud renderer; 1080p ≈ 49 days on this box) |
| aspect ratio | PASS | 16:9 |
| frame rate | PASS | 24.0 fps (MASTER_CONFIG 24) |
| duration | PASS | 302.0 s — inside MASTER_CONFIG 180-420 s, ~5 min preferred |
| audio codec | PASS | AAC 48 kHz stereo, 302.016 s |

## 2. Decode integrity — PASS

- Video: 7248/7248 frames decoded, 0 errors (5.4 s full pass).
- Audio: 14,496,768 samples/ch (302.02 s) decoded; peak 0.835 (non-silent).
- Loudness: −15.97 LUFS (internal BS.1770) / −16.8 LUFS (pyloudnorm
  cross-check; source mix measured −16.34 at Stage 13; spread noted),
  true peak −1.43 dBTP (ceiling −1.0 respected).

## 3. Black / frozen frame scan — one FAIL, one authored hold

- **FAIL — SC10 black:** frames 6768-7247 mean luma 0.58-1.82/255
  (effectively black). Only ≥7177 is authored black (SC10_SH005 hard cut).
  Frames 6768-7176 (SC10_SH001-SH004: "dawn light in the chamber", child
  entrance, macro key turn mirroring SC01_SH001) are authored VISIBLE but
  decode black. Per-scene luma: SC01 3.8-25.0, SC02 42.7-43.0, SC03 40.4-42.9,
  SC04 33.8-34.7, SC05 6.3-6.7, SC06 23.1-46.2, SC07 46.7-72.6,
  SC08 118.1-142.7, SC09 26.1-27.4, **SC10 0.6-1.8**.
- PASS w/ note — opening hold: frames 54-90 pixel-identical; SC01_SH001 is a
  macro of a key that "turns - once, twice, three times" with pauses; motion
  resumes at f91 (714→8501 changed pixels). Authored between-turn pause, not
  a stall.

## 4. Representative frames (extracted from the MP4, inspected visually)

| Frame | Label | Result |
|---|---|---|
| 60 | opening macro | PASS — brass gauge + cross-needle in authored darkness |
| 1100 | early SC02 | PASS — dusk plaza, WICK at pedestal, environment intact |
| 3624 | middle SC05 | PASS (note: dark night by design; silhouette + spark core discernible) |
| 6241 | climax SC08 | PASS — bright ignition bloom, well exposed |
| 6820 | SC10_SH002 | **FAIL — black** |
| 7120 | SC10_SH004 | **FAIL — black** (compare SC01_SH001 macro, which reads clearly) |
| 7240 | ending | PASS — black as authored ("hard cut to black") |

Stills: `FINAL/INDEPENDENT_VERIFY/iv_f*.png`.

## 5. Screenplay / shot list / edit timeline comparison

- 58 shots / 7248 frames / 302.0 s @24 in EDIT_TIMELINE == film (7248 frames,
  302.0 s). PASS.
- Scenes SC01-SC09 visually present with correct environments. PASS.
- SC10 content absent. **FAIL** — the story's resolution beats are not visible.

## 6. Could not be performed

ffprobe/ffmpeg CLI (absent; PyAV equivalent used); chunk-artifact cross-check
(gitignored chunks lost in reset; re-render forbidden); reference-based
perceptual metrics (no higher-quality reference exists).

## 7. Exact blocker and root cause

`light_design.py` SC10 entry: key = sun (energy 4.0, shadows) fully occluded
by the sealed tower shell; world ambient cannot reach the interior; single
SC10_FILL 12 W point light. Compare SC09 (luma 26: outdoor world light + 50 W
fill) and SC08 interior (luma 118-143: 15 W point inside the lamp room +
emissives). The sealed SC10 chamber receives effectively no light.

Why earlier stages missed it: the Stage-11 SC10 preview representative frame
captured warm emissive macro content; the Stage-13 lighting harness passed
without catching sealed-interior exposure; Stage-14 visual verification
sampled SC10 only at the authored-black ending frame.

Fix path for a FUTURE step (NOT executed now): add an effective interior key
for SC10 (≈50 W warm fill or interior area light, or open the chamber to the
dawn sun), re-render ONLY chunks 32-33 (6769-7248), re-mux, re-verify.

## 8. Status

Verdict **FAILED** / `FINAL MP4 NOT VERIFIED` with the single blocker above.
All technical container/codec/duration/audio checks and 9 of 10 scenes pass.
No repair performed (Step 16 mandate). Reports:
`FINAL/FINAL_VERIFICATION.json`, this file, stills in
`FINAL/INDEPENDENT_VERIFY/`.
