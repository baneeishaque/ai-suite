---
name: Brew Upgrade Command Assembly
description: Passive context bridge for the brew-upgrade-command-assembly base primitive.
category: Package-Management
---

# Brew Upgrade Command Assembly (Ref)

Generic primitive that assembles Homebrew upgrade/cleanup command chains
from package lists. Domain-agnostic — no awareness of outdated-leaves
discovery, priority ordering, or type resolution.

Most commonly invoked by
[brew-upgrade-workflow](../brew-upgrade-workflow/SKILL.md)
to produce the final executable command string.

- **Primary Entry Point**: [.agents/skills/brew-upgrade-command-assembly/SKILL.md](./SKILL.md)
