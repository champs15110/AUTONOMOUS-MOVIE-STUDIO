# CAMERA QC - NINETY-TWO TURNS

Generated 2026-10-08T01:24:30Z by 08_CAMERA/scripts/run_camera_tests.py (structural stub).
Status counts: {'VERIFIED': 58}. VERIFIED = all ten checks passed for the shot.

## Method

Every shot is built (scene + its animation, subjects at final pose) and its
camera executed from 08_CAMERA/scripts/shot_cams.py via cam_lib primitives.
Checks: camera present; lens == CAMERA_PLAN intention; all camera keys inside
the shot's exact frames; projected subject-scale fraction inside the authored
framing window; subject within 90% of half the vertical FOV of frame centre;
frame-right dot
+X (sea frame right) unless the plan marks reverse/axis-buffer; executed move
licensed by the plan's motivation sentence; DOF focus matches subject distance
(rack pulls end on target); camera path >= 0.12 m from non-subject geometry;
static framing of moving subjects wide enough unless an exit/entry is staged.

Honesty: this verifies camera LOGIC and geometry structurally. Framing taste
and final composition get a visual pass on the cloud Blender layer before
render, same as animation.

## Per-shot results

| shot | lens | move | scale frac | dist m | status |
|---|---|---|---|---|---|
| SC01_SH001 | 100mm | hold | 2.4691 | 0.1 | VERIFIED |
| SC01_SH002 | 100mm | push_in | 4.4444 | 0.1 | VERIFIED |
| SC01_SH003 | 100mm | hold | 4.4444 | 0.1 | VERIFIED |
| SC01_SH004 | 24mm | crane_back_up | 0.025 | 18.974 | VERIFIED |
| SC01_SH005 | 50mm | micro_drift | 0.6348 | 0.35 | VERIFIED |
| SC01_SH006 | 35mm | hold | 0.7969 | 8.676 | VERIFIED |
| SC02_SH001 | 35mm | hold | 0.4318 | 1.601 | VERIFIED |
| SC02_SH002 | 100mm | hold | 2.4691 | 0.1 | VERIFIED |
| SC02_SH003 | 200mm | hold | 0.3705 | 66.642 | VERIFIED |
| SC02_SH004 | 18mm | hold | 0.7182 | 11.138 | VERIFIED |
| SC02_SH005 | 85mm | hold | 0.8395 | 0.45 | VERIFIED |
| SC02_SH006 | 40mm | hold | 0.439 | 1.8 | VERIFIED |
| SC03_SH001 | 40mm | dolly | 0.5267 | 1.5 | VERIFIED |
| SC03_SH002 | 100mm | hold | 4.0404 | 0.11 | VERIFIED |
| SC03_SH003 | 24mm | push_in | 0.0377 | 12.578 | VERIFIED |
| SC03_SH004 | 40mm | dolly | 0.5644 | 1.4 | VERIFIED |
| SC03_SH005 | 35mm | hold | 0.4857 | 3.559 | VERIFIED |
| SC04_SH001 | 24mm | hold | 0.0846 | 5.601 | VERIFIED |
| SC04_SH002 | 50mm | micro_drift | 0.5486 | 1.8 | VERIFIED |
| SC04_SH003 | 50mm | hold | 0.4489 | 2.2 | VERIFIED |
| SC04_SH004 | 35mm | descend | 0.5286 | 1.308 | VERIFIED |
| SC04_SH005 | 35mm | hold | 0.8704 | 0.794 | VERIFIED |
| SC04_SH006 | 50mm | hold | 0.6945 | 1.422 | VERIFIED |
| SC05_SH001 | 28mm | hold | 0.0787 | 7.024 | VERIFIED |
| SC05_SH002 | 35mm | hold | 0.4321 | 1.6 | VERIFIED |
| SC05_SH003 | 50mm | pan_hold | 0.1693 | 5.832 | VERIFIED |
| SC05_SH004 | 85mm | hold | 0.9444 | 0.4 | VERIFIED |
| SC05_SH005 | 100mm | hold | 4.4444 | 0.1 | VERIFIED |
| SC05_SH006 | 40mm | dolly | 0.5267 | 1.5 | VERIFIED |
| SC05_SH007 | 100mm | rack | 3.7037 | 0.12 | VERIFIED |
| SC06_SH001 | 24mm | hold | 0.8873 | 4.541 | VERIFIED |
| SC06_SH002 | 50mm | whip | 0.3223 | 0.689 | VERIFIED |
| SC06_SH003 | 100mm | hold | 4.4444 | 0.1 | VERIFIED |
| SC06_SH004 | 18mm | tilt_to | 0.6724 | 4.627 | VERIFIED |
| SC06_SH005 | 35mm | cut_to | 1.6724 | 2.067 | VERIFIED |
| SC07_SH001 | 24mm | hold | 0.7342 | 14.528 | VERIFIED |
| SC07_SH002 | 50mm | tilt_to | 0.4623 | 8.011 | VERIFIED |
| SC07_SH003 | 35mm | crane_rise | 0.2765 | 2.5 | VERIFIED |
| SC07_SH004 | 135mm | hold | 0.9243 | 7.212 | VERIFIED |
| SC07_SH005 | 85mm | hold | 0.5996 | 0.35 | VERIFIED |
| SC07_SH006 | 50mm | hold | 0.7899 | 1.25 | VERIFIED |
| SC07_SH007 | 85mm | hold | 1.7172 | 0.22 | VERIFIED |
| SC07_SH008 | 35mm | hold | 0.4058 | 1.704 | VERIFIED |
| SC08_SH001 | 18mm | hold | 0.812 | 2.627 | VERIFIED |
| SC08_SH002 | 85mm | push_in | 1.1993 | 0.35 | VERIFIED |
| SC08_SH003 | 100mm | hold | 2.4691 | 0.3 | VERIFIED |
| SC08_SH004 | 100mm | hold | 3.2922 | 0.09 | VERIFIED |
| SC08_SH005 | 100mm | hold | 1.1111 | 0.4 | VERIFIED |
| SC08_SH006 | 100mm | hold | 2.4691 | 0.1 | VERIFIED |
| SC08_SH007 | 50mm | hold | 0.587 | 2.524 | VERIFIED |
| SC09_SH001 | 35mm | hold | 0.1244 | 34.747 | VERIFIED |
| SC09_SH002 | 300mm | hold | 0.5703 | 64.945 | VERIFIED |
| SC09_SH003 | 35mm | push_in | 0.4247 | 1.628 | VERIFIED |
| SC10_SH001 | 50mm | hold | 0.657 | 1.503 | VERIFIED |
| SC10_SH002 | 35mm | hold | 0.6151 | 3.091 | VERIFIED |
| SC10_SH003 | 85mm | hold | 0.8395 | 0.4 | VERIFIED |
| SC10_SH004 | 100mm | hold | 2.4691 | 0.1 | VERIFIED |
| SC10_SH005 | 100mm | hold | 4.0404 | 0.11 | VERIFIED |