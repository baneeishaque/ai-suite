---
name: NPM Global Package Path Discovery
description: Passive context bridge for finding the exact global npm package directory, CLI shim path, and runtime fallback command.
category: Environment-Management
---

# NPM Global Package Path Discovery (Ref)

This bridge provides passive context for the npm-global-package-path-discovery skill.

Invoke this skill when a user asks where a globally installed npm package is located,
or when a global package command is missing and the workflow must verify whether the
package exposes a CLI shim via the package.json bin field.

- Primary Entry Point: [SKILL.md](./SKILL.md)
- Related Skill: [mise-tool-management](../mise-tool-management/SKILL.md)
- Related Skill: [system-wide-tool-management](../system-wide-tool-management/SKILL.md)
