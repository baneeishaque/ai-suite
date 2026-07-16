#!/usr/bin/env python3
"""
batch-coverage-check.py — Given a file (or stdin) containing multiple shell
commands (one per line), extract all atomic segments, deduplicate, and produce
a coverage matrix against the is-this-command-safe safety-table.csv and the
active chat.tools.terminal.autoApprove entries.

Used during §4b (Batch Mode) of command-autoapprove-onboarding: instead of
running §4 Steps 1-7 independently for each command, the agent calls this
script first to get a unified view of which binaries are in the SSOT, which
have autoApprove coverage, and which are gaps, then plans all SSOT additions
and autoApprove edits in one consolidated pass.

Output columns (table to stdout):
    binary | ssot_verdict | ssot_row_present | autoapprove_entry | status

status values:
    COVERED          binary in SSOT + autoApprove entry covers it
    SSOT-ONLY        binary in SSOT but no autoApprove entry
    AUTOAPPROVE-ONLY entry exists but binary missing from SSOT
    GAP              neither SSOT nor autoApprove covers this binary

Usage
-----
    # From a file:
    python3 batch-coverage-check.py \
        --commands session-cmds.txt \
        --ssot .agents/skills/is-this-command-safe/docs/safety-table.csv \
        --settings "/Users/dk/Library/Application Support/Code - Insiders/User/settings.json"

    # From stdin:
    cat <<'EOF' | python3 batch-coverage-check.py --ssot safety-table.csv --settings settings.json
    git status --short
    git --no-pager log --oneline -3
    brew list --formula
    EOF

    # Gaps only (skip COVERED rows):
    python3 batch-coverage-check.py --commands cmds.txt --ssot safety-table.csv \
        --settings settings.json --gaps-only

    # SSOT check only (no autoApprove lookup):
    python3 batch-coverage-check.py --commands cmds.txt --ssot safety-table.csv \
        --no-autoapprove

Decomposition rules
-------------------
- Blank lines and lines beginning with # are skipped.
- Variable assignments (VAR=value) are skipped.
- Pipeline stages (|), chain operators (&&, ||, ;) each yield an independent segment.
- Command substitutions $(...) and backticks yield an additional segment.
- git: subcommand extracted after stripping -C <path> / --no-pager prefixes.
- git stash: includes next token (list/push/pop/apply/drop) as part of the key.
- Strip-prefix binaries (sudo, time, env, nice, nohup): recurse on remainder.

See also
--------
- SKILL.md §4b  Batch Mode (caller protocol)
- is-this-command-safe/docs/safety-table.csv  SSOT
- vscode-terminal-autoapprove-audit/scripts/find-entry.py  autoApprove lookup
"""

from __future__ import annotations
import argparse, csv, json, re, shlex, sys
from pathlib import Path

_SPLIT_RE = re.compile(r'\|\||&&|;|\|')
_PREFIX_BINARIES = {"sudo", "time", "env", "nice", "nohup", "xargs"}


def _mask_quotes(s: str) -> str:
    """Replace quoted string contents with placeholders so ; && || | inside quotes don't split."""
    result, i = [], 0
    while i < len(s):
        if s[i] in ('"', "'"):
            q, j = s[i], i + 1
            while j < len(s) and s[j] != q:
                if s[j] == '\\': j += 1
                j += 1
            result.append('X' * (j - i + 1))
            i = j + 1
        else:
            result.append(s[i])
            i += 1
    return ''.join(result)


def _strip_redirects(tok: str) -> str:
    return re.sub(r'\d?>{1,2}\S*|\d?<\S*', '', tok).strip()


def _extract_binary(segment: str) -> str | None:
    segment = segment.strip()
    if not segment:
        return None
    if re.match(r'^[A-Za-z_][A-Za-z0-9_]*=', segment):
        return None
    first = segment.split()[0]
    if first in {"if","then","else","elif","fi","for","while","do","done","case","esac","function","return","[","[["}:
        return None
    segment = re.sub(r'^([A-Za-z_][A-Za-z0-9_]*=\S+\s+)+', '', segment).strip()
    # For interpreters with -c, skip inline code (avoids false-positive token extraction)
    if re.match(r'^(python3?|node|bash|sh|ruby|perl)\s.*-c\s', segment):
        tokens = segment.split()[:2]  # only binary + -c
    else:
        try:
            tokens = shlex.split(segment, posix=True)
        except ValueError:
            tokens = segment.split()
    if not tokens:
        return None
    tokens = [_strip_redirects(t) for t in tokens if _strip_redirects(t)]
    if not tokens:
        return None
    binary = Path(tokens[0]).name
    if binary == "git":
        rest = tokens[1:]
        idx = 0
        while idx < len(rest):
            if rest[idx] in ("-C","--work-tree","--git-dir") and idx+1 < len(rest):
                idx += 2
            elif rest[idx] in ("--no-pager","--paginate","--version","--help"):
                idx += 1
            else:
                break
        if idx < len(rest) and not rest[idx].startswith("-"):
            sub = rest[idx]
            if sub == "stash" and idx+1 < len(rest) and not rest[idx+1].startswith("-"):
                sub = f"stash {rest[idx+1]}"
            binary = f"git {sub}"
    if binary == "brew":
        rest = tokens[1:]
        if rest and not rest[0].startswith("-"):
            binary = f"brew {rest[0]}"
    if binary in _PREFIX_BINARIES and len(tokens) > 1:
        return _extract_binary(" ".join(tokens[1:]))
    return binary or None


def decompose(cmdline: str) -> list[str]:
    subs = re.findall(r'\$\(([^)]+)\)|`([^`]+)`', cmdline)
    inner = [s[0] or s[1] for s in subs]
    clean = re.sub(r'\$\([^)]+\)|`[^`]+`', '', cmdline)
    # Split on operators using quote-masked positions to avoid splitting inside quoted strings
    masked = _mask_quotes(clean)
    split_points = [(m.start(), m.end()) for m in _SPLIT_RE.finditer(masked)]
    if split_points:
        prev, parts = 0, []
        for start, end in split_points:
            parts.append(clean[prev:start])
            prev = end
        parts.append(clean[prev:])
    else:
        parts = [clean]
    segments = parts + inner
    return [b for seg in segments for b in [_extract_binary(seg.strip())] if b]


def load_ssot(csv_path: Path) -> dict:
    table = {}
    with open(csv_path, newline='') as f:
        for row in csv.DictReader(f):
            key = row.get('binary','').strip().lower()
            if key:
                table[key] = row
    return table


def ssot_lookup(binary: str, table: dict) -> tuple:
    key = binary.lower()
    if key in table:
        return table[key].get('verdict',''), True
    short = key.split()[0]
    if short in table:
        return table[short].get('verdict',''), True
    return None, False


def autoapprove_entries(settings_path: Path) -> list:
    try:
        data = json.loads(settings_path.read_text())
        return list(data.get('chat.tools.terminal.autoApprove', {}).keys())
    except Exception:
        return []


def approves_binary(binary: str, keys: list) -> str | None:
    base = binary.split()[0].lower()
    sub  = binary.split()[1].lower() if len(binary.split()) > 1 else ""
    for key in keys:
        pattern = re.sub(r'^/\^?|\$?/[gimsuy]*$','', key)
        if base in pattern.lower() and (not sub or sub in pattern.lower()):
            return key
    return None


def main():
    p = argparse.ArgumentParser(description="Coverage matrix: batch commands vs SSOT + autoApprove.",
                                formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    p.add_argument("--commands", metavar="FILE", help="File with one command per line (default: stdin).")
    p.add_argument("--ssot", required=True, metavar="CSV", help="Path to safety-table.csv.")
    p.add_argument("--settings", metavar="JSON", help="Path to settings.json.")
    p.add_argument("--no-autoapprove", action="store_true", help="Skip autoApprove lookup.")
    p.add_argument("--gaps-only", action="store_true", help="Print only non-COVERED rows.")
    args = p.parse_args()

    lines = Path(args.commands).read_text().splitlines() if args.commands else sys.stdin.read().splitlines()

    all_binaries: dict[str, list] = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        for b in decompose(line):
            all_binaries.setdefault(b, []).append(line)

    ssot  = load_ssot(Path(args.ssot))
    ap_keys = autoapprove_entries(Path(args.settings)) if (not args.no_autoapprove and args.settings) else []

    print(f"{'BINARY':<42} {'VERDICT':<17} {'SSOT':<6} {'AUTOAPPROVE':<14} STATUS")
    print("-" * 104)

    counts = {"COVERED":0,"SSOT-ONLY":0,"AUTOAPPROVE-ONLY":0,"GAP":0}
    for binary in sorted(all_binaries):
        verdict, in_ssot = ssot_lookup(binary, ssot)
        ap_entry = approves_binary(binary, ap_keys) if ap_keys else None
        status = ("COVERED" if in_ssot and ap_entry else
                  "SSOT-ONLY" if in_ssot else
                  "AUTOAPPROVE-ONLY" if ap_entry else "GAP")
        counts[status] += 1
        if args.gaps_only and status == "COVERED":
            continue
        print(f"{binary:<42} {(verdict or '—')[:16]:<17} {'✓' if in_ssot else '✗':<6} "
              f"{'✓ ' + (ap_entry or '')[:11] if ap_entry else '—':<14} {status}")

    print()
    print(f"Binaries: {len(all_binaries)}  |  " +
          "  ".join(f"{k}: {v}" for k,v in counts.items()))


if __name__ == "__main__":
    main()
