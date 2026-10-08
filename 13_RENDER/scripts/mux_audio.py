#!/usr/bin/env python3
"""
mux_audio - Stage 14: FINAL_FILM.mp4 final mux.

The headless bpy FFMPEG animation render writes a SILENT AAC track even
though the sequencer audio evaluates fine (verified: sound-strip mixdown
peak 0.55 vs rendered-track peak 0.0). PyAV 18 offers no stream copy, so
the rendered H.264 video is transcoded once more (libx264 CRF 18, same
320x180 24fps) while 10_AUDIO/mix/FINAL_MIX.wav (measured -16.34 LUFS /
-1.50 dBTP) is encoded to AAC 128k; both packet lists are merged on
timestamps and muxed. Output replaces FINAL/FINAL_FILM.mp4.

Run: python3 13_RENDER/scripts/mux_audio.py
"""
import os
import wave
from fractions import Fraction

import av
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(ROOT, "FINAL", "FINAL_FILM.mp4")
WAV = os.path.join(ROOT, "10_AUDIO", "mix", "FINAL_MIX.wav")
TMP = os.path.join(ROOT, "FINAL", "FINAL_FILM_MUXED.mp4")

inp = av.open(SRC)
vs = next(s for s in inp.streams if s.type == "video")

w = wave.open(WAV)
fs = w.getframerate()
nch = w.getnchannels()
n = w.getnframes()
raw = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768.0
raw = raw.reshape(-1, nch)
w.close()
a_total = raw.shape[0]

out = av.open(TMP, "w")
out_vs = out.add_stream("libx264", rate=24)
out_vs.width = vs.width
out_vs.height = vs.height
out_vs.pix_fmt = "yuv420p"
out_vs.options = {"crf": "18", "preset": "fast"}
out_as = out.add_stream("aac", rate=fs)
out_as.bit_rate = 128_000
out_as.layout = "stereo"

# 1) encode ALL audio up front: exact, no overlap, no padding leaks
CH = 1024
apk = []
for i in range(0, a_total, CH):
    blk = raw[i:i + CH]
    if blk.shape[0] < CH:
        blk = np.concatenate([blk, np.zeros((CH - blk.shape[0], nch),
                                            np.float32)])
    fr = av.AudioFrame.from_ndarray(blk.T.copy(), format="fltp")
    fr.sample_rate = fs
    fr.pts = i
    apk += out_as.encode(fr)
apk += out_as.encode()
apk = [(p.pts / float(fs), p) for p in apk]

# 2) encode ALL video
vpk = []
nfr = 0
for fr in inp.decode(vs):
    fr.pts = nfr
    fr.time_base = Fraction(1, 24)
    for p in out_vs.encode(fr):
        vpk.append((p.pts * float(p.time_base), p))
    nfr += 1
for p in out_vs.encode():
    vpk.append((p.pts * float(p.time_base), p))
inp.close()

# 3) merge on time and mux
vpk.sort(key=lambda x: x[0])
ai = vi = 0
while vi < len(vpk) or ai < len(apk):
    take_a = ai < len(apk) and (vi >= len(vpk) or apk[ai][0] <= vpk[vi][0])
    if take_a:
        t, p = apk[ai]
        p.stream = out_as
        ai += 1
    else:
        t, p = vpk[vi]
        p.stream = out_vs
        vi += 1
    out.mux(p)
out.close()

os.replace(TMP, SRC)
print(f"MUX DONE {nfr} video frames, {len(apk)} audio packets, "
      f"{os.path.getsize(SRC)} bytes", flush=True)
