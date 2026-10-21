#!/usr/bin/env python3
"""Gap-closure session evidence driver (composer Tier-1).

Tier: Tier 1 (Python default) per scripting-language-selection-rules section 3
(orchestration only: argparse, subprocess, pathlib, json, hashlib, datetime,
os). Stdlib-only and 3.9-safe; PyYAML and ruamel.yaml live inside the composed
base scripts, never here.

The driver sequences the session-analysis bundle and path attribution, then
persists one gap-closure-scoped evidence manifest with absolute paths. It does
not re-implement session extraction, reporting, or attribution: those remain
owned by the composed CLIs.

Normal mode:
  bundle -> manifest -> optional per-token attribution -> final manifest.

Attribution-only mode:
  existing manifest -> per-token attribution -> merged manifest.

Composed scripts are resolved through Path(__file__).resolve().parents[4]
(= the skills/ folder), so the driver works from any working directory.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILLS_ROOT = Path(__file__).resolve().parents[4]
BUNDLE = (
    SKILLS_ROOT
    / "opencode/session/opencode-session-analysis-bundle/scripts"
    / "run-session-analysis-bundle.py"
)
ATTRIBUTION = (
    SKILLS_ROOT
    / "opencode/opencode-session-path-attribution/scripts"
    / "attribute-path-to-session.py"
)
NAMING = (
    SKILLS_ROOT
    / "general/file/scratch-artifact-naming/scripts"
    / "resolve-scratch-path.py"
)
DEFAULT_PURPOSE = "skill-library-gap-closure-evidence"
MANIFEST_NAME = "gap-closure-evidence-manifest.json"


def fail(message, code=2):
    """Emit one prefixed diagnostic and return the requested exit code."""
    print(f"gap-closure-evidence: {message}", file=sys.stderr)
    return code


def require(path, label):
    """Return a composed-script path or exit 4 when it is missing."""
    if not path.is_file():
        raise SystemExit(fail(f"missing composed {label} script: {path}", 4))
    return path


def run_capture(cmd):
    """Run a composed CLI and return its completed process."""
    try:
        return subprocess.run(cmd, capture_output=True, text=True)
    except OSError as exc:
        raise SystemExit(fail(f"cannot execute composed script: {exc}", 2))


def normalize_session_id(value):
    """Return the canonical ses_<short> form."""
    short = value[4:] if value.startswith("ses_") else value
    return f"ses_{short}"


def add_token(tokens, seen, value):
    """Append a first-seen, exact-match token."""
    if value and value not in seen:
        seen.add(value)
        tokens.append(value)


def load_paths(path_args, file_args):
    """Merge --path and every --paths-file, preserving first-seen order."""
    tokens = []
    seen = set()
    for value in path_args:
        token = value.strip()
        if not token:
            raise SystemExit(fail("--path must not be empty or whitespace-only", 2))
        add_token(tokens, seen, token)
    for name in file_args:
        path = Path(name)
        try:
            lines = path.read_text().splitlines()
        except OSError as exc:
            raise SystemExit(fail(f"cannot read --paths-file {path}: {exc}", 2))
        for line in lines:
            value = line.strip()
            if not value or value.startswith("#"):
                continue
            add_token(tokens, seen, value)
    return tokens


def slug_for_token(token):
    """Deterministic per-token attribution filename stem."""
    base = re.sub(r"[^a-z0-9]+", "-", token.lower()).strip("-")[:60]
    digest = hashlib.sha1(token.encode("utf-8")).hexdigest()[:8]
    return f"path-{base}-{digest}"


def resolve_evidence_dir(value):
    """Return an absolute evidence directory, creating it when requested."""
    path = Path(value).expanduser().resolve()
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise SystemExit(fail(f"cannot create evidence directory {path}: {exc}", 2))
    return path


def write_manifest(path, manifest):
    """Write the manifest atomically via a sibling temporary file."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(json.dumps(manifest, indent=2) + "\n")
        os.replace(tmp, path)
    except OSError as exc:
        raise SystemExit(fail(f"cannot write evidence manifest {path}: {exc}", 2))


def source_logs_for(session_dir):
    """List the source transcript files in a session directory."""
    return [
        str(path.resolve())
        for path in sorted(Path(session_dir).glob("[0-9][0-9][0-9]-*.yaml"))
    ]


def bundle_command(args, sid):
    """Build the bundle command for normal mode."""
    cmd = [
        sys.executable,
        str(BUNDLE),
        "--repo",
        args.repo,
        "--purpose",
        args.purpose,
        "--truncate",
        str(args.truncate),
    ]
    if sid:
        cmd.extend(["--session-id", sid])
    if args.log_dir:
        cmd.extend(["--log-dir", args.log_dir])
    if args.no_jsonl:
        cmd.append("--no-jsonl")
    return cmd


def attribution_command(args, token, output, sid, log_dir):
    """Build one attribution command."""
    cmd = [
        sys.executable,
        str(ATTRIBUTION),
        "--path",
        token,
        "--json",
        "--output",
        str(output),
    ]
    if not args.cross_session:
        cmd.extend(["--session", sid])
    if log_dir:
        cmd.extend(["--logs", log_dir])
    return cmd


def parse_bundle_manifest(stdout):
    """Parse and validate the bundle's JSON stdout."""
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(fail(f"malformed bundle JSON: {exc}", 2))
    required = {
        "session_id",
        "session_dir",
        "transcripts",
        "report",
        "jsonl",
        "log_dir",
        "excluded_turns",
    }
    if not isinstance(data, dict) or not required.issubset(data):
        raise SystemExit(fail("bundle JSON is missing required keys", 2))
    if not isinstance(data["transcripts"], list):
        raise SystemExit(fail("bundle JSON transcripts is not a list", 2))
    return data


def load_existing_manifest(path):
    """Load and minimally validate an existing evidence manifest."""
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(fail(f"cannot read evidence manifest {path}: {exc}", 2))
    required = {
        "session_id",
        "session_dir",
        "log_dir",
        "bundle",
        "source_logs",
        "attributions",
    }
    if not isinstance(data, dict) or not required.issubset(data):
        raise SystemExit(fail(f"malformed evidence manifest: {path}", 2))
    if not isinstance(data["attributions"], list):
        raise SystemExit(fail(f"malformed evidence manifest attributions: {path}", 2))
    return data


def merge_attributions(existing, additions):
    """Merge attribution entries by token, preserving existing order."""
    by_token = {entry.get("token"): entry for entry in existing}
    order = [entry.get("token") for entry in existing]
    for entry in additions:
        token = entry["token"]
        if token not in by_token:
            order.append(token)
        by_token[token] = entry
    return [by_token[token] for token in order if token in by_token]


def build_manifest(sid, session_dir, log_dir, evidence_dir, bundle):
    """Build the common evidence manifest skeleton."""
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "session_id": sid,
        "session_dir": str(Path(session_dir).resolve()),
        "log_dir": str(Path(log_dir).resolve()),
        "evidence_dir": str(evidence_dir.resolve()),
        "bundle": {
            "report": str(Path(bundle["report"]).resolve()),
            "jsonl": str(Path(bundle["jsonl"]).resolve()) if bundle.get("jsonl") else None,
            "transcripts": [
                str(Path(item).resolve()) for item in bundle.get("transcripts", [])
            ],
            "excluded_turns": list(bundle.get("excluded_turns", [])),
        },
        "source_logs": source_logs_for(session_dir),
        "attributions": [],
    }


def attribute_token(args, token, evidence_dir, sid, log_dir):
    """Run one attribution call and return its manifest entry."""
    output = evidence_dir / "path-attribution" / f"{slug_for_token(token)}.json"
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise SystemExit(
            fail(f"cannot create attribution directory {output.parent}: {exc}", 2)
        )
    cmd = attribution_command(args, token, output, sid, log_dir)
    proc = run_capture(cmd)
    records = None
    if output.is_file():
        try:
            records = json.loads(output.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            raise SystemExit(fail(f"malformed attribution JSON for {token}: {exc}", 2))
        if not isinstance(records, list):
            raise SystemExit(fail(f"attribution JSON for {token} is not an array", 2))
    if proc.returncode == 0:
        if records is None:
            raise SystemExit(fail(f"attribution output missing for {token}", 2))
        return {
            "token": token,
            "status": "match",
            "exit_code": 0,
            "match_count": len(records),
            "output": str(output.resolve()),
        }
    if proc.returncode == 1:
        return {
            "token": token,
            "status": "no_match",
            "exit_code": 1,
            "match_count": 0,
            "output": str(output.resolve()),
        }
    if proc.stderr.strip():
        print(proc.stderr.strip(), file=sys.stderr)
    raise SystemExit(
        fail(f"attribution failed for {token} (exit {proc.returncode})", 2)
    )


def print_summary(manifest, as_json):
    """Emit the manifest JSON or a compact human summary."""
    if as_json:
        print(json.dumps(manifest, indent=2))
        return
    print(f"session: {manifest['session_id']}")
    print(f"evidence: {manifest['evidence_dir']}")
    print(f"report: {manifest['bundle']['report']}")
    print(f"jsonl: {manifest['bundle']['jsonl'] or '(skipped)'}")
    print(f"transcripts: {len(manifest['bundle']['transcripts'])}")
    for entry in manifest["attributions"]:
        print(
            f"attribution: {entry['token']} -> {entry['status']} "
            f"({entry['match_count']})"
        )


def print_dry_run(args, tokens, evidence_dir, sid, log_dir):
    """Print resolved paths and commands without executing or writing."""
    print(f"skills root: {SKILLS_ROOT}")
    print(f"bundle: {BUNDLE}")
    print(f"attribution: {ATTRIBUTION}")
    print(f"naming: {NAMING}")
    print(f"session: {sid or 'auto-discover'}")
    print(
        "evidence dir: "
        f"{evidence_dir if evidence_dir else 'resolved-after-bundle'}"
    )
    if args.attribution_only and not args.evidence_dir:
        naming_command = [
            sys.executable,
            str(NAMING),
            "--repo",
            args.repo,
            "--purpose",
            args.purpose,
            "--session-id",
            args.session_id or "<session-id>",
        ]
        print("command: " + " ".join(naming_command))
    if not args.attribution_only:
        print("command: " + " ".join(bundle_command(args, args.session_id)))
    if tokens:
        target = evidence_dir or Path("<evidence-dir>")
        for token in tokens:
            output = target / "path-attribution" / f"{slug_for_token(token)}.json"
            command_sid = sid or "<session-id>"
            print(
                "command: "
                + " ".join(
                    attribution_command(args, token, output, command_sid, log_dir)
                )
            )
            print(f"output: {output}")


def main():
    """Parse arguments and run the selected evidence mode."""
    parser = argparse.ArgumentParser(
        description="Gap-closure session evidence driver (composer Tier-1)."
    )
    parser.add_argument(
        "--session-id",
        default=None,
        help=(
            "Session to analyze. Optional in normal mode; in --attribution-only "
            "it is required when --evidence-dir is omitted and must match the "
            "manifest when supplied. ses_ prefix optional."
        ),
    )
    parser.add_argument("--log-dir", default=None, help="Logger root override.")
    parser.add_argument("--repo", default=".", help="Repository root.")
    parser.add_argument(
        "--purpose", default=DEFAULT_PURPOSE, help="Scratch purpose slug."
    )
    parser.add_argument(
        "--truncate",
        type=int,
        default=500,
        help="Report skeleton truncation width.",
    )
    parser.add_argument(
        "--no-jsonl",
        action="store_true",
        help="Skip the full-fidelity JSONL.",
    )
    parser.add_argument(
        "--path",
        action="append",
        default=[],
        help="Path token to attribute. Repeatable.",
    )
    parser.add_argument(
        "--paths-file",
        action="append",
        default=[],
        help="File with one path token per line. Repeatable.",
    )
    parser.add_argument(
        "--attribution-only",
        action="store_true",
        help="Skip the bundle and run only path attribution.",
    )
    parser.add_argument(
        "--cross-session",
        action="store_true",
        help="Omit the --session filter in attribution.",
    )
    parser.add_argument(
        "--evidence-dir",
        default=None,
        help="Directory for the manifest and path-attribution files.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the summary manifest as JSON.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands and paths; perform no writes or subprocesses.",
    )
    args = parser.parse_args()

    tokens = load_paths(args.path, args.paths_file)
    if args.attribution_only and not tokens:
        raise SystemExit(
            fail("--attribution-only requires at least one path token", 2)
        )

    if args.attribution_only:
        if not args.evidence_dir and not args.session_id:
            raise SystemExit(
                fail(
                    "--attribution-only requires --session-id when "
                    "--evidence-dir is omitted",
                    2,
                )
            )
        if not args.evidence_dir:
            require(NAMING, "naming")
        require(ATTRIBUTION, "attribution")
        if args.dry_run:
            evidence_dir = (
                Path(args.evidence_dir).expanduser().resolve()
                if args.evidence_dir
                else None
            )
            manifest_path = (
                evidence_dir / MANIFEST_NAME
                if evidence_dir
                else Path("<evidence-dir>") / MANIFEST_NAME
            )
            if evidence_dir and not manifest_path.is_file():
                raise SystemExit(
                    fail(f"evidence manifest not found: {manifest_path}", 2)
                )
            print(f"manifest: {manifest_path}")
            print_dry_run(
                args,
                tokens,
                evidence_dir,
                normalize_session_id(args.session_id) if args.session_id else None,
                args.log_dir,
            )
            return 0

        if args.evidence_dir:
            evidence_dir = resolve_evidence_dir(args.evidence_dir)
        else:
            naming = run_capture(
                [
                    sys.executable,
                    str(NAMING),
                    "--repo",
                    args.repo,
                    "--purpose",
                    args.purpose,
                    "--session-id",
                    args.session_id,
                ]
            )
            if naming.returncode != 0:
                if naming.stderr.strip():
                    print(naming.stderr.strip(), file=sys.stderr)
                return fail("could not resolve the session scratch directory", 2)
            evidence_dir = Path(naming.stdout.strip()).parent.resolve()
        manifest_path = evidence_dir / MANIFEST_NAME
        manifest = load_existing_manifest(manifest_path)
        manifest_sid = normalize_session_id(manifest["session_id"])
        if args.session_id and normalize_session_id(args.session_id) != manifest_sid:
            raise SystemExit(
                fail(
                    "--session-id does not match the evidence manifest session",
                    2,
                )
            )
        if args.log_dir:
            manifest["log_dir"] = str(Path(args.log_dir).resolve())
        sid = manifest_sid
        log_dir = manifest["log_dir"]
        manifest["generated_at"] = datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        manifest["evidence_dir"] = str(evidence_dir.resolve())
        manifest["source_logs"] = source_logs_for(manifest["session_dir"])
        additions = []
        for token in tokens:
            try:
                additions.append(
                    attribute_token(args, token, evidence_dir, sid, log_dir)
                )
            except SystemExit as exc:
                manifest["attributions"] = merge_attributions(
                    manifest["attributions"], additions
                )
                manifest["error"] = {
                    "token": token,
                    "message": f"attribution failed for {token}",
                }
                write_manifest(manifest_path, manifest)
                raise exc
        manifest["attributions"] = merge_attributions(
            manifest["attributions"], additions
        )
        write_manifest(manifest_path, manifest)
        print_summary(manifest, args.json)
        return 0

    require(BUNDLE, "bundle")
    if tokens:
        require(ATTRIBUTION, "attribution")
    if args.dry_run:
        print_dry_run(
            args,
            tokens,
            Path(args.evidence_dir).expanduser().resolve()
            if args.evidence_dir
            else None,
            normalize_session_id(args.session_id) if args.session_id else None,
            args.log_dir,
        )
        return 0

    bundle = run_capture(bundle_command(args, args.session_id))
    if bundle.stderr.strip():
        print(bundle.stderr.strip(), file=sys.stderr)
    if bundle.returncode != 0:
        return bundle.returncode
    bundle_manifest = parse_bundle_manifest(bundle.stdout)
    sid = normalize_session_id(bundle_manifest["session_id"])
    log_dir = bundle_manifest["log_dir"]
    if args.evidence_dir:
        evidence_dir = resolve_evidence_dir(args.evidence_dir)
    else:
        evidence_dir = Path(bundle_manifest["report"]).parent.resolve()
    manifest = build_manifest(
        sid,
        bundle_manifest["session_dir"],
        log_dir,
        evidence_dir,
        bundle_manifest,
    )
    manifest_path = evidence_dir / MANIFEST_NAME
    additions = []
    for token in tokens:
        try:
            additions.append(attribute_token(args, token, evidence_dir, sid, log_dir))
        except SystemExit as exc:
            manifest["attributions"] = additions
            manifest["error"] = {
                "token": token,
                "message": f"attribution failed for {token}",
            }
            write_manifest(manifest_path, manifest)
            raise exc
    manifest["attributions"] = additions
    write_manifest(manifest_path, manifest)
    print_summary(manifest, args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
