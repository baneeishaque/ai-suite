---
name: git-remote-ref-reachability-primitives
description: Read-only Git primitives for proving whether a commit or branch is reachable
  from any configured remote, resolving the newest remote-resident ancestor, and
  live-probing a remote ref — each verdict carrying the caveat that a cached remote-tracking
  ref proves only fetched state.
category: Git-Hygiene
---

# Git Remote Ref Reachability Primitives (v1)

> **Skill ID:** `git-remote-ref-reachability-primitives`<br>
> **Version:** 1.0.0<br>
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)<br>
> **Layer:** Base (per [skill-factory §2.0 Layering Decision](../../../../skill-factory/SKILL.md))

## Description

Read-only primitives that answer three questions this repository's Git skills previously
answered ad hoc, with no SSOT:

1. Is this commit present in **any** configured remote — and does this branch track an upstream?
2. What is the **newest ancestor** of this branch that is already resident in any remote?
3. Does this remote branch currently **exist** (live, not cached-ref)?

Branch **naming-convention discovery** is deliberately NOT here. It is a separate question
with a separate consumer, and lives in
[`git-remote-branch-convention-discovery`](../../../config/git-remote-branch-convention-discovery/SKILL.md).

Every script here is read-only: none fetches, pushes, or mutates any ref, index, or
working tree. Mutating remote operations are owned by
[`git-remote-branch-lifecycle`](../../../repo/git-remote-branch-lifecycle/SKILL.md).

## Composition Rationale

This skill is a **base**: it owns only the deterministic Git query mechanics and emits
JSON verdicts. It is domain-agnostic over the Git transport — a caller may point it at a
main repository, a linked worktree git dir, or a submodule checkout via `--repo`.

The domain-specific *decision* logic — which remote to push to, what to name a branch,
when a rename is safe, whether the user consented to a local rename — belongs to the
composer, not here.

Inlining these probes into a composer is FORBIDDEN: the caveat text, the boundary
resolution, and the grouping inference are the reusable parts, and duplicated copies
silently drift.

Bidirectional discoverability: the composer lists this skill in its `## Composition
Rationale`; this skill lists it in `## Composition by Higher-Level Skills`.

## 1. Environment & Dependencies

| Requirement | Minimum | Verification |
| :--- | :--- | :--- |
| Python | 3.9+ (stdlib-only scripts) | `python3 --version` |
| git | any modern version | `git --version` |
| Network reachability | only for the Tier 2 and live probes | `git ls-remote --exit-code <remote>` |

Verification commands:

```bash
python3 -c "import json, os, re, subprocess, sys; print('stdlib OK')"
git --version
```

Scripts set `PAGER=cat` in the child environment themselves, so no caller-side
`PAGER=cat` prefix is required (adding one is harmless).

## 2. Operational Logic

All three scripts take `--repo` (default `.`) so a caller can target a linked-worktree git
dir such as `.git/modules-worktrees/<name>` without changing the process CWD.

### 2.1 Two-tier commit availability and branch tracking

```bash
python3 scripts/commit-remote-availability.py --repo <repo> --sha <sha> --branch <branch>
```

Emits `cached` (from `git branch -r --contains` over fetched refs), `live` (from
`git ls-remote --heads` per configured remote), a `verdict`, a mandatory `caveat` string,
and — when `--branch` is supplied — a `tracking` block with the three signals
(`branch -vv` `[upstream]` marker, `status -sb` `...` header, `branch.<name>.*` config).

The `caveat` field is the point of the skill: an empty `branch -r --contains` means "in
no **fetched** remote-tracking ref", never "absent from the remote". Callers MUST NOT
report a cached-only verdict as an absolute negative.

Use `--no-live` when the remote is unreachable and the cached tier is all that is
available; the verdict then carries the `_CACHED_ONLY` suffix.

### 2.2 Newest remote-resident ancestor

```bash
python3 scripts/newest-remote-resident-ancestor.py --repo <repo> --branch <branch>
```

Enumerates local-only commits via `git log --format=%H%x09%s <branch> --not --remotes`,
resolves the parent of the OLDEST local-only commit as the boundary, and reports which
remote branches carry it.

| Verdict | Meaning |
| :--- | :--- |
| `HEAD_REMOTE_RESIDENT` | The tip itself is already in a remote; no local-only commits. |
| `NEWEST_REMOTE_RESIDENT` | A boundary commit resolved and is carried by at least one remote branch. |
| `NO_REMOTE_RESIDENT_ANCESTOR` | The whole history is local-only (boundary would be the root commit). |

The emitted `caveat` records that `--not --remotes` subtracts only FETCHED refs.

### 2.3 Live remote-ref probe

```bash
python3 scripts/verify-remote-ref-live.py --repo <repo> --remote <remote> --branch <branch> \
    [--expect present|absent]
```

Wraps `git ls-remote --heads <remote> <branch>` into an explicit `PRESENT` / `ABSENT`
verdict. With `--expect`, the exit code becomes a gate: `0` when observed state matches
expectation, `1` when it contradicts, `2` when the remote is unreachable, `3` on a bad
invocation. Use it to prove a push or a delete landed instead of trusting cached refs.

## 3. Scripts

| Script | Role | Exit codes |
| :--- | :--- | :--- |
| `scripts/commit-remote-availability.py` | Two-tier commit availability + branch tracking | `0` verdict emitted · `2` remote unreachable (live tier) · `3` commit not found |
| `scripts/newest-remote-resident-ancestor.py` | Local-only sweep + boundary resolution | `0` verdict emitted · `2` rev-list failed · `3` rev not resolvable |
| `scripts/verify-remote-ref-live.py` | Single-ref live EXISTS/ABSENT gate | `0` match (or no `--expect`) · `1` expectation contradicted · `2` remote unreachable |

All three are Tier-1 Python (stdlib only) per
[scripting-language-selection-rules](../../../../../../ai-agent-rules/scripting-language-selection-rules.md)
§3 and §4. Each module docstring carries the tier citation.

## 4. Safety

- Read-only by construction: no script performs `fetch`, `push`, `add`, `commit`, or any
  write to a ref, index, or working tree.
- No script executes a caller-supplied command string — arguments are passed as argv
  lists to `subprocess`, so there is no shell-injection surface.
- Every script emits its `caveat` field so a cached-ref verdict can never be silently
  promoted to an absolute negative by a consuming skill.
- Diagnostics go to stderr; stdout carries only the JSON verdict.

## 5. Composition by Higher-Level Skills

| Composer | Composition Mechanism |
| :--- | :--- |
| [`git-remote-branch-lifecycle`](../../../repo/git-remote-branch-lifecycle/SKILL.md) | §2.1 supplies the pre-push availability and post-push tracking verdicts; §2.3 supplies the post-push and post-delete live proofs; §2.2 supplies the pre-rename backup boundary. |

## Related Skills

- [`git-remote-branch-lifecycle`](../../../repo/git-remote-branch-lifecycle/SKILL.md) — the
  mutating composer over these primitives (first push, remote rename, remote delete).
- [`git-repository-status`](../../../../git-repository-status/SKILL.md) — the sibling
  read-only status surface; its `branch -vv` step does not perform availability or
  tracking verdicts, which live here.
- [`git-divergence-audit`](../../../../git-divergence-audit/SKILL.md) — pairwise
  two-branch divergence; this skill's §2.2 is the multi-remote boundary sweep it lacks.
- [`git-worktree-state-fingerprint`](../git-worktree-state-fingerprint/SKILL.md) — working-tree
  fingerprint primitive that a composer pairs with §2.2 before a destructive operation.
- [`is-this-command-safe`](../../../../is-this-command-safe/SKILL.md) — destructive-flag
  classification for the mutating git commands a composer issues.

## 6. Traceability

See [TRACEABILITY.md](TRACEABILITY.md).

## 7. Changelog

See [CHANGELOG.md](CHANGELOG.md).
