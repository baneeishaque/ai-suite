---
name: git-remote-branch-convention-discovery
description: Read-only primitive that infers a remote's own branch naming and grouping
  convention from its live heads — grouping prefixes, per-prefix counts, the dominant
  prefix, and the outliers that break it — so a branch is named after what the remote
  actually follows rather than a hardcoded assumption.
category: Git-Hygiene
---

# Git Remote Branch Convention Discovery (v1)

> **Skill ID:** `git-remote-branch-convention-discovery`<br>
> **Version:** 1.0.0<br>
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)<br>
> **Layer:** Base (per [skill-factory §2.0 Layering Decision](../../../skill-factory/SKILL.md))

## Description

One read-only primitive, and it answers one question: **what branch naming and grouping
scheme does this remote actually follow?**

Convention-ownership skills in this repository state their convention as an axiom — "the
`personal/` prefix is required" — which teaches nothing about a remote whose scheme you
have not confirmed. This skill closes that gap by making the remote itself the authority:
it enumerates live heads and reports what they reveal.

Deliberately separate from
[`git-remote-ref-reachability-primitives`](../../basic/audit/git-remote-ref-reachability-primitives/SKILL.md).
Reachability asks *does this commit/ref exist*; convention discovery asks *how is this
remote organized*. The two have separate reusability and separate consumers, and merging
them left the merged name unable to describe both, which the
[Skill-Name Precision Mandate](../../../../../ai-agent-rules/ai-rule-standardization-rules.md)
forbids.

## Composition Rationale

This skill is a **base**: it owns one deterministic inference and emits one JSON verdict.
It does not choose the `<purpose>` segment of a name — that is a content judgement
belonging to the caller — and it does not push, rename, or delete anything.

Inlining the inference into a composer is FORBIDDEN: the prefix-bucketing rule and the
`dominant_prefix` verdict vocabulary must stay single-sourced so two composers cannot
disagree about what a remote's convention is.

Bidirectional discoverability: every consumer lists this skill in its `## Composition
Rationale`; this skill lists them in `## Composition by Higher-Level Skills`.

## 1. Environment & Dependencies

| Requirement | Minimum | Verification |
| :--- | :--- | :--- |
| Python | 3.9+ (stdlib-only script) | `python3 --version` |
| git | any modern version | `git --version` |
| Network reachability | required (reads live remote heads) | `git ls-remote --exit-code <remote>` |

```bash
python3 -c "import argparse, collections, json, os, subprocess, sys; print('stdlib OK')"
```

The script sets `PAGER=cat` in the child environment itself, so no caller-side prefix is
required.

## 2. Operational Logic

```bash
python3 scripts/discover-remote-branch-convention.py --repo <repo> --remote <remote>
```

Runs `git ls-remote --heads <remote>` and reports:

| Field | Meaning |
| :--- | :--- |
| `total_heads` | Number of live branch refs on the remote |
| `groupings` | Per-prefix buckets — `prefix`, `count`, up to 3 `examples` |
| `dominant_prefix` | Highest-count grouping prefix, or `null` when the remote has none |
| `ungrouped` / `outliers` | Branch names with no prefix; the outliers are what break the convention |
| `recommended_name_hint` | Mechanical form `<dominant_prefix><purpose>`, or `<branch-name>` when there is no prefix |
| `heads` | The full sorted branch list |

**`recommended_name_hint` is a mechanical hint, not a decision.** The `<purpose>` segment
must describe the branch's CONTENT, never the session or ticket that created it, and never
a worktree-local name. A worktree branch called `t19` must not become `t19` on the remote.

**`dominant_prefix: null` is a real answer, not a failure.** A remote with flat branch
names yields no prefix and no recommendation; name for that remote by explicit user
instruction instead of guessing.

The emitted `caveat` field records that the convention was inferred at probe time and
should be re-verified before a rename.

## 3. Scripts

| Script | Role | Exit codes |
| :--- | :--- | :--- |
| `scripts/discover-remote-branch-convention.py` | Grouping-prefix inference from live heads | `0` convention emitted · `2` remote unreachable |

Tier-1 Python (stdlib only) per
[scripting-language-selection-rules](../../../../../ai-agent-rules/scripting-language-selection-rules.md)
§3 and §4. The module docstring carries the tier citation.

## 4. Safety

- Read-only by construction: the script runs `git ls-remote` and nothing else. It never
  fetches, pushes, or mutates any ref, index, or working tree.
- No caller-supplied command is ever executed; arguments are passed as an argv list.
- Diagnostics go to stderr; stdout carries only the JSON verdict.

## 5. Composition by Higher-Level Skills

| Composer | Composition Mechanism |
| :--- | :--- |
| [`git-remote-branch-lifecycle`](../../repo/git-remote-branch-lifecycle/SKILL.md) | §2 Phase 1 Step 1 discovers the target remote's convention BEFORE a first push or a rename, so the remote's live heads — not a hardcoded axiom — decide the branch name. |

## Related Skills

- [`git-remote-ref-reachability-primitives`](../../basic/audit/git-remote-ref-reachability-primitives/SKILL.md)
  — sibling read-only base owning commit/ref reachability; deliberately NOT merged with this skill.
- [`git-personal-sandbox-remote`](../../../git-personal-sandbox-remote/SKILL.md) — states
  this repository's `personal/` convention and points here to discover a different remote's.
- [`git-remote-branch-lifecycle`](../../repo/git-remote-branch-lifecycle/SKILL.md) — the
  mutating composer that consumes this primitive.
- [`git-remote-origin-repoint`](../../repo/git-remote-origin-repoint/SKILL.md) — remote
  remediation, the other read that depends on the remote being reachable.

## 6. Traceability

See [TRACEABILITY.md](TRACEABILITY.md).

## 7. Changelog

See [CHANGELOG.md](CHANGELOG.md).
