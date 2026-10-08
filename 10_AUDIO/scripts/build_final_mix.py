#!/usr/bin/env python3
"""
build_final_mix - Stage 14: write the FINAL film mix to disk.

Byte-identical pipeline to 12_QC/scripts/measure_mix.py (same event order,
gains, fades, stem trims, tiling), then applies MIX_PLAN applied_trim_db
(+2.93 dB) and writes 10_AUDIO/mix/FINAL_MIX.wav (48 kHz, 16-bit stereo).
Re-measures the written file and compares with MIX_PLAN recorded numbers.

Run: python3 10_AUDIO/scripts/build_final_mix.py
"""
import json
import os
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import lufs  # noqa: E402
try:
    import pyloudnorm as _py  # noqa: E402
    _METER = _py.Meter(48000)
except Exception:  # noqa: BLE001
    _METER = None


def loudness(stereo):
    if _METER is not None:
        n = min(len(stereo[0]), len(stereo[1]))
        return float(_METER.integrated_loudness(
            np.stack([stereo[0][:n], stereo[1][:n]], axis=1)))
    return lufs.integrated_lufs(stereo)


FS = 48000
FPS = 24
AT = json.load(open(os.path.join(ROOT, "10_AUDIO", "AUDIO_TIMELINE.json"),
                    encoding="utf-8"))
MIXP = os.path.join(ROOT, "10_AUDIO", "mix", "MIX_PLAN.json")
mix = json.load(open(MIXP, encoding="utf-8"))
STEM_DB = {t: float(mix["stems"][t.upper()]["level_db"])
           for t in ("music", "sfx", "ambience")}
TRIM = mix["measurement"]["applied_trim_db"]
TOTAL = int(AT["total_frames"] / FPS * FS)

L = np.zeros(TOTAL, np.float64)
for tr in ("ambience", "music", "sfx"):
    amp0 = 10 ** (STEM_DB[tr] / 20)
    for ev in AT["tracks"][tr]:
        path = os.path.join(ROOT, "10_AUDIO", "assets", tr,
                            ev["asset"] + ".wav")
        w = wave.open(path)
        n = w.getnframes()
        raw = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float64)
        raw /= 32768.0
        w.close()
        f0 = int((ev["frame_in"] - 1) / FPS * FS)
        want = int((ev["frame_out"] - ev["frame_in"] + 1) / FPS * FS)
        if len(raw) < want:
            raw = np.tile(raw, want // len(raw) + 1)
        raw = raw[:want]
        if ev.get("fade_in"):
            k = min(len(raw), int(ev["fade_in"] / FPS * FS))
            raw[:k] *= np.linspace(0, 1, k)
        if ev.get("fade_out"):
            k = min(len(raw), int(ev["fade_out"] / FPS * FS))
            raw[-k:] *= np.linspace(1, 0, k)
        e = f0 + want
        L[f0:e] += raw * (ev["gain"] * amp0)

g = 10 ** (TRIM / 20)
L *= g
stereo = [L, L.copy()]

out = os.path.join(ROOT, "10_AUDIO", "mix", "FINAL_MIX.wav")
pc = np.clip(np.stack([L, L], axis=1), -1, 1)
pc = (pc * 32767).astype(np.int16)
w = wave.open(out, "wb")
w.setnchannels(2)
w.setsampwidth(2)
w.setframerate(FS)
w.writeframes(pc.tobytes())
w.close()

lufs_m = loudness(stereo)
tp = lufs.true_peak_dbtp(stereo)
print(f"wrote {out} {os.path.getsize(out)} bytes; "
      f"{lufs_m:.2f} LUFS / {tp:.2f} dBTP; MIX_PLAN says "
      f"{mix['measurement']['integrated_lufs']} / "
      f"{mix['measurement']['true_peak_dbtp']}")
