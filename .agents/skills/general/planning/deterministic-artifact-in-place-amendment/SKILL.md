---
name: deterministic-artifact-in-place-amendment
description: Decides whether a generated artifact must be regenerated or can be amended in
  place, by byte-comparing the shipped artifact against a fresh baseline — the gate that
  licenses a direct edit when the generator lacks a flag for the needed transformation.
category: Planning
---

# Deterministic Artifact In-Place Amendment (v1)

> **Skill ID:** `deterministic-artifact-in-place-amendment`<br>
> **Version:** 1.0.0<br>
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)<br>
> **Layer:** Base (per [skill-factory §2.0 Layering Decision](../../../skill-factory/SKILL.md))

## Description

When a deterministic generator has no flag for the transformation you need, the instinct
is to re-run it — which silently discards any human/agent judgement already merged into
its output. This skill supplies the gate that decides instead:

- `STALE` — the artifact has drifted from what the generator now produces → **regenerate**.
- `FRESH` — the artifact is still exactly what the generator produces → **amend in place**,
  because the generator is not the problem; the missing flag is.

This is the reusable decision rule behind the "rerun only if needed" instruction that
otherwise exists only as chat-local judgement.

## Composition Rationale

This skill is a **base**: it owns one deterministic comparison and emits one verdict. It
knows nothing about which generator produced the artifact, what the artifact means, or
what change is being applied.

The domain-specific follow-through — which sections to strike, which counts to repair,
which fields are judgement — belongs to the artifact's own domain skill. This skill only
answers "is regeneration even necessary?".

Inlining a hand-rolled `diff` or a byte comparison into a domain skill is FORBIDDEN: the
verdict vocabulary (`STALE` / `FRESH`) and its meaning must stay single-sourced so that a
consumer cannot invent its own notion of "still valid".

## 1. Environment & Dependencies

| Requirement | Minimum | Verification |
| :--- | :--- | :--- |
| Python | 3.9+ (stdlib-only script) | `python3 --version` |

```bash
python3 -c "import argparse, difflib, json, pathlib, sys; print('stdlib OK')"
```

## 2. Operational Logic

### Step 1 — Produce a baseline

Re-run the generator with the SAME inputs but a different destination, so the shipped
artifact is untouched:

```bash
<generator> <same-inputs> --output <baseline-path>
```

The caller owns this step because only the caller knows the generator's invocation. This
skill deliberately does NOT accept a command string to execute — passing an untrusted
command to a subprocess is an injection surface with no legitimate use here.

### Step 2 — Run the gate

```bash
python3 scripts/detect-regeneration-need.py --artifact <artifact> --baseline <baseline>
```

| Verdict | Exit | Action |
| :--- | :--- | :--- |
| `FRESH` | `0` | Amend the artifact in place; DO NOT re-run the generator over it. |
| `STALE` | `0` | Regenerate from the baseline, then re-apply any merged judgement. |
| `MISSING_ARTIFACT` | `3` | Investigate the path before assuming the artifact exists. |
| `MISSING_BASELINE` | `3` | The baseline step failed; fix it, do not guess a verdict. |
| `UNREADABLE` | `3` | Encoding problem; resolve before comparing. |

A `STALE` verdict carries a unified diff (truncated at `--max-diff-lines`, default 120) so
the drift can be triaged without a second tool call.

### Step 3 — Amend deterministically where possible

Once `FRESH` licenses in-place amendment, prefer a mechanical edit over prose. If the
amendment is "strike these sections and repair these totals", that arithmetic is Tier-A and
belongs in the artifact's own script — see
[`script-over-instruction-decomposition`](../../../script-over-instruction-decomposition/SKILL.md).

### Step 4 — Repair every downstream consumer

An in-place amendment to a generated artifact usually invalidates derived numbers quoted in
prose sections that the generator does not own. After amending, enumerate and reconcile
every such reference (summary totals, cross-section claims, index tables). Omitting one
produces an artifact whose own numbers contradict each other.

## 3. Scripts

| Script | Role | Exit codes |
| :--- | :--- | :--- |
| `scripts/detect-regeneration-need.py` | Byte-compare artifact vs baseline, emit `FRESH`/`STALE` verdict plus diff | `0` verdict emitted · `3` missing or unreadable input |

Tier-1 Python (stdlib only) per
[scripting-language-selection-rules../../../../../ai-agent-rules/scripting-language-selection-rules.md)
§3 and §4. The module docstring carries the tier citation.

## 4. Safety

- The script reads two files and writes nothing except its stdout JSON.
- It never executes a caller-supplied command; there is no injection surface.
- It never modifies the artifact — it only reports whether modification is warranted.

## 5. Composition by Higher-Level Skills

| Composer | Composition Mechanism |
| :--- | :--- |
| [`skill-library-gap-closure`](../../skill-dev/skill-library-gap-closure/SKILL.md) | Uses the gate to decide whether an existing skill doc can be amended in place rather than regenerated during a library-wide remediation pass. |

## Related Skills

- [`planning-artifact-lifecycle`](../planning-artifact-lifecycle/SKILL.md) — the
  lifecycle owner whose versioning gates pair with this one.
- [`script-over-instruction-decomposition`](../../../script-over-instruction-decomposition/SKILL.md)
  — where the deterministic half of any amendment belongs.
- [`versioned-artifact-superset-build`](../versioned-artifact-superset-build/SKILL.md) —
  the related construction rule for producing the next version of an artifact.

## 6. Traceability

See [TRACEABILITY.md](TRACEABILITY.md).

## 7. Changelog

See [CHANGELOG.md](CHANGELOG.md).
