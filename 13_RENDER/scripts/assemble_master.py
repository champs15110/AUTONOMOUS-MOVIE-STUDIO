#!/usr/bin/env python3
"""
assemble_master - assemble the shot-accurate final master.

Video: EDIT_TIMELINE shot order; frames decoded verbatim from each shot's
verified segment in 13_RENDER/SHOT_RENDERS/ (SC10_SH005 = authored
cut-to-black emitted as black frames). Audio: 10_AUDIO/mix/FINAL_MIX.wav
(-16.34 LUFS / -1.50 dBTP) as AAC 128k, timestamp-merged.

Output: FINAL/FINAL_FILM_CANDIDATE_V2.mp4 (never overwrites FINAL_FILM.mp4).

Run: python3 13_RENDER/scripts/assemble_master.py
"""
import os
import json
import wave
from fractions import Fraction

import av
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SEG = os.path.join(ROOT, "13_RENDER", "SHOT_RENDERS")
WAV = os.path.join(ROOT, "10_AUDIO", "mix", "FINAL_MIX.wav")
OUT = os.path.join(ROOT, "FINAL", "FINAL_FILM_CANDIDATE_V2.mp4")
EDL = json.load(open(os.path.join(ROOT, "11_EDIT", "EDIT_TIMELINE.json"),
                     encoding="utf-8"))
SHOTS = EDL["shots"]
AUTHORED_BLACK = {"SC10_SH005"}

frames = []
manifest = []
for sh in SHOTS:
    sid = sh["shot_id"]
    f0, f1 = sh["record_frame_in"], sh["record_frame_out"]
    want = f1 - f0 + 1
    if sid in AUTHORED_BLACK:
        frames += [np.zeros((360, 640, 3), np.uint8)] * want
        manifest.append(dict(shot_id=sid, frames=[f0, f1], source="authored_black"))
        continue
    seg = av.open(os.path.join(SEG, f"{sid}.mp4"))
    sv = next(s for s in seg.streams if s.type == "video")
    n0 = len(frames)
    for fr in seg.decode(sv):
        frames.append(fr.to_ndarray(format="rgb24"))
    seg.close()
    got = len(frames) - n0
    assert got == want, f"{sid}: decoded {got} frames, expected {want}"
    manifest.append(dict(shot_id=sid, frames=[f0, f1], source=f"{sid}.mp4",
                         decoded=got))
    print(f"{sid}: +{got}", flush=True)

TOTAL = EDL["total_frames"]
assert len(frames) == TOTAL, f"{len(frames)} != {TOTAL}"
print(f"all {len(SHOTS)} shots assembled: {len(frames)} frames", flush=True)
json.dump(dict(schema_version=1, shots=manifest, total_frames=TOTAL),
          open(os.path.join(ROOT, "13_RENDER", "SHOT_RENDERS",
                            "ASSEMBLY_MANIFEST.json"), "w"), indent=2)

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
ov.width, ov.height, ov.pix_fmt = 640, 360, "yuv420p"
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
print(f"MASTER CANDIDATE DONE {os.path.getsize(OUT)} bytes", flush=True)
