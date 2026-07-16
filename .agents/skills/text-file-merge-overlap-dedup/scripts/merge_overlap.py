#!/usr/bin/env python3
"""
Merge two text files with overlapping content at the boundary.

Uses suffix/prefix matching to detect the overlap region where the end of file1
matches the start of file2, and produces a deduplicated merge.

Tier 1 (Python 3.12+) per Scripting Language Selection Rules §3-§5.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Dict


class NoOverlapError(Exception):
    """Raised when no sufficient overlap is found."""
    pass


def read_lines(path: Path) -> List[str]:
    """Read file as lines, normalize CRLF->LF, preserve trailing newline semantics."""
    content = path.read_text(encoding='utf-8')
    # Normalize line endings
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    # Split preserving trailing empty line if file ends with newline
    lines = content.split('\n')
    # If original ended with newline, split() produces an extra empty string at end
    # We want to preserve that as a line
    if content.endswith('\n'):
        # Last element is empty string from trailing newline - keep it
        pass
    return lines


def write_lines(path: Path, lines: List[str]) -> None:
    """Write lines to file with LF endings."""
    content = '\n'.join(lines)
    # Ensure trailing newline if original had one (we detect by last line being empty)
    if lines and lines[-1] == '':
        content += '\n'
    path.write_text(content, encoding='utf-8')


def find_overlap(
    lines1: List[str],
    lines2: List[str],
    min_overlap: int,
    max_window: int = 5000
) -> Tuple[int, int, int]:
    """
    Find longest common contiguous line sequence where SUFFIX of lines1 matches PREFIX of lines2.

    This is the boundary-specific overlap we need for split file merging:
    - lines1 end overlaps with lines2 start
    - The match in lines2 MUST start at index 0 (prefix)
    - The match in lines1 must be a suffix (ending at the last line)

    Returns (start1, 0, length) where:
    - start1: index in lines1 where overlap begins
    - 0: always 0 for lines2 (prefix match)
    - length: number of overlapping lines

    Raises NoOverlapError if no overlap >= min_overlap found.
    """
    # We need: suffix of lines1 == prefix of lines2
    # So we search for k where lines1[-k:] == lines2[:k]
    
    max_possible = min(len(lines1), len(lines2), max_window)
    
    # Search from longest possible down to min_overlap
    for k in range(max_possible, min_overlap - 1, -1):
        # Check if suffix of lines1 (length k) equals prefix of lines2 (length k)
        if lines1[-k:] == lines2[:k]:
            start1 = len(lines1) - k
            return (start1, 0, k)

    raise NoOverlapError(f"No suffix/prefix overlap >= {min_overlap} lines found")


def merge_files(
    file1: Path,
    file2: Path,
    output: Path,
    min_overlap: int,
    report_path: Optional[Path]
) -> Dict:
    """Main merge logic. Returns report dict."""
    lines1 = read_lines(file1)
    lines2 = read_lines(file2)

    try:
        start1, start2, overlap_len = find_overlap(lines1, lines2, min_overlap)
    except NoOverlapError as e:
        # No overlap - just concatenate
        merged = lines1 + lines2
        write_lines(output, merged)
        report = {
            "file1_lines": len(lines1),
            "file2_lines": len(lines2),
            "overlap_start_file1": None,
            "overlap_start_file2": None,
            "overlap_line_count": 0,
            "merged_lines": len(merged),
            "algorithm": "suffix-prefix-match",
            "min_overlap_lines": min_overlap,
            "status": "no_overlap_concatenated"
        }
        if report_path:
            report_path.write_text(json.dumps(report, indent=2))
        else:
            print(json.dumps(report, indent=2))
        return report

    # Build merged: file1 + file2[overlap_len:]
    merged = lines1 + lines2[overlap_len:]
    write_lines(output, merged)

    report = {
        "file1_lines": len(lines1),
        "file2_lines": len(lines2),
        "overlap_start_file1": start1,
        "overlap_start_file2": start2,
        "overlap_line_count": overlap_len,
        "merged_lines": len(merged),
        "algorithm": "suffix-prefix-match",
        "min_overlap_lines": min_overlap,
        "status": "overlap_removed"
    }

    if report_path:
        report_path.write_text(json.dumps(report, indent=2))
    else:
        print(json.dumps(report, indent=2))

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Merge two text files with overlap deduplication",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 merge_overlap.py --file1 part1.txt --file2 part2.txt --output merged.txt
  python3 merge_overlap.py --file1 a.log --file2 b.log --output merged.log --min-overlap-lines 5 --report-json report.json
        """
    )
    parser.add_argument('--file1', required=True, type=Path, help='First file (earlier part)')
    parser.add_argument('--file2', required=True, type=Path, help='Second file (later part)')
    parser.add_argument('--output', required=True, type=Path, help='Merged output file')
    parser.add_argument('--min-overlap-lines', type=int, default=10, help='Minimum contiguous matching lines to qualify as overlap (default: 10)')
    parser.add_argument('--report-json', type=Path, help='Path to write overlap metadata JSON (default: stdout)')

    args = parser.parse_args()

    # Validate inputs
    if not args.file1.exists():
        print(f"Error: file1 not found: {args.file1}", file=sys.stderr)
        sys.exit(2)
    if not args.file2.exists():
        print(f"Error: file2 not found: {args.file2}", file=sys.stderr)
        sys.exit(2)
    if args.min_overlap_lines < 1:
        print("Error: --min-overlap-lines must be >= 1", file=sys.stderr)
        sys.exit(3)

    # Ensure output directory exists
    args.output.parent.mkdir(parents=True, exist_ok=True)

    try:
        report = merge_files(args.file1, args.file2, args.output, args.min_overlap_lines, args.report_json)
        if report["status"] == "overlap_removed":
            print(f"Success: merged {report['file1_lines']} + {report['file2_lines']} lines, removed {report['overlap_line_count']} line overlap -> {report['merged_lines']} lines", file=sys.stderr)
        else:
            print(f"Success: concatenated {report['file1_lines']} + {report['file2_lines']} lines (no overlap) -> {report['merged_lines']} lines", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()