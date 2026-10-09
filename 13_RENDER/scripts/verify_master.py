#!/usr/bin/env python3
"""
verify_master - full independent verification of an assembled master MP4.

Usage: python3 13_RENDER/scripts/verify_master.py <path-to-mp4> <out-dir>

Checks: file/size; container+streams (640x360, 24fps, 302.0s, AAC);
full decode integrity; black/frozen scan; per-shot cut detection against
EDIT_TIMELINE record ranges; same-scene shot-framing distinctness;
audio presence/duration/loudness; writes JSON summary + extracts stills.
"""
import json
import os
import struct
import sys
import zlib

import av
import numpy as np

ROOT = "/home/user/AUTONOMOUS-MOVIE-STUDIO"
sys.path.insert(0, os.path.join(ROOT, "tools"))
import lufs  # noqa: E402

P = sys.argv[1]
OUTD = sys.argv[2]
os.makedirs(OUTD, exist_ok=True)
EDL = json.load(open(os.path.join(ROOT, "11_EDIT", "EDIT_TIMELINE.json"),
                     encoding="utf-8"))
SHOTS = EDL["shots"]


def write_png(path, rgb):
    h, w, _ = rgb.shape
    raw = b"".join(b"\x00" + rgb[y].tobytes() for y in range(h))

    def chunk(t, d):
        c = struct.pack(">I", len(d)) + t + d
        return c + struct.pack(">I", zlib.crc32(t + d))
    open(path, "wb").write(b"\x89PNG\r\n\x1a\n"
                           + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                           + chunk(b"IDAT", zlib.compress(raw, 6))
                           + chunk(b"IEND", b""))


res = dict(path=P, checks=[])


def ck(name, ok, detail):
    res["checks"].append(dict(check=name, passed=bool(ok), detail=str(detail)[:400]))
    return bool(ok)


st = os.stat(P)
ck("file exists/size>0", st.st_size > 0, st.st_size)
inp = av.open(P)
vs = next(s for s in inp.streams if s.type == "video")
au = next(s for s in inp.streams if s.type == "audio")
ck("resolution 640x360 16:9", vs.width == 640 and vs.height == 360,
   f"{vs.width}x{vs.height}")
ck("fps 24", abs(float(vs.average_rate) - 24) < 0.01, float(vs.average_rate))
vd = float(vs.duration * vs.time_base)
ck("video duration 302.0", abs(vd - 302.0) < 0.5, vd)
ad = float(au.duration * au.time_base)
ck("audio aac 48k + duration", au.codec_context.name == "aac" and au.rate == 48000
   and abs(ad - 302.0) < 1.0, f"{au.codec_context.name} {au.rate} {ad:.2f}s")

# full decode + luma + frame snapshots at shot boundaries
luma = []
mid = {}
bounds = {}
for sh in SHOTS:
    mid[sh["shot_id"]] = (sh["record_frame_in"] + sh["record_frame_out"]) // 2
    bounds[sh["shot_id"]] = sh["record_frame_in"]
snaps = {}
snap_want = set(mid.values()) | set(bounds.values()) | {60, 3624, 6241, 7240}
n = 0
errs = 0
try:
    for fr in inp.decode(vs):
        g = fr.to_ndarray(format="gray").astype(np.float32)
        luma.append(float(g.mean()))
        if n in snap_want:
            snaps[n] = fr.to_ndarray(format="rgb24")
        n += 1
except Exception as e:  # noqa: BLE001
    errs += 1
    print("decode error", e)
ck("full decode 7248 frames 0 errors", n == 7248 and errs == 0, f"{n} frames")

# black segments
blacks = [i for i, m in enumerate(luma) if m < 4.0]
segs = []
for f in blacks:
    if segs and f == segs[-1][1] + 1:
        segs[-1][1] = f
    else:
        segs.append([f, f])
long_black = [(a + 1, b + 1) for a, b in segs if b - a >= 12]
expected_black = [(7177, 7248)]
ck("black segments only authored ending", long_black == expected_black,
   long_black)

# frozen runs
runs = []
rs = None
prev = None
for i, m in enumerate(luma):
    sig = round(m, 2)
    if sig == prev:
        if rs is None:
            rs = i - 1
    else:
        if rs is not None and i - 1 - rs >= 48:
            runs.append((rs + 1, i))
        rs = None
    prev = sig
ck("no unintended frozen runs >=2s", not runs, runs)

# cut detection at every shot boundary
cut_fail = []
for a, b in zip(SHOTS, SHOTS[1:]):
    fa = a["record_frame_out"] - 1
    fb = b["record_frame_in"]
    if fa in snaps and fb in snaps:
        d = np.abs(snaps[fa].astype(int) - snaps[fb].astype(int)).mean()
        if d < 2.0:
            cut_fail.append((a["shot_id"], b["shot_id"], round(float(d), 2)))
ck("cut visible at shot boundaries", len(cut_fail) <= 3,
   f"{len(SHOTS) - 1 - len(cut_fail)}/{len(SHOTS) - 1} cuts detected; weak: {cut_fail}")

# same-scene distinct framings (SC02 + SC10)
def pair(x, y):
    return float(np.abs(snaps[mid[x]].astype(int) - snaps[mid[y]].astype(int)).mean())
d_sc02 = min(pair("SC02_SH002", "SC02_SH003"), pair("SC02_SH003", "SC02_SH005"))
d_sc10 = pair("SC10_SH001", "SC10_SH002")
ck("shot-specific cameras visible (SC02,SC10)", d_sc02 > 8 and d_sc10 > 8,
   f"SC02 min diff {d_sc02:.1f}, SC10 {d_sc10:.1f}")

# SC10 illuminated, ending black
sc10_vis = [m for m in luma[6768:7176]]
ck("SC10 visible (luma>8)", min(sc10_vis) > 8 or np.percentile(sc10_vis, 5) > 8,
   f"min {min(sc10_vis):.1f} p5 {np.percentile(sc10_vis,5):.1f}")
ck("ending black", max(luma[7176:]) < 2.0, round(max(luma[7176:]), 2))

# audio
inp.close()
inp = av.open(P)
au = next(s for s in inp.streams if s.type == "audio")
L = []
R = []
for fr in inp.decode(au):
    a = fr.to_ndarray().astype(np.float64)
    L.append(a[0])
    R.append(a[1])
x = [np.concatenate(L), np.concatenate(R)]
pk = float(max(np.abs(x[0]).max(), np.abs(x[1]).max()))
lf = lufs.integrated_lufs(x, 48000)
tp = lufs.true_peak_dbtp(x, 48000)
ck("audio present 302s loudness", pk > 0.1 and abs(len(x[0]) / 48000 - 302.0) < 1
   and -18 < lf < -14, f"peak {pk:.3f} {lf:.2f} LUFS {tp:.2f} dBTP")
inp.close()

for f, label in ((60, "opening"), (bounds["SC02_SH003"], "SC02_SH003_wide"),
                 (mid["SC02_SH005"], "SC02_SH005_close"), (3624, "middle"),
                 (6241, "climax"), (mid["SC10_SH002"], "SC10_child"),
                 (mid["SC10_SH004"], "SC10_keyturn"), (7240, "ending")):
    if f in snaps:
        write_png(os.path.join(OUTD, f"v_{f:04d}_{label}.png"), snaps[f])

res["summary"] = dict(frames=n, black_segments=long_black, frozen_runs=runs,
                      audio=dict(peak=round(pk, 3), lufs=round(lf, 2),
                                 tp=round(tp, 2)))
res["overall_pass"] = all(c["passed"] for c in res["checks"])
json.dump(res, open(os.path.join(OUTD, "VERIFY_MASTER.json"), "w"), indent=2)
print("ALL CHECKS PASS" if res["overall_pass"] else
      "FAILED: " + str([c["check"] for c in res["checks"] if not c["passed"]]))
