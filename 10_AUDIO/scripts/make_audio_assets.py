#!/usr/bin/env python3
"""
make_audio_assets - synthesize every audio asset for NINETY-TWO TURNS.

All assets are procedurally synthesized in-repo (pure Python stdlib, no
samples, no external libraries, nothing licensed). Deterministic seeds:
the same run produces byte-identical WAVs.

Output: 10_AUDIO/assets/{ambience,sfx,music}/*.wav + ASSETS_MANIFEST.json

Run:  python3 10_AUDIO/scripts/make_audio_assets.py
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import audio_synth as A  # noqa: E402

OUT = os.path.abspath(os.path.join(HERE, "..", "assets"))
SR = A.SR

# note frequencies (equal temperament, A4 = 440)
N = dict(A4=440.0, A5=880.0, C6=1046.50, E6=1318.51, D4=293.66, A3=220.0,
         E4=329.63, F3=174.61, C4=261.63, F4=349.23, D2=73.42, D3=146.83,
         Fs3=185.0, A2=110.0, D5=587.33)

ASSETS = []  # (id, category, loop, purpose, builder)


def asset(id, category, loop, purpose):
    def deco(fn):
        ASSETS.append((id, category, loop, purpose, fn))
        return fn
    return deco


# ------------------------------------------------------------- ambience ----

@asset("AMB_QUAY_DUSK", "ambience", True,
       "SC01 still dusk quay: gentle water lapping, faint wind, no birds")
def _():
    water = A.amp_env(A.lowpass(A.noise(6.0, 21), 700), 0, 0)
    rnd = __import__("random").Random(5)
    # slow lap swells
    n = len(water)
    for i in range(n):
        water[i] *= 0.5 + 0.5 * math.sin(2 * math.pi * 0.11 * i / SR + 1.3)
    w = A.wind_bed(6.0, 22, 60, 320, 0.07, 0.5, 0.22)
    return A.crossfade_loop(A.mix(A.gain(water, 0.5), w))


@asset("AMB_HARBOUR_WIND", "ambience", True,
       "SC01_SH004-SC02 harbour: wind through iron over water")
def _():
    w = A.wind_bed(6.0, 31, 90, 520, 0.10, 0.7, 0.55)
    iron = A.gain(A.bandpass(A.noise(6.0, 32), 300, 900), 0.05)
    water = A.gain(A.lowpass(A.noise(6.0, 33), 600), 0.25)
    return A.crossfade_loop(A.mix(w, iron, water))


@asset("AMB_FOG_SWELL", "ambience", True,
       "SC03 open quay toward the flooded street: slow distant swell")
def _():
    n = A.sr_scale(6.0)
    x = A.lowpass(A.noise(6.0, 41), 500)
    out = [0.0] * n
    for i in range(n):
        out[i] = x[i] * (0.45 + 0.55 * math.sin(2 * math.pi * 0.07 * i / SR)) ** 2
    far = A.gain(A.lowpass(A.noise(6.0, 42), 300), 0.2)
    return A.crossfade_loop(A.mix(out, far))


@asset("AMB_FLOODED_STREET", "ambience", True,
       "SC04 pre-rain: wind funnelling between buildings over water")
def _():
    w = A.wind_bed(6.0, 51, 400, 900, 0.14, 0.75, 0.4)
    water = A.gain(A.lowpass(A.noise(6.0, 52), 800), 0.3)
    return A.crossfade_loop(A.mix(w, water))


@asset("AMB_RAIN_STEADY", "ambience", True,
       "SC04_SH006 onward: steady continuous rain")
def _():
    base = A.gain(A.bandpass(A.noise(6.0, 61), 400, 7000), 0.5)
    hiss = A.gain(A.highpass(A.noise(6.0, 62), 3500), 0.25)
    # sparse drop transients
    out = A.mix(base, hiss)
    rnd = __import__("random").Random(63)
    for _ in range(14):
        t = rnd.uniform(0, 5.8)
        p = A.gain(A.plink(rnd.uniform(900, 2600), 0.09, 0.25), 1.0)
        i0 = A.sr_scale(t)
        for i, v in enumerate(p):
            if i0 + i < len(out):
                out[i0 + i] += v
    return A.crossfade_loop(out)


@asset("AMB_DRIZZLE", "ambience", True,
       "SC09: rain thinning to drizzle")
def _():
    base = A.gain(A.bandpass(A.noise(6.0, 71), 600, 6000), 0.18)
    out = list(base)
    rnd = __import__("random").Random(72)
    for _ in range(7):
        t = rnd.uniform(0, 5.8)
        p = A.gain(A.plink(rnd.uniform(1200, 3000), 0.07, 0.18), 1.0)
        i0 = A.sr_scale(t)
        for i, v in enumerate(p):
            if i0 + i < len(out):
                out[i0 + i] += v
    return A.crossfade_loop(out)


@asset("AMB_GALE", "ambience", True,
       "SC05/SC07: the gale as a solid wall - wind plus horizontal rain")
def _():
    w = A.wind_bed(6.0, 81, 100, 700, 0.22, 0.55, 0.8)
    wall = A.gain(A.lowpass(A.noise(6.0, 82), 450), 0.55)
    rain = A.gain(A.bandpass(A.noise(6.0, 83), 900, 8000), 0.4)
    st = A.widen(A.mix(w, wall, rain), 0.011, 0.5)
    l = A.crossfade_loop(st[0])
    r = A.crossfade_loop(st[1])
    return (l, r)


@asset("AMB_TOWER_INT", "ambience", True,
       "SC06_SH004+/SC08 interior: storm reduced to murmur, tower hum, drips")
def _():
    murmur = A.gain(A.lowpass(A.noise(6.0, 91), 220), 0.6)
    hum = A.gain(A.sine(95, 6.0, 0.12), 1.0)
    out = A.mix(murmur, hum)
    for t in (1.1, 3.4, 5.2):
        d = A.gain(A.plink(760, 0.3, 0.5), 1.0)
        i0 = A.sr_scale(t)
        for i, v in enumerate(d):
            out[i0 + i] += v
    return A.crossfade_loop(A.reverb(out, 0.18, 0.4))


@asset("AMB_DAWN_CALM", "ambience", True,
       "SC09_SH003/SC10 dawn: still water, faint breeze, first birds")
def _():
    water = A.gain(A.lowpass(A.noise(6.0, 101), 500), 0.3)
    breeze = A.wind_bed(6.0, 102, 70, 300, 0.06, 0.5, 0.12)
    out = A.mix(water, breeze)
    for t, f0, f1 in ((0.8, 2600, 3900), (1.05, 3000, 2400), (2.9, 2400, 3600),
                      (3.1, 3600, 2800), (4.7, 2800, 4000)):
        c = A.chirp(f0, f1, 0.08, 0.16)
        i0 = A.sr_scale(t)
        for i, v in enumerate(c):
            if i0 + i < len(out):
                out[i0 + i] += v
    return A.crossfade_loop(out)


# ------------------------------------------------------------------ sfx ----

@asset("SFX_RATCHET_CLICK_A", "sfx", False,
       "WICK's dry ratchet click - close and intimate (variant A)")
def _():
    return A.click(0.012, 111, (2200, 4200), 330)


@asset("SFX_RATCHET_CLICK_B", "sfx", False, "Ratchet click variant B")
def _():
    return A.click(0.011, 112, (2000, 3900), 300)


@asset("SFX_RATCHET_CLICK_C", "sfx", False, "Ratchet click variant C")
def _():
    return A.click(0.013, 113, (2400, 4600), 350)


@asset("SFX_FOOTSTEP_TICK", "sfx", False,
       "Four-beat gait tick (established SC03_SH001; degrades per schedule)")
def _():
    body = A.gain(A.sine(240, 0.05), 0.6)
    body = [v * e for v, e in zip(body, A.decay_env(0.05, 0.02))]
    return A.mix(A.click(0.014, 121, (1800, 3600), 240), body)


@asset("SFX_FOOTSTEP_TICK_ECHO", "sfx", False,
       "Footstep tick inside the tower - reverb opens at the threshold (SC06_SH004)")
def _():
    return A.reverb(A.click(0.014, 121, (1800, 3600), 240), 0.55, 0.9)


@asset("SFX_JOINT_ALIGN", "sfx", False,
       "SC02_SH001: the small click of alignment as she seats herself")
def _():
    servo = A.gain(A.sine(185, 0.07), 0.3)
    servo = [v * e for v, e in zip(servo, A.decay_env(0.07, 0.03))]
    return A.mix(A.click(0.010, 131, (2600, 4800), 280), servo)


@asset("SFX_HOLLOW_SPIN", "sfx", False,
       "SC02_SH002: key spinning with no ratchet underneath - hollow")
def _():
    x = A.gain(A.bandpass(A.noise(0.9, 141), 380, 900), 1.0)
    n = len(x)
    out = [0.0] * n
    for i in range(n):
        out[i] = x[i] * (0.35 + 0.65 * abs(math.sin(2 * math.pi * 7.0 * i / SR)))
    return A.amp_env(out, 0.02, 0.25)


@asset("SFX_SHEAR_PING", "sfx", False,
       "SC01_SH002: bright metallic ping on the shear")
def _():
    return A.gain(A.bell(2100, 1.4, 1.0), 0.7)


@asset("SFX_SUB_THUD", "sfx", False,
       "SC01_SH002: low sub thud as the needle settles")
def _():
    return A.amp_env(A.glide(60, 35, 0.9, 0.9), 0.005, 0.4)


@asset("SFX_BELL_BUOY", "sfx", False,
       "SC02_SH003/SC09_SH002: distant bell buoy, slow and irregular")
def _():
    b = A.gain(A.bell(320, 4.0, 1.0), 0.55)
    return A.reverb(A.lowpass(b, 2600), 0.3, 0.8)


@asset("SFX_IRON_GROAN", "sfx", False,
       "SC02_SH004: iron groaning under load as the wind rises")
def _():
    x = A.gain(A.bandpass(A.noise(3.0, 151), 70, 160), 1.0)
    n = len(x)
    out = [0.0] * n
    for i in range(n):
        out[i] = x[i] * (0.4 + 0.6 * math.sin(2 * math.pi * 0.7 * i / SR))
    return A.amp_env(out, 0.6, 0.8)


@asset("SFX_POLE_SCRAPE", "sfx", False, "SC02_SH006: the lamp-pole scraping stone")
def _():
    x = A.highpass(A.noise(0.6, 161), 1200)
    n = len(x)
    for i in range(n):
        x[i] *= 0.4 + 0.6 * abs(math.sin(2 * math.pi * 19 * i / SR))
    return A.amp_env(x, 0.05, 0.15)


@asset("SFX_METAL_STRAIN", "sfx", False, "SC04_SH002: metal straining")
def _():
    x = A.bandpass(A.noise(2.5, 171), 150, 500)
    n = len(x)
    out = [0.0] * n
    for i in range(n):
        out[i] = x[i] * (0.3 + 0.7 * math.sin(2 * math.pi * 1.4 * i / SR + 0.7))
    return A.amp_env(out, 0.4, 0.5)


@asset("SFX_RAINDROP_FIRST", "sfx", False,
       "SC04_SH003: the first raindrops - distinct, countable")
def _():
    return A.plink(1450, 0.16, 0.9)


@asset("SFX_MUFFLED_SUB", "sfx", False, "SC04_SH004: a dull sub as everything muffles")
def _():
    return A.lowpass(A.amp_env(A.glide(70, 45, 1.0, 0.9), 0.01, 0.5), 120)


@asset("SFX_SURFACE_BREAK", "sfx", False,
       "SC04_SH006: the surface break, loud; reused distant in SC07_SH002")
def _():
    burst = A.gain(A.lowpass(A.noise(1.8, 181), 3000), 0.9)
    n = len(burst)
    out = [0.0] * n
    for i in range(n):
        t = i / SR
        out[i] = burst[i] * math.exp(-t / 0.45)
    drops = [0.0] * n
    rnd = __import__("random").Random(182)
    for _ in range(20):
        t = rnd.uniform(0.15, 1.6)
        p = A.gain(A.plink(rnd.uniform(700, 2200), 0.1, 0.3), 1.0)
        i0 = A.sr_scale(t)
        for i, v in enumerate(p):
            if i0 + i < n:
                drops[i0 + i] += v
    st = A.widen(A.mix(out, drops), 0.009, 0.6)
    return (A.amp_env(st[0], 0.005, 0.2), A.amp_env(st[1], 0.005, 0.2))


@asset("SFX_GUST_WALL", "sfx", False,
       "SC05_SH002: the gust as a solid wall of sound, not a whoosh")
def _():
    x = A.gain(A.lowpass(A.noise(4.0, 191), 600), 1.0)
    st = A.widen(A.amp_env(x, 0.5, 1.2), 0.013, 0.6)
    return st


@asset("SFX_POLE_CLATTER_SPLASH", "sfx", False,
       "SC05_SH003: the pole clattering on iron, one splash, then nothing")
def _():
    out = A.click(0.02, 201, (1600, 3400), 210)
    for k, t in enumerate((0.18, 0.33, 0.52)):
        c = A.gain(A.click(0.016, 202 + k, (1400 + 300 * k, 3200), 190), 0.8 - 0.15 * k)
        pad = A.sr_scale(t)
        need = pad + len(c)
        if len(out) < need:
            out = out + [0.0] * (need - len(out))
        for i, v in enumerate(c):
            out[pad + i] += v
    sp = A.gain(A.lowpass(A.noise(0.9, 203), 2200), 0.7)
    sp = [v * e for v, e in zip(sp, A.decay_env(0.9, 0.25))]
    pad = A.sr_scale(0.75)
    need = pad + len(sp)
    if len(out) < need:
        out = out + [0.0] * (need - len(out))
    for i, v in enumerate(sp):
        out[pad + i] += v
    return A.reverb(out, 0.25, 0.6)


@asset("SFX_GLASS_SEAL", "sfx", False, "SC05_SH005: the glass sealing over the spark")
def _():
    seal = A.gain(A.lowpass(A.click(0.03, 211, (600, 1600), 150), 1800), 1.0)
    shimmer = A.gain(A.glide(900, 1500, 0.35, 0.25), 1.0)
    shimmer = [v * e for v, e in zip(shimmer, A.decay_env(0.35, 0.15))]
    return A.mix(seal, shimmer)


@asset("SFX_IRON_SHRIEK", "sfx", False, "SC06_SH002: iron shrieking")
def _():
    x = A.bandpass(A.noise(1.5, 221), 2500, 5200)
    return A.amp_env(x, 0.15, 0.4)


@asset("SFX_NEEDLE_FRICTION", "sfx", True,
       "SC06_SH003: the tiny friction of the needle - the quietest moment")
def _():
    x = A.gain(A.highpass(A.noise(4.0, 231), 3000), 0.5)
    n = len(x)
    for i in range(n):
        x[i] *= 0.55 + 0.45 * abs(math.sin(2 * math.pi * 3.1 * i / SR))
    return A.crossfade_loop(x)


@asset("SFX_WIND_BREACH", "sfx", True,
       "SC06_SH005: wind coming through the breach in the door")
def _():
    return A.crossfade_loop(A.wind_bed(3.0, 241, 500, 1100, 0.3, 0.6, 0.5))


@asset("SFX_SHOULDER_SCREAM", "sfx", False,
       "SC07_SH004: one long metallic scream from the shoulder joint")
def _():
    x = A.bandpass(A.noise(2.5, 251), 700, 2600)
    n = len(x)
    out = [0.0] * n
    for i in range(n):
        sweep = 700 + 1800 * (i / n)
        out[i] = x[i] * (0.5 + 0.5 * math.sin(2 * math.pi * sweep * i / SR * 0.004))
    return A.reverb(A.amp_env(out, 0.3, 0.7), 0.3, 0.7)


@asset("SFX_MECHANISM_FAIL", "sfx", False,
       "SC07_SH007: the mechanism audibly failing - metal fatigue")
def _():
    out = [0.0] * A.sr_scale(3.0)
    rnd = __import__("random").Random(261)
    for _ in range(9):
        t = rnd.uniform(0.05, 2.6)
        c = A.gain(A.click(rnd.uniform(0.01, 0.03), rnd.randrange(300, 400),
                           (rnd.uniform(900, 2000), rnd.uniform(2600, 4200)),
                           rnd.uniform(150, 320)), rnd.uniform(0.35, 0.9))
        i0 = A.sr_scale(t)
        for i, v in enumerate(c):
            if i0 + i < len(out):
                out[i0 + i] += v
    return out


@asset("SFX_SPRING_STRAIN", "sfx", False,
       "SC06_SH002: her spring straining - a sound used nowhere else")
def _():
    x = A.glide(280, 880, 2.0, 0.5)
    n = len(x)
    for i in range(n):
        x[i] *= 0.55 + 0.45 * math.sin(2 * math.pi * 11.0 * i / SR)   # taut shiver
    grit = A.gain(A.bandpass(A.noise(2.0, 361), 900, 2800), 0.16)
    out = A.mix(x, grit)
    return A.amp_env(out, 0.25, 0.35)


@asset("SFX_WATER_LAP", "sfx", False,
       "SC03_SH005: water lapping at stone - close, patient")
def _():
    out = [0.0] * A.sr_scale(2.6)
    for k, t in enumerate((0.0, 0.9, 1.7)):
        lap = A.gain(A.lowpass(A.noise(0.8, 371 + k), 900), 0.55 - 0.12 * k)
        m = len(lap)
        for i in range(m):
            lap[i] *= math.sin(math.pi * i / m)
        i0 = A.sr_scale(t)
        for i, v in enumerate(lap):
            out[i0 + i] += v
    return A.reverb(out, 0.15, 0.4)


@asset("SFX_WATER_DROP", "sfx", False,
       "SC08 water drops - 'absolute silence. one water drop.'")
def _():
    return A.reverb(A.plink(720, 0.4, 0.85), 0.35, 0.7)


@asset("SFX_SPRING_CATCH", "sfx", False,
       "SC04_SH005: the first audible catch of her spring - a small bright note")
def _():
    return A.gain(A.music_note(N["C6"], 1.6, 0.6, 0.8), 0.8)


@asset("SFX_SPRING_UNSPOOL", "sfx", False,
       "SC08_SH006: the spring unspooling - a long, thin, singing sound")
def _():
    out = A.glide(880, 220, 4.5, 0.55)
    n = len(out)
    for i in range(n):
        out[i] *= 1.0 + 0.35 * math.sin(2 * math.pi * 6.5 * i / SR)   # tremolo
        out[i] += 0.12 * math.sin(2 * math.pi * 1760 * i / SR) * (1 - i / n)
    return A.amp_env(out, 0.1, 0.5)


@asset("SFX_RATCHET_ENGAGE", "sfx", False,
       "SC08_SH006: then the ratchet engaging - three loud clean clicks")
def _():
    out = A.gain(A.click(0.02, 271, (2200, 4400), 360), 1.0)
    for t in (0.14, 0.28):
        c = A.gain(A.click(0.02, 272, (2200, 4400), 360), 0.9)
        pad = A.sr_scale(t)
        out = out + [0.0] * (pad + len(c) - len(out))
        for i, v in enumerate(c):
            out[pad + i] += v
    return out


@asset("SFX_MECH_WINDDOWN", "sfx", False,
       "SC08_SH006: her mechanism winding down to nothing")
def _():
    whir = A.glide(420, 60, 3.0, 0.4)
    n = len(whir)
    for i in range(n):
        whir[i] *= (1 - i / n) ** 1.6
    x = A.bandpass(whir, 200, 3000)
    last = A.gain(A.click(0.015, 281, (1800, 3400), 260), 0.7)
    out = x + [0.0] * len(last)
    for i, v in enumerate(last):
        out[len(x) - A.sr_scale(0.2) + i] += v
    return out


@asset("SFX_IGNITION_BLOOM", "sfx", False,
       "SC08_SH007: the ignition - a huge, warm, low bloom")
def _():
    chord = A.pad_chord([55.0, 110.0, 146.83, 220.0], 6.0, attack=0.35,
                        release=3.0, detune=1.4)
    sub = A.amp_env(A.sine(55, 6.0, 0.5), 0.3, 2.5)
    warm = A.gain(A.music_note(220, 3.0, 0.5, 1.4), 0.35)
    st = A.widen(A.mix(chord, sub, warm), 0.017, 0.7)
    return st


@asset("SFX_BEACON_ROTATE", "sfx", True,
       "SC09: the beacon's slow rotation - rumble with a soft sweep each pass")
def _():
    rumble = A.gain(A.lowpass(A.noise(8.0, 291), 120), 0.7)
    out = list(rumble)
    for t in (1.0, 5.0):
        whoosh = A.gain(A.bandpass(A.noise(2.2, 292), 200, 700), 0.5)
        m = len(whoosh)
        for i in range(m):
            whoosh[i] *= math.sin(math.pi * i / m)
        i0 = A.sr_scale(t)
        for i, v in enumerate(whoosh):
            if i0 + i < len(out):
                out[i0 + i] += v
    st = A.widen(out, 0.02, 0.5)
    return (A.crossfade_loop(st[0]), A.crossfade_loop(st[1]))


@asset("SFX_BEACON_WINDDOWN", "sfx", False, "SC09_SH003: the beacon winding down")
def _():
    x = A.glide(110, 40, 5.0, 0.4)
    n = len(x)
    for i in range(n):
        x[i] *= (1 - i / n) ** 1.3
    return A.lowpass(x, 400)


@asset("SFX_KEY_LIFT", "sfx", False,
       "SC10_SH003: the key lifting out of the back plate - the opening's metal")
def _():
    scrape = A.gain(A.highpass(A.noise(0.35, 301), 2500), 0.5)
    scrape = A.amp_env(scrape, 0.02, 0.1)
    cl = A.gain(A.click(0.012, 302, (2400, 4600), 320), 0.9)
    out = scrape + [0.0] * len(cl)
    for i, v in enumerate(cl):
        out[len(scrape) - A.sr_scale(0.05) + i] += v
    return out


@asset("SFX_FINAL_CLICK", "sfx", False,
       "SC10_SH004/SH005: ONE click, clean and loud in the silence")
def _():
    return A.gain(A.click(0.016, 311, (2300, 4800), 340), 1.0)


@asset("SFX_COIL_CATCH", "sfx", False, "SC10_SH005: the coil catching")
def _():
    return A.mix(A.click(0.014, 321, (2000, 4000), 300),
                 A.gain(A.plink(1760, 0.3, 0.6), 1.0))


@asset("SFX_SHUTTER_OPEN", "sfx", False,
       "SC10_SH005: the shutter aperture opening - tiny iris ticks + air")
def _():
    out = [0.0] * A.sr_scale(0.7)
    for k, t in enumerate((0.0, 0.09, 0.17)):
        c = A.gain(A.click(0.008, 331 + k, (3000, 5200), 180), 0.4)
        i0 = A.sr_scale(t)
        for i, v in enumerate(c):
            out[i0 + i] += v
    air = A.gain(A.highpass(A.noise(0.5, 332), 4000), 0.12)
    air = A.amp_env(air, 0.1, 0.3)
    i0 = A.sr_scale(0.2)
    for i, v in enumerate(air):
        out[i0 + i] += v
    return out


@asset("SFX_BARE_FOOT_A", "sfx", False,
       "THE CHILD: bare feet on wet iron, near-silent (variant A)")
def _():
    x = A.gain(A.lowpass(A.noise(0.15, 341), 900), 0.8)
    return A.amp_env(x, 0.004, 0.09)


@asset("SFX_BARE_FOOT_B", "sfx", False, "THE CHILD bare foot variant B")
def _():
    x = A.gain(A.lowpass(A.noise(0.15, 342), 750), 0.8)
    return A.amp_env(x, 0.004, 0.1)


@asset("SFX_SPARK_HUM", "sfx", True,
       "SC05_SH005-SC08_SH003: the spark's own warm tone, beating softly")
def _():
    a = A.sine(110, 8.0, 0.5)
    b = A.sine(113.2, 8.0, 0.42)
    c = A.sine(220, 8.0, 0.1)
    return A.crossfade_loop(A.lowpass(A.mix(a, b, c), 900))


@asset("SFX_DRAIN_TICK", "sfx", True,
       "SC05_SH006-007: the drain - a slower tick layered over the gait")
def _():
    out = [0.0] * A.sr_scale(6.0)
    for t in (0.0, 2.0, 4.0):
        c = A.gain(A.click(0.01, 351, (1200, 2400), 180), 0.55)
        i0 = A.sr_scale(t)
        for i, v in enumerate(c):
            out[i0 + i] += v
    return A.crossfade_loop(out, 0.02)


# ---------------------------------------------------------------- music ----

def _motif(spacing, tau, bright, notes, tail=1.4):
    out = [0.0] * A.sr_scale(spacing * (len(notes) - 1) + 1.2 + tail)
    for k, f in enumerate(notes):
        nt = A.music_note(f, 1.2 + tail, bright, tau)
        i0 = A.sr_scale(k * spacing)
        for i, v in enumerate(nt):
            out[i0 + i] += v
    return out


@asset("MUS_CLOCK_A", "music", False,
       "SC01_SH005: her clock motif, first statement - three thin notes, slow")
def _():
    return _motif(0.9, 0.9, 0.55, [N["A5"], N["C6"], N["E6"]])


@asset("MUS_CLOCK_UNRESOLVED", "music", False,
       "SC01_SH006: the motif does not resolve - two notes, then it simply stops")
def _():
    out = [0.0] * A.sr_scale(2.4)
    for k, f in enumerate((N["A5"], N["C6"])):
        nt = A.music_note(f, 1.1, 0.55, 0.8)
        i0 = A.sr_scale(k * 0.8)
        for i, v in enumerate(nt):
            out[i0 + i] += v
    cut = A.sr_scale(1.75)          # hard stop - no tail, no resolution
    for i in range(cut, len(out)):
        out[i] *= max(0.0, 1.0 - (i - cut) / A.sr_scale(0.03))
    return out


@asset("MUS_CLOCK_B", "music", False,
       "SC02_SH005: second statement - noticeably faster than the first")
def _():
    return _motif(0.55, 0.8, 0.55, [N["A5"], N["C6"], N["E6"]])


@asset("MUS_CLOCK_DIST", "music", False,
       "SC04_SH004/SC07_SH007: the motif distorted, slowing, losing pitch")
def _():
    out = [0.0] * A.sr_scale(6.5)
    for k, f in enumerate((N["A5"], N["C6"], N["E6"])):
        nt = A.music_note(f * 0.97, 2.0, 0.4, 1.4)
        nt = A.lowpass(nt, 700)
        i0 = A.sr_scale(k * 1.25)
        for i, v in enumerate(nt):
            if i0 + i < len(out):
                out[i0 + i] += v
    return out


@asset("MUS_CLOCK_SKIP", "music", False,
       "SC07_SH006: the motif stuttering - audibly skipping the middle note")
def _():
    out = [0.0] * A.sr_scale(4.0)
    for k, (t, f) in enumerate(((0.0, N["A5"]), (1.1, N["E6"]))):
        nt = A.music_note(f, 1.3, 0.55, 0.9)
        i0 = A.sr_scale(t)
        for i, v in enumerate(nt):
            out[i0 + i] += v
    # the ghost of the missing note: a failed, choked attack
    ghost = A.gain(A.music_note(N["C6"], 0.25, 0.5, 0.12), 0.25)
    i0 = A.sr_scale(0.55)
    for i, v in enumerate(ghost):
        out[i0 + i] += v
    return out


@asset("MUS_CLOCK_COMPLETE", "music", False,
       "SC08_SH005: the only complete statement in the film, single instrument")
def _():
    out = _motif(0.85, 1.1, 0.6, [N["A5"], N["C6"], N["E6"]])
    oct_ = A.gain(A.music_note(N["A4"], 3.0, 0.4, 1.6), 0.5)
    i0 = A.sr_scale(1.7)
    out = out + [0.0] * (i0 + len(oct_) - len(out))
    for i, v in enumerate(oct_):
        out[i0 + i] += v
    return out


@asset("MUS_SHIP_MOTIF", "music", False,
       "SC02_SH003: the ship's motif - two descending notes, first statement")
def _():
    out = [0.0] * A.sr_scale(4.0)
    for t, f in ((0.0, N["D4"]), (1.3, N["A3"])):
        nt = A.horn_note(f, 1.6)
        i0 = A.sr_scale(t)
        for i, v in enumerate(nt):
            out[i0 + i] += v
    return out


@asset("MUS_SHIP_RESOLVE", "music", False,
       "SC09_SH002: the ship's motif resolved upward for the first time")
def _():
    out = [0.0] * A.sr_scale(4.0)
    for t, f in ((0.0, N["D4"]), (1.3, N["A4"])):
        nt = A.horn_note(f, 1.6)
        i0 = A.sr_scale(t)
        for i, v in enumerate(nt):
            out[i0 + i] += v
    return out


@asset("MUS_STRINGS_MAJOR", "music", False,
       "SC03_SH003: the music opens out - the only major-key passage in the film")
def _():
    return A.pad_chord([N["F3"], N["A3"], N["C4"], N["F4"]], 12.0,
                       attack=2.0, release=2.5)


@asset("MUS_FORWARD", "music", False,
       "SC02_SH006: the score's first forward motion underneath")
def _():
    out = [0.0] * A.sr_scale(10.0)
    step, k = 0.3, 0
    while step * k < 9.4:
        f = N["A3"] if k % 2 == 0 else N["E4"]
        nt = A.gain(A.music_note(f, 0.5, 0.35, 0.35), 0.3 + 0.4 * (k / 32))
        i0 = A.sr_scale(step * k)
        for i, v in enumerate(nt):
            if i0 + i < len(out):
                out[i0 + i] += v
        if k % 4 == 0:
            b = A.gain(A.horn_note(N["D2"] * 2, 1.1, 0.05), 0.18)
            for i, v in enumerate(b):
                if i0 + i < len(out):
                    out[i0 + i] += v
        k += 1
    return out


@asset("MUS_SINGLE_NOTE", "music", False,
       "SC07_SH005: the score returns - one bright note, one instrument only")
def _():
    return A.music_note(N["E6"], 5.0, 0.6, 1.5)


@asset("MUS_IGNITION_FULL", "music", False,
       "SC08_SH007: the score in full, for the first and only time")
def _():
    chord = A.pad_chord([N["D2"], N["A2"], N["D3"], N["Fs3"], N["A3"], N["D4"]],
                        10.0, attack=0.5, release=4.0, detune=1.2)
    top = A.gain(A.music_note(N["A4"], 4.0, 0.5, 1.8), 0.3)
    i0 = A.sr_scale(0.8)
    chord = chord + [0.0] * (i0 + len(top) - len(chord))
    for i, v in enumerate(top):
        chord[i0 + i] += v
    st = A.widen(chord, 0.015, 0.6)
    return st


@asset("MUS_BEACON_SUSTAIN", "music", False,
       "SC09_SH001-002: score sustained, no melody")
def _():
    return A.pad_chord([N["D2"], N["A2"], N["D3"]], 16.0, attack=3.0, release=4.0)


@asset("MUS_THINNING", "music", False,
       "SC09_SH003: the score thinning to nothing")
def _():
    pad = A.pad_chord([N["D3"], N["A3"]], 10.0, attack=0.8, release=1.0)
    n = len(pad)
    return [v * (1 - i / n) ** 2.2 for i, v in enumerate(pad)]


# ------------------------------------------------------------------ main ----

def main():
    manifest = []
    for id, category, loop, purpose, fn in ASSETS:
        audio = fn()
        if isinstance(audio, tuple):
            audio = A.normalize_st(audio)
            if not loop:
                audio = A.trim_st(audio)
        else:
            audio = A.normalize(audio)
            if not loop:
                audio = A.trim(audio)
        path = os.path.join(OUT, category, f"{id}.wav")
        info = A.wav_write(path, audio)
        manifest.append(dict(id=id, category=category, loop=loop, purpose=purpose,
                             rel_path=os.path.relpath(path, os.path.join(OUT, "..")),
                             provenance="procedurally synthesized in-repo "
                                        "(audio_synth.py, pure Python stdlib) - "
                                        "original, no samples, no license needed",
                             **info))
        print(f"  {id:<24} {info['dur']:>7.2f}s  {'stereo' if info['channels'] == 2 else 'mono  '}  peak {info['peak']:.3f}")
    with open(os.path.join(OUT, "ASSETS_MANIFEST.json"), "w", encoding="utf-8") as fh:
        json.dump(dict(schema_version=1, task_id="T09_AUDIO", sample_rate=SR,
                       bit_depth=16, asset_count=len(manifest),
                       total_dur=round(sum(m["dur"] for m in manifest), 2),
                       assets=manifest), fh, indent=2)
        fh.write("\n")
    print(f"{len(manifest)} assets, {sum(m['dur'] for m in manifest):.1f}s total ->", OUT)


if __name__ == "__main__":
    main()
