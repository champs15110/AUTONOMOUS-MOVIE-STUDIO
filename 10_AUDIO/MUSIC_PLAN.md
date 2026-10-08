# MUSIC PLAN — NINETY-TWO TURNS

Score for a wordless fable. The music is spare on purpose: it states two
motifs, refuses to develop them for nine scenes, and pays everything out in
exactly one moment. **Every cue below exists as a real audio asset** under
`10_AUDIO/assets/music/` and is keyed to approved frames in
`AUDIO_TIMELINE.json`.

> **Honest status.** The cues are *original procedural scratch
> recordings* synthesized in-repo (pure Python, `audio_synth.py`) — real
> audio files, verified by the harness, but **not** a final orchestral
> performance. The structure, timings, keys and orchestration intent below
> are production-ready; a live re-recording is a post-production decision.
> Nothing here claims to be more than it is.

---

## The two motifs

**Her clock motif** — three thin notes, A5–C6–E6, single music-box-ish
instrument. It never develops; it degrades. Its statements are the film's
spine:

| Statement | Cue | Frame | Note |
|---|---|---|---|
| First, slow | `MUS_CLOCK_A` | 529 (SC01_SH005) | three thin notes on a single instrument |
| Unresolved | `MUS_CLOCK_UNRESOLVED` | 649 (SC01_SH006) | two notes, then it simply stops — hard cut, no tail |
| Second, faster | `MUS_CLOCK_B` | 1321 (SC02_SH005) | noticeably faster than the first |
| Under strings | `MUS_CLOCK_B` (low) | 1993 (SC03_SH004) | continues under the only major-key passage |
| Distorted, slowing | `MUS_CLOCK_DIST` | 2569 (SC04_SH004) | detuned, low-passed, losing pitch |
| Stuttering | `MUS_CLOCK_SKIP` | 5185 (SC07_SH006) | skips the middle note; a choked ghost of it remains |
| No longer a melody | `MUS_CLOCK_DIST` (low) | 5305 (SC07_SH007) | the mechanism failing, stated musically |
| **Complete — the only one** | `MUS_CLOCK_COMPLETE` | 5953 (SC08_SH005) | whole motif, single instrument, octave below added |

**The ship's motif** — two notes on a soft horn voice. Descending
(`MUS_SHIP_MOTIF`, f1045) while the ship is only a promise; resolved
**upward** for the first and only time (`MUS_SHIP_RESOLVE`, f6490) when the
beacon answers it.

## Score structure by scene

- **SC01–SC02** — motif statements only, wind between them. "No music" is
  written into SC01_SH001–004 by the screenplay's own SOUND lines.
- **SC02_SH006** — `MUS_FORWARD` (f1441): the score's first forward motion,
  a quiet A3/E4 ostinato that carries into the gait's establishment.
- **SC03_SH003–004** — `MUS_STRINGS_MAJOR` (f1825–2112): F-major pad, **the
  only major-key passage in the film**. Music cuts out entirely at f2113.
- **SC04** — the distorted motif only; the storm owns the rest.
- **SC05, SC06 — no score, by design.** The gale is the score; SC06
  contains the quietest moment in the film (needle friction alone) and
  scoring it would destroy it.
- **SC07** — `MUS_SINGLE_NOTE` (f5065, one bright E6: "the score returns,
  one instrument only"), then the skipping and broken motif statements.
- **SC08_SH007** — `MUS_IGNITION_FULL` (f6241, one beat of silence first):
  **the score in full for the first and only time** — D-major arrival over
  a 55 Hz bloom, with `SFX_IGNITION_BLOOM` under it.
- **SC09** — `MUS_BEACON_SUSTAIN` (f6380, no melody) and `MUS_THINNING`
  (f6625, gone by the scene turn at f6768).
- **SC10 — no score, by design.** "Water dripping. Nothing else." The film
  ends diegetic: feet, the key, ONE click, the coil, the shutter, and one
  final click over black.

## Orchestration intent (for final recording)

- Clock motif: celesta or muted piano, close-miked, felt-damped. One
  instrument only — never doubled until SC08_SH007.
- Ship motif: solo horn, soft attack, distant reverb.
- Strings: 8 players, no vibrato in SC03 (innocence), full vibrato allowed
  only in the ignition cue.
- Ignition: low strings + two horns + sub; the only cue with more than
  five players.

## Mix notes

Score sits at −14 dB stem level, always under the gait ticks (they are the
lead voice), ducks 3 dB under the ignition bloom. Full targets and the
pending loudness measurement live in `mix/MIX_PLAN.json`
(−16 LUFS integrated, ≤ −1.5 dBTP, 48 kHz stereo — measurement requires
ffmpeg and happens at T11 render QC).

Cue-by-cue event sheet: `music/MUSIC_CUE_SHEET.json`.
