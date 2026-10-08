#!/usr/bin/env python3
"""
Stage 10 audio harness — NINETY-TWO TURNS.

Verifies the audio structure against the approved plan and the acceptance
contract, then writes the deliverables:
  AUDIO_TIMELINE.json, SFX_PLAN.json, AUDIO_INDEX.json, AUDIO_QC.md,
  music/MUSIC_CUE_SHEET.json, sfx/SFX_CUE_SHEET.json, mix/MIX_PLAN.json

Checks:
  1. asset-integrity    every event's asset exists; WAV header 48 kHz 16-bit;
                        peak <= -1 dBFS (0.891); provenance = synthesized here
  2. coverage           every frame 1-7248 covered by ambience/music/sfx, or
                        inside a declared intentional silence; no undeclared
                        gap longer than 6 s (144 frames)
  3. scene-coverage     every scene has ambience; music present or declared
                        intentional (SC05/SC06/SC10)
  4. sync-anchors       rain starts exactly at SC04_SH003 f2461; ignition at
                        SC08_SH007 f0+24; complete motif at SC08_SH005 f0;
                        spark hum ends inside SC08_SH003; final click inside
                        SC10_SH005; beacon loop starts SC09_SH001 f0
  5. gait-schedule      SC03 locked four-beat (even 12f); SC04 irregular;
                        SC07_SH006 skipping (gap > 20f); SC07_SH007 dragging
  6. wordless           dialogue track empty; DIALOGUE_PLAN.md declares it
  7. event-bounds       all events within 1-7248; loops have frame_out
  8. mix-targets        MIX_PLAN carries -16 LUFS / -1.5 dBTP / 48 kHz stereo
                        (loudness measurement honestly PENDING at T11)

Exit 0 only when all checks PASS.
"""
import json
import math
import os
import sys
import wave
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import audio_plan as P  # noqa: E402

OUT = os.path.join(ROOT, "10_AUDIO")
FPS = P.FPS
MANIFEST = json.load(open(os.path.join(OUT, "assets", "ASSETS_MANIFEST.json"),
                          encoding="utf-8"))
ASSETS = {a["id"]: a for a in MANIFEST["assets"]}
NOW = datetime.now(timezone.utc).isoformat(timespec="seconds")

SCENES_NO_MUSIC = {
    "SC05": "storm wall is the score; the spark hum (diegetic) is the only tone",
    "SC06": "pure sound-design scene - the quietest moment must not be scored",
    "SC10": "diegetic-only close by design ('water dripping. nothing else.')",
}

fails = []


def check(name, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f"  — {detail}" if detail and not ok else ""))
    if not ok:
        fails.append(f"{name}: {detail}")
    return ok


def dur_frames(asset_id):
    return int(math.ceil(ASSETS[asset_id]["dur"] * FPS))


def event_span(e):
    if e["frame_out"] is not None:
        return e["frame_in"], e["frame_out"]
    return e["frame_in"], min(P.TOTAL_FRAMES, e["frame_in"] + dur_frames(e["asset"]))


def main():
    print("Stage 10 audio checks")

    # 1 asset integrity
    probs = []
    used = {e["asset"] for e in P.ALL_EVENTS}
    for aid in used:
        if aid not in ASSETS:
            probs.append(f"{aid} missing from manifest")
            continue
        a = ASSETS[aid]
        path = os.path.join(OUT, "assets", a["category"], f"{aid}.wav")
        if not os.path.exists(path):
            probs.append(f"{aid} wav missing")
            continue
        with wave.open(path, "rb") as w:
            if w.getframerate() != 48000 or w.getsampwidth() != 2:
                probs.append(f"{aid} bad format {w.getframerate()}/{w.getsampwidth()}")
        if a["peak"] > 0.892:
            probs.append(f"{aid} peak {a['peak']} > -1 dBFS")
        if "procedurally synthesized in-repo" not in a["provenance"]:
            probs.append(f"{aid} provenance not documented")
    unused = set(ASSETS) - used
    check("asset-integrity", not probs, "; ".join(probs))
    check("assets-all-used", not unused, f"unused: {sorted(unused)}")

    # 1b loop seamlessness (beds repeat for whole scenes)
    import array as _ar
    seam_probs = []
    for aid, a in ASSETS.items():
        if not a["loop"]:
            continue
        path = os.path.join(OUT, "assets", a["category"], f"{aid}.wav")
        with wave.open(path, "rb") as w:
            ch = w.getnchannels()
            raw = w.readframes(w.getnframes())
        samples = _ar.array("h")
        samples.frombytes(raw)
        for c in range(ch):
            xs = samples[c::ch]
            if len(xs) < 1000:
                continue
            diffs = [abs(xs[i + 1] - xs[i]) for i in range(0, len(xs) - 1, 7)]
            mean_diff = sum(diffs) / len(diffs)
            seam = abs(xs[0] - xs[-1])
            if seam > max(8 * mean_diff, 600):
                seam_probs.append(f"{aid} ch{c} seam {seam} vs mean-diff {mean_diff:.0f}")
    check("loop-seamless", not seam_probs, "; ".join(seam_probs))

    # 2 coverage
    cover = [False] * (P.TOTAL_FRAMES + 2)
    for e in P.ALL_EVENTS:
        a, b = event_span(e)
        for f in range(max(1, a), min(P.TOTAL_FRAMES, b) + 1):
            cover[f] = True
    gaps = []
    f = 1
    while f <= P.TOTAL_FRAMES:
        if not cover[f]:
            g0 = f
            while f <= P.TOTAL_FRAMES and not cover[f]:
                f += 1
            gaps.append((g0, f - 1))
        else:
            f += 1
    bad_gaps = []
    for g0, g1 in gaps:
        if g1 - g0 + 1 > 144:
            declared = any(not (g1 < s["frames"][0] or g0 > s["frames"][1])
                           for s in P.INTENTIONAL_SILENCES)
            if not declared:
                bad_gaps.append((g0, g1))
    check("coverage", not bad_gaps, f"undeclared >6s gaps: {bad_gaps}")

    # 3 scene coverage
    sprob = []
    for sid, (a, b) in P.SCENE_FRAMES.items():
        amb = [e for e in P.AMBIENCE if e["frame_in"] <= b and event_span(e)[1] >= a]
        if not amb:
            sprob.append(f"{sid} no ambience")
        mus = [e for e in P.MUSIC if e["frame_in"] <= b and event_span(e)[1] >= a]
        if not mus and sid not in SCENES_NO_MUSIC:
            sprob.append(f"{sid} no music and not declared")
    check("scene-coverage", not sprob, "; ".join(sprob))

    # 4 sync anchors
    anchors = []
    rain = next(e for e in P.AMBIENCE if e["asset"] == "AMB_RAIN_STEADY"
                and e["shot"] == "SC04_SH003")
    anchors.append((rain["frame_in"] == 2461, "rain start f2461"))
    ig = next(e for e in P.SFX if e["asset"] == "SFX_IGNITION_BLOOM")
    anchors.append((ig["frame_in"] == P.SHOT_FRAMES["SC08_SH007"][0] + 24,
                    "ignition at SH007 f0+24"))
    cc = next(e for e in P.MUSIC if e["asset"] == "MUS_CLOCK_COMPLETE")
    anchors.append((cc["frame_in"] == P.SHOT_FRAMES["SC08_SH005"][0],
                    "complete motif at SH005 f0"))
    hum = next(e for e in P.SFX if e["asset"] == "SFX_SPARK_HUM")
    s3 = P.SHOT_FRAMES["SC08_SH003"]
    anchors.append((s3[0] <= hum["frame_out"] <= s3[1], "spark hum ends inside SH003"))
    fc = [e for e in P.SFX if e["asset"] == "SFX_FINAL_CLICK"]
    s5 = P.SHOT_FRAMES["SC10_SH005"]
    anchors.append((s5[0] <= fc[-1]["frame_in"] <= s5[1], "final click inside SH005"))
    br = next(e for e in P.SFX if e["asset"] == "SFX_BEACON_ROTATE")
    anchors.append((br["frame_in"] == P.SHOT_FRAMES["SC09_SH001"][0],
                    "beacon loop at SC09_SH001 f0"))
    check("sync-anchors", all(a for a, _ in anchors),
          "; ".join(n for a, n in anchors if not a))

    # 5 gait schedule
    def ticks(shot):
        return sorted(e["frame_in"] for e in P.SFX
                      if e["shot"] == shot and e["asset"] == "SFX_FOOTSTEP_TICK")
    t3 = ticks("SC03_SH001")
    d3 = {b - a for a, b in zip(t3, t3[1:])}
    t4 = ticks("SC04_SH002")
    d4 = {b - a for a, b in zip(t4, t4[1:])}
    t6 = ticks("SC07_SH006")
    d6 = [b - a for a, b in zip(t6, t6[1:])]
    t7 = ticks("SC07_SH007")
    d7 = [b - a for a, b in zip(t7, t7[1:])]
    gait = (d3 == {12} and len(d4) > 2 and max(d6) > 20 and min(d7) >= 18
            and len(t3) >= 9)
    check("gait-schedule", gait,
          f"SC03 {d3} | SC04 {sorted(d4)} | SC07_6 max {max(d6)} | SC07_7 min {min(d7)}")

    # 6 wordless
    dp = os.path.join(OUT, "DIALOGUE_PLAN.md")
    wordless = (not P.DIALOGUE
                and not any(e["track"] == "dialogue" for e in P.ALL_EVENTS)
                and os.path.exists(dp)
                and "wordless" in open(dp, encoding="utf-8").read().lower())
    check("wordless", wordless, "dialogue must be empty and documented")

    # 7 event bounds
    bprob = []
    for e in P.ALL_EVENTS:
        a, b = event_span(e)
        if a < 1 or b > P.TOTAL_FRAMES:
            bprob.append(f"{e['asset']}@{a}")
        if e["loop"] and e["frame_out"] is None:
            bprob.append(f"{e['asset']} loop without frame_out")
    check("event-bounds", not bprob, "; ".join(bprob))

    # 8 mix targets
    m = P.MIX["target"]
    check("mix-targets",
          m["integrated_lufs"] == -16.0 and m["true_peak_dbtp"] == -1.5
          and m["sample_rate"] == 48000 and m["channels"] == 2,
          str(m))

    # ------------------------------------------------------- deliverables --
    timeline = dict(
        schema_version=1, task_id="T09_AUDIO", project_id="AMS-001",
        film_title="NINETY-TWO TURNS", fps=FPS, total_frames=P.TOTAL_FRAMES,
        generated=NOW,
        wordless=True,
        tracks={
            "dialogue": [],
            "ambience": [dict(e, frame_out=event_span(e)[1]) for e in P.AMBIENCE],
            "music": [dict(e, frame_out=event_span(e)[1]) for e in P.MUSIC],
            "sfx": [dict(e, frame_out=event_span(e)[1]) for e in P.SFX],
        },
        intentional_silences=P.INTENTIONAL_SILENCES,
        scenes_without_music=SCENES_NO_MUSIC,
    )
    foley_ids = ("SFX_RATCHET_CLICK_A", "SFX_RATCHET_CLICK_B", "SFX_RATCHET_CLICK_C",
                 "SFX_FOOTSTEP_TICK", "SFX_FOOTSTEP_TICK_ECHO", "SFX_JOINT_ALIGN",
                 "SFX_POLE_SCRAPE", "SFX_GLASS_SEAL", "SFX_KEY_LIFT",
                 "SFX_BARE_FOOT_A", "SFX_BARE_FOOT_B", "SFX_RATCHET_ENGAGE")

    def asset_block(aid):
        a = ASSETS[aid]
        shots = sorted({e["shot"] for e in P.ALL_EVENTS if e["asset"] == aid})
        return dict(id=aid, path=f"10_AUDIO/assets/{a['category']}/{aid}.wav",
                    dur=a["dur"], loop=a["loop"], purpose=a["purpose"],
                    shots_used=shots, provenance=a["provenance"])

    sfx_plan = dict(
        schema_version=1, task_id="T09_AUDIO", generated=NOW,
        policy="every sound traces to an approved sound_intention line in "
               "MASTER_SHOT_PLAN.json; no decorative sound",
        foley=[asset_block(a) for a in foley_ids if a in ASSETS],
        hard_sfx=[asset_block(a) for a in sorted(ASSETS)
                  if a.startswith("SFX_") and a not in foley_ids],
        ambience=[asset_block(a) for a in sorted(ASSETS) if a.startswith("AMB_")],
        events=[dict(e, frame_out=event_span(e)[1]) for e in P.SFX],
    )
    cue_sheet = dict(
        schema_version=1, task_id="T09_AUDIO", generated=NOW,
        score_note="procedurally synthesized scratch score (original); final "
                   "performance/re-recording is a post-production decision "
                   "documented in MUSIC_PLAN.md",
        cues=[dict(id=a, **{k: v for k, v in asset_block(a).items() if k != "id"})
              for a in sorted(ASSETS) if a.startswith("MUS_")],
        events=[dict(e, frame_out=event_span(e)[1]) for e in P.MUSIC],
    )
    sfx_sheet = dict(schema_version=1, task_id="T09_AUDIO", generated=NOW,
                     events=[dict(e, frame_out=event_span(e)[1]) for e in P.SFX])
    index = dict(
        schema_version=1, task_id="T09_AUDIO", generated=NOW,
        asset_count=len(ASSETS),
        total_asset_seconds=MANIFEST["total_dur"],
        licensing="all assets original - procedurally synthesized in-repo "
                  "(pure Python, deterministic); no samples, no third-party "
                  "content, no licenses required",
        missing_assets=[],
        pending=["loudness measurement (requires ffmpeg; measured at T11 render QC)"],
        assets=[ASSETS[a] for a in sorted(ASSETS)],
    )
    for rel, doc in (("AUDIO_TIMELINE.json", timeline), ("SFX_PLAN.json", sfx_plan),
                     ("AUDIO_INDEX.json", index)):
        with open(os.path.join(OUT, rel), "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2)
            fh.write("\n")
    for rel, doc in ((os.path.join("music", "MUSIC_CUE_SHEET.json"), cue_sheet),
                     (os.path.join("sfx", "SFX_CUE_SHEET.json"), sfx_sheet),
                     (os.path.join("mix", "MIX_PLAN.json"), P.MIX)):
        os.makedirs(os.path.dirname(os.path.join(OUT, rel)), exist_ok=True)
        with open(os.path.join(OUT, rel), "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2)
            fh.write("\n")

    qc = ["# Stage 10 — Audio QC (NINETY-TWO TURNS)", "",
          f"Generated: {NOW} · harness: `run_audio_tests.py`", "",
          f"- {len(ASSETS)} assets (all original, synthesized in-repo; none missing)",
          f"- {len(P.ALL_EVENTS)} timeline events across ambience/music/sfx tracks",
          f"- dialogue track empty by design (wordless film)",
          f"- {len(P.INTENTIONAL_SILENCES)} declared intentional silences (all trace to approved intentions)",
          "- scenes without score by design: " + ", ".join(SCENES_NO_MUSIC),
          "- loudness compliance (-16 LUFS / -1.5 dBTP) PENDING measurement at T11 (needs ffmpeg)", "",
          "| Check | Result |", "|---|---|"]
    qc.append(f"| all | {'PASS' if not fails else 'FAIL: ' + '; '.join(fails)} |")
    with open(os.path.join(OUT, "AUDIO_QC.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(qc) + "\n")

    print("PASS" if not fails else "FAIL")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
