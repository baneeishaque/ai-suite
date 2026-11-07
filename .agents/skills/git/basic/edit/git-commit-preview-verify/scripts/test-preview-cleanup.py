#!/usr/bin/env python3
"""Regression checks for preview verification and recoverable cleanup.

Tier 1 (Python 3.12+) per Scripting Language Selection Rules §§3–5:
stdlib CLI tests with mocked disposal; fixtures remain in TEST_ARTIFACT_DIR.
No real preview, Trash, or repository history is modified.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("preview_verify", HERE / "verify-commit-preview.py")
assert SPEC and SPEC.loader
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)
TITLE = "docs(test): verify preview lifecycle"


class PreviewCleanupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parent = Path(os.environ["TEST_ARTIFACT_DIR"]).resolve()
        if not parent.is_dir():
            raise RuntimeError("TEST_ARTIFACT_DIR must be an existing task-owned directory")
        cls.root = Path(tempfile.mkdtemp(prefix="preview-cleanup-", dir=parent))

    def setUp(self):
        self.directory = self.root / self._testMethodName
        self.directory.mkdir()
        self.repo = self.directory / "repo with spaces"
        (self.repo / ".git").mkdir(parents=True)
        self.preview = self.directory / "commit preview.md"
        self.content = (HERE / "preview-cleanup-fixture.md.template").read_bytes()
        self.preview.write_bytes(self.content)

    def invoke(self, *flags, logs=None, preview=None):
        output, errors = io.StringIO(), io.StringIO()
        argv = [
            "verify-commit-preview.py", "--repo", str(self.repo),
            "--preview", str(preview or self.preview), "--format", "json", *flags,
        ]
        with (
            mock.patch.object(sys, "argv", argv),
            mock.patch.object(VERIFY, "run_git_log", return_value=logs if logs is not None else [f"abc1234 {TITLE}"]),
            contextlib.redirect_stdout(output),
            contextlib.redirect_stderr(errors),
        ):
            code = VERIFY.main()
        return code, json.loads(output.getvalue()), errors.getvalue()

    def moved_result(self, command, **kwargs):
        self.preview.rename(self.directory / "retired-preview.md")
        return subprocess.CompletedProcess(
            command, 0,
            json.dumps({"path": str(self.preview), "status": "removed", "message": "fixture move"}),
            "",
        )

    def test_default_is_read_only(self):
        with mock.patch.object(VERIFY, "cleanup_preview") as cleanup:
            code, report, errors = self.invoke()
        self.assertEqual(code, 0)
        self.assertEqual(report["done"], 1)
        self.assertNotIn("cleanup", report)
        self.assertEqual(errors, "")
        cleanup.assert_not_called()
        self.assertEqual(self.preview.read_bytes(), self.content)

    def test_pending_refuses_cleanup(self):
        with mock.patch.object(VERIFY, "cleanup_preview") as cleanup:
            code, report, errors = self.invoke("--cleanup", logs=[])
        self.assertEqual(code, 1)
        self.assertEqual(report["cleanup"]["status"], "refused")
        self.assertIn("pending commits", errors)
        cleanup.assert_not_called()
        self.assertEqual(self.preview.read_bytes(), self.content)

    def test_success_delegates_to_existing_base(self):
        with (
            mock.patch.object(sys, "platform", "darwin"),
            mock.patch.object(VERIFY.shutil, "which", return_value="/fixture/trash"),
            mock.patch.object(VERIFY.subprocess, "run", side_effect=self.moved_result) as run,
        ):
            code, report, errors = self.invoke("--cleanup")
        self.assertEqual((code, errors), (0, ""))
        self.assertEqual(report["cleanup"]["status"], "removed")
        self.assertFalse(self.preview.exists())
        self.assertEqual((self.directory / "retired-preview.md").read_bytes(), self.content)
        command = run.call_args.args[0]
        self.assertEqual(command, [sys.executable, str(VERIFY.CLEANUP_SCRIPT), str(self.preview), "--json"])
        self.assertTrue(VERIFY.CLEANUP_SCRIPT.is_absolute())
        self.assertTrue(VERIFY.CLEANUP_SCRIPT.is_file())
        self.assertEqual(run.call_args.kwargs["timeout"], 30)

    def test_relative_preview_from_different_cwd(self):
        previous = Path.cwd()
        try:
            os.chdir(self.directory)
            with (
                mock.patch.object(VERIFY.shutil, "which", return_value="/fixture/trash"),
                mock.patch.object(VERIFY.subprocess, "run", side_effect=self.moved_result) as run,
            ):
                code, report, _ = self.invoke("--cleanup", preview=Path(self.preview.name))
            self.assertEqual(code, 0)
            self.assertEqual(report["cleanup"]["status"], "removed")
            self.assertEqual(run.call_args.args[0][2], str(self.preview))
        finally:
            os.chdir(previous)

    def test_missing_helper_fails_without_disposal(self):
        with (
            mock.patch.object(VERIFY, "CLEANUP_SCRIPT", self.directory / "missing.py"),
            mock.patch.object(VERIFY.subprocess, "run") as run,
        ):
            code, report, errors = self.invoke("--cleanup")
        self.assertEqual(code, 5)
        self.assertEqual(report["cleanup"]["status"], "failed")
        self.assertIn("helper not found", errors)
        run.assert_not_called()
        self.assertEqual(self.preview.read_bytes(), self.content)

    def test_macos_missing_trash_fails_closed(self):
        with (
            mock.patch.object(sys, "platform", "darwin"),
            mock.patch.object(VERIFY.shutil, "which", return_value=None),
            mock.patch.object(VERIFY.subprocess, "run") as run,
        ):
            code, report, errors = self.invoke("--cleanup")
        self.assertEqual(code, 5)
        self.assertEqual(report["cleanup"]["status"], "failed")
        self.assertIn("Trash is unavailable", errors)
        run.assert_not_called()
        self.assertEqual(self.preview.read_bytes(), self.content)

    def test_helper_nonzero_propagates_failure(self):
        result = subprocess.CompletedProcess([], 1, "", "trash refused")
        with (
            mock.patch.object(VERIFY.shutil, "which", return_value="/fixture/trash"),
            mock.patch.object(VERIFY.subprocess, "run", return_value=result),
        ):
            code, report, errors = self.invoke("--cleanup")
        self.assertEqual(code, 5)
        self.assertEqual(report["cleanup"]["status"], "failed")
        self.assertIn("trash refused", errors)
        self.assertEqual(self.preview.read_bytes(), self.content)

    def test_malformed_skipped_and_false_success_are_failures(self):
        for output in ("not JSON", "[]", '{"status":"skipped"}', '{"status":"removed"}'):
            with (
                self.subTest(output=output),
                mock.patch.object(VERIFY.shutil, "which", return_value="/fixture/trash"),
                mock.patch.object(VERIFY.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, output, "")),
            ):
                code, report, _ = self.invoke("--cleanup")
                self.assertEqual(code, 5)
                self.assertEqual(report["cleanup"]["status"], "failed")
                self.assertEqual(self.preview.read_bytes(), self.content)

    def test_timeout_and_spawn_error_are_reported(self):
        for failure in (subprocess.TimeoutExpired("cleanup", 30), OSError("cannot start cleanup")):
            with (
                self.subTest(failure=type(failure).__name__),
                mock.patch.object(VERIFY.shutil, "which", return_value="/fixture/trash"),
                mock.patch.object(VERIFY.subprocess, "run", side_effect=failure),
            ):
                code, report, _ = self.invoke("--cleanup")
                self.assertEqual(code, 5)
                self.assertEqual(report["cleanup"]["status"], "failed")
                self.assertEqual(self.preview.read_bytes(), self.content)


if __name__ == "__main__":
    unittest.main()
