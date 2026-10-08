# QC REPORT - NINETY-TWO TURNS (Stage 13, FINAL QC & RECOVERY)

Generated 2026-10-08T17:21:00+00:00. Second verification pass after Stage-13 fixes.
OVERALL: **PASS**

| Domain | Pass | Evidence |
|---|---|---|
| story | True | SHOT_LIST contiguous 1-7248, runtime 302.0s in 180-420, 10 scenes |
| characters | True | principals present in CHARACTER_BIBLE; binds in SCENE_MANIFEST (build harness) |
| continuity | True | gauge chain 92->0->1 unbroken across shots/scenes; ranges contiguous |
| animation | True | stub harness 58/58; ANIMATION_STATUS 58x VERIFIED |
| camera | True | harness 58/58 after QC-13 nudges; occlusion audit 0 defects (was 11) |
| lighting | True | lighting/vfx harness green (re-run this pass) |
| vfx | True | VFX_PLAN parses; harness 0 purposeless effects |
| audio | True | harness 10/10; 65 assets present, peaks match; mix MEASURED -16.34 LUFS / -1.5 dBTP |
| editing | True | build_edit ALL CHECKS PASS; animatic 302.0 s verified |
| technical | True | all required artefacts parse; 10 previews present; ERROR_LOG all resolved/mitigated |

## Issues (3)
- [MINOR] audio: integrated -16.34 LUFS vs -16.0 target: true-peak ceiling -1.5 dBTP binds first; within ±0.5 LU tolerance; final mix uses a true-peak limiter to reach exact -16.0 -> DOCUMENTED
- [MINOR] technical: ERR-0003: no cloud/JANCTION renderer in this runtime; finals render on pypi bpy Cycles CPU (documented, MITIGATED) -> DOCUMENTED
- [MINOR] audio: 130 assets tiled in the numpy measurement mix; final mix loops beds properly at T12 -> DOCUMENTED

No CRITICAL or MAJOR open issues. MINOR items are documented carry-overs
(peak-ceiling loudness, measurement tiling, ERR-0003 environment).
