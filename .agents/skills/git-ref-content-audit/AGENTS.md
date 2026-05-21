---
name: git-ref-content-audit (bridge)
description: AGENTS.md bridge directing agents to SKILL.md for the bulk per-file blob-equality audit between two Git refs.
category: Git & Repository Management
---

# Git Ref Content Audit — Skill Bridge

This file is a thin pointer. The active source-of-truth is [`SKILL.md`](SKILL.md).

## When to use

Apply [`git-ref-content-audit`](SKILL.md) when you need to verify, file-by-file, that
every path captured by one Git ref (most often a stash with an untracked tree) is
present byte-identically in another ref (most often `HEAD`). Produces an
IDENTICAL / DIFFERENT / MISSING classification and a disposition verdict.

## Trigger phrases

- "Is this stash safe to drop?"
- "Has commit X been fully absorbed into branch Y?"
- "Compare every file in stash@{N} with HEAD."
- "Verify supersession before retiring this backup branch."

## Quick-start

```bash
python3 .agents/skills/git-ref-content-audit/scripts/audit-ref-content.py \
    --repo /path/to/repo \
    --stash "<message substring or index or stash@{N}>" \
    --show-diffs
```

For ref-vs-ref (no stash):

```bash
python3 .agents/skills/git-ref-content-audit/scripts/audit-ref-content.py \
    --repo /path/to/repo \
    --ref-a <commit-or-branch> \
    --ref-b <commit-or-branch>
```

See [`SKILL.md`](SKILL.md) for the full procedure, exit codes, and the disposition matrix.
