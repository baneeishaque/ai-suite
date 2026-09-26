#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, subprocess, sys
from pathlib import Path

REPO_ROOT_MARKER = ".git"

SCRIPT_DIR = Path(__file__).resolve().parent
# The skills live in the ai-suite repo; resolve the sibling base-skill script
# relative to this script's own location (.agents/skills/<layer>/<skill>/scripts).
RESOLVE_PY = SCRIPT_DIR.parents[1] / "general/file/scratch-artifact-naming/scripts/resolve-scratch-path.py"


def run(args: list[str], cwd: str, binary: bool = False) -> tuple[int, str | bytes]:
    try:
        r = subprocess.run(args, capture_output=True, cwd=cwd, timeout=120)
        out = r.stdout if binary else r.stdout.decode("utf-8", errors="replace").strip()
        return r.returncode, out
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, f"ERROR: {exc}"


def main() -> int:
    ap = argparse.ArgumentParser(description="Capture a repo file at any git ref into session-scoped scratch")
    ap.add_argument("--repo", required=True, help="Repo root (relative or absolute)")
    ap.add_argument("--ref", required=True, help="HEAD, stash@{0}, branch, tag, or commit SHA")
    ap.add_argument("--path", required=True, help="File path inside the repo (repo-root relative)")
    ap.add_argument("--purpose", required=True, help="Lowercase-kebab purpose slug")
    ap.add_argument("--session-id", help="Passthrough to scratch-artifact-naming (auto when omitted)")
    ap.add_argument("--force", action="store_true", help="Overwrite an existing artifact")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    if not (repo / REPO_ROOT_MARKER).is_dir() and not (repo / ".git").is_file():
        print(f"ERROR: not a git repo (no .git): {repo}", file=sys.stderr)
        return 1

    rc, full_sha = run(["git", "rev-parse", "--verify", f"{args.ref}^{{commit}}"], str(repo))
    if rc != 0 or not re.fullmatch(r"[0-9a-f]{40}", full_sha):
        print(f"ERROR: cannot resolve ref to a full commit SHA: {args.ref!r}", file=sys.stderr)
        return 1

    # Derive the ref slug: stash subject pre-first-colon lower-kebab, else the ref string lower-kebab
    ref_slug = None
    if args.ref.startswith("stash@"):
        rc2, stash_line = run(["git", "stash", "list", "--format=%H|%gs"], str(repo))
        if rc2 == 0:
            for line in stash_line.splitlines():
                if line.split("|", 1)[0].strip() == full_sha and "|" in line:
                    subject = line.split("|", 1)[1].strip()
                    if ":" in subject:
                        subject = subject.split(":", 1)[0].strip()
                    ref_slug = re.sub(r"[^a-z0-9]+", "-", subject.lower()).strip("-")
                    break
    if ref_slug is None:
        ref_slug = re.sub(r"[^a-z0-9]+", "-", args.ref.lower()).strip("-")
    if not ref_slug:
        print("ERROR: could not derive a ref slug", file=sys.stderr)
        return 1

    resolve_args = [
        sys.executable,
        str(RESOLVE_PY),
        "--repo",
        str(repo),
        "--purpose",
        args.purpose,
        "--ref-name",
        ref_slug,
        "--ref-sha",
        full_sha,
    ]
    if args.session_id:
        resolve_args += ["--session-id", args.session_id]
    rc, stem = run(resolve_args, str(repo))
    if rc != 0:
        print(f"ERROR: resolve-scratch-path failed: {stem}", file=sys.stderr)
        return 1

    rel = args.path.lstrip("./")
    rc, byte_count = run(["git", "cat-file", "-s", f"{args.ref}:{rel}"], str(repo))
    if rc != 0:
        print(f"ERROR: file not found at {args.ref}:{rel}", file=sys.stderr)
        return 1
    target = Path(stem.splitlines()[0])
    if target.exists() and not args.force:
        print(f"ERROR: artifact already exists: {target} (use --force to overwrite)", file=sys.stderr)
        return 1

    rc, content = run(["git", "show", f"{args.ref}:{rel}"], str(repo), binary=True)
    if rc != 0:
        print(f"ERROR: git show failed for {args.ref}:{rel}", file=sys.stderr)
        return 1
    target.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8", errors="surrogateescape"))

    actual = target.stat().st_size
    if actual != int(byte_count):
        print(f"ERROR: byte-count mismatch: wrote {actual} != {byte_count}", file=sys.stderr)
        return 1

    print(f"{target} | {full_sha} | {ref_slug}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
