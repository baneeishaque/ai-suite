# Heredoc-with-Markdown-Body Freeze (Repo-Scoped, Strict)

## Rule

NEVER embed a markdown body containing fenced code blocks or `### N.M` heading-looking lines
INSIDE a `python3 - <<'SENTINEL'` heredoc (i.e., as part of a Python triple-quoted string literal),
even when the outer sentinel appears unique. The combination stresses the IDE renderer the same way
nested heredocs do (AGENTS.md §3) and has produced full VS Code freezes requiring force-recovery.

## Safe Pattern (Mandatory)

Two-stage write:

1. Write the markdown body to a scratch file via a SINGLE clean heredoc whose sentinel does not
   appear anywhere in the body:
   `cat > /tmp/section.md <<'BODY_SENTINEL_UNIQUE'`
2. Run a tiny Python (or `awk`/`sed` for trivial inserts) that reads `/tmp/section.md` via
   `Path(...).read_text()` and splices it into the target file using LITERAL string `find()` /
   `replace()` — no regex that has to scan for heading boundaries inside the body.

## Forbidden Anti-Pattern

```text
python3 - <<'PY'
from pathlib import Path
new_section = """
### 5.5 Some Heading

```bash
example
```
"""
Path("target.md").write_text(...)
PY
```

The Python triple-quoted string contains BOTH fenced code blocks AND a `### N.M` line — this is
the freeze trigger.

## SSOT

- `.agents/skills/ide-renderer-freeze-prevention/SKILL.md` §3 Pattern (heredoc cliff family) and §7
  Pitfalls — the catalogue of freeze patterns is owned there.
- `AGENTS.md` Permanent Operating Reminder §3 — "Never nest heredocs inside heredocs" generalizes
  to "never embed sentinel-looking or fence-looking tokens in a heredoc body."

## Recovery

Force-quit VS Code; every in-flight tool call returns as `interrupted`; any pending file write
INSIDE the failed Python script did NOT execute (assertion / parse failure aborts before
`write_text()`), so target files are usually untouched. Verify with `git status` before re-running.

## Origin

Recorded after agent froze VS Code on 2026-05-31 while attempting to insert §5.5
"Section-Home Discipline" into `.agents/skills/skill-factory/SKILL.md` via a `python3 - <<'ZZZ_OUTER_ZZZ'`
heredoc whose body contained a triple-quoted Python string with both ```` ``` ```` fences and
`### 5.5` heading-looking lines. The script's `assert m` failed before `p.write_text()` so the
target file was unmodified, but the renderer froze and required force-recovery.
