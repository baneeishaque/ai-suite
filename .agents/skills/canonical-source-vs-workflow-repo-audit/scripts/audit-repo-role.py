#!/usr/bin/env python3
"""
audit-repo-role.py - Given any file or directory path inside a Git
working tree, classify the ENCLOSING repository as one of:

    canonical-source   - the authoritative source repo for an artifact
    workflow-backup    - a GitHub Actions / CI / mirror / backup repo
                         that runs jobs against / about the artifact
    mirror             - a read-only copy that should never be edited
    unknown            - heuristics inconclusive

Purpose: STOP the "edited the wrong repo" mistake BEFORE the edit.
Particularly common when a workflow/backup repo and a canonical source
repo share a domain name pattern (e.g. Account-Ledger-Server vs
Account-Ledger-Server-PHP).

Signals consulted (weighted):
    + .github/workflows/*.yml that ONLY dispatch / mirror / backup     -> workflow
    + Recent commit titles dominated by "backup:", "snapshot", "mirror"-> workflow
    + composer.json / package.json / pom.xml / go.mod / Cargo.toml /
      mise.toml / setup.py / pubspec.yaml at root                       -> canonical
    + presence of substantial source-tree dirs (src/, lib/, http_API/,
      app/, kotlin/, java/) with > N source files                       -> canonical
    + Repo description / README explicitly says "mirror of"             -> mirror

Inputs:
    <path>             positional; defaults to cwd
    --json             emit machine-readable verdict

Exit codes:
    0  verdict reported (any classification)
    2  path is not inside a Git working tree
"""
import argparse, json, os, subprocess, sys
from pathlib import Path

SOURCE_DIRS = ("src","lib","http_API","app","kotlin","java","pkg","cmd","internal")
SOURCE_MANIFESTS = ("composer.json","package.json","pom.xml","go.mod","Cargo.toml",
                    "setup.py","pyproject.toml","pubspec.yaml","build.gradle",
                    "build.gradle.kts","mise.toml")
WORKFLOW_KEYWORDS = ("backup","snapshot","mirror","sync","dispatch")

def git(repo, *args):
    try:
        r = subprocess.run(["git","-C",str(repo),*args], capture_output=True,
                           text=True, check=False)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", default=".")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    root = git(a.path, "rev-parse", "--show-toplevel")
    if not root:
        print(f"ERROR: not in a Git repo: {a.path}", file=sys.stderr); sys.exit(2)
    root = Path(root)

    signals = {"workflow": 0, "canonical": 0, "mirror": 0}
    notes = []

    # Workflow signals
    wf_dir = root / ".github" / "workflows"
    if wf_dir.is_dir():
        wf_files = list(wf_dir.glob("*.yml")) + list(wf_dir.glob("*.yaml"))
        wf_keyword_hits = sum(
            1 for f in wf_files
            if any(k in f.name.lower() for k in WORKFLOW_KEYWORDS)
        )
        if wf_files and wf_keyword_hits / len(wf_files) >= 0.5:
            signals["workflow"] += 3
            notes.append(f"{wf_keyword_hits}/{len(wf_files)} workflow files match backup/mirror/sync pattern")

    # Recent commit titles
    log = git(root, "log", "--oneline", "-n", "20") or ""
    backup_commits = sum(1 for line in log.splitlines()
                         if any(k in line.lower() for k in WORKFLOW_KEYWORDS))
    if backup_commits >= 10:
        signals["workflow"] += 2
        notes.append(f"{backup_commits}/20 recent commits look like backup/snapshot/mirror")

    # Manifest signals (canonical)
    manifests = [m for m in SOURCE_MANIFESTS if (root / m).exists()]
    if manifests:
        signals["canonical"] += 2
        notes.append(f"manifest(s) at root: {', '.join(manifests)}")

    # Source-tree signals
    src_dirs = [d for d in SOURCE_DIRS if (root / d).is_dir()]
    if src_dirs:
        # count files
        total = sum(sum(1 for _ in (root / d).rglob("*") if _.is_file()) for d in src_dirs)
        if total >= 10:
            signals["canonical"] += 2
            notes.append(f"source dirs {src_dirs} contain {total} files")

    # Mirror signals (README)
    for readme in ("README.md","README.rst","README.txt","README"):
        p = root / readme
        if p.exists():
            try:
                txt = p.read_text(errors="ignore").lower()
                if "mirror of" in txt or "read-only mirror" in txt:
                    signals["mirror"] += 3
                    notes.append(f"{readme} declares mirror status")
            except Exception:
                pass
            break

    verdict = max(signals, key=signals.get) if any(signals.values()) else "unknown"
    if signals[verdict] < 2:
        verdict = "unknown"

    result = {"root": str(root), "verdict": verdict, "signals": signals, "notes": notes}
    if a.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"REPO_ROOT: {root}")
        print(f"VERDICT:   {verdict}")
        print(f"SIGNALS:   {signals}")
        for n in notes:
            print(f"  - {n}")
        if verdict in ("workflow","mirror"):
            print(f"\nWARNING: editing source code in a {verdict} repo is almost always wrong.")
            print("         Locate the canonical source repo before proceeding.")
    sys.exit(0)

if __name__ == "__main__":
    main()
