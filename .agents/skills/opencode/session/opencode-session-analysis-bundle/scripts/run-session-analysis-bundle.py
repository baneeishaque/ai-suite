"""Session analysis bundle driver (composer Tier-1).

Tier: Tier 1 (Python default) per scripting-language-selection-rules section 3
(orchestration only: argparse, subprocess, pathlib, json, sys). Stdlib-only
and 3.9-safe; no third-party imports (PyYAML and ruamel.yaml live inside the
composed base scripts, never here).

Sequence: find-current-session -> locate-installed-plugins ->
extract-yaml-conversation -> extract-yaml-transcript ->
resolve-scratch-path -> reconstruct-workflow; then exclusions appendix and
JSON manifest on stdout. Skill scripts resolve through
Path(__file__).resolve().parents[3] (= the opencode/ skill folder) and
parents[4] (= the skills/ folder), so the pipeline works regardless of the
caller's working directory.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def base(*parts):
    """Resolve a composed script under opencode/; exit 4 when missing."""
    root = Path(__file__).resolve().parents[3]
    p = root.joinpath(*parts)
    if not p.is_file():
        print(f"bundle: missing composed script: {p}", file=sys.stderr)
        sys.exit(4)
    return str(p)


def naming_script():
    """Resolve resolve-scratch-path.py under skills/general/file/."""
    p = Path(__file__).resolve().parents[4] / "general" / "file" / \
        "scratch-artifact-naming" / "scripts" / "resolve-scratch-path.py"
    if not p.is_file():
        print(f"bundle: missing composed script: {p}", file=sys.stderr)
        sys.exit(4)
    return str(p)


def run(cmd, exit_code):
    """Run a composed CLI; diagnostics to stderr, payload on stdout."""
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.stderr.strip():
        print(proc.stderr.strip(), file=sys.stderr)
    if proc.returncode != 0:
        print(f"bundle: step failed (exit {proc.returncode}): {' '.join(cmd)}",
              file=sys.stderr)
        sys.exit(exit_code)
    return proc.stdout


def main():
    ap = argparse.ArgumentParser(description="Opencode session analysis bundle driver.")
    ap.add_argument("--session-id", default=None,
                    help="Full session ID (ses_ prefix optional).")
    ap.add_argument("--log-dir", default=None, help="Logger root override.")
    ap.add_argument("--repo", default=".", help="Repo root for session scratch.")
    ap.add_argument("--purpose", default="session-analysis", help="Scratch purpose slug.")
    ap.add_argument("--truncate", type=int, default=500, help="Skeleton truncation width.")
    ap.add_argument("--no-jsonl", action="store_true",
                    help="Skip the full-fidelity JSONL.")
    ap.add_argument("--exclude-turn", type=int, action="append", default=[],
                    help="Turn ordinal to exclude (repeatable).")
    ap.add_argument("--exclude-reason", default="",
                    help="Rationale recorded for exclusions.")
    args = ap.parse_args()

    conv = base("opencode-session-yaml-conversation-extractor", "scripts",
                "extract-yaml-conversation.py")
    tr = base("opencode-session-yaml-transcript-extractor", "scripts",
              "extract-yaml-transcript.py")
    recon = base("opencode-session-problem-solution-workflow-analysis", "scripts",
                 "reconstruct-workflow.py")
    find = base("opencode-current-session-id", "scripts", "find-current-session.py")
    locate = base("opencode-installed-plugin-lookup", "scripts",
                  "locate-installed-plugins.py")
    naming = naming_script()

    if args.session_id:
        sid = args.session_id
    else:
        info = json.loads(run(["python3", find, "--json"], 2))
        sid = info["session_id"]
        if not info.get("pending", False):
            print("bundle: warning: no in-flight pending marker; "
                  "selection is newest-mtime fallback", file=sys.stderr)

    if args.log_dir:
        log_dir = args.log_dir
    else:
        plugins = json.loads(run(["python3", locate, "--plugin", "logger", "--json"], 2))
        log_dir = plugins[0]["logs_dir"]

    short = sid[4:] if sid.startswith("ses_") else sid
    ses_dir = str(Path(log_dir) / f"ses_{short}")
    if not Path(ses_dir).is_dir():
        print(f"bundle: session dir missing: {ses_dir}", file=sys.stderr)
        sys.exit(3)

    out_dir = str(Path(ses_dir) / "transcripts")
    run(["python3", conv, "--input", ses_dir, "--output-dir", out_dir], 2)
    transcripts = sorted(str(p) for p in Path(out_dir).glob("*-transcript.yaml"))

    stem = run(["python3", naming, "--repo", args.repo, "--purpose", args.purpose,
                "--session-id", sid], 2).strip()
    jsonl_path, report_path = stem + ".jsonl", stem + ".md"

    if not args.no_jsonl:
        run(["python3", tr, "--input", ses_dir, "--output", jsonl_path], 2)
    else:
        jsonl_path = None

    # Exclusion is delegated to the generator, which owns the stub format and the
    # summary-count repair. The driver must not re-derive that logic or append a
    # post-hoc appendix: an appendix cannot repair counts it already printed above
    # itself.
    recon_cmd = ["python3", recon, "--input", ses_dir,
                 "--truncate", str(args.truncate), "--output", report_path]
    for turn in sorted(set(args.exclude_turn)):
        recon_cmd += ["--exclude-turn", str(turn)]
    if args.exclude_reason:
        recon_cmd += ["--exclude-reason", args.exclude_reason]
    run(recon_cmd, 2)

    manifest = {"session_id": sid, "session_dir": ses_dir,
                "transcripts": transcripts, "report": report_path,
                "jsonl": jsonl_path, "log_dir": log_dir,
                "excluded_turns": sorted(args.exclude_turn)}
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
