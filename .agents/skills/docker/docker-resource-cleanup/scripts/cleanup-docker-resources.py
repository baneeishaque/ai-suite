#!/usr/bin/env python3
"""Clean up Docker resources with stop-before-remove discipline (composer).

Tier 1 (Python) per scripting-language-selection-rules.md Section 3: subprocess
orchestration plus JSON consumption; standard library only.

Composes the base primitive
`docker-resource-inventory/scripts/inventory-docker-resources.py` (resolved via
a relative path anchored on THIS script's own location, never the caller's
cwd) at two points:

1. PRE-FLIGHT — a deterministic inventory report before any mutation.
2. POST-CLEANUP — a deterministic verification inventory compared against the
   per-scope expected state.

Encodes the six industrial lessons of the originating session:

- L1 inspect before acting (pre-flight inventory is mandatory)
- L3 stop running containers BEFORE removal; each docker command is one
  subprocess — destructive docker commands are NEVER chained in one shell call
- L4 `docker system prune` never removes running containers — explicit
  `docker stop` + `docker rm` are required for a full cleanup
- L5 `docker volume prune -f` can report 0 B reclaimed while dangling volumes
  survive — an explicit survivor sweep (`docker volume ls` + per-volume
  `docker volume rm`, tolerating in-use refusals) runs after every prune
- L6 final verification via the base inventory; per-scope expected state

Exit codes:
  0  success (cleanup complete and verification passed)
  1  invalid scope / base inventory script missing
  2  docker CLI binary not found
  3  Docker daemon unreachable
  4  verification mismatch (post-cleanup inventory violates the per-scope
     expected state)
  5  a docker command failed mid-cleanup (cleanup aborted)
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

DOCKER_TIMEOUT_SECONDS = 120
SCRIPT_DIR = Path(__file__).resolve().parent
BASE_INVENTORY_SCRIPT = (
    SCRIPT_DIR.parent.parent
    / "docker-resource-inventory"
    / "scripts"
    / "inventory-docker-resources.py"
)

SCOPES = ("full", "keep-running", "unused")

EXPECTED_ZERO = ("containers_total", "images", "volumes", "build_cache_entries")


def _fail(message: str, code: int) -> int:
    print(f"cleanup-docker-resources: {message}", file=sys.stderr)
    return code


def _run(docker_bin: str, args: List[str]) -> subprocess.CompletedProcess:
    """Run one docker command; raises RuntimeError on non-zero exit."""
    result = subprocess.run(
        [docker_bin, *args],
        capture_output=True,
        text=True,
        timeout=DOCKER_TIMEOUT_SECONDS,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "no output"
        raise RuntimeError(f"docker {' '.join(args)} failed: {detail}")
    return result


def _run_inventory() -> Tuple[int, Dict[str, Any]]:
    """Invoke the base inventory script; returns (exit_code, document).

    -1 means the base script itself is missing (composer packaging error).
    """
    if not BASE_INVENTORY_SCRIPT.is_file():
        return -1, {}
    result = subprocess.run(
        [sys.executable, str(BASE_INVENTORY_SCRIPT), "--format", "json"],
        capture_output=True,
        text=True,
        timeout=DOCKER_TIMEOUT_SECONDS,
        check=False,
    )
    if result.returncode != 0:
        return result.returncode, {}
    try:
        return 0, json.loads(result.stdout)
    except json.JSONDecodeError:
        return 3, {}


def _volume_names(docker_bin: str) -> List[str]:
    output = _run(docker_bin, ["volume", "ls", "--format", "{{.Name}}"]).stdout
    return [line.strip() for line in output.splitlines() if line.strip()]


def _reclaimable_bytes(document: Dict[str, Any]) -> int:
    return sum(row.get("reclaimable_bytes", 0) for row in document.get("df", []))


def _plan_for_scope(scope: str, docker_bin: str, before: Dict[str, Any]) -> List[Tuple[str, List[str]]]:
    """Build the ordered (step_label, docker_argv) plan for the scope."""
    containers = before.get("containers", [])
    running = [c["name"] for c in containers if c.get("state") == "running"]
    all_names = [c["name"] for c in containers]

    plan: List[Tuple[str, List[str]]] = []

    if scope == "full":
        for name in running:
            plan.append((f"stop running container {name}", ["stop", name]))
        for name in all_names:
            plan.append((f"remove container {name}", ["rm", name]))
        plan.append(("prune dangling volumes", ["volume", "prune", "-f"]))
        plan.append(("survivor sweep (remove listed volumes; in-use refusals are expected)", ["volume", "ls"]))
        plan.append(("prune unused images + build cache + stopped containers", ["system", "prune", "-a", "-f"]))
    elif scope == "keep-running":
        plan.append(("prune stopped containers", ["container", "prune", "-f"]))
        plan.append(("prune dangling volumes", ["volume", "prune", "-f"]))
        plan.append(("survivor sweep (remove listed volumes; in-use refusals are expected)", ["volume", "ls"]))
        plan.append(("prune unused images + build cache", ["system", "prune", "-a", "-f"]))
    else:  # unused
        plan.append(("prune stopped containers + unused images + build cache", ["system", "prune", "-a", "-f"]))
    return plan


def _verify_scope(scope: str, after: Dict[str, Any]) -> List[str]:
    """Return a list of violations of the per-scope expected end state."""
    summary = after.get("summary", {})
    violations: List[str] = []
    if scope == "full":
        for key in EXPECTED_ZERO:
            if summary.get(key, -1) != 0:
                violations.append(f"{key} = {summary.get(key)} (expected 0)")
    elif scope in ("keep-running", "unused"):
        total = summary.get("containers_total", -1)
        running = summary.get("containers_running", -1)
        if total != running:
            violations.append(f"stopped containers remain: total={total}, running={running}")
        if summary.get("build_cache_entries", -1) != 0:
            violations.append(f"build_cache_entries = {summary.get('build_cache_entries')} (expected 0)")
    return violations


def _print_report(before: Dict[str, Any], after: Dict[str, Any], reclaimed_bytes: int) -> None:
    before_summary = before.get("summary", {})
    after_summary = after.get("summary", {})
    print("Cleanup complete.")
    print(f"  reclaimed: {reclaimed_bytes} bytes")
    print("  before: " + ", ".join(f"{k}={v}" for k, v in before_summary.items()))
    print("  after:  " + ", ".join(f"{k}={v}" for k, v in after_summary.items()))


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Clean up Docker resources (containers, images, volumes, build cache) with stop-before-remove discipline."
    )
    parser.add_argument("--scope", choices=SCOPES, required=True, help="full = stop+remove everything; keep-running = everything except running containers; unused = docker system prune -a only")
    parser.add_argument("--dry-run", action="store_true", help="print the ordered execution plan without mutating anything")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        if exc.code == 2:
            return _fail("invalid arguments (see usage above)", 1)
        raise

    docker_bin = shutil.which("docker")
    if not docker_bin:
        return _fail("docker CLI not found in PATH", 2)

    exit_code, before = _run_inventory()
    if exit_code != 0:
        if exit_code == -1:
            return _fail(f"base inventory script missing: {BASE_INVENTORY_SCRIPT}", 1)
        mapping = {1: 2, 2: 3}
        return _fail(f"pre-flight inventory failed (base exit {exit_code})", mapping.get(exit_code, 5))
    before_summary = before.get("summary", {})

    plan = _plan_for_scope(args.scope, docker_bin, before)

    if args.dry_run:
        print(f"DRY-RUN — {args.scope} scope; no mutations performed.")
        print(f"Pre-flight: " + ", ".join(f"{k}={v}" for k, v in before_summary.items()))
        for index, (label, argv_cmd) in enumerate(plan, start=1):
            command = " ".join(argv_cmd) if argv_cmd[0] != "volume" or len(argv_cmd) > 2 else "volume ls --format '{{.Name}}'"
            print(f"  [{index}/{len(plan)}] {label}: docker {command}")
        return 0

    try:
        for index, (label, argv_cmd) in enumerate(plan, start=1):
            print(f"[{index}/{len(plan)}] {label} ...", flush=True)
            if argv_cmd[:2] == ["volume", "ls"]:
                for name in _volume_names(docker_bin):
                    try:
                        _run(docker_bin, ["volume", "rm", name])
                    except RuntimeError as error:
                        print(f"  (expected) volume {name} not removed: {error}", file=sys.stderr)
                continue
            _run(docker_bin, argv_cmd)
    except RuntimeError as error:
        return _fail(str(error), 5)
    except subprocess.TimeoutExpired:
        return _fail("docker subcommand timed out mid-cleanup", 5)

    exit_code, after = _run_inventory()
    if exit_code != 0:
        return _fail(f"post-cleanup verification inventory failed (base exit {exit_code})", 5)

    violations = _verify_scope(args.scope, after)
    if violations:
        for violation in violations:
            print(f"  VERIFICATION MISMATCH: {violation}", file=sys.stderr)
        return _fail("post-cleanup verification failed", 4)

    reclaimed = _reclaimable_bytes(before) - _reclaimable_bytes(after)
    _print_report(before, after, max(reclaimed, 0))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
