#!/usr/bin/env python3
"""attribute-lint-findings.py — Classify markdownlint findings as pre-existing or new.

Compares the working tree against a baseline Git ref. Both versions are linted
with the same custom-rule-free configuration, and every finding is keyed by
(file, line, column, rule). A finding is PRE-EXISTING when the baseline has
the same key (optionally within --line-tolerance), NEW when it does not, and
RESOLVED when only the baseline has it.

Usage:
    python3 attribute-lint-findings.py --baseline-ref HEAD <file.md> [<file.md> ...]

Exit codes: 0 = no new findings, 1 = new findings, 2 = error.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FINDING_RE = re.compile(
    r"^(?P<file>.+?):(?P<line>\d+):(?P<col>\d+) error (?P<rule>\S+) (?P<desc>.*)$"
)

CONFIG_CANDIDATES = (
    ".markdownlint-cli2.jsonc",
    ".markdownlint.jsonc",
    ".markdownlint.json",
)


def strip_jsonc(text: str) -> str:
    """Remove line/block comments and trailing commas from JSONC text."""
    out: list[str] = []
    i = 0
    in_string = False
    escaped = False
    while i < len(text):
        ch = text[i]
        if in_string:
            out.append(ch)
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
        elif ch == '"':
            in_string = True
            out.append(ch)
        elif ch == "/" and i + 1 < len(text) and text[i + 1] == "/":
            while i < len(text) and text[i] != "\n":
                i += 1
            continue
        elif ch == "/" and i + 1 < len(text) and text[i + 1] == "*":
            i += 2
            while i + 1 < len(text) and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
            continue
        else:
            out.append(ch)
        i += 1
    return re.sub(r",\s*([}\]])", r"\1", "".join(out))


def find_config(repo: Path) -> Path | None:
    """Return the first supported JSON/JSONC markdownlint config in the repo."""
    for name in CONFIG_CANDIDATES:
        candidate = repo / name
        if candidate.is_file():
            return candidate
    return None


def build_config(
    source: Path | None, dest: Path, keep_custom_rules: bool
) -> Path | None:
    """Write a temp config, dropping custom rules that need a full checkout."""
    if source is None:
        return None
    data = json.loads(strip_jsonc(source.read_text(encoding="utf-8")))
    if not keep_custom_rules:
        data.pop("customRules", None)
        nested = data.get("config")
        if isinstance(nested, dict):
            nested.pop("relative-links", None)
    target = dest / "markdownlint-config.json"
    target.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return target


def find_binary() -> str:
    """Resolve the standalone markdownlint-cli2 binary."""
    binary = shutil.which("markdownlint-cli2")
    if binary:
        return binary
    fallback = Path("/opt/homebrew/bin/markdownlint-cli2")
    if fallback.is_file():
        return str(fallback)
    raise RuntimeError("markdownlint-cli2 not found on PATH or at /opt/homebrew/bin")


def lint_files(
    binary: str, cwd: Path, config: Path | None, rel_paths: list[str]
) -> list[dict]:
    """Run markdownlint-cli2 and return parsed findings."""
    cmd = [binary, "--no-globs"]
    if config is not None:
        cmd += ["--config", str(config)]
    cmd += rel_paths
    proc = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, timeout=180
    )
    if proc.returncode not in (0, 1):
        detail = (proc.stderr or proc.stdout).strip()
        raise RuntimeError(f"markdownlint-cli2 failed ({proc.returncode}): {detail}")
    findings: list[dict] = []
    for line in (proc.stdout + "\n" + proc.stderr).splitlines():
        match = FINDING_RE.match(line.strip())
        if match:
            findings.append(
                {
                    "file": match.group("file").removeprefix("./"),
                    "line": int(match.group("line")),
                    "col": int(match.group("col")),
                    "rule": match.group("rule"),
                    "desc": match.group("desc"),
                }
            )
    if proc.returncode == 1 and not findings:
        detail = (proc.stderr or proc.stdout).strip()
        raise RuntimeError(f"markdownlint-cli2 reported issues but none parsed: {detail}")
    return findings


def extract_baseline(
    repo: Path, ref: str, rel_paths: list[str], dest: Path
) -> list[str]:
    """Write the baseline version of each path into dest; return those present."""
    present: list[str] = []
    for rel in rel_paths:
        proc = subprocess.run(
            ["git", "show", f"{ref}:{rel}"],
            cwd=repo,
            capture_output=True,
        )
        if proc.returncode != 0:
            continue
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(proc.stdout)
        present.append(rel)
    return present


def copy_current(repo: Path, rel_paths: list[str], dest: Path) -> None:
    """Copy the working-tree version of each path into dest."""
    for rel in rel_paths:
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(repo / rel, target)


def attribute(
    current: list[dict], baseline: list[dict], tolerance: int
) -> tuple[list[dict], list[dict], list[dict]]:
    """Match current findings against baseline findings by key and tolerance."""
    used = [False] * len(baseline)
    pre_existing: list[dict] = []
    pending: list[dict] = []
    for cur in current:
        matched = None
        for idx, base in enumerate(baseline):
            if used[idx]:
                continue
            if (
                base["file"] == cur["file"]
                and base["rule"] == cur["rule"]
                and base["col"] == cur["col"]
                and abs(base["line"] - cur["line"]) <= tolerance
            ):
                matched = idx
                break
        if matched is None:
            pending.append(cur)
        else:
            used[matched] = True
            pre_existing.append(cur)

    new: list[dict] = []
    for cur in pending:
        candidates = [
            idx
            for idx, base in enumerate(baseline)
            if not used[idx]
            and base["file"] == cur["file"]
            and base["rule"] == cur["rule"]
            and base["col"] == cur["col"]
            and base["desc"] == cur["desc"]
        ]
        if not candidates:
            new.append(cur)
            continue
        nearest = min(
            candidates,
            key=lambda idx: abs(baseline[idx]["line"] - cur["line"]),
        )
        used[nearest] = True
        pre_existing.append(cur)

    resolved = [base for idx, base in enumerate(baseline) if not used[idx]]
    return pre_existing, new, resolved


def emit(
    pre_existing: list[dict],
    new: list[dict],
    resolved: list[dict],
    output_format: str,
) -> None:
    """Print the attribution report."""
    if output_format == "json":
        print(
            json.dumps(
                {
                    "pre_existing": pre_existing,
                    "new": new,
                    "resolved": resolved,
                    "summary": {
                        "pre_existing": len(pre_existing),
                        "new": len(new),
                        "resolved": len(resolved),
                    },
                },
                indent=2,
            )
        )
        return
    for label, items in (
        ("PRE-EXISTING", pre_existing),
        ("NEW", new),
        ("RESOLVED", resolved),
    ):
        for item in items:
            print(
                f"{label:<12} {item['file']}:{item['line']}:{item['col']} "
                f"{item['rule']}"
            )
    print(
        f"Summary: {len(pre_existing)} pre-existing, {len(new)} new, "
        f"{len(resolved)} resolved"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Classify markdownlint findings as pre-existing or new."
    )
    parser.add_argument("files", nargs="+", metavar="file.md")
    parser.add_argument(
        "--baseline-ref",
        default="HEAD",
        help="Git ref to compare against (default: HEAD)",
    )
    parser.add_argument(
        "--repo", default=".", help="Repository root (default: current directory)"
    )
    parser.add_argument(
        "--config",
        help="Explicit markdownlint config (JSON/JSONC); defaults to the repo config",
    )
    parser.add_argument(
        "--line-tolerance",
        type=int,
        default=0,
        help="Maximum line drift when matching a finding (default: 0)",
    )
    parser.add_argument(
        "--keep-custom-rules",
        action="store_true",
        help="Keep custom rules (baseline files are linted in isolation)",
    )
    parser.add_argument(
        "--format", choices=("text", "json"), default="text", help="Report format"
    )
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    rel_paths: list[str] = []
    for raw in args.files:
        path = Path(raw)
        absolute = path.resolve() if path.is_absolute() else (repo / path).resolve()
        try:
            rel = absolute.relative_to(repo).as_posix()
        except ValueError:
            print(f"ERROR: {raw} is outside {repo}", file=sys.stderr)
            sys.exit(2)
        if not absolute.is_file():
            print(f"ERROR: not a file: {rel}", file=sys.stderr)
            sys.exit(2)
        rel_paths.append(rel)

    try:
        binary = find_binary()
        config_source = (
            (repo / args.config).resolve()
            if args.config and not Path(args.config).is_absolute()
            else (Path(args.config).resolve() if args.config else find_config(repo))
        )
        with tempfile.TemporaryDirectory(prefix="mdlint-attribute-") as tmp:
            work = Path(tmp)
            config = build_config(
                config_source, work, args.keep_custom_rules
            )
            current_dir = work / "current"
            current_dir.mkdir()
            copy_current(repo, rel_paths, current_dir)
            current = lint_files(binary, current_dir, config, rel_paths)
            baseline_dir = work / "baseline"
            baseline_dir.mkdir()
            present = extract_baseline(repo, args.baseline_ref, rel_paths, baseline_dir)
            baseline = (
                lint_files(binary, baseline_dir, config, present) if present else []
            )
        pre_existing, new, resolved = attribute(
            current, baseline, args.line_tolerance
        )
    except (RuntimeError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(2)

    emit(pre_existing, new, resolved, args.format)
    sys.exit(1 if new else 0)


if __name__ == "__main__":
    main()
