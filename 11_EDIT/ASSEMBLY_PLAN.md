# ASSEMBLY PLAN - NINETY-TWO TURNS (Stage 12, FILM EDITOR)

Generated 2026-10-08T16:54:40+00:00 by `11_EDIT/scripts/build_edit.py`.

## Editorial intent

Wordless 3D fable, 302.0s at 24 fps, 7248 frames, 58 shots in
10 scenes. The assembly is a **straight cut in exact screenplay order** - the
EDL (`EDIT_TIMELINE.json`) reuses every approved shot as authored; nothing is
replaced, trimmed or reordered. Rhythm comes from the authored shot lengths:
long contemplative holds for the wound-up automaton's failing gait, hard
motivated cuts on action beats (footfall, ratchet click, surface break,
ignition flood).

## Continuity & screen direction

- Master axis (locked): sea/ship FRAME RIGHT, tower FRAME LEFT, journey RIGHT
  to LEFT, payoff looks back RIGHT after ignition. Checked per shot against
  this plan (see EDITORIAL_QC).
- The 92-turn gauge is the continuity spine: every shot carries gauge_in/out;
  the EDL preserves the unbroken 92 -> 0 countdown and the final 0 -> 1
  resolution at the ending.
- Action clarity: cuts land on cause/effect beats carried in `transition_out`
  ("Cut on the footfall.", "Cut to the grip loss."), never on ambiguity.
- Emotional progression (scene ladder): curiosity, then dread -> dread hardening into resolve -> wonder, underpinned by a counting dread -> alarm -> loss, then tenderness, then a colder determination -> foreboding -> desperation, then a single moment of recognition -> recognition, sacrifice, awe -> relief, then mourning -> mourning resolving into hope.

## Pacing table (measured)

| scene | shots | seconds | avg shot s | cuts/min | beat |
| --- | --- | --- | --- | --- | --- |
| SC01 | 6 | 32.0 | 5.33 | 11.2 | HOOK |
| SC02 | 6 | 33.0 | 5.5 | 10.9 | STAKE |
| SC03 | 5 | 27.0 | 5.4 | 11.1 | DEPARTURE |
| SC04 | 6 | 30.0 | 5.0 | 12.0 | OBSTACLE_1 |
| SC05 | 7 | 36.0 | 5.14 | 11.7 | OBSTACLE_2_AND_LOSS |
| SC06 | 5 | 28.0 | 5.6 | 10.7 | OBSTACLE_3 |
| SC07 | 8 | 42.0 | 5.25 | 11.4 | ESCALATION_PEAK |
| SC08 | 7 | 34.0 | 4.86 | 12.4 | CLIMAX_AND_TWIST |
| SC09 | 3 | 20.0 | 6.67 | 9.0 | PAYOFF |
| SC10 | 5 | 20.0 | 4.0 | 15.0 | RESOLUTION_AND_LOOP |

## Transitions

All 58 shot-outs and 10 scene boundaries are hard, motivated cuts (no
dissolves/fades by design; the two light-flooding moments - SC08 ignition to
white-gold and SC10 hard cut to black - are authored inside the shots, not as
transition effects). Scene-boundary grammar:

| scene out | transition |
| --- | --- |
| SC01 | Hard cut on the shutter eyes opening. |
| SC02 | Cut on her first footfall out of frame left. |
| SC03 | Music cuts out on the water's edge; hard cut to the flooded street. |
| SC04 | Cut on the surface break and the first hard rain. |
| SC05 | Cut on a rack focus from the gauge to the tower door. |
| SC06 | Cut from the broken stair to the exterior breach. |
| SC07 | Cut as she collapses through the gallery doorway. |
| SC08 | Ignition floods the frame to white-gold; cut to the exterior beam. |
| SC09 | Slow push toward her silhouette as the beacon dies; cut to dawn interior. |
| SC10 | Hard cut to black on the final click. |

## Audio sync strategy

The film is wordless; the dialogue track is empty by design. 143 events across
ambience/music/sfx are placed at their authored absolute frames; because the
assembly is straight-cut (record == source frames), every event stays frame-
accurate against picture with zero conform offsets. The 5 declared intentional
silences are preserved (verified empty of event onsets). Fades (fade_in/out in
the timeline) are honoured by the mix at T11; the low-res preview carries
unity-gain audio without fades and is NOT the final mix.

## Low-resolution assembled preview

Built with Blender's VSE (`11_EDIT/scripts/assemble_preview.py`): one image
strip per shot using that scene's approved preview still at the shot's exact
duration, plus all 143 authored audio events on separate channels, 480x270 (quarter-HD) at
24 fps, H.264/AAC -> `11_EDIT/ASSEMBLY_PREVIEW_LOWRES.mp4`. This is an
**animatic for editorial review only - NOT final**: final picture comes from
T12 scene renders, final mix from T11.

## Known issues carried to final render (not fixed by substitution)

- 11 shots flagged by the Stage-11 occlusion audit (ERR-0004):
  SC02_SH006, SC03_SH001, SC03_SH004, SC04_SH001, SC04_SH003, SC08_SH001, SC08_SH003, SC09_SH002, SC09_SH003, SC10_SH001, SC10_SH002. They stay in the cut as scripted; their cameras
  are nudged/re-verified before the T12 final render.
- Preview stills stand in for unrendered finals in the animatic by design.
