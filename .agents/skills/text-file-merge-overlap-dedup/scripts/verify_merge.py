#!/usr/bin/env python3
"""
Verify round-trip integrity of merged file.

Reconstructs original file1 and file2 from merged file + overlap report,
compares SHA-256 hashes to original files.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path


def sha256_file(path: Path) -> str:
    """Compute SHA-256 hash of file."""
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def read_lines(path: Path) -> list[str]:
    """Read file as lines, normalize CRLF->LF."""
    content = path.read_text(encoding='utf-8')
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    lines = content.split('\n')
    if content.endswith('\n'):
        pass  # keep trailing empty string
    return lines


def write_lines(path: Path, lines: list[str]) -> None:
    """Write lines to file with LF endings."""
    content = '\n'.join(lines)
    if lines and lines[-1] == '':
        content += '\n'
    path.write_text(content, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(
        description="Verify round-trip integrity of merged file",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--merged', required=True, type=Path, help='Merged output file')
    parser.add_argument('--file1', required=True, type=Path, help='Original file1')
    parser.add_argument('--file2', required=True, type=Path, help='Original file2')
    parser.add_argument('--report', required=True, type=Path, help='Overlap report JSON from merge_overlap.py')

    args = parser.parse_args()

    # Validate inputs
    for p, name in [(args.merged, 'merged'), (args.file1, 'file1'), (args.file2, 'file2'), (args.report, 'report')]:
        if not p.exists():
            print(f"Error: {name} not found: {p}", file=sys.stderr)
            sys.exit(2)

    # Load report
    report = json.loads(args.report.read_text(encoding='utf-8'))

    # Read merged
    merged_lines = read_lines(args.merged)

    # Reconstruct file1
    if report.get("overlap_line_count", 0) > 0:
        start1 = report["overlap_start_file1"]
        overlap_len = report["overlap_line_count"]
        # file1 = merged[:start1 + overlap_len]
        recon1_lines = merged_lines[:start1 + overlap_len]
    else:
        # No overlap - file1 is first file1_lines of merged
        recon1_lines = merged_lines[:report["file1_lines"]]

    # Reconstruct file2
    if report.get("overlap_line_count", 0) > 0:
        start1 = report["overlap_start_file1"]
        # file2 = merged[start1:] (since file2 tail follows overlap in merged)
        recon2_lines = merged_lines[start1:]
    else:
        # No overlap - file2 is last file2_lines of merged
        recon2_lines = merged_lines[-report["file2_lines"]:]

    # Write reconstructions to temp files for hashing
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.tmp', encoding='utf-8') as f1:
        temp1 = Path(f1.name)
        write_lines(temp1, recon1_lines)
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.tmp', encoding='utf-8') as f2:
        temp2 = Path(f2.name)
        write_lines(temp2, recon2_lines)

    try:
        # Compute hashes
        orig1_hash = sha256_file(args.file1)
        orig2_hash = sha256_file(args.file2)
        recon1_hash = sha256_file(temp1)
        recon2_hash = sha256_file(temp2)

        print(f"Original file1 SHA-256: {orig1_hash}")
        print(f"Reconstructed file1 SHA-256: {recon1_hash}")
        print(f"Original file2 SHA-256: {orig2_hash}")
        print(f"Reconstructed file2 SHA-256: {recon2_hash}")

        ok1 = orig1_hash == recon1_hash
        ok2 = orig2_hash == recon2_hash

        if ok1 and ok2:
            print("✓ Round-trip verification PASSED")
            sys.exit(0)
        else:
            print("✗ Round-trip verification FAILED")
            if not ok1:
                print("  file1 mismatch", file=sys.stderr)
            if not ok2:
                print("  file2 mismatch", file=sys.stderr)
            sys.exit(1)

    finally:
        temp1.unlink(missing_ok=True)
        temp2.unlink(missing_ok=True)


if __name__ == '__main__':
    main()