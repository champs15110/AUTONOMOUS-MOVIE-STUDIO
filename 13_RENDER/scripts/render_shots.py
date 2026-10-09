#!/usr/bin/env python3
"""
render_shots - shot-accurate final render driver (supersedes render_chunks.py).

Root-cause fix (ERR-0009): render_chunks.py built ONE representative camera
per scene, so the 58-shot edit structure never appeared in the film. This
driver iterates the EDIT_TIMELINE shot records and, for every shot, builds
the scene with THAT shot's camera, subject performance, lighting and VFX
(preview_render.build) and renders exactly that shot's record frame range.

Spec: 640x360 (16:9), 24 fps, Cycles CPU 2spp adaptive(0.1) + OIDN,
max_bounces 2, volume_bounces 0, volume_step_rate 2 (calibrated ~2.6-3.3
s/frame on this 2-core box; 1080p measures ~52 h = infeasible, ERR-0003).

Recoverable: one mp4 + status json per shot in 13_RENDER/SHOT_RENDERS/.
Verified shots are NEVER re-rendered; re-running retries failures only.
SC10_SH005 (authored cut-to-black) is not rendered - assembly emits black.

Run: LD_LIBRARY_PATH=/tmp/glstub python3 13_RENDER/scripts/render_shots.py
"""
import json
import os
import struct
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in ("06_ASSETS/scripts", "06_ASSETS/materials", "07_ANIMATION/scripts",
          "08_CAMERA/scripts", "09_LIGHTING_VFX/scripts", "11_RENDER/scripts"):
    sys.path.insert(0, os.path.join(ROOT, p))
import bpy  # noqa: E402
import preview_render as PR  # noqa: E402

OUT = os.path.join(ROOT, "13_RENDER", "SHOT_RENDERS")
os.makedirs(OUT, exist_ok=True)
EDL = json.load(open(os.path.join(ROOT, "11_EDIT", "EDIT_TIMELINE.json"),
                     encoding="utf-8"))
SHOTS = EDL["shots"]
FPS = 24
AUTHORED_BLACK = {"SC10_SH005"}  # hard cut to black - never rendered


def probe_mp4(path):
    d = open(path, "rb").read()
    if len(d) < 1000 or d[4:8] != b"ftyp":
        return None
    mo = d.find(b"moov")
    i = d.find(b"mvhd", mo)
    if i < 0:
        return None
    ts, dur = struct.unpack(">II", d[i + 16:i + 24])
    t = d.find(b"tkhd", mo)
    if t < 0 or not ts:
        return None
    w, h = struct.unpack(">II", d[t + 80:t + 88])
    return dict(seconds=round(dur / ts, 3), width=w >> 16, height=h >> 16,
                avc1=d.find(b"avc1") > 0, size=len(d))


def probe_ok(sh, path):
    m = probe_mp4(path) if os.path.exists(path) else None
    want = (sh["record_frame_out"] - sh["record_frame_in"] + 1) / FPS
    good = bool(m) and abs(m["seconds"] - want) < 0.15 and m["width"] == 640 \
        and m["height"] == 360 and m["avc1"]
    return good, m


ok = fail = skipped = 0
for sh in SHOTS:
    sid = sh["shot_id"]
    f0, f1 = sh["record_frame_in"], sh["record_frame_out"]
    mp4 = os.path.join(OUT, f"{sid}.mp4")
    if sid in AUTHORED_BLACK:
        skipped += 1
        continue
    good, m = probe_ok(sh, mp4)
    if good:
        json.dump(dict(shot_id=sid, frames=[f0, f1], verified=True,
                       seconds=m["seconds"], size=m["size"]),
                  open(mp4.replace(".mp4", ".json"), "w"), indent=2)
        ok += 1
        print(f"{sid} VERIFIED-EXISTS", flush=True)
        continue
    t0 = time.time()
    try:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        PR.build(sh["scene_id"], sid)
        sc = bpy.context.scene
        sc.render.engine = "CYCLES"
        sc.cycles.device = "CPU"
        sc.cycles.samples = 2
        sc.cycles.use_adaptive_sampling = True
        sc.cycles.adaptive_threshold = 0.1
        sc.cycles.use_denoising = True
        sc.cycles.max_bounces = 2
        sc.cycles.volume_bounces = 0
        sc.cycles.volume_step_rate = 2.0
        sc.render.resolution_x, sc.render.resolution_y = 640, 360
        sc.render.fps = FPS
        sc.frame_start, sc.frame_end = f0, f1
        sc.render.image_settings.file_format = "FFMPEG"
        sc.render.ffmpeg.format = "MPEG4"
        sc.render.ffmpeg.codec = "H264"
        sc.render.ffmpeg.constant_rate_factor = "LOW"
        sc.render.ffmpeg.ffmpeg_preset = "GOOD"
        sc.render.ffmpeg.audio_codec = "NONE"
        sc.render.filepath = os.path.join(OUT, f"{sid}_")
        bpy.ops.render.render(animation=True)
        produced = os.path.join(OUT, f"{sid}_{f0:04d}-{f1:04d}.mp4")
        if os.path.exists(produced):
            os.replace(produced, mp4)
        good, m = probe_ok(sh, mp4)
        assert good, f"probe failed: {m}"
        json.dump(dict(shot_id=sid, frames=[f0, f1], verified=True,
                       seconds=m["seconds"], size=m["size"],
                       render_seconds=round(time.time() - t0, 1)),
                  open(mp4.replace(".mp4", ".json"), "w"), indent=2)
        ok += 1
        print(f"{sid} OK {time.time()-t0:.0f}s", flush=True)
    except Exception as e:  # noqa: BLE001
        fail += 1
        json.dump(dict(shot_id=sid, frames=[f0, f1], verified=False,
                       error=f"{type(e).__name__}: {e}"[-300:]),
                  open(mp4.replace(".mp4", ".json"), "w"), indent=2)
        print(f"{sid} FAIL {type(e).__name__}: {e}", flush=True)
print(f"SHOTS DONE ok={ok} fail={fail} black_skipped={skipped} "
      f"total={len(SHOTS)}", flush=True)
