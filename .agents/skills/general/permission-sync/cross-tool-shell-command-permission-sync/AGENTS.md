# cross-tool-shell-command-permission-sync — Bridge

## Purpose

This file bridges non-skill-aware agent runtimes that auto-load `AGENTS.md` by filename
convention. The operational Single Source of Truth lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

Use when you need to:

- Propagate a newly-approved **read-only** shell command (e.g. `docker ps`, `git submodule
  status`) from opencode into Kilo / Claude / Copilot-VSCode / Gemini so no assistant
  prompts for it.
- Confirm all five backends agree on a command's verdict before relying on auto-approval
  (run `--verify-only` first).
- Audit the delta between opencode's allow family and a target's current allow set
  (`--dry-run`).

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full protocol. Typical flow:

```bash
# 1. preview what would change (no writes)
python3 scripts/sync-permission-rules.py --dry-run

# 2. confirm current parity (no writes)
python3 scripts/sync-permission-rules.py --verify-only

# 3. apply — writes + md5-stability + parse-check + base-verifier parity
python3 scripts/sync-permission-rules.py
```

The composer delegates all verdict logic to the base
[`../shell-command-permission-verifier/SKILL.md`](../shell-command-permission-verifier/SKILL.md)
via subprocess (`python3 …/verify-verdicts.py cross-tool-align.spec.json --strict`). It
never inlines an engine.

## Files & Scripts

| Path | Purpose |
| :--- | :--- |
| `scripts/sync-permission-rules.py` | Composer — SSOT extraction, per-target translation, md5 backup, ≥3s stability, parse-check, base-verifier parity. `--dry-run` / `--tools` / `--verify-only`. |
| `scripts/tool-registry.json` | Canonical path + format + shape map per tool, with `<user-home>` placeholders (redaction-portability). |

## Engine Semantics (must not drift)

- **opencode** (SSOT): `permission.bash` object, last-match-wins, default `ask`. Translator copies
  glob strings verbatim to kilo.
- **claude**: `permissions.allow` fnmatch globs over full `Bash(<cmd>)` string → wrap pattern.
- **copilot**: VS Code `chat.tools.terminal.autoApprove` anchored regexes.
- **gemini**: `[[rule]]` priority tables; translator emits `commandRegex` at priority 100.

> Claude only allows Bash()-wrapped invocations, so bare `git status` is `ask` even though
> opencode allows it. The sync translates the opencode allow pattern `git status *` → Claude
> `Bash(git status *)` (which fnmatch against the real `Bash(git status -s)` call). This
> divergence is asserted in the base `cross-tool-align.spec.json` as the regression baseline.

## Cross-References

- [`../shell-command-permission-verifier/SKILL.md`](../shell-command-permission-verifier/SKILL.md)
  — base verdict engine (consumed as subprocess, not inlined).
- [`../../../is-this-command-safe/SKILL.md`](../../../is-this-command-safe/SKILL.md) — command
  safety classification (decides which commands are allow-vs-ask family).
- [`../../../is-this-command-safe/docs/safety-table.csv`](../../../is-this-command-safe/docs/safety-table.csv)
  — the safety SSOT (e.g. `docker ps` SAFE, `mkdir` MUTATES, `git submodule status` SAFE).
- [`../../../opencode-permission-config/SKILL.md`](../../../opencode-permission-config/SKILL.md)
  — opencode permission editing/debugging (the SSOT this composer reads).
- [`../../../opencode-jsonc-util/SKILL.md`](../../../opencode-jsonc-util/SKILL.md) — JSONC parse
  helper reused for opencode.json / kilo.jsonc / VS Code settings.json.
- [`../../../command-autoapprove-onboarding/SKILL.md`](../../../command-autoapprove-onboarding/SKILL.md)
  — VS Code auto-approve onboarding (related tool-approval domain).

## Redaction

Real config paths contain absolute `/Users/<user>/...` paths. `tool-registry.json` stores only
`<user-home>` placeholders; runtime expansion happens via env overrides
(`OPENCODE_CONFIG`, `KILO_CONFIG`, `CLAUDE_CONFIG`, `COPILOT_SETTINGS`,
`GEMINI_SAFE_COMMANDS`). Never paste verbatim absolute paths in committed fixtures.
