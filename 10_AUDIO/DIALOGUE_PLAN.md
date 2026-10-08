# DIALOGUE PLAN — NINETY-TWO TURNS

**The film is wordless by design.** `FINAL_SCREENPLAY.md`: *"The film has no
dialogue, no narration and no on-screen text. Every `dialogue` field reads
`none`."* `SHOT_LIST.json`: *"none — the film is wordless by design."*
`CHARACTER_BIBLE.md` on WICK: *"Mouth: None. Deliberately and permanently.
All 'speech' in the film is sound design."*

There is therefore **no spoken dialogue to write, cast, record or time** —
and none exists in `AUDIO_TIMELINE.json` (the dialogue track is empty).
What follows is the film's actual voice structure: for every character, a
**voice identity**, an **emotional delivery arc**, and **vocal timing** —
carried entirely by designed sound, per the approved `sound_intention`
lines in `MASTER_SHOT_PLAN.json`.

---

## WICK — the brass automaton

**Voice identity.** A four-beat ratchet gait — *"tick-tick-tick-tick"* —
plus joint clicks, spring tone and needle friction. Her body is her voice
box: brass, blued steel and glass, close-miked and dry. Assets:
`SFX_FOOTSTEP_TICK` (the voice itself), `SFX_RATCHET_CLICK_A/B/C` (winding
— her "words" of ritual), `SFX_JOINT_ALIGN`, `SFX_SPRING_UNSPOOL`,
`SFX_SPRING_CATCH`, `SFX_SPRING_STRAIN`, `SFX_MECH_WINDDOWN`.

**Emotional delivery — the gait degradation schedule (this is the
performance):**

| Scene | State | Delivery | Where |
|---|---|---|---|
| SC03_SH001 | Whole | Locked four-beat, even 12-frame spacing — confident, metronomic | f1573–1693 |
| SC04_SH002 | Shaken | Ticks go **irregular** after the underwater drop | f2345–2437 |
| SC05 | Draining | A slower **drain tick** layers over the gait | f3577–3792 |
| SC07_SH003 | Failing | Grab-strain-grab; rhythm audibly degrading | f4745–4889 |
| SC07_SH006 | Skipping | The pattern **skips beats** — the shoulder is gone | f5200–5296 |
| SC07_SH007 | Broken | Dragging: slow, spaced, fatigued | f5350–5390 |
| SC08_SH006 | Dying | Spring unspooling → ratchet engage → mechanism winding down to nothing | f6080–6216 |
| SC08_SH007 | Given | One beat of silence — then she gives the spark away | f6217–6241 |

**Vocal timing.** Every tick is keyed to frame numbers in
`AUDIO_TIMELINE.json` (sfx track); the harness verifies the spacing
schedules (`gait-schedule` check).

**"Dialogue" moments.** Her three winding clicks at f41/73/105 are the
film's opening line; the three hollow spins at f935/962/989 (no ratchet
underneath) are her first sentence of dread; the single clean click at
f7130 ("ONE click. Clean, loud in the silence.") is her last word — spoken
by the child's hand.

## THE CHILD

**Voice identity.** Organic, near-silent, the exact opposite of WICK: bare
feet on wet iron, small handling sounds. No voice, no cries — her presence
is the *absence* of ticking. Assets: `SFX_BARE_FOOT_A/B`, `SFX_KEY_LIFT`,
`SFX_COIL_CATCH`, `SFX_SHUTTER_OPEN`.

**Emotional delivery.** Careful → decisive. Her footsteps (f6895–6975) are
soft and unhurried; the key lift (f7005) matches the opening's metal
exactly — the film's only repeated "word"; then one committed click
(f7130), the coil catching (f7195), the shutter opening (f7215), and the
final click over black (f7240).

**Vocal timing.** SC10_SH002–SH005, f6877–7248.

## THE RETURNING SHIP

**Voice identity.** Distance and interval: a slow, irregular bell buoy and
a two-note descending motif (`MUS_SHIP_MOTIF`) — the horizon's voice.

**Emotional delivery.** Withheld → resolved. The motif states descending
at f1045 (unanswered, SC02_SH003); the bell buoy returns in rhythm with
the beacon at f6500/6560/6620; the motif **resolves upward for the first
time** (`MUS_SHIP_RESOLVE`) at f6490 in SC09_SH002.

**Vocal timing.** SC02_SH003, SC09_SH001–002.

---

## Rules this plan enforces

1. No spoken words, narration, or vocalizations exist or may be added —
   the wordless form is locked at development (T01) and screenplay (T02).
2. Every character sound above traces to an approved `sound_intention`.
3. Timing is frame-accurate at 24 fps and machine-verified by
   `10_AUDIO/scripts/run_audio_tests.py`.
4. Recording sessions required: **none**. All voice assets are synthesized
   in-repo and exist under `10_AUDIO/assets/` (see `AUDIO_INDEX.json`).
