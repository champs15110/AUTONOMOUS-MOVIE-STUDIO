#!/usr/bin/env python3
"""
run_previews - Stage 11 preview render driver.

Backend policy (honest): the preferred cloud backend JANCTION Render is NOT
configured in this runtime (no config, no credentials, network restricted);
recorded as ERR-0003 with classification TOOL_ABSENT before any recovery.
Recovery used: real Blender via the pypi `bpy` module, Cycles CPU (the
MASTER_CONFIG primary candidate `blender_headless_cpu`) - real frames.

Runs one fresh process per scene (preview_render.py), aggregates:
  11_RENDER/RENDER_STATUS.json    per-scene PREVIEW_* status + QC
  11_RENDER/RENDER_ESTIMATES.json measured preview cost + extrapolated final
                                  cost + 240-frame render-unit splits
  11_RENDER/RENDER_ERRORS.json    backend failure + per-scene problems

Run:  LD_LIBRARY_PATH=/tmp/glstub python3 11_RENDER/scripts/run_previews.py
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "11_RENDER")
NOW = datetime.now(timezone.utc).isoformat(timespec="seconds")

SCENE_FRAMES = {
    "SC01": (1, 768), "SC02": (769, 1560), "SC03": (1561, 2208),
    "SC04": (2209, 2928), "SC05": (2929, 3792), "SC06": (3793, 4464),
    "SC07": (4465, 5472), "SC08": (5473, 6288), "SC09": (6289, 6768),
    "SC10": (6769, 7248),
}
FINAL_FACTOR = (1920 * 1080) / (480 * 270) * (128 / 32)   # pixels x samples
JOB_LIMIT = 240  # JANCTION beta final-job frame limit


def record_backend_error():
    """Capture the JANCTION absence BEFORE recovery, per failure policy."""
    log = json.load(open(os.path.join(ROOT, "ERROR_LOG.json"), encoding="utf-8"))
    if any(e.get("error_id") == "ERR-0003" for e in log["errors"]):
        return [e for e in log["errors"] if e.get("error_id") == "ERR-0003"]
    entry = dict(
        error_id="ERR-0003", utc=NOW, task_id="T12_FINAL_RENDER",
        shot_id=None, scene_id="ALL",
        command_or_step="submit preview to configured cloud Blender renderer "
                        "(JANCTION Render preferred)",
        error_text="No JANCTION/cloud render backend is configured in this "
                   "runtime: no config entry, no credentials, and outbound "
                   "network is restricted to github/pypi/npm hosts. "
                   "MASTER_CONFIG blender_local.available=false (unchanged).",
        classification="TOOL_ABSENT",
        probable_cause="cloud render layer was documented at T05 but never "
                       "materialised in this sandbox",
        impact="no cloud preview/final renders possible from this runtime",
        preserved_outputs="all 06-10 stage artefacts intact",
        recovery_attempted="pypi bpy module (Blender 4.3.0) + Cycles CPU, the "
                           "MASTER_CONFIG 'blender_headless_cpu' candidate; "
                           "missing system GL/X libs satisfied with no-op "
                           "stubs + libxkbcommon from an opencv wheel "
                           "(headless CPU path never calls them)",
        resolution="MITIGATED", retry_count_after=0,
    )
    log["errors"].append(entry)
    log["last_updated"] = NOW
    json.dump(log, open(os.path.join(ROOT, "ERROR_LOG.json"), "w"),
              indent=2, ensure_ascii=False)
    return [dict(source="ERROR_LOG ERR-0003", **{k: v for k, v in entry.items()
                                                 if k != "source"})]


def record_camera_defects():
    """ERR-0004 (idempotent): preview-stage occlusion audit found shot cameras
    whose subject line-of-sight is blocked - invisible to T07's projection-only
    verification. Fix before final render (T12)."""
    audit_path = os.path.join(OUT, "CAMERA_OCCLUSION_AUDIT.json")
    if not os.path.exists(audit_path):
        return []
    audit = json.load(open(audit_path, encoding="utf-8"))
    defects = audit.get("defects", [])
    if not defects:
        return []
    log = json.load(open(os.path.join(ROOT, "ERROR_LOG.json"), encoding="utf-8"))
    if not any(e.get("error_id") == "ERR-0004" for e in log["errors"]):
        log["errors"].append(dict(
            error_id="ERR-0004", utc=NOW, task_id="T10_EDIT",
            shot_id=", ".join(d["shot_id"] for d in defects), scene_id="MULTI",
            command_or_step="Stage 11 preview QC + camera occlusion audit "
                            "(11_RENDER/scripts/occlusion_audit.py)",
            error_text=f"{len(defects)} of 46 shot cameras have the subject in "
                       "frame but the line of sight blocked by set geometry "
                       "(quay/coping/stall leg/tower shell/burner), e.g. "
                       "SC04_SH001 fully behind STREETS_coping",
            classification="TECHNICAL_DEFECT",
            probable_cause="T07 camera verification tested projection and "
                           "framing but never raycast occlusion; preview QC "
                           "raycasts exposed it",
            impact="affected shots would render the subject hidden behind set "
                   "geometry in the final",
            preserved_outputs="all shots/frames preserved; audit artefact "
                              "11_RENDER/CAMERA_OCCLUSION_AUDIT.json",
            recovery_attempted="representative shots for SC04/SC09 switched to "
                               "probe-clear shots (SC04_SH004, SC09_SH001); "
                               "blocked shots queued for camera nudge + "
                               "re-verification before T12 final render",
            resolution="MITIGATED", retry_count_after=0))
        log["last_updated"] = NOW
        json.dump(log, open(os.path.join(ROOT, "ERROR_LOG.json"), "w"),
                  indent=2, ensure_ascii=False)
    return defects


def main():
    base_errors = record_backend_error()
    camera_defects = record_camera_defects()
    statuses, estimates, scene_errors = {}, [], []
    for sid in sorted(SCENE_FRAMES):
        r = subprocess.run(
            [sys.executable, os.path.join(HERE, "preview_render.py"),
             "--scene", sid],
            capture_output=True, text=True,
            env=dict(os.environ, LD_LIBRARY_PATH="/tmp/glstub"),
            timeout=900)
        line = next((l for l in reversed(r.stdout.splitlines())
                     if l.startswith("{")), None)
        if line is None:
            st = dict(scene_id=sid, status="PREVIEW_FAILED",
                      problems=[f"renderer crashed: {r.stderr[-300:]}"])
        else:
            st = json.loads(line)
        statuses[sid] = st
        print(sid, st["status"])
        f0, f1 = SCENE_FRAMES[sid]
        frames = f1 - f0 + 1
        sec = st.get("render_seconds") or 0
        per_final = sec * FINAL_FACTOR
        estimates.append(dict(
            scene_id=sid, frames=frames,
            preview_seconds=sec, preview_spec="480x270 Cycles 32spp CPU",
            final_spec="1920x1080 Cycles 128spp CPU (denoised)",
            est_seconds_per_final_frame=round(per_final, 1),
            est_final_scene_minutes=round(frames * per_final / 60, 1),
            render_units_of_240=[(f0 + i * JOB_LIMIT, min(f1, f0 + (i + 1) * JOB_LIMIT - 1))
                                 for i in range((frames + JOB_LIMIT - 1) // JOB_LIMIT)],
            janction_estimate="UNAVAILABLE - no backend configured"))
        for prob in st.get("problems", []):
            scene_errors.append(dict(scene_id=sid, status=st["status"],
                                     problem=prob))

    json.dump(dict(schema_version=1, generated=NOW,
                   backend=dict(preferred="JANCTION Render", configured=False,
                                used="pypi bpy 4.3.0 / CYCLES CPU (no GPU)"),
                   job_limit_frames=JOB_LIMIT,
                   statuses={s: dict(status=v["status"],
                                     representative_shot=v.get("representative_shot"),
                                     preview_file=v.get("preview_file"),
                                     frame=v.get("frame"),
                                     render_seconds=v.get("render_seconds"),
                                     qc=v.get("qc"),
                                     technical_adjustments=v.get("technical_adjustments", {}),
                                     preflight=v.get("checks", {}).get("preflight"))
                             for s, v in statuses.items()}),
              open(os.path.join(OUT, "RENDER_STATUS.json"), "w"), indent=2)
    json.dump(dict(schema_version=1, generated=NOW,
                   method="measured preview cost extrapolated by pixel x "
                          "sample ratio; JANCTION estimate API unavailable",
                   scenes=estimates),
              open(os.path.join(OUT, "RENDER_ESTIMATES.json"), "w"), indent=2)
    json.dump(dict(schema_version=1, generated=NOW,
                   backend_errors=base_errors, scene_problems=scene_errors,
                   camera_occlusion_defects=camera_defects,
                   camera_occlusion_note="fix/re-verify these shots before "
                                         "T12 final render (see ERR-0004)"),
              open(os.path.join(OUT, "RENDER_ERRORS.json"), "w"), indent=2)
    bad = [s for s, v in statuses.items() if v["status"] != "PREVIEW_QC_PASS"]
    print("ALL PASS" if not bad else f"FAILING: {bad}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
