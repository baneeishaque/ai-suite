# shell-command-permission-verifier — Bridge

## Purpose

This file bridges non-skill-aware agent runtimes that auto-load `AGENTS.md` by filename
convention. The operational Single Source of Truth lives in [`SKILL.md`](SKILL.md).

## When This Skill Applies

Use when you need to:

- Answer "what would assistant X auto-approve for this shell command?" across all five
  assistants (opencode, Kilo, Claude, Copilot-VSCode, Gemini CLI).
- Regression-test permission backends before/after editing a config.
- Debug why a command is asked vs. allowed (last-match-wins, priority tiers, fnmatch, regex).
- Generate a per-command verdict table for a safety review.

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full protocol. The only actionable entry is the script:

```bash
# all engines against live configs — must be green before syncing
python3 scripts/verify-verdicts.py --strict

# one-off decision (e.g. while drafting a rule)
python3 scripts/verify-verdicts.py --cmd "git status" --tools opencode,kilo
python3 scripts/verify-verdicts.py --cmd "git status" --json
```

The script is **read-only**: it never writes any assistant config. If a config file is absent,
the corresponding engine returns `none` (never a false `allow`).

## Files & Scripts

| Path | Purpose |
| :--- | :--- |
| `scripts/verify-verdicts.py` | Base verdict engine — 5 backends (opencode/kilo object last-match-wins, claude fnmatch, copilot regex, gemini TOSL priority), `--cmd`, `--json`, `--strict`. |
| `specs/opencode-readonly.spec.json` | Allow family: docker ps/images/system df, git submodule status, read-only git, audit.py, find-current-session.py. |
| `specs/opencode-dangerous.spec.json` | Ask family: destructive git, shell chains, mkdir, sqlite DROP, psql, --outfile. |
| `specs/cross-tool-align.spec.json` | Per-engine verdict regression baseline — asserts the real divergence (e.g. Claude only allows `Bash()`-wrapped forms). |
| `specs/gemini-priority.spec.json` | Gemini TOSL priority-tiering, negative-lookahead exclusion, prefix trailing-space semantics, default ask_user. |

## Engine Semantics (must not drift — keep in sync with live configs)

- **opencode / kilo**: `permission.bash` is a pattern→action **object** (NOT a runtime-built
  classifier). Last match wins (`findLast`); default `ask`. Wildcard `*`→`.*` (trailing `*`
  becomes `( .*)?`); `?`→`.`; anchored `^…$`; backslash-normalized; case-sensitive.
- **claude**: `permissions.allow` list; `fnmatchcase` (any match → allow); bare commands are
  `ask` because Claude allow entries are full `Bash(<pattern>)` strings.
- **copilot**: `chat.tools.terminal.autoApprove` list of `/regex/flags`; any `re.search`
  match → allow.
- **gemini**: `[[rule]]` tables with `priority`; highest-priority tier first-match-wins;
  `commandPrefix` needs a trailing space; default `ask_user`.

## Cross-References

- [`../cross-tool-shell-command-permission-sync/SKILL.md`](../cross-tool-shell-command-permission-sync/SKILL.md)
  — composer that writes the allow rules here and invokes this base as a subprocess.
- [`../../../is-this-command-safe/SKILL.md`](../../../is-this-command-safe/SKILL.md) — command
  safety classification (the safety rationale behind which commands are allow-vs-ask).
- [`../../../is-this-command-safe/docs/safety-table.csv`](../../../is-this-command-safe/docs/safety-table.csv)
  — machine-readable safety table (SSOT for verdicts like `docker ps`, `git submodule status`,
  `mkdir`).
- [`../../../opencode-jsonc-util/SKILL.md`](../../../opencode-jsonc-util/SKILL.md) — JSONC parsing
  helper reused for opencode.json / kilo.jsonc comment stripping.
- [`../../../command-autoapprove-onboarding/SKILL.md`](../../../command-autoapprove-onboarding/SKILL.md)
  — VS Code auto-approve onboarding (related tool-approval domain).

## Redaction

The default config paths resolve to absolute `/Users/<user>/...` locations. Do not paste
verbatim paths in committed fixtures or session exports — use `$XDG_CONFIG_HOME`/`$HOME`
placeholders (see `redaction-portability/SKILL.md`).
