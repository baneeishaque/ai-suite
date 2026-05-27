---
name: Bash Multiline To Single Line
description: Passive context bridge for the bash-multiline-to-single-line base primitive.
category: Text-Manipulation
---

# Bash Multiline To Single Line (Ref)

Atomic primitive that flattens bash `\<newline>` continuations into a single
physical line, optionally restricted to a line range. Domain-agnostic — no
awareness of git, find, grep, or any specific command.

Most commonly invoked by [command-autoapprove-onboarding](../command-autoapprove-onboarding/SKILL.md)
to normalize user-pasted commands before regex coverage analysis.

- **Primary Entry Point**: [.agents/skills/bash-multiline-to-single-line/SKILL.md](./SKILL.md)
