import re
import sys
import argparse
from pathlib import Path


def find_repo_root(path):
    for parent in [path] + list(path.parents):
        if (parent / ".git").is_dir():
            return parent
    return None


def detect_cross_repo_links(filepath, fix=False):
    path = Path(filepath).resolve()
    repo_root = find_repo_root(path)
    if not repo_root:
        print(f"WARNING: could not find repo root for {filepath}", file=sys.stderr)
        return 1

    rel_to_repo = path.relative_to(repo_root)
    depth = len(rel_to_repo.parents)

    link_pattern = re.compile(r'\[([^\]]*?)\]\(((?:\.\./)+[^)]+)\)')
    matches = list(link_pattern.finditer(path.read_text(encoding="utf-8")))

    findings = []
    for m in matches:
        link_text = m.group(1)
        link_target = m.group(2)

        up_count = link_target.count("../")
        total_up = depth + up_count
        escapes = total_up > 1

        resolved = (path.parent / link_target).resolve()
        in_repo = False
        try:
            resolved.relative_to(repo_root)
            in_repo = True
        except ValueError:
            pass

        if not in_repo:
            findings.append((m.start(), m.end(), link_text, link_target, up_count, total_up))

    if not findings:
        return 0

    print(f"Found {len(findings)} cross-repo link(s) in {filepath}:")
    for start, end, text, target, up, total in findings:
        print(f"  [{text}]({target}) — {up} levels up from file depth {depth} (total: {total})")

    if fix:
        content = path.read_text(encoding="utf-8")
        for start, end, text, target, up, total in findings:
            replacement = f"`{text}` (in a sibling repository)"
            content = content[:start] + replacement + content[end:]
        path.write_text(content, encoding="utf-8")
        print(f"  → Fixed {len(findings)} link(s)")

    return 1 if findings else 0


def main():
    parser = argparse.ArgumentParser(description="Detect cross-repo relative links in skill files.")
    parser.add_argument("paths", nargs="+", help="Files to scan")
    parser.add_argument("--fix", action="store_true", help="Replace cross-repo links with name-only references")
    args = parser.parse_args()

    exit_code = 0
    for p in args.paths:
        code = detect_cross_repo_links(p, fix=args.fix)
        if code != 0:
            exit_code = code
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
