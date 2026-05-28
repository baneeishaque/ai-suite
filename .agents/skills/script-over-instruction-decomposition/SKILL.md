---
name: script-over-instruction-decomposition
description: When designing or refactoring a rule, skill, or sub-agent prompt, decompose its procedure into a deterministic script tier and a prose tier — encode every deterministic step as an executable script under scripts/, leave only judgement/branching/gates in prose.
category: Rule-Management
---

# Script Over Instruction Decomposition Skill

> **Skill ID:** `script-over-instruction-decomposition`
> **Version:** 1.0.0
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)

## Description

Encode the principle: **scripts are more deterministic than instructions.**
Any agent-facing procedure — rule, skill, sub-agent prompt, README,
checklist — is replayed by a probabilistic language model and may drift
in subtle ways. A script is replayed by an interpreter and either
succeeds identically or fails loudly.

This skill operationalizes the decomposition: for any procedure, split
its steps into a **deterministic tier** (becomes a script) and a
**judgement tier** (stays as prose). The script ships inside the host
skill's `scripts/` folder. Prose collapses to invocation + branching +
gates.

## Prerequisites

| Requirement | Minimum |
|---|---|
| Shell | PowerShell 5.1+ OR Bash 4+ OR Python 3.7+ (per host skill's language choice) |
| Edit access | Write access to the host skill / rule directory |

## When to Apply

Apply this skill when:

- Designing a NEW rule or skill that contains multi-step mechanical work.
- Refactoring an EXISTING rule/skill whose prose contains a long bash
  recipe, multi-file mutation sequence, or repeated-across-sessions
  verification pattern.
- Reviewing an agent prompt that hand-codes a deterministic procedure
  the agent could instead invoke via one script call.

Do NOT apply when:

- The procedure is genuinely one-shot exploration / triage requiring
  judgement.
- The procedure is a single shell command (a script is overhead).
- The host artifact is purely conceptual (architecture rationale,
  trade-off discussion).

## The Determinism Hierarchy

For any agent-facing procedure, classify each step into one tier:

| Tier | Encoding | When to choose |
|---|---|---|
| **A. Script (executable)** | `.ps1` / `.py` / `.bash` under `scripts/` | Deterministic mechanical work — file mutations, deployments, idempotent verifications, byte-level assertions, multi-step orchestrations. |
| **B. Script-invoking prose** | Markdown with a one-liner `python3 scripts/foo.py --bar` | The procedure exists as a script; prose tells the agent which script to run and when. |
| **C. Pure prose** | Markdown checklist or rule | Genuine judgement, branching on user intent, adversarial gates ("ASK BEFORE destructive op"), one-shot exploration / triage. |

When a procedure straddles tiers, split it: mechanics → A; gate → C;
Tier B prose threads them.

## Mandatory Categories (MUST be Tier A)

These categories MUST be encoded as scripts, never as prose recipes:

- **Multi-step file mutations** — write A, edit B, symlink C as one
  atomic operation.
- **Idempotent deployment / installation** — symlink creation, config
  fan-out from a canonical SSOT, mirrored backups.
- **Byte-level / JSON-shape verifications** — assertions like "file
  must JSON-equal target" or "all keys in alphabetical order".
- **Determinism-critical sequences** — operations whose correctness
  depends on exact ordering or exact intermediate state.
- **Repeated-across-sessions recipes** — anything the agent runs
  verbatim more than once across sessions (safety stash patterns,
  pre-commit verifications, environment hydration).

## Appropriate-for-Prose Categories (SHOULD be Tier C)

These SHOULD remain in prose:

- **Decision trees that branch on user intent** — "if user wants X
  then A, if Y then B."
- **Exploration / triage steps that require judgement** — "inspect the
  diff and classify each file by concern."
- **Adversarial / safety gates** — "before any destructive operation,
  ASK the user and WAIT for explicit confirmation."
- **Pedagogical explanations** — flag-by-flag breakdowns of a command,
  rationale for an architectural choice.
- **One-shot bootstrap steps that vary per machine** — the script
  cannot run yet because the script is itself the artefact being
  installed.

## Step-by-Step Procedure

### Step 1 — Identify the Host Artifact

Locate the rule, skill, or sub-agent prompt whose procedure is being
decomposed. Confirm its `scripts/` folder exists (create if not).

### Step 2 — Audit the Procedure for Tiers

Read the procedure top-to-bottom. For each numbered step:

- Mark **A** if it is deterministic mechanical work.
- Mark **C** if it is judgement / branching / gate / explanation.
- Mark **A+C** if it mixes both (will need to be split).

### Step 3 — Extract the Tier-A Core into a Script

Group consecutive Tier-A steps into a single script under
`scripts/<verb-noun>.{ps1|py|bash}`. The script MUST:

- Be **idempotent** — safe to re-run.
- Be **deterministic** — same input → same output.
- Fail **loudly** on unexpected state — never silently skip.
- Take parameters via flags / args, not hard-coded paths.
- Print a one-line summary per side-effect (created, updated, skipped).
- Obey the host project's language mandate (default PowerShell per
  `script-management-rules.md`; Python only with documented
  justification; Bash uses `.bash` extension).

### Step 4 — Trim the Prose to Tier B + C

Replace the extracted Tier-A prose with:

- **One-line invocation** (Tier B) — `python3 scripts/foo.py --bar`.
- **Preserved Tier C** — judgement, branching, gates, explanations.
- **Optional fallback** — the original manual recipe, labelled
  "Bootstrap / Audit / Rollback Fallback", referencing the script as
  the canonical path.

### Step 5 — Verify Script Independence

Confirm the script runs end-to-end on a fresh checkout with only the
prerequisites listed in the host skill. No reliance on agent state.

### Step 6 — Commit Atomically

Per
[`git-atomic-commit-construction`](../git-atomic-commit-construction/SKILL.md),
the extraction is one atomic commit. Message pattern:

```text
refactor(<host-skill>): extract <verb-noun> into scripts/<file>

Tier-A core of <procedure> was previously prose; replayed
non-deterministically per session. Extracting into an idempotent script
makes the procedure replayable and self-verifying. Prose §<N> trimmed
to invocation + fallback-for-audit.
```

## Anti-Patterns to Reject

| Anti-pattern | Why bad |
|---|---|
| Inlining script body inside a fenced code block in `SKILL.md` | Violates No-Embedded-Script Mandate; SSOT duplication. |
| "Run this 5-step bash recipe" with no script equivalent | Agent re-derives the recipe each session; drift inevitable. |
| Splitting one script into "prose + 3-line script" | Tier-A leak into prose. Move all mechanics into the script. |
| Removing the manual fallback entirely | Bootstrap and audit need it; preserve as labelled fallback. |
| Bulk "convert everything" sweep | High churn, low context. Refactor opportunistically per session. |

## Worked Example — MCP Consumer Symlink Deployment

The
[`mcp-cross-tool-config-sync`](../mcp-cross-tool-config-sync/SKILL.md)
skill originally documented its Phase 5 "Symlink Distribution" as a
five-step bash recipe (verify backup → `rm` → `ln -s` → verify →
`diff`). Each invocation rehydrated those steps from prose and ran them
per tool — error-prone, drift-prone, verbose.

The script-first refactor moved the entire deterministic core into
`scripts/generate-configs.py`:

- `deploy_symlink(link, target)` — idempotent, relative-path, skips
  silently when the consumer's parent dir is absent.
- `DEPLOY_TARGETS` map — single registration point for new tools.
- `--no-deploy` flag — generation-only mode for CI / dry-run.

Skill §9 prose was trimmed to "run the script; here's the fallback
manual pattern for bootstrap and audit." Adding a new tool means
appending one entry to a Python dict — no prose edit required.

See the upstream commit (`ai-suite-2` `c190f39`) and downstream sync
(`configurations-private` `27f0e6e`) for the canonical refactor.

## Cross-References

- **[Script Management Rules](../../../ai-agent-rules/script-management-rules.md)** —
  canonical SSOT for script craftsmanship (headers, language priority,
  `Common-Utils.ps1` dot-sourcing).
- **[Scripting Language Selection Rules](../../../ai-agent-rules/scripting-language-selection-rules.md)** —
  PowerShell vs Bash vs Python decision matrix.
- **[Bash Scripting Rules](../../../ai-agent-rules/bash-scripting-rules.md)** —
  Bash-specific craftsmanship (`.bash` extension, shebang,
  `set -euo pipefail`).
- **[AI Rule Standardization Rules §4](../../../ai-agent-rules/ai-rule-standardization-rules.md)** —
  Script SSOT Mandate and No-Embedded-Script Mandate.
- **[Git Atomic Commit Construction](../git-atomic-commit-construction/SKILL.md)** —
  per-extraction commit discipline.

## Traceability

Formalized after a session in which a configurations repository's MCP
consumer symlink (`User/mcp.json`) needed to be made portable across
machines. The refactor moved symlink creation from documented bash
steps into the generator script's `deploy_symlink` function and gated
on `link.parent.exists()` so the script is safe to run on machines
where each consumer is or is not installed.

User principle: *"I prefer script over skill instruction; scripts are
more deterministic than instruction (or its derivatives like rules,
skills, sub-agents, etc.)."* This skill is the operational form of
that principle.
