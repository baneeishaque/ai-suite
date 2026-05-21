# Python Package Version Update Agent

## Skills

| Skill | Path | When to use |
| :--- | :--- | :--- |
| Python Package Version Update | [`.agents/skills/python-package-version-update/SKILL.md`](.agents/skills/python-package-version-update/SKILL.md) | User asks to update Python package versions in requirements files, install updated packages in virtual environments, and verify compatibility with existing codebase. |

## Description

This agent specializes in Python package management, focusing on version updates, virtual environment management, and compatibility verification. It ensures safe package upgrades while maintaining codebase stability.

## Use Cases

- Updating package versions due to compatibility issues (e.g., ARM64 support)
- Installing newer package versions with bug fixes or security updates
- Verifying package compatibility before committing changes
- Managing Python virtual environments during package updates

## Related Skills

- [git-atomic-commit-construction](../git-atomic-commit-construction/SKILL.md) - For committing version updates
- [python-venv-repair](../python-venv-repair/SKILL.md) - For virtual environment validation
- [package-version-correction](../package-version-correction/SKILL.md) - For JavaScript/Node.js package management