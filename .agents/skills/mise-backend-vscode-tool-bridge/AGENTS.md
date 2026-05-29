# AGENTS.md — mise-backend-vscode-tool-bridge

Companion bridge. The SSOT is [SKILL.md](SKILL.md).

## One-Liner

Wire a non-default-backend mise binary (e.g., `github:adwinying/php`) into
the **built-in** VS Code interpreter settings for a language, across one
or more scope files (folder `settings.json` and/or `.code-workspace`).
Composer over `mise-non-standard-backend-bin-resolve` +
`vscode-multi-scope-setting-write`.

## Invocation

See [SKILL.md §3.1](SKILL.md#31-reference-invocation-php-dual-scope).

## Tier

Tier 1 (Python 3.12+) per
[scripting-language-selection-rules.md](../../../ai-agent-rules/scripting-language-selection-rules.md).
