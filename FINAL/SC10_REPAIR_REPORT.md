# SC10 REPAIR REPORT — STEP 17

Generated 2026-10-08 21:55 UTC. Scope: SC10 visible shots only
(SC10_SH001-SH004, frames 6769-7176). No other scene regenerated; original
`FINAL/FINAL_FILM.mp4` untouched; authored cut-to-black (7177-7248) unchanged.

## 1. Source recovery

- Scene/animation/camera/lighting scripts all present in repo; bpy **4.3.0**
  (the exact original render version) reinstalled after a sandbox reset.
- Original chunk mp4s were gitignored and lost in the reset (Git history holds
  only chunk_*.json) — unrecoverable; unaffected frames 1-6768 sourced
  verbatim by decoding the existing verified FINAL_FILM.mp4.
- FINAL_MIX.wav rebuilt deterministically; re-measured identical
  (−16.34 LUFS / −1.50 dBTP).

## 2. Root cause (confirmed) and exact lighting change

Sealed chamber, no effective light: sun occluded by tower shell, world
ambient blocked, one 12 W fill → luma 0.58-1.82/255.
`light_design.py` SC10 entry now adds (fills, no shadows — one-caster rule kept):

- `SC10_DAWN_KEY` POINT 55 W (1.0, 0.72, 0.55) at (1.7, 0.0, 13.1) — warm dawn
  key inside the chamber doorway.
- `SC10_CHAMBER_LIFT` POINT 22 W (1.0, 0.85, 0.72) at (−1.2, −1.0, 13.6).

Sun tune, original fill, world, exposure bounds, cameras, animation, timing:
unchanged.

## 3. Renders (actually performed)

Preview 160×90/4spp per shot inspected first (dawn warmth, no clipping).
Final spec 320×180 / 6spp + OIDN, bpy 4.3.0 Cycles CPU, per authored shot
camera: SH001 108 fr, SH002 108 fr, SH003 108 fr, SH004 84 fr →
`13_RENDER/REPAIR_CHUNKS/SC10_SH00X.mp4` (frame counts verified by decode).

## 4. Candidate and its verification

`FINAL/FINAL_FILM_REPAIRED_CANDIDATE.mp4` — 7,052,141 bytes. NOT promoted.

- 7248/7248 frames decode, 0 errors; 320×180 @24; 302.0 s; audio AAC 48k
  302.016 s, peak 0.835, −15.97 LUFS, −1.43 dBTP.
- SC10 luma now 11.8-28.1 across SH001-SH004 (was ~1); SH005 exactly 0.0
  (ending preserved); SC02/SC09 ranges match the old final within one
  re-encode generation.
- Visual: WICK shell + gauge readable (6770), child entrance recognizable
  (6930), key macro readable (7040), chest-drum macro warm (7150), black
  ending (7200). Stills in FINAL/INDEPENDENT_VERIFY/r_*.png.

## 5. Remaining blockers

1. Promotion requires Step 18 independent re-verification.
2. ERR-0009: scenes SC01-SC09 play as single representative cameras — the
   58-shot cut structure of EDIT_TIMELINE is absent outside SC10 (candidate
   renders SC10 per-shot). Fixing needs whole-film per-shot re-render: out of
   scope here.
3. 320×180 vs MASTER_CONFIG 1920×1080 (ERR-0003) — not claimed met.

Verdict: repair successful at candidate level; final verdict deferred.
