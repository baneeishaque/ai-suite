# VS Code Setting Schema Discovery — Agent Bridge

> **Active SSOT:** [`SKILL.md`](SKILL.md)
>
> This file is a passive companion bridge. When an agent loads this folder
> via directory-walk discovery, it MUST read `SKILL.md` for the operational
> protocol.

## Trigger Phrases

Invoke this skill when the user asks any of:

- "What does `<vscode.setting.key>` do?" and you do not recognize it.
- "Is `<setting>` real or a typo?"
- "What are the valid values for `<vscode setting>`?"
- "This setting isn't documented — find out what it does."
- Anything where a VS Code / Insiders / AntiGravity / Cursor / Codium /
  Windsurf setting key needs its schema (enum, default, description)
  resolved.

## One-Line Invocation

```bash
python3 scripts/resolve-vscode-setting.py <setting.key>
```

Auto-discovers the installed VS Code-family bundle; pass `--app <path>`
when probing a non-default fork.

## See Also

- Active protocol → [`SKILL.md`](SKILL.md)
- Script → [`scripts/resolve-vscode-setting.py`](scripts/resolve-vscode-setting.py)
- Sibling skill for *where* a tool writes (vs *what shape* it expects) →
  [`../tool-config-schema-probe/SKILL.md`](../tool-config-schema-probe/SKILL.md)
