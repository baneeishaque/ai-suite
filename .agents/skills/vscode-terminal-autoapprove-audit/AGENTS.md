# VS Code Terminal Auto-Approve Audit Skill

This is an Agent Skill for auditing, tightening, and pruning
`chat.tools.terminal.autoApprove` entries in VS Code `settings.json`.

Refer to the Single Source of Truth [SKILL.md](./SKILL.md) for the complete protocol:
entry-by-entry review, safety verdicts, dead-weight detection, loose prefix migration,
secret scanning, and batch drop execution.

The automation script lives at [`scripts/audit-autoapprove.py`](./scripts/audit-autoapprove.py).

This skill consumes [`is-this-command-safe`](../is-this-command-safe/SKILL.md) for all
four-tier safety verdicts — do not duplicate the classification logic here.
