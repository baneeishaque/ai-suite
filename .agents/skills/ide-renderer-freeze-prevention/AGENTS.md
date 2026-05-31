# IDE Renderer Freeze Prevention

> **Skill:** [`SKILL.md`](SKILL.md)

## Summary

SSOT for the bash-call-shape and tool-shape disciplines that prevent VS Code / Anti Gravity / Eclipse renderer freezes under unbounded scrollback. Owns the ten recurring freeze patterns, the eleven-item per-call self-audit checklist, and the four-step post-freeze recovery protocol.

## When the Agent Should Invoke This Skill

- Before EVERY `bash`, `edit`, or `create` tool call (apply the §5 checklist).
- Whenever a freeze occurs (follow §6 recovery protocol; do not retry).
- When authoring or editing any skill that mutates files (Pattern 6 / Pattern 4).
- When a turn has already issued ~8 content-emitting calls (Pattern 9).
- When a session approaches ~50 substantive tool calls or has been compaction-summarized (Pattern 10 — hand off to a fresh session).

## Quick Reference

Per-call self-audit (full text: [`SKILL.md` §5](SKILL.md)):

1. No chained commands (`;`, `&&`) unless a natural pipe.
2. No bash `grep -r` / `find` over a tree — use the `grep` / `glob` tools.
3. One path argument per call.
4. Heredoc body ≤ 50 lines.
5. Output bounded ≤ ~200 lines or redirected to `scratch/`.
6. Pessimistic-case output proven small.
7. No `edit` / `create` tool on > ~30-line changes.
8. Parallel batch sum within single-call budget.
9. First call of a new turn after a heavy turn is a trivial probe (`pwd`).
10. Current turn has < ~8 content-emitting calls so far.
11. Session has < ~50 substantive calls and has not been compaction-summarized.

## Key Rules

1. **One command per `bash` call.** Pipes only where natural.
2. **Use the `grep` tool**, not bash `grep -r`, for tree walks.
3. **One path per call.** Iterate at the agent level, not in shell.
4. **Split large writes** into ≤ 50-line heredoc appends or Python `pathlib.Path.write_text()`.
5. **Default pessimistic.** If the output upper bound is unprovable, redirect to [`scratch/`](../repo-scratch-output-capture/SKILL.md) or pipe to `head`.
6. **Never the `edit` / `create` tool for > ~30-line changes** — use bash heredoc or Python pathlib instead.
7. **Sum parallel-batch outputs** as one call's budget.
8. **Probe before content on every new turn after a heavy turn** (`pwd` / `ls`).
9. **Budget the WHOLE turn**, not just each call (~8-call ceiling per turn).
10. **Hand off the session** at ~50 substantive calls — Pattern 10 cannot be mitigated by per-call hygiene.
11. **After authoring §3 or §5, re-read the rule** before the next verification call (§7.9 — authoring momentum is not internalization).

## Recovery Protocol (After a Freeze)

1. Stop issuing tool calls. Wait for user acknowledgement.
2. Map the offending call to a §3 pattern number; do not rationalize.
3. Resume with one small bounded call (typically a `read_bash` to recover truncated output, or a single targeted `view` / `grep` tool call).
4. If a new pattern is revealed, propose its addition to §3 next turn.
