#!/usr/bin/env python3
"""
assemble_final - Stage 14: assemble verified FINAL_CHUNKS into
FINAL/FINAL_FILM.mp4 with the authored audio mix (Blender VSE, H.264 + AAC).

Video: one movie strip per verified chunk at its exact record range.
Audio: the measured FINAL mix (10_AUDIO/mix/FINAL_MIX.wav, -16.34 LUFS /
-1.50 dBTP) as a single strip. NOTE: headless bpy FFMPEG renders write a
silent AAC track (ERR-0007), so run 13_RENDER/scripts/mux_audio.py after
this to transcode the video once and encode the real AAC from FINAL_MIX.wav.

Run: LD_LIBRARY_PATH=/tmp/glstub python3 13_RENDER/scripts/assemble_final.py
     python3 13_RENDER/scripts/mux_audio.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
import bpy  # noqa: E402

CH = os.path.join(ROOT, "13_RENDER", "FINAL_CHUNKS")
FINAL = os.path.join(ROOT, "FINAL")
os.makedirs(FINAL, exist_ok=True)
chunks = []
for n in range(34):
    p = os.path.join(CH, f"chunk_{n:02d}.json")
    c = json.load(open(p)) if os.path.exists(p) else {}
    assert c.get("verified"), f"chunk {n} not verified - refusing to assemble"
    chunks.append((n, c))
print(f"assembling {len(chunks)} verified chunks", flush=True)

sc = bpy.context.scene
sc.render.fps = 24
sc.frame_start = 1
sc.frame_end = 7248
sc.render.resolution_x, sc.render.resolution_y = 320, 180
se = sc.sequence_editor_create()
for n, c in chunks:
    st = se.sequences.new_movie(name=f"chunk_{n:02d}",
                                filepath=os.path.join(CH, f"chunk_{n:02d}.mp4"),
                                channel=1, frame_start=c["frames"][0])
    st.frame_final_duration = c["frames"][1] - c["frames"][0] + 1

# audio = the measured FINAL mix WAV (identical pipeline to measure_mix.py,
# applied_trim_db baked in, re-verified at -16.34 LUFS / -1.50 dBTP)
st = se.sequences.new_sound(name="final_mix",
                            filepath=os.path.join(ROOT, "10_AUDIO", "mix",
                                                  "FINAL_MIX.wav"),
                            channel=2, frame_start=1)
st.frame_final_duration = 7248
st.volume = 1.0
print("final mix strip placed", flush=True)

sc.render.image_settings.file_format = "FFMPEG"
sc.render.ffmpeg.format = "MPEG4"
sc.render.ffmpeg.codec = "H264"
sc.render.ffmpeg.constant_rate_factor = "MEDIUM"
sc.render.ffmpeg.audio_codec = "AAC"
sc.render.ffmpeg.audio_bitrate = 128
sc.render.filepath = os.path.join(FINAL, "FINAL_FILM_")
bpy.ops.render.render(animation=True)
out = os.path.join(FINAL, "FINAL_FILM.mp4")
for cand in (os.path.join(FINAL, "FINAL_FILM_0001-7248.mp4"),
             os.path.join(FINAL, "FINAL_FILM_.mp4")):
    if os.path.exists(cand):
        os.replace(cand, out)
        break
print("ASSEMBLY DONE ->", out, os.path.getsize(out), "bytes", flush=True)
