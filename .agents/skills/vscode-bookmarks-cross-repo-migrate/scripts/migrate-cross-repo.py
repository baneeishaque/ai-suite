"""
migrate-cross-repo.py — Migrate VS Code bookmarks from source repo to target repo.

Discovers moved files, remaps old paths to new paths, delegates the merge
to the vscode-bookmarks-merge base skill's merge-bookmarks.py script.

Usage:
    python3 migrate-cross-repo.py --source-repo <path> --target-repo <path> [--dry-run] [--clean-source]

Language tier: Tier 1 (Python 3.12+) per scripting-language-selection-rules.
SSOT: vscode-bookmarks-cross-repo-migrate skill.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def resolve_script_path() -> Path:
    """Resolve path to the vscode-bookmarks-merge base script."""
    this_dir = Path(__file__).resolve().parent
    return (
        this_dir / ".." / ".." / "vscode-bookmarks-merge" / "scripts" / "merge-bookmarks.py"
    ).resolve()


def load_bookmarks(repo: Path) -> dict:
    path = repo / ".vscode" / "bookmarks.json"
    if not path.exists():
        return {"files": []}
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or "files" not in data:
        return {"files": []}
    return data


def save_bookmarks(repo: Path, data: dict):
    path = repo / ".vscode" / "bookmarks.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent="\t") + "\n", encoding="utf-8")


def remap_path(old_path: str, source_repo: Path, target_repo: Path) -> str | None:
    """Try to find the file at old_path in the target repo.

    Returns the new relative path, or None if not found.
    """
    # Strategy 1: same relative path
    candidate = target_repo / old_path
    if candidate.exists():
        return old_path

    # Strategy 2: check under docs/
    parts = Path(old_path).parts
    # If the path started with a subdirectory that might have moved under docs/
    doc_candidate = target_repo / "docs" / old_path
    if doc_candidate.exists():
        return str(Path("docs") / old_path)

    # Strategy 3: check if file moved to repo root
    # Strip leading directory components and look at basename
    basename = Path(old_path).name
    root_candidate = target_repo / basename
    if root_candidate.exists():
        return basename

    # Strategy 4: check if file is now in a subdirectory
    # Try each top-level subdirectory in target
    try:
        for entry in sorted(target_repo.iterdir()):
            if entry.is_dir() and not entry.name.startswith("."):
                sub_candidate = entry / old_path
                if sub_candidate.exists():
                    return str(entry.name / old_path)
    except PermissionError:
        pass

    return None


def clean_source_bookmarks(
    source_repo: Path, remapped_paths: set[str], dry_run: bool
) -> int:
    """Remove successfully migrated entries from source bookmarks.

    Returns 0 on success.
    """
    data = load_bookmarks(source_repo)
    original_count = len(data["files"])
    data["files"] = [
        entry
        for entry in data["files"]
        if entry.get("path", "") not in remapped_paths
    ]
    removed = original_count - len(data["files"])

    if dry_run:
        print(f"Would remove {removed} file entries from source bookmarks", file=sys.stderr)
    else:
        save_bookmarks(source_repo, data)
        print(f"Removed {removed} file entries from source bookmarks", file=sys.stderr)

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Migrate VS Code bookmarks across repos"
    )
    parser.add_argument(
        "--source-repo", required=True, type=Path, help="Path to source repository"
    )
    parser.add_argument(
        "--target-repo", required=True, type=Path, help="Path to target repository"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would happen without writing"
    )
    parser.add_argument(
        "--clean-source",
        action="store_true",
        help="Remove migrated entries from source bookmarks",
    )
    parser.add_argument(
        "--remap-file", type=Path, default=None, help="Manual remap dictionary JSON"
    )
    args = parser.parse_args()

    src = args.source_repo.resolve()
    tgt = args.target_repo.resolve()

    if not src.is_dir():
        print(f"Error: source repo not found: {src}", file=sys.stderr)
        sys.exit(2)
    if not tgt.is_dir():
        print(f"Error: target repo not found: {tgt}", file=sys.stderr)
        sys.exit(2)

    # Verify base script exists
    base_script = resolve_script_path()
    if not base_script.exists():
        print(
            f"Error: base merge script not found at {base_script}",
            file=sys.stderr,
        )
        sys.exit(3)

    # Load source bookmarks
    source_data = load_bookmarks(src)
    if not source_data["files"]:
        print("Source bookmarks file is empty — nothing to migrate.", file=sys.stderr)
        sys.exit(0)

    # Load manual remap if provided
    manual_remap = {}
    if args.remap_file:
        if args.remap_file.exists():
            with open(args.remap_file) as f:
                manual_remap = json.load(f)
        else:
            print(f"Warning: remap file not found: {args.remap_file}", file=sys.stderr)

    # Discover path remapping
    remap = {}
    unmapped = []

    for entry in source_data["files"]:
        old_path = entry.get("path", "")
        if old_path in manual_remap:
            remap[old_path] = manual_remap[old_path]
            continue

        new_path = remap_path(old_path, src, tgt)
        if new_path:
            remap[old_path] = new_path
        else:
            unmapped.append(old_path)

    # Report remapping
    print(f"Remapping: {len(remap)} paths resolved, {len(unmapped)} unresolved", file=sys.stderr)
    for old_p, new_p in sorted(remap.items()):
        print(f"  {old_p} -> {new_p}", file=sys.stderr)
    for old_p in unmapped:
        print(f"  UNMAPPED: {old_p}", file=sys.stderr)

    if unmapped and not manual_remap:
        print(
            "Some paths could not be remapped. "
            "Provide a --remap-file JSON to resolve them manually.",
            file=sys.stderr,
        )
        if not args.dry_run:
            sys.exit(4)

    if not remap:
        print("No paths could be remapped — nothing to migrate.", file=sys.stderr)
        sys.exit(0)

    # Build remapped source data
    remapped_files = []
    for entry in source_data["files"]:
        old_path = entry.get("path", "")
        if old_path in remap:
            remapped_files.append(
                {"path": remap[old_path], "bookmarks": entry.get("bookmarks", [])}
            )
        elif old_path in unmapped and manual_remap:
            # Skip unmapped entries when manual remap exists
            continue

    remapped_data = {"files": remapped_files}

    # Write temporary remapped source file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as tmp:
        json.dump(remapped_data, tmp, indent="\t")
        tmp_path = tmp.name

    # Target bookmark file
    target_bookmarks = tgt / ".vscode" / "bookmarks.json"
    output_path = str(target_bookmarks)

    if args.dry_run:
        output_path = "/dev/stdout"

    # Invoke base merge script
    cmd = [
        sys.executable,
        str(base_script),
        "--source",
        tmp_path,
        "--target",
        str(target_bookmarks),
        "--output",
        output_path,
    ]

    if args.dry_run:
        cmd.append("--dry-run")

    try:
        result = subprocess.run(cmd, capture_output=False, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Base merge script failed with exit code {e.returncode}", file=sys.stderr)
        os.unlink(tmp_path)
        sys.exit(1)

    os.unlink(tmp_path)

    if args.clean_source and not args.dry_run:
        clean_source_bookmarks(src, set(remap.keys()), dry_run=False)

    if args.dry_run:
        print("--- dry-run complete (no files written) ---", file=sys.stderr)
    else:
        print(
            f"Migration complete. Merged {len(remapped_files)} file entries into {target_bookmarks}",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
