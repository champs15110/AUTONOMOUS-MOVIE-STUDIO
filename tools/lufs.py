#!/usr/bin/env python3
"""
lufs - ITU-R BS.1770-4 loudness meter (48 kHz) in numpy/scipy.

Closes the T09 deferred measurement (MIX_PLAN PENDING_MEASUREMENT) without
ffmpeg: K-weighting (high shelf + 38 Hz high-pass), 400 ms gated blocks with
75% overlap, absolute gate -70 LUFS, relative gate -10 LU; true peak via 4x
oversampling.
"""
import numpy as np
from scipy.signal import lfilter, resample_poly


def _biquads(fs=48000.0):
    """K-weighting per BS.1770 design parameters (RBJ audio EQ formulas)."""
    # stage 1: high shelf f0=1681.97 Hz, G=+3.99984 dB, Q=0.70718
    f0, G, Q = 1681.97, 3.999843092376024, 0.7071752766589209
    A = 10.0 ** (G / 40.0)
    w0 = 2.0 * np.pi * f0 / fs
    al = np.sin(w0) / (2.0 * Q)
    c = np.cos(w0)
    s = np.sqrt(A)
    b0 = A * ((A + 1) + (A - 1) * c + 2 * s * al)
    b1 = -2 * A * ((A - 1) + (A + 1) * c)
    b2 = A * ((A + 1) + (A - 1) * c - 2 * s * al)
    a0 = (A + 1) + (A - 1) * c + 2 * s * al
    a1 = -2 * ((A - 1) + (A + 1) * c)
    a2 = (A + 1) + (A - 1) * c - 2 * s * al
    shelf_b = np.array([b0, b1, b2]) / a0
    shelf_a = np.array([a0, a1, a2]) / a0
    # stage 2: high-pass f0=38.13547 Hz, Q=0.50033
    f0, Q = 38.13547087602444, 0.5003284219260984
    w0 = 2.0 * np.pi * f0 / fs
    al = np.sin(w0) / (2.0 * Q)
    c = np.cos(w0)
    hp_b = np.array([(1 + c) / 2, -(1 + c), (1 + c) / 2])
    hp_a = np.array([1 + al, -2 * c, 1 - al])
    hp_b = hp_b / hp_a[0]
    hp_a = hp_a / hp_a[0]
    return shelf_b, shelf_a, hp_b, hp_a


SHELF_B, SHELF_A, HP_B, HP_A = _biquads()


def k_weight(x, fs=48000):
    assert fs == 48000, "coefficients are for 48 kHz"
    x = lfilter(SHELF_B, SHELF_A, x)
    return lfilter(HP_B, HP_A, x)


def integrated_lufs(channels, fs=48000):
    """channels: list of 1-D float arrays (mono -> [x]); returns LUFS."""
    block = int(0.4 * fs)
    step = block // 4
    n = min(len(c) for c in channels)
    kw = [k_weight(c[:n].astype(np.float64)) for c in channels]
    gates = []
    for i in range(0, n - block + 1, step):
        g = 0.0
        for y in kw:
            seg = y[i:i + block]
            g += float(np.mean(seg * seg))
        if g > 0:
            gates.append(-0.691 + 10 * np.log10(g))
    abs_g = [l for l in gates if l > -70.0]
    if not abs_g:
        return -70.0
    mean_lin = np.mean([10 ** (l / 10) for l in abs_g])
    rel = -0.691 + 10 * np.log10(mean_lin) - 10.0
    rel_g = [l for l in abs_g if l > rel]
    if not rel_g:
        return rel
    m = np.mean([10 ** (l / 10) for l in rel_g])
    return float(-0.691 + 10 * np.log10(m))


def true_peak_dbtp(channels, fs=48000):
    tp = 0.0
    for c in channels:
        up = resample_poly(c.astype(np.float64), 4, 1)
        tp = max(tp, float(np.max(np.abs(up))))
    return 20 * np.log10(tp) if tp > 0 else -100.0
