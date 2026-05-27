# Text Lines Sort By Length — Agent Bridge

Companion to [`SKILL.md`](./SKILL.md). This bridge exposes the operational
contract for sub-agents that need to invoke the primitive without reading
the full skill prose.

## Quick Invocation

```bash
python3 .agents/skills/text-lines-sort-by-length/scripts/text-lines-sort-by-length.py \
  --file <input> \
  [--header-lines N] [--reverse] [--drop-blank] \
  [--output PATH | --in-place [--no-backup]] [--dry-run]
```

## Decision Points

| User says… | Flags |
| :--- | :--- |
| "Sort shortest first" / unspecified order | (default) |
| "Sort longest first" / "descending" | `--reverse` |
| "Keep the first comment / shebang at top" | `--header-lines 1` (or N) |
| "Drop blank lines" | `--drop-blank` |
| "Write to a scratch file" | `--output <scratch>` |
| "Rewrite in place" | `--in-place` (creates `.bak`) |
| "Just show me" | `--dry-run` |

## Pre-Step

When the input contains `\<newline>`-continued bash lines, run
[bash-multiline-to-single-line](../bash-multiline-to-single-line/SKILL.md)
first so the length comparison reflects logical commands rather than
physical fragments.

## Exit Codes

- `0` — success or dry-run
- `1` — file missing, invalid `--header-lines`, or `--in-place` + `--output` collision
