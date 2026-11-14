<!-- title: VS Code editor-tab compare extensions comparison report -->

# Comparison Report: VS Code Editor-Tab Compare Extensions

**Research date: 14 November 2026.** This report compares four VS Code extensions that relate to comparing
files from the editor-tab context menu. It is written for a beginner: every technical term is explained
before it is used in comparisons.

## Table of contents

1. [Background: what the user needs](#1-background-what-the-user-needs)
2. [How VS Code's built-in compare works](#2-how-vs-codes-built-in-compare-works)
3. [Extension A: in4margaret.compareit](#3-extension-a-in4margaretcompareit)
4. [Extension B: moshfeu.diff-merge](#4-extension-b-moshfeudiff-merge)
5. [Extension C: DavidKol.fastcompare](#5-extension-c-davidkolfastcompare)
6. [Extension D: outofsync42.select-compare-tabs (recommended)](#6-extension-d-outofsync42select-compare-tabs-recommended)
7. [Side-by-side feature matrix](#7-side-by-side-feature-matrix)
8. [Known issues and limitations](#8-known-issues-and-limitations)
9. [Recommendation](#9-recommendation)
10. [How to install and use the recommended extension](#10-how-to-install-and-use-the-recommended-extension)

***

## 1. Background: what the user needs

The user already has `ryu1kn.partial-diff` installed. That extension lets you compare text selections
within a file, across files, or to the clipboard. However, its compare action is only reachable from
the VS Code **Explorer** view (the file tree on the left side of the window). It is not available when
you right-click on an editor **tab** (the tab bar at the top of the editor area).

The user wants an extension that provides the classic two-step compare workflow directly from
editor tabs:

1. **Step 1 — Select for Compare:** Right-click a tab and mark that file as "selected for comparison."
2. **Step 2 — Compare with Selected:** Right-click a different tab and compare it against the file
   marked in Step 1.

This is the same workflow that VS Code provides natively in the Explorer view (right-click a file →
"Select for Compare", then right-click another file → "Compare with Selected"), but applied to
editor tabs.

***

## 2. How VS Code's built-in compare works

Before evaluating extensions, it helps to understand what VS Code already provides out of the box.

### 2.1 The native diff editor

VS Code has a built-in **diff editor** that shows two files side by side with highlighted differences.
You can open it via:

- The command palette: `File: Compare Active File With...`
- The Explorer: right-click a file → "Select for Compare", then right-click another file → "Compare with Selected"
- The command line: `code --diff file1 file2`

The native diff editor uses VS Code's own diff algorithm and respects your theme, fonts, and settings.
It also supports editing the right-hand side (the "modified" file) if the file is writable.

### 2.2 Why extensions are needed

VS Code's native "Select for Compare" / "Compare with Selected" commands are only available in the
**Explorer** context menu. They are **not** available when you right-click on an editor **tab**.

This is a long-standing gap. The VS Code team has not added these commands to the tab context menu.
Several extensions have been created by the community to fill this gap.

### 2.3 Key terms

| Term | Meaning |
| --- | --- |
| **Explorer view** | The file tree panel on the left side of VS Code (Ctrl+Shift+E / Cmd+Shift+E) |
| **Editor tab** | A tab in the tab bar at the top of the editor area, representing an open file |
| **Context menu** | The menu that appears when you right-click on something |
| **Native diff** | VS Code's built-in side-by-side diff editor (uses `vscode.diff` command) |
| **Custom diff UI** | A diff viewer built by the extension itself (not VS Code's native one) |
| **Two-step selection** | First mark a file ("Select for Compare"), then compare another file against it ("Compare with Selected") |

***

## 3. Extension A: in4margaret.compareit

### 3.1 Basic information

| Property | Value |
| --- | --- |
| **Marketplace ID** | `in4margaret.compareit` |
| **Display name** | compareit |
| **Version** | 0.0.2 |
| **Installs** | ~648,315 |
| **Rating** | 4.69 (16 reviews) |
| **License** | MIT |
| **Repository** | [github.com/in4margaret/compareit](https://github.com/in4margaret/compareit) |
| **VS Code engine** | ^1.19.0 |

### 3.2 What it does

`compareit` adds two commands to the **Explorer** context menu:

- **Compare with...** — opens a file picker to choose a file to compare against the selected file
- **Compare with clipboard** — compares the selected file against the clipboard contents

### 3.3 Does it support editor-tab right-click?

**No.** The extension's `package.json` only contributes menus to `explorer/context`. There is no
`editor/title/context` entry. This means the compare action is only available from the Explorer file
tree, not from editor tabs.

### 3.4 Does it support two-step selection?

**No.** The extension uses a "compare with..." file picker approach. You right-click a file in the
Explorer, choose "Compare with...", then browse to select the second file. There is no
"Select for Compare" / "Compare with Selected" two-step workflow.

### 3.5 Does it use native diff?

**Yes.** The extension uses VS Code's built-in diff editor.

### 3.6 User feedback

The GitHub repository has an open issue (#2, opened July 2018) titled "Compare selected tab context
menu shortcuts." The user requests exactly what we need: right-click on VS Code document tabs to
get "Select for Compare" and "Compare with Selected" shortcuts. The issue has two comments, both
agreeing with the request, but **no maintainer response**. The issue has been open for over 8 years
with no resolution.

### 3.7 Verdict

**Does not meet the requirement.** No editor-tab context menu support. No two-step selection workflow.
The feature request has been ignored by the maintainer for years.

***

## 4. Extension B: moshfeu.diff-merge

### 4.1 Basic information

| Property | Value |
| --- | --- |
| **Marketplace ID** | `moshfeu.diff-merge` |
| **Display name** | Diff & Merge |
| **Version** | 0.7.0 |
| **Installs** | ~143,891 |
| **Rating** | 5.0 (16 reviews) |
| **License** | MIT |
| **Repository** | [github.com/moshfeu/vscode-diff-merge](https://github.com/moshfeu/vscode-diff-merge) |
| **VS Code engine** | ^1.38.0 |

### 4.2 What it does

`Diff & Merge` is a full diff-and-merge tool. It provides:

- **File against file:** Right-click in Explorer or on an editor tab → "Select file to compare" →
  right-click another file/tab → "Compare file with selected file"
- **File against clipboard:** Compare a file against clipboard contents
- **Git diff:** Compare a file against an older Git version
- **SVN diff:** Compare SVN changes
- **Blank diff view:** Open an empty diff view and paste content into both sides

### 4.3 Does it support editor-tab right-click?

**Yes.** The extension's `package.json` contributes menus to `editor/title/context` with commands
`diffMerge.selectToCompare` and `diffMerge.compareWithSelected`. This means the "Select file to compare"
and "Compare file with selected file" actions appear when you right-click on an editor tab.

### 4.4 Does it support two-step selection?

**Yes.** The workflow is:

1. Right-click a file in Explorer or on an editor tab → "Select file to compare"
2. Right-click another file or editor tab → "Compare file with selected file"

This is exactly the two-step workflow the user wants.

### 4.5 Does it use native diff?

**No.** This extension uses its own custom diff/merge UI built on the Monaco editor (the same editor
engine that powers VS Code). It does **not** use VS Code's native `vscode.diff` command. The README
explicitly states: "Notice that I (and seems that many others) couldn't find an easy way to implement
such feature. Therefore, the user experience may not be perfect."

### 4.6 Known limitations (from the README)

- The diff editor theme has a different look and feel than the current VS Code theme
- Left editor can be edited but cannot be saved
- File > Save is disabled
- No API to listen to "Save" event
- When moving from dark to light theme, opened windows don't refresh
- Context menu shows up for non-text files (binaries, PDFs, etc.)

### 4.7 Maintainer status

The maintainer (Mosh Feuchtwanger) added a prominent notice at the top of the README:

> "Since vscode has 3 way merge built-in, and even a better one, this extension is no longer needed.
> I keep the extension and the source code for education and references only."

This means the extension is effectively **abandoned**. It still works but will not receive updates or
bug fixes.

### 4.8 Verdict

**Works for the tab workflow, but with significant caveats.** It provides the two-step selection on
editor tabs, but uses a custom diff UI with visual and functional limitations. The extension is
abandoned by its maintainer. If you need the native VS Code diff experience, this is not the right
choice.

***

## 5. Extension C: DavidKol.fastcompare

### 5.1 Basic information

| Property | Value |
| --- | --- |
| **Marketplace ID** | `DavidKol.fastcompare` |
| **Display name** | Fast Compare |
| **Version** | 1.3.0 |
| **Installs** | ~110,708 |
| **Rating** | 5.0 (20 reviews) |
| **License** | Not specified in package.json |
| **Repository** | [github.com/davidKolar175/fast-compare](https://github.com/davidKolar175/fast-compare) |
| **VS Code engine** | ^1.70.0 |

### 5.2 What it does

`Fast Compare` adds a single command — "Compare with Active File" — to the editor-tab context menu
(`editor/title/context`) and the Explorer context menu. When you right-click a tab, it compares that
tab against whatever file is currently active in the editor.

### 5.3 Does it support editor-tab right-click?

**Yes.** The extension's `package.json` contributes menus to `editor/title/context` with the command
`fastcompare.compareWithActiveFile`. The `when` clause is `"true"`, meaning it always appears.

### 5.4 Does it support two-step selection?

**No.** The workflow is different from the classic "Select for Compare" / "Compare with Selected"
pattern. Instead:

1. Open file A (it becomes the active file)
2. Right-click on file B's tab → "Compare with Active File"
3. This compares file B against file A (the active file)

There is no "Select for Compare" step. You cannot mark a file and then compare another file against
it later. The comparison always uses the currently active file as the base.

### 5.5 Does it use native diff?

**Yes.** The extension's source code calls `vscode.commands.executeCommand("vscode.diff", ...)` which
opens VS Code's native diff editor.

### 5.6 Source code

The entire extension is a single file (`src/extension.ts`):

```typescript
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    const compareWithActiveFileDisposable = vscode.commands.registerCommand(
        'fastcompare.compareWithActiveFile', (commandContext) => {
        if (!vscode.window.activeTextEditor) {
            vscode.window.showErrorMessage("Active tab is not a Text Editor!");
            return;
        }
        if (commandContext.scheme !== "file" && commandContext.scheme !== "untitled") {
            vscode.window.showErrorMessage("Tab to compare is not a Text Editor!");
            return;
        }
        vscode.commands.executeCommand(
            "vscode.diff",
            vscode.window.activeTextEditor.document.uri,
            vscode.Uri.from(commandContext)
        );
    });
    context.subscriptions.push(compareWithActiveFileDisposable);
}
```

### 5.7 Verdict

**Partial match.** It supports editor-tab right-click and uses native diff, but it does **not** provide
the two-step "Select for Compare" / "Compare with Selected" workflow. Instead, it compares the clicked
tab against the currently active file. If your workflow is "I always want to compare against the file
I'm currently editing," this works well. If you need to mark a file and compare another file against
it later (without switching active tabs), this does not work.

***

## 6. Extension D: outofsync42.select-compare-tabs (recommended)

### 6.1 Basic information

| Property | Value |
| --- | --- |
| **Marketplace ID** | `outofsync42.select-compare-tabs` |
| **Display name** | Select Compare Tabs |
| **Version** | 1.0.3 |
| **Installs** | ~46,955 |
| **Rating** | Not available from API (Marketplace page shows stars) |
| **License** | MIT |
| **Repository** | [github.com/outofsync42/select-compare-tabs](https://github.com/outofsync42/select-compare-tabs) |
| **VS Code engine** | ^1.77.0 |

### 6.2 What it does

`Select Compare Tabs` adds three commands to the editor-tab context menu:

- **Select for compare** — marks the right-clicked tab's file as "selected for comparison"
- **Compare With Selected** — compares the right-clicked tab's file against the previously selected file
- **Swap sides** — (in the diff editor toolbar) swaps the two files being compared

### 6.3 Does it support editor-tab right-click?

**Yes.** The extension's `package.json` contributes menus to `editor/title/context` with commands
`select-compare-tabs.selectForCompare` and `select-compare-tabs.compareWithSelected`. The `when` clauses
are:

- `selectForCompare`: `editorIsOpen && !editorHasMultipleSelections`
- `compareWithSelected`: `editorIsOpen && !editorHasMultipleSelections && select-compare-tabs.compareEnabled`

This means "Select for compare" always appears on tabs, and "Compare With Selected" only appears after
you have selected a file for comparison.

### 6.4 Does it support two-step selection?

**Yes.** This is exactly the workflow the user requested:

1. Right-click on a file tab → "Select for compare" (marks it)
2. Right-click on another file tab → "Compare With Selected" (compares against the marked file)

### 6.5 Does it use native diff?

**Yes.** The extension's source code calls `vscode.commands.executeCommand('vscode.diff', file1, file2)`
which opens VS Code's native diff editor.

### 6.6 Source code

The entire extension is a single file (`extension.js`):

```javascript
const { log } = require('console');
const vscode = require('vscode');

function Extension() {
    let file1;
    let file2;

    this.selectForCompare = function (uri) {
        file1 = uri;
        vscode.commands.executeCommand('setContext', 'select-compare-tabs.compareEnabled', true);
    }

    this.compareWithSelected = function (uri) {
        file2 = uri;
        vscode.commands.executeCommand('vscode.diff', file1, file2);
        vscode.commands.executeCommand('setContext', 'select-compare-tabs.compareEnabled', false);
    }

    this.swapFiles = function () {
        let selectedEditors = vscode.window.visibleTextEditors;
        if (typeof selectedEditors[2] !== 'undefined') {
            file1 = selectedEditors[2].document.uri;
            file2 = selectedEditors[1].document.uri;
        } else {
            file1 = selectedEditors[1].document.uri;
            file2 = selectedEditors[0].document.uri;
        }
        vscode.commands.executeCommand('workbench.action.closeActiveEditor');
        vscode.commands.executeCommand('vscode.diff', file1, file2);
    }
}

function activate(context) {
    let ext = new Extension();
    context.subscriptions.push(vscode.commands.registerCommand(
        'select-compare-tabs.selectForCompare', function (event) {
            ext.selectForCompare(event);
    }));
    context.subscriptions.push(vscode.commands.registerCommand(
        'select-compare-tabs.compareWithSelected', function (event) {
            ext.compareWithSelected(event);
    }));
    context.subscriptions.push(vscode.commands.registerCommand(
        'select-compare-tabs.swapFiles', function () {
            ext.swapFiles();
    }));
}

exports.activate = activate;
```

### 6.7 Fork: ariccb/vscode-ext-select-compare-tabs

A fork exists at [github.com/ariccb/vscode-ext-select-compare-tabs](https://github.com/ariccb/vscode-ext-select-compare-tabs).
This fork adds a **clipboard comparison** feature:

- New command: "Compare File With Clipboard In New File"
- Reads clipboard contents, saves them to a configurable file path (`~/Downloads/clipboard.txt` by default),
  then opens a native diff comparing the selected file against the clipboard content
- Removes the "Swap sides" command (since VS Code now has this built-in)
- Adds error handling for missing files

This fork is not published on the Marketplace. To use it, you would need to build and install it from source.

### 6.8 Known issues (from GitHub)

| Issue # | Title | Status |
| --- | --- | --- |
| #5 | Inconsistent capitalization ("Select for compare" vs "Compare With Selected") | Open (since Mar 2025) |
| #4 | Compare file with clipboard in editable and swappable diff | Open (since Jul 2024) |
| #3 | Support for use other than from tab menu (keyboard shortcuts don't work) | Open (since Feb 2024) |

### 6.9 Verdict

**Best match.** This is the only extension found that provides:

- Editor-tab right-click support
- Two-step "Select for Compare" / "Compare with Selected" workflow
- Native VS Code diff editor

It is simple, focused, and does exactly what the user needs. The main downsides are: it is a small community
extension with limited maintenance, it has a few open issues, and it does not support clipboard comparison
(the fork adds this but is not published).

***

## 7. Side-by-side feature matrix

| Feature | in4margaret.compareit | moshfeu.diff-merge | DavidKol.fastcompare | outofsync42.select-compare-tabs |
| --- | --- | --- | --- | --- |
| Editor-tab right-click | No | Yes | Yes | Yes |
| Two-step selection (Select → Compare) | No | Yes | No | Yes |
| Native VS Code diff | Yes | No (custom UI) | Yes | Yes |
| Compare with clipboard | Yes | Yes | No | No (fork adds it) |
| Compare with active file | No | No | Yes | No |
| Swap sides in diff | No | Yes | No | Yes |
| Git/SVN diff | No | Yes | No | No |
| Blank diff view | No | Yes | No | No |
| Maintainer active? | No (issue open 8+ years) | No (abandoned) | Yes (v1.3.0 in 2026) | Limited (last update 2023) |
| Marketplace installs | ~648K | ~144K | ~111K | ~47K |

***

## 8. Known issues and limitations

### 8.1 outofsync42.select-compare-tabs (recommended)

- **Capitalization inconsistency:** "Select for compare" (lowercase 'c') vs "Compare With Selected" (uppercase 'W').
  Cosmetic only. (Issue #5)
- **No clipboard comparison:** The base extension does not support comparing against clipboard. The fork
  (`ariccb/vscode-ext-select-compare-tabs`) adds this but is not published on the Marketplace.
- **No keyboard shortcut support:** The commands are registered but don't work when invoked from the
  Command Palette or keyboard shortcuts — they only work from the tab context menu. (Issue #3)
- **No active maintainer:** The last release was v1.0.3 (August 2023). The maintainer may not respond to
  issues.
- **Simple implementation:** The extension stores file references in module-level variables. If VS Code
  crashes or the extension host restarts, the "selected" file is lost. This is expected for a simple
  extension.

### 8.2 DavidKol.fastcompare

- **No two-step selection:** You must have the base file open and active before right-clicking the
  comparison file. If you switch tabs, the base changes.
- **No clipboard support:** Cannot compare against clipboard contents.

### 8.3 moshfeu.diff-merge

- **Abandoned:** The maintainer explicitly states the extension is no longer needed.
- **Custom UI limitations:** Different look and feel from VS Code's native diff editor.
- **Cannot save:** The left editor cannot be saved; File > Save is disabled.
- **Theme issues:** Dark/light theme switching doesn't refresh the diff view.

### 8.4 in4margaret.compareit

- **No tab support:** Only works from the Explorer view.
- **No two-step selection:** Uses file picker instead.
- **Abandoned:** Feature request open for 8+ years with no maintainer response.

***

## 9. Recommendation

**Install `outofsync42.select-compare-tabs`.**

It is the only extension found that provides all three of the user's requirements:

1. ✅ Editor-tab right-click support
2. ✅ Two-step "Select for Compare" / "Compare with Selected" workflow
3. ✅ Native VS Code diff editor

If you also need clipboard comparison, consider building and installing the fork
(`ariccb/vscode-ext-select-compare-tabs`) which adds this feature. Alternatively, you can use
VS Code's built-in "Compare Active File with Clipboard" command (available via the Command Palette).

If you prefer the "compare against active file" workflow (where the base is always the file you're
currently editing), `DavidKol.fastcompare` is a good alternative with a more active maintainer and
higher install count.

***

## 10. How to install and use the recommended extension

### 10.1 Installation

**From the VS Code Marketplace:**

1. Open VS Code
2. Press `Ctrl+Shift+X` (Windows/Linux) or `Cmd+Shift+X` (macOS) to open the Extensions view
3. Search for "Select Compare Tabs" or "outofsync42.select-compare-tabs"
4. Click "Install"
5. Reload VS Code if prompted

**From the command line:**

```sh
code --install-extension outofsync42.select-compare-tabs
```

### 10.2 Usage

1. Open two or more files in VS Code (they appear as tabs in the editor area)
2. Right-click on the first file's tab → select **"Select for compare"**
   (This marks the file. You won't see a visual indicator, but the extension remembers it.)
3. Right-click on the second file's tab → select **"Compare With Selected"**
   (VS Code's native diff editor opens, showing the two files side by side.)
4. In the diff editor, you can use the **"Swap sides"** button in the toolbar to switch
   which file is on the left and which is on the right.

### 10.3 Tips

- The "selected for compare" state is stored in memory. If VS Code restarts or the extension host
  crashes, you'll need to re-select the first file.
- The "Compare With Selected" menu item only appears after you've selected a file for comparison.
  If you don't see it, right-click a tab and choose "Select for compare" first.
- For unsaved files (untitled documents), the extension should still work since it uses `vscode.diff`
  which supports untitled URIs.
- If you need to compare against clipboard contents, use VS Code's built-in command:
  `File: Compare Active File with Clipboard` (available via the Command Palette).

### 10.4 Verification

After installation, verify the extension is working:

1. Open two text files (e.g., `file1.txt` and `file2.txt`)
2. Right-click on `file1.txt`'s tab — you should see "Select for compare" in the context menu
3. Click "Select for compare"
4. Right-click on `file2.txt`'s tab — you should see "Compare With Selected" in the context menu
5. Click "Compare With Selected" — a diff editor should open showing both files side by side

If "Select for compare" does not appear, check that:

- The extension is installed and enabled (Extensions view → search "Select Compare Tabs")
- You are right-clicking on an editor **tab** (not in the Explorer or on a file in the editor body)
- The file is a text file (not a binary, image, or special editor)

***

## Appendix A: Research methodology

This research was conducted on 14 November 2026 using the following methods:

1. **Marketplace search:** Searched the VS Code Marketplace for extensions related to file comparison,
   diff, and merge.
2. **GitHub code search:** Searched GitHub for repositories containing "selectForCompare" and
   "compareWithSelected" to find any implementation of the two-step tab workflow.
3. **GitHub issue search:** Searched GitHub issues for "Compare with Selected vscode" to find feature
   requests and maintainer responses.
4. **Source code review:** Read the `package.json` and source code of each candidate extension to
   verify which context menus they contribute to and which diff engine they use.
5. **Fork analysis:** Identified and analyzed the fork `ariccb/vscode-ext-select-compare-tabs` which
   adds clipboard comparison.

### Search queries used

| Query | Purpose | Result |
| --- | --- | --- |
| `gh search code 'selectForCompare'` | Find any implementation of select-for-compare | Found `outofsync42/select-compare-tabs` |
| `gh search code 'compareWithSelected'` | Find any implementation of compare-with-selected | Found `moshfeu/vscode-diff-merge` and `outofsync42/select-compare-tabs` |
| `gh search issues 'Compare with Selected vscode'` | Find feature requests and maintainer responses | Found issue in `margaretos/compareit` (open since 2018, no maintainer response) |
| Marketplace search for "compare" | Find all comparison-related extensions | Found 20+ extensions, filtered to 4 relevant ones |
| `gh api repos/outofsync42/select-compare-tabs/contents` | Read extension source code | Confirmed native `vscode.diff` usage |

### Extensions considered but excluded

| Extension | Reason for exclusion |
| --- | --- |
| `ryu1kn.partial-diff` | Already installed by user; only Explorer view, not tabs |
| `keewek.compare-helper` | Compares via external tools, not native VS Code diff |
| `moshfeu.compare-folders` | Folder comparison, not file comparison |
| `L13RARY.l13-diff` | Folder comparison, not file comparison |
| `chekweitan.compare-view` | Different use case (compare views) |
| `DevartSoftware.CodeCompare` | External tool integration |
| `semanticdiff.semanticdiff` | Language-aware diff, not tab context menu |
| `jabacchetta.vscode-essentials` | Bundle of extensions, not focused on compare |

***

## Appendix B: Glossary

| Term | Definition |
| --- | --- |
| **Context menu** | The menu that appears when you right-click on an element in VS Code |
| **Editor tab** | A tab in the tab bar at the top of the editor area, representing an open file |
| **Explorer view** | The file tree panel on the left side of VS Code |
| **Extension host** | The process that runs VS Code extensions; if it crashes, extension state is lost |
| **Marketplace** | The VS Code extension marketplace (marketplace.visualstudio.com) |
| **Native diff** | VS Code's built-in side-by-side diff editor, opened via `vscode.diff` command |
| **Two-step selection** | First mark a file ("Select for Compare"), then compare another file against it |
| **URI** | Uniform Resource Identifier; in VS Code, file paths are represented as URIs |
| **vscode.diff** | The VS Code command that opens the native diff editor for two files |
