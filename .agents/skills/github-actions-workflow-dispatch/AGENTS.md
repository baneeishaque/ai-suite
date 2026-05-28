# GitHub Actions Workflow Dispatch — Agent Companion Bridge

This file is the **passive context bridge** for the GitHub Actions Workflow Dispatch skill.

For all active instructions, tooling, and operational logic, defer entirely to:

**[SKILL.md](./SKILL.md)**

***

## When to Activate This Skill

The agent MUST activate the **GitHub Actions Workflow Dispatch** skill when ANY of the following is detected:

- "Trigger / re-run / fire workflow `<X>`."
- "Kick off the deploy / backup / docs-regen workflow."
- "Dispatch workflow `<X>` against branch `<Y>` with input `<key>=<value>`."
- "Run workflow and wait for completion before continuing."

***

## Quick Reference

```bash
PY=~/.local/share/mise/installs/python/$(ls ~/.local/share/mise/installs/python | sort -V | tail -1)/bin/python
S=.agents/skills/github-actions-workflow-dispatch/scripts

# Fire and forget
"$PY" $S/trigger-workflow.py --repo owner/name --workflow my.yml

# Trigger and wait up to 5 minutes
"$PY" $S/trigger-workflow.py --repo owner/name --workflow my.yml --wait 300

# With inputs and custom ref
"$PY" $S/trigger-workflow.py --repo owner/name --workflow deploy.yml \
    --ref release/v2 --field environment=prod --wait 600
```

> [!IMPORTANT]
> Dispatch is a **write action**. The agent MUST obtain explicit user
> authorization before triggering — never auto-fire a workflow.
