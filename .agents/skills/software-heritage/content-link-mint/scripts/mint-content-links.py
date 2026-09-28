#!/usr/bin/env python3
"""Mint Software Heritage content (browse) links from local blob hashes.

A SWH `cnt` identifier IS the git blob SHA-1 ("blob <len>\\0<content>"), so
git hash-object output embeds directly. This composer delegates blob hashing
to git-blob-hash (compute-blob-sha1.py) and ingest confirmation to
content-ingestion-check (check-ingestion.py) via relative paths anchored on
this script's own location.

Per procedure, `;lines=` qualifiers are appended ONLY after ingest confirms
the content revision: --lines requires --verify (which checks ingestion via
content-ingestion-check) unless --force-lines is given.
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.parse
from typing import Any, Dict, List, Optional

BROWSE_BASE = "https://archive.softwareheritage.org"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BLOB_HASH_SCRIPT = os.path.abspath(os.path.join(
    SCRIPT_DIR, "../../../general/file/git-blob-hash/scripts/compute-blob-sha1.py"))
INGEST_CHECK_SCRIPT = os.path.abspath(os.path.join(
    SCRIPT_DIR, "../../../general/file/content-ingestion-check/scripts/check-ingestion.py"))


def run_base(script_path: str, args: List[str]) -> str:
    """Run a base-skill script, returning stdout. Exits with clear error if missing."""
    if not os.path.isfile(script_path):
        print("error: required base script not found: %s" % script_path,
              file=sys.stderr)
        sys.exit(2)
    proc = subprocess.run(
        [sys.executable, script_path] + args,
        capture_output=True, text=True)
    if proc.returncode != 0:
        print("error: %s failed: %s" % (os.path.basename(script_path),
                                        proc.stderr.strip()),
              file=sys.stderr)
        sys.exit(proc.returncode or 2)
    return proc.stdout


def hash_file(path: str, repo_root: str) -> str:
    """Hash a file via git-blob-hash base, return sha1_git."""
    out = run_base(BLOB_HASH_SCRIPT, ["--json", path])
    data = json.loads(out)
    return data[0]["sha1"]


def content_ingested(sha: str, timeout: float) -> bool:
    """Ask content-ingestion-check whether a blob is archived. True if KNOWN."""
    out = run_base(INGEST_CHECK_SCRIPT,
                   ["--hash", sha, "--timeout", str(timeout)])
    first_line = out.strip().splitlines()[0] if out.strip() else ""
    return first_line.startswith("KNOWN")


def mint_link(sha1_git: str, origin: str, relpath: str,
              lines: Optional[str]) -> str:
    """Assemble the canonical browse URL (qualifier order origin;path[;lines])."""
    path = urllib.parse.quote(relpath.replace(os.sep, "/"), safe="/")
    link = "%s/swh:1:cnt:%s;origin=%s;path=%s" % (
        BROWSE_BASE.rstrip("/"), sha1_git, origin, path)
    if lines:
        link += ";lines=%s" % lines
    return link


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Mint SWH content links from local file blob hashes.")
    parser.add_argument("files", nargs="+", help="Files to mint links for.")
    parser.add_argument("--origin", required=True,
                        help="SWH origin URL qualifier.")
    parser.add_argument("--repo-root", default=".",
                        help="Root the path= qualifier is relative to.")
    parser.add_argument("--verify", action="store_true",
                        help="Confirm each blob is ingested before emitting.")
    parser.add_argument("--lines", default=None, metavar="N[-M]",
                        help="Append ;lines= (requires --verify).")
    parser.add_argument("--force-lines", action="store_true",
                        help="Append ;lines= without ingest confirmation.")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--format", choices=["url", "markdown", "json"],
                        default="url")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    """Entry point. Returns process exit code."""
    args = parse_args(argv)
    if args.lines and not args.verify and not args.force_lines:
        print("error: --lines requires --verify (ingest must confirm the "
              "content first) or --force-lines", file=sys.stderr)
        return 2

    root = os.path.abspath(args.repo_root)
    results: List[Dict[str, Any]] = []
    failed = False
    for raw in args.files:
        abspath = os.path.abspath(raw)
        if not os.path.isfile(abspath):
            print("error: not a file: %s" % raw, file=sys.stderr)
            failed = True
            continue
        try:
            sha = hash_file(abspath, root)
        except Exception as exc:
            print("error: cannot hash %s: %s" % (raw, exc), file=sys.stderr)
            failed = True
            continue
        relpath = os.path.relpath(abspath, root)
        ingested: Optional[bool] = None
        if args.verify:
            ingested = content_ingested(sha, args.timeout)
            if not ingested:
                print("pending: %s blob %s not yet ingested; "
                      "emit link only after a successful Save + crawl" %
                      (relpath, sha), file=sys.stderr)
                failed = True
                continue
        link = mint_link(sha, args.origin, relpath,
                         args.lines if (args.verify or args.force_lines)
                         else None)
        results.append({"file": relpath, "sha1_git": sha,
                        "ingested": ingested, "link": link})

    if args.format == "json":
        print(json.dumps(results, indent=2))
    elif args.format == "markdown":
        for item in results:
            print("- [`%s`](%s)" % (item["file"], item["link"]))
    else:
        for item in results:
            print(item["link"])
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())