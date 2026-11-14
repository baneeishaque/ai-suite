<!-- title: VS Code editor-tab compare extensions research sources -->

# Research Sources: VS Code Editor-Tab Compare Extensions

**Research date: 14 November 2026.** This document lists all primary sources used in the comparison report.

## Extensions evaluated

### in4margaret.compareit

| Source | URL | What it provides |
| --- | --- | --- |
| Marketplace listing | [marketplace.visualstudio.com/items?itemName=in4margaret.compareit](https://marketplace.visualstudio.com/items?itemName=in4margaret.compareit) | Installs, rating, description, features |
| Source repository | [github.com/in4margaret/compareit](https://github.com/in4margaret/compareit) | Source code, package.json, README |
| package.json | [raw.githubusercontent.com/in4margaret/compareit/master/package.json](https://raw.githubusercontent.com/in4margaret/compareit/master/package.json) | Menu contributions (explorer/context only) |
| GitHub issue #2 | [github.com/in4margaret/compareit/issues/2](https://github.com/in4margaret/compareit/issues/2) | Feature request for tab context menu (open since 2018) |

### moshfeu.diff-merge

| Source | URL | What it provides |
| --- | --- | --- |
| Marketplace listing | [marketplace.visualstudio.com/items?itemName=moshfeu.diff-merge](https://marketplace.visualstudio.com/items?itemName=moshfeu.diff-merge) | Installs, rating, description |
| Source repository | [github.com/moshfeu/vscode-diff-merge](https://github.com/moshfeu/vscode-diff-merge) | Source code, package.json, README |
| package.json | [raw.githubusercontent.com/moshfeu/vscode-diff-merge/master/package.json](https://raw.githubusercontent.com/moshfeu/vscode-diff-merge/master/package.json) | Menu contributions (editor/title/context included) |
| README | [raw.githubusercontent.com/moshfeu/vscode-diff-merge/master/README.md](https://raw.githubusercontent.com/moshfeu/vscode-diff-merge/master/README.md) | Features, known issues, maintainer notice |

### DavidKol.fastcompare

| Source | URL | What it provides |
| --- | --- | --- |
| Marketplace listing | [marketplace.visualstudio.com/items?itemName=DavidKol.fastcompare](https://marketplace.visualstudio.com/items?itemName=DavidKol.fastcompare) | Installs, rating, description |
| Source repository | [github.com/davidKolar175/fast-compare](https://github.com/davidKolar175/fast-compare) | Source code, package.json, README |
| package.json | [raw.githubusercontent.com/davidKolar175/fast-compare/HEAD/package.json](https://raw.githubusercontent.com/davidKolar175/fast-compare/HEAD/package.json) | Menu contributions (editor/title/context included) |
| Source code | [raw.githubusercontent.com/davidKolar175/fast-compare/HEAD/src/extension.ts](https://raw.githubusercontent.com/davidKolar175/fast-compare/HEAD/src/extension.ts) | Full extension source (single file) |

### outofsync42.select-compare-tabs

| Source | URL | What it provides |
| --- | --- | --- |
| Marketplace listing | [marketplace.visualstudio.com/items?itemName=outofsync42.select-compare-tabs](https://marketplace.visualstudio.com/items?itemName=outofsync42.select-compare-tabs) | Installs, rating, description |
| Source repository | [github.com/outofsync42/select-compare-tabs](https://github.com/outofsync42/select-compare-tabs) | Source code, package.json, README |
| package.json | [raw.githubusercontent.com/outofsync42/select-compare-tabs/master/package.json](https://raw.githubusercontent.com/outofsync42/select-compare-tabs/master/package.json) | Menu contributions (editor/title/context included) |
| Source code | [raw.githubusercontent.com/outofsync42/select-compare-tabs/master/extension.js](https://raw.githubusercontent.com/outofsync42/select-compare-tabs/master/extension.js) | Full extension source (single file) |
| README | [raw.githubusercontent.com/outofsync42/select-compare-tabs/master/README.md](https://raw.githubusercontent.com/outofsync42/select-compare-tabs/master/README.md) | Features, usage, license |
| GitHub issues | [github.com/outofsync42/select-compare-tabs/issues](https://github.com/outofsync42/select-compare-tabs/issues) | Open issues (#3, #4, #5) |

### Fork: ariccb/vscode-ext-select-compare-tabs

| Source | URL | What it provides |
| --- | --- | --- |
| Source repository | [github.com/ariccb/vscode-ext-select-compare-tabs](https://github.com/ariccb/vscode-ext-select-compare-tabs) | Fork with clipboard comparison |
| package.json | [raw.githubusercontent.com/ariccb/vscode-ext-select-compare-tabs/master/package.json](https://raw.githubusercontent.com/ariccb/vscode-ext-select-compare-tabs/master/package.json) | Menu contributions (includes clipboard comparison) |
| Source code | [raw.githubusercontent.com/ariccb/vscode-ext-select-compare-tabs/master/extension.js](https://raw.githubusercontent.com/ariccb/vscode-ext-select-compare-tabs/master/extension.js) | Full extension source with clipboard feature |

## Search queries performed

| Query | Tool | Purpose | Key finding |
| --- | --- | --- | --- |
| `gh search code 'selectForCompare'` | GitHub CLI | Find implementations of select-for-compare | Found `outofsync42/select-compare-tabs` |
| `gh search code 'compareWithSelected'` | GitHub CLI | Find implementations of compare-with-selected | Found `moshfeu/vscode-diff-merge` and `outofsync42/select-compare-tabs` |
| `gh search issues 'Compare with Selected vscode'` | GitHub CLI | Find feature requests and maintainer responses | Found issue in `margaretos/compareit` (open since 2018) |
| Marketplace search for "compare" | VS Code Marketplace API | Find all comparison-related extensions | Found 20+ extensions, filtered to 4 relevant ones |
| `gh api repos/outofsync42/select-compare-tabs/contents` | GitHub API | Read extension source code | Confirmed native `vscode.diff` usage |
| `gh api repos/ariccb/vscode-ext-select-compare-tabs/contents` | GitHub API | Read fork source code | Confirmed clipboard comparison feature |
| `gh api search/issues?q=repo:microsoft/vscode+"select+for+compare"+tab` | GitHub API | Check if VS Code has a built-in feature request | No direct feature request found for tab context menu |

## Extensions considered but excluded

| Extension | Marketplace ID | Reason for exclusion |
| --- | --- | --- |
| Partial Diff | `ryu1kn.partial-diff` | Already installed by user; only Explorer view, not tabs |
| Compare Helper | `keewek.compare-helper` | Compares via external tools, not native VS Code diff |
| Compare Folders | `moshfeu.compare-folders` | Folder comparison, not file comparison |
| Diff Folders | `L13RARY.l13-diff` | Folder comparison, not file comparison |
| Compare View | `chekweitan.compare-view` | Different use case (compare views) |
| Code Compare | `DevartSoftware.CodeCompare` | External tool integration |
| SemanticDiff | `semanticdiff.semanticdiff` | Language-aware diff, not tab context menu |
| VSCode Essentials | `jabacchetta.vscode-essentials` | Bundle of extensions, not focused on compare |
| Git History | `donjayamanne.githistory` | Git history comparison, not general file compare |
| Git Tree Compare | `letmaik.git-tree-compare` | Git worktree comparison, not general file compare |

## Unresolved questions

1. **Is `outofsync42.select-compare-tabs` still maintained?** The last release was v1.0.3 (August 2023). The maintainer
   has not responded to issues #3, #4, or #5. If the extension stops working in a future VS Code version,
   there may be no update.
2. **Does the fork (`ariccb/vscode-ext-select-compare-tabs`) work?** The fork adds clipboard comparison but is
   not published on the Marketplace. It would need to be built and installed from source. Its quality and
   compatibility have not been verified.
3. **Will VS Code add native tab compare?** There is no known feature request in the VS Code repository for
   adding "Select for Compare" / "Compare with Selected" to the editor-tab context menu. The VS Code team
   may add this in the future, making these extensions unnecessary.
4. **Does `outofsync42.select-compare-tabs` work with unsaved files?** The extension uses `vscode.diff`
   which supports untitled URIs, but this has not been explicitly tested.
