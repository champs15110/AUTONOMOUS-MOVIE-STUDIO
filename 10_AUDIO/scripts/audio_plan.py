#!/usr/bin/env python3
"""
audio_plan - the authored audio structure for NINETY-TWO TURNS.

Every event below is synchronized to the approved shot frames (24 fps,
1-7248) and traces to a `sound_intention` line in MASTER_SHOT_PLAN.json.
The film is wordless; the dialogue track is intentionally empty
(FINAL_SCREENPLAY: "no dialogue, no narration and no on-screen text").

Tracks: AMBIENCE (looping beds), MUSIC (score cues), SFX (one-shots/loops),
DIALOGUE (empty by design - voice identity is sound design).
"""

FPS = 24
TOTAL_FRAMES = 7248

SCENE_FRAMES = {
    "SC01": (1, 768), "SC02": (769, 1560), "SC03": (1561, 2208),
    "SC04": (2209, 2928), "SC05": (2929, 3792), "SC06": (3793, 4464),
    "SC07": (4465, 5472), "SC08": (5473, 6288), "SC09": (6289, 6768),
    "SC10": (6769, 7248),
}

SHOT_FRAMES = {
    "SC01_SH001": (1, 132), "SC01_SH002": (133, 216), "SC01_SH003": (217, 336),
    "SC01_SH004": (337, 528), "SC01_SH005": (529, 648), "SC01_SH006": (649, 768),
    "SC02_SH001": (769, 924), "SC02_SH002": (925, 1032), "SC02_SH003": (1033, 1176),
    "SC02_SH004": (1177, 1320), "SC02_SH005": (1321, 1440), "SC02_SH006": (1441, 1560),
    "SC03_SH001": (1561, 1704), "SC03_SH002": (1705, 1824), "SC03_SH003": (1825, 1992),
    "SC03_SH004": (1993, 2112), "SC03_SH005": (2113, 2208),
    "SC04_SH001": (2209, 2328), "SC04_SH002": (2329, 2460), "SC04_SH003": (2461, 2568),
    "SC04_SH004": (2569, 2712), "SC04_SH005": (2713, 2832), "SC04_SH006": (2833, 2928),
    "SC05_SH001": (2929, 3048), "SC05_SH002": (3049, 3180), "SC05_SH003": (3181, 3288),
    "SC05_SH004": (3289, 3432), "SC05_SH005": (3433, 3576), "SC05_SH006": (3577, 3696),
    "SC05_SH007": (3697, 3792),
    "SC06_SH001": (3793, 3912), "SC06_SH002": (3913, 4080), "SC06_SH003": (4081, 4200),
    "SC06_SH004": (4201, 4344), "SC06_SH005": (4345, 4464),
    "SC07_SH001": (4465, 4596), "SC07_SH002": (4597, 4728), "SC07_SH003": (4729, 4920),
    "SC07_SH004": (4921, 5064), "SC07_SH005": (5065, 5184), "SC07_SH006": (5185, 5304),
    "SC07_SH007": (5305, 5400), "SC07_SH008": (5401, 5472),
    "SC08_SH001": (5473, 5592), "SC08_SH002": (5593, 5724), "SC08_SH003": (5725, 5832),
    "SC08_SH004": (5833, 5952), "SC08_SH005": (5953, 6072), "SC08_SH006": (6073, 6216),
    "SC08_SH007": (6217, 6288),
    "SC09_SH001": (6289, 6480), "SC09_SH002": (6481, 6624), "SC09_SH003": (6625, 6768),
    "SC10_SH001": (6769, 6876), "SC10_SH002": (6877, 6984), "SC10_SH003": (6985, 7092),
    "SC10_SH004": (7093, 7176), "SC10_SH005": (7177, 7248),
}

SHOT_SCENE = {sid: sid[:4] for sid in SHOT_FRAMES}


def ev(track, asset, f_in, note, gain=1.0, f_out=None, fade_in=0, fade_out=0,
       shot=None, loop=False):
    return dict(track=track, asset=asset, frame_in=f_in, frame_out=f_out,
                gain=gain, fade_in=fade_in, fade_out=fade_out, loop=loop,
                shot=shot, note=note)


# ---------------------------------------------------------------- ambience ---

AMBIENCE = [
    ev("ambience", "AMB_QUAY_DUSK", 1, "SC01_SH001 distant wind under; SH003 wind + distant water, 'nothing else - the silence is the point'",
       0.7, 132, fade_in=48, fade_out=24, shot="SC01_SH001"),
    ev("ambience", "AMB_QUAY_DUSK", 217, "SC01_SH003 wind, distant water",
       0.8, 336, fade_in=24, fade_out=72, shot="SC01_SH003"),
    ev("ambience", "AMB_HARBOUR_WIND", 300, "SC01_SH004 harbour ambience swells in as we widen - water, wind through iron, no birds",
       0.8, 984, fade_in=96, fade_out=24, shot="SC01_SH004"),
    ev("ambience", "AMB_HARBOUR_WIND", 1033, "SC02_SH003 harbour ambience resumes after the SC02_SH002 absolute silence (Stage-12 editorial conform)",
       0.8, 1176, fade_in=24, fade_out=24, shot="SC02_SH003"),
    ev("ambience", "AMB_HARBOUR_WIND", 1177, "SC02_SH004 wind rising",
       1.0, 1560, fade_out=48, shot="SC02_SH004"),
    ev("ambience", "AMB_FOG_SWELL", 1561, "SC03 slow swell beyond the fog",
       0.9, 2208, fade_in=48, fade_out=48, shot="SC03_SH001"),
    ev("ambience", "AMB_FLOODED_STREET", 2209, "SC04_SH001 water; wind funnelling between buildings",
       0.9, 2560, fade_in=24, fade_out=96, shot="SC04_SH001"),
    ev("ambience", "AMB_RAIN_STEADY", 2461, "rain begins exactly at SC04_SH003; 'rain now steady and continuous' by SC04_SH006",
       0.9, 2928, fade_in=372, fade_out=24, shot="SC04_SH003"),
    ev("ambience", "AMB_GALE", 2929, "SC05_SH001 wind up sharply; dies at the hole in the sound (Stage-12 editorial conform: was 3289, played through the SC05_SH003 silence)",
       1.0, 3239, fade_in=24, fade_out=24, shot="SC05_SH001"),
    ev("ambience", "AMB_GALE", 3289, "SC05_SH004 the wind drops for exactly one beat - the only quiet in the storm",
       0.25, 3432, shot="SC05_SH004"),
    ev("ambience", "AMB_GALE", 3432, "SC05_SH005-007 storm resumed",
       1.0, 3792, fade_out=24, shot="SC05_SH005"),
    ev("ambience", "AMB_RAIN_STEADY", 3793, "SC06_SH001 rain on iron; the tower humming in the wind",
       0.9, 4080, fade_in=24, fade_out=24, shot="SC06_SH001"),
    ev("ambience", "AMB_RAIN_STEADY", 4081, "SC06_SH003 'everything drops out except the tiny friction of the needle' - bed drops to a trace",
       0.12, 4200, fade_out=24, shot="SC06_SH003"),
    ev("ambience", "AMB_TOWER_INT", 4201, "SC06_SH004 threshold crossed - storm reduced to murmur, reverb opens",
       0.9, 4464, fade_in=24, fade_out=24, shot="SC06_SH004"),
    ev("ambience", "AMB_GALE", 4465, "SC07_SH001 the gale at full volume, rain horizontal",
       1.0, 5400, fade_in=24, shot="SC07_SH001"),
    ev("ambience", "AMB_GALE", 5401, "SC07_SH008 the gale drops sharply in the lee of the gallery",
       0.22, 5472, fade_out=24, shot="SC07_SH008"),
    ev("ambience", "AMB_TOWER_INT", 5473, "SC08_SH001 the storm reduced to a murmur outside; water dripping",
       0.8, 5759, fade_in=24, fade_out=48, shot="SC08_SH001"),
    ev("ambience", "AMB_TOWER_INT", 5953, "SC08_SH005 bed returns under the complete motif - SH003/SH004 are true silence ('No catch. Nothing.' / 'Absolute silence.')",
       0.5, 6216, fade_in=48, fade_out=24, shot="SC08_SH005"),
    ev("ambience", "AMB_TOWER_INT", 6242, "SC08_SH007 bed returns after the one-beat silence before ignition (Stage-12 editorial conform)",
       0.5, 6288, fade_in=12, fade_out=96, shot="SC08_SH007"),
    ev("ambience", "AMB_DRIZZLE", 6289, "SC09 clearing - rain thinning to drizzle",
       0.8, 6648, fade_in=48, fade_out=72, shot="SC09_SH001"),
    ev("ambience", "AMB_DAWN_CALM", 6577, "SC09_SH003 dawn - first living sound (birds)",
       0.9, 6876, fade_in=96, shot="SC09_SH003"),
    ev("ambience", "AMB_DAWN_CALM", 6877, "SC10 dawn calm under the child's scene - bed low, drips and feet carry it",
       0.45, 7092, fade_in=48, fade_out=48, shot="SC10_SH001"),
    ev("ambience", "AMB_DAWN_CALM", 7093, "SC10_SH004-005 'ONE click... loud in the silence' / 'one final click over black' - bed to a trace",
       0.12, 7248, shot="SC10_SH004"),
]

# ------------------------------------------------------------------- music ---

MUSIC = [
    ev("music", "MUS_CLOCK_A", 529, "SC01_SH005 her clock motif, first statement - three thin notes on a single instrument",
       0.9, shot="SC01_SH005"),
    ev("music", "MUS_CLOCK_UNRESOLVED", 649, "SC01_SH006 the motif does not resolve; it simply stops",
       0.85, shot="SC01_SH006"),
    ev("music", "MUS_SHIP_MOTIF", 1045, "SC02_SH003 the ship's motif - two descending notes, first statement",
       0.8, shot="SC02_SH003"),
    ev("music", "MUS_CLOCK_B", 1321, "SC02_SH005 second statement - noticeably faster",
       0.9, shot="SC02_SH005"),
    ev("music", "MUS_FORWARD", 1441, "SC02_SH006 the score's first forward motion underneath",
       0.7, shot="SC02_SH006"),
    ev("music", "MUS_STRINGS_MAJOR", 1825, "SC03_SH003 the music opens out - the only major-key passage in the film",
       0.9, 2112, fade_out=24, shot="SC03_SH003"),
    ev("music", "MUS_CLOCK_B", 1993, "SC03_SH004 the clock motif continues under the strings",
       0.4, shot="SC03_SH004"),
    ev("music", "MUS_CLOCK_DIST", 2569, "SC04_SH004 her clock motif distorted and slowing",
       0.8, shot="SC04_SH004"),
    ev("music", "MUS_SINGLE_NOTE", 5065, "SC07_SH005 a single bright note - the score returns, one instrument only",
       0.9, shot="SC07_SH005"),
    ev("music", "MUS_CLOCK_SKIP", 5185, "SC07_SH006 the motif stuttering - audibly skipping a note",
       0.9, shot="SC07_SH006"),
    ev("music", "MUS_CLOCK_DIST", 5305, "SC07_SH007 the clock motif has stopped being a melody",
       0.55, shot="SC07_SH007"),
    ev("music", "MUS_CLOCK_COMPLETE", 5953, "SC08_SH005 stated once, complete - the only complete statement in the film",
       1.0, shot="SC08_SH005"),
    ev("music", "MUS_IGNITION_FULL", 6241, "SC08_SH007 the ignition - the score in full, for the first and only time (one beat of silence first)",
       1.0, shot="SC08_SH007"),
    ev("music", "MUS_BEACON_SUSTAIN", 6380, "SC09_SH001-002 score sustained, no melody",
       0.8, 6624, fade_out=48, shot="SC09_SH001"),
    ev("music", "MUS_SHIP_RESOLVE", 6490, "SC09_SH002 the ship's two-note motif, resolved upward for the first time",
       0.9, shot="SC09_SH002"),
    ev("music", "MUS_THINNING", 6625, "SC09_SH003 the score thinning to nothing - gone by the scene turn; SC10 is diegetic only ('water dripping. nothing else.')",
       0.7, 6768, fade_out=72, shot="SC09_SH003"),
]

# --------------------------------------------------------------------- sfx ---
# Foley = WICK's gait ticks / joint clicks / handling; hard SFX = metal,
# water, mechanism. Tick placements encode the gait degradation schedule
# from CHARACTER_BIBLE: four-beat (SC03), irregular (SC04_SH002+),
# skipping (SC07_SH006), broken dragging (SC07_SH007).

SFX = [
    # SC01 - the winding ritual
    ev("sfx", "SFX_RATCHET_CLICK_A", 41, "three dry ratchet clicks, close and intimate (1/3)", 1.0, shot="SC01_SH001"),
    ev("sfx", "SFX_RATCHET_CLICK_B", 73, "(2/3)", 0.95, shot="SC01_SH001"),
    ev("sfx", "SFX_RATCHET_CLICK_C", 105, "(3/3)", 1.0, shot="SC01_SH001"),
    ev("sfx", "SFX_SHEAR_PING", 150, "a bright metallic ping on the shear", 0.9, shot="SC01_SH002"),
    ev("sfx", "SFX_SUB_THUD", 195, "a low sub thud as the needle settles", 0.9, shot="SC01_SH002"),
    # SC02 - the empty turns
    ev("sfx", "SFX_JOINT_ALIGN", 790, "the small click of alignment as she seats herself", 0.8, shot="SC02_SH001"),
    ev("sfx", "SFX_HOLLOW_SPIN", 935, "three hollow spins with no ratchet underneath (1/3)", 0.9, shot="SC02_SH002"),
    ev("sfx", "SFX_HOLLOW_SPIN", 962, "(2/3)", 0.9, shot="SC02_SH002"),
    ev("sfx", "SFX_HOLLOW_SPIN", 989, "(3/3) - then absolute silence", 0.9, shot="SC02_SH002"),
    ev("sfx", "SFX_BELL_BUOY", 1060, "a distant bell buoy, slow and irregular (1/2)", 0.7, shot="SC02_SH003"),
    ev("sfx", "SFX_BELL_BUOY", 1141, "(2/2)", 0.6, shot="SC02_SH003"),
    ev("sfx", "SFX_IRON_GROAN", 1195, "iron groaning under load (1/2)", 0.8, shot="SC02_SH004"),
    ev("sfx", "SFX_IRON_GROAN", 1270, "(2/2)", 0.7, shot="SC02_SH004"),
    ev("sfx", "SFX_POLE_SCRAPE", 1455, "the pole scraping stone", 0.85, shot="SC02_SH006"),
    ev("sfx", "SFX_FOOTSTEP_TICK", 1500, "one footfall", 0.9, shot="SC02_SH006"),
    # SC03 - the gait is established (four-beat, locked)
    *[ev("sfx", "SFX_FOOTSTEP_TICK", f, "four-beat ratchet gait - the film's central sound idea starts here",
         0.9, shot="SC03_SH001") for f in range(1573, 1694, 12)],
    ev("sfx", "SFX_FOOTSTEP_TICK", 1725, "two ticks, loud and dry, nothing under them (1/2)", 1.0, shot="SC03_SH002"),
    ev("sfx", "SFX_FOOTSTEP_TICK", 1765, "(2/2)", 1.0, shot="SC03_SH002"),
    ev("sfx", "SFX_WATER_LAP", 2120, "water lapping at stone (music cut out entirely)", 0.8, shot="SC03_SH005"),
    ev("sfx", "SFX_WATER_LAP", 2172, "lapping continues", 0.65, shot="SC03_SH005"),
    # SC04 - the storm front; the gait goes irregular
    ev("sfx", "SFX_METAL_STRAIN", 2350, "metal straining", 0.8, shot="SC04_SH002"),
    *[ev("sfx", "SFX_FOOTSTEP_TICK", f, "footfall ticks continue but are now irregular (gait degradation begins)",
         0.85, shot="SC04_SH002") for f in (2345, 2361, 2372, 2394, 2405, 2429, 2437)],
    *[ev("sfx", "SFX_RAINDROP_FIRST", f, "the first raindrops - distinct, countable",
         0.9, shot="SC04_SH003") for f in (2461, 2483, 2499, 2521, 2547)],
    ev("sfx", "SFX_MUFFLED_SUB", 2585, "everything muffles - a dull sub", 0.9, shot="SC04_SH004"),
    ev("sfx", "SFX_SPRING_CATCH", 2760, "the first audible catch of her spring - a small bright note under the murk",
       0.7, shot="SC04_SH005"),
    ev("sfx", "SFX_SURFACE_BREAK", 2845, "the surface break, loud", 1.0, shot="SC04_SH006"),
    # SC05 - the climb; the spark
    ev("sfx", "SFX_IRON_GROAN", 2950, "iron creaking under load", 0.9, shot="SC05_SH001"),
    ev("sfx", "SFX_GUST_WALL", 3049, "the gust as a solid wall of sound, not a whoosh", 1.0, shot="SC05_SH002"),
    ev("sfx", "SFX_POLE_CLATTER_SPLASH", 3200, "the pole clattering on iron, one splash, then nothing - a hole opens in the sound",
       0.9, shot="SC05_SH003"),
    ev("sfx", "SFX_GLASS_SEAL", 3450, "the glass sealing", 0.9, shot="SC05_SH005"),
    ev("sfx", "SFX_SPARK_HUM", 3470, "the spark's own warm tone begins - persists until SC08_SH003",
       0.5, 5760, loop=True, fade_in=24, fade_out=48, shot="SC05_SH005"),
    ev("sfx", "SFX_DRAIN_TICK", 3577, "a new, slower tick layered over the footfall ticks - the drain is audible",
       0.6, 3792, loop=True, fade_out=24, shot="SC05_SH006"),
    # SC06 - the door; the quietest moment
    ev("sfx", "SFX_IRON_SHRIEK", 3950, "iron shrieking", 0.8, shot="SC06_SH002"),
    ev("sfx", "SFX_SPRING_STRAIN", 4000, "her spring straining - a sound not used anywhere else", 0.8, shot="SC06_SH002"),
    ev("sfx", "SFX_NEEDLE_FRICTION", 4081, "everything drops out except the tiny friction of the needle - the quietest moment in the film",
       0.5, 4200, loop=True, fade_in=12, fade_out=24, shot="SC06_SH003"),
    *[ev("sfx", "SFX_FOOTSTEP_TICK_ECHO", f, "her footsteps echo - reverb opens hard at the threshold",
         0.9, shot="SC06_SH004") for f in (4230, 4280, 4325)],
    ev("sfx", "SFX_WIND_BREACH", 4345, "wind coming through the breach; the reverb narrows",
       0.6, 4464, loop=True, fade_in=12, fade_out=24, shot="SC06_SH005"),
    # SC07 - the gale; the gait fails
    ev("sfx", "SFX_SURFACE_BREAK", 4650, "the crash, delayed and far below", 0.35, shot="SC07_SH002"),
    *[ev("sfx", "SFX_FOOTSTEP_TICK", f, "grab, strain, grab - gait audibly irregular (degradation continues)",
         0.8, shot="SC07_SH003") for f in (4745, 4757, 4780, 4791, 4819, 4826, 4854, 4862, 4889)],
    ev("sfx", "SFX_SHOULDER_SCREAM", 4960, "one long metallic scream from the shoulder joint - music out entirely",
       0.9, shot="SC07_SH004"),
    *[ev("sfx", "SFX_FOOTSTEP_TICK", f, "the gait now skipping beats",
         0.75, shot="SC07_SH006") for f in (5200, 5212, 5236, 5260, 5272, 5296)],
    ev("sfx", "SFX_MECHANISM_FAIL", 5320, "the mechanism audibly failing - metal fatigue", 0.85, shot="SC07_SH007"),
    *[ev("sfx", "SFX_FOOTSTEP_TICK", f, "broken dragging gait",
         0.6, shot="SC07_SH007") for f in (5350, 5368, 5390)],
    # SC08 - the chamber; the end of her spring; the ignition
    ev("sfx", "SFX_WATER_DROP", 5510, "water dripping (1/2)", 0.7, shot="SC08_SH001"),
    ev("sfx", "SFX_WATER_DROP", 5570, "(2/2)", 0.6, shot="SC08_SH001"),
    ev("sfx", "SFX_WATER_DROP", 5900, "absolute silence. one water drop.", 0.9, shot="SC08_SH004"),
    ev("sfx", "SFX_SPRING_UNSPOOL", 6080, "the spring unspooling - a long, thin, singing sound", 0.9, shot="SC08_SH006"),
    ev("sfx", "SFX_RATCHET_ENGAGE", 6150, "then the ratchet engaging", 1.0, shot="SC08_SH006"),
    ev("sfx", "SFX_MECH_WINDDOWN", 6160, "then her mechanism winding down to nothing", 0.9, shot="SC08_SH006"),
    ev("sfx", "SFX_IGNITION_BLOOM", 6241, "one beat of absolute silence, then the ignition - a huge, warm, low bloom",
       1.0, shot="SC08_SH007"),
    # SC09 - the beacon; the ship resolved; dawn
    ev("sfx", "SFX_BEACON_ROTATE", 6289, "the beacon's slow rotation", 0.6, 6768,
       loop=True, fade_in=24, fade_out=72, shot="SC09_SH001"),
    *[ev("sfx", "SFX_BELL_BUOY", f, "the bell buoy, now in rhythm with the beacon",
         0.7, shot="SC09_SH002") for f in (6500, 6560, 6620)],
    ev("sfx", "SFX_BEACON_WINDDOWN", 6640, "the beacon winding down", 0.7, shot="SC09_SH003"),
    # SC10 - the child closes the loop
    *[ev("sfx", "SFX_WATER_DROP", f, "water dripping. nothing else.",
         0.8, shot="SC10_SH001") for f in (6795, 6830, 6862)],
    *[ev("sfx", a, f, "bare feet on wet iron - near-silent, organic, the opposite of her ticking",
         0.7, shot="SC10_SH002") for a, f in (("SFX_BARE_FOOT_A", 6895), ("SFX_BARE_FOOT_B", 6925),
                                             ("SFX_BARE_FOOT_A", 6955), ("SFX_BARE_FOOT_B", 6975))],
    ev("sfx", "SFX_KEY_LIFT", 7005, "the key lifting out of the back plate - the same small metal sound as the opening",
       0.9, shot="SC10_SH003"),
    ev("sfx", "SFX_FINAL_CLICK", 7130, "ONE click. clean, loud in the silence.", 1.0, shot="SC10_SH004"),
    ev("sfx", "SFX_COIL_CATCH", 7195, "the coil catching", 0.9, shot="SC10_SH005"),
    ev("sfx", "SFX_SHUTTER_OPEN", 7215, "the shutter aperture opening", 0.8, shot="SC10_SH005"),
    ev("sfx", "SFX_FINAL_CLICK", 7240, "one final click over black", 1.0, shot="SC10_SH005"),
]

DIALOGUE = []  # wordless by design - see DIALOGUE_PLAN.md

# Declared intentional silences (the gap checker may not flag these):
# each traces to an approved sound_intention line.
INTENTIONAL_SILENCES = [
    dict(frames=(985, 1032), reason="SC02_SH002: 'On the third, absolute silence.'"),
    dict(frames=(3240, 3289), reason="SC05_SH003: 'then nothing. A hole opens in the sound.'"),
    dict(frames=(5760, 5833), reason="SC08_SH003: 'The hum, then silence. No catch. No click. Nothing.'"),
    dict(frames=(5833, 5952), reason="SC08_SH004: 'Absolute silence. One water drop.'"),
    dict(frames=(6217, 6241), reason="SC08_SH007: 'One beat of absolute silence' before the ignition"),
]

MIX = dict(
    target=dict(integrated_lufs=-16.0, true_peak_dbtp=-1.5,
                sample_rate=48000, channels=2, format="WAV PCM 16-bit"),
    stems=dict(
        DIALOGUE=dict(level="-inf (track exists but is empty - the film is wordless)"),
        MUSIC=dict(level_db=-14.0, note="never competes with the gait ticks; "
                                        "ducks 3 dB under IGNITION_BLOOM"),
        SFX=dict(level_db=-8.0, note="the gait ticks are the lead voice of the "
                                    "film - always intelligible over ambience"),
        AMBIENCE=dict(level_db=-18.0, note="ducks 4 dB for 12 frames under "
                                           "dialogue-grade SFX (clicks, ignition)"),
    ),
    measurement=dict(
        status="PENDING_MEASUREMENT",
        note="Integrated LUFS / true-peak measurement requires ffmpeg "
             "(loudnorm/ebur128), which is not available in this "
             "environment. Structural levels (per-asset peak <= -1 dBFS) are "
             "verified by run_audio_tests.py; full loudness compliance is "
             "measured at render QC (T11).",
    ),
)

ALL_EVENTS = sorted(AMBIENCE + MUSIC + SFX, key=lambda e: e["frame_in"])
