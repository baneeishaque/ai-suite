#!/usr/bin/env python3
"""Git Blob Hash Engine — Compute git blob SHA-1 for files on disk.

A git blob object id is sha1("blob <length>\0<content>"), using the raw
working-tree bytes. This is identical to `git hash-object` output and to
the Software Heritage `cnt` object identifier. Domain-agnostic; used
by swh-content-link-mint and any content-addressable workflow.
"""

import argparse
import glob
import json
import os
import sys
from typing import Iterator, List, Optional, Tuple

SCRIPT_HASH_BLOB_HEADER = b"blob"


def compute_blob_sha1(data: bytes) -> str:
    """Return the git blob SHA-1 of raw bytes (sha1 of "blob <len>\\0<data>")."""
    header = SCRIPT_HASH_BLOB_HEADER + b" " + str(len(data)).encode("ascii") + b"\0"
    return __import__("hashlib").sha1(header + data).hexdigest()


def hash_file(path: str) -> str:
    """Read path as raw bytes and return its git blob SHA-1."""
    with open(path, "rb") as handle:
        return compute_blob_sha1(handle.read())


def iter_files(patterns: List[str], root: str) -> Iterator[Tuple[str, str]]:
    """Yield (absolute_path, display_path) for each pattern's matches."""
    seen = set()
    for pattern in patterns:
        full = os.path.join(root, pattern) if not os.path.isabs(pattern) else pattern
        matched = sorted(glob.glob(full, recursive=True))
        if not matched:
            continue
        for abspath in matched:
            if os.path.isdir(abspath):
                for dirpath, _dirs, files in os.walk(abspath):
                    for name in sorted(files):
                        fpath = os.path.join(dirpath, name)
                        if fpath not in seen:
                            seen.add(fpath)
                            rel = os.path.relpath(fpath, root)
                            yield fpath, rel
            else:
                if abspath not in seen:
                    seen.add(abspath)
                    rel = os.path.relpath(abspath, root)
                    yield abspath, rel


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Compute git blob SHA-1 for files (domain-agnostic)."
    )
    parser.add_argument("files", nargs="*", help="Files to hash.")
    parser.add_argument("--glob", action="append", default=[],
                        help="Glob patterns relative to --root (repeatable).")
    parser.add_argument("--root", default=".", help="Root for glob + relative output paths.")
    parser.add_argument("--json", action="store_true", help="JSON output.")
    parser.add_argument("--verify", metavar="SHA,FILE",
                        help="Assert FILE has blob hash SHA; exit 1 on mismatch.")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    """Entry point. Returns process exit code."""
    args = parse_args(argv)
    root = os.path.abspath(args.root)

    targets: List[Tuple[str, str]] = []
    for f in args.files:
        if os.path.isfile(f):
            targets.append((os.path.abspath(f), os.path.relpath(f, root)))
    for pattern in args.glob:
        for abspath, rel in iter_files([pattern], root):
            targets.append((abspath, rel))
    # --verify takes precedence: only the asserted file is checked.
    if args.verify:
        expected_sha, verify_file = args.verify.split(",", 1)
        expected_sha = expected_sha.strip()
        if not os.path.isfile(verify_file):
            print("error: verify target not a file: %s" % verify_file, file=sys.stderr)
            return 2
        actual = hash_file(verify_file)
        if actual != expected_sha:
            print("mismatch: %s expected %s got %s" % (verify_file, expected_sha, actual),
                  file=sys.stderr)
            return 1
        print("ok: %s == %s" % (verify_file, actual))
        return 0

    if not targets:
        print("error: no files matched (use positional files or --glob)", file=sys.stderr)
        return 2

    results: List[dict] = []
    exit_code = 0
    for abspath, rel in targets:
        try:
            sha = hash_file(abspath)
        except OSError as exc:
            print("error: cannot read %s: %s" % (rel, exc), file=sys.stderr)
            exit_code = 1
            continue
        results.append({"path": rel, "sha1": sha})
        if not args.json:
            print("%s\t%s" % (sha, rel))

    if args.json:
        print(json.dumps(results, indent=2))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
