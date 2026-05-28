# GitHub Actions Run Audit — Agent Companion Bridge

This file is the **passive context bridge** for the GitHub Actions Run Audit skill.

For all active instructions, tooling, and operational logic, defer entirely to:

**[SKILL.md](./SKILL.md)**

***

## When to Activate This Skill

The agent MUST activate the **GitHub Actions Run Audit** skill when ANY of the following is detected:

- "Did workflow `<X>` run? Was it successful?"
- "Show me the last N runs of `<workflow>`."
- "Did the periodic backup capture today's schema change?"
- "Trigger workflow `<X>` and verify it produced the expected artifact."
- "Download artifacts from run `<id>`."

***

## Critical Pre-Flight

> ⛔ **Workflows often live in a DIFFERENT repo from the application code.**
> Always confirm the **workflow-owning repo** first. Auditing the wrong repo
> yields stale / nonexistent runs. See `SKILL.md` §2.

***

## Quick Reference

```bash
PY=~/.local/share/mise/installs/python/$(ls ~/.local/share/mise/installs/python | sort -V | tail -1)/bin/python
THIS=.agents/skills/github-actions-run-audit/scripts

# Latest 5 runs + the very latest run's full detail
"$PY" $THIS/audit-run.py --repo owner/name --workflow my.yml

# Inspect one specific run
"$PY" $THIS/audit-run.py --repo owner/name --run-id 123456789

# Download all artifacts from one run
"$PY" $THIS/download-artifacts.py --repo owner/name --run-id 123456789 --dir ./artifacts/
```

For full audit pipeline (trigger → audit → verify committed artifact), see
`SKILL.md` §5.2 — it composes the two base skills `github-repo-commit-fetch`
and `github-actions-workflow-dispatch`.
