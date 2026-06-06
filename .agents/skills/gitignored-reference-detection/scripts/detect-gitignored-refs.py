"""Detect references to gitignored files in committed markdown.

Scans markdown files for link targets ([text](path)) and inline paths
in code blocks, checks each against git check-ignore -v, and reports
violations with suggested remediations.

Usage:
    python3 detect-gitignored-refs.py --path <file-or-directory>
    python3 detect-gitignored-refs.py --path .agents/skills/ --format json
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def get_repo_root(cwd: Path | None = None) -> Path:
    """Return the absolute path of the enclosing Git repository root.

    Checks *cwd* (or the current working directory if None) for a Git repo.
    """
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
        cwd=cwd,
    )
    return Path(result.stdout.strip())


def check_gitignored(path: str, repo_root: Path, cwd: Path | None = None) -> dict | None:
    """Run git check-ignore -v on *path* (relative to repo_root).

    Returns a dict with gitignore_rule, gitignore_line, and matched_path
    if the file is gitignored, or None if it is tracked.
    """
    try:
        result = subprocess.run(
            ["git", "check-ignore", "-v", path],
            capture_output=True, text=True, check=True,
            cwd=cwd or repo_root,
        )
        line = result.stdout.strip()
        if not line:
            return None
        parts = line.split("\t")
        if len(parts) >= 3:
            rule_file, line_number, matched = parts[0], parts[1], parts[2]
            return {
                "gitignore_rule": str(Path(rule_file).name),
                "gitignore_line": line_number,
                "matched_path": matched,
            }
        return {"gitignore_rule": line, "gitignore_line": "", "matched_path": path}
    except subprocess.CalledProcessError:
        return None


LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
CODE_BLOCK_PATH_PATTERN = re.compile(r"`([./][^\s`]+)`")


def extract_paths(content: str, source_file: Path) -> list[dict]:
    """Extract local path references from markdown content.

    Returns a list of dicts with fields: line_number, path, context, kind.
    """
    hits = []
    for match in LINK_PATTERN.finditer(content):
        target = match.group(2)
        if target.startswith("./") or target.startswith("../") or target.startswith(".agents"):
            line_num = content[: match.start()].count("\n") + 1
            hits.append({
                "line_number": line_num,
                "path": target,
                "context": match.group(0)[:60],
                "kind": "link",
            })
    for match in CODE_BLOCK_PATH_PATTERN.finditer(content):
        target = match.group(1)
        if target.startswith("./") or target.startswith("../") or target.startswith(".agents"):
            line_num = content[: match.start()].count("\n") + 1
            hits.append({
                "line_number": line_num,
                "path": target,
                "context": match.group(0)[:60],
                "kind": "code_path",
            })
    return hits


def resolve_relative(path: str, source_file: Path) -> Path:
    """Resolve a relative path against the source file's directory."""
    source_dir = source_file.resolve().parent
    return (source_dir / path).resolve()


def scan_file(file_path: Path, repo_root: Path) -> list[dict]:
    """Scan a single markdown file for gitignored references.

    Returns a list of violation dicts.
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return [{"file": str(file_path), "error": str(e)}]

    violations = []
    rel_file = file_path.resolve().relative_to(repo_root)

    for ref in extract_paths(content, file_path):
        target_path = resolve_relative(ref["path"], file_path)
        try:
            rel_target = target_path.relative_to(repo_root)
        except ValueError:
            continue

        gitignore_info = check_gitignored(str(rel_target), repo_root, cwd=repo_root)
        if gitignore_info is not None:
            violations.append({
                "file": str(rel_file),
                "line": ref["line_number"],
                "path": ref["path"],
                "resolved": str(rel_target),
                "context": ref["context"],
                "kind": ref["kind"],
                "gitignore": gitignore_info,
            })

    return violations


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Detect references to gitignored files in committed markdown."
    )
    parser.add_argument(
        "--path",
        required=True,
        help="File or directory to scan (relative to repo root or absolute).",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    args = parser.parse_args()

    raw_path = Path(args.path).resolve()
    if not raw_path.exists():
        print(f"Error: path does not exist: {raw_path}", file=sys.stderr)
        sys.exit(1)

    # Determine repo root from the scanned path (not CWD — they may differ)
    anchor = raw_path if raw_path.is_dir() else raw_path.parent
    repo_root = get_repo_root(cwd=anchor)
    scan_path = raw_path

    all_violations = []

    if scan_path.is_file() and scan_path.suffix in (".md", ".markdown"):
        all_violations.extend(scan_file(scan_path, repo_root))
    elif scan_path.is_dir():
        for md_file in sorted(scan_path.rglob("*.md")):
            all_violations.extend(scan_file(md_file, repo_root))
    else:
        print(f"Error: unsupported path (must be .md file or directory): {scan_path}", file=sys.stderr)
        sys.exit(1)

    if args.format == "json":
        print(json.dumps(all_violations, indent=2))
    else:
        if not all_violations:
            print("No violations found.")
            sys.exit(0)
        print(f"Found {len(all_violations)} gitignored reference(s):\n")
        for v in all_violations:
            print(f"  File:  {v['file']}:{v['line']}")
            print(f"  Path:  {v['path']}")
            print(f"  Kind:  {v['kind']}")
            print(f"  Rule:  {v['gitignore']['gitignore_rule']} (line {v['gitignore']['gitignore_line']})")
            print(f"  Ctx:   {v['context']}")
            print()
        sys.exit(1 if all_violations else 0)


if __name__ == "__main__":
    main()
