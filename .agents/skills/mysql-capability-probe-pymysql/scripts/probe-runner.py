#!/usr/bin/env python3
"""
probe-runner.py
===============

Orchestrates a PyMySQL probe end-to-end:

1. Resolves the mise-installed Python via DIRECT install path (no
   ``mise exec`` cascade — see ``mise-tool-management`` Layer 5).
2. Idempotently installs ``pymysql`` into that Python (``--user``).
3. Ensures ``<repo-root>/scratch/`` exists and is gitignored
   (see ``repo-scratch-output-capture``).
4. Runs the named probe script with ``--secrets <path>``, redirecting
   stdout/stderr to ``scratch/<probe-name>.out|err``.

Usage
-----
    python3 probe-runner.py --probe <probe-script.py> --secrets <act.secrets-path> [--name <slug>]

Defaults
--------
    --name = basename of probe script minus .py

Exit codes
----------
Forwards the probe's exit code (0 supported, 1 not, 2 config).

Tier
----
Tier-1 (Python) per ``scripting-language-selection-rules.md`` — filesystem
walk, semver-aware version sort, subprocess orchestration. Ported from
``probe-runner.sh`` per ``script-language-tier-port``.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

MISE_PY_ROOT = Path.home() / ".local" / "share" / "mise" / "installs" / "python"
SCRATCH_HELPER = (
    Path(__file__).resolve().parent.parent.parent
    / "repo-scratch-output-capture"
    / "scripts"
    / "ensure-scratch-gitignored.py"
)


def die(msg: str, code: int = 2) -> "None":
    print(f"[probe-runner] {msg}", file=sys.stderr)
    sys.exit(code)


def _version_key(name: str) -> tuple:
    return tuple(int(p) if p.isdigit() else p for p in re.split(r"(\d+)", name))


def resolve_mise_python() -> tuple[Path, Path]:
    if not MISE_PY_ROOT.is_dir():
        die(
            f"ERROR: no mise python installs at {MISE_PY_ROOT}\n"
            "[probe-runner] See mise-tool-management Layer 3 (Mise Python Setup).",
            2,
        )
    versions = sorted((p.name for p in MISE_PY_ROOT.iterdir() if p.is_dir()), key=_version_key)
    if not versions:
        die(f"ERROR: no mise python versions under {MISE_PY_ROOT}", 2)
    latest = versions[-1]
    py_bin = MISE_PY_ROOT / latest / "bin" / "python"
    pip_bin = MISE_PY_ROOT / latest / "bin" / "pip"
    if not os.access(py_bin, os.X_OK):
        die(f"no python binary at {py_bin}", 2)
    return py_bin, pip_bin


def git_repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        return Path(result.stdout.strip())
    return Path.cwd()


def ensure_pymysql(py_bin: Path, pip_bin: Path) -> None:
    check = subprocess.run([str(py_bin), "-c", "import pymysql"], capture_output=True)
    if check.returncode == 0:
        return
    repo = git_repo_root()
    scratch = repo / "scratch"
    scratch.mkdir(exist_ok=True)
    out_log = scratch / "pip-pymysql.out"
    err_log = scratch / "pip-pymysql.err"
    with out_log.open("wb") as out_fh, err_log.open("wb") as err_fh:
        rc = subprocess.run(
            [str(pip_bin), "install", "--user", "--quiet", "pymysql"],
            stdout=out_fh,
            stderr=err_fh,
        ).returncode
    if rc != 0:
        die(f"pip install pymysql failed; see {err_log}", 2)


def ensure_scratch() -> Path:
    if os.access(SCRATCH_HELPER, os.X_OK):
        result = subprocess.run(
            [sys.executable, str(SCRATCH_HELPER)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    repo = git_repo_root()
    scratch = repo / "scratch"
    scratch.mkdir(exist_ok=True)
    return scratch


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="PyMySQL probe orchestrator.")
    ap.add_argument("--probe", required=True)
    ap.add_argument("--secrets", required=True)
    ap.add_argument("--name", default="")
    args = ap.parse_args(argv)

    probe = Path(args.probe)
    secrets = Path(args.secrets)
    if not probe.is_file():
        die(f"probe script not found: {probe}", 2)
    if not secrets.is_file():
        die(f"secrets file not found: {secrets}", 2)

    name = args.name or probe.stem

    py_bin, pip_bin = resolve_mise_python()
    ensure_pymysql(py_bin, pip_bin)
    scratch = ensure_scratch()

    out_path = scratch / f"{name}.out"
    err_path = scratch / f"{name}.err"
    with out_path.open("wb") as out_fh, err_path.open("wb") as err_fh:
        rc = subprocess.run(
            [str(py_bin), str(probe), "--secrets", str(secrets)],
            stdout=out_fh,
            stderr=err_fh,
        ).returncode

    print(f"[probe-runner] exit={rc}  see {scratch}/{name}.{{out,err}}")
    print("--- verdict ---")
    try:
        sys.stdout.write(out_path.read_text(errors="ignore"))
    except OSError:
        pass
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
