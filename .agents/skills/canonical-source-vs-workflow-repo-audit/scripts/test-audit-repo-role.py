#!/usr/bin/env python3
"""CLI regressions for repository-role file and directory inputs.

Tier 1 (Python 3.12+) per Scripting Language Selection Rules §§3–5:
stdlib subprocess tests; all generated repositories stay in TEST_ARTIFACT_DIR.
No fixtures are deleted and no user repository commits or config are modified.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "audit-repo-role.py"


class RepoRoleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        parent = Path(os.environ["TEST_ARTIFACT_DIR"]).resolve()
        if not parent.is_dir():
            raise RuntimeError("TEST_ARTIFACT_DIR must be an existing task-owned directory")
        cls.root = Path(tempfile.mkdtemp(prefix="repo-role-", dir=parent))
        cls.repo = cls.make_repo(cls.root / "repo with spaces")

    @classmethod
    def make_repo(cls, path):
        path.mkdir()
        subprocess.run(["git", "init", "--quiet", str(path)], check=True, capture_output=True, timeout=15)
        (path / "package.json").write_bytes((HERE / "repo-role-manifest.json.template").read_bytes())
        return path

    def run_audit(self, path=None, cwd=None, env=None):
        command = [sys.executable, str(SCRIPT), "--json"]
        if path is not None:
            command.append(str(path))
        return subprocess.run(
            command, cwd=cwd or self.root, env=env, capture_output=True,
            text=True, timeout=15, check=False,
        )

    def verdict(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        return json.loads(result.stdout)

    def test_file_and_directory_have_identical_classification(self):
        directory = self.verdict(self.run_audit(self.repo))
        file = self.verdict(self.run_audit(self.repo / "package.json"))
        self.assertEqual(file, directory)
        self.assertEqual(file["root"], str(self.repo.resolve()))
        self.assertEqual(file["verdict"], "canonical")
        self.assertEqual(file["signals"], {"workflow": 0, "canonical": 2, "mirror": 0})

    def test_relative_file_and_default_directory(self):
        file = self.verdict(self.run_audit("package.json", cwd=self.repo))
        directory = self.verdict(self.run_audit(cwd=self.repo))
        self.assertEqual(file, directory)

    def test_nested_repository_uses_closest_root(self):
        nested = self.make_repo(self.repo / "nested repository")
        result = self.verdict(self.run_audit(nested / "package.json"))
        self.assertEqual(result["root"], str(nested.resolve()))
        self.assertNotEqual(result["root"], str(self.repo.resolve()))

    def test_missing_path_is_rejected_without_creation(self):
        missing = self.repo / "missing.json"
        result = self.run_audit(missing)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("not an existing file or directory", result.stderr)
        self.assertFalse(missing.exists())

    def test_non_repository_directory_and_file_are_rejected(self):
        # The task scratch directory may itself be inside the host repository.
        # A ceiling bounds discovery to this fixture without modifying Git config.
        plain = self.root / "not a repository"
        plain.mkdir()
        file = plain / "package.json"
        file.write_bytes((HERE / "repo-role-manifest.json.template").read_bytes())
        env = dict(os.environ, GIT_CEILING_DIRECTORIES=str(self.root))
        for path in (plain, file):
            with self.subTest(path=path):
                result = self.run_audit(path, env=env)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertIn("not in a Git repo", result.stderr)

    def test_broken_symlink_is_rejected(self):
        link = self.repo / "broken-link"
        link.symlink_to(self.repo / "absent-target")
        result = self.run_audit(link)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")

    def test_audit_leaves_repository_state_unchanged(self):
        command = ["git", "-C", str(self.repo), "status", "--porcelain=v1", "-z", "--untracked-files=all"]
        before = subprocess.check_output(command, timeout=15)
        self.verdict(self.run_audit(self.repo / "package.json"))
        self.assertEqual(subprocess.check_output(command, timeout=15), before)


if __name__ == "__main__":
    unittest.main()
