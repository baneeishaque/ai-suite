# VS Code Auto-Approve Entry Consolidation Skill

This is an Agent Skill for keeping the `chat.tools.terminal.autoApprove` list minimal by
extending existing anchored regex entries before adding new ones.

Refer to the Single Source of Truth [SKILL.md](./SKILL.md) for the complete protocol:
reuse-before-add procedure, extension pattern catalogue (optional suffix, optional flag group,
alternation collapse), and the periodic sweep protocol.

This skill is a **Composer** over
[`vscode-terminal-autoapprove-audit`](../vscode-terminal-autoapprove-audit/SKILL.md). It does
NOT ship its own scripts — all `edit-entry.py`, `find-entry.py`, and `fix-indents.py`
invocations target the base skill's `scripts/` directory.

It consumes [`is-this-command-safe`](../is-this-command-safe/SKILL.md) for all four-tier
safety verdicts — do not duplicate the classification logic here.
