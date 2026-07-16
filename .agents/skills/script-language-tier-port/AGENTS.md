# Script Language Tier Port — Agent Bridge

> **Active SSOT:** [`SKILL.md`](SKILL.md)
>
> This file is a passive companion bridge. When an agent loads this folder
> via directory-walk discovery, it MUST read `SKILL.md` for the operational
> protocol.

## Trigger Phrases

Invoke this skill when ANY of the following holds for a script under review:

- The body contains `python3 -c ...` or `python3 - <<PY ... PY` (nested
  heredoc — §2.3.3 silent-hang hazard).
- A `.bash` / `.sh` / `.ps1` script is at least 50 % JSON / regex /
  string / numeric work that Python's stdlib would handle natively.
- A user / reviewer asks "should this script really be in bash?" or
  "port this to Python."
- A skill-factory audit on an existing skill flags a tier-violation
  script.
- A skill-maintenance change reveals the script is the wrong tier — port
  FIRST as its own atomic commit.

## When NOT to Invoke

- Brand-new unshipped script — use
  [`scripting-language-selection-rules.md`](../../../ai-agent-rules/scripting-language-selection-rules.md)
  directly to pick the right tier the first time.
- Script genuinely IS at least 80 % native binary orchestration — Tier-2
  PowerShell is correct, not a porting candidate.
- Vendored / frozen-dependency script you cannot modify.

## See Also

- Active protocol → [`SKILL.md`](SKILL.md)
- Tier definitions →
  [`../../../ai-agent-rules/scripting-language-selection-rules.md`](../../../ai-agent-rules/scripting-language-selection-rules.md)
- Sister skill for new skill authoring →
  [`../skill-factory/SKILL.md`](../skill-factory/SKILL.md)
- Reference port that motivated this skill →
  [`../vscode-setting-schema-discovery/SKILL.md`](../vscode-setting-schema-discovery/SKILL.md)
