#!/usr/bin/env python3
"""
AMS MASTER CONTROLLER CLI
=========================
Single entry point for mutating the persistent production state of the
AUTONOMOUS-MOVIE-STUDIO project. The repository is the source of truth;
conversation memory is never authoritative.

Every mutation performed by this tool:
  * validates the change against the allowed status enum,
  * writes atomically (tmp file + os.replace) with a .bak of the prior version,
  * refreshes `last_updated`,
  * refuses illegal transitions (notably: overall_status -> COMPLETE is blocked
    unless FINAL/FINAL_FILM.mp4 exists and has been verified).

Usage:  python3 tools/studio.py <command> [options]
Run:    python3 tools/studio.py --help
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATE = os.path.join(ROOT, "PROJECT_STATE.json")
CONFIG = os.path.join(ROOT, "MASTER_CONFIG.json")
QUEUE = os.path.join(ROOT, "TASK_QUEUE.json")
ERRORS = os.path.join(ROOT, "ERROR_LOG.json")
SHOTS = os.path.join(ROOT, "SHOT_REGISTRY.json")
MANIFEST = os.path.join(ROOT, "13_RENDER", "RENDER_MANIFEST.json")
CHANGELOG = os.path.join(ROOT, "CHANGELOG.md")
FINAL_MP4 = os.path.join(ROOT, "FINAL", "FINAL_FILM.mp4")

STATUS_ENUM = [
    "NOT_STARTED", "IN_PROGRESS", "PARTIAL", "READY",
    "VERIFIED", "FAILED", "BLOCKED", "COMPLETE",
]
DONE_STATUSES = {"VERIFIED", "COMPLETE"}

SHOT_STAGES = ["story", "assets", "animation", "camera",
               "lighting", "audio", "render", "QC"]

RENDER_LIFECYCLE = ["SCENE", "PREVIEW", "QC", "FINAL_RENDER", "VERIFY"]


# --------------------------------------------------------------------------- #
# io helpers
# --------------------------------------------------------------------------- #
def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


def load(path: str) -> dict:
    if not os.path.exists(path):
        die(f"missing state file: {rel(path)} (workspace not initialized?)")
    with open(path, "r", encoding="utf-8") as fh:
        try:
            return json.load(fh)
        except json.JSONDecodeError as exc:
            die(f"corrupt JSON in {rel(path)}: {exc}")


def save(path: str, data: dict) -> None:
    """Atomic write with a one-generation backup."""
    if os.path.exists(path):
        try:
            with open(path, "rb") as src, open(path + ".bak", "wb") as dst:
                dst.write(src.read())
        except OSError:
            pass
    if "last_updated" in data:
        data["last_updated"] = now()
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def ok(msg: str) -> None:
    print(msg)


def check_status(value: str, field: str) -> str:
    if value not in STATUS_ENUM:
        die(f"{field}: '{value}' is not an allowed status. Allowed: {', '.join(STATUS_ENUM)}")
    return value


# --------------------------------------------------------------------------- #
# validate
# --------------------------------------------------------------------------- #
def cmd_validate(_: argparse.Namespace) -> int:
    problems: list[str] = []
    warnings: list[str] = []

    state = load(STATE)
    config = load(CONFIG)
    queue = load(QUEUE)
    errlog = load(ERRORS)
    shots = load(SHOTS)
    man = load(MANIFEST)

    # --- required top-level PROJECT_STATE fields (per spec) -----------------
    required_state = [
        "project_id", "film_title", "current_stage", "current_task",
        "overall_status", "completed_stages", "failed_tasks", "blocked_tasks",
        "completed_shots", "failed_shots", "rendered_scenes", "verified_scenes",
        "final_mp4_status", "last_checkpoint", "last_updated",
    ]
    for field in required_state:
        if field not in state:
            problems.append(f"PROJECT_STATE.json missing required field: {field}")

    if state.get("overall_status") not in STATUS_ENUM:
        problems.append(f"PROJECT_STATE.overall_status invalid: {state.get('overall_status')}")

    # --- task records -------------------------------------------------------
    required_task = ["task_id", "stage", "status", "dependencies",
                     "input_files", "output_files", "retry_count",
                     "last_error", "checkpoint"]
    ids = set()
    for task in queue.get("tasks", []):
        tid = task.get("task_id", "<unnamed>")
        if tid in ids:
            problems.append(f"duplicate task_id: {tid}")
        ids.add(tid)
        for field in required_task:
            if field not in task:
                problems.append(f"task {tid} missing required field: {field}")
        if task.get("status") not in STATUS_ENUM:
            problems.append(f"task {tid} has invalid status: {task.get('status')}")

    # dependency integrity + cycle detection
    for task in queue.get("tasks", []):
        for dep in task.get("dependencies", []) or []:
            if dep not in ids:
                problems.append(f"task {task['task_id']} depends on unknown task {dep}")

    graph = {t["task_id"]: list(t.get("dependencies") or []) for t in queue.get("tasks", [])}
    seen, stack = set(), set()

    def visit(node: str) -> bool:
        if node in stack:
            return True
        if node in seen:
            return False
        stack.add(node)
        for dep in graph.get(node, []):
            if visit(dep):
                problems.append(f"dependency cycle involving {node}")
                stack.discard(node)
                return True
        stack.discard(node)
        seen.add(node)
        return False

    for node in graph:
        visit(node)

    # --- stage coverage -----------------------------------------------------
    defined = {s["stage_id"]: s["task_id"] for s in config.get("stage_definitions", [])}
    for stage_id, task_id in defined.items():
        if task_id not in ids:
            problems.append(f"stage {stage_id} maps to unknown task {task_id}")
        if stage_id not in state.get("stage_status", {}):
            problems.append(f"PROJECT_STATE.stage_status missing stage {stage_id}")

    # --- consistency: state lists vs task statuses --------------------------
    task_status = {t["task_id"]: t["status"] for t in queue.get("tasks", [])}
    for tid in state.get("failed_tasks", []):
        if task_status.get(tid) != "FAILED":
            problems.append(f"{tid} listed in failed_tasks but task status is {task_status.get(tid)}")
    for tid in state.get("blocked_tasks", []):
        if task_status.get(tid) != "BLOCKED":
            problems.append(f"{tid} listed in blocked_tasks but task status is {task_status.get(tid)}")
    for stage in state.get("completed_stages", []):
        mapped = defined.get(stage)
        if mapped and task_status.get(mapped) not in DONE_STATUSES:
            problems.append(f"stage {stage} in completed_stages but {mapped} is {task_status.get(mapped)}")

    # --- counters -----------------------------------------------------------
    ctr = state.get("counters", {})
    shot_records = shots.get("shots", [])
    if ctr.get("shots_planned") != len(shot_records):
        problems.append(f"counters.shots_planned ({ctr.get('shots_planned')}) != "
                        f"SHOT_REGISTRY entries ({len(shot_records)})")
    complete_shots = [s for s in shot_records if s.get("overall_status") == "VERIFIED"]
    if ctr.get("shots_complete") != len(complete_shots):
        problems.append(f"counters.shots_complete ({ctr.get('shots_complete')}) != "
                        f"verified shots ({len(complete_shots)})")
    if ctr.get("errors_logged") != len(errlog.get("errors", [])):
        problems.append(f"counters.errors_logged ({ctr.get('errors_logged')}) != "
                        f"ERROR_LOG entries ({len(errlog.get('errors', []))})")
    scene_records = man.get("scenes", [])
    if ctr.get("scenes_planned") != len(scene_records):
        problems.append(f"counters.scenes_planned ({ctr.get('scenes_planned')}) != "
                        f"RENDER_MANIFEST entries ({len(scene_records)})")
    rendered = [s["scene_id"] for s in scene_records
                if s["stage"]["FINAL_RENDER"]["status"] in DONE_STATUSES]
    if sorted(state.get("rendered_scenes", [])) != sorted(rendered):
        problems.append("PROJECT_STATE.rendered_scenes out of sync with RENDER_MANIFEST")
    verified = [s["scene_id"] for s in scene_records
                if s["stage"]["VERIFY"]["status"] in DONE_STATUSES]
    if sorted(state.get("verified_scenes", [])) != sorted(verified):
        problems.append("PROJECT_STATE.verified_scenes out of sync with RENDER_MANIFEST")

    # --- shot slot validity -------------------------------------------------
    for shot in shot_records:
        for slot in SHOT_STAGES:
            st = (shot.get(slot) or {}).get("status")
            if st not in STATUS_ENUM:
                problems.append(f"shot {shot.get('shot_id')} slot '{slot}' invalid status: {st}")
        if not re.fullmatch(r"SC\d{2}_SH\d{3}", shot.get("shot_id", "")):
            problems.append(f"shot id does not match SCnn_SHmmm: {shot.get('shot_id')}")

    # --- artefact existence for done tasks ----------------------------------
    for task in queue.get("tasks", []):
        if task["status"] in DONE_STATUSES:
            for out in task.get("output_files", []):
                if not os.path.exists(os.path.join(ROOT, out)):
                    warnings.append(f"task {task['task_id']} is {task['status']} but "
                                    f"output missing: {out}")

    # --- completion gate ----------------------------------------------------
    mp4_ok = state.get("final_mp4", {}).get("verified") is True
    if state.get("overall_status") == "COMPLETE":
        if not os.path.exists(FINAL_MP4):
            problems.append("overall_status is COMPLETE but FINAL/FINAL_FILM.mp4 does not exist")
        elif not mp4_ok:
            problems.append("overall_status is COMPLETE but final_mp4.verified is not true")
    if state.get("final_mp4_status") == "COMPLETE" and not os.path.exists(FINAL_MP4):
        problems.append("final_mp4_status is COMPLETE but the file does not exist")

    # --- report -------------------------------------------------------------
    print(f"validated {len(queue.get('tasks', []))} tasks, "
          f"{len(shot_records)} shots, {len(scene_records)} scenes")
    if warnings:
        print(f"\nWARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  ! {w}")
    if problems:
        print(f"\nPROBLEMS ({len(problems)}):")
        for p in problems:
            print(f"  x {p}")
        print("\nVALIDATION: FAIL")
        return 1
    print("\nVALIDATION: PASS")
    return 0


# --------------------------------------------------------------------------- #
# status / next
# --------------------------------------------------------------------------- #
def cmd_status(_: argparse.Namespace) -> int:
    state = load(STATE)
    queue = load(QUEUE)
    print(f"PROJECT      {state['project_id']}  \"{state['film_title']}\"")
    print(f"STAGE        {state['current_stage']}")
    print(f"TASK         {state['current_task']}")
    print(f"OVERALL      {state['overall_status']}")
    print(f"FINAL MP4    {state['final_mp4_status']}  exists={state['final_mp4']['exists']} "
          f"verified={state['final_mp4']['verified']}")
    print(f"CHECKPOINT   {state['last_checkpoint']['checkpoint_id']} @ "
          f"{state['last_checkpoint']['utc']}")
    print(f"UPDATED      {state['last_updated']}")
    print("\nSTAGE STATUS")
    for stage, st in state.get("stage_status", {}).items():
        print(f"  {stage:<24} {st}")
    print("\nTASK QUEUE")
    for t in queue["tasks"]:
        flag = "*" if t["task_id"] == state["current_task"] else " "
        print(f" {flag} {t['task_id']:<26} {t['status']:<12} retries={t['retry_count']} "
              f"deps={len(t.get('dependencies') or [])}")
    ctr = state.get("counters", {})
    print(f"\nSHOTS {ctr.get('shots_complete', 0)}/{ctr.get('shots_planned', 0)}   "
          f"SCENES rendered {ctr.get('scenes_rendered', 0)} verified "
          f"{ctr.get('scenes_verified', 0)} of {ctr.get('scenes_planned', 0)}   "
          f"ERRORS {ctr.get('errors_logged', 0)}   CHECKPOINTS {ctr.get('checkpoints', 0)}")
    return 0


def next_task_id(queue: dict, state: dict) -> str | None:
    task_status = {t["task_id"]: t["status"] for t in queue["tasks"]}
    # prefer the current task if it is still open
    cur = state.get("current_task")
    if cur and task_status.get(cur) not in DONE_STATUSES:
        return cur
    for task in queue["tasks"]:
        if task["status"] in DONE_STATUSES or task["status"] == "BLOCKED":
            continue
        deps = task.get("dependencies") or []
        if all(task_status.get(d) in DONE_STATUSES for d in deps):
            return task["task_id"]
    return None


def cmd_next(_: argparse.Namespace) -> int:
    queue = load(QUEUE)
    state = load(STATE)
    tid = next_task_id(queue, state)
    if not tid:
        if state.get("overall_status") == "COMPLETE":
            print("NEXT TASK: none - project COMPLETE")
        else:
            print("NEXT TASK: none unblocked. Every remaining task is BLOCKED or failed; "
                  "see ERROR_LOG.json")
        return 0
    task = next(t for t in queue["tasks"] if t["task_id"] == tid)
    print(f"NEXT TASK: {task['task_id']}  [{task['stage']}]")
    print(f"  title        {task['title']}")
    print(f"  status       {task['status']}")
    print(f"  retries      {task['retry_count']}")
    print(f"  last_error   {task['last_error']}")
    print(f"  inputs       {', '.join(task['input_files']) or '-'}")
    print(f"  outputs      {', '.join(task['output_files']) or '-'}")
    print("  acceptance")
    for a in task.get("acceptance", []):
        print(f"    - {a}")
    return 0


# --------------------------------------------------------------------------- #
# task / stage mutations
# --------------------------------------------------------------------------- #
def sync_task_lists(state: dict, queue: dict) -> None:
    """Rebuild failed/blocked lists and stage_status from the task table."""
    defined = {s["task_id"]: s["stage_id"] for s in load(CONFIG)["stage_definitions"]}
    state["failed_tasks"] = [t["task_id"] for t in queue["tasks"] if t["status"] == "FAILED"]
    state["blocked_tasks"] = [t["task_id"] for t in queue["tasks"] if t["status"] == "BLOCKED"]
    for task in queue["tasks"]:
        stage = defined.get(task["task_id"])
        if stage:
            state["stage_status"][stage] = task["status"]
    done_stages = [s for s, st in state["stage_status"].items() if st in DONE_STATUSES]
    state["completed_stages"] = [s["stage_id"] for s in load(CONFIG)["stage_definitions"]
                                 if s["stage_id"] in done_stages]
    # overall status roll-up
    statuses = [t["status"] for t in queue["tasks"]]
    if all(s in DONE_STATUSES for s in statuses):
        # completion gate enforced separately by cmd_finalize
        state["overall_status"] = "VERIFIED" if state["overall_status"] != "COMPLETE" \
            else "COMPLETE"
    elif any(s == "BLOCKED" for s in statuses):
        state["overall_status"] = "BLOCKED"
    elif any(s == "FAILED" for s in statuses):
        state["overall_status"] = "FAILED"
    elif all(s == "NOT_STARTED" for s in statuses):
        state["overall_status"] = "NOT_STARTED"
    else:
        state["overall_status"] = "IN_PROGRESS"


def cmd_task_set(a: argparse.Namespace) -> int:
    state, queue = load(STATE), load(QUEUE)
    task = next((t for t in queue["tasks"] if t["task_id"] == a.task_id), None)
    if task is None:
        die(f"unknown task_id: {a.task_id}")
    check_status(a.status, "task status")

    task["status"] = a.status
    if a.increment_retry:
        task["retry_count"] = int(task.get("retry_count", 0)) + 1
    if a.error is not None:
        task["last_error"] = a.error or None
    if a.status in DONE_STATUSES and a.status == "FAILED":
        pass
    if a.status == "FAILED" and not task.get("last_error"):
        warnings = ("task marked FAILED without an error string; "
                    "run `log-error` so the cause is recoverable")
        print(f"WARNING: {warnings}", file=sys.stderr)
    if a.status == "VERIFIED":
        missing = [o for o in task["output_files"]
                   if not os.path.exists(os.path.join(ROOT, o))
                   and not o.startswith("FINAL/FINAL_FILM.mp4")]
        if missing:
            print("WARNING: marking VERIFIED with missing outputs: "
                  f"{', '.join(missing)}", file=sys.stderr)

    if a.checkpoint_id:
        task["checkpoint"] = a.checkpoint_id

    sync_task_lists(state, queue)
    if a.status not in DONE_STATUSES and a.status != "BLOCKED":
        state["current_task"] = task["task_id"]
        defined = {s["task_id"]: s["stage_id"] for s in load(CONFIG)["stage_definitions"]}
        if task["task_id"] in defined:
            state["current_stage"] = defined[task["task_id"]]

    save(QUEUE, queue)
    save(STATE, state)
    ok(f"task {task['task_id']} -> {task['status']} "
       f"(retries={task['retry_count']}, overall={state['overall_status']})")
    return 0


# --------------------------------------------------------------------------- #
# shots
# --------------------------------------------------------------------------- #
def blank_shot(shot_id: str, scene_id: str, index: int) -> dict:
    return {
        "shot_id": shot_id,
        "scene_id": scene_id,
        "index_in_scene": index,
        "story": {"beat": None, "description": None, "dialogue": None,
                  "start_frame": 0, "end_frame": 0, "duration_seconds": 0.0,
                  "status": "NOT_STARTED"},
        "assets": {"required": [], "status": "NOT_STARTED"},
        "animation": {"file": None, "status": "NOT_STARTED"},
        "camera": {"move": None, "lens_mm": None, "file": None, "status": "NOT_STARTED"},
        "lighting": {"setup": None, "grade": None, "file": None, "status": "NOT_STARTED"},
        "audio": {"music_cue": None, "sfx": [], "voice": None, "status": "NOT_STARTED"},
        "render": {"preview": None, "final": None, "frames": None, "status": "NOT_STARTED"},
        "QC": {"report": None, "issues": [], "status": "NOT_STARTED"},
        "overall_status": "NOT_STARTED",
        "retry_count": 0,
        "last_error": None,
        "checkpoint": None,
    }


def recompute_shot(shot: dict) -> None:
    slots = [shot[s]["status"] for s in SHOT_STAGES]
    if all(s in DONE_STATUSES for s in slots):
        shot["overall_status"] = "VERIFIED"
    elif all(s == "NOT_STARTED" for s in slots):
        shot["overall_status"] = "NOT_STARTED"
    elif any(s == "BLOCKED" for s in slots):
        shot["overall_status"] = "BLOCKED"
    elif any(s == "FAILED" for s in slots):
        shot["overall_status"] = "FAILED"
    else:
        shot["overall_status"] = "IN_PROGRESS"


def sync_shots(state: dict, shots: dict) -> None:
    records = shots["shots"]
    state["counters"]["shots_planned"] = len(records)
    state["counters"]["shots_complete"] = sum(
        1 for s in records if s["overall_status"] == "VERIFIED")
    state["completed_shots"] = sorted(s["shot_id"] for s in records
                                      if s["overall_status"] == "VERIFIED")
    state["failed_shots"] = sorted(s["shot_id"] for s in records
                                   if s["overall_status"] == "FAILED")


def cmd_shot_add(a: argparse.Namespace) -> int:
    shots = load(SHOTS)
    if not re.fullmatch(r"SC\d{2}", a.scene_id):
        die(f"scene_id must match SCnn: {a.scene_id}")
    existing = [s for s in shots["shots"] if s["scene_id"] == a.scene_id]
    start = max((s["index_in_scene"] for s in existing), default=0)
    added = []
    for i in range(a.count):
        idx = start + i + 1
        sid = f"{a.scene_id}_SH{idx:03d}"
        if any(s["shot_id"] == sid for s in shots["shots"]):
            print(f"skip (exists): {sid}")
            continue
        shots["shots"].append(blank_shot(sid, a.scene_id, idx))
        added.append(sid)
    shots["status"] = "POPULATED"
    state = load(STATE)
    sync_shots(state, shots)
    save(SHOTS, shots)
    save(STATE, state)
    ok(f"added {len(added)} shot(s) to {a.scene_id}: {', '.join(added) or '(none)'} "
       f"| registry total {len(shots['shots'])}")
    return 0


def cmd_shot_set(a: argparse.Namespace) -> int:
    shots, state = load(SHOTS), load(STATE)
    shot = next((s for s in shots["shots"] if s["shot_id"] == a.shot_id), None)
    if shot is None:
        die(f"unknown shot_id: {a.shot_id} (add it with `shot-add` first)")
    if a.stage not in SHOT_STAGES:
        die(f"unknown shot stage '{a.stage}'. Allowed: {', '.join(SHOT_STAGES)}")
    check_status(a.status, "shot slot status")
    shot[a.stage]["status"] = a.status
    if a.artefact:
        shot[a.stage]["file"] = a.artefact
    if a.error is not None:
        shot["last_error"] = a.error or None
    if a.increment_retry:
        shot["retry_count"] = int(shot.get("retry_count", 0)) + 1
    recompute_shot(shot)
    sync_shots(state, shots)
    save(SHOTS, shots)
    save(STATE, state)
    ok(f"{a.shot_id}.{a.stage} -> {a.status} | shot overall {shot['overall_status']} | "
       f"{state['counters']['shots_complete']}/{state['counters']['shots_planned']} complete")
    return 0


def cmd_shot_show(a: argparse.Namespace) -> int:
    shots = load(SHOTS)
    targets = shots["shots"]
    if a.shot_id:
        targets = [s for s in targets if s["shot_id"] == a.shot_id]
    if not targets:
        print("no shots registered yet")
        return 0
    print(f"{'SHOT':<14}{'OVERALL':<13}" + "".join(f"{s[:9]:<10}" for s in SHOT_STAGES))
    for s in targets:
        row = "".join(f"{s[st]['status'][:9]:<10}" for st in SHOT_STAGES)
        print(f"{s['shot_id']:<14}{s['overall_status']:<13}{row}")
    return 0


# --------------------------------------------------------------------------- #
# scenes / render lifecycle
# --------------------------------------------------------------------------- #
def cmd_scene_add(a: argparse.Namespace) -> int:
    man = load(MANIFEST)
    if not re.fullmatch(r"SC\d{2}", a.scene_id):
        die(f"scene_id must match SCnn: {a.scene_id}")
    if any(s["scene_id"] == a.scene_id for s in man["scenes"]):
        print(f"skip (exists): {a.scene_id}")
        return 0
    man["scenes"].append({
        "scene_id": a.scene_id,
        "title": a.title,
        "shots": [],
        "start_frame": 0, "end_frame": 0, "duration_seconds": 0.0,
        "stage": {k: {"status": "NOT_STARTED", "artefact": None, "utc": None}
                  for k in RENDER_LIFECYCLE},
        "overall_status": "NOT_STARTED",
        "retry_count": 0,
        "last_error": None,
        "checkpoint": None,
    })
    man["status"] = "POPULATED"
    state = load(STATE)
    state["counters"]["scenes_planned"] = len(man["scenes"])
    save(MANIFEST, man)
    save(STATE, state)
    ok(f"scene {a.scene_id} registered | scenes planned {len(man['scenes'])}")
    return 0


def cmd_scene_set(a: argparse.Namespace) -> int:
    man, state = load(MANIFEST), load(STATE)
    scene = next((s for s in man["scenes"] if s["scene_id"] == a.scene_id), None)
    if scene is None:
        die(f"unknown scene_id: {a.scene_id} (add it with `scene-add` first)")
    if a.lifecycle not in RENDER_LIFECYCLE:
        die(f"unknown lifecycle stage '{a.lifecycle}'. Allowed: {', '.join(RENDER_LIFECYCLE)}")
    check_status(a.status, "scene lifecycle status")

    order = {k: i for i, k in enumerate(RENDER_LIFECYCLE)}
    idx = order[a.lifecycle]
    # gate: no stage may start before the previous one is done
    if idx > 0 and a.status not in ("FAILED", "BLOCKED"):
        prev = RENDER_LIFECYCLE[idx - 1]
        if scene["stage"][prev]["status"] not in DONE_STATUSES:
            die(f"{a.scene_id}: cannot set {a.lifecycle} while {prev} is "
                f"{scene['stage'][prev]['status']} (lifecycle is strictly ordered)")

    scene["stage"][a.lifecycle]["status"] = a.status
    scene["stage"][a.lifecycle]["utc"] = now()
    if a.artefact:
        scene["stage"][a.lifecycle]["artefact"] = a.artefact
        if not os.path.exists(os.path.join(ROOT, a.artefact)):
            print(f"WARNING: artefact not on disk: {a.artefact}", file=sys.stderr)
    if a.error is not None:
        scene["last_error"] = a.error or None
    if a.increment_retry:
        scene["retry_count"] = int(scene.get("retry_count", 0)) + 1

    slots = [scene["stage"][k]["status"] for k in RENDER_LIFECYCLE]
    if all(s in DONE_STATUSES for s in slots):
        scene["overall_status"] = "VERIFIED"
    elif any(s == "BLOCKED" for s in slots):
        scene["overall_status"] = "BLOCKED"
    elif any(s == "FAILED" for s in slots):
        scene["overall_status"] = "FAILED"
    elif all(s == "NOT_STARTED" for s in slots):
        scene["overall_status"] = "NOT_STARTED"
    else:
        scene["overall_status"] = "IN_PROGRESS"

    state["rendered_scenes"] = sorted(
        s["scene_id"] for s in man["scenes"]
        if s["stage"]["FINAL_RENDER"]["status"] in DONE_STATUSES)
    state["verified_scenes"] = sorted(
        s["scene_id"] for s in man["scenes"]
        if s["stage"]["VERIFY"]["status"] in DONE_STATUSES)
    state["counters"]["scenes_rendered"] = len(state["rendered_scenes"])
    state["counters"]["scenes_verified"] = len(state["verified_scenes"])

    save(MANIFEST, man)
    save(STATE, state)
    ok(f"{a.scene_id}.{a.lifecycle} -> {a.status} | scene overall {scene['overall_status']} | "
       f"rendered {len(state['rendered_scenes'])} verified {len(state['verified_scenes'])}")
    return 0


# --------------------------------------------------------------------------- #
# errors
# --------------------------------------------------------------------------- #
def cmd_log_error(a: argparse.Namespace) -> int:
    errlog, state, queue = load(ERRORS), load(STATE), load(QUEUE)
    enum = errlog["classification_enum"]
    if a.classification not in enum:
        die(f"unknown classification '{a.classification}'. Allowed: {', '.join(enum)}")
    eid = f"ERR-{len(errlog['errors']) + 1:04d}"
    errlog["errors"].append({
        "error_id": eid,
        "utc": now(),
        "task_id": a.task_id,
        "shot_id": a.shot_id,
        "scene_id": a.scene_id,
        "command_or_step": a.command,
        "error_text": a.error_text,
        "classification": a.classification,
        "probable_cause": a.cause,
        "impact": a.impact,
        "preserved_outputs": a.preserved,
        "recovery_attempted": a.recovery,
        "resolution": a.resolution,
        "retry_count_after": None,
    })
    task = next((t for t in queue["tasks"] if t["task_id"] == a.task_id), None)
    if task:
        task["last_error"] = a.error_text
        if a.mark_failed and task["status"] not in DONE_STATUSES:
            task["status"] = "FAILED"
        task["retry_count"] = int(task.get("retry_count", 0)) + 1
        errlog["errors"][-1]["retry_count_after"] = task["retry_count"]
        sync_task_lists(state, queue)
        save(QUEUE, queue)
    state["counters"]["errors_logged"] = len(errlog["errors"])
    save(ERRORS, errlog)
    save(STATE, state)
    ok(f"logged {eid} [{a.classification}] on {a.task_id}")
    return 0


# --------------------------------------------------------------------------- #
# checkpoint
# --------------------------------------------------------------------------- #
def cmd_checkpoint(a: argparse.Namespace) -> int:
    state = load(STATE)
    n = int(state["counters"].get("checkpoints", 0)) + 1
    cp_id = f"CP-{n:04d}"
    commit = None
    if a.commit:
        try:
            subprocess.run(["git", "add", "-A"], cwd=ROOT, check=True,
                           capture_output=True, text=True)
            msg = f"checkpoint {cp_id}: {a.summary}"
            res = subprocess.run(["git", "commit", "-m", msg, "--allow-empty"],
                                 cwd=ROOT, capture_output=True, text=True)
            if res.returncode == 0:
                commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                        check=True, capture_output=True,
                                        text=True).stdout.strip()
            else:
                print(f"WARNING: git commit skipped: {res.stderr.strip()}", file=sys.stderr)
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            print(f"WARNING: git unavailable ({exc})", file=sys.stderr)

    entry = {"checkpoint_id": cp_id, "utc": now(), "actor": a.actor,
             "task_id": a.task_id, "summary": a.summary, "git_commit": commit}
    state["checkpoints"].append(entry)
    state["counters"]["checkpoints"] = n
    state["last_checkpoint"] = {"checkpoint_id": cp_id, "utc": entry["utc"],
                                "task_id": a.task_id, "git_commit": commit,
                                "summary": a.summary}
    if a.task_id:
        queue = load(QUEUE)
        task = next((t for t in queue["tasks"] if t["task_id"] == a.task_id), None)
        if task:
            task["checkpoint"] = cp_id
            save(QUEUE, queue)
    save(STATE, state)

    stamp = entry["utc"].replace("T", " ").rstrip("Z") + " UTC"
    line = (f"| {cp_id} | {stamp} | {a.task_id or '-'} | {a.summary} | "
            f"{commit[:7] if commit else 'pending'} |\n")
    if os.path.exists(CHANGELOG):
        with open(CHANGELOG, "r", encoding="utf-8") as fh:
            body = fh.read()
        marker = "<!-- CHECKPOINT_TABLE_END -->"
        if marker in body:
            body = body.replace(marker, line + marker)
        else:
            body += "\n" + line
        with open(CHANGELOG, "w", encoding="utf-8") as fh:
            fh.write(body)
    ok(f"checkpoint {cp_id} recorded" + (f" (commit {commit[:7]})" if commit else ""))
    return 0


# --------------------------------------------------------------------------- #
# mp4 probe (dependency-free verification fallback)
# --------------------------------------------------------------------------- #
def probe_mp4(path: str) -> dict:
    """Parse MP4 boxes directly so verification works even without ffprobe."""
    info = {"path": rel(path), "exists": os.path.exists(path),
            "size_bytes": os.path.getsize(path) if os.path.exists(path) else 0,
            "brands": [], "duration_seconds": None, "tracks": [],
            "has_video": False, "has_audio": False, "faststart": False}
    if not info["exists"]:
        return info

    def boxes(fh, start, end):
        fh.seek(start)
        while fh.tell() + 8 <= end:
            pos = fh.tell()
            head = fh.read(8)
            if len(head) < 8:
                break
            size = int.from_bytes(head[:4], "big")
            kind = head[4:8].decode("latin-1")
            hdr = 8
            if size == 1:
                size = int.from_bytes(fh.read(8), "big")
                hdr = 16
            elif size == 0:
                size = end - pos
            if size < hdr:
                break
            yield kind, pos + hdr, pos + size
            fh.seek(pos + size)

    CONTAINERS = {"moov", "trak", "mdia", "minf", "stbl", "edts", "udta"}
    with open(path, "rb") as fh:
        total = os.path.getsize(path)
        top = [(k, s, e) for k, s, e in boxes(fh, 0, total)]
        kinds = [k for k, _, _ in top]
        # faststart == moov precedes mdat, so playback can begin before full download
        if "moov" in kinds and "mdat" in kinds:
            info["faststart"] = kinds.index("moov") < kinds.index("mdat")
        else:
            info["faststart"] = "moov" in kinds
        for kind, start, end in top:
            if kind == "ftyp":
                fh.seek(start)
                data = fh.read(min(64, end - start))
                info["brands"] = [data[i:i + 4].decode("latin-1")
                                  for i in range(0, len(data), 4)][:4]
            elif kind == "moov":
                for mk, ms, me in boxes(fh, start, end):
                    if mk == "mvhd":
                        fh.seek(ms)
                        ver = fh.read(1)[0]
                        fh.seek(ms + (4 if ver == 0 else 8))
                        fh.read(8 if ver == 0 else 16)  # creation + modification
                        timescale = int.from_bytes(fh.read(4), "big")
                        dur = int.from_bytes(fh.read(8 if ver else 4), "big")
                        if timescale:
                            info["duration_seconds"] = round(dur / timescale, 4)
                    elif mk == "trak":
                        track = {"kind": None, "width": None, "height": None,
                                 "timescale": None, "duration_seconds": None}
                        for tk, ts_, te in boxes(fh, ms, me):
                            if tk == "tkhd":
                                fh.seek(te - 8)
                                w = int.from_bytes(fh.read(4), "big") >> 16
                                h = int.from_bytes(fh.read(4), "big") >> 16
                                if w and h:
                                    track["width"], track["height"] = w, h
                            elif tk == "mdia":
                                for mk2, ms2, me2 in boxes(fh, ts_, te):
                                    if mk2 == "mdhd":
                                        fh.seek(ms2)
                                        ver = fh.read(1)[0]
                                        fh.seek(ms2 + (4 if ver == 0 else 8))
                                        fh.read(8 if ver == 0 else 16)
                                        tsc = int.from_bytes(fh.read(4), "big")
                                        d = int.from_bytes(fh.read(8 if ver else 4), "big")
                                        track["timescale"] = tsc
                                        if tsc:
                                            track["duration_seconds"] = round(d / tsc, 4)
                                    elif mk2 == "hdlr":
                                        fh.seek(ms2 + 8)
                                        track["kind"] = fh.read(4).decode("latin-1")
                        if track["kind"] == "vide":
                            info["has_video"] = True
                        elif track["kind"] == "soun":
                            info["has_audio"] = True
                        info["tracks"].append(track)
    return info


def cmd_probe(a: argparse.Namespace) -> int:
    target = os.path.join(ROOT, a.path) if not os.path.isabs(a.path) else a.path
    info = probe_mp4(target)
    print(json.dumps(info, indent=2))
    return 0 if info["exists"] else 1


def cmd_verify_final(a: argparse.Namespace) -> int:
    """The only completion gate: prove FINAL/FINAL_FILM.mp4 is real and in spec."""
    state, config = load(STATE), load(CONFIG)
    info = probe_mp4(FINAL_MP4)
    spec = config["delivery_spec"]
    tspec = config["target_spec"]
    checks = []

    def add(name, passed, detail):
        checks.append({"check": name, "pass": bool(passed), "detail": detail})

    add("file_exists", info["exists"], info["path"])
    add("size_nonzero", info["size_bytes"] > 0, f"{info['size_bytes']} bytes")
    add("mp4_brand", bool(info["brands"]), f"brands={info['brands']}")
    add("has_video_track", info["has_video"], "hdlr=vide")
    add("has_audio_track", info["has_audio"], "hdlr=soun")

    dur = info["duration_seconds"]
    add("duration_in_range", dur is not None and
        tspec["duration_seconds"]["min"] <= dur <= tspec["duration_seconds"]["max"],
        f"{dur}s (allowed {tspec['duration_seconds']['min']}-"
        f"{tspec['duration_seconds']['max']}s)")

    vids = [t for t in info["tracks"] if t["kind"] == "vide"]
    if vids:
        w, h = vids[0]["width"], vids[0]["height"]
        spec_res = tspec["resolution"]
        add("resolution_1920x1080", (w, h) == (spec_res["width"], spec_res["height"]),
            f"{w}x{h} (spec {spec_res['width']}x{spec_res['height']})")
        if w and h:
            add("aspect_16_9", abs(w / h - 16 / 9) < 0.01, f"{w / h:.4f}")
    else:
        add("resolution_1920x1080", False, "no video track")
        add("aspect_16_9", False, "no video track")

    add("moov_before_mdat_faststart", info["faststart"], "ftyp/moov ordering")

    # audio mdhd timescale IS the sample rate
    souns = [t for t in info["tracks"] if t["kind"] == "soun"]
    if souns:
        rate = souns[0].get("timescale")
        add("audio_sample_rate_48000", rate == spec["audio_sample_rate_hz"],
            f"{rate} Hz (spec {spec['audio_sample_rate_hz']} Hz)")
    else:
        add("audio_sample_rate_48000", False, "no audio track")

    sha = None
    if info["exists"]:
        h = hashlib.sha256()
        with open(FINAL_MP4, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        sha = h.hexdigest()
        add("sha256_computed", True, sha)

    passed = all(c["pass"] for c in checks)
    report = {
        "verified_at_utc": now(),
        "result": "PASS" if passed else "FAIL",
        "path": "FINAL/FINAL_FILM.mp4",
        "probe": info,
        "sha256": sha,
        "checks": checks,
        "note": ("Probed by tools/studio.py MP4 box parser. "
                 "If ffprobe is available, re-run for codec-level confirmation."),
    }
    out = os.path.join(ROOT, "12_QC", "reports", "FINAL_VERIFICATION.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    save(out, report)

    fm = state["final_mp4"]
    fm.update({"path": "FINAL/FINAL_FILM.mp4", "exists": info["exists"],
               "verified": passed, "verified_at_utc": report["verified_at_utc"],
               "duration_seconds": dur,
               "resolution": (f"{vids[0]['width']}x{vids[0]['height']}" if vids else None),
               "fps": tspec["fps"], "size_bytes": info["size_bytes"],
               "sha256": sha, "qc_report": "12_QC/reports/FINAL_VERIFICATION.json"})
    state["final_mp4_status"] = "VERIFIED" if passed else "FAILED"
    if passed:
        state["overall_status"] = "COMPLETE"
        state["current_stage"] = "13_FINAL_VERIFICATION"
        state["current_task"] = "T13_FINAL_VERIFICATION"
        queue = load(QUEUE)
        for t in queue["tasks"]:
            if t["task_id"] == "T13_FINAL_VERIFICATION":
                t["status"] = "VERIFIED"
        sync_task_lists(state, queue)
        state["overall_status"] = "COMPLETE"  # gate satisfied
        state["stage_status"]["13_FINAL_VERIFICATION"] = "VERIFIED"
        if "13_FINAL_VERIFICATION" not in state["completed_stages"]:
            state["completed_stages"].append("13_FINAL_VERIFICATION")
        save(QUEUE, queue)
    save(STATE, state)

    print(json.dumps(report, indent=2))
    print(f"\nFINAL VERIFICATION: {report['result']}")
    return 0 if passed else 1


# --------------------------------------------------------------------------- #
# cli
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="studio.py",
                                description="AMS master controller CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("validate", help="validate every state file").set_defaults(fn=cmd_validate)
    sub.add_parser("status", help="print project state").set_defaults(fn=cmd_status)
    sub.add_parser("next", help="print the next actionable task").set_defaults(fn=cmd_next)

    s = sub.add_parser("task-set", help="change a task's status")
    s.add_argument("task_id")
    s.add_argument("--status", required=True)
    s.add_argument("--error", default=None)
    s.add_argument("--increment-retry", action="store_true")
    s.add_argument("--checkpoint-id", default=None)
    s.set_defaults(fn=cmd_task_set)

    s = sub.add_parser("shot-add", help="register shots for a scene")
    s.add_argument("scene_id")
    s.add_argument("--count", type=int, required=True)
    s.set_defaults(fn=cmd_shot_add)

    s = sub.add_parser("shot-set", help="update one shot stage slot")
    s.add_argument("shot_id")
    s.add_argument("--stage", required=True)
    s.add_argument("--status", required=True)
    s.add_argument("--artefact", default=None)
    s.add_argument("--error", default=None)
    s.add_argument("--increment-retry", action="store_true")
    s.set_defaults(fn=cmd_shot_set)

    s = sub.add_parser("shot-show", help="tabulate shot status")
    s.add_argument("shot_id", nargs="?")
    s.set_defaults(fn=cmd_shot_show)

    s = sub.add_parser("scene-add", help="register a scene in the render manifest")
    s.add_argument("scene_id")
    s.add_argument("--title", default=None)
    s.set_defaults(fn=cmd_scene_add)

    s = sub.add_parser("scene-set", help="advance a scene through the render lifecycle")
    s.add_argument("scene_id")
    s.add_argument("--lifecycle", required=True)
    s.add_argument("--status", required=True)
    s.add_argument("--artefact", default=None)
    s.add_argument("--error", default=None)
    s.add_argument("--increment-retry", action="store_true")
    s.set_defaults(fn=cmd_scene_set)

    s = sub.add_parser("log-error", help="record a failure before recovering")
    s.add_argument("--task-id", required=True)
    s.add_argument("--classification", required=True)
    s.add_argument("--command", default=None)
    s.add_argument("--error-text", required=True)
    s.add_argument("--cause", default=None)
    s.add_argument("--impact", default=None)
    s.add_argument("--preserved", default=None)
    s.add_argument("--recovery", default=None)
    s.add_argument("--resolution", default="UNRESOLVED_BLOCKED")
    s.add_argument("--shot-id", default=None)
    s.add_argument("--scene-id", default=None)
    s.add_argument("--mark-failed", action="store_true")
    s.set_defaults(fn=cmd_log_error)

    s = sub.add_parser("checkpoint", help="record a checkpoint and touch CHANGELOG")
    s.add_argument("--task-id", default=None)
    s.add_argument("--summary", required=True)
    s.add_argument("--actor", default="master_controller")
    s.add_argument("--commit", action="store_true")
    s.set_defaults(fn=cmd_checkpoint)

    s = sub.add_parser("probe", help="probe an mp4 without ffprobe")
    s.add_argument("path")
    s.set_defaults(fn=cmd_probe)

    s = sub.add_parser("verify-final",
                       help="verify FINAL/FINAL_FILM.mp4 - the only completion gate")
    s.set_defaults(fn=cmd_verify_final)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
