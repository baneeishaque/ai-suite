#!/usr/bin/env python3
"""migrate-and-symlink.py — Phase 1–4 of the Tool Config Directory Symlink protocol.

Usage:
  python3 migrate-and-symlink.py --mapping-file <path>
  echo '<json>' | python3 migrate-and-symlink.py

Input JSON: array of {"source": str, "target": str} objects.
Exit codes: 0 success, 1 any failure.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Copy tool config directories to a repo and symlink back."
    )
    parser.add_argument(
        "--mapping-file",
        type=str,
        default=None,
        help="Path to JSON file containing the source→target mapping array.",
    )
    return parser.parse_args()


def load_mapping(path: str | None) -> list[dict[str, str]]:
    if path:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return json.load(sys.stdin)


def copy_verify_symlink(entry: dict[str, str]) -> None:
    src = entry["source"]
    tgt = entry["target"]

    # Phase 1 — Copy
    os.makedirs(tgt, exist_ok=True)
    result = subprocess.run(
        ["cp", "-a", f"{src}/.", f"{tgt}/"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"FAIL copy: {src} → {tgt}\n{result.stderr}", file=sys.stderr)
        sys.exit(1)
    print(f"OK  copy: {src} → {tgt}")

    # Phase 2 — Verify
    result = subprocess.run(
        ["diff", "-rq", f"{src}/", f"{tgt}/"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(
            f"FAIL verify: diff mismatch between {src} and {tgt}\n{result.stdout}",
            file=sys.stderr,
        )
        sys.exit(1)
    print(f"OK  verify: {src} == {tgt}")

    # Phase 3 — Delete source, create symlink
    shutil.rmtree(src)
    os.symlink(tgt, src)
    print(f"OK  symlink: {src} → {tgt}")

    # Phase 4 — Verify symlink
    resolved = os.readlink(src)
    if resolved != tgt:
        print(
            f"FAIL symlink verify: {src} resolves to {resolved}, expected {tgt}",
            file=sys.stderr,
        )
        sys.exit(1)
    print(f"OK  symlink verify: {src} → {resolved}")


def main() -> None:
    args = parse_args()
    mapping = load_mapping(args.mapping_file)

    for entry in mapping:
        src = entry.get("source")
        tgt = entry.get("target")
        if not src or not tgt:
            print(f"SKIP invalid entry: {entry}", file=sys.stderr)
            continue
        if not os.path.isdir(src):
            print(f"SKIP source not found: {src}", file=sys.stderr)
            continue
        copy_verify_symlink(entry)

    print("All migrations completed successfully.")


if __name__ == "__main__":
    main()
