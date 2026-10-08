#!/usr/bin/env python3
"""
assemble_candidate - Step 17 C: build FINAL/FINAL_FILM_REPAIRED_CANDIDATE.mp4

Video timeline (7248 frames @24, unchanged timing):
  1-6768     decoded verbatim from the existing FINAL/FINAL_FILM.mp4
             (unaffected scenes preserved; original file untouched)
  6769-7176  repaired SC10 per-shot segments from 13_RENDER/REPAIR_CHUNKS/
             (SC10_SH001..SH004, authored shot cameras + repaired lighting)
  7177-7248  authored cut-to-black, emitted as black frames (unchanged intent)

Audio: 10_AUDIO/mix/FINAL_MIX.wav (measured -16.34 LUFS / -1.50 dBTP),
AAC 128k, timestamp-merged with video (PyAV).

Run: python3 13_RENDER/scripts/assemble_candidate.py
"""
import os
import wave
from fractions import Fraction

import av
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OLD = os.path.join(ROOT, "FINAL", "FINAL_FILM.mp4")
WAV = os.path.join(ROOT, "10_AUDIO", "mix", "FINAL_MIX.wav")
SEGDIR = os.path.join(ROOT, "13_RENDER", "REPAIR_CHUNKS")
OUT = os.path.join(ROOT, "FINAL", "FINAL_FILM_REPAIRED_CANDIDATE.mp4")
CUT_BLACK_FROM = 7177
TOTAL = 7248

# ---- collect video frames in order -------------------------------------
frames = []
inp = av.open(OLD)
vs = next(s for s in inp.streams if s.type == "video")
for fr in inp.decode(vs):
    if len(frames) >= 6768:
        break
    frames.append(fr.to_ndarray(format="rgb24"))
inp.close()
print("old-final frames taken:", len(frames), flush=True)

for shot in ("SC10_SH001", "SC10_SH002", "SC10_SH003", "SC10_SH004"):
    seg = av.open(os.path.join(SEGDIR, f"{shot}.mp4"))
    sv = next(s for s in seg.streams if s.type == "video")
    n0 = len(frames)
    for fr in seg.decode(sv):
        frames.append(fr.to_ndarray(format="rgb24"))
    seg.close()
    print(f"segment {shot}: +{len(frames) - n0} frames", flush=True)

while len(frames) < TOTAL:
    frames.append(np.zeros((180, 320, 3), np.uint8))
print("black ending frames:", TOTAL - (CUT_BLACK_FROM - 1), flush=True)
assert len(frames) == TOTAL

# ---- audio ---------------------------------------------------------------
w = wave.open(WAV)
fs = w.getframerate()
nch = w.getnchannels()
raw = np.frombuffer(w.readframes(w.getnframes()),
                    dtype=np.int16).astype(np.float32) / 32768.0
raw = raw.reshape(-1, nch)
w.close()
a_total = raw.shape[0]

out = av.open(OUT, "w")
ov = out.add_stream("libx264", rate=24)
ov.width, ov.height, ov.pix_fmt = 320, 180, "yuv420p"
ov.options = {"crf": "18", "preset": "fast"}
oa = out.add_stream("aac", rate=fs)
oa.bit_rate = 128_000
oa.layout = "stereo"

CH = 1024
apk = []
for i in range(0, a_total, CH):
    blk = raw[i:i + CH]
    if blk.shape[0] < CH:
        blk = np.concatenate([blk, np.zeros((CH - blk.shape[0], nch),
                                            np.float32)])
    af = av.AudioFrame.from_ndarray(blk.T.copy(), format="fltp")
    af.sample_rate = fs
    af.pts = i
    apk += oa.encode(af)
apk += oa.encode()
apk = [(p.pts / float(fs), p) for p in apk]

vpk = []
for i, arr in enumerate(frames):
    vf = av.VideoFrame.from_ndarray(arr, format="rgb24")
    vf.pts = i
    vf.time_base = Fraction(1, 24)
    for p in ov.encode(vf):
        vpk.append((p.pts * float(p.time_base), p))
for p in ov.encode():
    vpk.append((p.pts * float(p.time_base), p))
# NOTE: keep encode (dts) order for video; sorting by pts breaks dts monotonicity

ai = vi = 0
while vi < len(vpk) or ai < len(apk):
    if ai < len(apk) and (vi >= len(vpk) or apk[ai][0] <= vpk[vi][0]):
        _, p = apk[ai]
        p.stream = oa
        ai += 1
    else:
        _, p = vpk[vi]
        p.stream = ov
        vi += 1
    out.mux(p)
out.close()
print(f"CANDIDATE DONE {len(vpk)} video packets, {len(apk)} audio packets, "
      f"{os.path.getsize(OUT)} bytes", flush=True)
