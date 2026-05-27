---
name: separate-content-from-formatting-commits
description: When a file's diff mixes reformatting with semantic changes, build N intermediate states — one per content change in the original format — commit each atomically, then optionally finish with a pure style reformat commit.
category: Git & Repository Management
---

# Separate Content Changes from Formatting Commits

This skill is fully documented in
[`SKILL.md`](SKILL.md).

## Trigger

Activate this skill whenever:

- A file's `git diff` is polluted by formatter noise (indent style change,
  key sorting, trailing newlines) mixed with real semantic changes.
- The user asks to "commit each change separately" but `git add -p` is
  unreliable because the format changes are pervasive.

## Quick-Start

```bash
# 1. Capture baseline
git show HEAD:<file> > /tmp/baseline.txt

# 2. Write edits.json describing each semantic change
# 3. Run the builder
python3 .agents/skills/separate-content-from-formatting-commits/scripts/build-states-textual.py \
  --baseline /tmp/baseline.txt \
  --edits    /tmp/edits.json \
  --out-dir  /tmp/states \
  --target   <working-tree-file>

# 4. cp state-N.out → file; git add; git commit  (repeat per state)
# 5. Optional: git add <file>; git commit -m "style: reformat"
```

See [`SKILL.md`](SKILL.md) for the full step-by-step procedure and script
flag reference.
