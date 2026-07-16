# Command → Auto-Approve Onboarding Skill

This is an Agent Skill for the end-to-end pipeline of taking any shell command the user wants
auto-approved (single, chained, multi-line, or script form) and onboarding it into VS Code
`chat.tools.terminal.autoApprove` after a full safety audit.

Refer to the Single Source of Truth [SKILL.md](./SKILL.md) for the complete protocol:
decomposition rules, classification via `is-this-command-safe`, SSOT extension (cheatsheet &
safety-table), regex construction with anti-chaining char class, and hand-off to the
`vscode-autoapprove-entry-consolidation` reuse-before-add algorithm.

This skill is an **Orchestrator** (Composer-of-Composers). It owns NO scripts of its own. All
operational primitives live in the layer below:

- [`is-this-command-safe`](../is-this-command-safe/SKILL.md) — safety verdicts, SSOT files
- [`vscode-terminal-autoapprove-audit`](../vscode-terminal-autoapprove-audit/SKILL.md) — Python scripts
- [`vscode-autoapprove-entry-consolidation`](../vscode-autoapprove-entry-consolidation/SKILL.md) — reuse-before-add
