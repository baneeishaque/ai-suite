# dev-env-private-config-symlink — Agent Companion

This is the passive-context companion for the
[`dev-env-private-config-symlink`](SKILL.md) skill.

**When to invoke:**

- An app's `.env`, runtime JSON config, or HTTP-client environment is
  expected to be present but is missing, broken, or stale.
- A new host environment (Gitpod, Cloud Shell, NeverInstall, Ubuntu,
  macOS, Windows) needs the private-config layer set up from scratch.
- The user reports that the same app behaves differently across two
  machines — case-mismatch or stale-target diagnosis is needed.
- An audit is needed to decide whether a linked config file is
  actually consumed by source code (`relationOfAccounts.json`
  precedent) before adding / removing the link.

**Refer all operational logic to [SKILL.md](SKILL.md).**

**Related skills:**

- [`redaction-portability`](../redaction-portability/SKILL.md) — path
  and identity redaction policy.
- [`git-atomic-commit-construction`](../git-atomic-commit-construction/SKILL.md)
  — atomic-commit discipline for symlink-related changes.
- [`vscode-user-settings-symlink`](../vscode-user-settings-symlink/SKILL.md)
  — sibling pattern for IDE user-settings symlinking.
