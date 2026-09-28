# Jira acli Operations

Companion skill for automating Jira ticket creation and PR link commenting
via the `acli` CLI.

## Quick Reference

- **Skill SSOT:** [SKILL.md](./SKILL.md)
- **Scripts:** `scripts/discover-select-options.py` (JQL-probe a single-select custom field's valid option values)

## When to Apply

Use this skill when:
- Creating new Jira work items under an epic
- Commenting GitHub PR URLs on Jira tickets
- Automating repetitive Jira operations via `acli`
- Standardizing Jira ticket descriptions across a project
- Querying by, or discovering options of, a custom field (e.g. "Release Status")

## Key Standards

- Always include PR Link, Project, and Epic sections in descriptions
- Always comment PR URLs on corresponding Jira tickets for traceability
- Authentication must be verified before any operation
- Description templates use Atlassian Wiki Format (h2., h3., [Link|URL])
- **Custom fields:** `search` never returns them — fetch with `view --fields '*all'` (see SKILL.md §2.2.4a JQL and `--fields` Pitfalls). Never quote a spaced field name in `--fields` (acli strips the space → "field 'X' is not allowed"). Pass JQL as a single argv token, never a shell string.
