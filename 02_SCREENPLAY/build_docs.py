#!/usr/bin/env python3
"""
Emit 02_SCREENPLAY/FINAL_SCREENPLAY.md and 02_SCREENPLAY/CONTINUITY_BIBLE.md
from 02_SCREENPLAY/SHOT_LIST.json.

Both documents are generated from the single verified source of truth, so the screenplay,
the shot list, the CSV and the continuity ledger cannot disagree.

Run:  python3 02_SCREENPLAY/build_docs.py
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

J = json.load(open(os.path.join(HERE, "SHOT_LIST.json"), encoding="utf-8"))
B = json.load(open(os.path.join(ROOT, "01_DEVELOPMENT", "MASTER_FILM_BRIEF.json"),
                   encoding="utf-8"))
SC, SH = J["scenes"], J["shots"]
BY = {s["shot_id"]: s for s in SH}


def scene_shots(sid: str) -> list[dict]:
    return [s for s in SH if s["scene_id"] == sid]


# =========================================================================== #
# FINAL_SCREENPLAY.md
# =========================================================================== #
def screenplay() -> str:
    o: list[str] = []
    a = o.append
    a(f"# {B['title']}")
    a("")
    a("**FINAL SCREENPLAY — production-ready, locked for downstream stages**")
    a("")
    a(f"**Project:** AMS-2026-001 · **Task:** T02_SCREENPLAY · **Stage:** 02_SCREENPLAY  ")
    a(f"**Runtime:** {J['total_runtime_formatted']} ({J['total_runtime_seconds']}s) · "
      f"**Frames:** 1–{J['total_frames']} @ {J['fps']} fps · **Format:** 1920×1080, 16:9  ")
    a(f"**Scenes:** {J['scene_count']} · **Shots:** {J['shot_count']} · "
      f"**Average shot:** {J['average_shot_seconds']}s  ")
    a(f"**Dialogue:** none — the film is wordless by design")
    a("")
    a("Machine-readable twins: `SHOT_LIST.json`, `SHOT_LIST.csv`. "
      "Continuity authority: `CONTINUITY_BIBLE.md`. "
      "Concept authority: `01_DEVELOPMENT/MASTER_FILM_BRIEF.md`.")
    a("")
    a("---")
    a("")
    a("## LOGLINE")
    a("")
    a(f"> {B['logline']}")
    a("")
    a("## HOW TO READ THIS")
    a("")
    a("The film has **no dialogue, no narration and no on-screen text**. Every `dialogue` "
      "field reads `none`. The story is carried by action, the diegetic gauge in WICK's "
      "chest, sound design and light.")
    a("")
    a("Each scene block gives the production metadata first, then its shots in order. "
      "Shot timecodes are absolute film time; frame ranges are 1-based and contiguous "
      "across the whole film.")
    a("")
    a("---")
    a("")
    a("## SCENE INDEX")
    a("")
    a("| # | Scene | Slug | Timecode | Dur | Location | Shots | Gauge |")
    a("|---|---|---|---|---:|---|---:|---|")
    for i, s in enumerate(SC, 1):
        g = "—" if s["gauge_in"] is None else str(s["gauge_in"])
        a(f'| {i} | {s["scene_id"]} | {s["slug"]} | {s["time_in"]}–{s["time_out"]} | '
          f'{s["duration"]:.0f}s | {s["location"]} | {s["shot_count"]} | {g} → {s["gauge_out"]} |')
    a("")
    a("---")
    a("")

    for s in SC:
        rows = scene_shots(s["scene_id"])
        a(f'## {s["scene_id"]} — {s["slug"]}')
        a("")
        a(f'**{s["time_in"]} – {s["time_out"]}** · **{s["duration"]:.0f} seconds** · '
          f'frames {s["frame_in"]}–{s["frame_out"]} · **{s["shot_count"]} shots** · '
          f'beat: `{s["beat_type"]}`')
        a("")
        a("| | |")
        a("|---|---|")
        a(f'| **scene_id** | `{s["scene_id"]}` |')
        a(f'| **timecode** | {s["time_in"]} – {s["time_out"]} |')
        a(f'| **duration** | {s["duration"]:.0f} s ({s["frame_out"] - s["frame_in"] + 1} frames) |')
        a(f'| **location** | {s["location"]} |')
        a(f'| **characters** | {", ".join(s["characters"])} |')
        a(f'| **story_purpose** | {s["story_purpose"]} |')
        a(f'| **emotion** | {s["emotion"]} |')
        a(f'| **props** | {", ".join(s["props"])} |')
        a(f'| **environment_action** | {s["environment_action"]} |')
        a(f'| **gauge** | {s["gauge_in"] if s["gauge_in"] is not None else "winding"} → {s["gauge_out"]} |')
        a(f'| **transition** | {s["transition"]} |')
        a(f'| **dialogue** | none |')
        a("")
        a("**ACTION**")
        a("")
        a(f'{s["story_purpose"]} The scene runs: '
          + " ".join(f'({r["shot_id"].split("_")[1]}) {r["action"]}' for r in rows))
        a("")
        a("### SHOTS")
        a("")
        for r in rows:
            a(f'#### {r["shot_id"]} · {r["time_in"]}–{r["time_out"]} · {r["duration"]:.1f}s · '
              f'frames {r["frame_in"]}–{r["frame_out"]}')
            a("")
            a(f'*{r["shot_type"]} · {r["lens"]} · '
              f'gauge {r["gauge_in"] if r["gauge_in"] is not None else "—"} → '
              f'{r["gauge_out"] if r["gauge_out"] is not None else "—"}*')
            a("")
            a(f'**ACTION.** {r["action"]}')
            a("")
            a(f'**CHARACTER STATE.** {r["character_state"]}')
            a("")
            a(f'**CHARACTER POSITION.** {r["character_position"]}')
            a("")
            a(f'**PROP STATE.** {r["prop_state"]}')
            a("")
            a(f'**CAMERA.** {r["camera_intention"]}')
            a("")
            a(f'**SOUND.** {r["sound"]}')
            a("")
            a(f'**DIALOGUE.** {r["dialogue"]}')
            a("")
            a(f'**CONTINUITY.** {r["continuity_notes"]}')
            a("")
            a(f'**TRANSITION OUT.** {r["transition_out"]}')
            a("")
        a("---")
        a("")

    a("## END OF SCREENPLAY")
    a("")
    a(f'Total {J["total_runtime_formatted"]} · {J["shot_count"]} shots · '
      f'{J["total_frames"]} frames. The film ends on gauge 1 and a single click over black.')
    a("")
    return "\n".join(o)


# =========================================================================== #
# CONTINUITY_BIBLE.md
# =========================================================================== #
def gauge_ledger() -> list[str]:
    out = ["| Shot | TC out | Gauge in | Gauge out | Δ | What it costs |",
           "|---|---|---:|---:|---:|---|"]
    for s in SH:
        gi, go = s["gauge_in"], s["gauge_out"]
        if gi is None and go is None:
            continue
        if gi is None:
            out.append(f'| `{s["shot_id"]}` | {s["time_out"]} | winding | **{go}** | — | '
                       f'The needle settles. This is the film\'s opening number. |')
            continue
        d = gi - go
        if d == 0:
            delta, note = "0", "no cost"
        elif d > 0:
            delta, note = f"-{d}", "—"
        else:
            delta, note = f"+{-d}", f"**gains {-d}** — the single turn"
        out.append(f'| `{s["shot_id"]}` | {s["time_out"]} | {gi} | {go} | {delta} | {note} |')
    return out


def bible() -> str:
    o: list[str] = []
    a = o.append
    a(f"# CONTINUITY BIBLE — {B['title']}")
    a("")
    a("**Project:** AMS-2026-001 · **Task:** T02_SCREENPLAY · "
      "**Authority:** this document governs continuity for every downstream stage.")
    a("")
    a("If a downstream stage needs to change something recorded here, the change must be "
      "logged in `CHANGELOG.md` and this file updated. Continuity errors in a wordless film "
      "are unfixable in the mix — there is no dialogue to cover them.")
    a("")
    a("---")
    a("")
    a("## 1. THE COUNTDOWN LEDGER")
    a("")
    a("The gauge is the spine of the film and the audience is doing arithmetic with it. "
      "**Every change is listed. There are no others.**")
    a("")
    o.extend(gauge_ledger())
    a("")
    a("**Invariants, all machine-verified:**")
    a("")
    a("- Starts at **92**, settles at `SC01_SH002` (00:09), inside the 8-second hook deadline.")
    a("- Falls monotonically from 92 to 0, with no step upward anywhere in between.")
    a("- Effort spend totals **91**, so she reaches the burner with **1**.")
    a("- Reaches **0** for the first time at `SC08_SH006`, the ignition.")
    a("- Rises **exactly once**, at `SC10_SH005` — the child's single turn.")
    a("- Ends at **1**. Not restored. Restarted.")
    a("")
    a("---")
    a("")
    a("## 2. PROP STATE LEDGER")
    a("")
    a("### THE WINDING KEY")
    a("")
    a("| From | To | State |")
    a("|---|---|---|")
    a("| `SC01_SH001` | `SC02_SH002` | Seated in WICK's back. Slips on the fourth turn. |")
    a("| `SC02_SH002` | `SC10_SH002` | Useless — the socket is stripped. Never used again. |")
    a("| `SC10_SH003` | `SC10_SH005` | Removed by the child. Turns once. It catches. |")
    a("")
    a("### THE LAMP-POLE")
    a("")
    a("| From | To | State |")
    a("|---|---|---|")
    a("| `SC01_SH004` | `SC02_SH005` | Lying on the stone beside her. |")
    a("| `SC02_SH006` | `SC05_SH002` | Carried, on her shoulder, then braced horizontally. |")
    a("| `SC05_SH003` | — | **LOST.** Taken by a gust into the water. |")
    a("| `SC05_SH004` | `SC07_SH004` | **ABSENT. Must not appear in any frame.** |")
    a("| `SC07_SH005` | `SC10_SH005` | **RECOVERED** — wedged in the tower ironwork, blown there by the storm. Becomes a climbing brace, and is still in her hand at the end. |")
    a("")
    a("> The pole's absence across 21 shots is the single easiest continuity error in this "
      "film. `verify_shot_list.py` asserts it does not reappear.")
    a("")
    a("### THE SPARK")
    a("")
    a("| From | To | State |")
    a("|---|---|---|")
    a("| `SC03_SH004` | — | Implied: the one still-burning harbour lamp is its source. |")
    a("| `SC05_SH005` | `SC08_SH001` | **INTRODUCED.** Inside her chest drum, behind glass. Her glow is the only light in the tower interior from `SC06_SH004`. |")
    a("| `SC08_SH002` | `SC08_SH003` | **REMOVED** into her hand. Her chest goes dark for the first time since SC05. |")
    a("| `SC08_SH004` | `SC08_SH006` | Finds nothing to light. |")
    a("| `SC08_SH007` | — | **CONSUMED** by the ignition. |")
    a("")
    a("### THE MAINSPRING AND THE SOCKET")
    a("")
    a("| From | To | State |")
    a("|---|---|---|")
    a("| `SC01_SH002` | `SC08_SH005` | Inside her chest, one tooth sheared. |")
    a("| `SC08_SH004` | — | **THE SOCKET revealed.** No wick, no oil, no flint. Its diameter must visibly match her coil — match it in design at T03. |")
    a("| `SC08_SH006` | end | **Spring unspooled from her body and installed in the burner.** It cannot be put back, which is why the ending is a new turn and not a restoration. |")
    a("")
    a("### PERMANENT WORLD DAMAGE (never reversible)")
    a("")
    a("| Event | Shot | Consequence |")
    a("|---|---|---|")
    a("| Spring tooth shears | `SC01_SH002` | She can never hold a full charge again. |")
    a("| Pillar socket stripped | `SC02_SH002` | No recharge is possible anywhere in the film. |")
    a("| Tower door forced | `SC06_SH002` | Stands open from here on. |")
    a("| Stair torn away | `SC07_SH002` | No intact stair may appear in any later shot. |")
    a("| Shoulder joint damaged | `SC04_SH006` | Sparks again at `SC07_SH004`. Same joint. Cumulative, not incidental. |")
    a("")
    a("---")
    a("")
    a("## 3. CAUSE AND EFFECT ACROSS SCENES")
    a("")
    a("Nothing in this film happens without a cause established earlier. The chain:")
    a("")
    a("| # | Cause | Shot | Effect | Shot |")
    a("|---|---|---|---|---|")
    a("| 1 | The ratchet slips and a tooth shears | `SC01_SH001–002` | She has 92 turns and no way to make more | `SC02` |")
    a("| 2 | The pillar socket is stripped | `SC02_SH002` | She must carry her own energy to the tower | `SC03` |")
    a("| 3 | Movement spends turns | `SC03_SH001–002` | The audience learns to read the gauge as a receipt | all |")
    a("| 4 | The street is flooded at her scale | `SC04` | She is damaged, and the shoulder joint starts to fail | `SC04_SH006` |")
    a("| 5 | The storm takes the pole | `SC05_SH003` | She must shelter the spark in her own body | `SC05_SH005` |")
    a("| 6 | The spark draws power as she walks | `SC05_SH006` | Protecting it costs her — the midpoint reversal | `SC06` |")
    a("| 7 | The door costs 18 turns | `SC06_SH002` | The needle enters the red arc | `SC06_SH003` |")
    a("| 8 | The stair is torn away | `SC07_SH002` | The only way up is outside, in the gale | `SC07_SH003` |")
    a("| 9 | The storm blows the pole against the tower | `SC05_SH003` | She finds it as a brace and survives the grip loss | `SC07_SH005` |")
    a("| 10 | The damaged shoulder fails | `SC04_SH006` | She hangs by one arm over the drop | `SC07_SH004` |")
    a("| 11 | The spring weakens | `SC07_SH006–007` | Her gait breaks down; the motif starts skipping | `SC07_SH007` |")
    a("| 12 | The burner has only a socket | `SC08_SH004` | Her own spring is the only thing that fits | `SC08_SH006` |")
    a("| 13 | The beacon lights | `SC08_SH007` | The ship turns away from the reef | `SC09_SH002` |")
    a("| 14 | She is spent, not destroyed | `SC08_SH006` | One turn from the child is enough to begin again | `SC10_SH004–005` |")
    a("")
    a("**No disconnected beats.** Every scene is entered from a consequence of the previous "
      "one, and every scene exits on a state change that the next scene must honour.")
    a("")
    a("---")
    a("")
    a("## 4. ENVIRONMENT AND WEATHER PROGRESSION")
    a("")
    a("| Scenes | Weather | Light | Water |")
    a("|---|---|---|---|")
    a("| SC01–SC03 | Still. No wind yet. | Dusk, one warm practical | Calm, black, reflective |")
    a("| SC04 | First drops at `SC04_SH003`, steady by `SC04_SH006` | Dusk deepening | Disturbed, then violent |")
    a("| SC05–SC06 | Full storm. Wind **camera-right** throughout | Storm slate, near-monochrome | Horizontal rain |")
    a("| SC07 | Full gale; drops sharply inside the lee at `SC07_SH008` | Storm-white rim, near-monochrome | Sea white below |")
    a("| SC08 | Reduced to a murmur outside | Her glow only, then ignition bloom | Dripping inside |")
    a("| SC09 | Clearing | Beacon amber, then dawn grey-gold | Beam sweeping; rain turning to light |")
    a("| SC10 | Calm | Dawn rose-gold | Dripping. Still. |")
    a("")
    a("**Hard rules.** Wind direction is camera-right for all of SC05–SC07. Rain starts at "
      "`SC04_SH003` and never stops until `SC09`. The only organic sound in the film is the "
      "birdsong beginning at `SC09_SH003`.")
    a("")
    a("---")
    a("")
    a("## 5. SOUND AND MUSIC CONTINUITY")
    a("")
    a("| Element | Introduced | Development | Resolution |")
    a("|---|---|---|---|")
    a("| **The clock motif** (three notes) | `SC01_SH005`, thin, single instrument | Faster at `SC02_SH005`; stuttering and skipping from `SC07_SH006`; stops being a melody at `SC07_SH007` | Stated **once, complete**, at `SC08_SH005` |")
    a("| **Footfall ticks** | `SC03_SH001`, locked to her gait | Become irregular at `SC04_SH002` and never fully recover | Stop when she stops moving |")
    a("| **The spark hum** | `SC05_SH005`, when the glass seals | Layered under the footfalls at `SC05_SH006`; exposed and fragile at `SC08_SH002` | Ends in silence at `SC08_SH003` |")
    a("| **The ship motif** (two descending notes) | `SC02_SH003` | — | Resolved **upward** for the first time at `SC09_SH002` |")
    a("| **Full score** | withheld for the entire film | — | `SC08_SH007` only — the single full-orchestration moment |")
    a("| **The click** | `SC01_SH001`, three of them, the fourth slipping | — | `SC10_SH004`, one of them, clean. Same sound. |")
    a("")
    a("**The muffled underwater sound world** is used only at `SC04_SH004` and `SC04_SH005`. "
      "**Absolute silence** occurs three times: `SC02_SH002` (third spin), `SC08_SH004` (the "
      "reveal) and the beat before the ignition at `SC08_SH007`.")
    a("")
    a("---")
    a("")
    a("## 6. CAMERA AND LENS GRAMMAR")
    a("")
    a("| Rule | Detail |")
    a("|---|---|")
    a("| **Gauge insert framing is locked** | Same lens (100mm macro), same angle, same key for every insert: `SC01_SH002–003`, `SC03_SH002`, `SC05_SH007`, `SC06_SH003`, `SC10_SH005`. |")
    a("| **Never cut away from a decrement** | The gauge is on screen whenever it changes. Non-negotiable. |")
    a("| **Camera stays low** | At her eye height for the first two thirds. It rises above her only after the ignition. |")
    a("| **One fast move in the film** | The whip to the gauge at `SC06_SH002`. Everything else is deliberate. |")
    a("| **The loop** | `SC10_SH004` uses identical framing, lens and camera height to `SC01_SH001`, warmed from dusk to dawn. |")
    a("| **The protected hold** | `SC09_SH001`, 8 seconds, locked wide. No coverage may be cut into it. |")
    a("| **Lens vocabulary** | 100mm macro for mechanism · 85mm for her face · 35–50mm for action · 18–24mm for the world · 135–300mm for the ship and the drop. |")
    a("")
    a("---")
    a("")
    a("## 7. CHARACTER STATE ARC")
    a("")
    a("| Scene | WICK's state |")
    a("|---|---|")
    a("| SC01 | Wound, damaged, unaware of the scale of the problem |")
    a("| SC02 | Habitual → confused → alarmed → decided |")
    a("| SC03 | Purposeful. The gauge begins to teach her what she already suspects. |")
    a("| SC04 | Working hard, then failing, then angry |")
    a("| SC05 | Grieving the pole, then protective of the spark, then colder |")
    a("| SC06 | Daunted, at maximum effort, then apprehensive |")
    a("| SC07 | Exposed → in danger → astonished → spent → failing |")
    a("| SC08 | Awed → hopeful → afraid → understanding → at peace → gone dark |")
    a("| SC09 | Absent. Her work is on the water without her. |")
    a("| SC10 | Inert, then restarting. |")
    a("")
    a("**Her only expressions are shutter aperture, head tilt, limb posture and gait rhythm.** "
      "There is no face to animate and no line to read. The gait rhythm is the performance: "
      "it establishes at `SC03_SH001`, breaks at `SC04_SH002`, and fails completely at "
      "`SC07_SH007`.")
    a("")
    a("---")
    a("")
    a("## 8. THINGS THAT MUST NEVER CHANGE")
    a("")
    a("1. **92.** The number, and the arithmetic that spends it.")
    a("2. **One turn at the end.** Not a restoration. A beginning.")
    a("3. **The socket.** The climax is mechanical, not magical. No wick, no oil, no flint.")
    a("4. **Zero dialogue.** Any spoken line requires an explicit logged deviation.")
    a("5. **The pole's absence** between `SC05_SH003` and `SC07_SH005`.")
    a("6. **The loop.** `SC10_SH004` mirrors `SC01_SH001`.")
    a("7. **The single full-score moment** at `SC08_SH007`. Nowhere else.")
    a("8. **The child's face is never resolved.** Backlit, rim-lit, silhouette only.")
    a("")
    a("---")
    a("")
    a("## 9. VERIFICATION")
    a("")
    a("Run `python3 02_SCREENPLAY/verify_shot_list.py`. It checks, against the emitted "
      "artefacts only:")
    a("")
    a("shot-id uniqueness and format · timecode and frame contiguity at shot **and** scene "
      "level · runtime against the delivery window · all `MASTER_CONFIG` bounds · every "
      "required field populated · the full gauge ledger including the single rise · the "
      "pole's absence across the gap · cause-and-effect markers · JSON↔CSV parity.")
    a("")
    a("It does not import the generator, so it verifies what was shipped rather than what "
      "was intended.")
    a("")
    return "\n".join(o)


def main() -> int:
    sp = os.path.join(HERE, "FINAL_SCREENPLAY.md")
    bp = os.path.join(HERE, "CONTINUITY_BIBLE.md")
    open(sp, "w", encoding="utf-8").write(screenplay())
    open(bp, "w", encoding="utf-8").write(bible())
    print(f"wrote {os.path.relpath(sp, ROOT)}  ({os.path.getsize(sp)} bytes)")
    print(f"wrote {os.path.relpath(bp, ROOT)}  ({os.path.getsize(bp)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
