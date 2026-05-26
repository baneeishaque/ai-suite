---
name: Hardcoded /tmp Write→Read Chain — git diff Case Study
description: Sanitized log of the 2026-05-27 onboarding session that introduced the second hardcoded-chain MUTATES exception (git diff > /tmp/settings_diff.txt; wc -l && head).
category: Traceability
---

# Hardcoded Tmp-Write→Read Chain — `git diff` Case Study

**Date**: 2026-05-27 (single session)
**Trigger**: User asked to onboard 6 review-pipeline commands to VS Code `chat.tools.terminal.autoApprove`.
**Outcome**: New `sed` SSOT entry, promoted "Hardcoded Tmp-Write→Read Exception Pattern" section, second precedent for the exception, tightened `git diff` token whitelist, and §5.5 in the consolidation skill.

*Sanitized per [Redaction & Portability Skill](../../redaction-portability/SKILL.md) — Tier C content
only. User-home paths replaced with `<user-home>`, repo absolute paths replaced with `<repo>`,
author replaced with `<author>`.*

***

## 1. User Intent

Onboard the following review-pipeline commands so they auto-approve in subsequent sessions:

1. `git -C <repo> show --name-status --oneline -n 1`
2. `git -C <repo> diff -- <path> | head -200`
3. `git -C <repo> diff -- <path> > /tmp/settings_diff.txt; wc -l /tmp/settings_diff.txt && head -100 /tmp/settings_diff.txt`
4. `git -C <repo> diff -- <path> | sed -n '1,200p'`
5. `git -C <repo> diff --cached -- <path> | sed -n '1,200p'`
6. `git show --name-status --oneline -n 1`

***

## 2. Verdicts (Chronological)

| # | Segments | Worst-tier | Notes |
| :- | :- | :- | :- |
| 1 | `git show --name-status --oneline -n 1` | SAFE | Tight flag whitelist preferred over generic arg slot. |
| 2 | `git diff … \| head -N` | SAFE-IF-PIPED | Pipe-suffix added to the existing git-read entry. |
| 3 | `git diff … > /tmp/settings_diff.txt; wc -l … && head -N …` | **MUTATES** | Initially skipped; later admitted under hardcoded-chain exception. |
| 4 | `git diff … \| sed -n '1,200p'` | SAFE-IF-PIPED | Required adding `sed` to SSOT (new SAFE-IF-PIPED row). |
| 5 | `git diff --cached … \| sed -n '1,200p'` | SAFE-IF-PIPED | Drove `( --cached)?` token in tightened regex. |
| 6 | `git show --name-status --oneline -n 1` | SAFE | Same shape as #1 without `-C <path>`; both covered by one entry via optional `( -C ARG)?`. |

***

## 3. Key Decisions

1. **`matchCommandLine: true` retained** despite §11.3 default (`false` for SAFE). User
   preference: predictability over policy-default. All entries onboarded with full-line match.
2. **Tight token whitelist over generic arg slot**. For `git diff`, the chosen shape
   `(status|log|diff|ls-files)( --cached)?( -- [^;&|<>$BTICK()]+)?` rejects forms like
   `git diff HEAD~1`. Documented as a trade-off in `vscode-autoapprove-entry-consolidation`
   §5.5; flagged for re-evaluation if false-rejection rate becomes painful.
3. **Hardcoded Tmp-Write→Read exception (second precedent)**. After initial skip, the chain
   was admitted because all five clauses held:
   - hardcoded filename `/tmp/settings_diff.txt` (no variable expansion);
   - directory pinned under `/tmp`;
   - downstream consumers `wc -l` and `head` both SAFE;
   - segment separators limited to `;` and `&&` (no `|`, `||`, no command substitution);
   - every arg slot retained the anti-chaining class `[^;&|<>$BTICK()]`.
4. **`sed` added to SSOT** as SAFE-IF-PIPED. Cheatsheet section added between `### grep` and
   `### File Viewing`; `safety-table.csv` row added alphabetically between `python3` and
   `Select-Object`.
5. **`fix-indents.py` skipped**. User confirmed the target `settings.json` is JSON-formatted
   (not JSONC), so the audit skill's 8-space sub-key re-indent step is unnecessary.

***

## 4. Artifacts Produced

| Path | Change |
| :--- | :--- |
| `is-this-command-safe/docs/safety-table.csv` | Added `sed` row. |
| `is-this-command-safe/docs/cheatsheet.md` | Added `### sed` section; promoted "## Hardcoded Tmp-Write→Read Exception Pattern" section; cross-referenced from `### cat` and `### git diff` EXCEPTION blocks. |
| `is-this-command-safe/SKILL.md` | §4 paragraph cross-referencing the exception pattern. |
| `vscode-autoapprove-entry-consolidation/SKILL.md` | New §5.5 "Tight Token Whitelist (vs Generic Arg Slot)". |
| `command-autoapprove-onboarding/SKILL.md` | MUTATES row clarified to require the exception clauses; new §5.1 Worked Example for the hardcoded chain. |
| `command-autoapprove-onboarding/specs/hardcoded-chain-git-diff-tmp-settings-diff.spec.json` | Accept/reject spec (3 accepts, 6 rejects). |
| `<user-home>/Library/Application Support/Code - Insiders/User/settings.json` | Entries 30→31; mirrored & committed in `<configs-repo>` as `23ea585`. |

***

## 5. Future Triggers

Re-open this thread when:

- A third hardcoded-chain MUTATES exception is proposed — re-evaluate whether the exception
  warrants its own dedicated skill rather than living inside is-this-command-safe.
- `git diff HEAD~1`-style commands begin to be auto-approved frequently and the tight
  token whitelist starts producing user-visible friction.
- `sed` substitution forms (`s/…/…/`) are requested for auto-approval — they require their
  own classification (likely MUTATES when paired with `-i`).
