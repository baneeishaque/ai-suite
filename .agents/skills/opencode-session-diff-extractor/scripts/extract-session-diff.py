#!/usr/bin/env python3
"""
OpenCode Session Diff Extractor

Extract git diff blocks from opencode session export files.

Tier-1 (Python) per scripting-language-selection-rules §3.1 — pure text parsing, regex, file I/O.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Optional


def parse_session_file(session_path: Path) -> List[str]:
    """Parse opencode session markdown and extract git diff blocks."""
    content = session_path.read_text(encoding="utf-8")
    
    # Pattern: tool call blocks with bash/git diff commands and diff output
    # Session format has: **Tool: bash** followed by **Input:** with JSON containing "command"
    # Then **Output:** with the diff content
    
    diff_blocks = []
    
    # Find all tool call sections (bash commands)
    # Pattern matches: **Tool: bash** ... **Input:** ... "command": "git ... diff ..." ... **Output:** ... diff content
    tool_sections = re.split(r'\n##\s+(?:Assistant|User)', content)
    
    for section in tool_sections:
        # Check if this section contains a bash tool with git diff
        tool_match = re.search(r'\*\*Tool:\s*bash\*\*', section)
        if not tool_match:
            continue
            
        # Extract the command from Input JSON
        input_match = re.search(r'\*\*Input:\*\*\s*```json\s*(\{.*?\})\s*```', section, re.DOTALL)
        if not input_match:
            continue
            
        import json
        try:
            input_data = json.loads(input_match.group(1))
            command = input_data.get("command", "")
        except json.JSONDecodeError:
            continue
            
        # Must be a git diff command
        if "git" not in command or "diff" not in command:
            continue
            
        # Extract the diff output
        output_match = re.search(r'\*\*Output:\*\*\s*```\s*\n(.*?)\n```', section, re.DOTALL)
        if not output_match:
            continue
            
        output = output_match.group(1)
        
        # Find unified diff blocks in output
        diff_pattern = r'(diff --git a/.*?(?=\n```|\n\*\*|\n## |\Z))'
        diffs = re.findall(diff_pattern, output, re.DOTALL)
        
        for diff in diffs:
            diff = diff.strip()
            if diff.startswith("diff --git"):
                diff_blocks.append(diff)
    
    return diff_blocks


def filter_diffs_by_pattern(diffs: List[str], pattern: str) -> List[str]:
    """Filter diff hunks to only those affecting files matching the glob pattern."""
    import fnmatch
    filtered = []
    for diff in diffs:
        # Extract file paths from diff header
        header_match = re.search(r'diff --git a/(.*?) b/(.*?)\n', diff)
        if header_match:
            old_path, new_path = header_match.groups()
            if fnmatch.fnmatch(old_path, pattern) or fnmatch.fnmatch(new_path, pattern):
                filtered.append(diff)
    return filtered


def main():
    parser = argparse.ArgumentParser(
        description="Extract git diff blocks from opencode session export files"
    )
    parser.add_argument("--session", required=True, help="Path to opencode session export (.md)")
    parser.add_argument("--file-pattern", help="Glob pattern to filter diff hunks (e.g., AGENTS.md)")
    parser.add_argument("--output", help="Write diff to file instead of stdout")
    
    args = parser.parse_args()
    
    session_path = Path(args.session)
    if not session_path.exists():
        print(f"Error: Session file not found: {session_path}", file=sys.stderr)
        sys.exit(3)
    
    print(f"Parsing session: {session_path}", file=sys.stderr)
    diffs = parse_session_file(session_path)
    
    if not diffs:
        print("No git diff blocks found in session", file=sys.stderr)
        sys.exit(1)
    
    print(f"Found {len(diffs)} diff block(s)", file=sys.stderr)
    
    if args.file_pattern:
        original_count = len(diffs)
        diffs = filter_diffs_by_pattern(diffs, args.file_pattern)
        print(f"Filtered to {len(diffs)} diff block(s) matching '{args.file_pattern}'", file=sys.stderr)
        if not diffs:
            print(f"No diffs match pattern '{args.file_pattern}'", file=sys.stderr)
            sys.exit(1)
    
    output_text = "\n\n".join(diffs) + "\n"
    
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(output_text, encoding="utf-8")
        print(f"Diff written to: {output_path}", file=sys.stderr)
    else:
        sys.stdout.write(output_text)


if __name__ == "__main__":
    main()