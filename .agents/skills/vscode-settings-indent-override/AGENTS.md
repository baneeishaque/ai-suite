---
name: VS Code Settings Indent Override
description: Passive context bridge for applying per-key non-standard indentation overrides to VS Code settings.json.
category: VSCode-Configuration
---

# VS Code Settings Indent Override (Ref)

This bridge provides passive context for the `vscode-settings-indent-override` skill, which applies
targeted indentation overrides to specific top-level keys in a VS Code `settings.json` without
reformatting the rest of the file.

Invoke this skill whenever:

- A user wants a specific `settings.json` key's inner values indented at a non-standard depth.
- After a settings promotion, the promoted key's inner content needs a custom indent applied.
- Only specific named sub-keys within a nested object need re-indenting (e.g. `approve`,
  `matchCommandLine` inside per-command objects of `chat.tools.terminal.autoApprove`).

- **Primary Entry Point**: [.agents/skills/vscode-settings-indent-override/SKILL.md](./SKILL.md)
