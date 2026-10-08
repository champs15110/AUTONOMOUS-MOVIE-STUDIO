#!/usr/bin/env python3
"""
assemble_preview - Stage 12 low-resolution ASSEMBLED PREVIEW (animatic).

Real editing tool: Blender's Video Sequence Editor via the pypi `bpy` module
(same honest CPU path as Stage 11; built-in FFMPEG muxer, no external ffmpeg).

One image strip per shot (that scene's approved preview still, held for the
shot's exact authored duration) + every authored audio event as a sound strip
at its absolute frame, 320x180 @ 24 fps, H.264/AAC.

NOT FINAL: picture stands in for unrendered T12 finals; audio carries unity
fades approximated by strip fades; the final cut + mix come later.

Run: LD_LIBRARY_PATH=/tmp/glstub python3 11_EDIT/scripts/assemble_preview.py
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
import bpy  # noqa: E402

EDL = json.load(open(os.path.join(ROOT, "11_EDIT", "EDIT_TIMELINE.json"),
                     encoding="utf-8"))
AT = json.load(open(os.path.join(ROOT, "10_AUDIO", "AUDIO_TIMELINE.json"),
                    encoding="utf-8"))
ASSET_DIR = os.path.join(ROOT, "10_AUDIO", "assets")
PREV = os.path.join(ROOT, "11_RENDER", "PREVIEWS")
OUT = os.path.join(ROOT, "11_EDIT", "ASSEMBLY_PREVIEW_LOWRES")

sc = bpy.context.scene
sc.render.fps = EDL["fps"]
sc.frame_start = 1
sc.frame_end = EDL["total_frames"]
# low-res animatic: quarter-HD, native to the preview stills (no rescale)
sc.render.resolution_x = 480
sc.render.resolution_y = 270
sc.render.resolution_percentage = 100

se = sc.sequence_editor_create()

t0 = time.time()
# picture: one strip per shot, exact authored duration
for sh in EDL["shots"]:
    png = os.path.join(PREV, f"{sh['scene_id']}_preview.png")
    st = se.sequences.new_image(name=sh["shot_id"], filepath=png, channel=1,
                                frame_start=sh["record_frame_in"])
    st.frame_final_duration = sh["frames"]

# audio: every event on its own channel at absolute frames
ch = 2
n_aud = 0
for tr in ("ambience", "music", "sfx"):
    for ev in AT["tracks"][tr]:
        path = os.path.join(ASSET_DIR, tr, ev["asset"] + ".wav")
        if not os.path.exists(path):
            print("MISSING", path)
            continue
        st = se.sequences.new_sound(name=f"{tr}_{ev['asset']}_{ev['frame_in']}",
                                    filepath=path, channel=ch,
                                    frame_start=ev["frame_in"])
        st.frame_final_duration = ev["frame_out"] - ev["frame_in"] + 1
        try:
            st.volume = ev["gain"]
        except Exception:  # noqa: BLE001
            pass
        try:
            if ev.get("fade_in"):
                st.use_fade_in = True
                st.fade_in = ev["fade_in"]
            if ev.get("fade_out"):
                st.use_fade_out = True
                st.fade_out = ev["fade_out"]
        except Exception:  # noqa: BLE001
            pass
        ch += 1
        n_aud += 1

sc.render.image_settings.file_format = "FFMPEG"
sc.render.ffmpeg.format = "MPEG4"
sc.render.ffmpeg.codec = "H264"
sc.render.ffmpeg.constant_rate_factor = "LOW"
sc.render.ffmpeg.audio_codec = "AAC"
sc.render.ffmpeg.gopsize = 12
sc.render.filepath = OUT
print(f"VSE ready: {len(EDL['shots'])} picture strips, {n_aud} audio strips, "
      f"{sc.frame_end} frames @ {sc.render.fps} fps; rendering...")
bpy.ops.render.render(animation=True)
print("RENDER DONE in %.1fs" % (time.time() - t0))
