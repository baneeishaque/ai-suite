# [Update Safety Classification & Permission Config Skills from Conversation] (v1)

## Rule Compliance Reference

- [ai-agent-planning-rules.md §3](ai-agent-rules/ai-agent-planning-rules.md#3-components-of-an-effective-plan) — step-by-step breakdown with literal detail
- [ai-agent-planning-rules.md §4](ai-agent-rules/ai-agent-planning-rules.md#4-the-agent-planning-workflow) — plan first, execute after approval
- [ai-rule-standardization-rules.md §4](ai-agent-rules/ai-rule-standardization-rules.md#4-content-philosophy-ultra-lean-industrial) — SSOT integrity, preserve existing content, blend new info
- [skill-factory/SKILL.md §2.0](.agents/skills/skill-factory/SKILL.md#20-layering-decision-base-vs-composer) — base vs composer enrichment, no new skill needed
- [skill-factory/SKILL.md §5](.agents/skills/skill-factory/SKILL.md#5-skill-doc-editing-discipline) — cross-reference sweep, section insertion, numbering discipline
- [skill-factory/SKILL.md §3](.agents/skills/skill-factory/SKILL.md#3-post-drafting-checklist) — redaction, lint, cross-reference audit, bridge audit
- [ai-rule-standardization-rules.md §5.1](ai-agent-rules/ai-rule-standardization-rules.md#51-ssot-preservation-mandate) — additive refinement, no destructive overwrite

## Background

A recent conversation (this session) added auto-approve patterns to `opencode.json` for commands like `ffmpeg -version`, `pgrep`, and `brew info`. During the conversation, the following insights emerged that need to be captured in the skill SSOTs:

1. `pgrep`, `brew info`, `brew trust` were missing from the safety table and needed classification research.
2. `* --help` / `* --version` (GNU double-dash) is universally safe because it's a standardized convention — showing help/version and exiting before any main action.
3. `* -h` / `* -v` (single-dash) was initially considered and added, then removed because single-dash flags are command-specific and NOT safe to blanket-allow (e.g., `grep -h` = suppress filenames, `python3 -v` = verbose, `ffmpeg -v` = log level, `ls -h` = human-readable).
4. `brew trust` is MUTATES (modifies Homebrew tap trust state), not SAFE — was initially added as allow, then corrected to ask.
5. `ffmpeg -version*` was added as a narrow specific pattern instead of a broad `* -version`.

## Files Changed

### `is-this-command-safe/docs/safety-table.csv`

Add 3 rows at correct alphabetical positions:

| binary | verdict | destructive_flags | safe_alternative | notes |
|--------|---------|-------------------|------------------|-------|
| `brew info` | SAFE | | n/a | Displays formula/cask information — version, dependencies, description, install status. Read-only query of local Homebrew database. No filesystem mutation. |
| `brew trust` | MUTATES | | n/a | Adds or removes a tap from the Homebrew trust store. Modifies Homebrew's persistent trust state. Always mutates configuration. |
| `pgrep` | SAFE | | n/a | Searches process table by name/attributes and prints matching PIDs to stdout. Read-only process inspection. No destructive flags. Companion to `pkill` (which IS MUTATES — sends signals). |

### `is-this-command-safe/SKILL.md`

1. **Add new subsection §3.x: Flag Safety Conventions**
   - Document the GNU double-dash standard: `--help` prints usage and exits (universally safe), `--version` prints version and exits (universally safe).
   - Document the single-dash trap: `-h` and `-v` are command-specific, NOT standardized. Examples where they mean something other than help/version.
   - Reference the `opencode-permission-config` §6.7 table which already lists `* --help` / `* --version` as ported patterns.

2. **Update §7 (Allowlist Cheatsheet) prose** to reflect the new additions.

### `is-this-command-safe/docs/cheatsheet.md`

- Add `pgrep` under System/process inspection.
- Add `brew info` under Brew inventory.
- Add `brew trust` under MUTATES section.

### `opencode-permission-config/SKILL.md`

1. **Add new subsection §6.10: Single-Dash vs Double-Dash Flag Patterns**
   - Document the conversation finding: `* --help` / `* --version` (double-dash) are safe per GNU convention; `* -h` / `* -v` (single-dash) were considered and rejected because they are NOT standardized.
   - Document the specific solution: narrow `ffmpeg -version*` pattern instead of broad `* -version`.
   - Reference `is-this-command-safe` §3.x as the SSOT for the flag safety convention.

2. **Add new subsection §6.11: Pre-Addition Safety-Check Workflow**
   - Before adding any new pattern: (a) check the safety table for the binary's verdict, (b) if absent, research and classify via `is-this-command-safe` §8, (c) only then add the pattern.
   - Reference the `verify-permission-pattern.py` script and real-command verification (§4.5).

3. **Update §6.1 (Always-SAFE Commands)** — add `pgrep *`, `brew info *`, `which *`.

## Execution Steps

1. [ ] Extend `is-this-command-safe/docs/safety-table.csv` — add 3 rows at correct alphabetical positions.
2. [ ] Extend `is-this-command-safe/SKILL.md` — add §3.x (Flag Safety Conventions).
3. [ ] Extend `is-this-command-safe/docs/cheatsheet.md` — add `pgrep`, `brew info`, `brew trust`.
4. [ ] Extend `opencode-permission-config/SKILL.md` — add §6.10, §6.11, update §6.1.
5. [ ] Verify section numbering after insertions (mandated by skill-factory §5.4).
6. [ ] Run `post-rename-sweep.py` for any renumbered sections.
7. [ ] Run `markdownlint-cli2 --fix` on all edited files.
8. [ ] Run `verify-permission-pattern.py` against the current `opencode.json` to confirm patterns still match.
9. [ ] Run `audit-cross-refs.py` to verify cross-reference integrity.
