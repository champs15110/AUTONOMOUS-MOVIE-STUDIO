#!/usr/bin/env python3
"""
render_chunks - Stage 14 FINAL RENDER driver (local fallback backend).

JANCTION Render is absent (ERR-0003); finals render on pypi bpy Cycles CPU at
an honest local spec: 320x180, 24 fps, 6 samples adaptive + OIDN denoise
(1080p/128spp measures ~49 days on this 2-core box - see RENDER_ESTIMATES).

Chunks = <=240-frame units inside scene ranges (JANCTION beta job limit).
Each chunk: render -> verify (mp4 parse: duration/dims/codec) -> save json.
Successful chunks are NEVER re-rendered; re-running the driver retries only
failed/missing chunks.

Run: LD_LIBRARY_PATH=/tmp/glstub python3 13_RENDER/scripts/render_chunks.py
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

CHUNKS_DIR = os.path.join(ROOT, "13_RENDER", "FINAL_CHUNKS")
os.makedirs(CHUNKS_DIR, exist_ok=True)
FPS = 24
JOB = 240
SCENE_FRAMES = {
    "SC01": (1, 768), "SC02": (769, 1560), "SC03": (1561, 2208),
    "SC04": (2209, 2928), "SC05": (2929, 3792), "SC06": (3793, 4464),
    "SC07": (4465, 5472), "SC08": (5473, 6288), "SC09": (6289, 6768),
    "SC10": (6769, 7248),
}
CHUNKS = []
for sid in sorted(SCENE_FRAMES):
    f0, f1 = SCENE_FRAMES[sid]
    i = 0
    while f0 + i * JOB <= f1:
        a = f0 + i * JOB
        b = min(f1, a + JOB - 1)
        CHUNKS.append(dict(scene=sid, f0=a, f1=b))
        i += 1


def probe_mp4(path):
    """Parse mvhd/tkhd by BOX offset (find() hits the type string = start+4)."""
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


def probe_ok(chunk, path):
    m = probe_mp4(path) if os.path.exists(path) else None
    want = (chunk["f1"] - chunk["f0"] + 1) / FPS
    good = bool(m) and abs(m["seconds"] - want) < 0.15 and m["width"] == 320 \
        and m["height"] == 180 and m["avc1"]
    return (good, m)


def verified(chunk, path):
    good, _ = probe_ok(chunk, path)
    return good


def write_status(n, ch, mp4, ok, m=None, err="", t=None):
    st = dict(chunk=n, scene=ch["scene"], frames=[ch["f0"], ch["f1"]],
              verified=ok, error=err)
    if m:
        st.update(seconds=m["seconds"], size=m["size"])
    if t is not None:
        st["render_seconds"] = t
    json.dump(st, open(mp4.replace(".mp4", ".json"), "w"), indent=2)


ok = fail = 0
for n, ch in enumerate(CHUNKS):
    mp4 = os.path.join(CHUNKS_DIR, f"chunk_{n:02d}.mp4")
    good, m = probe_ok(ch, mp4)
    if good:
        # already rendered successfully - refresh status json, never re-render
        write_status(n, ch, mp4, True, m)
        ok += 1
        print(f"chunk {n:02d} {ch['scene']} {ch['f0']}-{ch['f1']} VERIFIED-EXISTS",
              flush=True)
        continue
    t0 = time.time()
    try:
        if bpy.data.objects:
            bpy.ops.wm.read_factory_settings(use_empty=True)
        rep = PR.REPRESENTATIVE[ch["scene"]]
        PR.build(ch["scene"], rep)
        sc = bpy.context.scene
        sc.render.engine = "CYCLES"
        sc.cycles.device = "CPU"
        sc.cycles.samples = 6
        sc.cycles.use_adaptive_sampling = True
        sc.cycles.adaptive_threshold = 0.1
        sc.cycles.use_denoising = True
        sc.cycles.max_bounces = 2
        sc.cycles.volume_bounces = 0
        sc.cycles.volume_step_rate = 2.0
        sc.render.resolution_x, sc.render.resolution_y = 320, 180
        sc.render.fps = FPS
        sc.frame_start, sc.frame_end = ch["f0"], ch["f1"]
        sc.render.image_settings.file_format = "FFMPEG"
        sc.render.ffmpeg.format = "MPEG4"
        sc.render.ffmpeg.codec = "H264"
        sc.render.ffmpeg.constant_rate_factor = "LOW"
        sc.render.ffmpeg.ffmpeg_preset = "GOOD"
        sc.render.ffmpeg.audio_codec = "NONE"
        sc.render.filepath = os.path.join(CHUNKS_DIR, f"chunk_{n:02d}_")
        bpy.ops.render.render(animation=True)
        produced = os.path.join(CHUNKS_DIR,
                                f"chunk_{n:02d}_{ch['f0']:04d}-{ch['f1']:04d}.mp4")
        if os.path.exists(produced):
            os.replace(produced, mp4)
        good, m = probe_ok(ch, mp4)
        assert good, f"probe failed: {m} want_secs={(ch['f1']-ch['f0']+1)/FPS}"
        write_status(n, ch, mp4, True, m,
                     t=round(time.time() - t0, 1))
        ok += 1
        print(f"chunk {n:02d} {ch['scene']} {ch['f0']}-{ch['f1']} OK "
              f"{time.time()-t0:.0f}s", flush=True)
    except Exception as e:  # noqa: BLE001
        fail += 1
        write_status(n, ch, mp4, False, err=f"{type(e).__name__}: {e}"[-200:])
        print(f"chunk {n:02d} {ch['scene']} FAIL {type(e).__name__}: {e}",
              flush=True)
print(f"CHUNKS DONE ok={ok} fail={fail} total={len(CHUNKS)}", flush=True)
