#!/usr/bin/env python3
"""
repair_sc10 - Step 17 targeted SC10 lighting repair (ERR-0008).

Renders ONLY SC10's visible story shots (SC10_SH001-SH004, frames
6769-7176) with their authored per-shot cameras and the repaired lighting
(light_design.py CP-0017). The authored cut-to-black (7177-7248) is NOT
rendered here - assembly emits black for that range.

Modes:
  preview  - 160x90 / 4spp stills at 6800/6930/7040/7150 for inspection
  render   - 320x180 / 6spp+OIDN H.264 segments per shot into
             13_RENDER/REPAIR_CHUNKS/

Run: LD_LIBRARY_PATH=/tmp/glstub python3 13_RENDER/scripts/repair_sc10.py preview|render
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in ("06_ASSETS/scripts", "06_ASSETS/materials", "07_ANIMATION/scripts",
          "08_CAMERA/scripts", "09_LIGHTING_VFX/scripts", "11_RENDER/scripts"):
    sys.path.insert(0, os.path.join(ROOT, p))
import bpy  # noqa: E402
import preview_render as PR  # noqa: E402

SHOTS = {"SC10_SH001": (6769, 6876), "SC10_SH002": (6877, 6984),
         "SC10_SH003": (6985, 7092), "SC10_SH004": (7093, 7176)}
PREVIEW_AT = {"SC10_SH001": 6800, "SC10_SH002": 6930, "SC10_SH003": 7040,
              "SC10_SH004": 7150}
OUT = os.path.join(ROOT, "13_RENDER", "REPAIR_CHUNKS")
os.makedirs(OUT, exist_ok=True)


def setup_common(sc, preview):
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 4 if preview else 6
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.1
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 2
    sc.cycles.volume_bounces = 0
    sc.cycles.volume_step_rate = 2.0
    sc.render.resolution_x, sc.render.resolution_y = \
        (160, 90) if preview else (320, 180)
    sc.render.fps = 24


def main(mode):
    for shot, (f0, f1) in SHOTS.items():
        bpy.ops.wm.read_factory_settings(use_empty=True)
        PR.build("SC10", shot)
        sc = bpy.context.scene
        sc.frame_start, sc.frame_end = f0, f1
        setup_common(sc, mode == "preview")
        if mode == "preview":
            sc.render.image_settings.file_format = "PNG"
            sc.frame_set(PREVIEW_AT[shot])
            sc.render.filepath = os.path.join(
                OUT, f"preview_{shot}_{PREVIEW_AT[shot]}.png")
            bpy.ops.render.render(write_still=True)
            print(f"preview {shot} f{PREVIEW_AT[shot]} done", flush=True)
        else:
            sc.render.image_settings.file_format = "FFMPEG"
            sc.render.ffmpeg.format = "MPEG4"
            sc.render.ffmpeg.codec = "H264"
            sc.render.ffmpeg.constant_rate_factor = "LOW"
            sc.render.ffmpeg.ffmpeg_preset = "GOOD"
            sc.render.ffmpeg.audio_codec = "NONE"
            sc.render.filepath = os.path.join(OUT, f"{shot}_")
            bpy.ops.render.render(animation=True)
            produced = os.path.join(OUT, f"{shot}_{f0:04d}-{f1:04d}.mp4")
            target = os.path.join(OUT, f"{shot}.mp4")
            if os.path.exists(produced):
                os.replace(produced, target)
            print(f"rendered {shot} {f0}-{f1} -> {os.path.getsize(target)}B",
                  flush=True)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "preview")
