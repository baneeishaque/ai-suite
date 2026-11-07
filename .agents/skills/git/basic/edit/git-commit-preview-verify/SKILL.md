---
name: git-commit-preview-verify
description: Verify commit-preview titles against Git history and optionally delegate authorized cleanup, failing closed without macOS Trash.
category: Git & Repository Management
---

# Git Commit Preview Verify Skill

> **Skill ID:** `git-commit-preview-verify`<br>
> **Version:** 1.0.0<br>
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)

## Description

Provides a deterministic, domain-agnostic primitive for verifying
whether the commits listed in a commit-preview markdown file have been
executed against git history. It parses the standard §2d preview format
produced by [`git-atomic-commit-construction`](../../../../git-atomic-commit-construction/SKILL.md),
cross-references each `Commit N:` title against `git log --oneline`, and
reports each arranged commit as `done` or `pending`.

The primitive supports human-readable text output and machine-readable
JSON. Optional `--cleanup` delegates removal only when no listed commit
is pending. Title matching is evidence for a caller's completion audit,
not proof that the committed contents or all plan actions are correct.

## Composition Rationale

Verification remains a standalone, read-only primitive. Its optional
cleanup mode composes
[`safe-file-cleanup`](../../../../general/file/safe-file-cleanup/SKILL.md)
through that skill's `scripts/safe_cleanup.py <preview> --json` CLI.
The helper path is anchored to this script's location, so another working
directory does not change the selected implementation. The caller owns
content/coverage/reference checks and consent; this script owns pending
commit refusal, the macOS Trash preflight, and cleanup-result verification.

## Environment & Dependencies

| Requirement | Minimum |
| --- | --- |
| Git | 2.x |
| Python | 3.12+ |
| safe-file-cleanup | Required only with `--cleanup`; sibling helper must exist |
| macOS `trash` | Required for macOS cleanup; no permanent-removal fallback |

Verify:

```bash
git --version
python3 --version
```

## When to Apply

Apply this skill when:

- A user points to an existing `scratch/commit-preview.md` and asks "is
  this done?" or "check if these commits were made".
- Resuming a session that previously generated a commit preview but may
  not have executed all commits.
- Auditing whether a planned commit sequence was fully executed.
- Cleaning up a stale preview file after all commits are confirmed
  executed.

Do NOT apply when:

- The preview has not been written yet — use
  [`git-atomic-commit-construction`](../../../../git-atomic-commit-construction/SKILL.md)
  §2d to generate it first.
- The user wants to verify individual commit content — use
  [`git-commit-metadata-extraction`](../../../../git-commit-metadata-extraction/SKILL.md).
- The user wants to split or rewrite existing commits — use
  [`git-history-refinement`](../../../../git-history-refinement/SKILL.md).

## Scripts (Public CLI Contract)

The deterministic Tier-A primitive is
[`scripts/verify-commit-preview.py`](scripts/verify-commit-preview.py)
per `script-over-instruction-decomposition`. It is read-only by default
and never mutates the working tree unless `--cleanup` is passed with all
commits done.

```bash
python3 scripts/verify-commit-preview.py --preview <path> [--repo <path>] [--format text|json] [--cleanup]
```

| Flag | Meaning |
| --- | --- |
| `--preview PATH` | Path to the commit-preview markdown file (required) |
| `--repo PATH` | Git repository root (default: auto-detect from CWD) |
| `--format text\|json` | Output format (default: `text`) |
| `--window N` | `git log` window size in commits (default: 50) |
| `--cleanup` | Delegate retirement after caller approval/coverage checks and zero pending commits |

### Examples

```bash
# Text report (default)
python3 scripts/verify-commit-preview.py --preview scratch/commit-preview.md

# Machine-readable JSON
python3 scripts/verify-commit-preview.py --preview scratch/commit-preview.md --format json

# After caller coverage checks and retirement consent
python3 scripts/verify-commit-preview.py --preview scratch/commit-preview.md --cleanup
```

### Exit Codes

| Code | Meaning |
| --- | --- |
| 0 | All commits verified as executed |
| 1 | One or more commits not found in git log |
| 2 | Preview file not found or unreadable |
| 3 | Not inside a git repository (and `--repo` not provided / invalid) |
| 4 | Preview file contains no parseable commit entries |
| 5 | Cleanup helper missing, unavailable, failed, timed out, or did not verify removal |

### Input / Output Format

The parser accepts the §2d preview's `Commit N:` section headers at any
heading level (`## Commit 1: <title>` or `### Commit 1: <title>`). For
each entry it records `{ index, title, status, sha }`. `status` is
`done` when the title matches a line of `git log --oneline -<window>`
(returning that line's SHA), otherwise `pending` with a null SHA.

Text output:

```text
Commit Preview Verification
==========================
Preview: scratch/commit-preview.md
Repository: <repo-root>

 #  Status   SHA       Title
 1  done     abc1234   docs(example): describe preview verification

Result: 1/1 commits executed
```

JSON output:

```json
{
  "preview_file": "scratch/commit-preview.md",
  "repo": "<repo-root>",
  "total": 1,
  "done": 1,
  "pending": 0,
  "commits": [
    { "index": 1, "title": "docs(example): describe preview verification", "status": "done", "sha": "abc1234" }
  ]
}
```

### Cleanup Semantics

- Before invoking `--cleanup`, the caller verifies actual commit contents,
  all actions within this preview's scope, inbound references, and explicit
  retirement consent. A finished preview does not complete an unfinished
  parent plan; retain current plans with open work.
- Pending commits refuse cleanup with exit 1 and no disposal call.
- A missing helper or missing macOS `trash` fails closed with exit 5.
- The helper runs under the same Python interpreter with an absolute
  preview path and a 30-second timeout. Nonzero exit, malformed JSON,
  a status other than `removed`, or a still-existing preview returns exit 5.
  Inspect the path after a helper failure; never infer removal or retry blindly.
- Without `--cleanup`, the existing JSON verification shape is unchanged.
  With it, `cleanup.status` is `removed`, `refused`, or `failed`.
  JSON stdout remains one valid report; diagnostics go to stderr. Text
  mode prints `Cleaned up: <path>` only after verified removal.
- On other platforms, disposal follows the base skill's backend policy.
  This caller adds a macOS fail-closed guard; it does not change the base.

## Verification

Run [scripts/test-preview-cleanup.py](scripts/test-preview-cleanup.py) with
`TEST_ARTIFACT_DIR` set to an existing session-scratch directory. Tests cover
read-only defaults, pending refusal, missing helper/Trash, delegated success,
invalid results, helper errors, and invocation from a different working directory.
Disposal is mocked as a fixture move; no user preview or actual Trash is touched.
The source fixture lives in [preview-cleanup-fixture.md.template](scripts/preview-cleanup-fixture.md.template).

```bash
python3 scripts/test-preview-cleanup.py
```

## Composition by Higher-Level Skills

| Composer | Composition Mechanism |
| --- | --- |
| [`git-atomic-commit-construction`](../../../../git-atomic-commit-construction/SKILL.md) | Invoked in §2d.2 for post-execution verification of arranged commits and preview cleanup |

## Related Skills

- [`git-commit-metadata-extraction`](../../../../git-commit-metadata-extraction/SKILL.md)
  — for extracting individual commit metadata.
- [`git-hunk-staging-primitives`](../../../../git-hunk-staging-primitives/SKILL.md)
  — sibling base skill for hunk-based staging during commit construction.
- [`repo-scratch-output-capture`](../../../../repo-scratch-output-capture/SKILL.md)
  — for managing the `scratch/` directory where previews live.

## Traceability

See [TRACEABILITY.md](TRACEABILITY.md).

## Changelog

See [CHANGELOG.md](CHANGELOG.md).
