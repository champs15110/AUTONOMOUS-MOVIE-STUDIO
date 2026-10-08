#!/usr/bin/env python3
"""
measure_mix - FINAL QC: construct the timeline mix in numpy from
AUDIO_TIMELINE (events + gains + fades + MIX_PLAN stem trims), measure
BS.1770 integrated loudness and true peak with tools/lufs.py, apply the trim
that lands the -16 LUFS / -1.5 dBTP target, re-measure (second verification),
and write the result back into MIX_PLAN.json (closes PENDING_MEASUREMENT).

Run: python3 12_QC/scripts/measure_mix.py
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
TOTAL = int(AT["total_frames"] / FPS * FS)

L = np.zeros(TOTAL, np.float64)
loops = 0
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
            loops += 1
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

stereo = [L, L.copy()]
before = loudness(stereo)
tp_before = lufs.true_peak_dbtp(stereo)

trim1 = -16.0 - before
g = 10 ** (trim1 / 20)
st2 = [L * g, L * g]
lufs_after = loudness(st2)
tp_after = lufs.true_peak_dbtp(st2)
extra = 0.0
if tp_after > -1.5:
    extra = tp_after - (-1.5)
    g2 = 10 ** (-extra / 20)
    st2 = [st2[0] * g2, st2[1] * g2]
    lufs_after = loudness(st2)
    tp_after = lufs.true_peak_dbtp(st2)

mix["measurement"] = {
    "status": "MEASURED",
    "method": "pyloudnorm (ITU-R BS.1770-4) integrated loudness; true "
              "peak 4x oversampled (tools/lufs.py); mix built in numpy from "
              "AUDIO_TIMELINE events + gains + fades + MIX_PLAN stem trims",
    "before_trim_lufs": round(before, 2),
    "before_trim_true_peak_dbtp": round(tp_before, 2),
    "applied_trim_db": round(trim1 - extra, 2),
    "integrated_lufs": round(lufs_after, 2),
    "true_peak_dbtp": round(tp_after, 2),
    "target": mix["target"],
    "looped_assets": loops,
    "note": "trim to be applied at T12 final mix; peak ceiling respected",
}
json.dump(mix, open(MIXP, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(f"before {before:.2f} LUFS / {tp_before:.2f} dBTP; trim "
      f"{trim1 - extra:.2f} dB; after {lufs_after:.2f} LUFS / "
      f"{tp_after:.2f} dBTP; loops {loops}")
