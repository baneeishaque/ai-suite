---
name: JSON Block Indent Override
description: Passive context bridge — composer that adds JSON awareness on top of text-block-indent-override.
category: Text-Manipulation
---

# JSON Block Indent Override (Ref)

This bridge provides passive context for the `json-block-indent-override` composer skill, which
re-indents lines inside a top-level JSON key's block with auto-quoted target sub-keys and
`json.loads` validation. It pipes through the
[text-block-indent-override](../text-block-indent-override/SKILL.md) base primitive.

Invoke directly for any JSON file. For VS Code `settings.json` specifically, prefer the
higher-level [vscode-settings-indent-override](../vscode-settings-indent-override/SKILL.md)
composer.

- **Primary Entry Point**: [.agents/skills/json-block-indent-override/SKILL.md](./SKILL.md)
