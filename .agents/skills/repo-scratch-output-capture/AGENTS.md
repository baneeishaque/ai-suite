# Repo Scratch Output Capture

> **Skill:** [`repo-scratch-output-capture`](SKILL.md)

## Summary

Redirects stdout and stderr of probes, installers, and diagnostic commands to a repo-root
`scratch/` folder (gitignored). Keeps the terminal clean without suppressing output.

## When the Agent Should Invoke This Skill

- Before running any probe, installer, or long build where output may contain the failure signal.
- Whenever the agent would otherwise pipe a command to `> /dev/null` or `/tmp`.
- When asked to "keep the terminal clean" or "redirect output to a file".

## Quick Reference

```bash
SCRATCH="$(python3 .agents/skills/repo-scratch-output-capture/scripts/ensure-scratch-gitignored.py)"
my-command > "$SCRATCH/my-command.out" 2> "$SCRATCH/my-command.err"
echo "Exit: $?  See $SCRATCH/my-command.{out,err}"
```

## Key Rules

1. Use `<repo-root>/scratch/` — never `/tmp/`.
2. Always capture BOTH stdout and stderr as sibling files.
3. Add `scratch/` to the committed `.gitignore`, not just `.git/info/exclude`.
4. Never commit scratch files.
