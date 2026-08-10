#!/usr/bin/env python3
"""Deterministic inventory of Docker resources (base primitive).

Tier 1 (Python) per scripting-language-selection-rules.md Section 3: subprocess
orchestration plus JSON serialization; standard library only, zero external
dependencies. Runs on any Python >= 3.10.

Emits a deterministic machine-readable JSON document (--format json, the
default and the stable contract consumed by composers) or a human-readable
text summary (--format text) of every Docker resource category:

- containers (running and stopped), with name, image, state and status
- images, with repository:tag and size
- volumes, with driver
- docker system df totals for every category (including Build Cache), with
  raw human sizes AND byte-precise size/reclaimable fields

Exit codes:
  0  success (including an empty inventory)
  1  docker CLI binary not found
  2  Docker daemon unreachable
  3  unexpected failure while invoking a docker subcommand
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from typing import Any, Dict, List

DOCKER_TIMEOUT_SECONDS = 30


def _fail(message: str, code: int) -> int:
    """Print a diagnostic on stderr and return the exit code."""
    print(f"inventory-docker-resources: {message}", file=sys.stderr)
    return code


def _run_docker(docker_bin: str, args: List[str]) -> subprocess.CompletedProcess:
    """Run one docker subcommand; raises RuntimeError on non-zero exit."""
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


def _parse_size_to_bytes(size_text: str) -> int:
    """Parse a docker human size (e.g. '244.9MB', '7.807GB', '0B') to bytes."""
    text = size_text.strip()
    if not text:
        return 0
    lowered = text.lower()
    units = {"b": 1, "kb": 1024, "mb": 1024**2, "gb": 1024**3, "tb": 1024**4}
    for unit, factor in units.items():
        if lowered.endswith(unit):
            number = lowered[: -len(unit)].strip()
            try:
                return int(round(float(number) * factor))
            except ValueError:
                return 0
    return 0


def _tsv_rows(output: str) -> List[List[str]]:
    """Parse tab-separated docker --format output into rows of cells."""
    rows: List[List[str]] = []
    for line in output.splitlines():
        if line.strip():
            rows.append([cell.strip() for cell in line.split("\t")])
    return rows


def _collect_containers(docker_bin: str) -> List[Dict[str, str]]:
    output = _run_docker(
        docker_bin,
        ["ps", "-a", "--format", "{{.ID}}\t{{.Names}}\t{{.Image}}\t{{.State}}\t{{.Status}}\t{{.Size}}"],
    ).stdout
    containers: List[Dict[str, str]] = []
    for row in _tsv_rows(output):
        if len(row) < 5:
            continue
        containers.append(
            {
                "id": row[0],
                "name": row[1],
                "image": row[2],
                "state": row[3],
                "status": row[4],
                "size": row[5] if len(row) > 5 else "",
            }
        )
    return containers


def _collect_images(docker_bin: str) -> List[Dict[str, str]]:
    output = _run_docker(
        docker_bin,
        ["images", "--format", "{{.ID}}\t{{.Repository}}:{{.Tag}}\t{{.Size}}"],
    ).stdout
    images: List[Dict[str, str]] = []
    for row in _tsv_rows(output):
        if len(row) < 2:
            continue
        images.append(
            {"id": row[0], "repo_tag": row[1], "size": row[2] if len(row) > 2 else ""}
        )
    return images


def _collect_volumes(docker_bin: str) -> List[Dict[str, str]]:
    output = _run_docker(
        docker_bin,
        ["volume", "ls", "--format", "{{.Name}}\t{{.Driver}}"],
    ).stdout
    volumes: List[Dict[str, str]] = []
    for row in _tsv_rows(output):
        if len(row) < 1 or not row[0]:
            continue
        volumes.append({"name": row[0], "driver": row[1] if len(row) > 1 else ""})
    return volumes


def _collect_df(docker_bin: str) -> List[Dict[str, Any]]:
    output = _run_docker(
        docker_bin,
        ["system", "df", "--format", "{{.Type}}\t{{.TotalCount}}\t{{.Active}}\t{{.Size}}\t{{.Reclaimable}}"],
    ).stdout
    rows: List[Dict[str, Any]] = []
    for row in _tsv_rows(output):
        if len(row) < 5:
            continue
        try:
            total = int(row[1])
            active = int(row[2])
        except ValueError:
            total, active = 0, 0
        rows.append(
            {
                "type": row[0],
                "total": total,
                "active": active,
                "size": row[3],
                "size_bytes": _parse_size_to_bytes(row[3]),
                "reclaimable": row[4],
                "reclaimable_bytes": _parse_size_to_bytes(row[4].split(" (")[0]),
            }
        )
    return rows


def _build_summary(containers: List[Dict[str, str]], images: List[Dict[str, str]], volumes: List[Dict[str, str]], df: List[Dict[str, Any]]) -> Dict[str, int]:
    running = sum(1 for c in containers if c["state"] == "running")
    build_cache_entries = 0
    for row in df:
        if "build" in row["type"].lower():
            build_cache_entries = row["total"]
    return {
        "containers_total": len(containers),
        "containers_running": running,
        "images": len(images),
        "volumes": len(volumes),
        "build_cache_entries": build_cache_entries,
    }


def _render_text(docker_cli_version: str, daemon_version: str, containers: List[Dict[str, str]], images: List[Dict[str, str]], volumes: List[Dict[str, str]], df: List[Dict[str, Any]], summary: Dict[str, int]) -> str:
    lines: List[str] = []
    lines.append("Docker resource inventory")
    lines.append(f"docker CLI: {docker_cli_version} | daemon: reachable ({daemon_version})")
    lines.append("")
    lines.append(f"CONTAINERS ({summary['containers_total']} total / {summary['containers_running']} running)")
    for c in containers:
        lines.append(f"  {c['name']}  {c['image']}  {c['state']}  {c['status']}  {c['size']}")
    lines.append("")
    lines.append(f"IMAGES ({summary['images']})")
    for image in images:
        lines.append(f"  {image['repo_tag']}  {image['size']}")
    lines.append("")
    lines.append(f"VOLUMES ({summary['volumes']})")
    for volume in volumes:
        lines.append(f"  {volume['name']}  {volume['driver']}")
    lines.append("")
    lines.append("DOCKER SYSTEM DF")
    for row in df:
        lines.append(f"  {row['type']:<14} {row['total']:>6} {row['active']:>6} {row['size']:>12} {row['reclaimable']:>14}")
    lines.append("")
    lines.append(
        "SUMMARY  "
        f"containers_total: {summary['containers_total']} | "
        f"containers_running: {summary['containers_running']} | "
        f"images: {summary['images']} | "
        f"volumes: {summary['volumes']} | "
        f"build_cache_entries: {summary['build_cache_entries']}"
    )
    return "\n".join(lines) + "\n"


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic inventory of Docker resources (containers, images, volumes, build cache)."
    )
    parser.add_argument("--format", choices=["json", "text"], default="json", help="json = machine contract (default), text = human summary")
    parser.add_argument("--docker", default=None, help="path to the docker binary (default: resolved via PATH)")
    args = parser.parse_args(argv)

    docker_bin = args.docker or shutil.which("docker")
    if not docker_bin:
        return _fail("docker CLI not found in PATH (install via system-wide-tool-management)", 1)

    try:
        daemon_version = _run_docker(docker_bin, ["version", "--format", "{{.Server.Version}}"]).stdout.strip()
    except RuntimeError:
        return _fail("Docker daemon unreachable — is the daemon running?", 2)
    if not daemon_version:
        return _fail("Docker daemon unreachable — is the daemon running?", 2)

    try:
        cli_version = _run_docker(docker_bin, ["version", "--format", "{{.Client.Version}}"]).stdout.strip()
        containers = _collect_containers(docker_bin)
        images = _collect_images(docker_bin)
        volumes = _collect_volumes(docker_bin)
        df = _collect_df(docker_bin)
    except RuntimeError as error:
        return _fail(str(error), 3)
    except subprocess.TimeoutExpired:
        return _fail("docker subcommand timed out", 3)

    summary = _build_summary(containers, images, volumes, df)

    if args.format == "text":
        print(_render_text(cli_version, daemon_version, containers, images, volumes, df, summary), end="")
        return 0

    document = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "docker_cli_version": cli_version,
        "daemon_reachable": True,
        "daemon_version": daemon_version,
        "containers": containers,
        "images": images,
        "volumes": volumes,
        "df": df,
        "summary": summary,
    }
    json.dump(document, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
