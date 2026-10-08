#!/usr/bin/env python3
"""
audio_synth - deterministic procedural audio synthesis (pure Python stdlib).

NINETY-TWO TURNS has no dialogue; the soundtrack IS the performance
(CHARACTER_BIBLE: "all 'speech' in the film is sound design"). Everything
here is synthesized in-repo from math - no samples, no libraries, nothing
licensed. Deterministic: same seed -> same bytes.

Convention: mono assets are float lists at SR; stereo assets are
(left, right) tuples. Written as 16-bit PCM WAV.
"""
from array import array as _arr
import math
import os
import random
import wave

SR = 48000


# ------------------------------------------------------------------ basics ---

def sr_scale(dur):
    return int(round(dur * SR))


def noise(dur, seed=1):
    rnd = random.Random(seed)
    n = sr_scale(dur)
    return [rnd.uniform(-1.0, 1.0) for _ in range(n)]


def sine(freq, dur, amp=1.0, phase=0.0):
    n = sr_scale(dur)
    w = 2.0 * math.pi * freq / SR
    return [amp * math.sin(w * i + phase) for i in range(n)]


def glide(f0, f1, dur, amp=1.0):
    """Sine with linear pitch glide (phase-continuous)."""
    n = sr_scale(dur)
    out = [0.0] * n
    ph = 0.0
    for i in range(n):
        t = i / n
        f = f0 + (f1 - f0) * t
        ph += 2.0 * math.pi * f / SR
        out[i] = amp * math.sin(ph)
    return out


def lowpass(xs, cutoff):
    a = 1.0 - math.exp(-2.0 * math.pi * cutoff / SR)
    y = 0.0
    out = [0.0] * len(xs)
    for i, x in enumerate(xs):
        y += a * (x - y)
        out[i] = y
    return out


def highpass(xs, cutoff):
    lp = lowpass(xs, cutoff)
    return [x - y for x, y in zip(xs, lp)]


def bandpass(xs, lo, hi):
    return lowpass(highpass(xs, lo), hi)


def amp_env(xs, attack=0.0, release=0.0, curve=1.0):
    n = len(xs)
    a = min(sr_scale(attack), n // 2)
    r = min(sr_scale(release), n // 2)
    out = list(xs)
    for i in range(a):
        out[i] *= (i / a) ** curve
    for i in range(r):
        out[n - 1 - i] *= (i / r) ** curve
    return out


def decay_env(dur, tau):
    """Multiplicative exponential decay, one multiply per sample."""
    n = sr_scale(dur)
    k = math.exp(-1.0 / (tau * SR))
    out = [0.0] * n
    v = 1.0
    for i in range(n):
        out[i] = v
        v *= k
    return out


def mix(*layers):
    n = max(len(l) for l in layers)
    out = [0.0] * n
    for l in layers:
        for i, v in enumerate(l):
            out[i] += v
    return out


def gain(xs, g):
    return [v * g for v in xs]


def delay_add(xs, seconds, g):
    d = sr_scale(seconds)
    out = list(xs) + [0.0] * d
    for i, v in enumerate(xs):
        out[i + d] += v * g
    return out


def reverb(xs, wet=0.3, rt=0.6):
    """Cheap Schroeder-ish tail: decaying delay taps."""
    out = list(xs)
    for t, g in ((0.037, 0.5), (0.053, 0.4), (0.079, 0.3), (0.113, 0.22)):
        out = delay_add(out, t, g * wet * (rt / 0.6))
    return out


def stereo(xs_l, xs_r=None):
    return (xs_l, xs_r if xs_r is not None else list(xs_l))


def widen(xs, decorr=0.012, g=0.6):
    """Fake stereo: decorrelated delayed copy on the right."""
    d = sr_scale(decorr)
    right = list(xs) + [0.0] * d
    for i, v in enumerate(xs):
        right[i + d] += v * g
    return (list(xs), right[d:d + len(xs)] if len(right) >= d + len(xs) else right)


def crossfade_loop(xs, xfade=0.05):
    """Make a buffer seamlessly loopable: fold tail into head."""
    n = len(xs)
    f = sr_scale(xfade)
    f = min(f, n // 4)
    out = list(xs)
    for i in range(f):
        w = i / f
        out[i] = xs[i] * w + xs[n - f + i] * (1.0 - w)
    return out[:n - f]


def normalize(xs, peak=0.891):
    m = max((abs(v) for v in xs), default=0.0)
    if m <= 0:
        return xs
    g = peak / m
    return [v * g for v in xs]


def normalize_st(st, peak=0.891):
    m = max(max((abs(v) for v in st[0]), default=0.0),
            max((abs(v) for v in st[1]), default=0.0))
    if m <= 0:
        return st
    g = peak / m
    return ([v * g for v in st[0]], [v * g for v in st[1]])


def trim(xs, floor=0.0005):
    """Cut leading/trailing near-silence from a one-shot."""
    idx = [i for i, v in enumerate(xs) if abs(v) > floor]
    if not idx:
        return xs
    return xs[max(0, idx[0] - 24):idx[-1] + 25]


def trim_st(st, floor=0.0005):
    idx = [i for i in range(len(st[0]))
           if abs(st[0][i]) > floor or abs(st[1][i]) > floor]
    if not idx:
        return st
    a, b = max(0, idx[0] - 24), idx[-1] + 25
    return (st[0][a:b], st[1][a:b])


def peak_of(xs):
    if isinstance(xs, tuple):
        return max(max(abs(v) for v in xs[0]), max(abs(v) for v in xs[1]))
    return max((abs(v) for v in xs), default=0.0)


# -------------------------------------------------------------------- wav ----

def _int16(xs):
    a = _arr("h", [0] * len(xs))
    for i, v in enumerate(xs):
        v = max(-1.0, min(1.0, v))
        a[i] = int(v * 32767)
    return a


def wav_write(path, audio, rate=SR):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if isinstance(audio, tuple):
        l, r = audio
        n = min(len(l), len(r))
        data = _arr("h", [0] * (2 * n))
        for i in range(n):
            data[2 * i] = int(max(-1.0, min(1.0, l[i])) * 32767)
            data[2 * i + 1] = int(max(-1.0, min(1.0, r[i])) * 32767)
        ch = 2
    else:
        data = _int16(audio)
        ch = 1
    with wave.open(path, "wb") as w:
        w.setnchannels(ch)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(data.tobytes())
    return dict(path=path, rate=rate, channels=ch, frames=len(data) // ch,
                dur=round(len(data) / ch / rate, 4), peak=round(peak_of(audio), 4))


# ----------------------------------------------------------------- voices ----

def music_note(freq, dur, bright=1.0, tau=0.9):
    """Music-box / harp pluck: harmonic stack, higher partials decay faster."""
    out = [0.0] * sr_scale(dur)
    for k in (1, 2, 3, 4, 5):
        amp = bright ** (k - 1) / k
        env = decay_env(dur, tau / (1 + 0.7 * (k - 1)))
        s = sine(freq * k, dur)
        for i in range(len(out)):
            out[i] += s[i] * env[i] * amp
    return out


def horn_note(freq, dur, attack=0.08):
    """Soft horn: fundamental + quiet 2nd/3rd, slow attack."""
    out = mix(gain(sine(freq, dur), 1.0),
              gain(sine(freq * 2, dur), 0.18),
              gain(sine(freq * 3, dur), 0.07))
    return amp_env(out, attack=attack, release=min(0.3, dur / 3))


def pad_chord(freqs, dur, attack=1.2, release=1.5, detune=0.9):
    """Warm string pad: detuned partial pairs, slow attack."""
    n = sr_scale(dur)
    out = [0.0] * n
    for f in freqs:
        for cents in (-detune, detune):
            ff = f * (2.0 ** (cents / 1200.0))
            s = sine(ff, dur, amp=0.5 / len(freqs))
            for i in range(n):
                out[i] += s[i]
    return amp_env(out, attack=attack, release=release)


def bell(freq, dur, amp=1.0):
    """Struck metal: inharmonic partials, long decay."""
    out = [0.0] * sr_scale(dur)
    for ratio, a, tau in ((1.0, 1.0, 2.2), (2.76, 0.45, 1.3), (5.4, 0.2, 0.7),
                          (8.93, 0.08, 0.4)):
        env = decay_env(dur, tau)
        s = sine(freq * ratio, dur)
        for i in range(len(out)):
            out[i] += s[i] * env[i] * a
    return gain(out, amp)


def click(dur=0.01, seed=1, band=(2200, 4200), body=320.0):
    """Dry mechanical click: bandpassed noise burst + body thock."""
    b = bandpass(noise(dur, seed), *band)
    env = decay_env(dur, dur * 0.5)
    b = [v * e for v, e in zip(b, env)]
    thock = gain(sine(body, dur * 2.5), 0.5)
    thock = [v * e for v, e in zip(thock, decay_env(dur * 2.5, dur))]
    return mix(b, thock)


def plink(freq, dur=0.35, amp=0.8):
    """Single water-drop / spring-catch plink."""
    g = glide(freq * 1.6, freq * 0.9, dur * 0.25)
    tail = sine(freq, dur)
    env = decay_env(dur, dur * 0.35)
    out = [v * e for v, e in zip(mix(g, tail), env)]
    return gain(out, amp)


def chirp(f0, f1, dur=0.09, amp=0.5):
    """Bird chirp: fast FM-ish sweep."""
    return amp_env(glide(f0, f1, dur, amp=amp), attack=0.005, release=0.03)


def wind_bed(dur, seed, base_lo=80, base_hi=500, gust_hz=0.09, gust_depth=0.6,
             level=0.5):
    """Wind: filtered noise with slow gusting AM."""
    n = sr_scale(dur)
    x = bandpass(noise(dur, seed), base_lo, base_hi)
    rnd = random.Random(seed + 7)
    # smooth random gust envelope
    seg = SR // 4
    pts = [rnd.uniform(1.0 - gust_depth, 1.0) for _ in range(n // seg + 3)]
    out = [0.0] * n
    for i in range(n):
        j = i // seg
        w = (i % seg) / seg
        g = pts[j] * (1 - w) + pts[j + 1] * w
        out[i] = x[i] * g * level
    return out
