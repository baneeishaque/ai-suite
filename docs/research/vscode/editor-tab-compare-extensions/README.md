<!-- title: VS Code editor-tab compare extensions research -->

# VS Code Editor-Tab Compare Extensions

**Research date: 14 November 2026.** This is a detailed, beginner-friendly comparison of VS Code extensions
that add "Select for Compare" and "Compare with Selected" actions to the editor-tab right-click menu.

## The short answer

The user already uses `ryu1kn.partial-diff`, which only exposes its compare action from the Explorer view,
not from the editor-tab right-click menu. Three candidate extensions were evaluated:

| Extension | Editor-tab right-click? | Select-then-compare? | Uses native diff? | Verdict |
| --- | --- | --- | --- | --- |
| [`in4margaret.compareit`](https://marketplace.visualstudio.com/items?itemName=in4margaret.compareit) | No | No (Explorer only) | Yes | Does not meet the requirement |
| [`moshfeu.diff-merge`](https://marketplace.visualstudio.com/items?itemName=moshfeu.diff-merge) | Yes | Yes | No (custom UI) | Works, but uses its own diff/merge UI with known limitations |
| [`DavidKol.fastcompare`](https://marketplace.visualstudio.com/items?itemName=DavidKol.fastcompare) | Yes | No (active-file only) | Yes | Partial — no two-step selection |
| [`outofsync42.select-compare-tabs`](https://marketplace.visualstudio.com/items?itemName=outofsync42.select-compare-tabs) | **Yes** | **Yes** | **Yes** | **Recommended** |

The extension that directly implements the requested workflow is
[`outofsync42.select-compare-tabs`](https://marketplace.visualstudio.com/items?itemName=outofsync42.select-compare-tabs).
It adds "Select for compare" and "Compare With Selected" to the editor-tab context menu and uses VS Code's
native `vscode.diff` command. It has 46,955 installs on the Marketplace.

## Start here

If these terms are new, begin with the [comparison report](comparison-report.md), which explains each
extension's behavior in plain language.

1. Read the [comparison report](comparison-report.md) for the practical differences and recommendations.
2. Read [research sources](research-sources.md) for source links, search coverage, and unresolved questions.

## What was compared

| Label | Input |
| --- | --- |
| A: `in4margaret.compareit` | Marketplace listing + `package.json` + source repository |
| B: `moshfeu.diff-merge` | Marketplace listing + `package.json` + README + source repository |
| C: `DavidKol.fastcompare` | Marketplace listing + `package.json` + source repository |
| D: `outofsync42.select-compare-tabs` | Marketplace listing + `package.json` + source repository + fork |

All evidence was gathered from public sources on 14 November 2026. No extension was installed or executed during
this research.

## Documentation layout

```text
vscode/editor-tab-compare-extensions/
├── AGENTS.md
├── README.md
├── comparison-report.md
└── research-sources.md
```
