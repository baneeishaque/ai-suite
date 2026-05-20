---
name: command-autoapprove-onboarding
description: Orchestrator — given any shell command (single / chained / multi-line / script), decompose it, classify every segment via `is-this-command-safe` (extending the cheatsheet & safety-table when a binary is missing), then onboard the verdict into VS Code `chat.tools.terminal.autoApprove` via the `vscode-autoapprove-entry-consolidation` reuse-before-add algorithm.
category: VS Code Configuration
---

# Command → Auto-Approve Onboarding Skill (v1)

This skill is the **end-to-end pipeline** for taking an arbitrary shell command the user wants
auto-approved and:

1. Decomposing it into atomic segments (single command, pipeline stages, `&&`/`||`/`;` chains,
   command substitutions, here-docs, script bodies).
2. Classifying each segment via [`is-this-command-safe`](../is-this-command-safe/SKILL.md) §6.
3. **Extending the cheatsheet & safety-table** when a referenced binary is missing — per the
   skill's §8 Append-Only Protocol.
4. Onboarding the command into `chat.tools.terminal.autoApprove` via the
   [`vscode-autoapprove-entry-consolidation`](../vscode-autoapprove-entry-consolidation/SKILL.md)
   reuse-before-add algorithm (extend existing entry first; only `--add` when no existing entry
   covers the same binary or shape).

This skill **orchestrates** the three lower-level skills — it owns NO scripts of its own. All
operational primitives live in the layer below.

***

## 1. Layering Decision

Per [Skill Factory §2.0](../skill-factory/SKILL.md#20-layering-decision-base-vs-composer), this
skill is a **Composer-of-Composers**:

| Layer | Skill | Role |
| :--- | :--- | :--- |
| Base | [`is-this-command-safe`](../is-this-command-safe/SKILL.md) | Four-tier safety verdict, cheatsheet & safety-table SSOT |
| Base | [`vscode-terminal-autoapprove-audit`](../vscode-terminal-autoapprove-audit/SKILL.md) | Owns `edit-entry.py`, `find-entry.py`, `fix-indents.py` and the indentation contract |
| Composer | [`vscode-autoapprove-entry-consolidation`](../vscode-autoapprove-entry-consolidation/SKILL.md) | Reuse-before-add algorithm, extension-pattern catalogue |
| **Orchestrator** | **This skill** | **Decompose → classify → extend SSOT → onboard** |

This skill is the only place where the full lifecycle (parse the user's command → write to
`settings.json`) is automated end-to-end. Every other skill in the chain is invoked by name; none
of their operational logic is duplicated here.

***

## 2. Environment & Dependencies

| Requirement | Verification |
| :--- | :--- |
| Python 3.9+ | `python3 --version` |
| `is-this-command-safe` skill present | `ls ../is-this-command-safe/docs/safety-table.csv` |
| `vscode-terminal-autoapprove-audit` scripts present | `ls ../vscode-terminal-autoapprove-audit/scripts/` |
| `vscode-autoapprove-entry-consolidation` SKILL present | `ls ../vscode-autoapprove-entry-consolidation/SKILL.md` |
| Target `settings.json` valid | `python3 -c "import json; json.load(open('<path>'))"` |

No additional dependencies. All scripts referenced are stdlib-only Python.

***

## 3. Trigger Conditions

Invoke this skill when the user says any of:

- "Auto-approve `<cmd>`"
- "Add `<cmd>` to autoApprove"
- "I keep getting approval prompts for `<cmd>` — fix it"
- Pastes a multi-line script and asks for it (or its components) to be auto-approved
- "Make `<pipeline>` not ask for permission"

The skill ALSO triggers implicitly inside any other workflow when the agent is about to issue a
command that has been refused or is about to require manual approval — onboard it once, never
fight the gate twice.

***

## 4. End-to-End Pipeline

### Step 1 — Capture the command verbatim

Record the exact command string the user wants auto-approved. Preserve quoting, redirection,
heredoc bodies. Never paraphrase.

### Step 2 — Decompose into atomic segments

| Construct | Decomposition |
| :--- | :--- |
| `A \| B \| C` | Three pipeline segments: `A`, `B`, `C`. Reclassify each via [`is-this-command-safe`](../is-this-command-safe/SKILL.md) §6. |
| `A && B` / `A \|\| B` / `A ; B` | Two (or more) chain segments. Each is an independent command to classify. |
| `A $(B)` / `` A `B` `` | Outer `A` plus inner `B`. Inner is a substitution; classify both. |
| `A > FILE` / `A >> FILE` / `A \| tee FILE` | Single command `A` plus redirection target. If `FILE` is an existing file and the redirection is truncating (`>`, `tee` without `-a`), `is-this-command-safe` §4 escalates the verdict to MUTATES. |
| Heredoc body (`<<EOF`) | Treat the heredoc body as input data, NOT as a command unless the heredoc is fed into `sh`/`bash`/`python -`. If fed to an interpreter, classify the body as a script (recurse into Step 2 for each line). |
| Multi-line script / `.sh` file | Walk the script line-by-line; classify each non-blank, non-comment, non-control-flow line. Control-flow (`if`, `for`, `while`) carries no destructive weight on its own — classify the bodies. |
| Variable assignment (`X=value`) | SAFE (no command executed). |
| `eval "$X"` / `bash -c "$X"` | UNKNOWN unless `$X` resolves to a literal at audit time — refuse-pending-user-confirmation. |

### Step 3 — Classify each segment

For each atomic segment produced by Step 2, follow
[`is-this-command-safe` §6 Lookup Procedure](../is-this-command-safe/SKILL.md#6-lookup-procedure)
and emit the §5 5-line verdict template. The overall command's verdict is the **strictest** of
all segment verdicts (worst-tier wins).

### Step 4 — Extend the cheatsheet & safety-table when a binary is missing

If any segment's binary is not present in
[`is-this-command-safe/docs/safety-table.csv`](../is-this-command-safe/docs/safety-table.csv):

1. Classify the binary via its man page or `--help` output.
2. Follow [`is-this-command-safe` §8 Append-Only Protocol](../is-this-command-safe/SKILL.md#8-extending-the-allowlist-append-only-protocol):
    - Add a row to `safety-table.csv` preserving column order.
    - Add a corresponding section to `cheatsheet.md` at the alphabetical position within its category.
    - Re-emit the verdict against the new entry to confirm correctness.
3. The cheatsheet & safety-table are the SSOT — **always update them before** updating
   `settings.json`. This ensures every autoApprove entry has a paper trail in the SSOT.

### Step 5 — Build the regex key

Choose the regex shape by the strictest verdict in Step 3:

| Worst-segment verdict | Allowed in autoApprove? | Regex shape |
| :--- | :--- | :--- |
| ✅ SAFE | Yes | Anchored `/^…$/` with anti-chaining char class `[^;&\|<>$BTICK()]` on every arg slot |
| 🟡 SAFE-IF-PIPED | Yes IFF the literal pipeline composed only of SAFE downstream sinks (`head`, `grep`, `wc`); escape the literal pipe `\|` between segments | Same shape, with `\|` literal between segment regexes |
| ⚠️ HAS-DESTRUCTIVE-FLAGS | Only the SAFE form (without the destructive flag) | Build the regex around the safe flag set; explicitly exclude the destructive flag |
| ❌ MUTATES | **Only with explicit user confirmation** per [`vscode-terminal-autoapprove-audit` §11.2](../vscode-terminal-autoapprove-audit/SKILL.md#112-adding-new-entries) | Anchored, narrow, no wildcards on the destructive flag |

The anti-chaining char class is mandatory on every arg slot to prevent
`cmd; rm -rf ~` from being approved by a regex that allowed `cmd …`.

### Step 6 — Onboard into autoApprove via the consolidation skill

Hand off to [`vscode-autoapprove-entry-consolidation`](../vscode-autoapprove-entry-consolidation/SKILL.md)
§4 Reuse-Before-Add Procedure:

1. `find-entry.py --grep <binary-token>` to check for existing coverage.
2. If 0 matches → `edit-entry.py --add --key '<new regex>'`.
3. If 1+ matches → `edit-entry.py --replace` to extend per §5 of the consolidation skill
   (optional suffix, optional flag group, alternation collapse).
4. `fix-indents.py` to restore the indentation contract.
5. Verify with `find-entry.py --grep`.

### Step 7 — Post-write audit

- Validate JSON: `python3 -c "import json; json.load(open('<path>'))"`
- Confirm the SQL/Conversation log captures: original command, decomposition, verdicts,
  cheatsheet rows added, autoApprove action (add / replace / no-op).

***

## 5. Worked Example

**User asks:** *"Auto-approve `git --no-pager stash list | grep before-nginx-on-agents-md`"*

| Step | Action | Result |
| :--- | :--- | :--- |
| 1 | Capture | `git --no-pager stash list \| grep before-nginx-on-agents-md` |
| 2 | Decompose | Two pipeline segments: `git --no-pager stash list`, `grep before-nginx-on-agents-md` |
| 3 | Classify | `git stash list` → SSOT MISS → classify SAFE; `grep` → SAFE-IF-PIPED |
| 4 | Extend SSOT | Add `git stash list` row to `safety-table.csv` and section to `cheatsheet.md` |
| 5 | Regex shape | `/^git( --no-pager)? stash list( ARG-CLASS*)?( \| grep( -[A-Za-z]+)*( ARG-CLASS+)+)?$/` |
| 6 | Onboard | `find-entry.py --grep stash` → 0 matches → `edit-entry.py --add`. (If a `git stash list` entry already existed without the `\| grep` suffix, hand off to consolidation §5.1 to `--replace` instead.) |
| 7 | Audit | JSON valid; new entry visible at correct position; indent overrides reapplied |

***

## 6. Decision Tree (Quick Reference)

```text
User asks to auto-approve a command
         │
         ▼
[ Step 2: Decompose ]
         │
         ▼
[ Step 3: Classify each segment via is-this-command-safe §6 ]
         │
         ├── Any segment UNKNOWN (binary missing from cheatsheet)?
         │      └── YES → [ Step 4: Extend cheatsheet & safety-table ]
         │
         ├── Worst verdict == MUTATES?
         │      └── YES → ask user to confirm; if no → STOP, do not onboard
         │
         ▼
[ Step 5: Build regex key with anti-chaining class on every arg slot ]
         │
         ▼
[ Step 6: Hand off to vscode-autoapprove-entry-consolidation §4 ]
         │
         ├── Existing entry covers the binary?
         │      ├── YES → --replace (extend per consolidation §5)
         │      └── NO  → --add
         │
         ▼
[ fix-indents.py → verify → done ]
```

***

## 7. Prohibited Behaviors

The agent is **BLOCKED** from:

1. Skipping Step 2 (decomposition) for chained / piped / scripted commands — every segment must
   be classified independently.
2. Adding an autoApprove entry **before** updating the cheatsheet & safety-table when a binary
   is missing from the SSOT. The SSOT is updated first; the autoApprove change is downstream.
3. Calling `edit-entry.py --add` without running the consolidation skill's §4 Step 1 reuse-check
   grep first.
4. Emitting a regex without the anti-chaining character class on every arg slot.
5. Auto-approving a `MUTATES` worst-verdict command without explicit user confirmation, even if
   the user originally asked for it.
6. Auto-approving `eval` / `bash -c "$VAR"` / any dynamic-construction form — these are
   UNKNOWN by `is-this-command-safe` §6 and MUST refuse pending user confirmation.

***

## 8. Verification & Markdown Hygiene

- This `SKILL.md` and its companion `AGENTS.md` MUST pass
  [Markdown Generation Rules](../../../ai-agent-rules/markdown-generation-rules.md) lint.
- All inter-skill links use **relative paths** with correct depth (`../../../` to reach
  `ai-agent-rules/` from this 3-deep skill folder; `../<skill>/SKILL.md` for siblings).
- Per [Redaction & Portability Skill](../redaction-portability/SKILL.md), every file here is
  Tier C (public/universal technical content) — no Tier A/B identifiers are present or may be
  introduced.

***

## 9. Related Skills

| Skill | Role |
| :--- | :--- |
| [`is-this-command-safe`](../is-this-command-safe/SKILL.md) | Base — four-tier verdict, cheatsheet & safety-table SSOT |
| [`vscode-terminal-autoapprove-audit`](../vscode-terminal-autoapprove-audit/SKILL.md) | Base — owns the three Python scripts and the indentation contract |
| [`vscode-autoapprove-entry-consolidation`](../vscode-autoapprove-entry-consolidation/SKILL.md) | Composer — reuse-before-add algorithm consumed by Step 6 |
| [`vscode-settings-promotion`](../vscode-settings-promotion/SKILL.md) | Promotes the consolidated setting across profiles after onboarding |
| [`skill-factory`](../skill-factory/SKILL.md) | Authored this skill per Industrial Fidelity mandates |

***

## 10. Traceability

- Originating session: end-to-end onboarding of `git --no-pager stash list | grep …` —
  produced a missing `git stash list` row in
  [`is-this-command-safe`](../is-this-command-safe/SKILL.md) and a single consolidated regex
  entry in `chat.tools.terminal.autoApprove`, demonstrating the four-skill orchestration
  (this skill → is-this-command-safe → vscode-autoapprove-entry-consolidation →
  vscode-terminal-autoapprove-audit scripts).
