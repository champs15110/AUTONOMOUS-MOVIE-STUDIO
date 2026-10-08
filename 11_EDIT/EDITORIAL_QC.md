# EDITORIAL QC - NINETY-TWO TURNS (Stage 12)

Generated 2026-10-08T16:54:40+00:00 by `11_EDIT/scripts/build_edit.py`. All values measured from
`EDIT_TIMELINE.json` inputs this run; overall: **ALL PASS**.

| Check | Result | Measured detail |
|---|---|---|
| assembly order == SHOT_LIST story order, no substitutions | PASS | 58 shots; plan coverage identical: True |
| source ranges contiguous 1..7248 (no gaps/overlaps) | PASS | first=1 last=7248; contiguous=True |
| runtime inside 180-420 s target | PASS | 302.0 s at 24 fps |
| record timeline contiguous, straight-cut (record==source spans) | PASS | hard-cut assembly; no overlap/dissolve offsets |
| per-shot timing matches screenplay durations | PASS | mismatches: none |
| screen direction honours master axis (camera harness re-run at edit) | PASS | run_camera_tests.py re-run: 58/58 VERIFIED (axis check included); authored reverses/buffers: ['POV across, then to her', 'the ship turns frame L (to harbour)']; axis: Master line of action: the sea and the returning ship sit FRAME RIGHT;... |
| dialogue sync: film is wordless, dialogue track empty | PASS | dialogue events: 0; wordless=True |
| audio events in range; shot tags on-shot or one-shot L-cut | PASS | 143 events; L-cuts (authored pre/post laps): 4; problems: none |
| intentional silences hold: no beds, only authored punctuations | PASS | 5 windows; bed/unauthored intrusions: none |
| every cut is motivated (no empty/foreign transition grammar) | PASS | 58 shot outs + 10 scene transitions, all cut-based; problems: none |
| opening hook: winding-key macro winds the 92-turn contract | PASS | SC01_SH001 extreme macro; SC01 gauge -> 92; countdown 92->0 then 0->1 resolution |
| climax: SC08 carries the ignition beat | PASS | 1 ignition shots in SC08 (['SC08_SH007']) |
| ending: final click + hard cut to black, gauge resolved 0->1 | PASS | SC10_SH005 gauge 0->1, out='Hard cut to black.' |
| pacing curve measured (climax density vs bookends) | PASS | SC08 avg shot 4.86s vs film range 4.00-6.67s; emotional ladder curiosity, then dread -> dread hardening into resolve -> wonder, underpinned by a counting dread -> alarm -> loss, then tenderness, then a colder determination -> foreboding -> desperation, then a single moment of recognition -> recognition, sacrifice, awe -> relief, then mourning -> mourning resolving into hope |
| all 10 scenes cleared preview QC before edit | PASS | statuses: ['PREVIEW_QC_PASS'] |
| occlusion-defective shots noted for pre-final camera fix (edit order kept) | PASS | 11 shots queued (ERR-0004); edit keeps scripted order - fixes land in T12 final render, not by substitution |
| opening hook | PASS | SC01_SH001 extreme macro of the winding key, gauge 92 - the contract of the title in the first 5.5 s |
| story comprehension | PASS | cause/effect cut grammar on every out; gauge spine 92->0->1 unbroken; wordless intent intact |
| pacing | PASS | see pacing table in ASSEMBLY_PLAN; bookends breathe, storm/climb tighten |
| climax | PASS | SC08 ignition floods to white-gold then cuts to the exterior beam |
| ending | PASS | final click, hard cut to black, gauge 0->1 resolution |
| audio sync | PASS | 143 events frame-accurate (straight cut => zero offsets); 5 silences clean; dialogue empty (wordless) |
| transitions | PASS | 58 motivated hard cuts + 10 authored scene boundaries; no foreign grammar |
| continuity | PASS | ranges contiguous 1..7248; gauge chain unbroken; no frame_count mismatch |
| screen direction | PASS | master axis honoured: T07 camera harness (axis check) re-run at edit, 58/58 VERIFIED |
| low-res preview (NOT final) | PASS | `ASSEMBLY_PREVIEW_LOWRES.mp4` present (9.0 MB), VSE animatic of all 58 shots + 143 audio events; labelled non-final |

Editorial issues found: **0** blocking;
camera-occlusion fixes for 11 shots are queued to the final
render (ERR-0004), not handled by shot substitution.
