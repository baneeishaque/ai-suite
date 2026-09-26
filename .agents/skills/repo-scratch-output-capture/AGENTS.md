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
REPO="$(git rev-parse --show-toplevel)"
printf 'scratch/\n' >> "$REPO/.gitignore" 2>/dev/null
STEM="$(python3 "$REPO/.agents/skills/general/file/scratch-artifact-naming/scripts/resolve-scratch-path.py" \
    --repo "$REPO" --purpose my-command)"
my-command > "$STEM.out" 2> "$STEM.err"
echo "Exit: $?  See $STEM.{out,err}"
```

## Key Rules

1. Use `<repo-root>/scratch/<session-id>/` — never `/tmp/`.
2. Always capture BOTH stdout and stderr as sibling files.
3. Add `scratch/` to the committed `.gitignore`, not just `.git/info/exclude`.
4. **Get the session folder + filename from
   [`scratch-artifact-naming`](../general/file/scratch-artifact-naming/SKILL.md)** —
   do not derive `<purpose>_<ts>` / `<purpose>_<ref-slug>_<sha>` by hand.
5. Never commit scratch files.
