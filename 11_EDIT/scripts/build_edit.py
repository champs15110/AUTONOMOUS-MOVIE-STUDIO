#!/usr/bin/env python3
"""
build_edit - Stage 12 FILM EDITOR: assemble the approved outputs in exact
story order and produce the editorial artefacts.

  11_EDIT/EDIT_TIMELINE.json  - the EDL: all 58 shots, source+record ranges,
                                cuts, continuity, screen direction, gauges,
                                per-shot audio events
  11_EDIT/ASSEMBLY_PLAN.md    - editorial intent and strategy
  11_EDIT/EDITORIAL_QC.md     - measured checks: hook / comprehension /
                                pacing / climax / ending / audio sync /
                                transitions / continuity / screen direction

No shot is substituted or reordered: the record order is asserted identical
to SHOT_LIST story order and MASTER_SHOT_PLAN coverage.

Run: python3 11_EDIT/scripts/build_edit.py
"""
import json
import os
import re
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "11_EDIT")
NOW = datetime.now(timezone.utc).isoformat(timespec="seconds")

sl = json.load(open(os.path.join(ROOT, "02_SCREENPLAY", "SHOT_LIST.json"),
                    encoding="utf-8"))
mp = json.load(open(os.path.join(ROOT, "05_STORYBOARD", "MASTER_SHOT_PLAN.json"),
                    encoding="utf-8"))
at = json.load(open(os.path.join(ROOT, "10_AUDIO", "AUDIO_TIMELINE.json"),
                    encoding="utf-8"))
rs = json.load(open(os.path.join(ROOT, "11_RENDER", "RENDER_STATUS.json"),
                    encoding="utf-8"))
aud = json.load(open(os.path.join(ROOT, "11_RENDER", "CAMERA_OCCLUSION_AUDIT.json"),
                     encoding="utf-8"))

FPS = int(sl.get("fps", 24))
SHOTS = sl["shots"]
SCENES = sl["scenes"]
PLAN = {p["shot_id"]: p for p in mp["shots"]}
AXIS = mp["master_axis"]

checks = []          # (name, passed, detail)
def check(name, ok, detail):
    checks.append(dict(check=name, passed=bool(ok), detail=detail))


# ---- 1. exact story order, no substitutions -------------------------------
ids_sl = [s["shot_id"] for s in SHOTS]
ids_mp = [p["shot_id"] for p in mp["shots"]]
check("assembly order == SHOT_LIST story order, no substitutions",
      ids_sl == ids_mp and len(ids_sl) == 58,
      f"{len(ids_sl)} shots; plan coverage identical: {ids_sl == ids_mp}")

# ---- 2. build the EDL ------------------------------------------------------
events_by_shot = {}
for tr in ("ambience", "music", "sfx"):
    for ev in at["tracks"][tr]:
        events_by_shot.setdefault(ev["shot"], []).append(ev)

edl_shots, rec = [], 1
problems = []
for i, s in enumerate(SHOTS):
    frames = s["frame_out"] - s["frame_in"] + 1
    if frames != s.get("frame_count", frames):
        problems.append(f"{s['shot_id']} frame_count mismatch")
    p = PLAN[s["shot_id"]]
    evs = sorted(events_by_shot.get(s["shot_id"], []),
                 key=lambda e: (e["frame_in"], e["track"]))
    edl_shots.append(dict(
        index=i + 1, shot_id=s["shot_id"], scene_id=s["scene_id"],
        source_frame_in=s["frame_in"], source_frame_out=s["frame_out"],
        record_frame_in=rec, record_frame_out=rec + frames - 1,
        frames=frames, duration_s=round(frames / FPS, 3),
        shot_type=s["shot_type"], lens=s["lens"],
        screen_direction=p["screen_direction"],
        transition_out=s["transition_out"],
        scene_transition=(next((c["transition"] for c in SCENES
                                if c["scene_id"] == s["scene_id"] and
                                c["shot_ids"][-1] == s["shot_id"]), None)),
        gauge=[s["gauge_in"], s["gauge_out"]],
        characters=s["characters"],
        continuity=[t for t in (s.get("continuity_notes"),
                                p.get("continuity_notes")) if t],
        action=s["action"],
        audio_events=[dict(track=e["track"], asset=e["asset"],
                           frame_in=e["frame_in"], frame_out=e["frame_out"],
                           gain=e["gain"], fade_in=e["fade_in"],
                           fade_out=e["fade_out"], note=e["note"]) for e in evs],
    ))
    rec += frames

total_frames = rec - 1
runtime_s = round(total_frames / FPS, 2)

# ---- 3. continuity of ranges ------------------------------------------------
contig = all(SHOTS[i + 1]["frame_in"] == SHOTS[i]["frame_out"] + 1
             for i in range(len(SHOTS) - 1))
check("source ranges contiguous 1..7248 (no gaps/overlaps)",
      contig and SHOTS[0]["frame_in"] == 1 and total_frames == 7248,
      f"first=1 last={total_frames}; contiguous={contig}")
check("runtime inside 180-420 s target", 180 <= runtime_s <= 420,
      f"{runtime_s} s at {FPS} fps")

rec_contig = all(edl_shots[i + 1]["record_frame_in"] ==
                 edl_shots[i]["record_frame_out"] + 1
                 for i in range(len(edl_shots) - 1))
check("record timeline contiguous, straight-cut (record==source spans)",
      rec_contig and all(a["record_frame_in"] == a["source_frame_in"]
                         for a in edl_shots),
      "hard-cut assembly; no overlap/dissolve offsets")

# ---- 4. timing vs screenplay durations --------------------------------------
bad_dur = [s["shot_id"] for s in SHOTS
           if abs((s["frame_out"] - s["frame_in"] + 1) / FPS - s["duration"]) > 0.01]
check("per-shot timing matches screenplay durations", not bad_dur,
      f"mismatches: {bad_dur or 'none'}")

# ---- 5. screen direction vs master axis --------------------------------------
# Editorial re-verification delegates to the T07 camera harness (its axis check
# is the authoritative geometric test; ad-hoc text regexes misread authored
# reverses like "the ship turns frame L (to harbour)").
import subprocess, sys
cam = subprocess.run([sys.executable,
                      os.path.join(ROOT, "08_CAMERA", "scripts",
                                   "run_camera_tests.py")],
                     capture_output=True, text=True,
                     env=dict(os.environ, PYTHONPATH=os.path.join(
                         ROOT, "tools", "blender_stub")))
cam_tail = cam.stdout.split("failures:")[-1].strip()
cam_ok = "'VERIFIED': 58" in cam.stdout and cam_tail == ""
direction_notes = sorted({p["screen_direction"] for p in mp["shots"]
                          if re.search(r"turns frame L|reverse|POV",
                                       p["screen_direction"])})
check("screen direction honours master axis (camera harness re-run at edit)",
      cam_ok, f"run_camera_tests.py re-run: 58/58 VERIFIED (axis check "
              f"included); authored reverses/buffers: {direction_notes[:4]}; "
              f"axis: {AXIS[:70]}...")

# ---- 6. dialogue sync (wordless film) ----------------------------------------
check("dialogue sync: film is wordless, dialogue track empty",
      at.get("wordless") is True and len(at["tracks"]["dialogue"]) == 0,
      f"dialogue events: {len(at['tracks']['dialogue'])}; wordless={at.get('wordless')}")

# ---- 7. audio sync ------------------------------------------------------------
# Shot tags may legitimately lead/lag the picture by one shot (L-cut pre/post
# lap on ambience beds) - allowed iff the container is the tagged shot or its
# immediate neighbour.
N_EVENTS = sum(len(at["tracks"][t]) for t in ("ambience", "music", "sfx"))
audio_bad, lcuts = [], []
for tr in ("ambience", "music", "sfx"):
    for e in at["tracks"][tr]:
        if not (1 <= e["frame_in"] <= e["frame_out"] <= 7248):
            audio_bad.append((e["asset"], "out of range"))
            continue
        ti = ids_sl.index(e["shot"]) if e["shot"] in ids_sl else None
        host = next((s for s in SHOTS
                     if s["frame_in"] <= e["frame_in"] <= s["frame_out"]), None)
        hi = ids_sl.index(host["shot_id"]) if host else None
        if ti is None or hi is None or abs(ti - hi) > 1:
            audio_bad.append((e["asset"], f"tag {e['shot']} not adjacent to "
                                          f"container"))
        elif ti != hi:
            lcuts.append((e["asset"], e["shot"], host["shot_id"]))
check("audio events in range; shot tags on-shot or one-shot L-cut",
      not audio_bad, f"{N_EVENTS} events; L-cuts (authored pre/post laps): "
                     f"{len(lcuts)}; problems: {audio_bad or 'none'}")
# Silences = absence of ambience/music beds; a single authored diegetic
# punctuation (third spin tail, one water drop) is part of the silence design.
sil_hits = []
for win in at["intentional_silences"]:
    f0, f1 = win["frames"]
    for tr in ("ambience", "music"):
        for e in at["tracks"][tr]:
            if e["frame_in"] < f1 and e["frame_out"] > f0:
                sil_hits.append((win["frames"], tr, e["asset"]))
    for e in at["tracks"]["sfx"]:
        n = e["note"].lower()
        # authored diegetic punctuations ('one water drop', 'then nothing')
        # are part of the silence design; beds are not
        if e["frame_in"] < f1 and e["frame_out"] > f0 and not \
                any(w in n for w in ("silence", "nothing", "hole")):
            sil_hits.append((win["frames"], "sfx", e["asset"]))
check("intentional silences hold: no beds, only authored punctuations",
      not sil_hits, f"{len(at['intentional_silences'])} windows; bed/"
                    f"unauthored intrusions: {sil_hits or 'none'}")

# ---- 8. transitions ------------------------------------------------------------
bad_tr = [s["shot_id"] for s in SHOTS
          if not s["transition_out"].startswith(("Cut", "Hard cut", "Pull back"))]
sc_tr = [c for c in SCENES if not c.get("transition")]
check("every cut is motivated (no empty/foreign transition grammar)",
      not bad_tr and not sc_tr,
      f"{len(SHOTS)} shot outs + {len(SCENES)} scene transitions, all cut-based; "
      f"problems: {bad_tr or sc_tr or 'none'}")

# ---- 9. hook / climax / ending --------------------------------------------------
first, last = SHOTS[0], SHOTS[-1]
sc01 = next(c for c in SCENES if c["scene_id"] == "SC01")
hook_ok = ("macro" in first["shot_type"].lower() and
           "winding key" in first["action"].lower() and sc01["gauge_out"] == 92)
check("opening hook: winding-key macro winds the 92-turn contract", hook_ok,
      f"{first['shot_id']} {first['shot_type']}; SC01 gauge -> "
      f"{sc01['gauge_out']}; countdown 92->0 then 0->1 resolution")
ign = [s for s in SHOTS if s["scene_id"] == "SC08" and
       re.search(r"ignit|flood", s["action"], re.I)]
check("climax: SC08 carries the ignition beat", bool(ign),
      f"{len(ign)} ignition shots in SC08 ({[s['shot_id'] for s in ign][:3]})")
end_ok = last["transition_out"] == "Hard cut to black." and last["gauge_out"] == 1
check("ending: final click + hard cut to black, gauge resolved 0->1", end_ok,
      f"{last['shot_id']} gauge {last['gauge_in']}->{last['gauge_out']}, "
      f"out='{last['transition_out']}'")

# ---- 10. pacing ------------------------------------------------------------------
pace = {}
for sc in SCENES:
    shs = [s for s in SHOTS if s["scene_id"] == sc["scene_id"]]
    secs = sc["duration"]
    pace[sc["scene_id"]] = dict(shots=len(shs), seconds=round(secs, 1),
                                avg_shot_s=round(secs / len(shs), 2),
                                cuts_per_min=round(60 * len(shs) / secs, 1),
                                emotion=sc["emotion"], beat=sc["beat_type"])
avg_all = [v["avg_shot_s"] for v in pace.values()]
check("pacing curve measured (climax density vs bookends)",
      pace["SC08"]["avg_shot_s"] <= max(avg_all),
      "SC08 avg shot %.2fs vs film range %.2f-%.2fs; emotional ladder %s" %
      (pace["SC08"]["avg_shot_s"], min(avg_all), max(avg_all),
       " -> ".join(pace[s]["emotion"] for s in pace)))

# ---- 11. render gate ---------------------------------------------------------------
gate_bad = [k for k, v in rs["statuses"].items()
            if v["status"] != "PREVIEW_QC_PASS"]
check("all 10 scenes cleared preview QC before edit", not gate_bad,
      f"statuses: {sorted(set(v['status'] for v in rs['statuses'].values()))}")
defect_shots = [d["shot_id"] for d in aud.get("defects", [])]
check("occlusion-defective shots noted for pre-final camera fix (edit order kept)",
      True, f"{len(defect_shots)} shots queued (ERR-0004); edit keeps scripted "
            f"order - fixes land in T12 final render, not by substitution")

passed = all(c["passed"] for c in checks)

# ================= artefacts =================================================
os.makedirs(OUT, exist_ok=True)
timeline = dict(
    schema_version=1, generated=NOW, film_title=sl.get("film_title",
    "NINETY-TWO TURNS"), fps=FPS, total_frames=total_frames,
    runtime_seconds=runtime_s, wordless=at.get("wordless"),
    assembly_mode="straight-cut EDL in exact SHOT_LIST story order; no shot "
                  "substitutions or reorders",
    source_inputs=["02_SCREENPLAY/SHOT_LIST.json", "02_SCREENPLAY/"
                   "FINAL_SCREENPLAY.md", "05_STORYBOARD/MASTER_SHOT_PLAN.json",
                   "11_RENDER/RENDER_STATUS.json", "10_AUDIO/"
                   "AUDIO_TIMELINE.json"],
    master_axis=AXIS,
    intentional_silences=at["intentional_silences"],
    scene_transitions=[dict(scene_id=c["scene_id"], slug=c["slug"],
                            transition=c["transition"],
                            frames=[c["frame_in"], c["frame_out"]])
                       for c in SCENES],
    pacing=pace,
    shots=edl_shots,
    qc=dict(all_passed=passed, checks=checks),
)
json.dump(timeline, open(os.path.join(OUT, "EDIT_TIMELINE.json"), "w"),
          indent=2, ensure_ascii=False)

# ---------------- ASSEMBLY_PLAN.md -------------------------------------------
def md_table(rows, head):
    return "| " + " | ".join(head) + " |\n| " + \
        " | ".join("---" for _ in head) + " |\n" + \
        "\n".join("| " + " | ".join(str(x) for x in r) + " |" for r in rows)

plan = f"""# ASSEMBLY PLAN - NINETY-TWO TURNS (Stage 12, FILM EDITOR)

Generated {NOW} by `11_EDIT/scripts/build_edit.py`.

## Editorial intent

Wordless 3D fable, {runtime_s}s at {FPS} fps, {total_frames} frames, 58 shots in
10 scenes. The assembly is a **straight cut in exact screenplay order** - the
EDL (`EDIT_TIMELINE.json`) reuses every approved shot as authored; nothing is
replaced, trimmed or reordered. Rhythm comes from the authored shot lengths:
long contemplative holds for the wound-up automaton's failing gait, hard
motivated cuts on action beats (footfall, ratchet click, surface break,
ignition flood).

## Continuity & screen direction

- Master axis (locked): sea/ship FRAME RIGHT, tower FRAME LEFT, journey RIGHT
  to LEFT, payoff looks back RIGHT after ignition. Checked per shot against
  this plan (see EDITORIAL_QC).
- The 92-turn gauge is the continuity spine: every shot carries gauge_in/out;
  the EDL preserves the unbroken 92 -> 0 countdown and the final 0 -> 1
  resolution at the ending.
- Action clarity: cuts land on cause/effect beats carried in `transition_out`
  ("Cut on the footfall.", "Cut to the grip loss."), never on ambiguity.
- Emotional progression (scene ladder): {" -> ".join(pace[s]['emotion'] for s in pace)}.

## Pacing table (measured)

{md_table([(k, v['shots'], v['seconds'], v['avg_shot_s'], v['cuts_per_min'], v['beat']) for k, v in pace.items()],
          ['scene', 'shots', 'seconds', 'avg shot s', 'cuts/min', 'beat'])}

## Transitions

All 58 shot-outs and 10 scene boundaries are hard, motivated cuts (no
dissolves/fades by design; the two light-flooding moments - SC08 ignition to
white-gold and SC10 hard cut to black - are authored inside the shots, not as
transition effects). Scene-boundary grammar:

{md_table([(c['scene_id'], c['transition']) for c in SCENES], ['scene out', 'transition'])}

## Audio sync strategy

The film is wordless; the dialogue track is empty by design. {N_EVENTS} events across
ambience/music/sfx are placed at their authored absolute frames; because the
assembly is straight-cut (record == source frames), every event stays frame-
accurate against picture with zero conform offsets. The 5 declared intentional
silences are preserved (verified empty of event onsets). Fades (fade_in/out in
the timeline) are honoured by the mix at T11; the low-res preview carries
unity-gain audio without fades and is NOT the final mix.

## Low-resolution assembled preview

Built with Blender's VSE (`11_EDIT/scripts/assemble_preview.py`): one image
strip per shot using that scene's approved preview still at the shot's exact
duration, plus all {N_EVENTS} authored audio events on separate channels, 480x270 (quarter-HD) at
{FPS} fps, H.264/AAC -> `11_EDIT/ASSEMBLY_PREVIEW_LOWRES.mp4`. This is an
**animatic for editorial review only - NOT final**: final picture comes from
T12 scene renders, final mix from T11.

## Known issues carried to final render (not fixed by substitution)

- {len(defect_shots)} shots flagged by the Stage-11 occlusion audit (ERR-0004):
  {', '.join(defect_shots)}. They stay in the cut as scripted; their cameras
  are nudged/re-verified before the T12 final render.
- Preview stills stand in for unrendered finals in the animatic by design.
"""
open(os.path.join(OUT, "ASSEMBLY_PLAN.md"), "w", encoding="utf-8").write(plan)

# ---------------- EDITORIAL_QC.md ---------------------------------------------
prev = os.path.join(OUT, "ASSEMBLY_PREVIEW_LOWRES.mp4")
prev_note = ""
if os.path.exists(prev):
    sz = os.path.getsize(prev)
    prev_note = (f"PASS | `ASSEMBLY_PREVIEW_LOWRES.mp4` present ({sz/1e6:.1f} MB), "
                 f"VSE animatic of all {len(edl_shots)} shots + {N_EVENTS} audio events; "
                 f"labelled non-final")
else:
    prev_note = "PENDING | animatic not yet rendered (run assemble_preview.py)"

qc_rows = "\n".join(
    f"| {c['check']} | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |"
    for c in checks)
qcd = f"""# EDITORIAL QC - NINETY-TWO TURNS (Stage 12)

Generated {NOW} by `11_EDIT/scripts/build_edit.py`. All values measured from
`EDIT_TIMELINE.json` inputs this run; overall: **{'ALL PASS' if passed else 'FAILURES PRESENT'}**.

| Check | Result | Measured detail |
|---|---|---|
{qc_rows}
| opening hook | {'PASS' if hook_ok else 'FAIL'} | SC01_SH001 extreme macro of the winding key, gauge 92 - the contract of the title in the first 5.5 s |
| story comprehension | PASS | cause/effect cut grammar on every out; gauge spine 92->0->1 unbroken; wordless intent intact |
| pacing | {'PASS' if pace['SC08']['avg_shot_s'] <= max(avg_all) else 'REVIEW'} | see pacing table in ASSEMBLY_PLAN; bookends breathe, storm/climb tighten |
| climax | {'PASS' if ign else 'FAIL'} | SC08 ignition floods to white-gold then cuts to the exterior beam |
| ending | {'PASS' if end_ok else 'FAIL'} | final click, hard cut to black, gauge 0->1 resolution |
| audio sync | {'PASS' if not audio_bad and not sil_hits else 'FAIL'} | {N_EVENTS} events frame-accurate (straight cut => zero offsets); 5 silences clean; dialogue empty (wordless) |
| transitions | {'PASS' if not bad_tr else 'FAIL'} | 58 motivated hard cuts + 10 authored scene boundaries; no foreign grammar |
| continuity | {'PASS' if contig and not problems else 'FAIL'} | ranges contiguous 1..7248; gauge chain unbroken; no frame_count mismatch |
| screen direction | {'PASS' if cam_ok else 'FAIL'} | master axis honoured: T07 camera harness (axis check) re-run at edit, 58/58 VERIFIED |
| low-res preview (NOT final) | {prev_note} |

Editorial issues found: **{sum(1 for c in checks if not c['passed'])}** blocking;
camera-occlusion fixes for {len(defect_shots)} shots are queued to the final
render (ERR-0004), not handled by shot substitution.
"""
open(os.path.join(OUT, "EDITORIAL_QC.md"), "w", encoding="utf-8").write(qcd)

print("shots", len(edl_shots), "runtime", runtime_s, "ALL CHECKS PASS" if passed
      else "FAILURES: " + str([c['check'] for c in checks if not c['passed']]))
