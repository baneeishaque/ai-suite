#!/usr/bin/env python3
##
# AGENTS.md Recovery from Session
# 
# Applies extracted git diff from opencode session export to restore AGENTS.md
# base skill skill and restores lost skills row additions.
# 
# (Uses opencode-session-diff-extractor as base primitive for extraction)

import argparse
import subprocess
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile


def extract_session_diff(session_path: Path, temp_path: Path, file_pattern: str | None = None) -> Path:
    """Extract diff from session file using opencode-session-diff-extractor."""
    
    extract_script = Path(__file__).parent.parent.parent / "opencode-session-diff-extractor" / "scripts" / "extract-session-diff.py"
    
    if not extract_script.exists():
        msg = f"Extract script not found: {extract_script}"
        print(msg, file=sys.stderr)
        sys.exit(2)
    
    cmd = ["python3", str(extract_script), "--session", str(session_path)]
    if file_pattern:
        cmd.extend(["--file-pattern", file_pattern])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        diff_content = result.stdout
        temp_path.write_text(diff_content)
        if not diff_content.strip():
            print("Extracted diff appears empty.", file=sys.stderr)
            return 1
        print(f"Diff extracted successfully ({len(diff_content)} bytes).")
        return None
    else:
        print("Extraction failed:", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        return result.returncode


def save_diff_to_file(diff_output: str, temp_path: Path) -> None:
    """Save extracted diff to temporary file."""
    temp_path.write_text(diff_output)
    print(f"Diff saved to: {temp_path}")


def apply_diff_to_agents_md(temp_path: Path) -> bool:
    """Apply extracted diff to AGENTS.md."""
    agents_md = Path(__file__).parent.parent.parent / "AGENTS.md"
    
    if not agents_md.exists():
        print(f"AGENTS.md not found at: {agents_md}", file=sys.stderr)
        print("Please initialize the ai-suite repository first.", file=sys.stderr)
        return False
    
    cmd = ["git", "apply", "--3way", str(temp_path)]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        return True
    else:
        print("Failed to apply diff:", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        return False


def verify_ordering(agents_md: Path) -> bool:
    """Verify skills table is alphabetically ordered."""
    print("Verifying skills table ordering...")
    
    cmd = ["grep", "-A", "200", "^## Skills$", str(agents_md), "|", "head", "-n", "+7", "|", "sed", "-n", "1,200p"]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Skills table may be out of order (exit code != 0)", file=sys.stderr)
        print("Consider using text-lines-sort-by-length or manual sort fix.", file=sys.stderr)
        return False
    
    print("Skills table ordering verified.")
    return True


def check_markdownlint(agents_md: Path) -> bool:
    """Check for markdownlint errors."""
    try:
        result = subprocess.run(
            ["markdownlint", "--fix", str(agents_md)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("Markdownlint: no issues found.")
            return True
        else:
            print("Markdownlint issues found:", file=sys.stderr)
            print(result.stdout, file=sys.stderr)
            print("Fix manually or run: markdownlint --fix AGENTS.md", file=sys.stderr)
            return False
    except FileNotFoundError:
        print("Markdownlint not installed. Skipping lint check.", file=sys.stderr)
        return True


def branch_if_requested(branch_name: str | None) -> Path | None:
    """Create a new git branch if requested."""
    if not branch_name:
        return None
    
    result = subprocess.run(
        ["git", "branch", branch_name],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"Created branch: {branch_name}")
        return Path(branch_name) if result.stdout.strip() else None
    else:
        print(f"Failed to create branch '{branch_name}': {result.stderr}", file=sys.stderr)
        return None


def commit_if_requested(dry_run: bool) -> bool:
    """Commit changes if requested (and not dry run)."""
    if dry_run:
        print("Dry run: skipping commit.")
        return True
    
    result = subprocess.run(["git", "status", "--short"], capture_output=True, text=True)
    
    if "AGENTS.md" in result.stdout:
        msg = """agents-md-recovery: restore AGENTS.md from session export

        Extracted diff from session export. Restored lost skills table entries and file structure.

        See git log for full diff.
        """
        
        result = subprocess.run(
            ["git", "add", "AGENTS.md"],
            capture_output=True,
            text=True
        )
        
        result = subprocess.run(
            ["git", "commit", "-m", msg.strip()],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("Committed changes.")
            return True
        else:
            print("Failed to commit:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            return False
    else:
        print("No changes to commit (AGENTS.md not modified).")
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Restore AGENTS.md from opencode session export"
    )
    parser.add_argument(
        "--session",
        type=Path,
        required=True,
        help="Path to opencode session export (.md) with lost diff"
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Automatically commit changes after recovery"
    )
    parser.add_argument(
        "--branch",
        type=str,
        help="Create a new branch before recovery (default: agents-md-recovery-{timestamp})"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print steps without executing (no file modifications)"
    )
    parser.add_argument(
        "--file-pattern",
        type=str,
        default="AGENTS.md",
        help="Filter diff to specific file pattern (default: AGENTS.md)"
    )
    
    args = parser.parse_args()
    
    # Validate session file
    if not args.session.exists():
        print(f"Session file not found: {args.session}", file=sys.stderr)
        sys.exit(3)
    
    # Create temporary file for diff
    with NamedTemporaryFile(mode='w', suffix='.patch', delete=False) as tmp:
        temp_path = Path(tmp.name)
    
    # Extract diff
    if args.dry_run:
        print(f"[DRY RUN] Would extract diff from: {args.session}", file=sys.stderr)
        print(f"[DRY RUN] Would save to: {temp_path}", file=sys.stderr)
        print(f"[DRY RUN] Would apply to: ai-suite/AGENTS.md", file=sys.stderr)
        temp_path.unlink()
        sys.exit(0)
    
    if args.branch:
        if not branch_if_requested(args.branch):
            temp_path.unlink()
            sys.exit(1)
    
    exit_code = extract_session_diff(args.session, temp_path, args.file_pattern)
    
    if exit_code == 1:
        print("No AGENTS.md diff found in session.", file=sys.stderr)
        sys.exit(1)
    elif exit_code == 2:
        temp_path.unlink()
        sys.exit(2)
    else:
        diff_content = open(temp_path).read()
        if not diff_content.strip():
            print("Extracted diff is empty.", file=sys.stderr)
            temp_path.unlink()
            sys.exit(1)
        save_diff_to_file(diff_content, temp_path)
        
        # Apply diff
        if not apply_diff_to_agents_md(temp_path):
            temp_path.unlink()
            sys.exit(1)
        
        # Verify
        agents_md = Path(__file__).parent.parent.parent / "AGENTS.md"
        verify_ordering(agents_md)
        check_markdownlint(agents_md)
        
        # Commit
        if args.commit and not commit_if_requested(args.dry_run):
            temp_path.unlink()
            sys.exit(1)
        
        temp_path.unlink()
        print("\nRecovery complete.")
        sys.exit(0)


if __name__ == "__main__":
    main()