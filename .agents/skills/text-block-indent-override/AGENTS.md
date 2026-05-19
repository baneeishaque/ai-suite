---
name: Text Block Indent Override
description: Passive context bridge for the text-block-indent-override base primitive.
category: Text-Manipulation
---

# Text Block Indent Override (Ref)

This bridge provides passive context for the `text-block-indent-override` base skill, which locates
a regex-matched block in any text file and re-indents specific lines inside it from N spaces to M
spaces. Domain-agnostic — no JSON / YAML / TOML knowledge.

Invoke directly only when no domain composer exists. Otherwise compose through:

- [json-block-indent-override](../json-block-indent-override/SKILL.md)
- [vscode-settings-indent-override](../vscode-settings-indent-override/SKILL.md)

- **Primary Entry Point**: [.agents/skills/text-block-indent-override/SKILL.md](./SKILL.md)
