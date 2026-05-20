# Git Cross-Ref File Parity — Agent Bridge

This file registers the `git-cross-ref-file-parity` skill for agent discovery.

## Skill

| Field | Value |
| :--- | :--- |
| **Name** | Git Cross-Ref File Parity |
| **ID** | `git-cross-ref-file-parity` |
| **SKILL.md** | [`SKILL.md`](SKILL.md) |
| **Category** | Git & Repository Management |

## Trigger Phrases

Invoke this skill when the user says any of:

- "does the commit have the same changes as the stash?"
- "are the changes in commit X equal to the changes in stash Y?"
- "compare the diff on `<file>` between a commit and a stash"
- "check if stash can be dropped because commit already has those changes"
- "verify the cherry-pick reproduced the same change to `<file>`"
- "is the diff for `<file>` in ref A the same as ref B?"

## Script

```bash
python3 .agents/skills/git-cross-ref-file-parity/scripts/compare-file-diff.py \
    --repo   <repo-path> \
    --commit <SHA> \
    --stash  <stash-name-or-ref> \
    --file   <file-path>
```
