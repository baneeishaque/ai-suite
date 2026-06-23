# GitHub Repo Commit Fetch — Agent Companion Bridge

This file is the **passive context bridge** for the GitHub Repo Commit Fetch skill.

For all active instructions, tooling, and operational logic, defer entirely to:

**[SKILL.md](./SKILL.md)**

***

## When to Activate This Skill

The agent MUST activate the **GitHub Repo Commit Fetch** skill when ANY of the following is detected:

- "List the last N commits on `<repo>`."
- "What files did commit `<sha>` touch?"
- "Get me the file `<path>` at ref `<sha>` / `<branch>` without cloning."
- The agent needs to verify a GitHub-hosted file's content at a historical commit.
- A higher-level skill (e.g., `github-actions-run-audit`) needs to compose these read primitives.

***

## Quick Reference

```bash
SCRIPTS_DIR=.agents/skills/github-repo-commit-fetch/scripts

python3 "$SCRIPTS_DIR"/list-commits.py     --repo owner/name --limit 5
python3 "$SCRIPTS_DIR"/commit-details.py   --repo owner/name --sha <SHA> --files-only
python3 "$SCRIPTS_DIR"/fetch-file-at-ref.py --repo owner/name --ref <SHA> --path <PATH> --out <LOCAL>
```

> [!NOTE]
> All scripts are pure stdlib Python wrapping `gh api`. If `gh` is unavailable,
> fall back to [`github-rest-api-fallback`](../github-rest-api-fallback/SKILL.md).
