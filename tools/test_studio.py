#!/usr/bin/env python3
"""
Self-test suite for the AMS master controller CLI.

Each test copies the live repository state into a throwaway directory and drives the
REAL tools/studio.py against it as a subprocess, so what is exercised is the shipped
code path, not a re-implementation of it.

Run:  python3 tools/test_studio.py -v
"""

from __future__ import annotations

import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CLI = os.path.join(HERE, "studio.py")

COPIED_FILES = [
    "PROJECT_STATE.json",
    "MASTER_CONFIG.json",
    "TASK_QUEUE.json",
    "ERROR_LOG.json",
    "SHOT_REGISTRY.json",
    "13_RENDER/RENDER_MANIFEST.json",
    "CHANGELOG.md",
]


# --------------------------------------------------------------------------- #
# minimal MP4 builder (enough for the dependency-free probe to read)
# --------------------------------------------------------------------------- #
def box(kind: str, payload: bytes) -> bytes:
    return struct.pack(">I", 8 + len(payload)) + kind.encode("latin-1") + payload


def mvhd(timescale: int, duration: int) -> bytes:
    return box("mvhd", struct.pack(">BBBBIIII", 0, 0, 0, 0, 0, 0, timescale, duration)
               + b"\x00" * 80)


def tkhd(w: int, h: int) -> bytes:
    body = struct.pack(">BBBBIIII", 0, 0, 0, 0, 0, 0, 0, 0) + b"\x00" * 72
    body += struct.pack(">II", w << 16, h << 16)  # width/height, 16.16 fixed
    return box("tkhd", body)


def mdhd(timescale: int, duration: int) -> bytes:
    return box("mdhd", struct.pack(">BBBBIIII", 0, 0, 0, 0, 0, 0, timescale, duration)
               + b"\x00" * 20)


def hdlr(handler: str) -> bytes:
    return box("hdlr", b"\x00\x00\x00\x00" + b"\x00" * 4 + handler.encode("latin-1")
               + b"\x00" * 12)


def trak(handler: str, w: int, h: int, timescale: int, duration: int) -> bytes:
    mdia = box("mdia", mdhd(timescale, duration) + hdlr(handler)
               + box("minf", box("stbl", box("stsd", b"\x00" * 8))))
    return box("trak", tkhd(w, h) + mdia)


def build_mp4(path: str, seconds: float = 300.0, w: int = 1920, h: int = 1080,
              timescale: int = 24000, faststart: bool = True) -> None:
    duration = int(seconds * timescale)
    ftyp = box("ftyp", b"isom" + struct.pack(">I", 512) + b"isomiso2mp41")
    moov = box("moov", mvhd(timescale, duration)
               + trak("vide", w, h, timescale, duration)
               + trak("soun", 0, 0, 48000, int(seconds * 48000)))
    mdat = box("mdat", b"\x00" * 64)
    order = (ftyp + moov + mdat) if faststart else (ftyp + mdat + moov)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(order)


# --------------------------------------------------------------------------- #
class StudioTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp(prefix="ams_test_")
        for rel in COPIED_FILES:
            src, dst = os.path.join(REPO, rel), os.path.join(self.tmp, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
        os.makedirs(os.path.join(self.tmp, "tools"), exist_ok=True)
        shutil.copy2(CLI, os.path.join(self.tmp, "tools", "studio.py"))
        os.makedirs(os.path.join(self.tmp, "12_QC", "reports"), exist_ok=True)
        os.makedirs(os.path.join(self.tmp, "FINAL"), exist_ok=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, os.path.join(self.tmp, "tools", "studio.py"),
                               *args], cwd=self.tmp, capture_output=True, text=True)

    def read(self, rel: str) -> dict:
        with open(os.path.join(self.tmp, rel), encoding="utf-8") as fh:
            return json.load(fh)

    # -- integrity --------------------------------------------------------- #
    def test_01_validate_passes_on_fresh_init(self):
        res = self.run_cli("validate")
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("VALIDATION: PASS", res.stdout)

    def test_02_status_reports_not_started(self):
        res = self.run_cli("status")
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("OVERALL      NOT_STARTED", res.stdout)

    def test_03_next_task_is_development(self):
        res = self.run_cli("next")
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("NEXT TASK: T01_DEVELOPMENT", res.stdout)

    def test_04_rejects_invalid_status(self):
        res = self.run_cli("task-set", "T01_DEVELOPMENT", "--status", "DONE")
        self.assertEqual(res.returncode, 1)
        self.assertIn("not an allowed status", res.stderr)

    def test_05_rejects_unknown_task(self):
        res = self.run_cli("task-set", "T99_NOPE", "--status", "IN_PROGRESS")
        self.assertEqual(res.returncode, 1)
        self.assertIn("unknown task_id", res.stderr)

    # -- task flow --------------------------------------------------------- #
    def test_06_task_progress_updates_current_task_and_rolls_up(self):
        self.assertEqual(self.run_cli("task-set", "T01_DEVELOPMENT",
                                      "--status", "IN_PROGRESS").returncode, 0)
        state = self.read("PROJECT_STATE.json")
        self.assertEqual(state["overall_status"], "IN_PROGRESS")
        self.assertEqual(state["current_task"], "T01_DEVELOPMENT")
        self.assertEqual(state["stage_status"]["01_DEVELOPMENT"], "IN_PROGRESS")

    def test_07_next_skips_unmet_dependencies(self):
        # T02 depends on T01; with T01 unfinished, next must still be T01.
        res = self.run_cli("next")
        self.assertIn("T01_DEVELOPMENT", res.stdout)
        self.run_cli("task-set", "T01_DEVELOPMENT", "--status", "VERIFIED")
        res = self.run_cli("next")
        self.assertIn("T02_SCREENPLAY", res.stdout)
        self.assertIn("completed_stages", json.dumps(self.read("PROJECT_STATE.json")))
        self.assertIn("01_DEVELOPMENT",
                      self.read("PROJECT_STATE.json")["completed_stages"])

    # -- shots ------------------------------------------------------------- #
    def test_08_shot_add_creates_registry_entries(self):
        res = self.run_cli("shot-add", "SC01", "--count", "3")
        self.assertEqual(res.returncode, 0, res.stderr)
        reg = self.read("SHOT_REGISTRY.json")
        self.assertEqual([s["shot_id"] for s in reg["shots"]],
                         ["SC01_SH001", "SC01_SH002", "SC01_SH003"])
        state = self.read("PROJECT_STATE.json")
        self.assertEqual(state["counters"]["shots_planned"], 3)
        self.assertEqual(self.run_cli("validate").returncode, 0)

    def test_09_shot_add_rejects_bad_scene_id(self):
        self.assertEqual(self.run_cli("shot-add", "SC1", "--count", "1").returncode, 1)

    def test_10_shot_becomes_verified_only_when_all_slots_done(self):
        self.run_cli("shot-add", "SC01", "--count", "1")
        for slot in ["story", "assets", "animation", "camera", "lighting", "audio", "render"]:
            self.run_cli("shot-set", "SC01_SH001", "--stage", slot, "--status", "VERIFIED")
        reg = self.read("SHOT_REGISTRY.json")
        self.assertNotEqual(reg["shots"][0]["overall_status"], "VERIFIED",
                            "shot must not verify while QC is still open")
        self.run_cli("shot-set", "SC01_SH001", "--stage", "QC", "--status", "VERIFIED")
        reg = self.read("SHOT_REGISTRY.json")
        self.assertEqual(reg["shots"][0]["overall_status"], "VERIFIED")
        self.assertIn("SC01_SH001", self.read("PROJECT_STATE.json")["completed_shots"])

    def test_11_failed_shot_is_tracked(self):
        self.run_cli("shot-add", "SC02", "--count", "1")
        self.run_cli("shot-set", "SC02_SH001", "--stage", "render", "--status", "FAILED",
                     "--error", "scene render exited 1")
        state = self.read("PROJECT_STATE.json")
        self.assertIn("SC02_SH001", state["failed_shots"])
        self.assertNotIn("SC02_SH001", state["completed_shots"])

    # -- render lifecycle -------------------------------------------------- #
    def test_12_scene_lifecycle_is_strictly_ordered(self):
        self.run_cli("scene-add", "SC01", "--title", "Cold open")
        res = self.run_cli("scene-set", "SC01", "--lifecycle", "PREVIEW",
                           "--status", "VERIFIED")
        self.assertEqual(res.returncode, 1,
                         "PREVIEW must be refused before SCENE is verified")
        self.assertIn("strictly ordered", res.stderr)

    def test_13_scene_reaches_verified_and_syncs_state(self):
        self.run_cli("scene-add", "SC01")
        for step in ["SCENE", "PREVIEW", "QC", "FINAL_RENDER", "VERIFY"]:
            res = self.run_cli("scene-set", "SC01", "--lifecycle", step,
                               "--status", "VERIFIED")
            self.assertEqual(res.returncode, 0, res.stderr)
        state = self.read("PROJECT_STATE.json")
        self.assertEqual(state["rendered_scenes"], ["SC01"])
        self.assertEqual(state["verified_scenes"], ["SC01"])
        self.assertEqual(self.read("13_RENDER/RENDER_MANIFEST.json")
                         ["scenes"][0]["overall_status"], "VERIFIED")
        self.assertEqual(self.run_cli("validate").returncode, 0)

    def test_14_failed_scene_can_be_retried_alone(self):
        self.run_cli("scene-add", "SC01")
        self.run_cli("scene-add", "SC02")
        for step in ["SCENE", "PREVIEW", "QC", "FINAL_RENDER", "VERIFY"]:
            self.run_cli("scene-set", "SC01", "--lifecycle", step, "--status", "VERIFIED")
        self.run_cli("scene-set", "SC02", "--lifecycle", "SCENE", "--status", "VERIFIED")
        self.run_cli("scene-set", "SC02", "--lifecycle", "PREVIEW", "--status", "FAILED",
                     "--error", "timeout after 900s")
        state = self.read("PROJECT_STATE.json")
        self.assertEqual(state["verified_scenes"], ["SC01"],
                         "SC01 verification must survive SC02 failing")
        # rerender SC02 alone
        for step in ["PREVIEW", "QC", "FINAL_RENDER", "VERIFY"]:
            self.run_cli("scene-set", "SC02", "--lifecycle", step, "--status", "VERIFIED")
        self.assertEqual(sorted(self.read("PROJECT_STATE.json")["verified_scenes"]),
                         ["SC01", "SC02"])

    # -- errors / checkpoints --------------------------------------------- #
    def test_15_log_error_records_and_marks_failed(self):
        res = self.run_cli("log-error", "--task-id", "T05_3D_ASSETS",
                           "--classification", "TOOL_ABSENT",
                           "--command", "blender --version",
                           "--error-text", "blender: command not found",
                           "--cause", "Blender not installed",
                           "--preserved", "03/04/05 outputs",
                           "--recovery", "python_software_raster fallback",
                           "--mark-failed")
        self.assertEqual(res.returncode, 0, res.stderr)
        log = self.read("ERROR_LOG.json")
        self.assertEqual(log["errors"][0]["error_id"], "ERR-0001")
        self.assertEqual(log["errors"][0]["classification"], "TOOL_ABSENT")
        queue = self.read("TASK_QUEUE.json")
        task = next(t for t in queue["tasks"] if t["task_id"] == "T05_3D_ASSETS")
        self.assertEqual(task["status"], "FAILED")
        self.assertEqual(task["retry_count"], 1)
        self.assertIn("T05_3D_ASSETS", self.read("PROJECT_STATE.json")["failed_tasks"])
        self.assertEqual(self.run_cli("validate").returncode, 0)

    def test_16_log_error_rejects_bad_classification(self):
        res = self.run_cli("log-error", "--task-id", "T01_DEVELOPMENT",
                           "--classification", "MYSTERY", "--error-text", "x")
        self.assertEqual(res.returncode, 1)

    def test_17_checkpoint_appends_changelog_and_state(self):
        res = self.run_cli("checkpoint", "--task-id", "T01_DEVELOPMENT",
                           "--summary", "premise locked")
        self.assertEqual(res.returncode, 0, res.stderr)
        state = self.read("PROJECT_STATE.json")
        self.assertEqual(state["counters"]["checkpoints"], 2)
        self.assertEqual(state["last_checkpoint"]["checkpoint_id"], "CP-0002")
        queue = self.read("TASK_QUEUE.json")
        self.assertEqual(next(t for t in queue["tasks"]
                              if t["task_id"] == "T01_DEVELOPMENT")["checkpoint"], "CP-0002")
        with open(os.path.join(self.tmp, "CHANGELOG.md"), encoding="utf-8") as fh:
            self.assertIn("CP-0002", fh.read())

    # -- completion gate --------------------------------------------------- #
    def test_18_verify_final_fails_without_mp4(self):
        res = self.run_cli("verify-final")
        self.assertEqual(res.returncode, 1)
        self.assertEqual(self.read("PROJECT_STATE.json")["overall_status"], "NOT_STARTED")
        self.assertEqual(self.read("12_QC/reports/FINAL_VERIFICATION.json")["result"], "FAIL")

    def test_19_completion_is_refused_without_a_verified_file(self):
        self.run_cli("task-set", "T12_FINAL_RENDER", "--status", "VERIFIED")
        state_before = self.read("PROJECT_STATE.json")
        self.assertNotEqual(state_before["overall_status"], "COMPLETE")
        res = self.run_cli("verify-final")
        self.assertEqual(res.returncode, 1)
        self.assertNotEqual(self.read("PROJECT_STATE.json")["overall_status"], "COMPLETE",
                            "no COMPLETE without a real verified MP4")

    def test_20_probe_reads_synthetic_mp4(self):
        build_mp4(os.path.join(self.tmp, "13_RENDER", "previews", "SC01_preview.mp4"),
                  seconds=30.0)
        res = self.run_cli("probe", "13_RENDER/previews/SC01_preview.mp4")
        self.assertEqual(res.returncode, 0, res.stderr)
        info = json.loads(res.stdout)
        self.assertTrue(info["has_video"] and info["has_audio"])
        self.assertAlmostEqual(info["duration_seconds"], 30.0, places=2)
        self.assertTrue(info["faststart"])

    def test_21_verify_final_passes_and_completes_project(self):
        build_mp4(os.path.join(self.tmp, "FINAL", "FINAL_FILM.mp4"),
                  seconds=300.0, w=1920, h=1080)
        res = self.run_cli("verify-final")
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("FINAL VERIFICATION: PASS", res.stdout)
        state = self.read("PROJECT_STATE.json")
        self.assertEqual(state["overall_status"], "COMPLETE")
        self.assertEqual(state["final_mp4_status"], "VERIFIED")
        self.assertTrue(state["final_mp4"]["verified"])
        self.assertTrue(state["final_mp4"]["sha256"])
        self.assertEqual(self.run_cli("validate").returncode, 0)

    def test_22_verify_final_rejects_out_of_spec_render(self):
        build_mp4(os.path.join(self.tmp, "FINAL", "FINAL_FILM.mp4"),
                  seconds=45.0, w=1280, h=720)
        res = self.run_cli("verify-final")
        self.assertEqual(res.returncode, 1)
        report = self.read("12_QC/reports/FINAL_VERIFICATION.json")
        self.assertEqual(report["result"], "FAIL")
        failed = {c["check"] for c in report["checks"] if not c["pass"]}
        self.assertIn("duration_in_range", failed)
        self.assertIn("resolution_1920x1080", failed)
        self.assertNotEqual(self.read("PROJECT_STATE.json")["overall_status"], "COMPLETE")

    def test_23_corrupt_state_is_detected(self):
        path = os.path.join(self.tmp, "TASK_QUEUE.json")
        data = self.read("TASK_QUEUE.json")
        data["tasks"][1]["dependencies"] = ["T99_GHOST"]
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh)
        res = self.run_cli("validate")
        self.assertEqual(res.returncode, 1)
        self.assertIn("unknown task T99_GHOST", res.stdout)

    def test_24_dependency_cycle_is_detected(self):
        path = os.path.join(self.tmp, "TASK_QUEUE.json")
        data = self.read("TASK_QUEUE.json")
        by_id = {t["task_id"]: t for t in data["tasks"]}
        by_id["T01_DEVELOPMENT"]["dependencies"] = ["T02_SCREENPLAY"]
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh)
        res = self.run_cli("validate")
        self.assertEqual(res.returncode, 1)
        self.assertIn("cycle", res.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
