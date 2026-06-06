#!/usr/bin/env python3
"""TypeScript Import Formatting Tool.

Tier: Python 3.12+.

This script rewrites single-line TypeScript/TSX named imports with two or more
specifiers into multiline import blocks. It preserves default imports and
namespace imports, and skips imports that already span multiple lines.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

IMPORT_RE = re.compile(
    r'^(?P<indent>[ \t]*)import\s+'
    r'(?:(?P<prefix>[^\{\n]+?)\s*,\s*)?'
    r'\{\s*(?P<names>[^}]*?)\s*\}'
    r'\s*from\s*(?P<from>["\'][^"\']+["\'])'
    r'(?P<semicolon>\s*;?)\s*$',
    re.MULTILINE,
)


def rewrite_import_line(match: re.Match[str]) -> str:
    indent = match.group('indent') or ''
    prefix = match.group('prefix') or ''
    names = match.group('names')
    source = match.group('from')
    semicolon = ';' if match.group('semicolon') and ';' in match.group('semicolon') else ''

    if '\n' in names or '//' in names or '/*' in names:
        return match.group(0)

    specs = [specifier.strip() for specifier in names.split(',') if specifier.strip()]
    if len(specs) <= 1:
        return match.group(0)

    middle = ',\n'.join(f'  {specifier}' for specifier in specs) + ','
    if prefix:
        return f"{indent}import {prefix}, {{\n{middle}\n}} from {source}{semicolon}"
    return f"{indent}import {{\n{middle}\n}} from {source}{semicolon}"


def rewrite_file_contents(text: str) -> str:
    return IMPORT_RE.sub(rewrite_import_line, text)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Format TypeScript/TSX named imports into multiline blocks.')
    parser.add_argument('--file', '-f', required=True, help='Path to the TypeScript/TSX file.')
    parser.add_argument('--dry-run', action='store_true', help='Print whether the file would change, but do not write it.')
    parser.add_argument('--backup', action='store_true', help='Create a .bak backup before writing changes.')
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    path = pathlib.Path(args.file)
    if not path.exists() or not path.is_file():
        print(f'ERROR: File not found: {path}', file=sys.stderr)
        return 1

    if path.suffix not in {'.ts', '.tsx', '.js', '.jsx'}:
        print(
            f'ERROR: Unsupported file extension {path.suffix}. Supported extensions: .ts, .tsx, .js, .jsx.',
            file=sys.stderr,
        )
        return 1

    text = path.read_text(encoding='utf-8')
    rewritten = rewrite_file_contents(text)

    if rewritten == text:
        print('No multiline named-import rewrites were needed.')
        return 0

    if args.dry_run:
        print('The file would be updated to multiline named imports.')
        return 0

    if args.backup:
        backup_path = path.with_suffix(path.suffix + '.bak')
        backup_path.write_text(text, encoding='utf-8')
        print(f'Backup saved to {backup_path}')

    path.write_text(rewritten, encoding='utf-8')
    print(f'Updated imports in {path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
