---
name: vscode-terminal-autoapprove-audit
description: Audit, tighten, and prune chat.tools.terminal.autoApprove entries in VS Code settings.json — one-by-one review with is-this-command-safe verdicts, dead-weight detection, loose prefix migration to anchored anti-chaining regex, secret scanning, and batch drop execution.
category: VSCode-Configuration
---

# VS Code Terminal Auto-Approve Audit Skill (v1)

This skill governs the lifecycle of `chat.tools.terminal.autoApprove` entries in VS Code
`settings.json`: initial audit, entry-by-entry safety review, migration of loose prefix rules
to anchored regex, secret scanning, and surgical bulk removal of dead-weight one-shots.

It composes the [`is-this-command-safe`](../is-this-command-safe/SKILL.md) skill as its
verdict engine. Classification tiers and destructive-flag inventory are NOT duplicated here —
they are the SSOT of that skill.

***

## 1. Layering Decision

Per [Skill Factory §2.0](../skill-factory/SKILL.md#20-layering-decision-base-vs-composer), this
skill is **Atomic** at v1. The entire workflow (list → classify → decide → apply) is specific to
`chat.tools.terminal.autoApprove` and has no reusable primitive that another domain would need.

It **consumes** (does not duplicate):

- [`is-this-command-safe`](../is-this-command-safe/SKILL.md) — four-tier safety verdict
- [`vscode-settings-promotion`](../vscode-settings-promotion/SKILL.md) — if the setting needs
  promoting across profiles after cleanup

***

## 2. Environment & Dependencies

| Requirement | Verification |
| :--- | :--- |
| Python 3.9+ | `python3 --version` |
| Valid `settings.json` | `python3 -c "import json; json.load(open('<path>'))"` |
| `is-this-command-safe` skill | Read `../is-this-command-safe/SKILL.md` |

No pip packages required — scripts use only the standard library (`json`, `re`, `sys`, `os`).

***

## 3. Trigger Conditions

Invoke this skill when:

1. `chat.tools.terminal.autoApprove` has accumulated many entries and needs pruning.
2. A bare-prefix entry (e.g. `"mkdir": true`) needs migrating to an anchored regex.
3. A suspected secret (password, token) is embedded in an entry key.
4. A new auto-approve rule is proposed and must pass safety classification before addition.

### 3.1 Formatting Contract — settings.json Indentation

The target `settings.json` is assumed to use **4-space indentation**, which yields:

| Depth | Spaces | Content |
| :--- | :--- | :--- |
| 1 | 4  | Top-level keys (`"chat.tools.terminal.autoApprove": { ... }`) |
| 2 | 8  | Per-entry regex keys inside the `autoApprove` object |
| 3 | 12 | `approve` / `matchCommandLine` sub-keys |

All scripts in this skill (`audit-autoapprove.py`, `edit-entry.py`) read with
`json.load(... object_pairs_hook=OrderedDict)` to preserve entry order and write with
`json.dump(..., indent=4)` to preserve this contract.

If the user's profile follows a different convention (e.g. 2-space global with 8-space
override for `approve` / `matchCommandLine`), re-run
[`vscode-settings-indent-override`](../vscode-settings-indent-override/SKILL.md) §5.2
**after** any edit by this skill to restore the per-key override:

```bash
python3 .agents/skills/vscode-settings-indent-override/scripts/vscode-settings-indent-override.py \
  --file <settings.json> \
  --key "chat.tools.terminal.autoApprove" \
  --from-spaces 6 --to-spaces 8 \
  --target-keys approve matchCommandLine
```

***

## 4. Pre-Audit Setup

### 4.1 SQL Session Table

Create a tracking table at the start of the audit session — schema mirrors the actual
fields used during review:

```sql
DROP TABLE IF EXISTS autoapprove_review;
CREATE TABLE autoapprove_review (
    seq          INTEGER PRIMARY KEY,    -- 1-based entry position at time of review
    key_snippet  TEXT,                   -- first ~80 chars of decoded key
    verdict      TEXT,                   -- SAFE | SAFE-IF-PIPED | HAS-DESTRUCTIVE-FLAGS | MUTATES
    decision     TEXT,                   -- KEPT | DROPPED | MIGRATED | REPLACED
    notes        TEXT                    -- justification, related entries, follow-up
);
```

If the session is interrupted and the table schema is lost, recreate it. The SQL table is
a *side log* — the source of truth is `settings.json` itself plus the conversation.

### 4.2 Count and List Entries

Use the helper script (preferred — preserves indentation contract):

```bash
python3 .agents/skills/vscode-terminal-autoapprove-audit/scripts/find-entry.py \
  --settings <path/to/settings.json> --list
```

### 4.3 Targeted Lookup

| Goal | Command |
| :--- | :--- |
| Print one entry by 0-based index | `find-entry.py --settings <p> --index 11` |
| Print one entry by 1-based index | `find-entry.py --settings <p> --index 12 --one-based` |
| Find entries containing substring | `find-entry.py --settings <p> --grep 'ssh-mcp'` |

> When grepping, keys are stored with `\\` escapes — search for `ast\\.parse`, not `ast.parse`.

***

## 5. One-by-One Review Protocol

For each entry the agent MUST:

1. **Decode the key** — unescape `\n`, `\\.`, `\\(`, `\\)` etc. to recover the effective command.
2. **Classify** using [`is-this-command-safe`](../is-this-command-safe/SKILL.md) §6 Lookup Procedure.
3. **Emit the §5 verdict template** from that skill (see §5.1 below).
4. **Apply dead-weight detection** (§6 below).
5. **Apply secret scanning** (§8 below).
6. **Present verdict + recommendation** and await user decision: `drop`, `keep`, or `next`.
7. **Log the decision** to the SQL table.

### 5.1 Verdict Output Format

Follow `is-this-command-safe` §5 exactly — no prose preamble, no essay:

```text
Command   : <verbatim effective command (first 120 chars)>
Verdict   : <SAFE | SAFE-IF-PIPED | HAS-DESTRUCTIVE-FLAGS | MUTATES>
Reason    : <one-line justification>
Safe form : <dry-run equivalent, or "n/a">
Action    : <Execute | Execute-with-care | Refuse-pending-user-confirmation>
```

Then append:

```text
Dead-weight: <Yes — one-shot, won't re-match | No — reusable>
Secrets    : <None | CREDENTIAL DETECTED — rotate before proceeding>
Recommend  : <Keep | Drop | Migrate prefix to anchored regex>
```

***

## 6. Dead-Weight Detection

An entry is **dead weight** when ALL of the following hold:

1. The key is a regex anchored with `^…$` and `matchCommandLine: true`.
2. The body contains hardcoded absolute paths (specific CSV files, session-specific backup
   directories) unlikely to recur verbatim.
3. The entry is a one-shot analysis or discovery command from a past session.

**Dead-weight recommendation: Drop.**

Entries that are **not** dead weight (keep/reuse candidates):

- Short general commands: `git remote -v`, `git status`, `git log --oneline`.
- Regex patterns covering a class of commands (e.g. anchored `git rev-parse` form).
- Lint/check tools invoked repeatedly: `markdownlint-cli2`, `npm list`.

***

## 7. Loose Prefix Migration Protocol

A **loose prefix** entry has the form `"<token>": true` (no `^…$` anchors, no
`matchCommandLine`). This matches any command line beginning with the token — including
injected mutations (e.g. `"command": true` approves `command rm -rf ~`).

### 7.1 Standard Migration Table

| Original loose form | Migrated anchored form | Class |
| :--- | :--- | :--- |
| `"git rev-parse": true` | `/^git rev-parse( [^;&\|<>\$` + '`' + `()]*)?$/` | SAFE |
| `"command": true` | `/^command -v [A-Za-z0-9_.+-]+$/` | SAFE |
| `"markdownlint-cli2": true` | `/^markdownlint-cli2( [^;&\|<>\$` + '`' + `()]*)?$/` | SAFE |
| `"mkdir": true` | `/^mkdir( -p)?( [^;&\|<>\$` + '`' + `()]+)+$/` | MUTATES (accepted) |
| `"pg_restore": true` | `/^pg_restore --list [^;&\|<>\$` + '`' + `()]+$/` | MUTATES→SAFE (list-only) |

### 7.2 Anti-Chaining Character Class

Every migrated regex MUST gate argument slots with `[^;&|<>$` + '`' + `()]` to block:

| Character | Attack blocked |
| :--- | :--- |
| `;` | Command sequencing (`cmd1; rm -rf ~`) |
| `&` | AND-chaining / backgrounding (`cmd && rm`) |
| `\|` | Pipe to destructive downstream |
| `<` `>` | Redirection (overwrite existing file) |
| `$` | Variable/command substitution `$()` |
| `` ` `` | Backtick command substitution |
| `(` `)` | Subshell |

### 7.3 Application Steps

1. Edit `settings.json`: replace `"<token>": true` with:
   ```jsonc
   "/^<anchored-regex>$/": {
       "approve": true,
       "matchCommandLine": true
   }
   ```
2. Validate: `python3 -c "import json; json.load(open('<settings.json>')); print('OK')"`
3. Log decision as `migrated` in the SQL table.

### 7.4 Script — `edit-entry.py`

Handles add, in-place key replacement (for migration), and delete without touching other
entries. Writes with `indent=4` (§3.1 contract).

```bash
# Migrate loose prefix to anchored form (position preserved)
python3 .agents/skills/vscode-terminal-autoapprove-audit/scripts/edit-entry.py \
  --settings <path> --replace \
  --old-key '"mkdir": true' \
  --new-key '/^mkdir( -p)?( [^;&|<>$`()]+)+$/'

# Add a new anchored entry at the tail
python3 .agents/skills/vscode-terminal-autoapprove-audit/scripts/edit-entry.py \
  --settings <path> --add \
  --key '/^echo( [^;&|<>$`()]*)?$/'

# Delete one entry by exact key
python3 .agents/skills/vscode-terminal-autoapprove-audit/scripts/edit-entry.py \
  --settings <path> --delete \
  --key '/^<full regex key>$/'
```

***

## 8. Secret Scanning

Before logging `keep` or `migrate`, scan the entry key for:

| Pattern | Risk tier | Action |
| :--- | :--- | :--- |
| `--password=`, `PASSWORD='…'` literal | Tier A credential | **Drop immediately + rotate + audit git history** |
| `CREATE ROLE … PASSWORD '…'` SQL DDL | Tier A credential | Same |
| Bearer / API token literal | Tier A credential | Same |
| IPv4 of non-public host | Tier B topology | Warn; recommend drop |
| Internal hostname / domain | Tier B topology | Warn; recommend drop |

> **Warning**: `settings.json` is often committed to version-controlled
> `configurations-private` repositories and synced via
> `workbench.settings.applyToAllProfiles`. Credentials embedded in entry keys appear in git
> history. Rotate before removing the entry.

***

## 9. Batch Drop Execution

After collecting all `drop` decisions, apply in one atomic pass:

```bash
python3 .agents/skills/vscode-terminal-autoapprove-audit/scripts/audit-autoapprove.py \
  --settings  <path/to/settings.json> \
  --drop-indices 0 1 2 3 6 7 8
```

The script ([`scripts/audit-autoapprove.py`](./scripts/audit-autoapprove.py)):

1. Loads `settings.json`, extracts `chat.tools.terminal.autoApprove`.
2. Removes keys at the specified 0-based indices (resolved before removal — indices stable).
3. Re-serialises JSON, fixes trailing-comma artifacts, validates with `json.loads`.
4. Writes file in-place.
5. Prints: `Removed N entries. autoApprove entries now: M`.

**Always confirm the drop index list against the SQL table before running.**

***

## 10. Post-Audit Checklist

- [ ] JSON validates: `python3 -c "import json; json.load(open('<settings.json>'))"`
- [ ] No loose-prefix entries remain: `grep -n '": true' settings.json`
  (only `workbench.settings.applyToAllProfiles` array values should show `true`)
- [ ] No secrets in retained entries (re-run §8 scan on remaining keys)
- [ ] SQL table has a row for every reviewed entry
- [ ] `workbench.settings.applyToAllProfiles` still lists `chat.tools.terminal.autoApprove`
- [ ] Git diff reviewed before committing

***

## 11. Forward Policy — Adding New Entries

Before adding any new entry, the agent MUST:

1. Classify with `is-this-command-safe` §6.
2. If verdict is `MUTATES`: obtain explicit user confirmation.
3. Use anchored regex `/^…$/` + `matchCommandLine: true`. Bare-prefix `"token": true` is
   **FORBIDDEN** for any token that prefixes a destructive command.
4. Apply anti-chaining character class (§7.2) in all argument slots.
5. Scan for Tier A/B data (§8) before committing.

***

## 12. Related Skills

| Skill | Role |
| :--- | :--- |
| [`is-this-command-safe`](../is-this-command-safe/SKILL.md) | SSOT for four-tier safety verdicts — consumed by §5 |
| [`vscode-settings-promotion`](../vscode-settings-promotion/SKILL.md) | Promotes setting to all profiles after cleanup |
| [`vscode-settings-indent-override`](../vscode-settings-indent-override/SKILL.md) | Re-indents `approve`/`matchCommandLine` sub-keys if needed |
| [`redaction-portability`](../redaction-portability/SKILL.md) | Sanitisation contract for `docs/conversations/` logs |

***

## 13. Traceability

- [`docs/conversations/2026-05-19-autoapprove-audit.md`](./docs/conversations/2026-05-19-autoapprove-audit.md)
  — originating audit session: 47 entries reviewed, 10 dropped (first pass), 5 loose prefixes
  migrated to anchored anti-chaining regex; sanitised per Redaction & Portability protocol.
