# brew-upgrade-zsh-parse-error-10de29229ffe2XlWZDaPZRh2LK

**Session ID:** ses_10de29229ffe2XlWZDaPZRh2LK
**Created:** 6/23/2026, 7:04:35 AM
**Updated:** 6/23/2026, 1:02:10 PM

---

## Assistant (Build · Big Pickle · 3.1s)

_Thinking:_

OK, the MD038 for brew-upgrade-command-assembly line 80 was fixed. Now the MD038 on line 119 — let me check that one.

**Tool: read**

**Input:**
```json
{
  "offset": 115,
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/brew-upgrade-command-assembly/SKILL.md",
  "limit": 10
}
```

**Output:**
```
<path>/Users/dk/lab-data/ai-suite/.agents/skills/brew-upgrade-command-assembly/SKILL.md</path>
<type>file</type>
<content>
115: The raw string this primitive produces follows this structure (one logical line):
116: 
117: ```text
118: export HOMEBREW_DOWNLOAD_CONCURRENCY=1; brew upgrade --verbose --cask <first-cask> && brew cleanup --verbose <first-cask> && brew upgrade --verbose --formula <f1> && brew cleanup --verbose <f1> && brew upgrade --verbose --cask <c1> && brew cleanup --verbose <c1> && brew cleanup --prune=all --verbose && brew fetch --cask --verbose <fetch1>
119: ```
120: 
121: **Join pattern:** The first join after `export ...` is `; ` (NOT ` && `) because the export is a standalone statement whose exit code is irrelevant. All subsequent brew subcommands are joined with ` && `. A common mistake is writing `export ...; && brew upgrade ...` — the `;` terminates the export, leaving nothing for `&&` to chain to, which causes a shell parse error. See [`general/macos-shell-portability`](../general/macos-shell-portability/SKILL.md) §5.1 for details.
122: 
123: Key constraints enforced:
124: 

(Showing lines 115-124 of 253. Use offset=125 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 23.1s)

_Thinking:_

The MD038 on line 119 is actually about the code block at line 118 (the backtick-fenced code block content with `; ` inside). Wait, let me check — the error says "line 119" — that's the closing backtick fence. But the error message says `Spaces inside code span elements [Context: "; "]`. It could be that there was a code span (inline backticks) previously on line 119 but now the file has changed.

Wait, I actually already fixed this by changing `; ` to `;` then space. But the error was at line 119 originally. Let me re-check. The original line 119 was the closing fence of the code block.

Actually, looking more carefully at the linter output:
- `.agents/skills/brew-upgrade-command-assembly/SKILL.md:80:30 error MD038/no-space-in-code Spaces inside code span elements [Context: "`; `"]`

Line 80 was the `; ` inside backticks. I just changed that line. So the MD038 on that line should be fixed.

- `.agents/skills/brew-upgrade-command-assembly/SKILL.md:119:58 error MD038/no-space-in-code Spaces inside code span elements [Context: "`; `"]`

Line 119 — this is in the text after the code block. Let me check if the line is still there after my edits. The new line 121 has `` `; ` `` — yes, that's where the second MD038 is coming from.

Let me fix line 121 — the `; ` inside backticks.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/brew-upgrade-command-assembly/SKILL.md",
  "oldString": "**Join pattern:** The first join after `export ...` is `; ` (NOT ` && `) because the export is a standalone statement whose exit code is irrelevant. All subsequent brew subcommands are joined with ` && `. A common mistake is writing `export ...; && brew upgrade ...` — the `;` terminates the export, leaving nothing for `&&` to chain to, which causes a shell parse error. See [`general/macos-shell-portability`](../general/macos-shell-portability/SKILL.md) §5.1 for details.",
  "newString": "**Join pattern:** The first join after `export ...` is `;` (NOT ` && `)\nbecause the export is a standalone statement whose exit code is irrelevant.\nAll subsequent brew subcommands are joined with ` && `. A common mistake is\nwriting `export ...; && brew upgrade ...` — the `;` terminates the export,\nleaving nothing for `&&` to chain to, which causes a shell parse error.\nSee [`general/macos-shell-portability`](../general/macos-shell-portability/SKILL.md)\n§5.1 for details."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 2.9s)

_Thinking:_

Good. Now let me fix the other line length issues in brew-upgrade-command-assembly. Let me check the remaining ones.

**Tool: read**

**Input:**
```json
{
  "offset": 170,
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/brew-upgrade-command-assembly/SKILL.md",
  "limit": 30
}
```

**Output:**
```
<path>/Users/dk/lab-data/ai-suite/.agents/skills/brew-upgrade-command-assembly/SKILL.md</path>
<type>file</type>
<content>
170: 
171: ```bash
172: python3 .agents/skills/brew-upgrade-command-assembly/scripts/assemble-brew-command.py \
173:   --formula-names "gh,jq" \
174:   --cask-names "google-chrome,onedrive" \
175:   --first "claude-code@latest"
176: ```
177: 
178: The output places `claude-code@latest` first in the chain, before `gh`, `jq`, and the rest.
179: 
180: ***
181: 
182: ## 6. Output Capture Patterns
183: 
184: The generated brew command chain can be long (dozens of `upgrade && cleanup` pairs). The user typically needs to see live progress AND keep a log. Two patterns suit this:
185: 
186: ### 6.1 Interactive: `tee` (live progress + log file)
187: 
188: Pipe the entire chain through `tee` to watch output scroll while saving a permanent log:
189: 
190: ```bash
191: python3 .agents/skills/brew-upgrade-command-assembly/scripts/assemble-brew-command.py \
192:   --formula-names "gh,jq" \
193:   --cask-names "google-chrome"
194: ```
195: 
196: Then execute the output with `tee`:
197: 
198: ```bash
199: <assembled-command> | tee brew.log

(Showing lines 170-199 of 259. Use offset=200 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 8.5s)

_Thinking:_

I see the line length issues:
- Line 184: long line about "dozens of upgrade && cleanup pairs" 
- Let me also check lines 194, 198, etc.

Let me fix the longest lines.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/brew-upgrade-command-assembly/SKILL.md",
  "oldString": "The generated brew command chain can be long (dozens of `upgrade && cleanup` pairs). The user typically needs to see live progress AND keep a log. Two patterns suit this:",
  "newString": "The generated brew command chain can be long (dozens of `upgrade && cleanup`\npairs). The user typically needs to see live progress AND keep a log. Two\npatterns suit this:"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 2.9s)

_Thinking:_

Now check the remaining line length issues. Let me read further in the file.

**Tool: read**

**Input:**
```json
{
  "offset": 200,
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/brew-upgrade-command-assembly/SKILL.md",
  "limit": 60
}
```

**Output:**
```
<path>/Users/dk/lab-data/ai-suite/.agents/skills/brew-upgrade-command-assembly/SKILL.md</path>
<type>file</type>
<content>
200: ```bash
201: <assembled-command> | tee brew.log
202: ```
203: 
204: This shows every package's progress on the terminal AND writes a byte-for-byte copy to `brew.log` in the working directory. On macOS, `tee` is the BSD variant — `tee --version` fails, but `tee --help` works. See [`general/macos-shell-portability`](../general/macos-shell-portability/SKILL.md) §4.1.
205: 
206: ### 6.2 Silent: `repo-scratch-output-capture` (background / unattended)
207: 
208: For probes, pre-flights, or CI-like runs where live output is not needed, use the [`repo-scratch-output-capture`](../repo-scratch-output-capture/SKILL.md) base skill. It redirects stdout and stderr into separate files under a gitignored `scratch/` folder co-located with the repo:
209: 
210: ```bash
211: SCRATCH="$(python3 .agents/skills/repo-scratch-output-capture/scripts/ensure-scratch-gitignored.py)"
212: <assembled-command> > "$SCRATCH/brew-upgrade.out" 2> "$SCRATCH/brew-upgrade.err"
213: echo "Exit: $?  See $SCRATCH/brew-upgrade.{out,err}"
214: ```
215: 
216: ### 6.3 Combined (both stdout and stderr through tee)
217: 
218: The `tee` pattern above only captures stdout. To capture both stdout and stderr while still seeing both on the terminal:
219: 
220: ```bash
221: <assembled-command> 2>&1 | tee brew.log
222: ```
223: 
224: ***
225: 
226: ## 7. Related Skills
227: 
228: | Skill | Relationship |
229: | :--- | :--- |
230: | [`brew-upgrade-workflow`](../brew-upgrade-workflow/SKILL.md) | Composer — discovers outdated leaves, resolves types, and pipes sorted lists into this base assembler |
231: | [`general/macos-shell-portability`](../general/macos-shell-portability/SKILL.md) | Reference — macOS shell differences (zsh, BSD tools, `; &&` pitfalls) that affect how the generated command runs |
232: | [`repo-scratch-output-capture`](../repo-scratch-output-capture/SKILL.md) | Companion — silent output capture to `scratch/` for background brew runs |
233: 
234: ***
235: 
236: ## 8. Traceability
237: 
238: - **Source**: `ai-agent-rules/brew-rules.md` Section 3 — Sequential Upgrade and Cleanup Workflow
239: - **Industrialized via**: `rule-to-skill-industrialization` protocol
240: - **Constraint source**: `brew-rules.md` §3.5 (fetch-after-cleanup
241:   ordering), §3.6 (export prefix), §1.3 (no --cask/--formula on cleanup)
242: 
243: ## 9. Changelog
244: 
245: ### v3 (2026-06-23)
246: 
247: - **`;` vs `&&` clarification**: §3 Generated Command Anatomy now explicitly documents that the first join is `;` not ` && `, and warns about the common `export ...; &&` parse error.
248: - **Output capture patterns**: New §6 documents three capture patterns: interactive `tee`, silent `repo-scratch-output-capture`, and combined `2>&1 | tee`.
249: - **Related Skills**: New §7 table links `brew-upgrade-workflow`, `general/macos-shell-portability`, and `repo-scratch-output-capture`.
250: - **Portability cross-ref**: §3 links to `general/macos-shell-portability` §5.1 for the `; &&` pitfall explanation.
251: - **Section renumbering**: Traceability moved to §8, Changelog to §9.
252: 
253: ### v2 (2026-06-23)
254: 
255: - **`--first` flag added**: Packages listed via `--first` are placed first in the command
256:   chain, before all formulae and casks. Internally refactored `_add_pkg()` helper extracted
257:   for DRY.
258: - **Stdin mode extended**: `first:<name>` prefix now supported alongside `formula:`, `cask:`,
259:   `fetch:`.

(Showing lines 200-259 of 261. Use offset=260 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 13.6s)

_Thinking:_

I need to fix:
- Line 204: long line (about 195 chars) — "This shows every package's progress..."
- Line 208: long line — "For probes, pre-flights, or CI-like runs..."
- Line 230: long line in table (brew-upgrade-workflow row)
- Line 231: long line in table (macos-shell-portability row)
- Line 232: long line in table (repo-scratch-output-capture row)
- Line 247-251: Maybe long lines in changelog

Wait, the markdownlint config has `Expected: 120` but many of these lines are fine. Let me check the actual lengths.

Actually, let me just wrap the problematic lines. I'll use python for precise wrapping.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/brew-upgrade-command-assembly/SKILL.md",
  "oldString": "This shows every package's progress on the terminal AND writes a byte-for-byte copy to `brew.log` in the working directory. On macOS, `tee` is the BSD variant — `tee --version` fails, but `tee --help` works. See [`general/macos-shell-portability`](../general/macos-shell-portability/SKILL.md) §4.1.",
  "newString": "This shows every package's progress on the terminal AND writes a byte-for-byte\ncopy to `brew.log` in the working directory. On macOS, `tee` is the BSD variant\n— `tee --version` fails, but `tee --help` works. See\n[`general/macos-shell-portability`](../general/macos-shell-portability/SKILL.md)\n§4.1."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 13.1s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/brew-upgrade-command-assembly/SKILL.md",
  "oldString": "For probes, pre-flights, or CI-like runs where live output is not needed, use the [`repo-scratch-output-capture`](../repo-scratch-output-capture/SKILL.md) base skill. It redirects stdout and stderr into separate files under a gitignored `scratch/` folder co-located with the repo:",
  "newString": "For probes, pre-flights, or CI-like runs where live output is not needed, use\nthe [`repo-scratch-output-capture`](../repo-scratch-output-capture/SKILL.md)\nbase skill. It redirects stdout and stderr into separate files under a\ngitignored `scratch/` folder co-located with the repo:"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 11.2s)

_Thinking:_

Now the Related Skills table rows are also too long. Let me fix those.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/brew-upgrade-command-assembly/SKILL.md",
  "oldString": "| Skill | Relationship |\n| :--- | :--- |\n| [`brew-upgrade-workflow`](../brew-upgrade-workflow/SKILL.md) | Composer — discovers outdated leaves, resolves types, and pipes sorted lists into this base assembler |\n| [`general/macos-shell-portability`](../general/macos-shell-portability/SKILL.md) | Reference — macOS shell differences (zsh, BSD tools, `; &&` pitfalls) that affect how the generated command runs |\n| [`repo-scratch-output-capture`](../repo-scratch-output-capture/SKILL.md) | Companion — silent output capture to `scratch/` for background brew runs |",
  "newString": "| Skill | Relationship |\n| :--- | :--- |\n| [`brew-upgrade-workflow`](../brew-upgrade-workflow/SKILL.md) | Composer — discovers outdated leaves and pipes sorted lists into this assembler |\n| [`general/macos-shell-portability`](../general/macos-shell-portability/SKILL.md) | Reference — macOS shell differences (zsh, BSD tools, `;` vs `&&`) for brew commands |\n| [`repo-scratch-output-capture`](../repo-scratch-output-capture/SKILL.md) | Companion — silent output capture to `scratch/` for background brew runs |"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 3.9s)

_Thinking:_

Now let me run lint again to check if this file is clean.

**Tool: bash**

**Input:**
```json
{
  "command": "markdownlint-cli2 \\\n  \".agents/skills/brew-upgrade-command-assembly/SKILL.md\"",
  "description": "Lint brew-upgrade-command-assembly",
  "timeout": 30000
}
```

**Output:**
```
markdownlint-cli2 v0.22.1 (markdownlint v0.40.0)
Finding: .agents/skills/brew-upgrade-command-assembly/SKILL.md
Linting: 1 file(s)
Summary: 2 error(s)
.agents/skills/brew-upgrade-command-assembly/SKILL.md:254:121 error MD013/line-length Line length [Expected: 120; Actual: 182]
.agents/skills/brew-upgrade-command-assembly/SKILL.md:255:121 error MD013/line-length Line length [Expected: 120; Actual: 155]

```

---

## Assistant (Build · Big Pickle · 3.3s)

_Thinking:_

Those are the pre-existing v2 changelog lines (lines 254-255). These were already in the file before my edits. Let me check them — they might have been exceeding 120 chars already. Let me fix them too.

**Tool: read**

**Input:**
```json
{
  "offset": 253,
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/brew-upgrade-command-assembly/SKILL.md",
  "limit": 5
}
```

**Output:**
```
<path>/Users/dk/lab-data/ai-suite/.agents/skills/brew-upgrade-command-assembly/SKILL.md</path>
<type>file</type>
<content>
253: 
254: - **`;` vs `&&` clarification**: §3 Generated Command Anatomy now explicitly documents that the first join is `;` not ` && `, and warns about the common `export ...; &&` parse error.
255: - **Output capture patterns**: New §6 documents three capture patterns: interactive `tee`, silent `repo-scratch-output-capture`, and combined `2>&1 | tee`.
256: - **Related Skills**: New §7 table links `brew-upgrade-workflow`, `general/macos-shell-portability`, and `repo-scratch-output-capture`.
257: - **Portability cross-ref**: §3 links to `general/macos-shell-portability` §5.1 for the `; &&` pitfall explanation.

(Showing lines 253-257 of 268. Use offset=258 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 44.2s)

_Thinking:_

These are the v3 changelog entries I just added. Lines 254 and 255 are too long. Let me wrap them.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/brew-upgrade-command-assembly/SKILL.md",
  "oldString": "- **`;` vs `&&` clarification**: §3 Generated Command Anatomy now explicitly documents that the first join is `;` not ` && `, and warns about the common `export ...; &&` parse error.\n- **Output capture patterns**: New §6 documents three capture patterns: interactive `tee`, silent `repo-scratch-output-capture`, and combined `2>&1 | tee`.",
  "newString": "- **`;` vs `&&` clarification**: §3 Generated Command Anatomy now explicitly\n  documents that the first join is `;` not ` && `, and warns about the common\n  `export ...; &&` parse error.\n- **Output capture patterns**: New §6 documents three capture patterns:\n  interactive `tee`, silent `repo-scratch-output-capture`, and combined\n  `2>&1 | tee`."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 4.2s)

_Thinking:_

Good. Now let me fix the brew-upgrade-workflow lint errors.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/brew-upgrade-workflow/SKILL.md",
  "oldString": "**Join pattern:** The first join after `export ...` is `; ` (NOT ` && `) because the export is a standalone statement whose exit code is irrelevant. All subsequent brew subcommands are joined with ` && `. A common mistake is writing `export ...; && brew upgrade ...` — the `;` terminates the export, leaving nothing for `&&` to chain to, which causes a shell parse error. See [`general/macos-shell-portability`](../general/macos-shell-portability/SKILL.md) §5.1 for details.",
  "newString": "**Join pattern:** The first join after `export ...` is `;` (NOT ` && `)\nbecause the export is a standalone statement whose exit code is irrelevant.\nAll subsequent brew subcommands are joined with ` && `. A common mistake is\nwriting `export ...; && brew upgrade ...` — the `;` terminates the export,\nleaving nothing for `&&` to chain to, which causes a shell parse error.\nSee [`general/macos-shell-portability`](../general/macos-shell-portability/SKILL.md)\n§5.1 for details."
}
```

**Error:**
```
Could not find oldString in the file. It must match exactly, including whitespace, indentation, and line endings.
```

---

## Assistant (Build · Big Pickle · 3.5s)

_Thinking:_

Let me search for where this text appears in the workflow file.

**Tool: grep**

**Input:**
```json
{
  "pattern": "the first join after",
  "path": "/Users/dk/lab-data/ai-suite/.agents/skills/brew-upgrade-workflow"
}
```

**Output:**
```
No files found
```

---

## Assistant (Build · Big Pickle · 3.2s)

_Thinking:_

It seems the workflow SKILL.md doesn't have this text after all. The MD038 error might be elsewhere. Let me check what's on line 250 of the workflow file.

**Tool: read**

**Input:**
```json
{
  "offset": 246,
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/brew-upgrade-workflow/SKILL.md",
  "limit": 10
}
```

**Output:**
```
<path>/Users/dk/lab-data/ai-suite/.agents/skills/brew-upgrade-workflow/SKILL.md</path>
<type>file</type>
<content>
246: base skill to redirect to gitignored `scratch/` files.
247: 
248: ### 8.3 macOS Shell Portability
249: 
250: The generated command uses a `; ` (not ` && `) after the `export`
251: statement. Writing `export ...; && brew upgrade ...` causes a shell
252: parse error. See
253: [`general/macos-shell-portability`](../general/macos-shell-portability/SKILL.md) §5.1.
254: 
255: ***

(Showing lines 246-255 of 298. Use offset=256 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 7.5s)

_Thinking:_

Found it — line 250 has `; ` inside backticks. The MD038 rule says no trailing space inside code span elements. Let me fix it.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/brew-upgrade-workflow/SKILL.md",
  "oldString": "The generated command uses a `; ` (not ` && `) after the `export`",
  "newString": "The generated command uses `;` (not ` && `) after the `export`"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 3.2s)

_Thinking:_

Now fix the line length issue on the Related Skills section in brew-upgrade-workflow.

**Tool: read**

**Input:**
```json
{
  "offset": 280,
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/brew-upgrade-workflow/SKILL.md",
  "limit": 5
}
```

**Output:**
```
<path>/Users/dk/lab-data/ai-suite/.agents/skills/brew-upgrade-workflow/SKILL.md</path>
<type>file</type>
<content>
280: - **Execution Guidance**: New §8 documents three output capture patterns for the user when running the assembled command: interactive `tee`, silent `repo-scratch-output-capture`, and combined `2>&1 | tee`.
281: - **Portability cross-ref**: §8.3 links to `general/macos-shell-portability` §5.1 for the `;` vs `&&` pitfall explanation.
282: - **Related Skills**: New §9 table links `brew-upgrade-command-assembly`, `general/macos-shell-portability`, and `repo-scratch-output-capture`.
283: - **Section renumbering**: §§8-10 renumbered to accommodate new sections.
284: 

(Showing lines 280-284 of 298. Use offset=285 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 46.1s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/brew-upgrade-workflow/SKILL.md",
  "oldString": "- **Execution Guidance**: New §8 documents three output capture patterns for the user when running the assembled command: interactive `tee`, silent `repo-scratch-output-capture`, and combined `2>&1 | tee`.",
  "newString": "- **Execution Guidance**: New §8 documents three output capture patterns for\n  the user when running the assembled command: interactive `tee`, silent\n  `repo-scratch-output-capture`, and combined `2>&1 | tee`."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 4.0s)

_Thinking:_

Now fix the macos-shell-portability lint issues. Let me read the file and fix all issues.

**Tool: bash**

**Input:**
```json
{
  "command": "markdownlint-cli2 \".agents/skills/general/macos-shell-portability/SKILL.md\" \".agents/skills/general/macos-shell-portability/AGENTS.md\"",
  "description": "Lint the new skill files",
  "timeout": 30000
}
```

**Output:**
```
markdownlint-cli2 v0.22.1 (markdownlint v0.40.0)
Finding: .agents/skills/general/macos-shell-portability/SKILL.md .agents/skills/general/macos-shell-portability/AGENTS.md
Linting: 2 file(s)
Summary: 16 error(s)
.agents/skills/general/macos-shell-portability/AGENTS.md:16:121 error MD013/line-length Line length [Expected: 120; Actual: 259]
.agents/skills/general/macos-shell-portability/AGENTS.md:21:121 error MD013/line-length Line length [Expected: 120; Actual: 132]
.agents/skills/general/macos-shell-portability/AGENTS.md:23:121 error MD013/line-length Line length [Expected: 120; Actual: 145]
.agents/skills/general/macos-shell-portability/SKILL.md:20:121 error MD013/line-length Line length [Expected: 120; Actual: 177]
.agents/skills/general/macos-shell-portability/SKILL.md:24:121 error MD013/line-length Line length [Expected: 120; Actual: 181]
.agents/skills/general/macos-shell-portability/SKILL.md:36:121 error MD013/line-length Line length [Expected: 120; Actual: 129]
.agents/skills/general/macos-shell-portability/SKILL.md:60:121 error MD013/line-length Line length [Expected: 120; Actual: 195]
.agents/skills/general/macos-shell-portability/SKILL.md:92:121 error MD013/line-length Line length [Expected: 120; Actual: 209]
.agents/skills/general/macos-shell-portability/SKILL.md:115:121 error MD013/line-length Line length [Expected: 120; Actual: 164]
.agents/skills/general/macos-shell-portability/SKILL.md:130:121 error MD013/line-length Line length [Expected: 120; Actual: 263]
.agents/skills/general/macos-shell-portability/SKILL.md:134:121 error MD013/line-length Line length [Expected: 120; Actual: 193]
.agents/skills/general/macos-shell-portability/SKILL.md:163:121 error MD013/line-length Line length [Expected: 120; Actual: 176]
.agents/skills/general/macos-shell-portability/SKILL.md:164:121 error MD013/line-length Line length [Expected: 120; Actual: 138]
.agents/skills/general/macos-shell-portability/SKILL.md:165:121 error MD013/line-length Line length [Expected: 120; Actual: 167]
.agents/skills/general/macos-shell-portability/SKILL.md:166:121 error MD013/line-length Line length [Expected: 120; Actual: 139]
.agents/skills/general/macos-shell-portability/SKILL.md:170:121 error MD013/line-length Line length [Expected: 120; Actual: 280]

```

---

## Assistant (Build · Big Pickle · 3.6s)

_Thinking:_

There are many line length issues in the new SKILL.md and AGENTS.md. Instead of fixing each one manually, let me read the file and do quick fixes on all of them.

**Tool: read**

**Input:**
```json
{
  "offset": 15,
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/general/macos-shell-portability/AGENTS.md",
  "limit": 15
}
```

**Output:**
```
<path>/Users/dk/lab-data/ai-suite/.agents/skills/general/macos-shell-portability/AGENTS.md</path>
<type>file</type>
<content>
15: 
16: Read [`SKILL.md`](SKILL.md) for the full reference on macOS shell portability, including zsh differences, BSD tool behavior, and portable command patterns. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.
17: 
18: ## Cross-References
19: 
20: - [`SKILL.md`](SKILL.md) — SSOT with the complete macOS shell portability reference
21: - [`brew-upgrade-command-assembly`](../../brew-upgrade-command-assembly/SKILL.md) — consumes the `;` vs `&&` pattern documented here
22: - [`brew-upgrade-workflow`](../../brew-upgrade-workflow/SKILL.md) — composer that delegates to the assembler
23: - [`repo-scratch-output-capture`](../../repo-scratch-output-capture/SKILL.md) — alternative output capture approach (silent redirect to scratch/)

(End of file - total 23 lines)
</content>
```

---

## Assistant (Build · Big Pickle · 6.6s)

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/general/macos-shell-portability/AGENTS.md",
  "oldString": "Read [`SKILL.md`](SKILL.md) for the full reference on macOS shell portability, including zsh differences, BSD tool behavior, and portable command patterns. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.",
  "newString": "Read [`SKILL.md`](SKILL.md) for the full reference on macOS shell portability,\nincluding zsh differences, BSD tool behavior, and portable command patterns.\nDo NOT execute any step without first loading `SKILL.md` — this bridge is\nintentionally non-actionable."
}
```

**Error:**
```
The user rejected permission to use this specific tool call.
```

---

## User

can lint cli fix it? what skill sya about?

---

## Assistant (Build · Big Pickle · 5.8s)

_Thinking:_

The user is asking if markdownlint-cli2 has a fix/auto-fix mode, and what the skill says about linting. Let me check the markdownlint-cli2 docs and the relevant skill.

Actually, markdownlint-cli2 does support `--fix` to auto-fix some rules. Let me try that.

But the user is asking a meta question — they noticed the lint fix step and are wondering if there's a simpler way. Let me just try the `--fix` flag.

Some rules like MD013 (line length) aren't auto-fixable by markdownlint-cli2 — they need manual editing. But let me check if MD038 (no-space-in-code) is fixable.

Actually, let me just try running with `--fix` and see what happens.

**Tool: bash**

**Input:**
```json
{
  "command": "markdownlint-cli2 --fix \".agents/skills/general/macos-shell-portability/SKILL.md\" \".agents/skills/general/macos-shell-portability/AGENTS.md\" \".agents/skills/brew-upgrade-command-assembly/SKILL.md\" \".agents/skills/brew-upgrade-workflow/SKILL.md\" \"AGENTS.md\"",
  "description": "Auto-fix markdown issues with --fix",
  "timeout": 30000
}
```

**Output:**
```
markdownlint-cli2 v0.22.1 (markdownlint v0.40.0)
Finding: .agents/skills/general/macos-shell-portability/SKILL.md .agents/skills/general/macos-shell-portability/AGENTS.md .agents/skills/brew-upgrade-command-assembly/SKILL.md .agents/skills/brew-upgrade-workflow/SKILL.md AGENTS.md
Linting: 5 file(s)
Summary: 16 error(s)
.agents/skills/general/macos-shell-portability/AGENTS.md:16:121 error MD013/line-length Line length [Expected: 120; Actual: 259]
.agents/skills/general/macos-shell-portability/AGENTS.md:21:121 error MD013/line-length Line length [Expected: 120; Actual: 132]
.agents/skills/general/macos-shell-portability/AGENTS.md:23:121 error MD013/line-length Line length [Expected: 120; Actual: 145]
.agents/skills/general/macos-shell-portability/SKILL.md:20:121 error MD013/line-length Line length [Expected: 120; Actual: 177]
.agents/skills/general/macos-shell-portability/SKILL.md:24:121 error MD013/line-length Line length [Expected: 120; Actual: 181]
.agents/skills/general/macos-shell-portability/SKILL.md:36:121 error MD013/line-length Line length [Expected: 120; Actual: 129]
.agents/skills/general/macos-shell-portability/SKILL.md:60:121 error MD013/line-length Line length [Expected: 120; Actual: 195]
.agents/skills/general/macos-shell-portability/SKILL.md:92:121 error MD013/line-length Line length [Expected: 120; Actual: 209]
.agents/skills/general/macos-shell-portability/SKILL.md:115:121 error MD013/line-length Line length [Expected: 120; Actual: 164]
.agents/skills/general/macos-shell-portability/SKILL.md:130:121 error MD013/line-length Line length [Expected: 120; Actual: 263]
.agents/skills/general/macos-shell-portability/SKILL.md:134:121 error MD013/line-length Line length [Expected: 120; Actual: 193]
.agents/skills/general/macos-shell-portability/SKILL.md:163:121 error MD013/line-length Line length [Expected: 120; Actual: 176]
.agents/skills/general/macos-shell-portability/SKILL.md:164:121 error MD013/line-length Line length [Expected: 120; Actual: 138]
.agents/skills/general/macos-shell-portability/SKILL.md:165:121 error MD013/line-length Line length [Expected: 120; Actual: 167]
.agents/skills/general/macos-shell-portability/SKILL.md:166:121 error MD013/line-length Line length [Expected: 120; Actual: 139]
.agents/skills/general/macos-shell-portability/SKILL.md:170:121 error MD013/line-length Line length [Expected: 120; Actual: 280]

```

---

## Assistant (Build · Big Pickle · 5.2s)

_Thinking:_

The `--fix` flag worked and eliminated the brew-upgrade-command-assembly and brew-upgrade-workflow errors (they're now clean), but MD013 (line length) is not auto-fixable by markdownlint-cli2. All remaining 16 errors are MD013 line-length violations in the new skill files.

Let me use the `markdown-generation` skill which might have guidance on this, or I could just use a script to wrap lines. Actually, let me use python to wrap long lines in the affected files.

The simplest approach is to use a python script to wrap lines longer than 120 characters. But I need to be careful — code blocks, tables, and URLs shouldn't be broken.

Actually, let me just use `gsed` or `fmt` to wrap the text. But first, let me check what the existing files look like to understand the convention.

Let me just fix these manually - it's only a few lines per file.

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/general/macos-shell-portability/SKILL.md",
  "limit": 40
}
```

**Output:**
```
<path>/Users/dk/lab-data/ai-suite/.agents/skills/general/macos-shell-portability/SKILL.md</path>
<type>file</type>
<content>
1: ---
2: name: macos-shell-portability
3: description: Reference for macOS shell environment differences — zsh vs bash defaults, BSD vs GNU tool behavior, and portable command patterns for agent-authored shell commands on macOS.
4: category: Shell & Scripting
5: ---
6: 
7: # macOS Shell Portability (v1) — Reference
8: 
9: ## 1. When to Apply
10: 
11: Apply this reference whenever authoring or documenting shell commands intended for execution on macOS. Specifically:
12: 
13: - Generating brew / mise / npm / pip command chains for macOS users
14: - Documenting shell snippets in SKILL.md files that target macOS
15: - Diagnosing shell syntax errors or tool failures on macOS (e.g., `tee --version` fails, `help tee` is unknown)
16: - Writing cross-platform scripts that must work on both macOS and Linux
17: 
18: ## 2. Scope
19: 
20: This skill documents **differences** between macOS and Linux shell environments. It does NOT teach shell basics. It is consumed by other skills as a portability cross-reference.
21: 
22: ## 3. Default Shell: zsh
23: 
24: macOS Catalina (10.15, 2019) and later ship with **zsh** as the default login and interactive shell (previously bash). Key differences from bash that affect agent-authored commands:
25: 
26: | Behavior | bash | zsh (macOS default) |
27: |---|---|---|
28: | `help <cmd>` builtin | Available (`help cd`, `help echo`) | NOT available — use `man <cmd>` instead |
29: | Prompt variable | `PS1` | `PROMPT` (though `PS1` is aliased for compatibility) |
30: | Array indices | Zero-based (`${arr[0]}`) | One-based (`${arr[1]}`) |
31: | Brace expansion | `{a,b}` works | `{a,b}` works (compatible) |
32: | Process substitution | `<(cmd)` works | `<(cmd)` works (compatible) |
33: | `[[ ]]` test syntax | Works (Korn-derived) | Works (same origin) |
34: | Default startup file | `~/.bashrc`, `~/.bash_profile` | `~/.zshrc`, `~/.zprofile` |
35: 
36: **Key pitfall:** Never use `help <cmd>` on macOS — it is a bash builtin, not a zsh one. Always use `man <cmd>` or `<cmd> --help`.
37: 
38: ## 4. BSD vs GNU Tool Differences
39: 
40: macOS ships BSD variants of core utilities, not GNU variants. The following table documents common flags that differ:

(Showing lines 1-40 of 170. Use offset=41 to continue.)
</content>

<system-reminder>
Instructions from: /Users/dk/lab-data/ai-suite/.agents/skills/general/macos-shell-portability/AGENTS.md
# macOS Shell Portability — Companion Bridge

## Purpose

This file is the companion bridge for non-skill-aware agent runtimes. The operational SSOT resides in [`SKILL.md`](SKILL.md).

## When This Skill Applies

- You are authoring shell commands or documentation that targets macOS
- You encounter a shell parse error like `; &&` on macOS
- A tool's `--version` flag fails on macOS (BSD vs GNU differences)
- You need to write a cross-platform script that works on both macOS and Linux

## Operational Procedure

Read [`SKILL.md`](SKILL.md) for the full reference on macOS shell portability, including zsh differences, BSD tool behavior, and portable command patterns. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable.

## Cross-References

- [`SKILL.md`](SKILL.md) — SSOT with the complete macOS shell portability reference
- [`brew-upgrade-command-assembly`](../../brew-upgrade-command-assembly/SKILL.md) — consumes the `;` vs `&&` pattern documented here
- [`brew-upgrade-workflow`](../../brew-upgrade-workflow/SKILL.md) — composer that delegates to the assembler
- [`repo-scratch-output-capture`](../../repo-scratch-output-capture/SKILL.md) — alternative output capture approach (silent redirect to scratch/)

</system-reminder>
```

---

## Assistant (Build · Big Pickle · 4.3s)

_Thinking:_

I see the long lines in the SKILL.md. Let me fix them. The file has many MD013 line-length violations. Let me wrap the specific lines:

- Line 3: description in YAML frontmatter (this is a single line by nature, may need shortening)
- Line 11: "Apply this reference whenever authoring or documenting shell commands intended for execution on macOS. Specifically:"
- Line 15: "Diagnosing shell syntax errors or tool failures on macOS (e.g., `tee --version` fails, `help tee` is unknown)"
- Line 20: "This skill documents **differences** between macOS and Linux shell environments..."
- Line 24: "macOS Catalina (10.15, 2019) and later ship with **zsh**..."
- Line 36: "**Key pitfall:** Never use `help <cmd>` on macOS..."

Let me read the rest of the file too.

**Tool: read**

**Input:**
```json
{
  "offset": 41,
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/general/macos-shell-portability/SKILL.md"
}
```

**Output:**
```
<path>/Users/dk/lab-data/ai-suite/.agents/skills/general/macos-shell-portability/SKILL.md</path>
<type>file</type>
<content>
41: 
42: ### 4.1 `tee`
43: 
44: | Flag | BSD tee (macOS) | GNU tee (Linux) |
45: |---|---|---|
46: | `--version` | FAILS with `illegal option` | Prints version |
47: | `--help` | Prints help (works on both) | Prints help |
48: | `-a` (append) | Works | Works |
49: | Default behavior | Overwrites output file | Overwrites output file |
50: 
51: **Portable pattern:** Use `man tee` for help (works on both). Never rely on `tee --version` succeeding.
52: 
53: ### 4.2 `sed -i`
54: 
55: | Flag | BSD sed (macOS) | GNU sed (Linux) |
56: |---|---|---|
57: | `-i ''` | Requires empty-string arg AFTER `-i` (no space variant may work) | `-i` optional; with arg = backup extension |
58: | `-i` without extension | `sed -i ''` (MUST supply empty string) | `sed -i` (extension optional) |
59: 
60: **Portable pattern:** Prefer Python / Node scripts over `sed -i` for in-place file mutations. If `sed -i` is unavoidable, use `sed -i ''` on macOS (empty backup extension) or detect the platform.
61: 
62: ### 4.3 `find`
63: 
64: | Feature | BSD find (macOS) | GNU find (Linux) |
65: |---|---|---|
66: | `-printf` | NOT available | Available |
67: | `-exec {} +` | Works | Works |
68: | `-maxdepth` | Works | Works (both support this) |
69: | `-delete` | Works | Works |
70: 
71: **Portable pattern:** Avoid `-printf` on macOS. Use `-exec echo {} \;` or Python for custom output formatting.
72: 
73: ### 4.4 `xargs`
74: 
75: | Feature | BSD xargs (macOS) | GNU xargs (Linux) |
76: |---|---|---|
77: | `-0` (null delimiter) | Works | Works |
78: | `-d` (delimiter) | NOT available | Available |
79: | `-r` (no-run-if-empty) | BSD default behavior | GNU requires `-r` |
80: 
81: **Portable pattern:** Use `-0` with `find ... -print0` for null-delimited pipelines (works on both). Avoid `-d`.
82: 
83: ### 4.5 `date`
84: 
85: | Feature | BSD date (macOS) | GNU date (Linux) |
86: |---|---|---|
87: | `-d @<timestamp>` | NOT available (`-d` sets date, not parses) | Converts epoch to date |
88: | `-r <file>` | Shows file's last-modified time | NOT available |
89: | `+%s` | Works (epoch seconds from current time) | Works |
90: | `-j -f` | Parses formatted date with `-j -f` | Not needed (`-d` handles parsing) |
91: 
92: **Portable pattern:** For epoch-to-date conversion on macOS, use `date -r <timestamp>`. For date-to-epoch, use `date -j -f "%Y-%m-%d" "2026-06-23" "+%s"`. Prefer Python `datetime` for cross-platform date work.
93: 
94: ### 4.6 `grep`
95: 
96: | Feature | BSD grep (macOS) | GNU grep (Linux) |
97: |---|---|---|
98: | `-P` (Perl regex) | NOT available (unless `ggrep` installed) | Available |
99: | `-o` (only-matching) | Works | Works |
100: | `-r` (recursive) | Works (but prefer the built-in `grep` tool) | Works |
101: 
102: **Portable pattern:** Avoid `-P`. Use extended regex with `-E` instead (works on both).
103: 
104: ## 5. Common Shell Pitfalls
105: 
106: ### 5.1 `; &&` Parse Error
107: 
108: This pattern produces a shell parse error on zsh AND bash:
109: 
110: ```bash
111: export VAR=value; && command
112: #                ^^--- error: nothing between ; and &&
113: ```
114: 
115: The `;` is a command terminator — it ends the `export` command. The `&&` expects a command on its left. After `;` there is nothing, so `&&` has nothing to chain to.
116: 
117: **Correct forms:**
118: 
119: ```bash
120: # Option A: chain with && (export must succeed)
121: export VAR=value && command
122: 
123: # Option B: independent statements (run regardless)
124: export VAR=value; command
125: 
126: # Option C: mixed — export unconditionally, chain subsequent commands
127: export VAR=value; command1 && command2 && command3
128: ```
129: 
130: Option C is the pattern used by `brew-upgrade-command-assembly` — the `export HOMEBREW_DOWNLOAD_CONCURRENCY=1;` is a standalone statement (the env var is set, exit code is irrelevant), and all subsequent `brew upgrade && brew cleanup` pairs are chained with `&&`.
131: 
132: ### 5.2 Missing `help` Builtin
133: 
134: On macOS (zsh), `help cd` fails with `zsh: command not found: help`. Use `man cd` instead. In bash, `help` lists shell builtins; in zsh, `run-help` is the equivalent (often unbound by default).
135: 
136: ### 5.3 `--version` on BSD Tools
137: 
138: Many BSD tools on macOS reject `--version`:
139: 
140: ```bash
141: tee --version   # "illegal option -- -"
142: sed --version   # "illegal option -- -"
143: ```
144: 
145: Use `<tool> --help` (which both BSD and GNU accept), or `man <tool>`, instead of `--version`.
146: 
147: ## 6. Portable Command Patterns
148: 
149: When writing shell commands for macOS (and optionally Linux cross-compatibility):
150: 
151: | Goal | Portable Pattern | Avoid |
152: |---|---|---|
153: | Get tool help | `man <tool>` or `<tool> --help` | `<tool> --version` (BSD fails) |
154: | Get shell help | `man <builtin>` | `help <builtin>` (zsh fails) |
155: | Pipe with output capture | `command 2>&1 \| tee output.log` | `command &> output.log` (bash 4+ only) |
156: | In-place file edit | Use Python `pathlib.Path.write_text()` or Node.js | `sed -i` (BSD/GNU differ) |
157: | Parse date | Use Python `datetime` | `date -d` (BSD incompatible) |
158: | Suppress errors | `2>/dev/null` (works on both) | N/A |
159: | Time command | `command` prefixed with `time` (zsh has a `time` reserved word) | N/A |
160: 
161: ## 7. Cross-References
162: 
163: - [`brew-upgrade-command-assembly`](../../brew-upgrade-command-assembly/SKILL.md) — brew upgrade chain assembler that uses the `export ...; cmd1 && cmd2 && cmd3` pattern (§5.1)
164: - [`brew-upgrade-workflow`](../../brew-upgrade-workflow/SKILL.md) — composer that discovers outdated leaves and delegates to the assembler
165: - [`repo-scratch-output-capture`](../../repo-scratch-output-capture/SKILL.md) — silent stdout/stderr capture to `scratch/` (alternative to `tee` for background probes)
166: - [`is-this-command-safe`](../../is-this-command-safe/SKILL.md) — shell command safety vetting that classifies `tee overwrite` as `MUTATES`
167: 
168: ## 8. Traceability
169: 
170: - **Origin Conversation**: Session 2026-06-23 — user on macOS hit `; &&` parse error in a brew upgrade chain, then discovered `tee --version` fails and `help` is unavailable on zsh. The three gaps (zsh defaults, BSD tools, `; &&` pitfall) were extracted into this reference skill.

(End of file - total 170 lines)
</content>
```

---

## Assistant (Build · Big Pickle · 6.0s)

_Thinking:_

I need to fix the line-length violations in the SKILL.md file and AGENTS.md. The lines that are too long are:

AGENTS.md:
- Line 16: 259 chars
- Line 21: 132 chars  
- Line 23: 145 chars

SKILL.md:
- Line 3: 177 chars (YAML frontmatter description)
- Line 11: "Apply this reference whenever..."
- Line 15: "Diagnosing shell syntax errors..."
- Line 20: "This skill documents differences..."
- Line 24: "macOS Catalina (10.15, 2019)..."
- Line 36: "**Key pitfall:**..."
- Line 60: "**Portable pattern:** Prefer Python / Node scripts..."
- Line 92: "**Portable pattern:** For epoch-to-date conversion..."
- Line 115: "The `;` is a command terminator..."
- Line 130: "Option C is the pattern..."
- Line 134: "On macOS (zsh), `help cd` fails..."
- Lines 163-166: Cross-reference lines
- Line 170: "Origin Conversation" traceability

Let me fix all of these efficiently. I'll read the whole YAML frontmatter first since line 3 is the description.

**Tool: read**

**Input:**
```json
{
  "offset": 1,
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/general/macos-shell-portability/SKILL.md",
  "limit": 5
}
```

**Output:**
```
<path>/Users/dk/lab-data/ai-suite/.agents/skills/general/macos-shell-portability/SKILL.md</path>
<type>file</type>
<content>
1: ---
2: name: macos-shell-portability
3: description: Reference for macOS shell environment differences — zsh vs bash defaults, BSD vs GNU tool behavior, and portable command patterns for agent-authored shell commands on macOS.
4: category: Shell & Scripting
5: ---

(Showing lines 1-5 of 170. Use offset=6 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 8.9s)

_Thinking:_

Now let me make all the fixes. I'll use a Python script approach for efficiency since there are many lines to fix.

**Tool: bash**

**Input:**
```json
{
  "command": "python3 - <<'PYEOF'\nimport re\n\ndef wrap_line(line, maxlen=120):\n    \"\"\"Wrap a single line to maxlen, preserving leading whitespace and not breaking URLs or code spans.\"\"\"\n    if len(line) <= maxlen:\n        return line\n    # Don't wrap code blocks, tables, or list continuations\n    stripped = line.lstrip()\n    if stripped.startswith('```') or stripped.startswith('|') or stripped.startswith('- '):\n        return line\n    # Heuristic: break at word boundary before maxlen\n    # But don't break inside backtick code spans or markdown links\n    prefix = line[:len(line)-len(stripped)]\n    words = stripped.split()\n    result = []\n    current = \"\"\n    for w in words:\n        test = (current + \" \" + w).strip()\n        if len(prefix) + len(test) > maxlen and current:\n            result.append(prefix + current)\n            current = w\n        else:\n            current = test\n    if current:\n        result.append(prefix + current)\n    return \"\\n\".join(result)\n\nfiles = {\n    \".agents/skills/general/macos-shell-portability/AGENTS.md\": [16, 21, 23],\n    \".agents/skills/general/macos-shell-portability/SKILL.md\": [3, 11, 15, 20, 24, 36, 60, 92, 115, 130, 134, 163, 164, 165, 166, 170],\n}\n\nfor fpath, lineno in files.items():\n    with open(fpath) as f:\n        lines = f.readlines()\n    \n    for ln in sorted(lineno, reverse=True):\n        idx = ln - 1\n        wrapped = wrap_line(lines[idx].rstrip())\n        if wrapped != lines[idx].rstrip():\n            lines[idx] = wrapped + \"\\n\"\n    \n    with open(fpath, 'w') as f:\n        f.writelines(lines)\n\nprint(\"done\")\nPYEOF",
  "description": "Wrap long lines in markdown files",
  "timeout": 15000
}
```

**Error:**
```
The user rejected permission to use this specific tool call.
```

---

## User

i sthere script for this already?

---

## Assistant (Build · Big Pickle · 22.0s)

_Thinking:_

The user is asking if there's already a script in the codebase for wrapping long lines or fixing markdown lint issues. Let me check the skills for any markdown-related scripts.

**Tool: task**

**Input:**
```json
{
  "description": "Find markdown lint fix scripts",
  "prompt": "Search the codebase at /Users/dk/lab-data/ai-suite for any existing script that fixes markdown lint issues (MD013 line-length, wrapping, etc.) or any script that auto-fixes markdown. Look in:\n- .agents/skills/ directories (especially markdown-generation, github-ci-markdown-lint)\n- .agents/skills/general/ directories\n- Any scripts/ directories\n- ai-agent-rules/ directories\n\nReturn the paths and brief descriptions of any relevant scripts found. If no such script exists, say \"none found\".",
  "subagent_type": "explore"
}
```

**Error:**
```
Task cancelled
```

---

## User

under markdown skill

---

## Assistant (Build · Big Pickle · 4.0s)

_Thinking:_

The user is saying to look under the `markdown-generation` skill. Let me check if there's a script there for wrapping lines.

**Tool: glob**

**Input:**
```json
{
  "pattern": ".agents/skills/markdown-generation/scripts/**"
}
```

**Output:**
```
/Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/scripts/fix-fenced-code-language.py
/Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/scripts/fix-list-style.py
/Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/scripts/wrap-long-lines.py
/Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/scripts/fix-heading-spacing.py
/Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/scripts/fix-table-separators.py
/Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/scripts/fix-emphasis-as-heading.py
/Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/scripts/fix-container-fence.py
```

---

## Assistant (Build · Big Pickle · 3.6s)

_Thinking:_

Yes! There's a `wrap-long-lines.py` script. This is exactly what we need. Let me check how to use it and then run it.

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/scripts/wrap-long-lines.py"
}
```

**Output:**
```
<path>/Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/scripts/wrap-long-lines.py</path>
<type>file</type>
<content>
1: #!/usr/bin/env python3
2: """wrap-long-lines.py — Wrap prose lines exceeding the configured line-length limit.
3: 
4: Preserves code blocks, table rows, list items, blockquotes, headings,
5: and other structural markdown elements. Only wraps continuous prose
6: paragraphs.
7: 
8: Usage:
9:     python3 wrap-long-lines.py [--max 120] <file.md> [<file.md> ...]
10: 
11: File is modified in-place. Use --check for dry-run.
12: """
13: 
14: import argparse
15: import sys
16: import textwrap
17: 
18: 
19: def wrap_prose_line(line: str, max_width: int) -> str:
20:     """Wrap a single prose line, preserving leading/trailing whitespace."""
21:     leading = line[:len(line) - len(line.lstrip())]
22:     trailing = line[len(line.rstrip()):]
23:     content = line.strip()
24: 
25:     if not content:
26:         return line
27: 
28:     wrapped = textwrap.fill(
29:         content,
30:         width=max_width,
31:         break_long_words=False,
32:         break_on_hyphens=True,
33:         subsequent_indent=leading,
34:     )
35: 
36:     if trailing:
37:         wrapped += trailing
38:     return wrapped
39: 
40: 
41: def should_skip(line: str) -> bool:
42:     """Check whether a line should be skipped (preserved as-is)."""
43:     stripped = line.strip()
44:     if not stripped:
45:         return True  # blank line
46: 
47:     # Skip code fences
48:     if stripped.startswith("```"):
49:         return True
50:     if stripped.startswith("~~~"):
51:         return True
52: 
53:     # Skip table rows (| ... |)
54:     if stripped.startswith("|") and stripped.endswith("|"):
55:         return True
56: 
57:     # Skip YAML frontmatter fences
58:     if stripped == "---":
59:         return True
60: 
61:     return False
62: 
63: 
64: def fix_file(path: str, max_width: int, dry_run: bool = False) -> bool:
65:     """Wrap long prose lines in the file. Returns True if changes were made."""
66:     with open(path, encoding="utf-8") as f:
67:         lines = f.readlines()
68: 
69:     changed = False
70:     in_code_block = False
71:     in_yaml_block = False
72:     new_lines = []
73: 
74:     for i, line in enumerate(lines):
75:         raw = line.rstrip("\n").rstrip("\r")
76:         stripped = raw.strip()
77: 
78:         # Track code block state
79:         if stripped.startswith("```") or stripped.startswith("~~~"):
80:             in_code_block = not in_code_block
81:             new_lines.append(line)
82:             continue
83: 
84:         # Track YAML frontmatter
85:         if i == 0 and stripped == "---":
86:             in_yaml_block = True
87:             new_lines.append(line)
88:             continue
89:         if in_yaml_block and stripped == "---":
90:             in_yaml_block = False
91:             new_lines.append(line)
92:             continue
93: 
94:         if in_code_block or in_yaml_block:
95:             new_lines.append(line)
96:             continue
97: 
98:         if should_skip(raw):
99:             new_lines.append(line)
100:             continue
101: 
102:         # Only wrap lines that exceed the limit
103:         if len(raw) > max_width:
104:             wrapped = wrap_prose_line(raw, max_width)
105:             if wrapped != raw:
106:                 changed = True
107:                 if dry_run:
108:                     print(f"  L{i+1}: {len(raw)} chars -> wrapped")
109:                 if not dry_run:
110:                     new_lines.append(wrapped + "\n")
111:                     continue
112: 
113:         new_lines.append(line)
114: 
115:     if changed and not dry_run:
116:         with open(path, "w", encoding="utf-8") as f:
117:             f.writelines(new_lines)
118:         print(f"  Wrapped {path}")
119: 
120:     return changed
121: 
122: 
123: def main() -> int:
124:     parser = argparse.ArgumentParser(
125:         description="Wrap long prose lines in markdown files to meet a configured line limit"
126:     )
127:     parser.add_argument("files", nargs="+", help="Markdown file(s) to fix")
128:     parser.add_argument("--max", type=int, default=120, help="Maximum line width (default: 120)")
129:     parser.add_argument("--check", action="store_true", help="Dry-run: show what would change")
130:     args = parser.parse_args()
131: 
132:     exit_code = 0
133:     for path in args.files:
134:         print(f"Checking {path[:60]}...")
135:         if fix_file(path, args.max, dry_run=args.check):
136:             exit_code = 1 if args.check else 0
137: 
138:     return exit_code
139: 
140: 
141: if __name__ == "__main__":
142:     sys.exit(main())

(End of file - total 142 lines)
</content>

<system-reminder>
Instructions from: /Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/AGENTS.md
# AGENTS.md (Markdown Generation)

Refer to [SKILL.md](./SKILL.md) and [markdown-generation-rules.md](../../../ai-agent-rules/markdown-generation-rules.md) for the active operational protocol for generating lint-compliant documentation.

## Mandates

- **Line Length**: 120-character limit (MD013).
- **Auto-Fix**: Mandatory use of `markdownlint-cli2 --fix` before submission.
- **Zero Angle Brackets**: Escaping all `<` and `>` tags in technical context.

</system-reminder>
```

---

## Assistant (Build · Big Pickle · 5.4s)

_Thinking:_

There it is — `wrap-long-lines.py` in the `markdown-generation` skill. Let me run it on the affected files.

**Tool: bash**

**Input:**
```json
{
  "command": "python3 .agents/skills/markdown-generation/scripts/wrap-long-lines.py \\\n  .agents/skills/general/macos-shell-portability/SKILL.md \\\n  .agents/skills/general/macos-shell-portability/AGENTS.md",
  "description": "Wrap long lines in new skill files",
  "timeout": 15000
}
```

**Output:**
```
Checking .agents/skills/general/macos-shell-portability/SKILL.md...
  Wrapped .agents/skills/general/macos-shell-portability/SKILL.md
Checking .agents/skills/general/macos-shell-portability/AGENTS.md...
  Wrapped .agents/skills/general/macos-shell-portability/AGENTS.md

```

---

## Assistant (Build · Big Pickle · 4.1s)

_Thinking:_

The script wrapped the long lines. Let me verify by running markdownlint again.

**Tool: bash**

**Input:**
```json
{
  "command": "markdownlint-cli2 \\\n  \".agents/skills/general/macos-shell-portability/SKILL.md\" \\\n  \".agents/skills/general/macos-shell-portability/AGENTS.md\" \\\n  \".agents/skills/brew-upgrade-command-assembly/SKILL.md\" \\\n  \".agents/skills/brew-upgrade-workflow/SKILL.md\" \\\n  \"AGENTS.md\"",
  "description": "Run markdownlint on all modified files",
  "timeout": 30000
}
```

**Output:**
```
markdownlint-cli2 v0.22.1 (markdownlint v0.40.0)
Finding: .agents/skills/general/macos-shell-portability/SKILL.md .agents/skills/general/macos-shell-portability/AGENTS.md .agents/skills/brew-upgrade-command-assembly/SKILL.md .agents/skills/brew-upgrade-workflow/SKILL.md AGENTS.md
Linting: 5 file(s)
Summary: 0 error(s)

```

---

## Assistant (Build · Big Pickle · 3.5s)

All 5 files pass lint — 0 errors.

**Tool: todowrite**

**Input:**
```json
{
  "todos": [
    {
      "priority": "high",
      "content": "Create new skill: general/macos-shell-portability",
      "status": "completed"
    },
    {
      "priority": "high",
      "content": "Update brew-upgrade-command-assembly to v3",
      "status": "completed"
    },
    {
      "priority": "high",
      "content": "Update brew-upgrade-workflow to v3",
      "status": "completed"
    },
    {
      "priority": "high",
      "content": "Register new skill in root AGENTS.md",
      "status": "completed"
    },
    {
      "priority": "medium",
      "content": "Markdown lint all edited files",
      "status": "completed"
    }
  ]
}
```

**Output:**
```
[
  {
    "content": "Create new skill: general/macos-shell-portability",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Update brew-upgrade-command-assembly to v3",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Update brew-upgrade-workflow to v3",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Register new skill in root AGENTS.md",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Markdown lint all edited files",
    "status": "completed",
    "priority": "medium"
  }
]
```

---

## Assistant (Build · Big Pickle · 4.7s)

_Thinking:_

All tasks are completed. Let me summarize what was done for the user.

Done. All changes are live:

**New skill:**
- `.agents/skills/general/macos-shell-portability/` — reference covering zsh defaults, BSD vs GNU tools (`tee`, `sed`, `find`, `xargs`, `date`, `grep`), and the `; &&` pitfall

**Updated to v3:**
- `brew-upgrade-command-assembly` — §3 now clarifies `;` vs `&&` join anatomy, new §6 documents `tee`/`repo-scratch-output-capture` patterns, new §7 Related Skills
- `brew-upgrade-workflow` — new §8 Execution Guidance with the three capture patterns, new §9 Related Skills

**Root AGENTS.md** — new `macos-shell-portability` entry registered

**All 5 files pass `markdownlint-cli2` with 0 errors** — used the existing `wrap-long-lines.py` from the `markdown-generation` skill to fix MD013 line-length violations.

---

## User

k, good - but:-
---------
markdownlint-cli2 has fix mode. we must use that first. after that we have to use the available scripts under markdown skill to handle markdown lint errors. after that you can geos to further fixes in your way
--------

is this workflow correctly documented?
update all relevant skills - according to our conversation.

create new skills if that is most appropriate - you can also enrich existing skills if that is most appropriate.

we are using a layered approach for skills.
we need maximum number of reusable skills. skills can be base or composers.

plan first according to /Users/dk/lab-data/ai-suite/ai-agent-rules/ai-agent-planning-rules.md. follow the instructions in /Users/dk/lab-data/ai-suite/ai-agent-rules/ai-agent-planning-rules.md strictly & deeply.

you must obey /Users/dk/lab-data/ai-suite/ai-agent-rules/ai-rule-standardization-rules.md instructions & /Users/dk/lab-data/ai-suite/.agents/skills/skill-factory/SKILL.md skill instructions.
you can check /Users/dk/lab-data/ai-suite/.agents/skills, /Users/dk/lab-data/oleovista-acers/.agents/skills & /Users/dk/lab-data/oleovista-acers/acers-web/.claude/skills folders for existing skills.
general skills can create under ai-agents.
also refer the new skill whenever it is applicable.
these scripts helps a lot. we have to keep them as part of the skill.

---

## Assistant (Build · Big Pickle · 8.4s)

_Thinking:_

The user is asking me to:

1. Update the markdown linting workflow across relevant skills - the process should be:
   - First: `markdownlint-cli2 --fix` (auto-fix mode)
   - Second: Use available scripts under `markdown-generation/scripts/` to fix remaining issues
   - Third: Manual fixes if needed

2. This workflow isn't documented properly yet. I need to update existing skills and potentially create new ones.

3. They want me to follow the planning rules, standardization rules, and skill factory protocol strictly.

4. Let me first read the planning rules, then develop a plan.

Let me start by reading the relevant reference files.

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/ai-agent-rules/ai-agent-planning-rules.md"
}
```

**Output:**
```
<path>/Users/dk/lab-data/ai-suite/ai-agent-rules/ai-agent-planning-rules.md</path>
<type>file</type>
<content>
1: ---
2: title: Agent Planning
3: description: Guidelines for agent planning,
4:     including the core directive to plan before acting and a protocol for
5:     iterative plan revisions.
6: category: Core Agent Behavior
7: ---
8: 
9: 
10: # Agent Planning Rule: Core Principles and Best Practices
11: 
12: This document outlines the mandatory planning protocol for all AI agents. The primary directive is to ensure all
13: actions are preceded by a transparent, user-approved plan. This rule is foundational to establishing a clear,
14: trustworthy, and effective interaction model.
15: 
16: ---
17: 
18: ## 1. Goal Description & Versioning
19: 
20: All implementation plans MUST follow a strict naming and header convention to ensure traceability and version control.
21: 
22: - **H1 Header Versioning**: Every implementation plan MUST use the format `# [Goal Description] (vN)`
23:   as its primary H1 title (e.g., `# [Setup Authentication] (v1)`).
24: - **Rule Compliance Reference**: A dedicated section titled `## Rule Compliance Reference` MUST immediately follow the
25:   H1 header. It must contain a bulleted list of the specific industrial rules (with relative links) being followed in
26:   the current plan.
27: 
28: ---
29: 
30: ## 2. The Core Planning Directive
31: 
32: All agents must present a clear, step-by-step plan before any implementation. The plan must be explicit,
33: actionable, and tailored to the user’s request. **Only after the plan is approved or clarified should
34: implementation begin.**
35: 
36: This directive is not merely a formality; it is a critical safeguard. By externalizing the planning process, the
37: agent minimizes the risk of misunderstanding, prevents "hallucination," and ensures complete alignment with the
38: user's intent from the outset.
39: 
40: ### 1.1 Primary Goal Persistence Mandate
41: 
42: The agent **MUST** carry over the original 'Starting Point' enquiry (the core objective) into every version of the
43: implementation plan. This goal must remain the primary heading of the document. Any shift in focus or addition of
44: sub-tasks MUST be explicitly documented as secondary or supporting actions to this primary goal, not as a replacement
45: for it.
46: 
47: ### 1.2 Architectural Boundary Verification
48: 
49: Before adding any execution step, the agent MUST verify it is not designated as 'CI/CD Managed' in project rules.
50: Local execution of automated pipeline tasks is PROHIBITED. If a script is for CI/CD, the agent must only modify its
51: templates or source metadata.
52: 
53: ---
54: 
55: ---
56: 
57: ## 3. Components of an Effective Plan
58: 
59: An effective plan is built on four key pillars:
60: 
61: - **Clarity:** The plan must be written in plain, unambiguous language. Avoid technical jargon or internal thought
62: 
63:     process descriptions. Each step should be a simple statement of intent, easily understood by a non-technical
64:     user.
65: 
66: - **Step-by-Step Breakdown:** The plan must break down the request into a logical sequence of discrete, manageable
67: 
68:     steps. This demonstrates a structured approach and allows the user to follow the agent's thought process.
69: 
70: - **Actionability:** Every step in the plan must represent a concrete, executable action. For example, instead of
71: 
72:     "Gather information," an actionable step would be "Search the web for Q4 2024 financial reports from Google."
73: 
74: - **Tailored to the Request:** The plan should directly address the specifics of the user's query. It should not be
75: 
76:     a generic template but a custom-designed workflow that reflects the unique nuances of the task.
77: 
78: ---
79: 
80: ## 4. The Agent Planning Workflow
81: 
82: A well-structured interaction with an agent should follow this five-step workflow:
83: 
84: 1. **Deconstruct the Request:** The agent's first internal action is to analyze the user's prompt. It should
85: 
86:    identify the core task, the specific constraints, the desired output format, and any potential ambiguities or
87:    missing information.
88: 
89: 1. **Formulate the Plan:** Based on the deconstruction, the agent constructs a detailed plan. This plan should be
90: 
91:    a bulleted or numbered list that outlines the exact steps to be taken, including any necessary data retrieval,
92:    analysis, or content generation.
93: 
94: 1. **Present for Approval**: The agent presents the formulated plan to the user. This is a crucial checkpoint.
95:    The agent should explicitly ask for confirmation or for any necessary adjustments before proceeding.
96:    - **Browser Approval**: For manual testing plans, all browser-based tool requests are considered pre-approved
97:        unless explicitly denied by the user.
98: 
99: 1. **Execute the Plan:** Upon receiving user approval, the agent proceeds to implement the plan, step by step. Each
100: 
101:    action is performed as outlined, ensuring the process remains transparent and predictable.
102: 
103: 1. **Report Progress & Completion:** The agent should provide a final summary of the work done, confirming that all
104: 
105:    steps in the plan were executed. For long or complex tasks, providing interim progress updates may also be
106:    beneficial.
107: 
108: ---
109: 
110: ## 5. Handling Edge Cases and Best Practices
111: 
112: - **Ambiguous Requests:** If the user's request is unclear or incomplete, the agent must include a clarification
113: 
114:     step in its plan. The plan should state, "First, I will ask for clarification on `the ambiguous part` to ensure I
115:     proceed correctly."
116: 
117: - **Multi-Turn Conversations:** For continuous dialogues, a new, explicit plan is required for each distinct task or
118: 
119:     significant shift in the user's request. Simple, short follow-up questions do not require a new plan.
120: 
121: - **Exemptions to the Rule:** A plan is not required for trivial, single-step requests that have a straightforward,
122: 
123:     factual answer. For example, a request like "What is the capital of France?" should be answered directly without
124:     a planning step. This demonstrates the agent's ability to discern between simple queries and complex tasks.
125: 
126: ---
127: 
128: ## 6. Iterative Planning and Plan Versioning
129: 
130: The initial plan is a blueprint, not an unbreakable contract. For complex,
131: 
132: - **Categorical Alignment**: Group changes by their architectural layer (e.g., UI, Logic, Docs) unless they are
133: 
134:     functionally coupled.
135: 
136: - **Git Hygiene & Rebase Integration**: For tasks involving multiple branches or history refinement, the plan MUST
137: 
138:     include:
139: 
140: - **Hierarchical Mermaid Mapping**: Visualizing branch dependencies (referencing [Git Rebase Standardization
141: 
142:     Rules](./git-rebase-standardization-rules.md)).
143: 
144: - **CAM Table**: Mapping specific actions per commit to ensure logic isolation.
145: 
146: - **Workflow-First Priority**: If changes involve CI/CD workflows (GitHub Actions, scripts), the agent **MUST** fix,
147: 
148:     test, and verify the workflow functionality *before* arranging or executing commits. Functional stability of the
149:     CI pipeline takes precedence over documentation or stylistic refinements.
150: 
151: ### 1.1 Long-Running & Dynamic Tasks
152: 
153: For long-running or dynamic tasks, the agent may encounter new information or unforeseen obstacles that necessitate
154: a change in direction. In these cases, the agent MUST NOT deviate from the original plan without explicit approval.
155: 
156: ---
157: 
158: ## 7. Industrial Planning Mandates
159: 
160: - **Environment State Check**: Every plan involving runtime verification MUST include a prerequisite step to
161:     confirm the application is running and accessible (e.g., "Verify App is live at `http://localhost:3000`").
162: - **Maximum Literal Detail**: Plans must be exhaustive and literal.
163: 
164: ### 5.1 Impact Scan Enhancement (Maximum Literal Detail)
165: 
166: For every DELETION, RENAMING, or REFUNDAMENTAL change, the plan MUST include a dedicated 'Surface Area Scan' to identify
167: and remediate all global references, internal links, and cross-file dependencies.
168: 
169: ### 5.2 Anti-Summarization & No-Truncation Guardrail
170: 
171: Agents MUST NOT summarize or collapse previously established literal details (file lists, exact commands, logic
172: branches) unless they are functionally obsolete or a mistake. Maximum clarity and non-ambiguity take precedence over
173: brevity. **The 'Change History' table MUST NOT be truncated.** It must remain a complete and literal record of all plan
174: versions (v1, v2, v3, ... vN) without omission.
175: 
176: - **Files:** Explicitly list every file (absolute paths) to be created, modified, or deleted.
177: - **Exact Commands:** CLI commands must be written exactly as they will be executed, including full arguments and piped
178:     operations.
179: - **Literal Payloads:** For operations like `git commit --amend -m "..."`, the plan must include the **literal message
180:     string** within the execution step, not just a reference to it.
181: - **Verifications:** Explicitly state the exact command or visual check used to verify each step.
182: - **Guardrails**: Restate the literal logic for handling conflicts, empty commits, and safety checks in every iteration.
183: - **Pre-Plan Context Gathering**: Information gathering (reading files, `git diff`,`ls`) must happen **BEFORE**
184:     the plan is finalized. A plan based on assumptions is a failed plan.
185: 
186: ---
187: 
188: ## 8. Temporal Hygiene & Change History
189: 
190: To ensure absolute traceability and industrial reliability, all planning and verification artifacts MUST
191: incorporate temporal data.
192: 
193: - **Execution Timestamps**: Every item in `task.md` and `walkthrough.md` MUST include a completion or event
194:     timestamp in the format `[YYYY-MM-DD HH:mm]`.
195: - **Change History Table**: Every versioned implementation plan (v2+) MUST include a "Change History" table
196:     immediately following the goal statement. This table MUST track:
197: 
198:     | Timestamp | Summary of Changes | Rationale |
199:     | :--- | :--- | :--- |
200:     | `[YYYY-DD-MM HH:mm]` | Concise description of the delta. | Why the change was necessary. |
201: 
202: ---
203: 
204: ## 9. Plan Versioning & SSOT Integrity (History Mandate)
205: 
206: **Iterative Planning** is the process of updating a plan based on new findings or changes in a task's requirements.
207: This practice ensures flexibility while maintaining the core principles of transparency and user alignment.
208: 
209: - **Plan Versioning**: All plans must be explicitly versioned (e.g., `implementation_plan_v1.md`, `implementation_plan_v2.md`).
210: - **History Mandate**: New versions MUST NOT overwrite old versions. Each new version MUST include the Change History table documenting all previous revisions.
211: - **SSOT (Single Source of Truth)**: Each version MUST be self-contained, restating all valid context and guardrails. Do not refer to previous versions for "missing details."
212: - **Fresh Start Protocol**: When a "Fresh Start" version (vN) is declared, all subsequent plans (vN+1, vN+2, etc.) MUST reset the 'Change History' and 'User Questions & Answers' to only include items from the declared fresh start version onwards. This is a strict exception to the full history mandate.
213: 
214: ### 7.1 Continuity Audit Mandate (CAM)
215: 
216: Before presenting a new plan version, the agent **MUST** perform a literal line-by-line comparison against the previous
217: version. Any dropped task, alert, or requirement MUST be either restored or explicitly listed in the 'Change History'
218: with a rationale for its removal. **Summarizing integrated logic from sub-plans is a violation.**
219: 
220: ### 7.2 Sub-Plan Versioning & Integration Mandate
221: 
222: All planning artifacts, including secondary or 'sub-plans,' MUST follow the versioning mandate (v1, v2, etc.). They
223: MUST NOT be edited in place. Once a sub-plan is confirmed by the user, its content MUST be integrated into the next
224: version of the main implementation plan while maintaining its full literal detail. **All subsequent updates MUST occur
225: within the main plan.** **Integration MUST be via literal copy-paste of all confirmed mandates.** Any modification for
226: 'brevity' is prohibited. Once integrated, the sub-plan is retired and redundant versioning is forbidden.
227: 
228: - **Propose a Plan Revision:** When a change is required, the agent must immediately pause execution
229:   and present a revised plan to the user.
230: - **Provide a Rationale:** The agent must clearly explain **why** the change is necessary.
231: - **Seek Approval:** The agent must explicitly ask for user approval for the revised plan before proceeding.
232:   This final check ensures the new direction aligns with the user's updated expectations.
233: 
234: ---
235: 
236: ## 10. Task Artifact Synchronization
237: 
238: Follow the status markers and include timestamps:
239: 
240: - **Initial Creation**: Create `task.md` at the start of planning with all top-level items.
241: - **Incremental Updates**: Update `task.md` after completing each significant milestone.
242: - **Status Markers**: Use `[ ]` for pending, `[/]` for in-progress, and `[x]` for completed items `[YYYY-MM-DD HH:mm]`.
243: - **Artifact Location**: All planning artifacts (task.md, implementation plans, walkthroughs) MUST be stored in
244:     the **main repository's** `docs/` directory (e.g., `docs/implementation-plans/<date>-<topic>.md`). When
245:     `ai-agent-rules/` is a Git submodule, artifacts MUST NOT be placed inside the submodule — doing so scatters
246:     planning history into a separate repo's commit graph. The main repo's `docs/` tree is the single source of
247:     truth for all planning artifacts.
248: - **Artifact Cleanup**: If everything is OK, we can remove the artifacts. The removal needs explicit user confirmation.
249: - **Compliance Mandate**: Every generated artifact (task, implementation plan, walkthrough) MUST strictly comply
250:     with **[Markdown Generation Rules](./markdown-generation-rules.md)** and
251:     **[Markdown Generation Rules Additions](./markdown-generation-rules-additions.md)**.
252:     This includes mandatory verification using `markdownlint-cli` before finalizing any artifact.
253: 
254: ---
255: 
256: ## 11. Status Traceability in Iterative Plans
257: 
258: To ensure absolute clarity during multi-phase execution, iterative plans (v2+) MUST track the status of proposed changes.
259: 
260: - **Marking Completed Steps**: If an implementation plan is updated during execution, any proposed change that has
261:   already been successfully implemented MUST be explicitly marked as `[DONE] [YYYY-MM-DD HH:mm]` or
262:   `[COMPLETED] [YYYY-MM-DD HH:mm]` within the 'Proposed Changes' section.
263: - **Visual Distinction**: Completed steps should ideally remain in the plan (to maintain context) but be clearly
264:   demarcated to differentiate them from pending work.
265: 
266: ---
267: 
268: ## 11. User Question Integration Mandate
269: 
270: To ensure maximum transparency and technical accuracy, the agent MUST explicitly address any technical or
271: process-related questions raised by the user during the planning phase.
272: 
273: - **Mandated Documentation**: All user questions and their corresponding agent answers MUST be documented in a
274:     dedicated **"User Questions & Answers"** section at the top of the revised implementation plan.
275: - **Traceability**: This ensures that critical clarifications and course corrections are captured in the
276:     Single Source of Truth (SSOT), making them available for future reference and audits.
277: - **Clarity**: Answers should be technically precise, referring to specific rules or protocols where applicable.
278: 
279: ---
280: 
281: ## 12. State-Dependent Phase Gating
282: 
283: Plans involving future states (e.g., Git history after 3 phases of changes)
284: **MUST NOT** predict or mock the result. They must instead define a **Protocol
285: Gate**: a set of mandatory discovery commands (e.g., `git status`, `git diff`)
286: and verification steps that the agent will run *at that time* to generate a
287: fresh, accurate preview for user approval.
288: 
289: ---
290: 
291: ## 13. Sequential Objective Protocol
292: 
293: To ensure absolute precision and user control, the agent MUST adhere to a strict sequential focus:
294: 
295: - **Single Objective Focus**: When instructed to perform a specific task (e.g., "update rules"), the agent MUST focus
296:   solely on that objective.
297: - **Deferment of Follow-ups**: The agent MUST NOT plan or prepare for follow-up actions (e.g., commit execution) in
298:   the same plan unless explicitly asked.
299: - **Verification Gates**: Follow-up instructions will be provided by the user *after* the current objective is
300:   confirmed complete.
301: - **Instructional Rationale**: When told to update rules, focus on updates ONLY. Do not jump to execution or
302:   downstream tasks until explicitly directed.
303: 
304: ## 14. Single Source of Truth & Content Integrity
305: 
306: The agent MUST strictly maintain the integrity of existing documentation:
307: 
308: - **Anti-Duplication**: Please don't duplicate things. We always need SSOT.
309: - **Audit Requirement**: When adding or updating something, the agent MUST read the file deeply and carefully. Only add what is missing.
310: - **Blending Strategy**: Blend new information into the existing documentation, or enhance the existing information. We always need single source.

(End of file - total 310 lines)
</content>
```

---

## Assistant (Build · Big Pickle · 2.8s)

_Thinking:_

Alright, I need to follow the planning rules strictly. Let me also read the standardization rules and skill factory.

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/ai-agent-rules/ai-rule-standardization-rules.md"
}
```

**Output:**
```
<path>/Users/dk/lab-data/ai-suite/ai-agent-rules/ai-rule-standardization-rules.md</path>
<type>file</type>
<content>
1: ---
2: name: AI Agent Rule Standardization Rules
3: description: Craftsmanship standards for developing "Ultra-Lean Industrial" AI Agent Rules,
4:     ensuring consistent formatting,
5:     structural hierarchy, and pedagogical clarity.
6: category: Rule-Management
7: ---
8: 
9: # AI Agent Rule Standard Creation
10: 
11: This document defines the craftsmanship standards for creating new AI Agent Rules. Adhering to these protocols ensures
12: that all rules remain professional, machine-parseable, and human-readable.
13: 
14: > ## ⛔ BLOCKING — Cross-Repository Reference Test
15: >
16: > Before creating ANY rule / skill / doc that references content in a **different Git repository** (sibling folder in a multi-root workspace, separately-cloned tool repo, org-private companion repo, etc.), confirm ALL THREE:
17: >
18: > 1. Both endpoints in the same repo, OR a parent + `.gitmodules`-registered-submodule pair.
19: > 2. Survives the **Standalone-Clone Test**: clone the host repo only, into an empty directory, with no knowledge of the other repo's existence — does every link resolve and every prose reference still make sense?
20: > 3. Leaks zero org-private repo names / internal codenames / internal hostnames into a public-scope artifact.
21: >
22: > Multi-root VS Code workspaces and "the other repo is right there on my disk" are NOT valid layout proofs — they are local accidents per the Independence Axiom in [`redaction-portability-rules.md` §1.0](./redaction-portability-rules.md#10-the-independence-axiom-read-this-first). Full enforcement: §1.3 of the same rules file.
23: 
24: ***
25: 
26: ## 1. Preparation & Context Assembly (Crucial)
27: 
28: Before drafting a rule file, the agent MUST:
29: 
30: 1. **Assemble Conversation Points**: Review the entire conversation history to capture specific user preferences, edge
31: 
32:    cases discussed, and implied constraints (e.g., "plain text only", "no icons").
33: 
34: 1. **Identify Edge Cases**: Explicitly document "what not to do" based on user feedback (e.g., "Articles don't support
35: 
36:    tags").
37: 
38: 1. **Synthesize Limitations**: If a platform or tool has limitations (e.g., LinkedIn Article tags), the rule MUST
39: 
40:    address them.
41: 
42: ***
43: 
44: ## 2. File Naming & Meta-Data
45: 
46: All rule files must be stored in the `AI-Agent-Rules` directory. However, for specific workflows,
47: tasks, or capabilities, the system mandates a **Skill-First** architecture.
48: 
49: - **Skill-First Architecture**: Any new, complex work process or agent-specific workflow
50:   MUST be created as an **Agent Skill** instead of a flat rule file. Rationale: rules /
51:   instruction files are **vendor-locked** (`.cursor/rules/*.mdc`, `.github/copilot-instructions.md`,
52:   `AGENTS.md`, `CLAUDE.md`, `.windsurfrules`, etc.) -- a rule authored for one vendor is invisible
53:   to every other. The Agent Skills standard ([agentskills.io](https://agentskills.io),
54:   Anthropic-originated, multi-vendor adopted) is the open, portable alternative: a single
55:   `SKILL.md` with YAML frontmatter is consumable by every conformant runtime. Authoring a
56:   parallel rule file alongside a skill is **FORBIDDEN** -- it re-introduces vendor lock and
57:   splits the SSOT. Full rationale: see `rule-to-skill-industrialization` skill (sibling
58:   `ai-agents` repo).
59: - **Skill Directory**: Skills are housed in `.agent/skills/<skill-name>/` (legacy/single-agent) or
60:   `.agents/skills/<skill-name>/` (plural/standardized). Skill names MUST use lowercase letters, numbers, and hyphens (no underscores).
61: - **Core Skill Files**:
62:     - `SKILL.md`: The SSOT containing active instructions following the **agentskills.io protocol**
63:       (YAML frontmatter + Markdown body).
64:     - `AGENTS.md`: The companion bridge providing "passive context" and referring tools back to the `SKILL.md`.
65: - **Independence Mandate**: Every Skill MUST be self-contained. It MUST manage its own environmental verification,
66:   dependencies, and execution logic independently.
67: - **Layered Composition Mandate (Base → Composer)**: When a workflow contains a generic primitive (e.g., glob assembly,
68:   metadata extraction, path normalization) reused by multiple domain-specific tasks, it MUST be split into:
69:     1. A **base skill** that owns ONLY the generic primitive, accepts inputs via stdin / file / arguments, and
70:        produces a deterministic output. The base skill MUST be domain-agnostic.
71:     2. One or more **composer skills** that own the domain-specific discovery (e.g., parsing `.gitmodules`, walking
72:        `node_modules`) and pipe their output into the base skill via its public CLI contract.
73:   Composer scripts MUST resolve the base script through a relative path (`$(dirname "$0")/../../<base>/scripts/...`)
74:   so the pipeline works regardless of the caller's `cwd`. Inlining base logic into a composer is **FORBIDDEN** —
75:   duplication breaks the SSOT contract and silently diverges bug fixes. Each composer's `SKILL.md` MUST link to its
76:   base skill in a "Composition Rationale" section, and the base skill MUST list known composers in a "Composition by
77:   Higher-Level Skills" section so the dependency graph is bidirectionally discoverable.
78: - **Path Portability**: All links within a Skill MUST be relative and depth-correct (e.g., `../../../` for
79:   skills residing 3 levels deep) to ensure zero-dependency portability across filesystems.
80: - **Cross-Repository / Submodule Isolation (SSOT)**: When a rule or skill file lives inside a repository that is
81:   also consumed as a Git submodule of another repository (e.g., `ai-agent-rules` embedded in `ai-agents`), the
82:   asymmetric link rule defined in
83:   **[markdown-generation-rules.md §4.2.8](./markdown-generation-rules.md#428-cross-repository--submodule-isolation-links)**
84:   applies: inbound (parent → submodule) relative links are allowed; outbound (submodule → parent or sibling)
85:   relative links are FORBIDDEN and MUST be replaced by SHA-pinned hosted-VCS permalinks. Rule files MUST NOT
86:   inline this protocol — they MUST defer to §4.2.8 as SSOT.
87: 
88: - **File Naming**: Use strictly lowercase, kebab-case ending in `-rules.md` (e.g., `git-submodule-rules.md`).
89: - **Skill Naming**: Skill names in YAML frontmatter MUST use lowercase letters, numbers, and hyphens (no underscores or spaces).
90: - **Skill-Name Precision Mandate (SSOT)**: A skill's `name:` (folder name + YAML frontmatter) MUST encode every distinguishing constraint of its scope — not just the generic action. Names that omit a qualifying constraint (filetype, transport, mode, exclusion) silently overlap with future skills that own the constraint and mislead callers into composing the wrong primitive. Example: a skill that performs selective Git submodule init/update **while skipping LFS blob downloads** MUST be named `git-submodule-selective-init-no-lfs` (or `git-submodule-selective-init-lfs-skip`), NOT `git-submodule-selective-init` — the latter reads as the generic selective-init primitive and leaves no name-space for a future LFS-aware variant. When in doubt, append the differentiating qualifier; a longer precise name is always preferable to a shorter ambiguous one. Renaming after the fact requires a folder move + frontmatter update + every inbound link rewrite across the repo and submodules — much cheaper to name correctly at creation.
91: 
92: - **YAML Frontmatter**: Every file MUST start with the following metadata block:
93: 
94:     ```markdown
95:     ---
96:     name: [Short, Impactful Title]
97:     description: [One-sentence summary of the rule's scope]
98:     category: [Existing or New Category]
99:     ---
100:     ```
101: 
102: - **Frontmatter Position Mandate**: The YAML frontmatter block (`---` ... `---`) MUST be the very FIRST content
103:   in the file — line 1 column 1, with NO blank lines, BOM, HTML comments (`<!-- ... -->`), or any other content
104:   preceding it. The agentskills.io lint validator parses frontmatter strictly: any preceding character (including
105:   an HTML comment block that some legacy projects use as an alternative metadata carrier) makes the validator
106:   treat the YAML as absent, producing `Skill must provide a name` even when a syntactically valid `name:` exists
107:   below. If a project tradition uses an HTML-comment metadata block, the YAML frontmatter MUST still come first;
108:   the HTML comment MAY follow it as a secondary, lint-ignored carrier.
109: 
110: - **Namespaced Skill IDs vs Lint-Conformant Names**: Some workspaces use namespaced Skill IDs containing slashes
111:   or underscores (e.g., `dgs_ice/damos_validation_completeness_audit`) for human discoverability. Those forms are
112:   FORBIDDEN in the `name:` field because the lint validator enforces `^[a-z0-9-]+$`. Resolution:
113:   the `name:` field MUST be the hyphenated, single-segment form (e.g., `damos-validation-completeness-audit`);
114:   the namespaced form MAY appear ONLY in the body (e.g., `> **Skill ID:** \`dgs_ice/damos_validation_completeness_audit\``)
115:   where it is not lint-validated.
116: 
117: ***
118: 
119: ## 3. Structural Hierarchy
120: 
121: Rule files must follow a predictable, industrialized structure to maximize readability:
122: 
123: 1. **H1 Title**: Matches the YAML title but is more formal (e.g., `# Git Submodule Management Rules`).
124: 
125: 1. **Scope Statement**: A brief paragraph defining *why* the rule exists and who the stakeholders are.
126: 
127: 1. **Section Dividers**: Use `***` (horizontal rules) between major H2 sections.
128: 
129: 1. **Numbered Sections**: Use H2 headers with sequential numbering (e.g., `## 1. Preparation & Context Assembly`).
130: 
131: 1. **Sub-sections**: Use H3 for specific technical details (e.g., `### 1.1 Command Syntax`).
132: 
133: 1. **Related Conversations**: Use an H2 section at the bottom for traceability (e.g., `## 6. Related Conversations &
134: 
135:    Traceability`), linking to permanent session logs in the`docs/conversations/` directory.
136: 
137: ***
138: 
139: ## 4. Content Philosophy (Ultra-Lean Industrial)
140: 
141: The content must balance conciseness with technical depth:
142: 
143: - **Zero Noise**: Avoid introductory fluff, "happy to help" phrases, or redundant explanations.
144: - **Fidelity Mandate (Zero Omission)**: The agent MUST NEVER summarize or omit technical specifics, operational
145:   logic, or workflows provided by the user. "Conciseness" applies only to noise reduction, not to the factual depth
146:   of user-defined constraints.
147: - **Preservation Mandate (Additive Refinement)**: The current information in a document is considered correct and MUST
148:   NOT be removed unless explicitly requested or proven duplicate. New information MUST be blended into existing content
149:   to create an enhanced, "greater-than-before" version. If content is removed, the rationale and original content
150:   (if unique) must be preserved in a "Design Appendix" or session log.
151: - **Script SSOT Mandate (Audit Before Creation)**: The agent MUST audit existing skill directories for prior automation
152:   scripts before creating new ones. If a script already exists for a similar purpose, it MUST be refined or consolidated
153:   rather than duplicated. All scripts MUST reside in a `scripts/` subdirectory within the skill folder.
154: - **No-Embedded-Script Mandate**: Script source code MUST NOT be embedded inside `SKILL.md`, `AGENTS.md`, README, or any
155:   other markdown document — neither inline nor inside fenced code blocks. Markdown documents MUST link to the separate
156:   script file under `scripts/` using a **relative** path (e.g., `[scripts/foo.ps1](scripts/foo.ps1)`) and MAY include a
157:   short fenced **invocation example** (one-liner). Embedding full script bodies is FORBIDDEN because it (a) loses
158:   syntax highlighting, debugging, and standalone execution, (b) duplicates the SSOT, and (c) silently diverges from the
159:   executable file when one side is edited.
160: - **Self-Verification Mandate (Lint Before Present)**: After generating or editing ANY markdown artifact, the agent
161:   MUST re-read the artifact and verify it for formatting issues — stray tool-output tags (`</content>`, `<parameter ...>`),
162:   duplicated lines, broken/multi-line links, missing fenced-block closers, embedded absolute paths — and fix them
163:   BEFORE presenting the result to the user. Presenting an artifact that the agent has not re-read is FORBIDDEN.
164: - **Script Delivery Mandate (Ship It)**: Automation scripts developed during a skill session are **first-class
165:   deliverables** of the skill — NOT disposable work products. If a workflow was automated by a script during the
166:   session, that script MUST be committed inside the skill's `scripts/` directory as part of the skill's canonical
167:   form. "The script helped during the session" is sufficient justification to ship it permanently.
168: - **Script Preservation Mandate (Never Silent Drop)**: Existing scripts in a skill's `scripts/` directory MUST NOT
169:   be deleted, emptied, or replaced without an explicit user instruction to do so. During skill refactors (e.g.,
170:   extracting a base layer), the original script MUST be migrated or superseded explicitly — not silently removed.
171:   If a script is superseded by a higher-layer composer, the SKILL.md MUST document the migration rationale and the
172:   new invocation path so no operational knowledge is lost.
173: - **Script Language Mandate (SSOT-Delegated)**: When creating a new automation script, the language MUST be chosen
174:   per the four-tier framework in **[Scripting Language Selection Rules](./scripting-language-selection-rules.md)** —
175:   which is the SSOT. In summary (do NOT inline the framework here — read the SSOT):
176:     - **Tier 1 (default) — Python 3.12+** for general-purpose automation, JSON / text file mutation, REST clients,
177:       data munging, and ALL agent helper scripts UNLESS a Tier 2–4 override applies.
178:     - **Tier 2 — PowerShell 7+ (`pwsh`)** ONLY when the script body IS shell glue (≤ 80% native-binary
179:       invocation in sequence). Cross-compatible with **Windows PowerShell 5.1+** only under the §3.4 escape
180:       clause.
181:     - **Tier 3 (systems: C / Go / Rust / Zig)** ONLY after a measured Python prototype proves the bottleneck.
182:     - **Tier 4 (special: Java / C# / Node.js / PHP)** ONLY when ecosystem mandates it.
183:   Any deviation from the SSOT's recommendation requires explicit user override or a written `.NOTES`-block
184:   justification citing the §3–§5 rule that applies. The **older "PowerShell-First" default is RETIRED for new
185:   scripts** — see Scripting Language Selection Rules §intro for the supersession statement. Tier-2 (PowerShell)
186:   craftsmanship details — documentation headers (`.SYNOPSIS`, `.DESCRIPTION`, `.PARAMETER`, `.EXAMPLE`,
187:   `.NOTES`), execution priority (`pwsh-preview` → `pwsh` fallback), `Common-Utils.ps1` dot-sourcing, and the
188:   `Write-Message` empty-string safeguard — remain SSOT-owned by
189:   [Script Management Rules](./script-management-rules.md) and MUST be obeyed whenever Tier 2 is selected.
190:   Tier-1 (Python) craftsmanship details are SSOT-owned by Scripting Language Selection Rules §2.3 (byte-safe
191:   I/O, `argparse`, `ruff`, `pytest`, PEP 723 / `uv`). **Bash Extension Mandate**: When Bash is selected (a
192:   Tier-2 borderline case requiring documented justification — usually because the host lacks `pwsh`), the
193:   file MUST use the `.bash` extension — never `.sh` — per the
194:   [Bash Scripting Rules](./bash-scripting-rules.md) §Naming and the
195:   [GitHub Actions Workflow Rules](./github-actions-workflow-rules.md) standalone-script mandate.
196: - **Portable Script Path Mandate**: Any script that depends on a sibling artifact (the shared `Common-Utils.ps1`, a
197:   base-skill script under the Layered Composition Mandate, a config file, etc.) MUST resolve that artifact through a
198:   path anchored on the script's **own** location — NOT the caller's working directory. In PowerShell, use
199:   `Split-Path -Parent $MyInvocation.MyCommand.Path` and `Join-Path` with relative `..\` segments, then `Resolve-Path`
200:   for diagnostic clarity. Hard-coded absolute paths and `$PWD`-relative paths are FORBIDDEN.
201: - **Recursive Submodule Mandate**: Any documented `git submodule add`, `git submodule update --init`, or
202:   `git clone` instruction MUST use the recursive form (`--recursive` for `submodule update`, `--recurse-submodules`
203:   for `clone`). Submodules frequently embed their own submodules, and a non-recursive instruction silently leaves
204:   nested pointers uninitialized — a class of bug that surfaces only at runtime. See the
205:   [Git Submodule Addition](https://github.com/Baneeishaque/ai-agents/blob/de777420fe2931e8ef43ea7a0aa9b27f7e6bf296/.agents/skills/git-submodule-addition/SKILL.md) skill §3.3 for the canonical commands.
206: - **Pedagogical Snippets**: Use code blocks to demonstrate correct command usage or file formats.
207: 
208: - **Architectural Samples (PoC)**: Rules defining complex patterns MUST link to high-fidelity reference implementations
209: 
210:     (templates) in the `/architectures/`directory. These MUST include a`package.json` for dependency transparency.
211: 
212: - **Industrial Portability**: All implementations MUST be linked as examples so that when a rule or standard changes,
213: 
214:     the reference implementations can be updated in sync.
215: 
216: - **Industrial Folder Structure**: For feature-level or architecture rules, the rule MUST follow a standardized
217: 
218:     directory structure:
219: 
220: - `/types.ts`: Centralized Enums and Interfaces (SSOT).
221: 
222: - `/config.json`: Environmental/Externalized configuration to avoid hardcoded logic.
223: 
224: - `/engine.ts`or`/index.ts`: Main logic or entry point.
225: 
226: - `/docs/`: Implementation plans and technical goal documents.
227: 
228: - `/*.md`: Every code file MUST have an adjacent Markdown file explaining the code line-by-line with usage scenarios.
229: 
230:     These explainers MUST be pedagogical and deep, following the strict standards defined in **[Code Documentation
231:     Rules](./code-documentation-rules.md)**.
232: 
233: - **Relative Links**: Documentation and explainers MUST use **Relative Links** (not absolute paths) to ensure the
234:     rule set remains portable and functional in any local filesystem.
235: 
236: - **Environmental & Dependency Mandate**: Every `SKILL.md` MUST include a dedicated section for "Environmental Setup"
237:   or "Environment & Dependencies". This section MUST instruct the agent to autonomously verify required tools
238:   (e.g., `rclone`, `diff`) and provide installation logic for standard package managers (`brew`, `apt`, `yum`).
239: 
240: - **Artifact Linting Mandate**: All Markdown artifacts (Plans, Tasks, Walkthroughs, Skills, Rules) MUST be verified
241:   with the **`markdownlint-cli2`** binary prior to user presentation. Any violations MUST be resolved.
242:     - **Direct Execution (NO NPX)**: The agent MUST invoke the standalone binary directly (e.g.,
243:       `markdownlint-cli2 <path>` and `markdownlint-cli2 --fix <path>`). Using `npx markdownlint-cli2` is
244:       **FORBIDDEN** — it adds startup overhead, masks installation drift, and bypasses the project's pinned tool.
245:     - **SSOT**: This mandate mirrors and is governed by
246:       **[Markdown Generation Rules §5 (Validation Rules)](./markdown-generation-rules.md#5-validation-rules-markdownlint-cli2)**;
247:       that section is the single source of truth for invocation, install path, and custom-rule resolution.
248: 
249: - **Status Traceability Mandate**: Plans used for rule-building or multi-phase tasks MUST mark completed steps with
250:   `[DONE] [TIMESTAMP]` in the 'Proposed Changes' section to maintain execution context.
251: 
252: - **Multi-Project SSOT**: When providing multiple samples (e.g., CRA and Vite), the core logic MUST be extracted into
253: 
254:     a **Shared Library** folder. Samples MUST reference this shared core (e.g., via symbolic links or relative imports)
255:     to maintain a Single Source of Truth and avoid code duplication.
256: 
257: - **Core Logic Links**: Rules defining complex logic MUST link to their respective architectural SSOT providers (e.g.,
258: 
259:     [Sync Logic](./zero-backend-sync-rules.md)).
260: 
261: - **Technology Independence & Depth**: Rules MUST be technology-independent in their core principles but MUST provide
262: 
263:     maximum-detail, industry-standard examples (e.g., Nostr, WASM, RxDB) that can be reused or generated as new
264:     implementations according to the situation.
265: 
266: - **Inter-Document SSOT**: To maintain a Single Source of Truth across the rule
267:     set, documentation MUST NOT duplicate content that exists in another
268:     definitive rule file. Instead, it MUST use **Relative Section Links** to
269:     refer the agent to the authoritative source (e.g., refer to the
270:     `git-commit-message-rules.md` for formatting standards).
271: - **Selection & Trade-offs**: Rules MUST clearly explain the options, trade-offs, and alternatives available for an
272:     architectural pattern. The assistant MUST iterate with the USER to present all options (sorted by priority) and
273:     discuss the best fit for the context before concluding with a final recommendation for approval.
274: 
275: - **Context Discovery Protocol**: Rules MUST mandate that the assistant:
276:      1. **Identifies Context**: Detect build tools (Vite/CRA), frameworks (React/Vue), and identifiers (Email/PubKey).
277:      1. **Confirms Context**: Explicitly ask the user to confirm the detected environment before proceeding.
278: 
279: - **SSOT (Single Source of Truth)**: Rules MUST mandate centralized Enums for any inter-process (Worker) or
280: 
281:     inter-component communication to prevent "magic string" typos.
282: 
283: - **Decoupled Configuration**: Parameters likely to change (Relays, Endpoints, feature toggles) MUST be isolated in
284: 
285:     machine-readable config files (JSON preferred).
286: 
287: - **Storage Logic Hierarchy**: Rules MUST provide a selection logic for storage (Relational -> NoSQL -> File -> Text)
288: 
289:     based on problem context. Priority MUST be documented (e.g., 1st, 2nd, 3rd) with clear rationale for each.
290: 
291: - **Git Hygiene & Rebase (Industrial Standard)**: Rules involving Git operations MUST mandate:
292: 
293: - **Hierarchical Rebase Mapping**: Using Mermaid diagrams for branch dependencies.
294: 
295: - **Commit Action Mapping (CAM)**: Standardized KEEP/REWORD/DROP/SQUASH tables.
296: 
297: - **Literal Exhaustive Plans**: Mandating exact CLI commands and message payloads (SSOT) to prevent execution-time
298: 
299:     ambiguity.
300: 
301: - **Performance Abstraction**: Mandate backgrounding (Workers/Threads) for all heavy logic (Crypto/Network) to ensure
302: 
303:     60 FPS UI stability.
304: 
305: - **Performance Abstraction**: Mandate backgrounding (Workers/Threads) for all heavy logic (Crypto/Network) to ensure
306: 
307:     60 FPS UI stability.
308: 
309: - **Coding Standards (SSOT & Safety)**:
310: 
311: - **Comment Style**: Comments MUST be placed *before* the code line or in block format. Avoid trailing comments after
312: 
313:     semicolons.
314: 
315: - **Deep Type Safety**: Implementations MUST avoid `any` and use deep typing for all data structures (e.g.,
316: 
317:     MessageEvent data).
318: 
319: - **Runtime & Type Safety**: The agent MUST prioritize both compile-time (TS) and runtime (Schema/Validation) safety.
320: 
321: - **Defensive Programming**: All network and I/O logic MUST implement defensive programming (e.g., try-catch, JSON
322: 
323:     validation, socket state checks) to prevent silent failures.
324: 
325: - **Real Usage Samples**: Rules for frameworks (React/Vue) MUST include a real integration sample showing
326: 
327:     component/hook orchestration.
328: 
329: - **Prohibited Behaviors**: Explicitly list actions the agent is forbidden from taking (e.g., "DO NOT hardcode keys",
330: 
331:     "DO NOT block UI"). These MUST be clear, non-ambiguous, and explained as the SSOT for what to avoid.
332: 
333: - **Traceability Portability**: Permanent records MUST be stored in the **main repository's** documentation directory
334:     (`docs/`) using a structured hierarchy. When `ai-agent-rules/` is a Git submodule, records MUST NOT be placed
335:     inside the submodule — use the main repo's `docs/` tree instead (e.g., `docs/implementation-plans/`,
336:     `docs/conversations/`, `docs/walkthroughs/`).
337:     - **Protocols**: All session or conversation logs MUST follow the protocols defined in
338:       **[AI Agent Session Documentation Rules](./ai-agent-session-documentation-rules.md)**.
339:     - **Relative Pathing**: For relative paths, artifact permanence, and link references, follow the
340:       **File References** standards defined in **[Markdown Generation Rules](./markdown-generation-rules.md)**.
341: 
342: - **Redaction & Portability Mandate (SSOT)**: Every rule file, skill file (`SKILL.md`, `AGENTS.md`), session log,
343:   case study, and committed artifact authored under these standards MUST be passed through the
344:   **[Redaction & Portability Skill](https://github.com/Baneeishaque/ai-agents/blob/de777420fe2931e8ef43ea7a0aa9b27f7e6bf296/.agents/skills/redaction-portability/SKILL.md)**
345:   (rules-side mirror: **[Redaction & Portability Rules](./redaction-portability-rules.md)**)
346:   before commit. The skill is the authoritative SSOT; the rules-side mirror is the normative form referenced
347:   by all other rules. The skill is the SSOT for: (a) the three-tier sensitivity model (Tier A identity/credentials,
348:   Tier B machine/org topology, Tier C public/universal), (b) the canonical placeholder vocabulary
349:   (`<workspace-root>`, `<user-home>`, `<toolbase>`, `<author>`, `<user>`, `<corp-proxy-host>`, `<corp-domain>`,
350:   `<internal-vcs>`, `<ticket-system>`, `<customer>`, `<product-codename>`, etc.), (c) absolute-path relativization,
351:   (d) author / username / email redaction, (e) internal-domain / proxy / ticket / customer redaction, (f) filename
352:   hygiene, and (g) the verification-scan + encoding sanity-check audit steps. Rule files MUST NOT inline their
353:   own redaction vocabulary or replacement tokens — they MUST defer to the Redaction skill. Ad-hoc placeholder
354:   invention, half-redacted strings (e.g., `<corp-proxy-host>.<real-corp>.com`), and over-redaction of public
355:   open-source identifiers (`Apache Commons`, `Eclipse`, `Maven Central`) are FORBIDDEN per Redaction §10.
356: 
357: - **Repository Scope Tier Mandate (SSOT, additive to Redaction)**: Every authored file lives in exactly one
358:   publication-scope tier — **public** (e.g., the public `ai-agents` repo), **org-private** (e.g., a
359:   `<corp>_ai_agents` sibling repo), or **personal** (e.g., a sandbox branch).
360:   The tier is determined by the **enclosing Git repository**, not by the file's content or by any local
361:   workspace layout. The cardinal premise — stated as the **Independence Axiom** in
362:   [`redaction-portability-rules.md`](./redaction-portability-rules.md) §1.0 — is that the public and
363:   org-private repos are **independent Git repositories** with separate clone URLs, separate publication
364:   lifecycles, and separate existences; a developer may legitimately clone either one **standalone**.
365:   Portability in this rule set is defined as **passing the Standalone-Clone Test**: "if I clone ONLY
366:   the repo this file lives in, into a fresh empty directory, on a machine that has never heard of the
367:   other repo — does every relative link still resolve and does every prose reference still make sense?"
368:   Multi-root VS Code workspaces and sibling-folder conventions are local accidents, not portable
369:   properties, and are **inadmissible defences**. The scope tier governs what is allowed:
370:     - **Public-scope files MUST be self-contained.** They MUST NOT (a) link via relative path into an
371:     org-private or personal sibling repo (the link is broken in any standalone public clone and leaks the
372:     private repo's existence + name), (b) name a specific organization in prose (use `<corp>` or generic
373:     "your organization" phrasing instead), or (c) rely on a multi-root VS Code workspace to make a
374:     cross-repo link "resolve" — it resolves only for the original author. The correct way to delegate to
375:     an org-private capability is generic prose: *"consult your organization's internal skill library, if
376:     one exists."*
377:     - **Org-private-scope files MAY reference public-scope files — by name, not by relative
378:     path.** Per the Independence Axiom, a relative link
379:     `../../../../<public-repo>/...` only resolves inside one specific multi-root workspace
380:     layout and is broken for any developer who clones the org-private repo standalone.
381:     Reference public-scope skills and rules by canonical inline-code name only (e.g.,
382:     ``the general `system-wide-tool-management` skill in the public `ai-agents` repo``).
383:     Org-private files MAY use literal Tier B values universally true within that
384:     organization (`<toolbase>`, the corporate proxy host, the internal VCS URL). Use the
385:     canonical `<placeholder>` once beside the first literal occurrence as a teaching aid
386:     for future public-scope ports.
387:     - **Unifying principle:** no relative-path link may escape its enclosing repository,
388:     regardless of direction.
389: 
390:   Before staging any cross-repo reference, the agent MUST run the **Pre-Commit Checklist** in
391:   [`redaction-portability-rules.md`](./redaction-portability-rules.md) §1.4, and SHOULD consult the
392:   **Worked Example** in §1.5 (a public skill ↔ org-private skill pair) for the canonical correct +
393:   inadmissible patterns. See
394:   [`redaction-portability-rules.md`](./redaction-portability-rules.md) §1 for the full matrix and
395:   detection heuristic.
396: 
397: - **Mandatory Protocols**: Use clear, imperative language (e.g., "The agent MUST...", "The agent is BLOCKED from...").
398: 
399: - **Deep Command Explanation Mandate**: Any shell command or CLI snippet provided in a Rule or Skill MUST include
400:   a deep, flag-by-flag pedagogical breakdown. This ensures the agent (and user) understands the exact logic and
401:   rationale behind every argument, preventing "magic command" execution.
402: 
403: ***
404: 
405: ## 5. Verification & Commit
406: 
407: Before finalizing a new rule:
408: 
409: 1. **Cross-Reference**: Check for existing rules to avoid duplication.
410: 
411: 1. **Lint Check**: Ensure all content complies with **[Markdown Generation Rules](./markdown-generation-rules.md)** and
412:     **[Markdown Generation Rules Additions](./markdown-generation-rules-additions.md)**.
413: 
414: 1. **Sync Trigger**: Remind the user to trigger the `agent-rules.md` update workflow.
415: 
416: 1. **Commit Message**: Use Conventional Commits (e.g., `feat: establish standard creation rules for AI agents`).
417: 
418: ### 6. Auto-Generated Indices (CI/CD Managed)
419: 
420: The `agent-rules.md`and`README.md` files are strictly derivative artifacts managed by CI/CD.
421: 
422: - **NEVER** edit or commit these files directly.
423: 
424: - **SOURCE OF TRUTH**: All structural changes (diagrams, layout) MUST be made in the `templates/*.template` files.
425: 
426: - **AUTOMATION**: Updates are automatically triggered by pushes to rule files or templates via the `update-rules.yml`
427: 
428:     workflow.
429: 
430: - **PROHIBITED ACTION**: Manually replacing placeholders (e.g., `<!-- RULES_INDEX -->`) in templates or output files.

(End of file - total 430 lines)
</content>
```

---

## Assistant (Build · Big Pickle · 3.3s)

_Thinking:_

Now let me also read the skill factory skill and the markdown-generation skill to understand the full protocol.

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/skill-factory/SKILL.md"
}
```

**Output:**
```
<path>/Users/dk/lab-data/ai-suite/.agents/skills/skill-factory/SKILL.md</path>
<type>file</type>
<content>
1: ---
2: name: skill-factory
3: description: Industrial protocol for automated creation of "Skill-First" AI Agent skills with high fidelity.
4: category: Meta-Automation
5: ---
6: 
7: # Skill Factory Skill (v1)
8: 
9: This skill automates the creation of new AI Agent Skills following the **agentskills.io** protocol and the
10: **Industrial Fidelity** mandates.
11: 
12: ***
13: 
14: ## 1. Preparation: The Fidelity Scan
15: 
16: The Agent MUST ensure that no operational detail is lost during the skill creation process.
17: 
18: 1. **Source Discovery**: Identify all user-provided operational logic, dependencies, and constraints from the
19:    conversation history.
20: 2. **Anti-Loss Validation**: Create a list of "Must-Include" technical specifics. **Summarization is BLOCKED** for
21:    these items.
22: 3. **Preservation Check**: Ensure existing content is preserved and blended. **Destructive overwriting is FORBIDDEN**.
23: 4. **Script Audit**: Search the target skill directory and workspace for existing automation scripts. **Consolidation
24:    is MANDATORY**—Utility duplication is a failure of the Industrial standard.
25: 
26: - **Greater-Than-Before**: The skill MUST be more detailed than the prompt that initiated it, including
27:   extrapolated context where necessary.
28: 
29: ***
30: 
31: ## 2. Skill Generation Protocol
32: 
33: ### 2.0 Layering Decision (Base vs. Composer)
34: 
35: Before creating any new skill, the Agent MUST decide whether the requested capability is:
36: 
37: 1. **Atomic** — a single, indivisible workflow with no reusable primitive. Proceed to §2.1 as one skill.
38: 2. **Layerable** — contains a generic primitive (glob assembly, metadata extraction, path normalization, brace
39:    expansion, list sort+dedupe, etc.) that other domain-specific tasks could reuse. Split into:
40:     - A **base skill** owning ONLY the primitive, with a stdin / file / argument CLI contract and deterministic output.
41:       The base skill MUST be domain-agnostic.
42:     - One or more **composer skills** owning the domain-specific discovery, piping their output into the base skill.
43: 
44: The layering test: *"Could a different domain ever need the same primitive?"* If yes, layering is **MANDATORY** —
45: inlining the primitive into a single skill is a violation of the SSOT contract.
46: 
47: Reference exemplar: [vscode-search-exclude-glob](../vscode-search-exclude-glob/SKILL.md) (base) +
48: [vscode-search-exclude-submodules](../vscode-search-exclude-submodules/SKILL.md) (composer).
49: 
50: ### 2.1 Directory Structure
51: 
52: - Create the target folder in `.agents/skills/<skill-name>/` (hyphens required for names).
53: - Initialize `SKILL.md` (active SSOT) and `AGENTS.md` (companion bridge).
54: - For **composer skills**: the composer's script MUST resolve the base script via a relative path anchored to its own
55:   location (`SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"` then `BASE="$SCRIPT_DIR/../../<base-skill>/scripts/..."`),
56:   so invocation works regardless of the caller's `cwd`. The composer MUST verify the base script exists and exit
57:   non-zero with a clear error if it is missing.
58: - **`scripts/` SANITY CHECK**: Only create `scripts/` when the skill ships executable scripts. A skill with no
59:   scripts (pure documentation + conventions) MUST NOT have a `scripts/` directory.
60: 
61: ### 2.2 SKILL.md Composition
62: 
63: The `SKILL.md` MUST include:
64: 
65: 1. **YAML Frontmatter**: name, description, category. Skill names MUST use lowercase letters, numbers, and hyphens.
66:    The frontmatter block (`---` ... `---`) MUST be the FIRST content in the file (line 1 column 1, no BOM, no
67:    preceding blank lines, **no preceding HTML comments**); any preceding character makes the agentskills.io lint
68:    validator emit `Skill must provide a name` even when the YAML is otherwise valid. When a workspace tradition
69:    uses a namespaced Skill ID containing slashes or underscores (e.g., `dgs_ice/foo_bar`), that form is FORBIDDEN
70:    in `name:` (validator enforces `^[a-z0-9-]+$`) — put the hyphenated single-segment form in `name:` and keep
71:    the namespaced form in the body under `> **Skill ID:** ...` where it is not lint-validated.
72:    The `name:` MUST also satisfy the **Skill-Name Precision Mandate** ([`ai-rule-standardization-rules.md` §Skill Naming](../../../ai-agent-rules/ai-rule-standardization-rules.md)) — every distinguishing constraint of the skill's scope (filetype, transport, mode, exclusion) MUST appear in the name; generic names that omit a qualifying constraint silently collide with future variants and mislead callers. A longer precise name is always preferable to a shorter ambiguous one.
73: 2. **Environment & Dependencies**: Mandated verification logic (`which`, version checks).
74: 3. **Operational Logic**: The EXACT steps provided by the user (**Zero Omission**).
75: 4. **SSOT Compliance**: The skill MUST NOT duplicate technical standards
76:    defined in the central rule repository. Instead, it MUST link to the
77:    authoritative rule files using relative links (e.g., to the atomic
78:    commit rules or commit message rules).
79: 5. **Traceability Section**: Links to permanent conversation logs. All such logs MUST be sanitised through the
80:    **[Redaction & Portability Skill](../redaction-portability/SKILL.md)** before being committed — see §3 of this
81:    document for the mandatory audit checklist.
82: 
83: **No-Parallel-Rule-File Mandate**: When the Factory produces a new skill, it MUST NOT also produce a parallel
84: rule file (`ai-agent-rules/<topic>-rules.md`) covering the same procedure. Rule / instruction files are
85: vendor-locked (`.cursor/rules/*.mdc`, `.github/copilot-instructions.md`, `AGENTS.md`, `CLAUDE.md`,
86: `.windsurfrules`, etc.); the `agentskills.io` standard is the open, multi-vendor-portable alternative.
87: Authoring a sibling rule re-introduces the vendor lock the skill was created to escape and splits the SSOT.
88: An `AGENTS.md` Permanent Operating Reminder (one-line bullet pointing at the skill) is permitted and
89: encouraged; a full parallel rule file is FORBIDDEN. Authoritative rationale:
90: [`ai-rule-standardization-rules.md` §2 Skill-First Architecture](../../../ai-agent-rules/ai-rule-standardization-rules.md)
91: and [`rule-to-skill-industrialization` §0](../rule-to-skill-industrialization/SKILL.md).
92: 
93: ### 2.2.1 Script Authoring Mandates
94: 
95: **No-Embedded-Script Mandate**: Script source code MUST NOT be embedded inside `SKILL.md`, `AGENTS.md`, or any other
96: markdown document. Markdown MUST link to the separate file under `scripts/` via a **relative** path
97: (e.g., `[scripts/foo.ps1](scripts/foo.ps1)`) and MAY include a short fenced invocation example (one-liner).
98: Embedding the full script body is FORBIDDEN — it breaks syntax highlighting, debugging, standalone execution, and
99: the SSOT contract. See [AI Rule Standardization Rules — No-Embedded-Script Mandate](../../../ai-agent-rules/ai-rule-standardization-rules.md).
100: 
101: **Tier Decomposition Mandate**: Before drafting the `SKILL.md` body, walk every step of the user-provided procedure
102: and classify each as Tier A (deterministic) or Tier C (judgement) per
103: [`script-over-instruction-decomposition`](../script-over-instruction-decomposition/SKILL.md). Every Tier-A step MUST
104: be extracted into a script under `scripts/` and invoked from prose via a one-liner. Prose MUST NOT carry multi-line
105: bash recipes, Python heredocs, regex-laden `sed`/`awk` chains, or step-by-step file-mutation walkthroughs — those
106: belong in a script. A skill whose prose still embeds deterministic mechanics has skipped the decomposition step and
107: fails the Factory's industrial standard.
108: 
109: When the skill ships executable scripts under `scripts/`, every script MUST obey the **Universal Script Mandates** in §2.2.1.1 (all scripts, all tiers) and, when Tier 2 (PowerShell) is selected, additionally obey the **Tier-2 (PowerShell) Craftsmanship Mandates** in §2.2.1.2.
110: 
111: #### 2.2.1.1 Universal Script Mandates
112: 
113: Apply to every script regardless of language tier.
114: 
115: 1. **Language Selection (SSOT-Delegated)**: The script's language MUST be chosen per the four-tier framework in
116:    **[Scripting Language Selection Rules](../../../ai-agent-rules/scripting-language-selection-rules.md)** — that
117:    document is the SSOT. Do NOT inline the framework here. In one line: **Tier 1 (Python 3.12+) is the default for
118:    new scripts**; Tier 2 (PowerShell 7+ / `pwsh`) is reserved for scripts whose body IS shell glue; Tier 3 (C / Go /
119:    Rust / Zig) is reserved for measured CPU-bound bottlenecks; Tier 4 (Java / C# / Node / PHP) is reserved for
120:    ecosystem-mandated cases. The **older "PowerShell-First" default is RETIRED** for new scripts (see Scripting
121:    Language Selection Rules §intro). Selection MUST be made BEFORE drafting the script and MUST be documented in
122:    the script's header (`.NOTES` block for `.ps1`, module docstring for `.py`) with a one-line citation of the
123:    §3–§5 tier rule that applies. **Tier-1 (Python) craftsmanship details** (byte-safe I/O, `argparse`, `ruff`,
124:    `pytest`, PEP 723 / `uv`, mise-equivalence) are SSOT-owned by Scripting Language Selection Rules §2.3.
125:    **Tier-2 (PowerShell) craftsmanship details** (comment-based help, `pwsh-preview` → `pwsh` fallback,
126:    `Common-Utils.ps1` dot-source, `Write-Message` guard, strict-mode hygiene) — §2.2.1.2 below — remain
127:    mandatory whenever Tier 2 is selected; they DO NOT apply to Tier-1 (Python) scripts.
128: 2. **Bash Extension Mandate**: When Bash is selected (a Tier-2 borderline case requiring documented justification —
129:    usually because the host lacks `pwsh`), the file MUST use the `.bash` extension — never `.sh` — per
130:    [Bash Scripting Rules §Naming](../../../ai-agent-rules/bash-scripting-rules.md) and the
131:    [GitHub Actions Workflow Rules](../../../ai-agent-rules/github-actions-workflow-rules.md) standalone-script
132:    mandate.
133: 3. **Tier-Violation Remediation**: When a Factory audit on an EXISTING skill discovers a script that picked the
134:    wrong language tier per
135:    [`scripting-language-selection-rules`](../../../ai-agent-rules/scripting-language-selection-rules.md)
136:    (typically a `.bash` / `.sh` wrapping a `python3 - <<PY` heredoc, or a shell script doing JSON / regex work),
137:    DELEGATE the port to [`script-language-tier-port`](../script-language-tier-port/SKILL.md) as its own atomic
138:    refactor commit — do NOT inline the port mechanics here.
139: 4. **Plan-Time Tier Declaration**: Any planning artifact (per
140:    [`ai-agent-planning-rules`](../../../ai-agent-rules/ai-agent-planning-rules.md))
141:    that proposes NEW scripts MUST surface, in the plan body, a per-script
142:    table listing (a) the Tier-1 (Python) evaluation, (b) the chosen tier,
143:    (c) the `scripting-language-selection-rules` §3–§5 citation, and (d) —
144:    if the chosen tier is NOT Tier-1 — the explicit deviation reason. This
145:    surfaces wrong-tier picks at plan-review time, where they cost a plan
146:    revision, instead of post-implementation, where they cost a
147:    [`script-language-tier-port`](../script-language-tier-port/SKILL.md)
148:    refactor commit.
149: 5. **Recursive Submodule Bootstrap**: Any documentation that instructs the user to clone or initialize the
150:    `powershell-scripts` submodule (or any other submodule) MUST use the recursive form
151:    (`git submodule update --init --recursive <path>` or `git clone --recurse-submodules <url>`).
152: 6. **Template Extraction Mandate** (companion to No-Embedded-Script Mandate): When a script writes
153:    file content (YAML, markdown, .gitignore, config stanzas, etc.), that content MUST be kept in a
154:    separate `.template` file under `scripts/` and read at runtime via a path anchored on the script's
155:    own location (`Path(__file__).parent / "<name>.template"` in Python;
156:    `Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "<name>.template"` in PowerShell).
157:    Embedding file-content strings in scripts is FORBIDDEN because it: (a) breaks syntax highlighting
158:    and linting of the template format, (b) duplicates SSOT — the truth lives both in the string
159:    literal and the generated file, (c) prevents editors from applying format-specific tooling,
160:    (d) makes content changes require touching the script file.  For automated remediation of existing
161:    scripts that violate this mandate, use
162:    [`script-template-extraction`](../script-template-extraction/SKILL.md).
163: 7. **Documentation Invocation Convention** — Skill docs MUST use simplified
164:    invocation forms (`python3`, `node`, `ruby`, `php`, `pwsh`). Never embed
165:    fragile path-resolution commands like
166:    `PY=~/.local/share/mise/installs/python/$(ls … | sort … | tail -1)/bin/python`
167:    in documentation code blocks. The companion runtime resolution logic is
168:    documented in
169:    [`mise-tool-management §3.3`](../mise-tool-management/SKILL.md#33-runtime-tool-resolution).
170:    Use `scripts/verify-doc-invocations.py` to audit for violations.
171: 
172: #### 2.2.1.2 Tier-2 (PowerShell) Craftsmanship Mandates
173: 
174: Apply **only when the script's selected tier is Tier 2 (PowerShell)**. Tier-1 (Python) scripts are exempt — Python craftsmanship is SSOT-owned by [Scripting Language Selection Rules §2.3](../../../ai-agent-rules/scripting-language-selection-rules.md).
175: 
176: 1. **Documentation Headers**: Comment-based help with `.SYNOPSIS`, `.DESCRIPTION`, `.PARAMETER`, `.EXAMPLE`, `.NOTES`
177:    sections — see the [Script Management Rules](../../../ai-agent-rules/script-management-rules.md).
178: 2. **Execution**: Documented invocations MUST use `pwsh-preview` (preferred) with `pwsh` as fallback.
179: 3. **Common-Utils Dot-Source**: Scripts MUST dot-source `Common-Utils.ps1` from the
180:    [`powershell-scripts`](../../../ai-agent-rules/powershell-scripts/) submodule of `ai-agent-rules` for shared
181:    helpers (`Write-Message`, etc.) unless an explicit exemption is justified in the script's `.NOTES` block.
182: 4. **Portable Anchored Paths**: All sibling-artifact lookups (the dot-source above, base-skill scripts under the
183:    Layered Composition Mandate, config files) MUST be resolved through paths anchored on the script's own location
184:    via `Split-Path -Parent $MyInvocation.MyCommand.Path` + `Join-Path` — NEVER `$PWD`-relative or hard-coded.
185: 5. **Write-Message Safeguard**: Every `Write-Message` call MUST be guarded with
186:    `if (-not [string]::IsNullOrWhiteSpace($Message)) { ... }`.
187: 6. **Strict Mode Hygiene**: Scripts SHOULD declare `Set-StrictMode -Version Latest` and `$ErrorActionPreference = 'Stop'`.
188:    When reading `$LASTEXITCODE` after invoking another script, guard with
189:    `Test-Path Variable:LASTEXITCODE` to avoid strict-mode failures on first invocation.
190: 
191: ### 2.2.2 Script Delivery & Preservation Mandates
192: 
193: Scripts are **first-class deliverables** of a skill — not disposable session artifacts:
194: 
195: 1. **Ship It (Delivery Mandate)**: Any automation script developed during a skill session MUST be committed inside
196:    the skill's `scripts/` directory as part of the skill's canonical form. "The script helped during the session"
197:    is sufficient and mandatory justification to ship it permanently. Leaving scripts uncommitted is a failure of
198:    the Industrial standard.
199: 2. **Never Silent Drop (Preservation Mandate)**: Existing scripts in a skill's `scripts/` directory MUST NOT be
200:    deleted, emptied, or replaced without an explicit user instruction. During skill refactors (e.g., extracting a
201:    base layer), the original script MUST be migrated or superseded explicitly — not silently removed.
202: 3. **Supersession Documentation**: If a script is superseded by a higher-layer composer (3-layer stack refactor),
203:    the SKILL.md MUST document: (a) which script replaces it, (b) the new invocation path, and (c) the rationale —
204:    so no operational knowledge is lost even when the old file is intentionally removed.
205: 4. **Commit Inclusion**: The skill's scripts MUST appear in the same commit as the skill's `SKILL.md` — never
206:    deferred to a follow-up commit. An uncommitted script that exists only in the working tree is NOT part of the
207:    skill.
208: 
209: ### 2.3 AGENTS.md (Companion Bridge) Composition
210: 
211: Every skill folder MUST contain an `AGENTS.md` file alongside `SKILL.md`. The file is a **passive bridge** that exposes the skill to *non-skill-aware* agent runtimes — clients that auto-load `AGENTS.md` by filename convention (e.g., Codex CLI, some Cursor profiles, some Continue.dev configurations) but do not parse `agentskills.io` YAML frontmatter or the `.agents/skills/<name>/SKILL.md` directory contract. The bridge ensures those agents discover the skill exists and know to read `SKILL.md` for the operational details, instead of silently missing the skill.
212: 
213: #### 2.3.1 Disambiguation — Per-Skill Bridge vs. Root Registry
214: 
215: Two distinct files share the filename `AGENTS.md`:
216: 
217: | File | Path | Role | Maintained by |
218: |---|---|---|---|
219: | **Root registry** | `<repo-root>/AGENTS.md` | Index of all skills + Permanent Operating Reminders | §2.4 Registration (root-table row inserted via `agents-md-stage-row.py`) |
220: | **Per-skill bridge** | `.agents/skills/<skill>/AGENTS.md` | Companion bridge for one skill | THIS subsection (§2.3) |
221: 
222: They are NOT the same artifact and MUST NOT be conflated. The per-skill bridge does not list other skills; the root registry does not duplicate per-skill operational content. A failure to distinguish them has been observed where an author put per-skill bridge content into the root registry (or vice versa).
223: 
224: #### 2.3.2 Required Sections (Template)
225: 
226: The per-skill `AGENTS.md` MUST contain the following sections in this order:
227: 
228: 1. **`# <Skill Display Name> — Companion Bridge`** (level-1 heading; the literal suffix `— Companion Bridge` lets reviewers grep for bridges across the tree).
229: 2. **`## Purpose`** (1–3 sentences). State that this file is the bridge for non-skill-aware runtimes and that the operational SSOT lives in [`SKILL.md`](SKILL.md).
230: 3. **`## When This Skill Applies`** (1 short paragraph or 3–5 bullets). Plain-language trigger conditions, paraphrased from `SKILL.md`'s `## Description` and `## When to Apply` sections — NOT copy-pasted.
231: 4. **`## Operational Procedure`** (1 sentence + the link). A single sentence directing the agent to `SKILL.md` for the procedure: *"Read [`SKILL.md`](SKILL.md) for the full operational procedure, including all mandates, scripts, and verification steps. Do NOT execute any step without first loading `SKILL.md` — this bridge is intentionally non-actionable."*
232: 5. **`## Cross-References`** (optional bullet list). Relative links to closely-related skills and rule files. Use §5.6 (Cross-Reference Link Discipline) — proper relative markdown links, not bare code spans.
233: 
234: #### 2.3.3 Frontmatter Prohibition
235: 
236: The per-skill `AGENTS.md` MUST NOT carry YAML frontmatter (no leading triple-dash block). Frontmatter is the discriminator that distinguishes `SKILL.md` (skill-aware runtime metadata) from the bridge file. Adding frontmatter to `AGENTS.md` causes some runtimes to mis-classify it as a second skill registration and emit duplicate-name lint errors.
237: 
238: #### 2.3.4 Forbidden Content
239: 
240: The per-skill `AGENTS.md` MUST NOT contain:
241: 
242: 1. **Embedded scripts** (covered by §2.2.1 No-Embedded-Script Mandate — applies to ALL markdown in the skill, including the bridge).
243: 2. **Duplicated rule content** from `SKILL.md` or from `ai-agent-rules/*.md`. The bridge paraphrases trigger conditions; operational mandates are not restated.
244: 3. **Step-by-step procedures**. Any reader looking for the procedure MUST be sent to `SKILL.md`. The bridge is intentionally non-actionable so divergence between the two files is impossible.
245: 4. **Long verbatim quotes** from `SKILL.md`. If the bridge starts copying paragraphs from `SKILL.md`, the bridge has overstepped its role and will drift on the next `SKILL.md` edit.
246: 
247: #### 2.3.5 Size Guidance
248: 
249: A correctly-scoped per-skill `AGENTS.md` is typically **40–120 lines** (Purpose + When + Operational pointer + Cross-References). Sub-40 lines suggests missing sections (e.g., no When-This-Applies); over-120 lines suggests content duplication that should be deleted and replaced with a pointer to `SKILL.md`. The size is a smell test, not a hard cap.
250: 
251: #### 2.3.6 Audience Clarification
252: 
253: The bridge serves **two audiences**:
254: 
255: 1. **Non-skill-aware agent runtimes** that auto-load `AGENTS.md` by filename convention. The bridge ensures these runtimes discover the skill and know to load `SKILL.md` for operational details.
256: 2. **Human reviewers** browsing the skill folder who haven't yet opened `SKILL.md`. The bridge gives them a one-minute orientation before they commit to reading the full SSOT.
257: 
258: It is NOT for skill-aware runtimes — those load `SKILL.md` directly via the `agentskills.io` discovery contract and ignore the bridge.
259: 
260: #### 2.3.7 Audit Step
261: 
262: A bridge audit row is added to §3 Post-Drafting Checklist verifying that `<skill>/AGENTS.md` exists, has no frontmatter, contains the five required sections from §2.3.2, and is within the 40–120 line size guidance from §2.3.5. A skill with no bridge file is INCOMPLETE and MUST NOT be marked done.
263: 
264: ### 2.4 Registration
265: 
266: - Update the root `AGENTS.md` skills table to register the new skill with its absolute path and description.
267:     Use the shared registration helper instead of hand-editing the table:
268: 
269:     ```bash
270:     python3 .agents/skills/git-atomic-commit-construction/scripts/agents-md-stage-row.py \
271:         --mode worktree \
272:         --row "| Skill Name | [\`.agents/skills/<skill-name>/SKILL.md\`](.agents/skills/<skill-name>/SKILL.md) | One-line description |"
273:     ```
274: 
275:     `--mode worktree` reads the working-tree `AGENTS.md`, inserts the row at the alphabetically correct position,
276:     and writes the result back to the working tree for normal `git add` review. The default `--mode staged`
277:     is reserved for the Atomic Commit Construction §2f Interleaving Mandate when `AGENTS.md` already carries
278:     unrelated pending hunks.
279: - **Alphabetical Order Mandate**: The root `AGENTS.md` skills table MUST remain sorted alphabetically (case-insensitive)
280:   by the **Skill** column. New entries MUST be inserted at the correct sorted position \u2014 NEVER appended to the end.
281:   After insertion, the Agent MUST visually verify that the row above and below the new entry maintain the sort order.
282: - For layered pairs: register **both** the base and the composer in the same change at their respective sorted
283:   positions, with the composer's row explicitly noting *"Composer \u2014 feeds X into the base Y skill"* so the dependency
284:   is visible at the index level.
285: 
286: ***
287: 
288: ## 3. Post-Drafting Checklist
289: 
290: Every skill generated via the Factory MUST automatically undergo the final verification:
291: 
292: - **Portability, Redaction & PII Audit (MANDATORY — SSOT delegation)**: Every file produced by the Factory MUST be
293:   put through the full **[Redaction & Portability Skill](../redaction-portability/SKILL.md)** protocol before the
294:   skill is considered complete. The Factory MUST NOT inline its own redaction rules — the redaction skill is the SSOT.
295:   Specifically, the Factory MUST execute, in order:
296:     1. **Tier Classification** (Redaction §1): Walk every string in every generated artifact (`SKILL.md`,
297:        `AGENTS.md`, every `docs/conversations/*.md`, every `docs/cases/*.md`, every script header) and classify
298:        each candidate string as Tier A (identity/credentials), Tier B (machine/org topology), or Tier C
299:        (public/universal).
300:     2. **Canonical Placeholder Substitution** (Redaction §2): Replace every Tier-A and Tier-B match with the
301:        canonical placeholder vocabulary (`<workspace-root>`, `<user-home>`, `<toolbase>`, `<author>`, `<user>`,
302:        `<corp-proxy-host>`, `<corp-domain>`, `<internal-vcs>`, `<ticket-system>`, `<customer>`,
303:        `<product-codename>`, etc.). Ad-hoc placeholder invention is FORBIDDEN — extend Redaction §2 first.
304:     3. **Path Handling** (Redaction §3): All absolute Windows / POSIX paths are converted to workspace-relative,
305:        user-home-relative (`~`), or placeholder form. Angle-bracket placeholders in `[text](target)` link targets
306:        are converted to inline-code symbolic references per Redaction §3.3 to avoid broken navigation.
307:     4. **Identity Handling** (Redaction §4): Author trailers, reviewer names, OS usernames, and email addresses are
308:        redacted. Commit SHAs are preserved.
309:     5. **Network & Org Handling** (Redaction §5): Internal proxy hosts, internal domains, internal repository URLs,
310:        ticket IDs, customer names, and product codenames are redacted; the `nonProxyHosts` and analogous wildcards
311:        use `<corp-domain>` / `<corp-cloud-domain>` placeholders.
312:     6. **File Naming Hygiene** (Redaction §6): Conversation and case-study filenames MUST encode topics, never
313:        organization or identity strings.
314:     7. **Verification Scan** (Redaction §8 Step 4): Re-run the regex inventory scans for absolute paths, emails,
315:        IPv4, and internal hostnames. The terminal output MUST be empty (or contain only Tier-C universally-true
316:        matches) before the audit passes.
317:     8. **Encoding Sanity Check** (Redaction §8 Step 5): Scan for mojibake markers (`Ã`, `â€`, `Â`, `ï¿½`) that
318:        redaction edits frequently introduce, and fix them before considering the audit complete.
319:     9. **Directory Depth Audit**: Verify the correct directory depth (e.g., `../../../` from a 3-level deep skill).
320:    10. **Repository Independence Audit** (Redaction §1.0 + §1.4): When the new skill mentions ANY other repository
321:        (whether by Markdown link or by prose), run the Pre-Commit Checklist from Redaction §1.4 and apply the
322:        Standalone-Clone Test from §1.0 — "if I clone ONLY the enclosing repo into a fresh empty directory, does
323:        every relative link resolve and does every prose reference still make sense?" Reject any relative-path link
324:        whose target escapes the enclosing repo (count `../` segments) regardless of how it resolves on the author's
325:        disk. Multi-root VS Code layouts are inadmissible defences. The Worked Example in Redaction §1.5
326:        (a public-skill ↔ org-private-skill pair) is the reference pattern.
327: - **Prohibited Behavior**: The Factory MUST NOT publish a skill that has not passed the Redaction & Portability audit.
328:   Half-redacted strings (e.g., `<corp-proxy-host>.<real-corp>.com`) and over-redacted public identifiers
329:   (e.g., redacting `Apache Commons`, `Eclipse`, `Maven Central`) are both audit failures per Redaction §10.
330: - **Contextual Hosting**: Documentation (logs, artifacts) MUST reside in the component's `docs/` folder.
331: - **Fidelity Check**: Verify that no technical details from the source conversation were summarized or lost.
332: - **Markdown Audit**: Run the **[Markdown Generation](../markdown-generation/SKILL.md)**
333:   protocol to ensure 100% lint compliance. The agent MUST re-read
334:   every generated/edited markdown file and fix any stray tool-output tags (`</content>`, `<parameter ...>`), duplicated
335:   lines, broken or multi-line links, unclosed fences, and embedded absolute paths BEFORE presenting the artifact.
336:   Linting MUST be performed by invoking the **`markdownlint-cli2`** binary directly
337:   (e.g., `markdownlint-cli2 --fix <path>` then `markdownlint-cli2 <path>`); using `npx markdownlint-cli2` is
338:   **FORBIDDEN** per
339:   **[Markdown Generation Rules §5](../../../ai-agent-rules/markdown-generation-rules.md#5-validation-rules-markdownlint-cli2)**.
340:   Recommended fix-script execution order is documented in
341:   **[Markdown Generation §3.1](../markdown-generation/SKILL.md#31-execution-order)**.
342: - **Bridge Audit**: Confirm `<skill-dir>/AGENTS.md` exists, carries NO YAML frontmatter (no leading `---` block), contains the five required sections from §2.3.2 (`# <Skill> — Companion Bridge` / `## Purpose` / `## When This Skill Applies` / `## Operational Procedure` / `## Cross-References`), and is within the 40–120 line size guidance from §2.3.5. A skill with no bridge file is INCOMPLETE.
343: - **Registration Audit**: Confirm the new skill row was inserted into the root `AGENTS.md` skills table at the correct
344:   alphabetical (case-insensitive) position by the **Skill** column, NOT appended to the end. Spot-check the rows
345:   immediately above and below to verify the sort order holds.
346: - **Organization Audit**: Confirm the new skill's placement obeys the domain taxonomy in
347:   [`skill-library-domain-grouping` §1](../general/skill-library-domain-grouping/SKILL.md#1-domain-taxonomy).
348:   The parent folder MUST have ≤10 items; if the addition would exceed the threshold, the agent
349:   MUST propose a sub-grouping before adding.
350: - **Invocation Audit**: Run `scripts/verify-doc-invocations.py` to confirm no fragile invocation
351:   patterns are present in any `**/SKILL.md` file (mandate #7). The script MUST exit 0 before
352:   the skill is considered complete.
353: - **Composition Audit** (when layering applies):
354:     1. **No Inlining**: Confirm the composer script does NOT reimplement the base primitive — it MUST shell out to
355:        the base script.
356:     2. **End-to-End Pipeline Validation**: Execute the composer against a real input and confirm the output matches
357:        the base skill's expected format (deterministic, sorted, deduped, correctly framed).
358:     3. **Bidirectional Discoverability**: Confirm the base skill lists the new composer in its
359:        `## Composition by Higher-Level Skills` table, and the composer links back to the base in its
360:        `## Composition Rationale` and `## Related Skills` sections.
361:     4. **Cross-Reference Integrity**: Run the
362:        [`skill-cross-reference-audit`](../general/skill-cross-reference-audit/SKILL.md)
363:        base script to detect: (a) skill names duplicated in both Composition and
364:        Related Skills sections, (b) missing AGENTS.md, (c) missing YAML frontmatter,
365:        (d) empty Related Skills sections, (e) missing Related Skills in skills that
366:        have Composition sections. Resolve all reported issues before declaring the
367:        skill complete.
368:        ```bash
369:        python3 .agents/skills/general/skill-cross-reference-audit/scripts/audit-cross-refs.py
370:        ```
371: - **Script Authoring Audit** (when scripts are shipped):
372:     1. **Cross-Version Smoke Test**: Execute the script with `pwsh-preview` (and, where feasible, `pwsh`) on a real
373:        input and confirm exit code 0 on the success path and exit code 1 with a `Write-Message`-rendered diagnostic on
374:        the failure path.
375:     2. **Pipeline Cleanliness**: Capture the script's stdout into a variable (`$out = & ./script.ps1 ...`) and confirm
376:        it contains exactly the expected payload — no diagnostic noise leaking onto the success stream.
377:     3. **Common-Utils Dependency**: Confirm the documented `git submodule update --init --recursive` snippet for the
378:        `powershell-scripts` submodule appears in the skill's Environment & Dependencies section.
379:     4. **Path Portability**: Run the script from at least two different working directories (e.g., the repo root and
380:        `/tmp`) to prove the `$MyInvocation`-anchored relative paths still resolve.
381: 
382: ## 4. Bash-Authoring Hygiene During Skill Creation
383: 
384: Skill authoring itself frequently mutates many files via bash. The same patterns that freeze the VS Code renderer during normal agent work also freeze it during skill-authoring sessions. Before any bash invocation a Factory author MUST satisfy:
385: 
386: 1. **One command per call.** No `;` / `&&` chaining unless required by a pipe.
387: 2. **One path argument per call.** Iterate at the agent level, not in shell.
388: 3. **No bash `grep -r` / `find` for searches.** Use the in-process `grep` / `glob` tools with `head_limit`.
389: 4. **Heredoc body ≤ ~50 lines.** Split into multiple `cat >> file <<EOF` appends; for surgical insertions use Python `pathlib.Path.read_text() / write_text()` instead of `sed -i`.
390: 5. **Bound every call's output.** Redirect unknowns to `scratch/` per [`repo-scratch-output-capture`](../repo-scratch-output-capture/SKILL.md).
391: 
392: The ten recurring freeze patterns, the eleven-item per-call self-audit checklist, and the post-freeze recovery protocol are owned by [`ide-renderer-freeze-prevention`](../ide-renderer-freeze-prevention/SKILL.md) — Factory authors enforce its §5 checklist on every bash call made during skill creation but do not re-document the patterns locally (SSOT).
393: 
394: ## 5. Skill-Doc Editing Discipline
395: 
396: Eight independent invariants govern in-place edits to existing skill docs (`SKILL.md`, `AGENTS.md`) so that one author's mutation does not leave broken references, duplicated sections, misplaced subsections, off-topic bloat, broken cross-reference links, too-narrow top-level headings, formatting drift, or numbering gaps for the next author to clean up.
397: 
398: ### 5.1 Post-Rename Cross-Reference Sweep
399: 
400: Whenever a skill-authoring task renames anything that other artifacts may reference:
401: 
402: - A heading anchor or section number (e.g., `§3c` → `§3b`)
403: - A skill folder or skill identifier (e.g., `git-submodule-selective-init` → `git-submodule-selective-init-no-lfs`)
404: - A file path, symbol name, or canonical placeholder
405: 
406: …the renamer MUST, **before reporting the task done**, sweep the entire affected tree for the OLD form and update every inbound hit in the same operation. The mechanics are Tier-A (per [`script-over-instruction-decomposition`](../script-over-instruction-decomposition/SKILL.md)) and are owned by the dedicated script — INVOKE the script, do NOT re-derive the sweep ad-hoc:
407: 
408: ```bash
409: # 1. Dry-run preview (exit 1 if hits found, 0 if clean)
410: .agents/skills/skill-factory/scripts/post-rename-sweep.py --old "<OLD>" --new "<NEW>"
411: 
412: # 2. Review the per-file hit listing; if all hits are legitimate inbound refs:
413: .agents/skills/skill-factory/scripts/post-rename-sweep.py --old "<OLD>" --new "<NEW>" --apply
414: 
415: # 3. Verify zero residual hits (exit 0 == clean):
416: .agents/skills/skill-factory/scripts/post-rename-sweep.py --old "<OLD>" --new "<NEW>"
417: ```
418: 
419: The script auto-discovers repo root, applies safe default scopes (skill `.md`, skill `scripts/`, `ai-agent-rules/`, root `AGENTS.md`, `memories/repo/`), uses LITERAL string replacement only (no regex — per §5.1 a rename is always a literal-form change), and skips `.git/`, `node_modules/`, `__pycache__/`, `.venv/` unconditionally. Custom scope can be passed via repeatable `--scope <GLOB>`. The script is the SSOT for the sweep mechanics — do NOT fall back to bash `grep -r` (violates [`ide-renderer-freeze-prevention`](../ide-renderer-freeze-prevention/SKILL.md) §3 Pattern 2) or to inline Python re-implementation (violates [`script-over-instruction-decomposition`](../script-over-instruction-decomposition/SKILL.md) Consumer Discipline).
420: 
421: A rename is a refactor; every inbound reference is part of the refactor's scope. Stopping at the renamed file is an incomplete refactor and the user has to catch it.
422: 
423: **Insertion-induced renumbering counts.** "Rename" here includes any change that shifts the section's identifier, even when the heading TEXT is untouched. Specifically:
424: 
425: 1. **Insertion before**: adding a new `## N.` before an existing section bumps that section (and all successors) to `## (N+1).`. The displaced section has been renumbered — every inbound `§N` reference (whether self-referential within the same skill or cross-skill) becomes dangling and MUST be updated in the same edit.
426: 2. **Deletion before**: removing a `## N.` shifts successors down by one. Same sweep obligation.
427: 3. **Promotion / demotion**: moving `### N.M` up to `## (N+1).` or vice versa changes the citation form (`§N.M` ↔ `§(N+1)`). Same sweep obligation.
428: 
429: These no-text-change renumbers are the most-missed class because the diff looks small ("just inserted a new section, nothing else changed"). The cross-reference impact is identical to a text-rename. Apply §5.4 verification (`grep -n '^## \|^### ' <file>`) AND the inbound-sweep above on every numbered insertion / deletion / promotion.
430: 
431: **Self-referential references count too.** A `§N` citation inside the same skill that points to a now-renumbered sibling section is just as dangling as a cross-skill `§N`. Include the same file in the sweep target list — do not assume "the heading's just two screens above, I'd have noticed."
432: 
433: **Historical example**: in [`git-submodule-dead-upstream-audit`](../git-submodule-dead-upstream-audit/SKILL.md), an inbound reference *"The `curl` invocations in §2 follow…"* in §1 became dangling because the curl-introducing section is actually §3 (Upstream Reachability Probe) and §4 (Fork / Mirror Discovery) — not §2 (Pre-Audit Discovery, which uses only `git`). Whether the slip originated from an early-draft renumber or a typo, §5.4's verification step (numbering audit) combined with this §5.1 inbound-sweep would have caught it before the doc shipped.
434: 
435: ### 5.2 Cross-Reference Append Discipline
436: 
437: When adding an inbound back-link section (e.g., `## Composition by Higher-Level Skills`) to a target skill:
438: 
439: 1. First check whether the target already has that section (`grep -n "<section heading>" target/SKILL.md`).
440: 2. If it does → append a **row to the existing table / bullet to the existing list**.
441: 3. If it does NOT → create the section.
442: 
443: Never create a second heading of the same name. The skill-factory's "one section per topic" invariant must be preserved.
444: 
445: (Persisted as `permanent_discipline.post-rename-cross-reference-sweep`.)
446: 
447: ### 5.2.1 Composition-Table Membership & Description Discipline
448: 
449: The `## Composition by Higher-Level Skills` table on a base skill is NOT a catalog of "skills that mention this one" — it is the **inbound composition graph**. Three failure modes have been observed when authors append rows carelessly:
450: 
451: 1. **Unrelated skills listed**: a skill that neither composes nor consumes the base is added because its topic sounded adjacent. PROHIBITED — the table loses signal and downstream readers compose the wrong primitive.
452: 2. **Merely related skills listed**: a sibling skill that shares a topic but does NOT invoke / depend on / extend the base is added. PROHIBITED in this table — such skills belong in the base's `## Related Skills` section instead. The Composition table is reserved for true composers (callers that pipe through the base's public contract) and consumers (skills that hard-depend on the base's output shape).
453: 3. **Generic / non-contextual descriptions**: a true composer is listed but its description is a paraphrase of the composer's own one-liner ("does X with Y"). PROHIBITED — the description MUST state HOW the composer uses the base: which base section/script it invokes, what it pipes in, what it gets out, and (if applicable) at which stage of its own workflow.
454: 
455: **Acceptance criteria** for any new row in `## Composition by Higher-Level Skills`:
456: 
457: - [ ] The candidate skill ACTUALLY invokes the base skill (via script shell-out, explicit `§N` reference, or hard dependency on the base's output contract). If it merely shares a topic → move to `## Related Skills` instead.
458: - [ ] The description names the **specific composition mechanism** — which section/script of the base is invoked, with what input, producing what output, at what stage of the composer's flow.
459: - [ ] The description is NOT a copy of the composer's own description; it is written from the BASE skill's perspective ("Composer X feeds inputs A into §N of this skill; consumes output B at its Step M").
460: 
461: **Verification**: before declaring a Composition table edit done, open each newly-added row's composer and confirm a literal reference to the base skill exists (script include, `§N` citation, or relative link to the base SKILL.md). If no such reference exists, the row is misplaced — move it to `## Related Skills` or delete it.
462: 
463: (Persisted as `permanent_discipline.composition-table-membership-and-description-discipline`.)
464: 
465: ### 5.2.2 Composition Rationale Section Discipline
466: 
467: The `## Composition Rationale` section sits in the skill's front-matter zone (before `## 1.`) and answers a question the reader has on first arrival: **"why does this skill exist as a separate atomic unit, and how does it fit into the larger graph of skills?"** It is NOT a duplicate of `## Description` (which states what the skill does) and NOT a duplicate of `## Related Skills` (a flat list of adjacents). It is the **justification for atomicity + the upstream/downstream wiring statement**.
468: 
469: #### Purpose by skill role
470: 
471: - **Base skill** (owns a generic primitive consumed by others): Composition Rationale explains why the primitive was extracted as its own skill (typically: "multiple composers reuse it; inlining would split the SSOT") and names the known composer(s) that depend on its public contract. It MUST link to each composer.
472: - **Composer skill** (calls one or more base skills via their public CLI / section contracts): Composition Rationale names every base skill it composes, the EXACT mechanism of composition (which script / section / CLI flag), and the domain-specific value the composer adds on top of the bases. It MUST link to each base.
473: - **Standalone skill** (neither base nor composer): a one-paragraph statement of why the procedure is atomic and self-contained. Short. No table.
474: 
475: #### How a composer's Composition Rationale differs from a base's
476: 
477: | Aspect | Base skill | Composer skill |
478: |---|---|---|
479: | Direction of wiring | Downstream (lists who depends on me) | Upstream (lists what I depend on) |
480: | Mandatory link targets | Every known composer | Every base skill composed |
481: | Typical mechanism phrasing | "Composers shell out to `scripts/<base>.sh` and consume its stdout JSON contract" | "Pipes `<input-discovery-output>` into `<base>/scripts/<x>` via `$(dirname "$0")/../../<base>/scripts/<x>`" |
482: | What it justifies | Why the primitive was extracted (SSOT) | Why the composer adds value beyond the base (domain knowledge, multi-base orchestration) |
483: | Failure mode if missing | Composers re-implement the primitive (inline-duplication) | Base is invoked redundantly or the wrong base is chosen |
484: 
485: #### Quick decision rule (which section does a cross-skill link belong in?)
486: 
487: ```
488: Is the OTHER skill INVOKED by this skill (script call / CLI / hard contract dep)?
489: ├── YES → ## Composition Rationale (and the base lists me back under ## Composition by Higher-Level Skills)
490: └── NO  → Is it topic-adjacent (same domain area but no invocation)?
491:           ├── YES → ## Related Skills (one-line bullet, no mechanism prose)
492:           └── NO  → Do NOT link it. Topic vagueness is not a reason to cross-link.
493: ```
494: 
495: #### Example: a composer's Composition Rationale (maximum-detail template)
496: 
497: For a hypothetical `git-submodule-selective-init-no-lfs` skill that composes two bases — `git-submodule-selective-init` (the generic selective-init primitive) and `git-lfs-skip-smudge-env` (sets `GIT_LFS_SKIP_SMUDGE=1` in a scoped subshell) — the Composition Rationale would read:
498: 
499: ```markdown
500: ## Composition Rationale
501: 
502: This skill is a composer: it does NOT re-implement selective submodule init logic, nor does it re-implement the LFS skip-smudge environment manipulation. It orchestrates two atomic base skills:
503: 
504: 1. **[`git-lfs-skip-smudge-env`](../git-lfs-skip-smudge-env/SKILL.md)** — invoked FIRST. The composer sources its `scripts/enter-skip-smudge.sh` via `source "$(dirname "$0")/../../git-lfs-skip-smudge-env/scripts/enter-skip-smudge.sh"` to export `GIT_LFS_SKIP_SMUDGE=1` for the current shell. This ensures any subsequent `git submodule update` invocation will fetch submodule trees without triggering LFS smudge filters (saves bandwidth + disk on repos with multi-GB LFS objects the caller does not need).
505: 2. **[`git-submodule-selective-init`](../git-submodule-selective-init/SKILL.md)** — invoked SECOND. The composer shells out to its `scripts/init-selected-submodules.sh <path-glob>...` passing the user-supplied submodule path globs. The base script's stdout (one initialized submodule path per line) is consumed by this composer to confirm the selection matched and to surface progress.
506: 
507: The composer's domain-specific value-add over either base alone: a single CLI surface that guarantees the LFS-skip environment is active BEFORE the submodule update runs (ordering is critical — setting the env after the update is a no-op). Inlining either base would duplicate logic that other composers (`git-submodule-selective-init-shallow`, `git-lfs-mirror-skip-blobs`) also consume.
508: 
509: Bidirectional discoverability: both bases list this composer in their respective `## Composition by Higher-Level Skills` tables.
510: ```
511: 
512: And the corresponding base-side entry (on `git-submodule-selective-init/SKILL.md`):
513: 
514: ```markdown
515: ## Composition by Higher-Level Skills
516: 
517: | Composer | Composition Mechanism |
518: |---|---|
519: | [`git-submodule-selective-init-no-lfs`](../git-submodule-selective-init-no-lfs/SKILL.md) | Calls `scripts/init-selected-submodules.sh <glob>...` AFTER sourcing `git-lfs-skip-smudge-env`'s env-setter; consumes the one-path-per-line stdout to surface progress to the user. |
520: | [`git-submodule-selective-init-shallow`](../git-submodule-selective-init-shallow/SKILL.md) | Calls `scripts/init-selected-submodules.sh <glob>...` with `GIT_SUBMODULE_DEPTH=1` pre-exported; relies on the base's exit code only (does not parse stdout). |
521: ```
522: 
523: Note how each composer-table row names the EXACT script invoked, the input contract, the output contract consumed, and any ordering / env constraints. Generic descriptions like "uses selective init for the no-LFS variant" are FORBIDDEN per §5.2.1.
524: 
525: (Persisted as `permanent_discipline.composition-rationale-section-discipline`.)
526: 
527: ### 5.3 Subsection Insertion Position
528: 
529: When adding a new numbered subsection (e.g., `### 4.7`, `#### 3b`) to an existing skill, insert it at the **correct logical position by section number** — between the existing predecessor and successor — **never append at file end**.
530: 
531: The default `cat >> file <<EOF` heredoc pattern is fast but appends at end-of-file; for mid-file insertions use Python `pathlib.Path.read_text() / write_text()` with a string-anchor replacement instead:
532: 
533: ```python
534: import pathlib
535: p = pathlib.Path("path/to/SKILL.md")
536: s = p.read_text(encoding="utf-8")
537: target = "\n***\n\n## 5. Next Section"   # the successor
538: new_block = "\n### 4.7 New Subsection\n\nBody…\n\n***\n"
539: p.write_text(s.replace(target, new_block + "\n## 5. Next Section", 1), encoding="utf-8")
540: ```
541: 
542: **Verification step** (mandatory before declaring the insert done):
543: 
544: ```bash
545: grep -n '^##\|^### [0-9]' path/to/SKILL.md
546: ```
547: 
548: Read the output and confirm that within each parent section the numbering is **monotone** (4.1, 4.2, …, 4.7, then ## 5.). A subsection that appears after the parent's terminator (`## 5.`, `## 6.`) is misplaced — relocate it.
549: 
550: (Persisted as `permanent_discipline.insert-subsection-at-logical-position`.)
551: 
552: ### 5.4 Numbered-Section Scheme Consistency
553: 
554: When the target document uses a numbered section scheme (`## 1.`, `## 2.`, `## 3.`, …), any new section MUST follow the scheme:
555: 
556: - Number it as the next sequential top-level (`## N.`) — or
557: - Demote it to a sub-section of an existing parent (`### N.M`).
558: 
559: NEVER append an unnumbered `## Heading` into a numbered document. Equally: if inserting **between** existing numbered sections, **renumber all successors** in the same edit.
560: 
561: **Front-matter exemption.** Sections that appear BEFORE `## 1.` (typically `## Description`, `## Composition Rationale`, `## Related Skills`, `## Source Rules`) are exempt — those follow the repo's pre-Step-1 convention.
562: 
563: **Verification step** (mandatory before declaring the insert done):
564: 
565: ```bash
566: grep -n '^##\|^### ' path/to/SKILL.md
567: ```
568: 
569: Read the output and confirm:
570: 
571: 1. Numbering is **monotone** across all `## N.` headings.
572: 2. Every `### N.M` lives between its parent `## N.` and the next `## (N+1).`.
573: 3. No unnumbered `## Heading` appears after `## 1.`.
574: 
575: (Persisted as `permanent_discipline.numbered-section-scheme-consistency`.)
576: 
577: **Indent-continuity check (pointer).** Every skill-doc edit that inserts
578: or rewrites list items, code-fence contents, or table rows MUST verify
579: that the new content's continuation-line indent exactly matches unmodified
580: sibling lines. Delegate detection and repair to the
581: [`list-indent-consistency`](../general/list-indent-consistency/SKILL.md)
582: base skill. Accept only after re-verifying that surrounding and added lines
583: agree.
584: 
585: ### 5.5 Section-Home Discipline (Don't Bloat Tangential Skills)
586: 
587: Before adding a section of more than ~10 lines to an existing skill doc, the author MUST first answer: **"Is this section's topic within this skill's declared scope (Description + Composition Rationale)?"**
588: 
589: Three failure modes have been observed when authors append sections carelessly:
590: 
591: 1. **Topic-mismatch bloat**: a large body of guidance is dropped into a skill whose scope it does not belong to, merely because the *task* that surfaced the guidance happened to touch that skill (e.g., adding a multi-paragraph "Bash-Authoring Hygiene" section to [`repo-scratch-output-capture`](../repo-scratch-output-capture/SKILL.md) just because the author was *using* scratch redirection while authoring bash). PROHIBITED — readers of the host skill encounter off-topic content, and the true SSOT skill never gets the addition.
592: 2. **Duplicate-SSOT drift**: the guidance is added to skill A even though skill B already owns it. PROHIBITED — future edits diverge between the two copies.
593: 3. **No-SSOT-yet sprawl**: the guidance is genuinely new and has no owning skill, so the author parks it in the nearest neighbour. PROHIBITED — create a new dedicated skill (via the Factory's normal flow) or extend the most-related EXISTING owner; do not park.
594: 
595: **Acceptance criteria** before adding a section larger than ~10 lines to an existing skill:
596: 
597: - [ ] The section's topic is explicitly named in the host skill's `## Description` OR `## Composition Rationale`. If not → STOP, find/create the correct owner.
598: - [ ] No other skill already owns the topic (verify with the `grep` tool on a 2–3 word topic phrase across `.agents/skills/**/SKILL.md`). If another skill owns it → add there; in the host, leave at most a one-line delegation pointer with relative link to the SSOT.
599: - [ ] If genuinely new and no owner exists → invoke the Factory's new-skill flow (`## 1. When to Apply`) rather than parking.
600: 
601: **Thin-pointer template** for the host skill when delegating: a single sentence of the form *"For <topic>, see [<owner-skill>](../<owner-skill>/SKILL.md) — that skill is the SSOT."* A one-line pointer is the maximum permitted footprint of a tangential topic on a host skill.
602: 
603: **Historical example**: an earlier authoring session embedded a multi-paragraph Bash-Authoring Hygiene section into [`repo-scratch-output-capture`](../repo-scratch-output-capture/SKILL.md) because the author was using scratch redirection while writing the bash. The correct home was this skill's §4 (which delegates the freeze catalogue to [`ide-renderer-freeze-prevention`](../ide-renderer-freeze-prevention/SKILL.md) as the SSOT). The section was later relocated and only the SSOT pointer remained in scratch.
604: 
605: (Persisted as `permanent_discipline.section-home-discipline`.)
606: 
607: ### 5.6 Cross-Reference Link Discipline
608: 
609: Every **first-mention** (within a given section / subsection) of any of the following inside a skill doc MUST be rendered as a proper relative markdown link, not as a bare backtick code span:
610: 

(Output capped at 50 KB. Showing lines 1-610. Use offset=611 to continue.)
</content>

<system-reminder>
Instructions from: /Users/dk/lab-data/ai-suite/.agents/skills/skill-factory/AGENTS.md
# AGENTS.md (Skill Factory)

Refer to [SKILL.md](./SKILL.md) for the active operational protocol for generating "Skill-First" AI Agent capabilities with absolute data fidelity and zero-leak portability.

## Mandates

- **Fidelity Scan**: Mandatory identification of all user specifics before drafting.
- **Zero Omission**: Technical workflows and dependencies MUST NOT be summarized or removed.
- **Redaction Integration**: Automatically apply the **Redaction & Portability** skill to all factory-generated output.
- **Invocation Convention** (mandate #7): Skill docs MUST use simplified invocation forms; run `scripts/verify-doc-invocations.py` as a post-creation audit step.

</system-reminder>
```

---

## Assistant (Build · Big Pickle · 3.4s)

_Thinking:_

Let me also read the markdown-generation skill which should have the lint/auto-fix workflow documented.

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/SKILL.md"
}
```

**Output:**
```
<path>/Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/SKILL.md</path>
<type>file</type>
<content>
1: ---
2: name: markdown-generation
3: description: Industrial protocol for generating lint-compliant, high-fidelity markdown documentation.
4: category: Documentation-Standards
5: ---
6: 
7: # Markdown Generation Skill (v1)
8: 
9: This skill provides a standardized protocol for generating Markdown that complies with the **Industrial standard**
10: (120-character line limit) and passes `markdownlint-cli2` (markdown linting CLI tool) audits.
11: 
12: ***
13: 
14: ## 1. Core Syntax Standards
15: 
16: Every generated file MUST adhere to these absolute constraints:
17: 
18: ### 1.1 Line Length (MD013)
19: 
20: - **Limit**: 120 characters per line.
21: - **Exception**: Long URLs and file paths that cannot be broken. Use **Reference-style links** at the bottom of the
22:   document to resolve length violations for URLs.
23: - **Wrapping**: Proactively wrap descriptions and YAML blocks to stay under the limit.
24: 
25: ### 1.2 Layout & Tables (MD060)
26: 
27: - **Table Alignment**: Use mathematically perfect aligned pipes (`|`).
28: - **Cell Spacing**: One mandatory space padding on both sides of every pipe (` | content | `).
29: - **Blank Lines**: Headers, lists, and code blocks MUST be surrounded by blank lines.
30: 
31: ### 1.3 Frontmatter
32: 
33: - **Rules/Skills**: Use the triple-dash block (`---`) as defined in [ai-rule-standardization-rules.md](../../../ai-agent-rules/ai-rule-standardization-rules.md).
34: - **General Docs**: Use the HTML comment block (`<!-- title: ... -->`) for indexing.
35: 
36: ### 1.4 Cross-Reference Links & Anchors
37: 
38: The `markdownlint-cli2` tool validates anchors via **MD051 - Link fragments should be valid**.
39: 
40: - **Anchor Format**: For header `### Step 1 — Deep Change Analysis`, the anchor is `#step-1-deep-change-analysis`
41: - **Generation Rule**: Convert header to lowercase, replace spaces and `—` (em dash) with dashes (`-`)
42: - **Verification**: Run `markdownlint-cli2` - it will catch broken anchor errors (MD051)
43: - **Best Practice**: Always use anchors when linking to headers within skill/rule files
44: 
45: ### 1.5 Path Verification
46: 
47: #### Default (CLI-Only)
48: 
49: - **Anchor**: Enforced by MD051 (built-in)
50: - **File Path**: NOT enforced - run manual verification:
51:     - `ls -la <path>` to confirm target exists
52:     - From `skills/<skill>/`: `ls ../<sibling-skill>/SKILL.md`
53:     - From `skills/<skill>/`: `ls ../../../ai-agent-rules/<rule>.md`
54: 
55: #### With Node.js Custom Rules (If Available)
56: 
57: Install and configure:
58: 
59: ```bash
60: npm install --save-dev markdownlint-rule-relative-links
61: ```
62: 
63: Add to `.markdownlint-cli2.jsonc` (NOT `.markdownlint.jsonc`):
64: 
65: ```jsonc
66: {
67:     "customRules": ["markdownlint-rule-relative-links"],
68:     "config": {
69:         "relative-links": { "root_path": "." }
70:     }
71: }
72: ```
73: 
74: Then both anchors AND file paths validated automatically.
75: 
76: ***
77: 
78: ## 2. Verification Workflow
79: 
80: Before finalizing ANY markdown file, the agent MUST:
81: 
82: 1. **Config Initialization**: If the project lacks a `.markdownlint.jsonc` file, the agent
83:    MUST initialize it using rules from the reference config (`../../../.markdownlint.jsonc`
84:    relative to this skill file), incorporating the `MD013` 120-character line length exception.
85: 2. **Sync Check**: Ensure `.vscode/settings.json` contains `"markdownlint.configFile": ".markdownlint.jsonc"` to
86:    synchronize the IDE extension with the project's Industrial standard.
87: 3. **Auto-Fix**: Run `markdownlint-cli2 --fix <file_path>` from the project root.
88:    Use paths **relative** to the project root — absolute paths can cause the
89:    tool to silently find 0 files (`Linting: 0 file(s)`) and do nothing.
90: 4. **Dry-Run Companion Scripts**: Before applying any companion script from §3,
91:    MUST run with `--check` first to preview changes, review the proposed diffs,
92:    then re-run without `--check` to apply. Dry-run before apply is MANDATORY
93:    for every companion script.
94: 5. **Audit Check**: Run `markdownlint-cli2 <file_path>`.
95: 6. **Manual Correction**: Fix any remaining semantic or structural errors (e.g., heading increments).
96: 7. **Fidelity Verification**: Ensure the "Fidelity Mandate" (no loss of user technical specifics) is upheld during
97:    formatting.
98: 
99: ***
100: 
101: ## 3. Companion Scripts
102: 
103: This skill ships seven helper scripts under
104: [`scripts/`](scripts/) for one-shot lint fixes:
105: 
106: - [`fix-table-separators.py`](scripts/fix-table-separators.py) — scans for
107:   compact table separators (`|---|---|`) and rewrites them with proper spacing
108:   (`| --- | --- |`) to satisfy MD060. Use `--check` for dry-run.
109: - [`wrap-long-lines.py`](scripts/wrap-long-lines.py) — wraps prose lines
110:   exceeding the configured `--max` width (default 120) while preserving code
111:   blocks, tables, YAML frontmatter, and list structure. Use `--check` for
112:   dry-run.
113: - [`fix-fenced-code-language.py`](scripts/fix-fenced-code-language.py) — adds
114:   a default language tag (default `text`) to bare opening fenced code blocks
115:   to satisfy MD040. Properly undoes `markdownlint-cli2 --fix` damage that
116:   attaches `text` to closing fences. Use `--default <lang>` to override the
117:   language (default: `text`). Use `--check` for dry-run.
118: - [`fix-emphasis-as-heading.py`](scripts/fix-emphasis-as-heading.py) — strips
119:   emphasis markers (`*...*`, `_..._`) from lines that are standalone
120:   emphasis-as-heading paragraphs to satisfy MD036. Use `--check` for dry-run.
121: - [`fix-list-style.py`](scripts/fix-list-style.py) — converts asterisk
122:   unordered list markers (`*`) to dash style (`-`) to satisfy MD004.
123:   Use `--check` for dry-run.
124: - [`fix-heading-spacing.py`](scripts/fix-heading-spacing.py) — inserts a blank
125:   line before headings that lack one to satisfy MD022. Skips YAML frontmatter
126:   and code blocks. Use `--check` for dry-run.
127: - [`fix-container-fence.py`](scripts/fix-container-fence.py) — detects fenced
128:   code blocks whose outer fence uses 4+ backtick markers with content containing
129:   inner ``` fences (markdown-syntax examples). Adds a `text` language tag to
130:   the opening fence to satisfy MD040 without breaking the inner fences. Use
131:   `--check` for dry-run.
132: 
133: All seven scripts operate in-place on a list of file arguments.
134: 
135: ```bash
136: python3 scripts/fix-table-separators.py --check path/to/file.md
137: python3 scripts/fix-table-separators.py path/to/file.md
138: 
139: python3 scripts/wrap-long-lines.py --max 120 --check path/to/file.md
140: python3 scripts/wrap-long-lines.py --max 120 path/to/file.md
141: 
142: python3 scripts/fix-fenced-code-language.py --check path/to/file.md
143: python3 scripts/fix-fenced-code-language.py path/to/file.md
144: 
145: python3 scripts/fix-emphasis-as-heading.py --check path/to/file.md
146: python3 scripts/fix-emphasis-as-heading.py path/to/file.md
147: 
148: python3 scripts/fix-list-style.py --check path/to/file.md
149: python3 scripts/fix-list-style.py path/to/file.md
150: 
151: python3 scripts/fix-heading-spacing.py --check path/to/file.md
152: python3 scripts/fix-heading-spacing.py path/to/file.md
153: 
154: python3 scripts/fix-container-fence.py --check path/to/file.md
155: python3 scripts/fix-container-fence.py path/to/file.md
156: ```
157: 
158: These are convenience tools for the `## 2. Verification Workflow` step 3
159: (auto-fix) — they target patterns `markdownlint-cli2 --fix` does not resolve.
160: 
161: ### 3.1 Execution Order
162: 
163: When running multiple fix scripts, the following order is **REQUIRED** to avoid
164: re-introducing lint errors:
165: 
166: 1. `fix-table-separators.py`
167: 2. `fix-fenced-code-language.py` (MUST run BEFORE `wrap-long-lines.py` — fence
168:    lines may exceed the width limit and wrapping a fence line before its
169:    language tag has been added produces a broken fence)
170: 3. `fix-container-fence.py`
171: 4. `wrap-long-lines.py`
172: 5. `fix-emphasis-as-heading.py`
173: 6. `fix-list-style.py`
174: 7. `fix-heading-spacing.py`
175: 
176: > **Indent drift after editing / lint-fix.** After running the §3.1 pipeline,
177: > verify that continuation-line indent in edited regions matches the original
178: > file's siblings. `markdownlint-cli2 --fix` and companion scripts can leave
179: > whitespace drift on adjacent lines. Delegate detection and repair to the
180: > [`list-indent-consistency`](../general/list-indent-consistency/SKILL.md)
181: > base skill, then re-run the `markdownlint-cli2` audit before staging.
182: 
183: ### 3.2 Known `markdownlint-cli2 --fix` Caveats
184: 
185: **`markdownlint-cli2 --fix` corrupts bare closing fences.** When it encounters
186: a fenced code block without a language tag (\`\`\`), the built-in `MD040` fix
187: attaches a `text` language tag to **every** \`\`\` line — including the
188: closing fence — producing a broken construct:
189: 
190: ````text
191: ```text
192: code here
193: ```text
194: ````
195: 
196: **Resolution:** Do NOT use `markdownlint-cli2 --fix` for MD040. Instead, run
197: `fix-fenced-code-language.py` which correctly tracks open/close fence state
198: and strips any language tag from closing fences. If `--fix` has already been
199: applied, `fix-fenced-code-language.py` will repair the damage.
200: 
201: ***
202: 
203: ## 4. Related Rules
204: 
205: - **SSOT**: [markdown-generation-rules.md](../../../ai-agent-rules/markdown-generation-rules.md)
206: - **Formatting Protocol**: [ai-rule-standardization-rules.md](../../../ai-agent-rules/ai-rule-standardization-rules.md)
207: 
208: ***
209: 
210: ## 5. CI Integration
211: 
212: ### 5.1 Pipeline Script Execution Order
213: 
214: When automating lint fixing in a CI pipeline or pre-commit hook, run the
215: companion scripts in the order defined in §3.1. The pipeline MUST NOT use
216: `markdownlint-cli2 --fix` for MD040 (use `fix-fenced-code-language.py`
217: instead) per the caveat in §3.2.
218: 
219: Recommended one-shot invocation from the repo root:
220: 
221: ```bash
222: python3 .agents/skills/markdown-generation/scripts/fix-table-separators.py \
223:   --check file.md
224: python3 .agents/skills/markdown-generation/scripts/fix-fenced-code-language.py \
225:   --check file.md
226: python3 .agents/skills/markdown-generation/scripts/wrap-long-lines.py \
227:   --max 120 --check file.md
228: python3 .agents/skills/markdown-generation/scripts/fix-emphasis-as-heading.py \
229:   --check file.md
230: python3 .agents/skills/markdown-generation/scripts/fix-list-style.py \
231:   --check file.md
232: python3 .agents/skills/markdown-generation/scripts/fix-heading-spacing.py \
233:   --check file.md
234: ```
235: 
236: Drop `--check` to apply changes in-place.
237: 
238: ### 5.2 YAML Frontmatter Validation
239: 
240: YAML frontmatter `description` values that contain colons followed by
241: YAML-reserved tokens (e.g., `resetMocks: true`) cause downstream parsers
242: (VS Code preview, `markdownlint-cli2`) to misinterpret the colon as a new
243: YAML key opening.
244: 
245: **Rule:** If a `description` value contains any colon (`:`) that is not
246: trailing whitespace or a URL scheme (`https://`), wrap the entire value in
247: double quotes (`"..."`). Bare unquoted descriptions containing internal
248: colons are FORBIDDEN.
249: 
250: **Correct:**
251: 
252: ```yaml
253: ---
254: description: "Repository-specific composer that uses the generic ai-suite skill for debugging missing toolbar features"
255: ---
256: ```
257: 
258: **Incorrect:**
259: 
260: ```yaml
261: ---
262: description: Repository-specific composer that uses the generic ai-suite skill for debugging missing toolbar features
263: ---
264: ```
265: 
266: The difference is invisible in most Markdown renderers but causes silent
267: YAML parse failures in editor preview panes and schema validators.
268: 
269: ### 5.3 Lint Gate
270: 
271: Every skill authored via the Skill Factory (`skill-factory`) MUST pass the
272: full Verification Workflow (§2) including the companion-script pipeline
273: (§3.1) before it is considered complete. The factory's Post-Drafting
274: Checklist (§3) is the SSOT for the gating criteria; this section is the
275: SSOT for the technical execution order.

(End of file - total 275 lines)
</content>
```

---

## Assistant (Build · Big Pickle · 175.2s)

_Thinking:_

Now I have a clear picture. The current workflow documented in the markdown-generation skill is:

1. Run `markdownlint-cli2 --fix <file_path>` (auto-fix)
2. Run companion scripts in order (§3.1):
   - fix-table-separators.py
   - fix-fenced-code-language.py
   - fix-container-fence.py
   - wrap-long-lines.py
   - fix-emphasis-as-heading.py
   - fix-list-style.py
   - fix-heading-spacing.py
3. Run `markdownlint-cli2 <file_path>` to audit
4. Manual correction for remaining issues

But the user's workflow says:
1. First: `markdownlint-cli2 --fix`
2. Then: the companion scripts
3. Then: manual if needed

This matches what's already documented! But the user is suggesting this workflow isn't clearly documented and needs to be updated across relevant skills.

Let me check what skills reference markdown linting to find where the workflow is documented inconsistently.

Let me also check if there are existing skills in the other repos the user mentioned.

Actually, let me re-read the user's message more carefully:

> markdownlint-cli2 has fix mode. we must use that first. after that we have to use the available scripts under markdown skill to handle markdown lint errors. after that you can go to further fixes in your way
> is this workflow correctly documented?
> update all relevant skills - according to our conversation.
> create new skills if that is most appropriate - you can also enrich existing skills if that is most appropriate.
> we are using a layered approach for skills.
> we need maximum number of reusable skills. skills can be base or composers.

So the user wants me to:
1. Verify if the 3-step workflow (markdownlint-cli2 --fix → companion scripts → manual fixes) is correctly documented
2. Update all relevant skills if not
3. Create new skills if appropriate, or enrich existing ones
4. Follow layered approach (base → composer)

Let me think about what skills need updating:

1. **markdown-generation** — The SSOT for the markdown lint workflow. It already documents the workflow in §2 and §3. But I need to check if the "Step 1 → Step 2 → Step 3" sequence is explicitly clear. Looking at §2:
   - Step 3: Auto-Fix (markdownlint-cli2 --fix)
   - Step 4: Dry-Run Companion Scripts
   - Step 5: Audit Check
   - Step 6: Manual Correction

   This matches the user's stated workflow. But maybe it could be clearer.

2. **skill-factory** — References markdown-generation for linting. §3 Post-Drafting Checklist mentions: "Linting MUST be performed by invoking `markdownlint-cli2 --fix <path>` then `markdownlint-cli2 <path>`" and "Recommended fix-script execution order is documented in Markdown Generation §3.1."

   This already delegates correctly to markdown-generation.

So the question is: what's missing or unclear?

Looking more carefully, the markdown-generation §2 says:
1. Config Initialization
2. Sync Check
3. Auto-Fix (markdownlint-cli2 --fix)
4. Dry-Run Companion Scripts (---check first, then apply)
5. Audit Check (markdownlint-cli2)
6. Manual Correction
7. Fidelity Verification

Step 4 mentions "Before applying any companion script from §3, MUST run with --check first to preview changes" - this is saying to use --check before applying each script.

But this doesn't mention running ALL scripts in the §3.1 order. Let me re-read...

Actually §3.1 does define the execution order. And step 4 says to use companion scripts. But the "Dry-Run Companion Scripts" step says "MUST run with --check first to preview changes" and "then re-run without --check to apply." It doesn't explicitly say "run ALL scripts in §3.1 order."

So there's a gap: step 4 says to use companion scripts but doesn't explicitly say "run all companion scripts from §3 in the order specified by §3.1." The link is there but indirect.

Also, the user's workflow says:
1. `markdownlint-cli2 --fix` (auto-fix mode)
2. Companion scripts from markdown-generation
3. Manual fixes

This is exactly what §2 steps 3, 4, 6 say. So maybe the user just wants me to verify this is correct and then update all skills that mention linting to be consistent.

Let me search for all skills that reference markdownlint or linting workflow.

**Tool: task**

**Input:**
```json
{
  "description": "Find all lint-workflow references",
  "subagent_type": "explore",
  "prompt": "Do a thorough search of these directories for ALL references to markdown lint workflow, markdownlint, auto-fix, fix scripts, companion scripts, verification workflow, lint verification, or lint audit:\n\n1. /Users/dk/lab-data/ai-suite/.agents/skills/ — search SKILL.md and AGENTS.md files\n2. /Users/dk/lab-data/ai-suite/ai-agent-rules/ — search .md files\n3. /Users/dk/lab-data/ai-suite/AGENTS.md — the root AGENTS.md\n\nAlso check these sibling workspace paths:\n4. /Users/dk/lab-data/oleovista-acers/.agents/skills/ — search SKILL.md and AGENTS.md\n5. /Users/dk/lab-data/oleovista-acers/acers-web/.claude/skills/ — search .md files\n\nFor each match, return:\n- The full file path\n- The relevant paragraph/section (copy a few lines around the match)\n- Which step of the lint workflow it describes (if any)\n\nBe very thorough — check ALL skills. I need to know which skills independently document linting steps vs. which delegate to markdown-generation skill."
}
```

**Output:**
```
<task id="ses_10d82cbf9ffeTVEAq5qgWqqXxW" state="completed">
<task_result>
Here is the complete, organized report of all findings.

---

## Summary: No results in oleovista-acers workspace

Both `/Users/dk/lab-data/oleovista-acers/.agents/skills/` and `/Users/dk/lab-data/oleovista-acers/acers-web/.claude/skills/` (the latter does not exist) have **zero** matches for any of the search patterns.

---

## CATEGORY A: Skills that INDEPENDENTLY DOCUMENT their own lint workflow or command references

These skills define concrete `markdownlint-cli2` commands, steps, or procedures **without** delegating to the `markdown-generation` skill for execution:

### 1. `markdown-generation` (THE CENTRAL SKILL)
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/SKILL.md`
- **Lines 78-98 — §2 Verification Workflow:**
  Defines the full 7-step verification pipeline: (1) Config initialization, (2) Sync check with `.vscode/settings.json`, (3) Auto-fix via `markdownlint-cli2 --fix`, (4) Dry-run companion scripts first, (5) Audit check via `markdownlint-cli2`, (6) Manual correction, (7) Fidelity verification.
- **Lines 101-181 — §3 Companion Scripts:**
  Ships **7 fix scripts** (`fix-table-separators.py`, `wrap-long-lines.py`, `fix-fenced-code-language.py`, `fix-emphasis-as-heading.py`, `fix-list-style.py`, `fix-heading-spacing.py`, `fix-container-fence.py`), each with `--check` dry-run mode. Defines the **mandatory execution order** in §3.1.
- **Lines 183-199 — §3.2 markdownlint-cli2 --fix Caveats:**
  Documents the known `--fix` corruption of closing fences (MD040) and provides the resolution.
- **Lines 210-236 — §5 CI Integration:**
  Pipeline execution order for CI and the one-shot invocation commands.
- **Lines 269-275 — §5.3 Lint Gate:**
  Every skill-factory-authored skill MUST pass the full Verification Workflow.

### 2. `markdown-generation/AGENTS.md`
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/AGENTS.md`
- **Line 8:** `- **Auto-Fix**: Mandatory use of markdownlint-cli2 --fix before submission.`

### 3. `mise-tool-management`
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/mise-tool-management/SKILL.md`
- **Lines 1070-1074 — §9.1 Validation Commands by File Type:**
  Documents `markdownlint-cli2 <absolute_path>` for syntax check and `markdownlint-cli2 --fix <absolute_path>` for format check & fix for `*.md` Markdown files.
- **Lines 1082-1090:** Auto-fixer guidance for Python (ruff/black) — not markdown but shows it documents its own tools independently.

### 4. `is-this-command-safe`
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/is-this-command-safe/SKILL.md`
- **Line 175:** Lists `markdownlint-cli2` as a known linter in the SAFE command allowlist.
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/is-this-command-safe/docs/cheatsheet.md`
- **Lines 383-393:** Full safety classification for `markdownlint-cli2` — SAFE without `--fix`, HAS-DESTRUCTIVE-FLAGS with `--fix`.

### 5. `opencode-permission-config`
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/opencode-permission-config/SKILL.md`
- **Lines 284-286:** Documents `markdownlint-cli2` as allowed as `markdownlint-cli2 *` in opencode's permission config; notes the `--fix` flag matches the same wildcard.

### 6. `vscode-terminal-autoapprove-audit`
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/vscode-terminal-autoapprove-audit/SKILL.md`
- **Line 188:** Lists `markdownlint-cli2` as a "lint/check tool invoked repeatedly" (keep candidate).
- **Line 204:** Provides the anchored regex migration pattern for `markdownlint-cli2`.

### 7. `vscode-autoapprove-entry-consolidation`
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/vscode-autoapprove-entry-consolidation/SKILL.md`
- **Line 190:** Mentions `markdownlint-cli2` in the context of extending existing regex patterns with `(?! .*--fix)`.
- **Line 200-204:** Uses `markdownlint-cli2 --fix` as an example of a dangerous flag variant.

---

## CATEGORY B: Skills that DELEGATE to `markdown-generation` for lint verification

These skills explicitly reference `markdown-generation` or `markdown-generation-rules.md` as the SSOT for linting:

### 8. `skill-factory`
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/skill-factory/SKILL.md`
- **Lines 332-341:** Explicitly delegates: "Run the **Markdown Generation** protocol to ensure 100% lint compliance." References both `markdown-generation/SKILL.md` and `markdown-generation-rules.md §5`. Specifically directs to `markdown-generation §3.1` for fix-script execution order.

### 9. `git-feature-branch-atomic-commit`
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/git-feature-branch-atomic-commit/SKILL.md`
- **Line 32:** Lists `markdown_generation` as a related skill for "Artifact lint verification via markdownlint-cli2 CLI."

### 10. `git-stash-parent-commit`
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/git-stash-parent-commit/SKILL.md`
- **Lines 103-105:** "All markdown artifacts ... MUST be verified with `markdownlint-cli2` per Markdown Generation Rules."

### 11. `code-explanation`
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/code-explanation/SKILL.md`
- **Line 91:** "All documentation MUST pass **Markdown Generation Rules**."

### 12. `loan-foreclosure-analysis`
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/loan-foreclosure-analysis/SKILL.md`
- **Line 23:** "Format results in lint-compliant markdown tables per Markdown Generation Rules."
- **Lines 105-113:** Lists `markdownlint-cli2` for document validation but frames it as per the rules.
- **Line 155:** References `markdown-generation-rules.md`.
- **AGENTS.md Line 9:** "All output MUST pass `markdownlint-cli2` audit."

### 13. `dev-env-private-config-symlink`
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/dev-env-private-config-symlink/SKILL.md`
- **Line 199:** References `markdown-generation` + project rules for output format.

### 14. `env-example-creation`
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/env-example-creation/SKILL.md`
- **Line 101:** "Lint clean via `markdownlint-cli2` (if the file contains markdown)" — in the verification checklist, but not defining its own workflow.

### 15. `jira-automation-rules`
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/jira-automation-rules/SKILL.md`
- **Line 397:** Lists `../markdown-generation/SKILL.md` as the reference for markdown linting.

### 16. `jira-workitem-hierarchy-report`
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/jira-workitem-hierarchy-report/SKILL.md`
- **Line 110:** Lists `markdown-generation` skill for markdown generation.

### 17. `java-vendored-snapshot-compile-check`
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/java-vendored-snapshot-compile-check/SKILL.md`
- **Line 187:** Delegates to "Markdown Generation Skill" for markdown formatting.

### 18. `unused-dependencies-audit/AGENTS.md`
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/unused-dependencies-audit/AGENTS.md`
- **Line 42:** "Markdown Generation — Document audit results."

### 19. `package-version-correction/AGENTS.md`
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/package-version-correction/AGENTS.md`
- **Line 37:** "Markdown Generation — Document version audit results."

### 20. `npm-overrides-audit/AGENTS.md`
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/npm-overrides-audit/AGENTS.md`
- **Line 41:** "Markdown Generation — Document override audit results."

### 21. `copilot-chat-history-analysis`
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/copilot-chat-history-analysis/SKILL.md`
- **Line 292:** References "Markdown Generation Rules lint."

### 22. `command-autoapprove-onboarding`
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/command-autoapprove-onboarding/SKILL.md`
- **Line 442:** References "Markdown Generation Rules lint."

### 23. `rule-to-skill-industrialization`
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/rule-to-skill-industrialization/SKILL.md`
- **Line 115:** "A final `markdownlint-cli2` audit passes with ZERO errors."
- **Line 121:** "Verification Tool: `markdownlint-cli2` (Mandatory for compliance checks)."
- **Line 74:** References `markdown-generation-rules.md §4.2.8` for cross-repo links.

### 24. `jira-acli-operations`
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/jira-acli-operations/SKILL.md`
- **Line 804:** References `markdown-generation/SKILL.md`.

### 25. `postgres-local-dump-restore`
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/postgres-local-dump-restore/SKILL.md`
- **Line 316:** References "Markdown Generation Rules."

---

## CATEGORY C: Skills that MERELY MENTION markdownlint in passing (no workflow delegation or definition)

### 26. `separate-content-from-formatting-commits`
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/separate-content-from-formatting-commits/SKILL.md`
- **Lines 358-359:** Mentions `markdownlint-cli2 --fix` in a narrative example of formatting drift. Not a workflow step.

### 27. `android-feature-to-shared-kotlin-lib`
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/android-feature-to-shared-kotlin-lib/SKILL.md`
- **Line 237:** "Markdown lint: project `markdownlint-cli2` invocation." — just a callout in a delegation list.

### 28. `mcp-cross-tool-config-sync`
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/mcp-cross-tool-config-sync/SKILL.md`
- **Lines 288-289:** Mentions `/opt/homebrew/bin/markdownlint-cli2` as an example of preferring direct binary over `npx`. Not a lint workflow reference.

### 29. `general/list-indent-consistency`
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/general/list-indent-consistency/SKILL.md`
- **Lines 15, 24, 37:** Mentions auto-fix modes and markdown-generation linting as a consumer domain. The skill itself is a consumed primitive.
- **AGENTS.md Line 27:** References "markdown-generation ... with lint auto-fix."

---

## CATEGORY D: GitHub CI Workflow Skills for Markdown Lint

### 30. `github-ci-markdown-lint` (B7)
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/github-ci-markdown-lint/SKILL.md`
- **FULL SKILL (101 lines):** Generates `.github/workflows/ci-markdown-lint.yml` using `DavidAnson/markdownlint-cli2-action@v19`. This is a **CI-only** workflow generator — it produces a GitHub Actions YAML file, not local lint procedures. It is consumed by `github-ci-lint`, `github-workflows`, and `github-repo-publish`.

### 31. `github-ci-lint` (C2)
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/github-ci-lint/SKILL.md`
- **Lines 11-23:** Calls B7 (`github-ci-markdown-lint`) and B8 (`github-ci-python-lint`). A composer that delegates to the base skills.

### 32. `github-workflows` (C4)
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/github-workflows/SKILL.md`
- **Line 22:** Includes `github-ci-markdown-lint` (B7) in its assembly of all workflows.

### 33. `github-pr-labeler`
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/github-pr-labeler/SKILL.md` (line 128) and `AGENTS.md` (line 20)
- References `github-ci-markdown-lint` as a companion CI workflow.

### 34. `github-ci-python-lint`
- **File:** `/Users/dk/lab-data/ai-suite/.agents/skills/github-ci-python-lint/SKILL.md`
- **Lines 26, 108:** References `github-ci-markdown-lint` as a companion base skill.

---

## CATEGORY E: ai-agent-rules files that define lint standards

### 35. `ai-agent-rules/markdown-generation-rules.md`
- **File:** `/Users/dk/lab-data/ai-suite/ai-agent-rules/markdown-generation-rules.md`
- **§5 (lines 438-475):** The definitive **Validation Rules** section — defines direct execution (no npx), auto-fix first mandate, project root execution requirement, cross-platform compatibility, IDE synchronization. The SSOT for all markdown lint technical rules.
- **§5.1 (lines 478-517):** Common rules & aliases table (MD001-MD999).
- **§6 (lines 551-1002):** Common error patterns & troubleshooting with resolution strategies.

### 36. `ai-agent-rules/markdown-generation-rules-additions.md`
- **File:** `/Users/dk/lab-data/ai-suite/ai-agent-rules/markdown-generation-rules-additions.md`
- **Lines 1-37:** Supplements §6 with additional error patterns (MD051 link fragment errors from malformed fences, MD001 heading increments).

### 37. `ai-agent-rules/ai-rule-standardization-rules.md`
- **File:** `/Users/dk/lab-data/ai-suite/ai-agent-rules/ai-rule-standardization-rules.md`
- **Lines 241-246:** Mandates validation with `markdownlint-cli2` binary, forbids `npx`, references `markdown-generation-rules.md §5`.
- **Lines 411-412:** Mandates lint check per both `markdown-generation-rules.md` and its additions.

### 38. `ai-agent-rules/ai-agent-planning-rules.md`
- **File:** `/Users/dk/lab-data/ai-suite/ai-agent-rules/ai-agent-planning-rules.md`
- **Lines 250-252:** Mandates compliance with both `markdown-generation-rules.md` and its additions before finalizing artifacts.

### 39. `ai-agent-rules/code-documentation-rules.md`
- **File:** `/Users/dk/lab-data/ai-suite/ai-agent-rules/code-documentation-rules.md`
- **Line 140:** "All documentation MUST pass Markdown Generation Rules."

### 40. `ai-agent-rules/ai-agent-session-documentation-rules.md`
- **File:** `/Users/dk/lab-data/ai-suite/ai-agent-rules/ai-agent-session-documentation-rules.md`
- **Lines 90-91, 108:** Mandates compliance with both `markdown-generation-rules.md` and `markdown-generation-rules-additions.md`.

### 41. `ai-agent-rules/shell-execution-rules.md`
- **File:** `/Users/dk/lab-data/ai-suite/ai-agent-rules/shell-execution-rules.md`
- **Line 776:** A comment reference "under markdown lint" in a formatting context.

---

## CATEGORY F: Root AGENTS.md

### 42. `/Users/dk/lab-data/ai-suite/AGENTS.md`
- **Line 204:** Documents `github-ci-lint` skill in the skills table: "C2 composer — generates CI lint workflows by calling B7 (markdown lint) and B8 (python lint) base skills."

---

## KEY ANALYSIS: Independent vs. Delegating

### Skills that INDEPENDENTLY document linting steps:
1. **`markdown-generation`** — The SSOT. Defines the full 7-step Verification Workflow, 7 companion fix scripts with execution order, CI pipeline integration, caveats.
2. **`mise-tool-management`** — Defines its own per-file-type validation command table including `markdownlint-cli2` commands.
3. **`is-this-command-safe`** — Independently classifies `markdownlint-cli2` safety in its cheatsheet.
4. **`opencode-permission-config`** — Independently documents the `markdownlint-cli2 *` permission pattern.
5. **`vscode-terminal-autoapprove-audit`** — Independently provides the anchored regex for `markdownlint-cli2`.
6. **`github-ci-markdown-lint`** (B7) — Independently generates the CI workflow YAML (different concern: CI/CD, not local lint).

### Skills that DELEGATE to `markdown-generation`:
- `skill-factory` (explicitly cites it with section references)
- `git-feature-branch-atomic-commit`
- `git-stash-parent-commit`
- `code-explanation`
- `loan-foreclosure-analysis`
- `dev-env-private-config-symlink`
- `jira-automation-rules`
- `jira-workitem-hierarchy-report`
- `java-vendored-snapshot-compile-check`
- `unused-dependencies-audit`
- `package-version-correction`
- `npm-overrides-audit`
- `copilot-chat-history-analysis`
- `command-autoapprove-onboarding`
- `rule-to-skill-industrialization`
- `jira-acli-operations`
- `postgres-local-dump-restore`

### Skills with merely passing mentions:
- `separate-content-from-formatting-commits`
- `android-feature-to-shared-kotlin-lib`
- `mcp-cross-tool-config-sync`
- `general/list-indent-consistency`
- `env-example-creation`
</task_result>
</task>
```

---

## Assistant (Build · Big Pickle · 24.3s)

_Thinking:_

This is very comprehensive. Now I understand the landscape. Let me analyze what the user is asking:

1. Is the 3-step workflow (`markdownlint-cli2 --fix` → companion scripts → manual fixes) correctly documented?
2. Update all relevant skills
3. Create new skills if appropriate
4. Follow layered approach (base → composer)

Let me examine what's actually documented versus what should be:

**Current state in `markdown-generation` (§2 Verification Workflow):**
1. Config Initialization
2. Sync Check  
3. **Auto-Fix**: `markdownlint-cli2 --fix <file_path>` 
4. **Dry-Run Companion Scripts**: Must run with `--check` first, then re-run without
5. **Audit Check**: `markdownlint-cli2 <file_path>`
6. **Manual Correction**: Fix remaining issues
7. **Fidelity Verification**

The issue is: Step 4 says "Before applying any companion script from §3, MUST run with `--check` first to preview changes, review the proposed diffs, then re-run without `--check` to apply."

But this says "for each script, do --check first then apply" — which is a bit awkward. Also, it doesn't explicitly say to run ALL scripts in the §3.1 order.

The user's desired workflow is simpler:
1. Run `markdownlint-cli2 --fix` (auto-fix mode handles what it can)
2. Run companion scripts in order (handles what --fix can't)
3. Manual fixes for anything remaining

This is cleaner and matches the "pipeline" concept better.

Also, the `--check` step seems unnecessarily cautious for every script — the companion scripts are deterministic and well-tested. The `--check` should be optional, not mandatory.

Let me now think about what needs to change:

1. **Refine `markdown-generation` SKILL.md** to clarify the 3-step workflow
2. **The key issue**: The markdown-generation skill's Verification Workflow mentions companion scripts as step 4 but:
   - It says "for each script, --check first then apply" which is awkward
   - It doesn't clearly state "run ALL companion scripts in §3.1 order"
   - It could really benefit from a clear "3-step markdown lint fix pipeline" concept

Also, the skill-factory's Post-Drafting Checklist delegates to markdown-generation. Let me check if it's missing anything.

In `skill-factory` §3:
- "Recommended fix-script execution order is documented in **Markdown Generation §3.1**"
- "Linting MUST be performed by invoking `markdownlint-cli2 --fix <path>` then `markdownlint-cli2 <path>`"

This says `markdownlint-cli2 --fix` then `markdownlint-cli2` — but doesn't mention running companion scripts. It does mention §3.1 but only in the context of "recommended fix-script execution order."

So the gap is: skill-factory §3 mentions `markdownlint-cli2 --fix` + companion scripts (via §3.1 reference), but doesn't explicitly articulate the 3-step pipeline.

Now, what new skills do we need?

The user said:
- "create new skills if that is most appropriate"
- "we are using a layered approach for skills"
- "we need maximum number of reusable skills"

But the markdown lint workflow is already well-covered by `markdown-generation` as the SSOT. The gap is that:
1. The 3-step pipeline isn't clearly articulated there
2. The `--check` step is unnecessarily framed as mandatory-per-script
3. Some skills reference linting independently without delegating to markdown-generation

So the right approach is:
- **Enrich** `markdown-generation/SKILL.md` — make the 3-step pipeline explicit
- **Enrich** `skill-factory/SKILL.md` §3 to clearly state the 3-step pipeline
- **Create** a new skill? Maybe a small base skill that wraps the pipeline into a single script?

Actually, thinking about it more: The user wants "maximum number of reusable skills" with a "layered approach." 

What reusable base skills can we extract?
1. **`markdown-lint-fix-pipeline`** — A base skill that provides a single script wrapping the 3-step pipeline. This would be a base primitive that:
   - Runs `markdownlint-cli2 --fix`
   - Runs companion scripts in §3.1 order
   - Runs `markdownlint-cli2` final audit
   
But wait — this is just composing existing tools/scripts. The layering would be:
- `markdown-generation` (base) — owns the 7 companion scripts + workflow
- `markdown-lint-fix-pipeline` (composer) — shells out to `markdownlint-cli2` + companion scripts

Actually, looking at this more carefully, `markdown-generation` IS already the base skill. The issue is the workflow documentation.

Let me think about what would be most valuable:

1. **Refine `markdown-generation` §2** to clearly state the 3-step pipeline:
   - Step 1: `markdownlint-cli2 --fix`
   - Step 2: Companion scripts in §3.1 order
   - Step 3: Manual fixes + final audit

2. **Update `skill-factory` §3** to reference the 3-step pipeline explicitly

3. Maybe create a **composer skill** `markdown-lint-pipeline` that provides a single invocation:
   ```bash
   python3 fix-markdown.py file.md
   ```
   Which wraps the whole 3-step pipeline into one command.

This last option would be a composer on top of `markdown-generation`'s companion scripts. It would make it a reusable primitive that CI, pre-commit hooks, and other skills can call.

Actually, that's a really good idea. Let me think about it:
- **Base**: `markdown-generation` — owns the fix scripts + workflow protocol
- **Composer**: `markdown-lint-pipeline` — provides a single `fix-markdown-pipeline.py` script that runs: `markdownlint-cli2 --fix` → companion scripts → `markdownlint-cli2` audit. Reports any remaining errors.

But wait, the markdown-generation skill already IS the base skill with its scripts. Do we need another layer?

Looking at it from the "maximum reusability" perspective:
- `markdown-generation` owns the scripts and the protocol
- Skills that need linting can either:
  a) Call `markdown-generation`'s companion scripts directly
  b) Use a simpler pipeline script

The user wants clarity. Let me focus on what's currently documented and where the gaps are.

**The 3-step workflow** the user described:
1. `markdownlint-cli2 --fix` first
2. Companion scripts from markdown-generation
3. Manual fixes

**Current documentation** in `markdown-generation §2`:
- Step 3: Auto-Fix (`markdownlint-cli2 --fix`) ✓
- Step 4: Companion scripts (but framed as dry-run first, and not explicitly "run all in §3.1 order")
- Step 5: Audit check
- Step 6: Manual correction

So the gap is:
- Step 4 should be restructured to clearly say: "run ALL companion scripts in §3.1 order"
- The `--check` requirement should be clarified as optional, not per-script mandatory
- The pipeline should be reframed as a clear 3-step process

Let me also look at what the user said about "these scripts helps a lot. we have to keep them as part of the skill."

This confirms scripts should be part of skills.

Let me also check if a composer wrapping the pipeline would be useful...

Actually, I think the right approach is:
1. **Refine `markdown-generation` §2** — articulate the 3-step pipeline clearly
2. **Create a pipeline script** `scripts/fix-markdown-pipeline.py` in `markdown-generation` — a convenience wrapper that does all 3 steps (this would be a NEW companion script for the skill)
3. **Update `skill-factory` §3** — reference the 3-step pipeline clearly, including the new script
4. **Cross-reference** the pipeline in the root AGENTS.md

Let me plan this properly following the planning rules.

Actually wait — before I plan, let me re-read the key instruction: "plan first according to /Users/dk/lab-data/ai-suite/ai-agent-rules/ai-agent-planning-rules.md. follow the instructions in /Users/dk/lab-data/ai-suite/ai-agent-rules/ai-agent-planning-rules.md strictly & deeply."

The user is asking me to present a plan FIRST before executing. Let me deconstruct the request and formulate a plan.

Plan elements:
1. **Goal**: Verify and document the correct 3-step markdown lint fix pipeline across all relevant skills
2. **What to create/update**:

Let me first verify my understanding of the gaps:

In `markdown-generation/SKILL.md §2`:
- Steps 3-6 should be reorganized into a clear 3-step pipeline
- The companion script execution should say "run ALL scripts in §3.1 order" not "for each, --check first"
- The known caveats should still be documented

In `skill-factory/SKILL.md §3`:
- The lint gate should reference the explicit 3-step pipeline, not just "markdown-generation protocol"
- Should say: Step 1 = markdownlint-cli2 --fix, Step 2 = companion scripts, Step 3 = manual fixes + audit

Now for the new script: `scripts/fix-markdown-pipeline.py` in `markdown-generation`:
- Runs: markdownlint-cli2 --fix → companion scripts (§3.1 order) → markdownlint-cli2 audit
- Exit 0 if clean, non-zero with report of remaining issues

Then update skill-factory to reference this script.

Let me formulate the plan now.

Let me read the planning rules deeply and formulate a proper plan.

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/SKILL.md",
  "limit": 105,
  "offset": 76
}
```

**Output:**
```
<path>/Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/SKILL.md</path>
<type>file</type>
<content>
76: ***
77: 
78: ## 2. Verification Workflow
79: 
80: Before finalizing ANY markdown file, the agent MUST:
81: 
82: 1. **Config Initialization**: If the project lacks a `.markdownlint.jsonc` file, the agent
83:    MUST initialize it using rules from the reference config (`../../../.markdownlint.jsonc`
84:    relative to this skill file), incorporating the `MD013` 120-character line length exception.
85: 2. **Sync Check**: Ensure `.vscode/settings.json` contains `"markdownlint.configFile": ".markdownlint.jsonc"` to
86:    synchronize the IDE extension with the project's Industrial standard.
87: 3. **Auto-Fix**: Run `markdownlint-cli2 --fix <file_path>` from the project root.
88:    Use paths **relative** to the project root — absolute paths can cause the
89:    tool to silently find 0 files (`Linting: 0 file(s)`) and do nothing.
90: 4. **Dry-Run Companion Scripts**: Before applying any companion script from §3,
91:    MUST run with `--check` first to preview changes, review the proposed diffs,
92:    then re-run without `--check` to apply. Dry-run before apply is MANDATORY
93:    for every companion script.
94: 5. **Audit Check**: Run `markdownlint-cli2 <file_path>`.
95: 6. **Manual Correction**: Fix any remaining semantic or structural errors (e.g., heading increments).
96: 7. **Fidelity Verification**: Ensure the "Fidelity Mandate" (no loss of user technical specifics) is upheld during
97:    formatting.
98: 
99: ***
100: 
101: ## 3. Companion Scripts
102: 
103: This skill ships seven helper scripts under
104: [`scripts/`](scripts/) for one-shot lint fixes:
105: 
106: - [`fix-table-separators.py`](scripts/fix-table-separators.py) — scans for
107:   compact table separators (`|---|---|`) and rewrites them with proper spacing
108:   (`| --- | --- |`) to satisfy MD060. Use `--check` for dry-run.
109: - [`wrap-long-lines.py`](scripts/wrap-long-lines.py) — wraps prose lines
110:   exceeding the configured `--max` width (default 120) while preserving code
111:   blocks, tables, YAML frontmatter, and list structure. Use `--check` for
112:   dry-run.
113: - [`fix-fenced-code-language.py`](scripts/fix-fenced-code-language.py) — adds
114:   a default language tag (default `text`) to bare opening fenced code blocks
115:   to satisfy MD040. Properly undoes `markdownlint-cli2 --fix` damage that
116:   attaches `text` to closing fences. Use `--default <lang>` to override the
117:   language (default: `text`). Use `--check` for dry-run.
118: - [`fix-emphasis-as-heading.py`](scripts/fix-emphasis-as-heading.py) — strips
119:   emphasis markers (`*...*`, `_..._`) from lines that are standalone
120:   emphasis-as-heading paragraphs to satisfy MD036. Use `--check` for dry-run.
121: - [`fix-list-style.py`](scripts/fix-list-style.py) — converts asterisk
122:   unordered list markers (`*`) to dash style (`-`) to satisfy MD004.
123:   Use `--check` for dry-run.
124: - [`fix-heading-spacing.py`](scripts/fix-heading-spacing.py) — inserts a blank
125:   line before headings that lack one to satisfy MD022. Skips YAML frontmatter
126:   and code blocks. Use `--check` for dry-run.
127: - [`fix-container-fence.py`](scripts/fix-container-fence.py) — detects fenced
128:   code blocks whose outer fence uses 4+ backtick markers with content containing
129:   inner ``` fences (markdown-syntax examples). Adds a `text` language tag to
130:   the opening fence to satisfy MD040 without breaking the inner fences. Use
131:   `--check` for dry-run.
132: 
133: All seven scripts operate in-place on a list of file arguments.
134: 
135: ```bash
136: python3 scripts/fix-table-separators.py --check path/to/file.md
137: python3 scripts/fix-table-separators.py path/to/file.md
138: 
139: python3 scripts/wrap-long-lines.py --max 120 --check path/to/file.md
140: python3 scripts/wrap-long-lines.py --max 120 path/to/file.md
141: 
142: python3 scripts/fix-fenced-code-language.py --check path/to/file.md
143: python3 scripts/fix-fenced-code-language.py path/to/file.md
144: 
145: python3 scripts/fix-emphasis-as-heading.py --check path/to/file.md
146: python3 scripts/fix-emphasis-as-heading.py path/to/file.md
147: 
148: python3 scripts/fix-list-style.py --check path/to/file.md
149: python3 scripts/fix-list-style.py path/to/file.md
150: 
151: python3 scripts/fix-heading-spacing.py --check path/to/file.md
152: python3 scripts/fix-heading-spacing.py path/to/file.md
153: 
154: python3 scripts/fix-container-fence.py --check path/to/file.md
155: python3 scripts/fix-container-fence.py path/to/file.md
156: ```
157: 
158: These are convenience tools for the `## 2. Verification Workflow` step 3
159: (auto-fix) — they target patterns `markdownlint-cli2 --fix` does not resolve.
160: 
161: ### 3.1 Execution Order
162: 
163: When running multiple fix scripts, the following order is **REQUIRED** to avoid
164: re-introducing lint errors:
165: 
166: 1. `fix-table-separators.py`
167: 2. `fix-fenced-code-language.py` (MUST run BEFORE `wrap-long-lines.py` — fence
168:    lines may exceed the width limit and wrapping a fence line before its
169:    language tag has been added produces a broken fence)
170: 3. `fix-container-fence.py`
171: 4. `wrap-long-lines.py`
172: 5. `fix-emphasis-as-heading.py`
173: 6. `fix-list-style.py`
174: 7. `fix-heading-spacing.py`
175: 
176: > **Indent drift after editing / lint-fix.** After running the §3.1 pipeline,
177: > verify that continuation-line indent in edited regions matches the original
178: > file's siblings. `markdownlint-cli2 --fix` and companion scripts can leave
179: > whitespace drift on adjacent lines. Delegate detection and repair to the
180: > [`list-indent-consistency`](../general/list-indent-consistency/SKILL.md)

(Showing lines 76-180 of 275. Use offset=181 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 3.5s)

_Thinking:_

Now let me read the skill-factory §3 Post-Drafting Checklist for the lint reference.

**Tool: read**

**Input:**
```json
{
  "offset": 286,
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/skill-factory/SKILL.md",
  "limit": 60
}
```

**Output:**
```
<path>/Users/dk/lab-data/ai-suite/.agents/skills/skill-factory/SKILL.md</path>
<type>file</type>
<content>
286: ***
287: 
288: ## 3. Post-Drafting Checklist
289: 
290: Every skill generated via the Factory MUST automatically undergo the final verification:
291: 
292: - **Portability, Redaction & PII Audit (MANDATORY — SSOT delegation)**: Every file produced by the Factory MUST be
293:   put through the full **[Redaction & Portability Skill](../redaction-portability/SKILL.md)** protocol before the
294:   skill is considered complete. The Factory MUST NOT inline its own redaction rules — the redaction skill is the SSOT.
295:   Specifically, the Factory MUST execute, in order:
296:     1. **Tier Classification** (Redaction §1): Walk every string in every generated artifact (`SKILL.md`,
297:        `AGENTS.md`, every `docs/conversations/*.md`, every `docs/cases/*.md`, every script header) and classify
298:        each candidate string as Tier A (identity/credentials), Tier B (machine/org topology), or Tier C
299:        (public/universal).
300:     2. **Canonical Placeholder Substitution** (Redaction §2): Replace every Tier-A and Tier-B match with the
301:        canonical placeholder vocabulary (`<workspace-root>`, `<user-home>`, `<toolbase>`, `<author>`, `<user>`,
302:        `<corp-proxy-host>`, `<corp-domain>`, `<internal-vcs>`, `<ticket-system>`, `<customer>`,
303:        `<product-codename>`, etc.). Ad-hoc placeholder invention is FORBIDDEN — extend Redaction §2 first.
304:     3. **Path Handling** (Redaction §3): All absolute Windows / POSIX paths are converted to workspace-relative,
305:        user-home-relative (`~`), or placeholder form. Angle-bracket placeholders in `[text](target)` link targets
306:        are converted to inline-code symbolic references per Redaction §3.3 to avoid broken navigation.
307:     4. **Identity Handling** (Redaction §4): Author trailers, reviewer names, OS usernames, and email addresses are
308:        redacted. Commit SHAs are preserved.
309:     5. **Network & Org Handling** (Redaction §5): Internal proxy hosts, internal domains, internal repository URLs,
310:        ticket IDs, customer names, and product codenames are redacted; the `nonProxyHosts` and analogous wildcards
311:        use `<corp-domain>` / `<corp-cloud-domain>` placeholders.
312:     6. **File Naming Hygiene** (Redaction §6): Conversation and case-study filenames MUST encode topics, never
313:        organization or identity strings.
314:     7. **Verification Scan** (Redaction §8 Step 4): Re-run the regex inventory scans for absolute paths, emails,
315:        IPv4, and internal hostnames. The terminal output MUST be empty (or contain only Tier-C universally-true
316:        matches) before the audit passes.
317:     8. **Encoding Sanity Check** (Redaction §8 Step 5): Scan for mojibake markers (`Ã`, `â€`, `Â`, `ï¿½`) that
318:        redaction edits frequently introduce, and fix them before considering the audit complete.
319:     9. **Directory Depth Audit**: Verify the correct directory depth (e.g., `../../../` from a 3-level deep skill).
320:    10. **Repository Independence Audit** (Redaction §1.0 + §1.4): When the new skill mentions ANY other repository
321:        (whether by Markdown link or by prose), run the Pre-Commit Checklist from Redaction §1.4 and apply the
322:        Standalone-Clone Test from §1.0 — "if I clone ONLY the enclosing repo into a fresh empty directory, does
323:        every relative link resolve and does every prose reference still make sense?" Reject any relative-path link
324:        whose target escapes the enclosing repo (count `../` segments) regardless of how it resolves on the author's
325:        disk. Multi-root VS Code layouts are inadmissible defences. The Worked Example in Redaction §1.5
326:        (a public-skill ↔ org-private-skill pair) is the reference pattern.
327: - **Prohibited Behavior**: The Factory MUST NOT publish a skill that has not passed the Redaction & Portability audit.
328:   Half-redacted strings (e.g., `<corp-proxy-host>.<real-corp>.com`) and over-redacted public identifiers
329:   (e.g., redacting `Apache Commons`, `Eclipse`, `Maven Central`) are both audit failures per Redaction §10.
330: - **Contextual Hosting**: Documentation (logs, artifacts) MUST reside in the component's `docs/` folder.
331: - **Fidelity Check**: Verify that no technical details from the source conversation were summarized or lost.
332: - **Markdown Audit**: Run the **[Markdown Generation](../markdown-generation/SKILL.md)**
333:   protocol to ensure 100% lint compliance. The agent MUST re-read
334:   every generated/edited markdown file and fix any stray tool-output tags (`</content>`, `<parameter ...>`), duplicated
335:   lines, broken or multi-line links, unclosed fences, and embedded absolute paths BEFORE presenting the artifact.
336:   Linting MUST be performed by invoking the **`markdownlint-cli2`** binary directly
337:   (e.g., `markdownlint-cli2 --fix <path>` then `markdownlint-cli2 <path>`); using `npx markdownlint-cli2` is
338:   **FORBIDDEN** per
339:   **[Markdown Generation Rules §5](../../../ai-agent-rules/markdown-generation-rules.md#5-validation-rules-markdownlint-cli2)**.
340:   Recommended fix-script execution order is documented in
341:   **[Markdown Generation §3.1](../markdown-generation/SKILL.md#31-execution-order)**.
342: - **Bridge Audit**: Confirm `<skill-dir>/AGENTS.md` exists, carries NO YAML frontmatter (no leading `---` block), contains the five required sections from §2.3.2 (`# <Skill> — Companion Bridge` / `## Purpose` / `## When This Skill Applies` / `## Operational Procedure` / `## Cross-References`), and is within the 40–120 line size guidance from §2.3.5. A skill with no bridge file is INCOMPLETE.
343: - **Registration Audit**: Confirm the new skill row was inserted into the root `AGENTS.md` skills table at the correct
344:   alphabetical (case-insensitive) position by the **Skill** column, NOT appended to the end. Spot-check the rows
345:   immediately above and below to verify the sort order holds.

(Showing lines 286-345 of 710. Use offset=346 to continue.)
</content>
```

---

## User

---

## Assistant (Compaction · Big Pickle · 24.5s)

_Thinking:_

&lt;previous-summary&gt;
## Goal
- Document learnings from a macOS brew upgrade session into reusable skills — create `macos-shell-portability` reference, update `brew-upgrade-command-assembly` and `brew-upgrade-workflow` with output capture patterns, shell portability notes, and `; &&` pitfall documentation.

## Constraints & Preferences
- Layered skill architecture: base primitives (atomic, reusable) vs composers (domain-specific, consume base skills)
- Maximum reusability: decompose into atomic primitives before composing
- Follow skill-factory protocol, planning rules, and standardization rules strictly
- Cross-reference `repo-scratch-output-capture` (already exists) rather than duplicating output capture logic

## Progress
### Done
- Identified the `; &&` parse error root cause in user's brew command chain (semicolon terminates export, leaving `&&` with nothing to chain to)
- Confirmed the `brew-upgrade-command-assembly` script correctly uses `export HOMEBREW_DOWNLOAD_CONCURRENCY=1; brew upgrade ... && brew cleanup ... && ...` (first join is `;`, subsequent joins are `&&`)
- Found existing `repo-scratch-output-capture` skill that user previously used for output capture
- Distinguished `tee brew.log` (interactive, shows output in terminal) vs `repo-scratch-output-capture` (silent, separate .out/.err files in scratch/) as different patterns for different cases
- Created new skill: `.agents/skills/general/macos-shell-portability/SKILL.md` (v1, reference) — documents zsh defaults, BSD vs GNU tool differences, `; &&` pitfall, portable command patterns, cross-references

### In Progress
- Update `brew-upgrade-command-assembly` to v3: clarify `;` vs `&&` in command anatomy, add `tee` capture example + `repo-scratch-output-capture` cross-ref, link `macos-shell-portability`

### Blocked
- (none)

## Key Decisions
- `macos-shell-portability` is a standalone reference skill (no CLI script) placed under `general/` — it's consumed by other skills via cross-link, not invoked programmatically
- `tee brew.log` pattern belongs as a usage example in brew skills, not as its own skill — the silent variant is already covered by `repo-scratch-output-capture`
- Brew skills (`brew-upgrade-command-assembly`, `brew-upgrade-workflow`) get v3 updates with cross-references to the new portability skill and existing output capture skill

## Next Steps
1. Update `brew-upgrade-command-assembly/SKILL.md` to v3: clarify command anatomy (§3), add tee output capture example (§5), add Related Skills section with `macos-shell-portability` and `repo-scratch-output-capture`
2. Update `brew-upgrade-workflow/SKILL.md` to v3: add execution guidance subsection with tee pattern, link `macos-shell-portability` and `repo-scratch-output-capture`, add Related Skills section
3. Register new `macos-shell-portability` skill in root `.agents/skills/AGENTS.md`
4. Run markdownlint on all edited files

## Critical Context
- `; &&` parse error: `export VAR=1; && cmd` is invalid; correct forms are `export VAR=1 && cmd` (chain exit codes) or `export VAR=1; cmd` (independent) or `export VAR=1; cmd1 && cmd2` (mixed)
- macOS ships BSD `tee` that rejects `--version` (fails with `illegal option -- -`) — use `--help` or `man tee` instead
- macOS uses zsh by default since Catalina 10.15 — `help` is a bash builtin, NOT available in zsh; use `man` instead
- `repo-scratch-output-capture` skill uses `> scratch/file.out 2> scratch/file.err` (silent, separate files, gitignored)
- `tee brew.log` captures stdout to file while showing on terminal; requires `2>&1 | tee brew.log` to also capture stderr (as used in the session)
- The user's original command had `| tee brew.log` at the end of the entire `&&` chain — this captures stdout of the LAST command only, not the whole chain; `2>&1 | tee brew.log` after the last command captures only that command's output; to capture everything, wrap the chain in curly braces or a subshell: `{ cmd1 && cmd2; } 2>&1 | tee brew.log`

## Relevant Files
- `.agents/skills/general/macos-shell-portability/SKILL.md`: newly created reference skill (v1)
- `.agents/skills/brew-upgrade-command-assembly/SKILL.md`: base primitive, pending v3 update
- `.agents/skills/brew-upgrade-workflow/SKILL.md`: composer, pending v3 update
- `.agents/skills/repo-scratch-output-capture/SKILL.md`: existing output capture skill, cross-reference target
- `ai-agent-rules/ai-agent-planning-rules.md`: planning protocol followed for plan approval
- `ai-agent-rules/ai-rule-standardization-rules.md`: standardization rules for skill creation
- `.agents/skills/skill-factory/SKILL.md`: skill factory protocol for creation and layering
&lt;/previous-summary&gt;

## Goal
- Document the markdown lint workflow (step 1: `markdownlint-cli2 --fix`, step 2: companion scripts from `markdown-generation/`, step 3: manual corrections) correctly across all relevant skills, using layered base/composer architecture.

## Constraints & Preferences
- Layered skill architecture: base primitives (atomic, reusable) vs composers (domain-specific, consume base skills)
- Maximum reusability: decompose into atomic primitives before composing
- Follow skill-factory protocol, planning rules, and standardization rules strictly
- `markdownlint-cli2 --fix` must run FIRST, THEN companion scripts, THEN manual fixes
- Companion scripts live under `markdown-generation/scripts/` — keep them there, do not duplicate
- New skills under `general/` for cross-domain reusable primitives
- Cross-reference from `oleovista-acers` repos if patterns already exist there

## Progress
### Done
- Brew upgrade output capture and shell portability work is complete (new `macos-shell-portability` skill, `brew-upgrade-command-assembly` v3, `brew-upgrade-workflow` v3, root AGENTS.md registration)
- Discovered `markdown-generation/scripts/wrap-long-lines.py` — successfully used it to fix MD013 violations
- Verified `markdownlint-cli2` has `--fix` mode for auto-fixable rules (MD038, MD040, etc.)
- Confirmed the full lint workflow: `--fix` → companion scripts → manual
- Found that `markdown-generation/SKILL.md` §2 already documents this 7-step workflow
- Found that `skill-factory/SKILL.md` §3 delegates linting to `markdown-generation`
- Identified multiple skills that independently document `markdownlint-cli2` commands WITHOUT delegating to `markdown-generation`:
  - `skill-auto-audit-siblings/SKILL.md` — hardcoded 120-char check
  - `skill-creation-workflow/SKILL.md` — hardcoded command
  - `maven-pom-audit/SKILL.md` — hardcoded command
  - `recursive-claude-transform/SKILL.md` — hardcoded command
  - `ai-rule-standardization-rules.md` — mentions line limit without referencing markdown-generation
  - Several AGENTS.md bridges repeat parts of the workflow

### In Progress
- (none — planning phase before implementation)

### Blocked
- (none)

## Key Decisions
- The 3-step lint workflow (`--fix` → companion scripts → manual) is already correctly documented in `markdown-generation/SKILL.md` §2 (steps 3-4-6) and §3.1 (script order). The gap is that OTHER skills independently hardcode their own `markdownlint-cli2` commands instead of delegating to `markdown-generation`.
- `markdown-generation` is the **base primitive** — owns the lint workflow SSOT, ships the fix scripts, defines execution order. It cannot delegate further.
- Skills that currently hardcode `markdownlint-cli2` commands should be updated to cross-reference `markdown-generation` §2 instead of repeating the command.
- A new composer skill is NOT needed — the delegation pattern (cross-reference + link) is the right mechanism, consistent with how `skill-factory` already delegates to `markdown-generation`.
- Create `general/markdown-lint-orchestration` (or similar) is overkill — the existing `markdown-generation` base skill is the right home for the SSOT; the gap is in the OTHER skills that don't delegate.

## Next Steps
1. Plan and approve: read the full markdown-generation SKILL.md to verify current workflow documentation matches user's stated 3-step workflow (Step 3: --fix, Step 4: companion scripts, Step 6: manual). If all clear, proceed to update non-delegating skills.
2. Update `skill-auto-audit-siblings/SKILL.md`: replace hardcoded `markdownlint-cli2 --max 120` with a cross-reference to `markdown-generation` §2. Add delegation note.
3. Update `skill-creation-workflow/SKILL.md`: replace hardcoded markdownlint command with cross-reference to `markdown-generation` §2.
4. Update `maven-pom-audit/SKILL.md`: replace hardcoded markdownlint command with cross-reference to `markdown-generation` §2.
5. Update `recursive-claude-transform/SKILL.md`: replace hardcoded markdownlint command with cross-reference to `markdown-generation` §2.
6. Update `ai-rule-standardization-rules.md`: replace standalone "120-character limit" statement with cross-reference to `markdown-generation` §1.1.
7. Update all affected AGENTS.md companion bridges to reflect the delegation.
8. Run `markdownlint-cli2 --fix` then `wrap-long-lines.py` on all edited files.

## Critical Context
- `markdownlint-cli2 --fix <file>` auto-fixes MD038 (no-space-in-code), MD040 (fenced-code-language), and other rules — does NOT fix MD013 (line-length) or table alignment issues
- Companion scripts in `markdown-generation/scripts/` handle what `--fix` cannot: `wrap-long-lines.py` (MD013), `fix-table-separators.py` (table alignment), `fix-fenced-code-language.py`, `fix-container-fence.py`, `fix-emphasis-as-heading.py`, `fix-list-style.py`, `fix-heading-spacing.py`
- Execution order per `markdown-generation` §3.1: fix-table-separators → fix-fenced-code-language → fix-container-fence → wrap-long-lines → fix-emphasis-as-heading → fix-list-style → fix-heading-spacing
- Current `markdown-generation/SKILL.md` step 4 says "Dry-Run Companion Scripts" — this requires the user/agent to run ALL scripts in §3.1 order; step 4 does NOT explicitly say "run all scripts in §3.1 order" — this is an indirect relationship that could be clearer
- `skill-factory/SKILL.md` §3 Post-Drafting Checklist already correctly delegates: "Linting MUST be performed by invoking `markdownlint-cli2 --fix <path>` then `markdownlint-cli2 <path>`" and references `markdown-generation` §3.1 for fix-script order
- The user's workflow is: (1) `markdownlint-cli2 --fix` → (2) companion scripts → (3) manual. This matches `markdown-generation` §2 steps 3-4-6 exactly.

## Relevant Files
- `.agents/skills/markdown-generation/SKILL.md`: SSOT for lint workflow — §2 Verification Workflow (7 steps), §3 Companion Scripts (execution order), §3.2 --fix caveats
- `.agents/skills/skill-factory/SKILL.md`: currently delegates to `markdown-generation` correctly — linting step references §3.1
- `.agents/skills/skill-auto-audit-siblings/SKILL.md`: hardcodes `markdownlint-cli2 --max 120` — needs delegation update
- `.agents/skills/skill-creation-workflow/SKILL.md`: hardcodes markdownlint command — needs delegation update
- `.agents/skills/maven-pom-audit/SKILL.md`: hardcodes markdownlint command — needs delegation update
- `.agents/skills/recursive-claude-transform/SKILL.md`: hardcodes markdownlint command — needs delegation update
- `ai-agent-rules/ai-rule-standardization-rules.md`: hardcodes 120-char limit — needs cross-ref to markdown-generation
- `.agents/skills/general/macos-shell-portability/SKILL.md`: newly created, already lint-clean

---

## User

---

## Assistant (Build · Big Pickle · 4.4s)

_Thinking:_

The user is asking me to continue with next steps. Let me now read the other skills that need updating to understand the scope of work, then present a plan.

Let me read the hardcoded markdownlint references in the skills that need updating.

**Tool: grep**

**Input:**
```json
{
  "pattern": "markdownlint",
  "path": "/Users/dk/lab-data/ai-suite/.agents/skills",
  "include": "*.md"
}
```

**Output:**
```
Found 52 matches
/Users/dk/lab-data/ai-suite/.agents/skills/opencode-permission-config/SKILL.md:
  Line 284: - **`markdownlint-cli2`** — allowed as `markdownlint-cli2 *`. The `--fix` flag

  Line 394: | `markdownlint-cli2 *` | VSCode: identical (no --fix) | Identical intent |


/Users/dk/lab-data/ai-suite/.agents/skills/skill-factory/SKILL.md:
  Line 336:   Linting MUST be performed by invoking the **`markdownlint-cli2`** binary directly

  Line 337:   (e.g., `markdownlint-cli2 --fix <path>` then `markdownlint-cli2 <path>`); using `npx markdownlint-cli2` is

  Line 339:   **[Markdown Generation Rules §5](../../../ai-agent-rules/markdown-generation-rules.md#5-validation-rules-markdownlint-cli2)**.


/Users/dk/lab-data/ai-suite/.agents/skills/github-ci-markdown-lint/SKILL.md:
  Line 3: description: Base skill — write a GitHub Actions workflow for markdown linting via `DavidAnson/markdownlint-cli2-action`. Single-purpose workflow generator for CI markdown quality enforcement.

  Line 18: Use this skill whenever an agent must **create or update** a GitHub Actions workflow that lints Markdown files via `markdownlint-cli2` across a repository.

  Line 34: The generated workflow requires the `DavidAnson/markdownlint-cli2-action@v19` GitHub Action (publicly available on the marketplace).

  Line 78:         uses: DavidAnson/markdownlint-cli2-action@v19


/Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/SKILL.md:
  Line 10: (120-character line limit) and passes `markdownlint-cli2` (markdown linting CLI tool) audits.

  Line 38: The `markdownlint-cli2` tool validates anchors via **MD051 - Link fragments should be valid**.

  Line 42: - **Verification**: Run `markdownlint-cli2` - it will catch broken anchor errors (MD051)

  Line 60: npm install --save-dev markdownlint-rule-relative-links

  Line 63: Add to `.markdownlint-cli2.jsonc` (NOT `.markdownlint.jsonc`):

  Line 67:     "customRules": ["markdownlint-rule-relative-links"],

  Line 82: 1. **Config Initialization**: If the project lacks a `.markdownlint.jsonc` file, the agent

  Line 83:    MUST initialize it using rules from the reference config (`../../../.markdownlint.jsonc`

  Line 85: 2. **Sync Check**: Ensure `.vscode/settings.json` contains `"markdownlint.configFile": ".markdownlint.jsonc"` to

  Line 87: 3. **Auto-Fix**: Run `markdownlint-cli2 --fix <file_path>` from the project root.

  Line 94: 5. **Audit Check**: Run `markdownlint-cli2 <file_path>`.

  Line 115:   to satisfy MD040. Properly undoes `markdownlint-cli2 --fix` damage that

  Line 159: (auto-fix) — they target patterns `markdownlint-cli2 --fix` does not resolve.

  Line 178: > file's siblings. `markdownlint-cli2 --fix` and companion scripts can leave

  Line 181: > base skill, then re-run the `markdownlint-cli2` audit before staging.

  Line 183: ### 3.2 Known `markdownlint-cli2 --fix` Caveats

  Line 185: **`markdownlint-cli2 --fix` corrupts bare closing fences.** When it encounters

  Line 196: **Resolution:** Do NOT use `markdownlint-cli2 --fix` for MD040. Instead, run

  Line 216: `markdownlint-cli2 --fix` for MD040 (use `fix-fenced-code-language.py`

  Line 242: (VS Code preview, `markdownlint-cli2`) to misinterpret the colon as a new


/Users/dk/lab-data/ai-suite/.agents/skills/mise-tool-management/SKILL.md:
  Line 1074: | `*.md` Markdown | `markdownlint-cli2` | `markdownlint-cli2 <absolute_path>` | `markdownlint-cli2 --fix <absolute_path>` |


/Users/dk/lab-data/ai-suite/.agents/skills/is-this-command-safe/SKILL.md:
  Line 175: - **Linters**: `markdownlint-cli2`


/Users/dk/lab-data/ai-suite/.agents/skills/is-this-command-safe/docs/cheatsheet.md:
  Line 49: | `markdownlint-cli2` | ✅ / ⚠️ | `--fix` (edits files in-place) | omit `--fix` |

  Line 383: ### `markdownlint-cli2`

  Line 390: - **Sink expansion (auto-approve OK)**: `markdownlint-cli2 ... 2>&1 | (head|tail|wc) -N` ·


/Users/dk/lab-data/ai-suite/.agents/skills/env-example-creation/SKILL.md:
  Line 101: - Lint clean via `markdownlint-cli2` (if the file contains markdown)


/Users/dk/lab-data/ai-suite/.agents/skills/separate-content-from-formatting-commits/SKILL.md:
  Line 358:   separator style, blank lines before code blocks from `markdownlint-cli2


/Users/dk/lab-data/ai-suite/.agents/skills/vscode-terminal-autoapprove-audit/SKILL.md:
  Line 188: - Lint/check tools invoked repeatedly: `markdownlint-cli2`, `npm list`.

  Line 204: | `"markdownlint-cli2": true` | `/^markdownlint-cli2( [^;&\|<>\$` + '`' + `()]*)?$/` | SAFE |


/Users/dk/lab-data/ai-suite/.agents/skills/vscode-autoapprove-entry-consolidation/SKILL.md:
  Line 190:    flags (e.g., `markdownlint-cli2` branch MUST retain `(?! .*--fix)`).

  Line 200: **Worked example — appending `sed -n`, `cat`, `head`, `ls`, `which`, `grep`, `markdownlint-cli2`

  Line 204: && rm -rf ~`, `cat file > /etc/important`, `sed -i ...`, `markdownlint-cli2 --fix ...`,


/Users/dk/lab-data/ai-suite/.agents/skills/rule-to-skill-industrialization/SKILL.md:
  Line 115: 3. A final `markdownlint-cli2` audit passes with **ZERO** errors.

  Line 121: - **Verification Tool**: `markdownlint-cli2` (Mandatory for compliance checks).


/Users/dk/lab-data/ai-suite/.agents/skills/mcp-cross-tool-config-sync/SKILL.md:
  Line 288: real CLI shim, invoke the binary directly (e.g., `/opt/homebrew/bin/markdownlint-cli2`) — `npx` adds startup


/Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/AGENTS.md:
  Line 8: - **Auto-Fix**: Mandatory use of `markdownlint-cli2 --fix` before submission.


/Users/dk/lab-data/ai-suite/.agents/skills/loan-foreclosure-analysis/SKILL.md:
  Line 105: - `markdownlint-cli2` for document validation

  Line 112: - Pass `markdownlint-cli2` audit


/Users/dk/lab-data/ai-suite/.agents/skills/loan-foreclosure-analysis/AGENTS.md:
  Line 9: - **Markdown Compliance**: All output MUST pass `markdownlint-cli2` audit


/Users/dk/lab-data/ai-suite/.agents/skills/is-this-command-safe/docs/conversations/2026-01-30-shell-command-safety-vetting.md:
  Line 46: | 2026-02-06 | `markdownlint-cli2` (user followed up "i mean, is that safe?") | SAFE / HAS-DESTRUCTIVE-FLAGS (`--fix`) |


/Users/dk/lab-data/ai-suite/.agents/skills/git-stash-parent-commit/SKILL.md:
  Line 104:   MUST be verified with `markdownlint-cli2` per [Markdown Generation


/Users/dk/lab-data/ai-suite/.agents/skills/git-feature-branch-atomic-commit/SKILL.md:
  Line 32: | [`markdown_generation`](../markdown-generation/SKILL.md) | Artifact lint verification via `markdownlint-cli2` CLI |


/Users/dk/lab-data/ai-suite/.agents/skills/android-feature-to-shared-kotlin-lib/SKILL.md:
  Line 237: - **Markdown lint**: project `markdownlint-cli2` invocation.

```

**Tool: grep**

**Input:**
```json
{
  "pattern": "markdownlint",
  "path": "/Users/dk/lab-data/ai-suite/ai-agent-rules",
  "include": "*.md"
}
```

**Output:**
```
Found 74 matches
/Users/dk/lab-data/ai-suite/ai-agent-rules/ai-agent-planning-rules.md:
  Line 252:     This includes mandatory verification using `markdownlint-cli` before finalizing any artifact.


/Users/dk/lab-data/ai-suite/ai-agent-rules/ai-rule-standardization-rules.md:
  Line 241:   with the **`markdownlint-cli2`** binary prior to user presentation. Any violations MUST be resolved.

  Line 243:       `markdownlint-cli2 <path>` and `markdownlint-cli2 --fix <path>`). Using `npx markdownlint-cli2` is

  Line 246:       **[Markdown Generation Rules §5 (Validation Rules)](./markdown-generation-rules.md#5-validation-rules-markdownlint-cli2)**;


/Users/dk/lab-data/ai-suite/ai-agent-rules/markdown-generation-rules.md:
  Line 11: compatibility with modern linters (e.g., `markdownlint-cli2`) and ensures consistent readability across all documentation.

  Line 15: - **Rules**: `.markdownlint.jsonc` (Industry Standard JSONC with comments)

  Line 16: - **Ignores**: `.markdownlintignore` (Standard ignore file)

  Line 310: - **Usage**: content of `.markdownlintignore`

  Line 320: - **Inheritance**: Sub-repos MUST have their own `.markdownlint.jsonc` that extends the parent configuration or replicates

  Line 322: - **Local Ignores**: Sub-repos MUST have a corresponding `.markdownlintignore` generated by combining:

  Line 323:   1. Parent `.markdownlintignore` rules.

  Line 394: - **Rule Compliance**: This ensures compliance with `markdownlint` rule MD035 and provides a consistent visual weight.

  Line 402: - **Lint Compliance**: Avoid inline suppression (`MD033`). Instead, use the project-level`.markdownlint.json`

  Line 438: ## 5. Validation Rules (markdownlint-cli2)

  Line 446:     - **Command**: `markdownlint-cli2`

  Line 447:     - **Forbidden**: NEVER use `npx markdownlint-cli2`. Relying on `npx` introduces unnecessary overhead and

  Line 453:     - **Command**: `markdownlint-cli2 --fix "**/*.md"`

  Line 457: 3. **Project Root Execution (CRITICAL)**: ALWAYS run `markdownlint-cli2` from the project root directory where

  Line 458:     `.markdownlint.jsonc` is located. Running from subdirectories will use default settings (80-char line length)

  Line 460:     - **Correct**: `cd /path/to/project && markdownlint-cli2 "ai-agent-rules/file.md"`

  Line 461:     - **Incorrect**: `cd /path/to/project/ai-agent-rules && markdownlint-cli2 "file.md"`

  Line 465:     - Use forward slashes (`/`) for paths and globs, as they are universally supported by `markdownlint-cli2`.

  Line 470:     - To ensure the VS Code `markdownlint` extension (DavidAnson) respects the workspace's Industrial standards,

  Line 472:     - **Protocol**: Add `"markdownlint.configFile": ".markdownlint.jsonc"` to the workspace settings.

  Line 476: Before finalizing any Markdown file, the agent MUST validate against the following rules using `markdownlint-cli2`.

  Line 517: See the full [Rules documentation](https://github.com/DavidAnson/markdownlint/blob/main/doc/Rules.md) for a complete

  Line 553: 3. Verify with `markdownlint-cli2`

  Line 814: Apply the following manual troubleshooting strategies during the generation phase or if `markdownlint-cli2 --fix`

  Line 818:   `.markdownlint.jsonc`) for line-length and wrapping.

  Line 830: markdownlint-cli2 "**/*.md" > lint_report.txt

  Line 858: markdownlint-cli2 "path/to/file.md"

  Line 861: markdownlint-cli2 "**/*.md"

  Line 864: markdownlint-cli2 --rules MD001,MD051 "**/*.md"

  Line 889: - Check `.markdownlint.json` for project-specific rules

  Line 957: markdownlint-cli2 "**/*.md" || exit 1

  Line 967:     npm install -g markdownlint-cli2

  Line 968:     markdownlint-cli2 "**/*.md"

  Line 975: - Install `markdownlint` extension

  Line 980:   "markdownlint.config": {


/Users/dk/lab-data/ai-suite/ai-agent-rules/markdown-generation-rules-additions.md:
  Line 35: 3. Verify with `markdownlint-cli2`

  Line 291: markdownlint-cli2 "**/*.md" > lint_report.txt

  Line 319: markdownlint-cli2 "path/to/file.md"

  Line 322: markdownlint-cli2 "**/*.md"

  Line 325: markdownlint-cli2 --rules MD001,MD051 "**/*.md"

  Line 350: - Check `.markdownlint.json` for project-specific rules

  Line 413: markdownlint-cli2 "**/*.md" || exit 1

  Line 423:     npm install -g markdownlint-cli2

  Line 424:     markdownlint-cli2 "**/*.md"

  Line 431: - Install `markdownlint` extension

  Line 436:   "markdownlint.config": {


/Users/dk/lab-data/ai-suite/ai-agent-rules/docs/walkthroughs/2026-02-09-bash-scripting-standards-walkthrough.md:
  Line 44: - ✅ All modified markdown files pass `markdownlint-cli2`.


/Users/dk/lab-data/ai-suite/ai-agent-rules/docs/implementation-plans/2026-02-09-bash-scripting-rules-standardization.md:
  Line 56: - Run `markdownlint-cli2` on all modified files.


/Users/dk/lab-data/ai-suite/ai-agent-rules/docs/conversations/2025-12-26-pdf-cli-extraction-tool.md:
  Line 1: <!-- markdownlint-disable MD013 -->


/Users/dk/lab-data/ai-suite/ai-agent-rules/docs/conversations/2025-12-26-mise-verification-script-alignment.md:
  Line 1: <!-- markdownlint-disable MD013 -->


/Users/dk/lab-data/ai-suite/ai-agent-rules/docs/conversations/2025-12-16-workflow-fix-mise-input.md:
  Line 1: <!-- markdownlint-disable MD013 -->


/Users/dk/lab-data/ai-suite/ai-agent-rules/docs/conversations/2025-12-26-cicd-rulebooks-refinement-and-deduplication.md:
  Line 1: <!-- markdownlint-disable MD013 -->


/Users/dk/lab-data/ai-suite/ai-agent-rules/docs/conversations/2025-12-18-react-query-organization-table.md:
  Line 1: <!-- markdownlint-disable MD013 -->


/Users/dk/lab-data/ai-suite/ai-agent-rules/docs/conversations/2026-02-06-standardizing-typescript-config.md:
  Line 1: <!-- markdownlint-disable MD013 -->


/Users/dk/lab-data/ai-suite/ai-agent-rules/docs/conversations/2025-12-27-staging-server-diagnostics.md:
  Line 1: <!-- markdownlint-disable MD013 -->


/Users/dk/lab-data/ai-suite/ai-agent-rules/docs/conversations/2026-02-06-dependency-freezing-and-rule-standardization.md:
  Line 1: <!-- markdownlint-disable MD013 -->


/Users/dk/lab-data/ai-suite/ai-agent-rules/docs/conversations/2025-12-16-file-renaming-task.md:
  Line 1: <!-- markdownlint-disable MD013 -->


/Users/dk/lab-data/ai-suite/ai-agent-rules/conversations/2026-02-01-submodule-history-repair.md:
  Line 1: <!-- markdownlint-disable MD013 -->


/Users/dk/lab-data/ai-suite/ai-agent-rules/conversations/2026-01-19-rclone-download-optimization.md:
  Line 1: <!-- markdownlint-disable MD013 -->


/Users/dk/lab-data/ai-suite/ai-agent-rules/conversations/2026-01-19-github-atom-feed-urls.md:
  Line 1: <!-- markdownlint-disable MD013 -->


/Users/dk/lab-data/ai-suite/ai-agent-rules/conversations/2024-05-23-kmp-upgrade-protocol-derivation.md:
  Line 1: <!-- markdownlint-disable MD013 -->


/Users/dk/lab-data/ai-suite/ai-agent-rules/conversations/2026-02-06-typescript-hardening-workflow-globalization.md:
  Line 1: <!-- markdownlint-disable MD013 -->


/Users/dk/lab-data/ai-suite/ai-agent-rules/conversations/2026-01-15-zero-backend-preferences-sync.md:
  Line 1: <!-- markdownlint-disable MD013 -->


/Users/dk/lab-data/ai-suite/ai-agent-rules/architectures/sync/tsconfig.json.md:
  Line 1: <!-- markdownlint-disable MD013 -->


/Users/dk/lab-data/ai-suite/ai-agent-rules/architectures/sync/packages/core/src/worker/index.ts.md:
  Line 1: <!-- markdownlint-disable MD013 -->


/Users/dk/lab-data/ai-suite/ai-agent-rules/architectures/sync/packages/core/src/worker/crypto.asm.ts.md:
  Line 1: <!-- markdownlint-disable MD013 -->


/Users/dk/lab-data/ai-suite/ai-agent-rules/architectures/sync/packages/core/src/storage.ts.md:
  Line 1: <!-- markdownlint-disable MD013 -->


/Users/dk/lab-data/ai-suite/ai-agent-rules/architectures/sync/packages/core/src/types.ts.md:
  Line 1: <!-- markdownlint-disable MD013 -->


/Users/dk/lab-data/ai-suite/ai-agent-rules/architectures/sync/packages/core/src/config.json.md:
  Line 1: <!-- markdownlint-disable MD013 -->


/Users/dk/lab-data/ai-suite/ai-agent-rules/architectures/sync/packages/core/src/engine.ts.md:
  Line 1: <!-- markdownlint-disable MD013 -->

```

---

## Assistant (Build · Big Pickle · 25.4s)

_Thinking:_

The grep results are quite extensive. Let me identify which skills have hardcoded `markdownlint-cli2` commands that should delegate to `markdown-generation` instead:

1. **`git-stash-parent-commit/SKILL.md:104`** — "MUST be verified with `markdownlint-cli2` per [Markdown Generation..." This already delegates! It says "per Markdown Generation" — that's correct.

2. **`separate-content-from-formatting-commits/SKILL.md:358`** — just mentions markdownlint-cli2 as a fact, not a command.

3. **`env-example-creation/SKILL.md:101`** — "Lint clean via `markdownlint-cli2` (if the file contains markdown)" — this is a simple reference, not a full workflow.

4. **`loan-foreclosure-analysis/SKILL.md:105,112`** — mentions markdownlint-cli2 as requirement, doesn't detail the workflow.

5. **`rule-to-skill-industrialization/SKILL.md:115`** — "A final `markdownlint-cli2` audit passes with ZERO errors." and mentions `markdownlint-cli2` as verification tool.

6. **`skill-factory/SKILL.md:336-341`** — Already delegates to `markdown-generation` §3.1 and mentions the `markdownlint-cli2 --fix` then `markdownlint-cli2` pattern.

7. **`mise-tool-management/SKILL.md:1074`** — Just a tool table entry for reference.

8. **`ai-rule-standardization-rules.md:241-246`** — Has its own detailed markdownlint rules section.

Now, the key question is: which skills have workflow duplication vs just a reference?

Looking more carefully at the grep results, most entries are either:
- Direct delegations to `markdown-generation` (correct)
- Brief mentions/requirements (not duplicating workflow)
- Just tool table entries
- References in auto-approve/cheatsheet contexts

The real duplication I found earlier was from the old session state that identified:
- `skill-auto-audit-siblings/SKILL.md` (but I didn't see this in the grep results — maybe I missed it or it doesn't exist anymore)
- `skill-creation-workflow/SKILL.md` (same — might not exist)
- `maven-pom-audit/SKILL.md` (just says "Markdown lint: project markdownlint-cli2 invocation" — this is fine)
- `recursive-claude-transform/SKILL.md` (same)
- `ai-rule-standardization-rules.md` — this has its own detailed section but it's a **rule file** not a skill, so it's expected to have its own rules.

Wait — I need to reconsider. The old session analysis was about skills I found earlier, but the grep results show the current state. Let me check if those specific skills still exist and have hardcoded markdownlint references.

Actually, looking at the grep results again, I see:
- `ai-rule-standardization-rules.md:241-246` — has markdownlint section
- `ai-agent-planning-rules.md:252` — mentions markdownlint-cli in verification
- `markdown-generation-rules.md` — extensive markdownlint rules (this IS the SSOT for rules)

So the landscape is:
1. `markdown-generation/SKILL.md` is the SSOT for the **workflow/protocol** (how to lint)
2. `markdown-generation-rules.md` is the SSOT for the **validation rules** (what to check)
3. `skill-factory/SKILL.md` correctly delegates to `markdown-generation`
4. `ai-rule-standardization-rules.md` has its own markdownlint section — this is OK as it's a rule file
5. Other skills mostly just reference markdownlint briefly or delegate correctly

Now the user's original question was about whether the 3-step workflow is correct:
1. `markdownlint-cli2 --fix`
2. Companion scripts
3. Manual fixes

And the user wanted to document it clearly across skills.

Looking at the current `markdown-generation §2`:
- Step 3: Auto-Fix (markdownlint-cli2 --fix) ✓
- Step 4: Dry-Run Companion Scripts (current: "for each script, --check first then apply") — but should be "run ALL scripts in §3.1 order"
- Step 5: Audit Check (markdownlint-cli2) ✓
- Step 6: Manual Correction ✓

The main issue is Step 4 which says "MUST run with `--check` first to preview changes, review the proposed diffs, then re-run without `--check` to apply. Dry-run before apply is MANDATORY for every companion script."

This is overly cautious for an AI agent workflow. The agent should just run the scripts in order. The `--check` step is unnecessary overhead for every script.

So what I should do:
1. **Update `markdown-generation §2`**: Reframe as a clear "3-step pipeline":
   - Step 1: `markdownlint-cli2 --fix` (auto-fix)
   - Step 2: Companion scripts in §3.1 order (without mandatory --check per script)
   - Step 3: Final audit + manual fixes
   
2. **Update `markdown-generation §3`**: Change the "All seven scripts must use --check first" pattern to "scripts accept --check for optional preview, but in the pipeline they run directly"

3. **Update `skill-factory §3`**: Currently says "Linting MUST be performed by invoking `markdownlint-cli2 --fix <path>` then `markdownlint-cli2 <path>`" and references §3.1 for fix scripts. This should be updated to explicitly mention the 3-step pipeline.

4. Other skills: Most already delegate correctly. The ones that don't are mostly brief references, not full workflow duplication.

Let me think about whether a new pipeline script is warranted.

The user said: "i'm thinking we can have a base skill that handles the whole process. something like: step 1: run markdownlint-cli2 --fix. step 2: run companion scripts. step 3: manual fix."

So the user wants a **new base skill** that wraps the pipeline into a single script. This would be a reusable primitive that any skill can invoke with a single command.

But wait — if I create a new base skill with a script, where does it live? Options:
a) Under `markdown-generation/scripts/fix-markdown-pipeline.py` — since it's part of the markdown-generation ecosystem
b) Under a new standalone base skill directory like `general/markdown-lint-pipeline/` — maximum reusability

Given the layered architecture:
- `markdown-generation` already IS the base skill for markdown generation
- Adding a pipeline script to `markdown-generation/scripts/` is the natural extension
- A separate `general/markdown-lint-pipeline` skill would be a composer on top of `markdown-generation`

Actually, looking at this from a "scripts" perspective: markdown-generation already ships fix scripts. Adding a pipeline wrapper script that orchestrates them is a natural companion. It doesn't need to be a separate skill — it's just a convenience script within the existing skill.

But the user says "have a base skill" — maybe they want a standalone skill. Let me re-read: "we can have a base skill that handles the whole process."

Hmm, but what would a standalone base skill do that `markdown-generation` doesn't already do? It would:
- Define the 3-step pipeline as a reusable protocol
- Maybe ship the pipeline script
- Be consumed by other skills that need markdown linting

The issue is: `markdown-generation` ALREADY defines the protocol and ships the scripts. Creating a separate skill that duplicates this would be bad layering.

I think the right approach is:
1. **Update `markdown-generation/SKILL.md`** to better articulate the 3-step pipeline
2. **Update `markdown-generation/SKILL.md`** to add a convenience pipeline script
3. **Decide** whether the pipeline script + logic should be extractable as a standalone `general/markdown-lint-pipeline` base skill

Actually, re-reading the user more carefully:

> step 1: run markdownlint-cli2 --fix
> step 2: run companion scripts
> step 3: manual fix
> we call it something like "markdown lint workflow"
> i'm thinking we can have a base skill that handles the whole process

The user envisions a base skill called "markdown lint workflow" or similar. But this IS what `markdown-generation` §2 already documents! The issue is that:
1. It's not explicitly called a "3-step pipeline"
2. Step 4 has the cumbersome --check requirement
3. Other skills don't clearly delegate to it

So the fix should be:
1. Enrich `markdown-generation §2` to be a clear "3-step pipeline"
2. Don't create a new separate skill (markdown-generation is already the right home)
3. Add a convenience pipeline script to `markdown-generation/scripts/`
4. Update the other skills that hardcode markdownlint commands to delegate

Let me now formulate the plan and present it to the user.

Actually, let me also consider: should I create a standalone `general/markdown-lint-workflow` base skill that:
- Defines the 3-step pipeline as a reusable protocol
- Ships a single `fix-markdown.sh` or `fix-markdown.py` script
- References `markdown-generation` for companion scripts

This would be a separate base skill consumed by skill-factory and other skills, while `markdown-generation` remains the authoring/companion-script owner.

The layering would be:
- `markdown-generation` (base) — owns companion scripts, lint config, workflow protocol (the "how")
- `general/markdown-lint-workflow` (base) — owns the pipeline script that calls markdownlint-cli2 + companion scripts in order (the "do")

This is actually a cleaner separation. The workflow script lives in the general skill and can be consumed by CI, CI workflows, pre-commit hooks, and other skills without depending on `markdown-generation`'s authoring context.

But wait, the pipeline script would depend on `markdown-generation/scripts/*.py` — so it would still reference `markdown-generation`. That creates a dependency chain: `general/markdown-lint-workflow` → `markdown-generation`.

Hmm, thinking about this differently. What if the pipeline script is just in `markdown-generation/scripts/` and other skills delegate to `markdown-generation`? That's the simplest approach and follows the existing pattern (skill-factory already delegates to markdown-generation).

OK, I think I'm overthinking this. Let me present a clear plan to the user and let them decide.

The plan:
1. **Update `markdown-generation/SKILL.md` §2** — Reframe as explicit 3-step pipeline
2. **Add pipeline script** to `markdown-generation/scripts/` — convenience wrapper
3. **Update `skill-factory/SKILL.md` §3** — Explicitly reference 3-step pipeline
4. **Update dependent skills** to delegate to `markdown-generation` where they currently hardcode

Let me present this plan.

Good. I now have a clear picture of the landscape. Let me present the plan.

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/ai-agent-rules/ai-agent-planning-rules.md",
  "limit": 90
}
```

**Output:**
```
<path>/Users/dk/lab-data/ai-suite/ai-agent-rules/ai-agent-planning-rules.md</path>
<type>file</type>
<content>
1: ---
2: title: Agent Planning
3: description: Guidelines for agent planning,
4:     including the core directive to plan before acting and a protocol for
5:     iterative plan revisions.
6: category: Core Agent Behavior
7: ---
8: 
9: 
10: # Agent Planning Rule: Core Principles and Best Practices
11: 
12: This document outlines the mandatory planning protocol for all AI agents. The primary directive is to ensure all
13: actions are preceded by a transparent, user-approved plan. This rule is foundational to establishing a clear,
14: trustworthy, and effective interaction model.
15: 
16: ---
17: 
18: ## 1. Goal Description & Versioning
19: 
20: All implementation plans MUST follow a strict naming and header convention to ensure traceability and version control.
21: 
22: - **H1 Header Versioning**: Every implementation plan MUST use the format `# [Goal Description] (vN)`
23:   as its primary H1 title (e.g., `# [Setup Authentication] (v1)`).
24: - **Rule Compliance Reference**: A dedicated section titled `## Rule Compliance Reference` MUST immediately follow the
25:   H1 header. It must contain a bulleted list of the specific industrial rules (with relative links) being followed in
26:   the current plan.
27: 
28: ---
29: 
30: ## 2. The Core Planning Directive
31: 
32: All agents must present a clear, step-by-step plan before any implementation. The plan must be explicit,
33: actionable, and tailored to the user’s request. **Only after the plan is approved or clarified should
34: implementation begin.**
35: 
36: This directive is not merely a formality; it is a critical safeguard. By externalizing the planning process, the
37: agent minimizes the risk of misunderstanding, prevents "hallucination," and ensures complete alignment with the
38: user's intent from the outset.
39: 
40: ### 1.1 Primary Goal Persistence Mandate
41: 
42: The agent **MUST** carry over the original 'Starting Point' enquiry (the core objective) into every version of the
43: implementation plan. This goal must remain the primary heading of the document. Any shift in focus or addition of
44: sub-tasks MUST be explicitly documented as secondary or supporting actions to this primary goal, not as a replacement
45: for it.
46: 
47: ### 1.2 Architectural Boundary Verification
48: 
49: Before adding any execution step, the agent MUST verify it is not designated as 'CI/CD Managed' in project rules.
50: Local execution of automated pipeline tasks is PROHIBITED. If a script is for CI/CD, the agent must only modify its
51: templates or source metadata.
52: 
53: ---
54: 
55: ---
56: 
57: ## 3. Components of an Effective Plan
58: 
59: An effective plan is built on four key pillars:
60: 
61: - **Clarity:** The plan must be written in plain, unambiguous language. Avoid technical jargon or internal thought
62: 
63:     process descriptions. Each step should be a simple statement of intent, easily understood by a non-technical
64:     user.
65: 
66: - **Step-by-Step Breakdown:** The plan must break down the request into a logical sequence of discrete, manageable
67: 
68:     steps. This demonstrates a structured approach and allows the user to follow the agent's thought process.
69: 
70: - **Actionability:** Every step in the plan must represent a concrete, executable action. For example, instead of
71: 
72:     "Gather information," an actionable step would be "Search the web for Q4 2024 financial reports from Google."
73: 
74: - **Tailored to the Request:** The plan should directly address the specifics of the user's query. It should not be
75: 
76:     a generic template but a custom-designed workflow that reflects the unique nuances of the task.
77: 
78: ---
79: 
80: ## 4. The Agent Planning Workflow
81: 
82: A well-structured interaction with an agent should follow this five-step workflow:
83: 
84: 1. **Deconstruct the Request:** The agent's first internal action is to analyze the user's prompt. It should
85: 
86:    identify the core task, the specific constraints, the desired output format, and any potential ambiguities or
87:    missing information.
88: 
89: 1. **Formulate the Plan:** Based on the deconstruction, the agent constructs a detailed plan. This plan should be
90: 

(Showing lines 1-90 of 310. Use offset=91 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 2.9s)

_Thinking:_

Let me read the rest of the planning rules for the full protocol, then formulate and present the plan.

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/ai-agent-rules/ai-agent-planning-rules.md",
  "offset": 91
}
```

**Output:**
```
<path>/Users/dk/lab-data/ai-suite/ai-agent-rules/ai-agent-planning-rules.md</path>
<type>file</type>
<content>
91:    a bulleted or numbered list that outlines the exact steps to be taken, including any necessary data retrieval,
92:    analysis, or content generation.
93: 
94: 1. **Present for Approval**: The agent presents the formulated plan to the user. This is a crucial checkpoint.
95:    The agent should explicitly ask for confirmation or for any necessary adjustments before proceeding.
96:    - **Browser Approval**: For manual testing plans, all browser-based tool requests are considered pre-approved
97:        unless explicitly denied by the user.
98: 
99: 1. **Execute the Plan:** Upon receiving user approval, the agent proceeds to implement the plan, step by step. Each
100: 
101:    action is performed as outlined, ensuring the process remains transparent and predictable.
102: 
103: 1. **Report Progress & Completion:** The agent should provide a final summary of the work done, confirming that all
104: 
105:    steps in the plan were executed. For long or complex tasks, providing interim progress updates may also be
106:    beneficial.
107: 
108: ---
109: 
110: ## 5. Handling Edge Cases and Best Practices
111: 
112: - **Ambiguous Requests:** If the user's request is unclear or incomplete, the agent must include a clarification
113: 
114:     step in its plan. The plan should state, "First, I will ask for clarification on `the ambiguous part` to ensure I
115:     proceed correctly."
116: 
117: - **Multi-Turn Conversations:** For continuous dialogues, a new, explicit plan is required for each distinct task or
118: 
119:     significant shift in the user's request. Simple, short follow-up questions do not require a new plan.
120: 
121: - **Exemptions to the Rule:** A plan is not required for trivial, single-step requests that have a straightforward,
122: 
123:     factual answer. For example, a request like "What is the capital of France?" should be answered directly without
124:     a planning step. This demonstrates the agent's ability to discern between simple queries and complex tasks.
125: 
126: ---
127: 
128: ## 6. Iterative Planning and Plan Versioning
129: 
130: The initial plan is a blueprint, not an unbreakable contract. For complex,
131: 
132: - **Categorical Alignment**: Group changes by their architectural layer (e.g., UI, Logic, Docs) unless they are
133: 
134:     functionally coupled.
135: 
136: - **Git Hygiene & Rebase Integration**: For tasks involving multiple branches or history refinement, the plan MUST
137: 
138:     include:
139: 
140: - **Hierarchical Mermaid Mapping**: Visualizing branch dependencies (referencing [Git Rebase Standardization
141: 
142:     Rules](./git-rebase-standardization-rules.md)).
143: 
144: - **CAM Table**: Mapping specific actions per commit to ensure logic isolation.
145: 
146: - **Workflow-First Priority**: If changes involve CI/CD workflows (GitHub Actions, scripts), the agent **MUST** fix,
147: 
148:     test, and verify the workflow functionality *before* arranging or executing commits. Functional stability of the
149:     CI pipeline takes precedence over documentation or stylistic refinements.
150: 
151: ### 1.1 Long-Running & Dynamic Tasks
152: 
153: For long-running or dynamic tasks, the agent may encounter new information or unforeseen obstacles that necessitate
154: a change in direction. In these cases, the agent MUST NOT deviate from the original plan without explicit approval.
155: 
156: ---
157: 
158: ## 7. Industrial Planning Mandates
159: 
160: - **Environment State Check**: Every plan involving runtime verification MUST include a prerequisite step to
161:     confirm the application is running and accessible (e.g., "Verify App is live at `http://localhost:3000`").
162: - **Maximum Literal Detail**: Plans must be exhaustive and literal.
163: 
164: ### 5.1 Impact Scan Enhancement (Maximum Literal Detail)
165: 
166: For every DELETION, RENAMING, or REFUNDAMENTAL change, the plan MUST include a dedicated 'Surface Area Scan' to identify
167: and remediate all global references, internal links, and cross-file dependencies.
168: 
169: ### 5.2 Anti-Summarization & No-Truncation Guardrail
170: 
171: Agents MUST NOT summarize or collapse previously established literal details (file lists, exact commands, logic
172: branches) unless they are functionally obsolete or a mistake. Maximum clarity and non-ambiguity take precedence over
173: brevity. **The 'Change History' table MUST NOT be truncated.** It must remain a complete and literal record of all plan
174: versions (v1, v2, v3, ... vN) without omission.
175: 
176: - **Files:** Explicitly list every file (absolute paths) to be created, modified, or deleted.
177: - **Exact Commands:** CLI commands must be written exactly as they will be executed, including full arguments and piped
178:     operations.
179: - **Literal Payloads:** For operations like `git commit --amend -m "..."`, the plan must include the **literal message
180:     string** within the execution step, not just a reference to it.
181: - **Verifications:** Explicitly state the exact command or visual check used to verify each step.
182: - **Guardrails**: Restate the literal logic for handling conflicts, empty commits, and safety checks in every iteration.
183: - **Pre-Plan Context Gathering**: Information gathering (reading files, `git diff`,`ls`) must happen **BEFORE**
184:     the plan is finalized. A plan based on assumptions is a failed plan.
185: 
186: ---
187: 
188: ## 8. Temporal Hygiene & Change History
189: 
190: To ensure absolute traceability and industrial reliability, all planning and verification artifacts MUST
191: incorporate temporal data.
192: 
193: - **Execution Timestamps**: Every item in `task.md` and `walkthrough.md` MUST include a completion or event
194:     timestamp in the format `[YYYY-MM-DD HH:mm]`.
195: - **Change History Table**: Every versioned implementation plan (v2+) MUST include a "Change History" table
196:     immediately following the goal statement. This table MUST track:
197: 
198:     | Timestamp | Summary of Changes | Rationale |
199:     | :--- | :--- | :--- |
200:     | `[YYYY-DD-MM HH:mm]` | Concise description of the delta. | Why the change was necessary. |
201: 
202: ---
203: 
204: ## 9. Plan Versioning & SSOT Integrity (History Mandate)
205: 
206: **Iterative Planning** is the process of updating a plan based on new findings or changes in a task's requirements.
207: This practice ensures flexibility while maintaining the core principles of transparency and user alignment.
208: 
209: - **Plan Versioning**: All plans must be explicitly versioned (e.g., `implementation_plan_v1.md`, `implementation_plan_v2.md`).
210: - **History Mandate**: New versions MUST NOT overwrite old versions. Each new version MUST include the Change History table documenting all previous revisions.
211: - **SSOT (Single Source of Truth)**: Each version MUST be self-contained, restating all valid context and guardrails. Do not refer to previous versions for "missing details."
212: - **Fresh Start Protocol**: When a "Fresh Start" version (vN) is declared, all subsequent plans (vN+1, vN+2, etc.) MUST reset the 'Change History' and 'User Questions & Answers' to only include items from the declared fresh start version onwards. This is a strict exception to the full history mandate.
213: 
214: ### 7.1 Continuity Audit Mandate (CAM)
215: 
216: Before presenting a new plan version, the agent **MUST** perform a literal line-by-line comparison against the previous
217: version. Any dropped task, alert, or requirement MUST be either restored or explicitly listed in the 'Change History'
218: with a rationale for its removal. **Summarizing integrated logic from sub-plans is a violation.**
219: 
220: ### 7.2 Sub-Plan Versioning & Integration Mandate
221: 
222: All planning artifacts, including secondary or 'sub-plans,' MUST follow the versioning mandate (v1, v2, etc.). They
223: MUST NOT be edited in place. Once a sub-plan is confirmed by the user, its content MUST be integrated into the next
224: version of the main implementation plan while maintaining its full literal detail. **All subsequent updates MUST occur
225: within the main plan.** **Integration MUST be via literal copy-paste of all confirmed mandates.** Any modification for
226: 'brevity' is prohibited. Once integrated, the sub-plan is retired and redundant versioning is forbidden.
227: 
228: - **Propose a Plan Revision:** When a change is required, the agent must immediately pause execution
229:   and present a revised plan to the user.
230: - **Provide a Rationale:** The agent must clearly explain **why** the change is necessary.
231: - **Seek Approval:** The agent must explicitly ask for user approval for the revised plan before proceeding.
232:   This final check ensures the new direction aligns with the user's updated expectations.
233: 
234: ---
235: 
236: ## 10. Task Artifact Synchronization
237: 
238: Follow the status markers and include timestamps:
239: 
240: - **Initial Creation**: Create `task.md` at the start of planning with all top-level items.
241: - **Incremental Updates**: Update `task.md` after completing each significant milestone.
242: - **Status Markers**: Use `[ ]` for pending, `[/]` for in-progress, and `[x]` for completed items `[YYYY-MM-DD HH:mm]`.
243: - **Artifact Location**: All planning artifacts (task.md, implementation plans, walkthroughs) MUST be stored in
244:     the **main repository's** `docs/` directory (e.g., `docs/implementation-plans/<date>-<topic>.md`). When
245:     `ai-agent-rules/` is a Git submodule, artifacts MUST NOT be placed inside the submodule — doing so scatters
246:     planning history into a separate repo's commit graph. The main repo's `docs/` tree is the single source of
247:     truth for all planning artifacts.
248: - **Artifact Cleanup**: If everything is OK, we can remove the artifacts. The removal needs explicit user confirmation.
249: - **Compliance Mandate**: Every generated artifact (task, implementation plan, walkthrough) MUST strictly comply
250:     with **[Markdown Generation Rules](./markdown-generation-rules.md)** and
251:     **[Markdown Generation Rules Additions](./markdown-generation-rules-additions.md)**.
252:     This includes mandatory verification using `markdownlint-cli` before finalizing any artifact.
253: 
254: ---
255: 
256: ## 11. Status Traceability in Iterative Plans
257: 
258: To ensure absolute clarity during multi-phase execution, iterative plans (v2+) MUST track the status of proposed changes.
259: 
260: - **Marking Completed Steps**: If an implementation plan is updated during execution, any proposed change that has
261:   already been successfully implemented MUST be explicitly marked as `[DONE] [YYYY-MM-DD HH:mm]` or
262:   `[COMPLETED] [YYYY-MM-DD HH:mm]` within the 'Proposed Changes' section.
263: - **Visual Distinction**: Completed steps should ideally remain in the plan (to maintain context) but be clearly
264:   demarcated to differentiate them from pending work.
265: 
266: ---
267: 
268: ## 11. User Question Integration Mandate
269: 
270: To ensure maximum transparency and technical accuracy, the agent MUST explicitly address any technical or
271: process-related questions raised by the user during the planning phase.
272: 
273: - **Mandated Documentation**: All user questions and their corresponding agent answers MUST be documented in a
274:     dedicated **"User Questions & Answers"** section at the top of the revised implementation plan.
275: - **Traceability**: This ensures that critical clarifications and course corrections are captured in the
276:     Single Source of Truth (SSOT), making them available for future reference and audits.
277: - **Clarity**: Answers should be technically precise, referring to specific rules or protocols where applicable.
278: 
279: ---
280: 
281: ## 12. State-Dependent Phase Gating
282: 
283: Plans involving future states (e.g., Git history after 3 phases of changes)
284: **MUST NOT** predict or mock the result. They must instead define a **Protocol
285: Gate**: a set of mandatory discovery commands (e.g., `git status`, `git diff`)
286: and verification steps that the agent will run *at that time* to generate a
287: fresh, accurate preview for user approval.
288: 
289: ---
290: 
291: ## 13. Sequential Objective Protocol
292: 
293: To ensure absolute precision and user control, the agent MUST adhere to a strict sequential focus:
294: 
295: - **Single Objective Focus**: When instructed to perform a specific task (e.g., "update rules"), the agent MUST focus
296:   solely on that objective.
297: - **Deferment of Follow-ups**: The agent MUST NOT plan or prepare for follow-up actions (e.g., commit execution) in
298:   the same plan unless explicitly asked.
299: - **Verification Gates**: Follow-up instructions will be provided by the user *after* the current objective is
300:   confirmed complete.
301: - **Instructional Rationale**: When told to update rules, focus on updates ONLY. Do not jump to execution or
302:   downstream tasks until explicitly directed.
303: 
304: ## 14. Single Source of Truth & Content Integrity
305: 
306: The agent MUST strictly maintain the integrity of existing documentation:
307: 
308: - **Anti-Duplication**: Please don't duplicate things. We always need SSOT.
309: - **Audit Requirement**: When adding or updating something, the agent MUST read the file deeply and carefully. Only add what is missing.
310: - **Blending Strategy**: Blend new information into the existing documentation, or enhance the existing information. We always need single source.

(End of file - total 310 lines)
</content>
```

---

## Assistant (Build · Big Pickle · 188.2s)

_Thinking:_

OK, I've read the planning rules. Now let me formulate a proper implementation plan following the rules:

1. The plan should have a versioned H1 header
2. A Rule Compliance Reference section
3. Step-by-step breakdown
4. Be explicit and actionable

Let me also check what the current `markdown-generation §2` actually says more carefully. I already read lines 76-180, but let me also check lines 1-75 for context.

Actually, I have enough context. Let me present the plan.

Key decisions to make:
1. Should the pipeline script live in `markdown-generation/scripts/` or in a new standalone skill?
2. Should the 3-step pipeline be part of `markdown-generation` skill or a separate skill?

The user wants "maximum number of reusable skills" with "layered approach." The 3-step pipeline:
- Step 1: `markdownlint-cli2 --fix` — this is just running a CLI tool
- Step 2: companion scripts from `markdown-generation` — these scripts exist
- Step 3: manual fixes — human/agent judgement

A pipeline script that wraps steps 1-2 (step 3 is manual) would be useful. Where should it live?

Option A: Add it as a script in `markdown-generation/scripts/` and update `markdown-generation/SKILL.md` §2 to clearly articulate the pipeline. Other skills delegate to `markdown-generation`.

Option B: Create a new standalone `general/markdown-lint-workflow` skill that ships the pipeline script and references `markdown-generation` for companion scripts.

The user said "we call it something like 'markdown lint workflow'" — this suggests they want a named concept. And "i'm thinking we can have a base skill that handles the whole process" — suggests they want a separate skill.

But the planning rules say: "Anti-Duplication: Please don't duplicate things. We always need SSOT."

If I create `general/markdown-lint-workflow`, I'd be splitting the lint workflow between `markdown-generation` (which owns the companion scripts and the protocol) and the new skill (which owns the pipeline). That creates two SSOTs for the linting workflow.

Better approach: Keep the SSOT in `markdown-generation`, but restructure it to clearly articulate the 3-step pipeline (including renaming sections if needed). Then add the pipeline convenience script there too.

But the user explicitly said "base skill that handles the whole process" — maybe they want `markdown-generation` to be that skill, just better documented?

I think the right answer is:
1. `markdown-generation/SKILL.md` IS the base skill for markdown lint workflow. Enrich it.
2. Add `scripts/fix-markdown-pipeline.py` convenience wrapper there.
3. Update `skill-factory` and other skills to reference the pipeline.

Let me present this plan.

Actually, hmm. I realize I need to ask a question about whether to create a separate skill or enrich existing. The user explicitly suggested "we call it something like 'markdown lint workflow'" and "have a base skill that handles the whole process." But my analysis says enriching `markdown-generation` is better for SSOT.

Let me include this in the plan as a decision point. I'll present a clear plan with options and ask for approval.

## Analysis & Plan

Here's my understanding after deep reading of both `markdown-generation/SKILL.md` and `skill-factory/SKILL.md`:

### Current State
`markdown-generation/SKILL.md §2` already documents the workflow as 7 steps. But:
- Step 4 mandates `--check` before EVERY companion script — cumbersome for agent workflow
- The 7 steps don't explicitly group into a "step 1: --fix, step 2: companion scripts, step 3: manual" pipeline
- No convenience pipeline script exists to run the pipeline in one invocation

`skill-factory/SKILL.md §3` currently says: "Linting MUST be performed by invoking `markdownlint-cli2 --fix <path>` then `markdownlint-cli2 <path>`" and references §3.1 for fix scripts — but doesn't articulate the 3-step pipeline.

### Proposed Plan

**Option A (Recommended — SSOT discipline):** Enrich `markdown-generation` as the SSOT for the lint workflow
1. **Update `markdown-generation/SKILL.md`** — Restructure §2 as explicit 3-step pipeline; relax mandatory `--check` per script to optional preview mode; add a `scripts/fix-markdown-pipeline.py` convenience script
2. **Update `skill-factory/SKILL.md` §3** — Explicitly reference the 3-step pipeline by name
3. **No new standalone skill** — avoids SSOT split between `markdown-generation` (companion scripts) and a new skill (pipeline)

**Option B:** Create a new `general/markdown-lint-workflow` base skill that ships the pipeline script and references `markdown-generation` for companion scripts

I recommend **Option A** because:
- `markdown-generation` already IS the SSOT for the lint workflow protocol and scripts
- Splitting the pipeline into a separate skill creates two SSOTs
- Following `markdown-generation/SKILL.md` line 158 ("convenience tools for the Verification Workflow"), a pipeline script fits naturally there

**Tool: question**

**Input:**
```json
{
  "questions": [
    {
      "question": "Option A: enrich markdown-generation as SSOT (Recommended), or Option B: create standalone markdown-lint-workflow skill?",
      "header": "Architecture choice",
      "options": [
        {
          "label": "Option A: Enrich markdown-generation (Recommended)",
          "description": "Add pipeline script + restructure §2 as 3-step pipeline in existing markdown-generation skill. No new skill. Best for SSOT discipline."
        },
        {
          "label": "Option B: New standalone skill",
          "description": "Create general/markdown-lint-workflow with pipeline script, referencing markdown-generation companion scripts."
        }
      ]
    }
  ]
}
```

**Output:**
```
User has answered your questions: "Option A: enrich markdown-generation as SSOT (Recommended), or Option B: create standalone markdown-lint-workflow skill?"="what is more reusable: md generation with linting, or separate md generation & linting skills (md generation will invoke linting after generation)". You can now continue with the user's answers in mind.
```

---

## Assistant (Build · Big Pickle · 66.4s)

_Thinking:_

The user is asking a deeper architectural question: what's more reusable?
- A) `markdown-generation` WITH linting (monolithic) — one skill that both generates AND lints markdown
- B) Separate skills: `markdown-generation` (generates) + `markdown-lint-workflow` (lints) — generation invokes linting after generating

This is a legitimate layering question. Let me think about it:

### If monolithic (markdown-generation includes linting workflow):
- **Pro**: Single skill to invoke. One import for "generate and lint my markdown."
- **Con**: What if someone wants to lint markdown WITHOUT generating it? E.g., a CI workflow that just lints existing files, or a skill that edits an existing .md and wants to lint it without generation.
- **Con**: The lint workflow is coupled to the generation context.

### If separated (markdown-generation generates, separate skill lints):
- **Pro**: `markdown-lint-workflow` is a pure utility — any skill, CI workflow, or agent can call it to lint any .md file.
- **Pro**: `markdown-generation` focuses on generation; linting is delegated.
- **Pro**: Maximum reusability — the lint skill can be consumed by skill-factory, CI, pre-commit hooks, other skills that edit markdown.
- **Con**: More skills to manage.
- **Con**: `markdown-generation` needs to know about and invoke the lint skill.

### The key question: what calls the lint workflow?
Looking at current consumers:
- `skill-factory` §3: "Run the Markdown Generation protocol to ensure 100% lint compliance" — this calls `markdown-generation` for linting
- CI workflows: `github-ci-markdown-lint` uses `markdownlint-cli2-action` directly — this doesn't use either skill
- Skills that edit .md files: they need linting after edits, but currently reference `markdownlint-cli2` or `markdown-generation`

If we separate:
- `markdown-generation` becomes purely about creating/generating markdown content
- `general/markdown-lint-workflow` owns the 3-step pipeline + convenience script
- `markdown-generation` would invoke the lint workflow after generation
- Other skills (edit existing .md) would invoke the lint workflow directly

This is cleaner layering! The lint workflow is a cross-cutting concern, not tied to generation.

But wait — `markdown-generation` also owns the companion scripts (wrap-long-lines.py, fix-table-separators.py, etc.). Are those part of "generation" or "linting"?

Looking at their purpose: they fix lint errors that `markdownlint-cli2 --fix` cannot fix. So they're part of the lint workflow, not generation.

If we separate, where do the companion scripts live?
- Option: Move them to `general/markdown-lint-workflow/scripts/`
- This creates a dependency: `markdown-generation` depends on `markdown-lint-workflow` for post-generation linting

Hmm, but companion scripts are about fixing formatting, not about generation. Their home should be in the lint skill.

Actually wait — the user asked "what is more reusable?" Let me think about reusability patterns:

**Pattern: markdown-generation calls markdown-lint-workflow after generation**
- Skills that generate markdown: call `markdown-generation` → automatically gets linted (markdown-generation invokes lint internally)
- Skills that edit markdown: call `markdown-lint-workflow` directly
- CI: uses `github-ci-markdown-lint` (already standalone)

**Pattern: markdown-generation includes linting**
- Skills that generate markdown: call `markdown-generation` → gets linted
- Skills that edit markdown: also call `markdown-generation` — but they don't need generation, just linting. Makes markdown-generation the gateway for ALL linting needs.
- But markdown-generation has generation-specific content (config init, sync check, fidelity verification) that's irrelevant when you just want to lint.

Option B (separate) is more reusable because:
1. The lint workflow can be used independently by ANY skill, CI, or pre-commit hook
2. The generation skill stays focused on generation
3. The companion scripts logically belong to "lint fixing" not "markdown generation"

But there's a practical concern: scripts like `wrap-long-lines.py` live in `markdown-generation/scripts/` right now. Moving them would be a lot of churn.

Better approach: keep scripts in `markdown-generation/scripts/` but have the lint skill invoke them from that path. This avoids moving files while still achieving separation.

Actually, let me just answer the user's question directly with my analysis.

Great question. Let me analyze the reusability tradeoff:

### If `markdown-generation` includes linting (monolithic)
- Skills that GENERATE markdown: call `markdown-generation` ✓
- Skills that EDIT existing .md (but don't generate): must call `markdown-generation` even though they don't need generation — the lint workflow is coupled to generation
- CI / pre-commit hooks: reference part of `markdown-generation` protocol

### If separated (`markdown-generation` + `general/markdown-lint-workflow`)
- `markdown-generation` generates AND hands off to lint skill after generation ✓
- Skills that EDIT existing .md: call `markdown-lint-workflow` directly — pure linting, no generation overhead ✓
- CI / pre-commit hooks: call `markdown-lint-workflow` directly ✓
- `skill-factory`: calls `markdown-lint-workflow` for post-draft linting (currently calls `markdown-generation`) ✓
- Companion scripts live in `markdown-lint-workflow/scripts/` since they're about fixing lint, not generating content ✓

**Separate is more reusable.** The lint workflow is a cross-cutting concern that many skills need (edit, generation, factory, CI). Coupling it to generation forces every lint consumer to pass through generation's context.

The companion scripts (`wrap-long-lines.py`, etc.) would move to `markdown-lint-workflow/scripts/` — they're lint fixers, not generators.

**Tool: question**

**Input:**
```json
{
  "questions": [
    {
      "question": "Proceed with Option B (separate skills)? This means:\n1. Create `general/markdown-lint-workflow` — owns the 3-step pipeline protocol + companion scripts + pipeline convenience script\n2. Move companion scripts from `markdown-generation/scripts/` to `markdown-lint-workflow/scripts/`\n3. Update `markdown-generation` to invoke `markdown-lint-workflow` after generation\n4. Update `skill-factory` §3 to reference `markdown-lint-workflow` instead of `markdown-generation` for linting",
      "options": [
        {
          "label": "Proceed",
          "description": "Create general/markdown-lint-workflow. Move companion scripts. Update references."
        },
        {
          "label": "Keep in markdown-generation",
          "description": "Keep companion scripts and lint workflow SSOT in markdown-generation. Simpler, less churn."
        }
      ],
      "header": "Architecture decision"
    }
  ]
}
```

**Output:**
```
User has answered your questions: "Proceed with Option B (separate skills)? This means:
1. Create `general/markdown-lint-workflow` — owns the 3-step pipeline protocol + companion scripts + pipeline convenience script
2. Move companion scripts from `markdown-generation/scripts/` to `markdown-lint-workflow/scripts/`
3. Update `markdown-generation` to invoke `markdown-lint-workflow` after generation
4. Update `skill-factory` §3 to reference `markdown-lint-workflow` instead of `markdown-generation` for linting"="Proceed". You can now continue with the user's answers in mind.
```

---

## Assistant (Build · Big Pickle · 18.3s)

_Thinking:_

OK, the user wants to proceed with Option B. Let me plan the implementation in detail.

The implementation plan:

1. **Create `general/markdown-lint-workflow/`** with:
   - `SKILL.md` — documents the 3-step pipeline protocol
   - `scripts/` — directory for companion scripts
   - `AGENTS.md` — companion bridge

2. **Move companion scripts** from `markdown-generation/scripts/` to `markdown-lint-workflow/scripts/`:
   - `fix-table-separators.py`
   - `wrap-long-lines.py`
   - `fix-fenced-code-language.py`
   - `fix-container-fence.py`
   - `fix-emphasis-as-heading.py`
   - `fix-list-style.py`
   - `fix-heading-spacing.py`
   
3. **Create pipeline convenience script** `scripts/fix-markdown-pipeline.py` in `markdown-lint-workflow/scripts/`

4. **Update `markdown-generation/SKILL.md`**:
   - Remove §2 steps 3-6 (lint workflow), replace with "Run markdown-lint-workflow protocol"
   - Remove §3 (Companion Scripts) — redirect to `markdown-lint-workflow`
   - Keep what's unique to generation: config init, sync check, fidelity verification, anchor validation, relative-links rule
   - Add cross-reference to `markdown-lint-workflow`

5. **Update `skill-factory/SKILL.md`**:
   - §3 Markdown Audit: reference `markdown-lint-workflow` instead of `markdown-generation`

6. **Update other skills** that reference the lint workflow or companion scripts

7. **Register in root AGENTS.md**

8. **Update `markdown-generation/AGENTS.md`** companion bridge

9. **Run lint on all edited files**

Let me now think about the exact content of `general/markdown-lint-workflow/SKILL.md`:

The 3-step pipeline:
1. **Auto-Fix**: `markdownlint-cli2 --fix <file_path>`
2. **Companion Scripts**: Run in §3.1 order
3. **Manual Fix**: Fix remaining semantic/structural errors
4. **Final Audit**: `markdownlint-cli2 <file_path>` (verify clean)

Wait, the user said 3 steps: (1) --fix, (2) companion scripts, (3) manual fix. The final audit is implicit (you check after manual fixes). Let me keep it simple and follow the user's stated 3 steps, with audit as the verification gate.

Actually, re-reading the user's original description:
- step 1: run markdownlint-cli2 --fix
- step 2: run companion scripts
- step 3: manual fix

Step 3 "manual fix" includes the audit check — fix what's left.

So the pipeline is:
1. `markdownlint-cli2 --fix`
2. Companion scripts in order
3. Manual fix + final audit
4. Optional: list-indent-consistency check

Now, about the `--check` requirement: In the new skill, I should make `--check` optional (not mandatory per script). The pipeline script runs scripts directly; agents can dry-run individual scripts if they want.

Let me also think about the pipeline convenience script:

```python
#!/usr/bin/env python3
"""
fix-markdown-pipeline.py — Run the full 3-step markdown lint fix pipeline.

Usage: python3 fix-markdown-pipeline.py <file.md> [<file.md> ...]

Pipeline:
1. markdownlint-cli2 --fix <file>
2. Run companion scripts (§3.1 order)
3. Report remaining errors for manual fix
"""

import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent

SCRIPTS_ORDER = [
    ("fix-table-separators.py", []),
    ("fix-fenced-code-language.py", []),
    ("fix-container-fence.py", []),
    ("wrap-long-lines.py", ["--max", "120"]),
    ("fix-emphasis-as-heading.py", []),
    ("fix-list-style.py", []),
    ("fix-heading-spacing.py", []),
]

def main():
    files = sys.argv[1:]
    if not files:
        print("Usage: python3 fix-markdown-pipeline.py <file.md> [...]")
        sys.exit(1)

    # Step 1: markdownlint-cli2 --fix
    print("=== Step 1: markdownlint-cli2 --fix ===")
    r = subprocess.run(["markdownlint-cli2", "--fix"] + files, capture_output=True, text=True)
    if r.stdout:
        print(r.stdout)
    if r.stderr:
        print(r.stderr, file=sys.stderr)

    # Step 2: companion scripts
    print("\n=== Step 2: Companion scripts ===")
    for script_name, extra_args in SCRIPTS_ORDER:
        script_path = SCRIPTS_DIR / script_name
        if not script_path.exists():
            print(f"[SKIP] {script_name} — not found")
            continue
        print(f"\n--- {script_name} ---")
        r = subprocess.run([sys.executable, str(script_path)] + extra_args + files, capture_output=True, text=True)
        if r.stdout:
            print(r.stdout)
        if r.stderr:
            print(r.stderr, file=sys.stderr)
        if r.returncode != 0:
            print(f"[WARN] {script_name} exited with code {r.returncode}")

    # Step 3: audit
    print("\n=== Step 3: Final audit ===")
    r = subprocess.run(["markdownlint-cli2"] + files, capture_output=True, text=True)
    if r.stdout:
        print("Remaining issues:")
        print(r.stdout)
        sys.exit(1)
    else:
        print("Clean!")
        sys.exit(0)

if __name__ == "__main__":
    main()
```

Wait, but the companion scripts may print output that's just informational. The exit code matters more. And `markdownlint-cli2 --fix` returns 0 even when there are remaining unfixable issues — you need to run `markdownlint-cli2` (without --fix) to check.

Let me adjust: after --fix and companion scripts, run `markdownlint-cli2` audit. If there are remaining issues, print them and exit non-zero.

Also, I need to think about the pipeline script's location. It should be in `general/markdown-lint-workflow/scripts/fix-markdown-pipeline.py`. It references other scripts in the same directory.

Now let me think about what stays in `markdown-generation/SKILL.md` after the split:

**Keep in markdown-generation:**
- §1: Config initialization (`.markdownlint.jsonc`) — unique to generation
- §2: Verification Workflow — but step 3-6 become "Run markdown-lint-workflow protocol"
- §3: Companion Scripts — REMOVE (moved to markdown-lint-workflow)
- §4: Anchor validation / relative links — unique to generation
- §5: (what's next?)

Let me re-read markdown-generation full content to plan the split precisely.

Actually, I already read lines 76-180. Let me read the beginning and end.

Good choice. Let me read the full `markdown-generation` skill to plan the split precisely.

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/SKILL.md",
  "limit": 75
}
```

**Output:**
```
<path>/Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/SKILL.md</path>
<type>file</type>
<content>
1: ---
2: name: markdown-generation
3: description: Industrial protocol for generating lint-compliant, high-fidelity markdown documentation.
4: category: Documentation-Standards
5: ---
6: 
7: # Markdown Generation Skill (v1)
8: 
9: This skill provides a standardized protocol for generating Markdown that complies with the **Industrial standard**
10: (120-character line limit) and passes `markdownlint-cli2` (markdown linting CLI tool) audits.
11: 
12: ***
13: 
14: ## 1. Core Syntax Standards
15: 
16: Every generated file MUST adhere to these absolute constraints:
17: 
18: ### 1.1 Line Length (MD013)
19: 
20: - **Limit**: 120 characters per line.
21: - **Exception**: Long URLs and file paths that cannot be broken. Use **Reference-style links** at the bottom of the
22:   document to resolve length violations for URLs.
23: - **Wrapping**: Proactively wrap descriptions and YAML blocks to stay under the limit.
24: 
25: ### 1.2 Layout & Tables (MD060)
26: 
27: - **Table Alignment**: Use mathematically perfect aligned pipes (`|`).
28: - **Cell Spacing**: One mandatory space padding on both sides of every pipe (` | content | `).
29: - **Blank Lines**: Headers, lists, and code blocks MUST be surrounded by blank lines.
30: 
31: ### 1.3 Frontmatter
32: 
33: - **Rules/Skills**: Use the triple-dash block (`---`) as defined in [ai-rule-standardization-rules.md](../../../ai-agent-rules/ai-rule-standardization-rules.md).
34: - **General Docs**: Use the HTML comment block (`<!-- title: ... -->`) for indexing.
35: 
36: ### 1.4 Cross-Reference Links & Anchors
37: 
38: The `markdownlint-cli2` tool validates anchors via **MD051 - Link fragments should be valid**.
39: 
40: - **Anchor Format**: For header `### Step 1 — Deep Change Analysis`, the anchor is `#step-1-deep-change-analysis`
41: - **Generation Rule**: Convert header to lowercase, replace spaces and `—` (em dash) with dashes (`-`)
42: - **Verification**: Run `markdownlint-cli2` - it will catch broken anchor errors (MD051)
43: - **Best Practice**: Always use anchors when linking to headers within skill/rule files
44: 
45: ### 1.5 Path Verification
46: 
47: #### Default (CLI-Only)
48: 
49: - **Anchor**: Enforced by MD051 (built-in)
50: - **File Path**: NOT enforced - run manual verification:
51:     - `ls -la <path>` to confirm target exists
52:     - From `skills/<skill>/`: `ls ../<sibling-skill>/SKILL.md`
53:     - From `skills/<skill>/`: `ls ../../../ai-agent-rules/<rule>.md`
54: 
55: #### With Node.js Custom Rules (If Available)
56: 
57: Install and configure:
58: 
59: ```bash
60: npm install --save-dev markdownlint-rule-relative-links
61: ```
62: 
63: Add to `.markdownlint-cli2.jsonc` (NOT `.markdownlint.jsonc`):
64: 
65: ```jsonc
66: {
67:     "customRules": ["markdownlint-rule-relative-links"],
68:     "config": {
69:         "relative-links": { "root_path": "." }
70:     }
71: }
72: ```
73: 
74: Then both anchors AND file paths validated automatically.
75: 

(Showing lines 1-75 of 275. Use offset=76 to continue.)
</content>

<system-reminder>
Instructions from: /Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/AGENTS.md
# AGENTS.md (Markdown Generation)

Refer to [SKILL.md](./SKILL.md) and [markdown-generation-rules.md](../../../ai-agent-rules/markdown-generation-rules.md) for the active operational protocol for generating lint-compliant documentation.

## Mandates

- **Line Length**: 120-character limit (MD013).
- **Auto-Fix**: Mandatory use of `markdownlint-cli2 --fix` before submission.
- **Zero Angle Brackets**: Escaping all `<` and `>` tags in technical context.

</system-reminder>
```

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/SKILL.md",
  "offset": 181
}
```

**Output:**
```
<path>/Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/SKILL.md</path>
<type>file</type>
<content>
181: > base skill, then re-run the `markdownlint-cli2` audit before staging.
182: 
183: ### 3.2 Known `markdownlint-cli2 --fix` Caveats
184: 
185: **`markdownlint-cli2 --fix` corrupts bare closing fences.** When it encounters
186: a fenced code block without a language tag (\`\`\`), the built-in `MD040` fix
187: attaches a `text` language tag to **every** \`\`\` line — including the
188: closing fence — producing a broken construct:
189: 
190: ````text
191: ```text
192: code here
193: ```text
194: ````
195: 
196: **Resolution:** Do NOT use `markdownlint-cli2 --fix` for MD040. Instead, run
197: `fix-fenced-code-language.py` which correctly tracks open/close fence state
198: and strips any language tag from closing fences. If `--fix` has already been
199: applied, `fix-fenced-code-language.py` will repair the damage.
200: 
201: ***
202: 
203: ## 4. Related Rules
204: 
205: - **SSOT**: [markdown-generation-rules.md](../../../ai-agent-rules/markdown-generation-rules.md)
206: - **Formatting Protocol**: [ai-rule-standardization-rules.md](../../../ai-agent-rules/ai-rule-standardization-rules.md)
207: 
208: ***
209: 
210: ## 5. CI Integration
211: 
212: ### 5.1 Pipeline Script Execution Order
213: 
214: When automating lint fixing in a CI pipeline or pre-commit hook, run the
215: companion scripts in the order defined in §3.1. The pipeline MUST NOT use
216: `markdownlint-cli2 --fix` for MD040 (use `fix-fenced-code-language.py`
217: instead) per the caveat in §3.2.
218: 
219: Recommended one-shot invocation from the repo root:
220: 
221: ```bash
222: python3 .agents/skills/markdown-generation/scripts/fix-table-separators.py \
223:   --check file.md
224: python3 .agents/skills/markdown-generation/scripts/fix-fenced-code-language.py \
225:   --check file.md
226: python3 .agents/skills/markdown-generation/scripts/wrap-long-lines.py \
227:   --max 120 --check file.md
228: python3 .agents/skills/markdown-generation/scripts/fix-emphasis-as-heading.py \
229:   --check file.md
230: python3 .agents/skills/markdown-generation/scripts/fix-list-style.py \
231:   --check file.md
232: python3 .agents/skills/markdown-generation/scripts/fix-heading-spacing.py \
233:   --check file.md
234: ```
235: 
236: Drop `--check` to apply changes in-place.
237: 
238: ### 5.2 YAML Frontmatter Validation
239: 
240: YAML frontmatter `description` values that contain colons followed by
241: YAML-reserved tokens (e.g., `resetMocks: true`) cause downstream parsers
242: (VS Code preview, `markdownlint-cli2`) to misinterpret the colon as a new
243: YAML key opening.
244: 
245: **Rule:** If a `description` value contains any colon (`:`) that is not
246: trailing whitespace or a URL scheme (`https://`), wrap the entire value in
247: double quotes (`"..."`). Bare unquoted descriptions containing internal
248: colons are FORBIDDEN.
249: 
250: **Correct:**
251: 
252: ```yaml
253: ---
254: description: "Repository-specific composer that uses the generic ai-suite skill for debugging missing toolbar features"
255: ---
256: ```
257: 
258: **Incorrect:**
259: 
260: ```yaml
261: ---
262: description: Repository-specific composer that uses the generic ai-suite skill for debugging missing toolbar features
263: ---
264: ```
265: 
266: The difference is invisible in most Markdown renderers but causes silent
267: YAML parse failures in editor preview panes and schema validators.
268: 
269: ### 5.3 Lint Gate
270: 
271: Every skill authored via the Skill Factory (`skill-factory`) MUST pass the
272: full Verification Workflow (§2) including the companion-script pipeline
273: (§3.1) before it is considered complete. The factory's Post-Drafting
274: Checklist (§3) is the SSOT for the gating criteria; this section is the
275: SSOT for the technical execution order.

(End of file - total 275 lines)
</content>
```

---

## Assistant (Build · Big Pickle · 23.0s)

_Thinking:_

Now I have the full picture of `markdown-generation/SKILL.md`. Let me plan what stays and what moves:

**Stays in `markdown-generation/SKILL.md`:**
- §1: Core Syntax Standards (line length, tables, frontmatter, anchors, paths)
- §2: Verification Workflow — BUT steps 3-7 (lint workflow) replaced with "Run the markdown-lint-workflow protocol"
- §4: Related Rules
- §5.2: YAML Frontmatter Validation (unique to generation)
- §5.3: Lint Gate (updated to reference `markdown-lint-workflow`)

**Moves to `general/markdown-lint-workflow/SKILL.md`:**
- §2 steps 3-6: The full lint fix pipeline (--fix → companion scripts → manual → audit)
- §3: Companion Scripts and their execution order (§3.1)
- §3.2: Known `markdownlint-cli2 --fix` Caveats
- §5.1: Pipeline Script Execution Order (will become the pipeline convenience script)

Remaining question: the anchor validation (MD051) and relative links are tightly coupled to `markdownlint-cli2` — but they're about *content correctness* not *lint fixing*. They should stay in `markdown-generation` as part of the content standard.

Now let me plan the `general/markdown-lint-workflow/SKILL.md` content:

```markdown
---
name: markdown-lint-workflow
description: Three-step markdown lint fix pipeline — run markdownlint-cli2 --fix, companion scripts, manual fix.
category: General
---

# Markdown Lint Workflow (v1)

This skill provides the protocol for fixing markdown lint issues in any project.
It is consumed by `markdown-generation` (post-generation linting), `skill-factory`
(post-drafting verification), and any skill that edits `.md` files.

***

## 1. The 3-Step Pipeline

Before finalizing ANY markdown file, run:

### Step 1: Auto-Fix

```bash
markdownlint-cli2 --fix <file_path>
```

Run from the project root. Use paths relative to the project root — absolute
paths can cause the tool to silently find 0 files.

Caveat: `markdownlint-cli2 --fix` corrupts bare closing fences for MD040 (adds
`text` to the closing ```). Do NOT use `--fix` for MD040 — companion script
Step 2 handles it.

### Step 2: Companion Scripts

Run ALL companion scripts from §2 in the required order. These handle patterns
that `markdownlint-cli2 --fix` does not resolve (line length, table alignment,
fence language tags, etc.).

### Step 3: Manual Fix + Audit

Fix remaining semantic/structural errors (e.g., heading increments, broken
cross-references, anchor mismatches). Then verify:

```bash
markdownlint-cli2 <file_path>
```

Zero errors means the file is lint-compliant.

---

## 2. Companion Scripts

This skill ships seven helper scripts under [`scripts/`](scripts/) ...

(Same as current markdown-generation §3)

### 2.1 Execution Order

... (same as 3.1)

### 2.2 Known `markdownlint-cli2 --fix` Caveats

... (same as 3.2)

---

## 3. Convenience Pipeline Script

This skill ships [`scripts/fix-markdown-pipeline.py`](scripts/fix-markdown-pipeline.py)
which wraps the entire 3-step pipeline into a single invocation:

```bash
python3 .agents/skills/general/markdown-lint-workflow/scripts/fix-markdown-pipeline.py <file.md> [<file.md> ...]
```

The script:
1. Runs `markdownlint-cli2 --fix`
2. Runs all companion scripts in §2.1 order
3. Runs final `markdownlint-cli2` audit
4. Exits 0 if clean, non-zero with remaining-error report

---

## 4. Cross-References

- `markdown-generation` — consumes this skill for post-generation linting
- `skill-factory` §3 — consumes this skill for post-drafting linting
- `list-indent-consistency` — check continuation-line indent after lint-fix
```

OK, now I need to also plan the AGENTS.md for the new skill, and the updates to other files.

Let me write out the implementation plan.

Files to create:
1. `.agents/skills/general/markdown-lint-workflow/SKILL.md` — new skill
2. `.agents/skills/general/markdown-lint-workflow/AGENTS.md` — companion bridge
3. `.agents/skills/general/markdown-lint-workflow/scripts/fix-markdown-pipeline.py` — pipeline script

Files to modify:
4. `.agents/skills/markdown-generation/SKILL.md` — remove §3, update §2 and §5
5. `.agents/skills/markdown-generation/AGENTS.md` — update to reference new workflow
6. `.agents/skills/skill-factory/SKILL.md` — §3 update reference
7. Root `.agents/skills/AGENTS.md` — register new skill
8. Various skills that hardcode markdownlint commands

Files to move:
9. `.agents/skills/markdown-generation/scripts/*.py` → `.agents/skills/general/markdown-lint-workflow/scripts/*.py`

Let me now implement all of this. I should present the plan first, then wait for approval.

Actually, I already asked and got approval to proceed. Let me just present the full plan and then execute.

Wait — the planning rules say I should present the plan for approval before executing. I asked about the architecture choice and got approval, but I should present the full implementation plan.

Actually, let me re-read: the user said "Continue if you have next steps" — meaning they're OK with me proceeding. And I asked the architecture question and they said "Proceed." So I have approval to go ahead.

Let me now create the plan and start implementing.

Actually, let me be careful about the order of operations:

1. First, I need to create the new skill directory and scripts
2. Then move the existing scripts
3. Then update the old skill to reference the new one
4. Then update other skills that reference markdown-generation for linting

But moving scripts while updating references in the same operation could be tricky. Let me think about this more carefully.

If I move `wrap-long-lines.py` etc. from `markdown-generation/scripts/` to `markdown-lint-workflow/scripts/`, then:
- `markdown-generation/SKILL.md` references to `scripts/xxx.py` become broken
- I need to update those references or remove them
- Any skill that references `markdown-generation/scripts/xxx.py` also breaks

Let me check who references the scripts:

Actually, within `markdown-generation/SKILL.md`, the scripts are referenced as `scripts/fix-xxx.py` (relative path within the skill directory). If I move them, these relative references break.

In the CI integration section (§5.1), the paths are absolute `python3 .agents/skills/markdown-generation/scripts/fix-table-separators.py ...`

So after the move, all these paths need to be updated.

And `fix-markdown-pipeline.py` in the new skill will reference scripts in its own directory: `SCRIPTS_DIR = Path(__file__).parent` — so it works out of the box.

OK let me just proceed with the implementation. I'll create the new skill first, then move scripts, then update references.

Actually wait, Git operations: The user hasn't mentioned committing. But moving files between directories would be done with `git mv` if we want to preserve history, or just `mv` if not. Since this is a refactoring and the files are small scripts, plain `mv` is fine.

Let me start implementing.

Implementation plan approved. Let me now execute step by step.

**Tool: todowrite**

**Input:**
```json
{
  "todos": [
    {
      "content": "Create general/markdown-lint-workflow/ directory structure",
      "status": "in_progress",
      "priority": "high"
    },
    {
      "content": "Write general/markdown-lint-workflow/SKILL.md — 3-step pipeline protocol",
      "status": "pending",
      "priority": "high"
    },
    {
      "content": "Create fix-markdown-pipeline.py convenience script",
      "status": "pending",
      "priority": "high"
    },
    {
      "content": "Move companion scripts from markdown-generation/scripts/ to markdown-lint-workflow/scripts/",
      "status": "pending",
      "priority": "high"
    },
    {
      "content": "Update markdown-generation/SKILL.md — remove §3, update §2 and §5 to delegate",
      "status": "pending",
      "priority": "high"
    },
    {
      "content": "Update markdown-generation/AGENTS.md — reference new workflow",
      "status": "pending",
      "priority": "medium"
    },
    {
      "content": "Update skill-factory §3 — reference markdown-lint-workflow",
      "status": "pending",
      "priority": "high"
    },
    {
      "content": "Register new skill in root AGENTS.md",
      "status": "pending",
      "priority": "medium"
    },
    {
      "content": "Create AGENTS.md companion bridge for new skill",
      "status": "pending",
      "priority": "medium"
    },
    {
      "content": "Run lint on all edited files",
      "status": "pending",
      "priority": "medium"
    }
  ]
}
```

**Output:**
```
[
  {
    "content": "Create general/markdown-lint-workflow/ directory structure",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "Write general/markdown-lint-workflow/SKILL.md — 3-step pipeline protocol",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Create fix-markdown-pipeline.py convenience script",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Move companion scripts from markdown-generation/scripts/ to markdown-lint-workflow/scripts/",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Update markdown-generation/SKILL.md — remove §3, update §2 and §5 to delegate",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Update markdown-generation/AGENTS.md — reference new workflow",
    "status": "pending",
    "priority": "medium"
  },
  {
    "content": "Update skill-factory §3 — reference markdown-lint-workflow",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Register new skill in root AGENTS.md",
    "status": "pending",
    "priority": "medium"
  },
  {
    "content": "Create AGENTS.md companion bridge for new skill",
    "status": "pending",
    "priority": "medium"
  },
  {
    "content": "Run lint on all edited files",
    "status": "pending",
    "priority": "medium"
  }
]
```

---

## Assistant (Build · Big Pickle · 3.8s)

_Thinking:_

Let me start by creating the directory structure and listing existing scripts to move.

**Tool: bash**

**Input:**
```json
{
  "command": "mkdir -p /Users/dk/lab-data/ai-suite/.agents/skills/general/markdown-lint-workflow/scripts",
  "description": "Create new skill directory structure"
}
```

**Output:**
```
(no output)
```

**Tool: bash**

**Input:**
```json
{
  "command": "ls /Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/scripts/",
  "description": "List existing companion scripts to move"
}
```

**Output:**
```
fix-container-fence.py
fix-emphasis-as-heading.py
fix-fenced-code-language.py
fix-heading-spacing.py
fix-list-style.py
fix-table-separators.py
wrap-long-lines.py

```

---

## Assistant (Build · Big Pickle · 4.5s)

_Thinking:_

Now let me create the new SKILL.md and the pipeline script. I'll write them both in parallel.

**Tool: todowrite**

**Input:**
```json
{
  "todos": [
    {
      "priority": "high",
      "content": "Create general/markdown-lint-workflow/ directory structure",
      "status": "completed"
    },
    {
      "priority": "high",
      "content": "Write general/markdown-lint-workflow/SKILL.md — 3-step pipeline protocol",
      "status": "in_progress"
    },
    {
      "priority": "high",
      "content": "Create fix-markdown-pipeline.py convenience script",
      "status": "in_progress"
    },
    {
      "priority": "high",
      "content": "Move companion scripts from markdown-generation/scripts/ to markdown-lint-workflow/scripts/",
      "status": "pending"
    },
    {
      "priority": "high",
      "content": "Update markdown-generation/SKILL.md — remove §3, update §2 and §5 to delegate",
      "status": "pending"
    },
    {
      "priority": "medium",
      "content": "Update markdown-generation/AGENTS.md — reference new workflow",
      "status": "pending"
    },
    {
      "priority": "high",
      "content": "Update skill-factory §3 — reference markdown-lint-workflow",
      "status": "pending"
    },
    {
      "priority": "medium",
      "content": "Register new skill in root AGENTS.md",
      "status": "pending"
    },
    {
      "priority": "medium",
      "content": "Create AGENTS.md companion bridge for new skill",
      "status": "pending"
    },
    {
      "priority": "medium",
      "content": "Run lint on all edited files",
      "status": "pending"
    }
  ]
}
```

**Output:**
```
[
  {
    "content": "Create general/markdown-lint-workflow/ directory structure",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Write general/markdown-lint-workflow/SKILL.md — 3-step pipeline protocol",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "Create fix-markdown-pipeline.py convenience script",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "Move companion scripts from markdown-generation/scripts/ to markdown-lint-workflow/scripts/",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Update markdown-generation/SKILL.md — remove §3, update §2 and §5 to delegate",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Update markdown-generation/AGENTS.md — reference new workflow",
    "status": "pending",
    "priority": "medium"
  },
  {
    "content": "Update skill-factory §3 — reference markdown-lint-workflow",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Register new skill in root AGENTS.md",
    "status": "pending",
    "priority": "medium"
  },
  {
    "content": "Create AGENTS.md companion bridge for new skill",
    "status": "pending",
    "priority": "medium"
  },
  {
    "content": "Run lint on all edited files",
    "status": "pending",
    "priority": "medium"
  }
]
```

---

## Assistant (Build · Big Pickle · 19.6s)

_Thinking:_

Let me create the SKILL.md and pipeline script. Per AGENTS.md §2, for large writes I should use heredocs, not the create tool. Both files are well under the thresholds though (< 10 KB, < 100 lines), so the create tool is acceptable per the carve-out. But the rule says "for whole-file authoring use cat > file <<'EOF' ... EOF" so let me use heredocs.

Actually wait — the SKILL.md will be roughly 250-300 lines, which is > 100 lines. The pipeline script will be ~80 lines. So:
- SKILL.md: use heredoc (large write)
- Pipeline script: use heredoc or create (borderline, but heredoc is safer)

Let me use heredocs for both.

**Tool: bash**

**Input:**
```json
{
  "description": "Write markdown-lint-workflow SKILL.md",
  "command": "cat > /Users/dk/lab-data/ai-suite/.agents/skills/general/markdown-lint-workflow/SKILL.md << 'SKILL_EOF'\n---\nname: markdown-lint-workflow\ndescription: Three-step pipeline for fixing markdown lint issues — markdownlint-cli2 --fix, companion scripts, manual fix + audit.\ncategory: General\n---\n\n# Markdown Lint Workflow (v1)\n\nThis skill provides the three-step pipeline protocol for fixing markdown lint\nissues in any project. It is consumed by:\n\n- **`markdown-generation`** — post-generation linting\n- **`skill-factory` §3** — post-drafting linting\n- **Any skill that edits `.md` files** — pre-submission lint verification\n\nThe companion scripts under [`scripts/`](scripts/) handle patterns that\n`markdownlint-cli2 --fix` does not resolve (line length, table alignment, fence\nlanguage tags, list style, heading spacing, etc.).\n\n***\n\n## 1. The 3-Step Pipeline\n\nBefore finalizing ANY markdown file, run these steps in order:\n\n### Step 1: Auto-Fix\n\n```bash\nmarkdownlint-cli2 --fix <file_path>\n```\n\n- Run from the project root where `.markdownlint.jsonc` lives.\n- Use paths **relative** to the project root — absolute paths can cause the\n  tool to silently find 0 files (`Linting: 0 file(s)`) and do nothing.\n\n**Caveat:** `markdownlint-cli2 --fix` corrupts bare closing fences for MD040.\nDo NOT rely on `--fix` for MD040 — Step 2 handles it correctly. See §2.2.\n\n### Step 2: Companion Scripts\n\nRun ALL companion scripts from [§2](#2-companion-scripts) in the\n[required execution order](#21-execution-order). Each script accepts\n`--check` for a dry-run preview; omit `--check` to apply changes in-place.\n\n```bash\n# Quick overview of available scripts:\npython3 .agents/skills/general/markdown-lint-workflow/scripts/fix-table-separators.py file.md\npython3 .agents/skills/general/markdown-lint-workflow/scripts/fix-fenced-code-language.py file.md\npython3 .agents/skills/general/markdown-lint-workflow/scripts/fix-container-fence.py file.md\npython3 .agents/skills/general/markdown-lint-workflow/scripts/wrap-long-lines.py --max 120 file.md\npython3 .agents/skills/general/markdown-lint-workflow/scripts/fix-emphasis-as-heading.py file.md\npython3 .agents/skills/general/markdown-lint-workflow/scripts/fix-list-style.py file.md\npython3 .agents/skills/general/markdown-lint-workflow/scripts/fix-heading-spacing.py file.md\n```\n\nFor a single automated invocation, see the\n[Convenience Pipeline Script](#3-convenience-pipeline-script).\n\n### Step 3: Manual Fix + Final Audit\n\nFix any remaining semantic or structural errors (e.g., heading increments,\nbroken cross-references, anchor mismatches). Then verify:\n\n```bash\nmarkdownlint-cli2 <file_path>\n```\n\nZero errors means the file is lint-compliant.\n\n***\n\n## 2. Companion Scripts\n\nThis skill ships seven helper scripts under\n[`scripts/`](scripts/) for one-shot lint fixes:\n\n- [`fix-table-separators.py`](scripts/fix-table-separators.py) — scans for\n  compact table separators (`|---|---|`) and rewrites them with proper spacing\n  (`| --- | --- |`) to satisfy MD060. Use `--check` for dry-run.\n- [`wrap-long-lines.py`](scripts/wrap-long-lines.py) — wraps prose lines\n  exceeding the configured `--max` width (default 120) while preserving code\n  blocks, tables, YAML frontmatter, and list structure. Use `--check` for\n  dry-run.\n- [`fix-fenced-code-language.py`](scripts/fix-fenced-code-language.py) — adds\n  a default language tag (default `text`) to bare opening fenced code blocks\n  to satisfy MD040. Properly undoes `markdownlint-cli2 --fix` damage that\n  attaches `text` to closing fences. Use `--default <lang>` to override the\n  language (default: `text`). Use `--check` for dry-run.\n- [`fix-emphasis-as-heading.py`](scripts/fix-emphasis-as-heading.py) — strips\n  emphasis markers (`*...*`, `_..._`) from lines that are standalone\n  emphasis-as-heading paragraphs to satisfy MD036. Use `--check` for dry-run.\n- [`fix-list-style.py`](scripts/fix-list-style.py) — converts asterisk\n  unordered list markers (`*`) to dash style (`-`) to satisfy MD004.\n  Use `--check` for dry-run.\n- [`fix-heading-spacing.py`](scripts/fix-heading-spacing.py) — inserts a blank\n  line before headings that lack one to satisfy MD022. Skips YAML frontmatter\n  and code blocks. Use `--check` for dry-run.\n- [`fix-container-fence.py`](scripts/fix-container-fence.py) — detects fenced\n  code blocks whose outer fence uses 4+ backtick markers with content containing\n  inner ``` fences (markdown-syntax examples). Adds a `text` language tag to\n  the opening fence to satisfy MD040 without breaking the inner fences. Use\n  `--check` for dry-run.\n\n### 2.1 Execution Order\n\nWhen running multiple fix scripts, the following order is **REQUIRED** to avoid\nre-introducing lint errors:\n\n1. `fix-table-separators.py`\n2. `fix-fenced-code-language.py` (MUST run BEFORE `wrap-long-lines.py` — fence\n   lines may exceed the width limit and wrapping a fence line before its\n   language tag has been added produces a broken fence)\n3. `fix-container-fence.py`\n4. `wrap-long-lines.py`\n5. `fix-emphasis-as-heading.py`\n6. `fix-list-style.py`\n7. `fix-heading-spacing.py`\n\n> **Indent drift after editing / lint-fix.** After running the §2.1 pipeline,\n> verify that continuation-line indent in edited regions matches the original\n> file's siblings. The fix scripts and `markdownlint-cli2 --fix` can leave\n> whitespace drift on adjacent lines. Delegate detection and repair to the\n> [`list-indent-consistency`](../list-indent-consistency/SKILL.md)\n> base skill, then re-run the audit before staging.\n\n### 2.2 Known `markdownlint-cli2 --fix` Caveats\n\n**`markdownlint-cli2 --fix` corrupts bare closing fences.** When it encounters\na fenced code block without a language tag (\\`\\`\\`), the built-in `MD040` fix\nattaches a `text` language tag to **every** \\`\\`\\` line — including the\nclosing fence — producing a broken construct:\n\n```text\ntext\ncode here\ntext\n```\n\n**Resolution:** Do NOT use `markdownlint-cli2 --fix` for MD040. Instead, run\n`fix-fenced-code-language.py` which correctly tracks open/close fence state\nand strips any language tag from closing fences. If `--fix` has already been\napplied, `fix-fenced-code-language.py` will repair the damage.\n\n***\n\n## 3. Convenience Pipeline Script\n\nThis skill ships\n[`scripts/fix-markdown-pipeline.py`](scripts/fix-markdown-pipeline.py) which\nwraps the entire 3-step pipeline into a single invocation:\n\n```bash\npython3 .agents/skills/general/markdown-lint-workflow/scripts/fix-markdown-pipeline.py <file.md> [<file.md> ...]\n```\n\nThe script:\n\n1. Runs `markdownlint-cli2 --fix` (Step 1)\n2. Runs all companion scripts in §2.1 order (Step 2)\n3. Runs final `markdownlint-cli2` audit (Step 3 verification)\n4. Exits 0 if clean, non-zero with remaining-error report\n\nThis is equivalent to executing the full manual workflow but guarantees\ncorrect script ordering and avoids the `--check` per-script overhead.\n\n***\n\n## 4. Cross-References\n\n- [`markdown-generation`](../markdown-generation/SKILL.md) — consumes this\n  skill for post-generation linting\n- [`skill-factory`](../skill-factory/SKILL.md) §3 — Post-Drafting Checklist\n  references this skill for linting\n- [`list-indent-consistency`](../list-indent-consistency/SKILL.md) — detect\n  and repair indent drift after fix scripts\n- [`markdownlint-cli2`](https://github.com/DavidAnson/markdownlint-cli2) —\n  the underlying lint tool\nSKILL_EOF"
}
```

**Output:**
```
(no output)
```

---

## Assistant (Build · Big Pickle · 197.7s)

_Thinking:_

Good, now let me create the pipeline convenience script.

**Tool: bash**

**Input:**
```json
{
  "description": "Write fix-markdown-pipeline.py script",
  "command": "cat > /Users/dk/lab-data/ai-suite/.agents/skills/general/markdown-lint-workflow/scripts/fix-markdown-pipeline.py << 'PYEOF'\n#!/usr/bin/env python3\n\"\"\"Run the full 3-step markdown lint fix pipeline on one or more .md files.\n\nUsage:\n    python3 fix-markdown-pipeline.py <file.md> [<file.md> ...]\n\nPipeline:\n    1. markdownlint-cli2 --fix  (auto-fix what it can)\n    2. Companion scripts in §2.1 order  (fix what --fix cannot)\n    3. markdownlint-cli2 audit  (verify clean; exit non-zero if issues remain)\n\nExit status:\n    0  — all files lint-clean\n    1  — one or more files have remaining lint issues\n\"\"\"\n\nimport subprocess\nimport sys\nfrom pathlib import Path\n\nSCRIPTS_DIR = Path(__file__).resolve().parent\n\nSCRIPTS_ORDER = [\n    (\"fix-table-separators.py\", []),\n    (\"fix-fenced-code-language.py\", []),\n    (\"fix-container-fence.py\", []),\n    (\"wrap-long-lines.py\", [\"--max\", \"120\"]),\n    (\"fix-emphasis-as-heading.py\", []),\n    (\"fix-list-style.py\", []),\n    (\"fix-heading-spacing.py\", []),\n]\n\n\ndef run(args, label):\n    print(f\"[{label}] {' '.join(args)}\")\n    r = subprocess.run(args, capture_output=True, text=True)\n    if r.stdout:\n        print(r.stdout.rstrip())\n    if r.stderr:\n        print(r.stderr.rstrip(), file=sys.stderr)\n    return r\n\n\ndef main():\n    files = sys.argv[1:]\n    if not files:\n        print(\"Usage: python3 fix-markdown-pipeline.py <file.md> [<file.md> ...]\")\n        sys.exit(1)\n\n    total_ok = True\n\n    print(\"=\" * 60)\n    print(\"STEP 1: markdownlint-cli2 --fix\")\n    print(\"=\" * 60)\n    r = run([\"markdownlint-cli2\", \"--fix\"] + files, \"step-1\")\n    if r.returncode != 0:\n        print(\"[INFO] --fix finished (non-zero exit is normal when unfixable issues remain)\")\n\n    print(\"\\n\" + \"=\" * 60)\n    print(\"STEP 2: Companion scripts\")\n    print(\"=\" * 60)\n    for script_name, extra_args in SCRIPTS_ORDER:\n        script_path = SCRIPTS_DIR / script_name\n        if not script_path.exists():\n            print(f\"  [SKIP] {script_name} — not found at {script_path}\")\n            continue\n        r = run([sys.executable, str(script_path)] + extra_args + files, f\"  {script_name}\")\n        if r.returncode != 0:\n            print(f\"  [WARN] {script_name} exited with code {r.returncode}\")\n\n    print(\"\\n\" + \"=\" * 60)\n    print(\"STEP 3: Final audit\")\n    print(\"=\" * 60)\n    r = run([\"markdownlint-cli2\"] + files, \"audit\")\n    if r.returncode == 0:\n        print(\"\\nAll files lint-clean.\")\n        sys.exit(0)\n    else:\n        print(\"\\nRemaining lint issues found. See output above.\")\n        sys.exit(1)\n\n\nif __name__ == \"__main__\":\n    main()\nPYEOF\nchmod +x /Users/dk/lab-data/ai-suite/.agents/skills/general/markdown-lint-workflow/scripts/fix-markdown-pipeline.py"
}
```

**Output:**
```
(no output)
```

---

## Assistant (Build · Big Pickle · 5.1s)

_Thinking:_

Good. Now let me move the companion scripts and update the existing skills. Let me move the scripts first using git mv to preserve history.

Now move the companion scripts and update all referencing files.

**Tool: todowrite**

**Input:**
```json
{
  "todos": [
    {
      "priority": "high",
      "content": "Create general/markdown-lint-workflow/ directory structure",
      "status": "completed"
    },
    {
      "priority": "high",
      "content": "Write general/markdown-lint-workflow/SKILL.md — 3-step pipeline protocol",
      "status": "completed"
    },
    {
      "priority": "high",
      "content": "Create fix-markdown-pipeline.py convenience script",
      "status": "completed"
    },
    {
      "priority": "high",
      "content": "Move companion scripts from markdown-generation/scripts/ to markdown-lint-workflow/scripts/",
      "status": "in_progress"
    },
    {
      "priority": "high",
      "content": "Update markdown-generation/SKILL.md — remove §3, update §2 and §5 to delegate",
      "status": "pending"
    },
    {
      "priority": "medium",
      "content": "Update markdown-generation/AGENTS.md — reference new workflow",
      "status": "pending"
    },
    {
      "priority": "high",
      "content": "Update skill-factory §3 — reference markdown-lint-workflow",
      "status": "pending"
    },
    {
      "priority": "medium",
      "content": "Register new skill in root AGENTS.md",
      "status": "pending"
    },
    {
      "priority": "medium",
      "content": "Create AGENTS.md companion bridge for new skill",
      "status": "pending"
    },
    {
      "priority": "medium",
      "content": "Run lint on all edited files",
      "status": "pending"
    }
  ]
}
```

**Output:**
```
[
  {
    "content": "Create general/markdown-lint-workflow/ directory structure",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Write general/markdown-lint-workflow/SKILL.md — 3-step pipeline protocol",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Create fix-markdown-pipeline.py convenience script",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Move companion scripts from markdown-generation/scripts/ to markdown-lint-workflow/scripts/",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "Update markdown-generation/SKILL.md — remove §3, update §2 and §5 to delegate",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Update markdown-generation/AGENTS.md — reference new workflow",
    "status": "pending",
    "priority": "medium"
  },
  {
    "content": "Update skill-factory §3 — reference markdown-lint-workflow",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Register new skill in root AGENTS.md",
    "status": "pending",
    "priority": "medium"
  },
  {
    "content": "Create AGENTS.md companion bridge for new skill",
    "status": "pending",
    "priority": "medium"
  },
  {
    "content": "Run lint on all edited files",
    "status": "pending",
    "priority": "medium"
  }
]
```

---

## Assistant (Build · Big Pickle · 8.5s)

_Thinking:_

Let me move the scripts using git mv to preserve history, then update the skill files.

**Tool: bash**

**Input:**
```json
{
  "description": "Move companion scripts with git mv",
  "command": "cd /Users/dk/lab-data/ai-suite && git mv .agents/skills/markdown-generation/scripts/fix-container-fence.py .agents/skills/general/markdown-lint-workflow/scripts/ && git mv .agents/skills/markdown-generation/scripts/fix-emphasis-as-heading.py .agents/skills/general/markdown-lint-workflow/scripts/ && git mv .agents/skills/markdown-generation/scripts/fix-fenced-code-language.py .agents/skills/general/markdown-lint-workflow/scripts/ && git mv .agents/skills/markdown-generation/scripts/fix-heading-spacing.py .agents/skills/general/markdown-lint-workflow/scripts/ && git mv .agents/skills/markdown-generation/scripts/fix-list-style.py .agents/skills/general/markdown-lint-workflow/scripts/ && git mv .agents/skills/markdown-generation/scripts/fix-table-separators.py .agents/skills/general/markdown-lint-workflow/scripts/ && git mv .agents/skills/markdown-generation/scripts/wrap-long-lines.py .agents/skills/general/markdown-lint-workflow/scripts/"
}
```

**Output:**
```
(no output)
```

---

## Assistant (Build · Big Pickle · 3.3s)

_Thinking:_

Good, the scripts have been moved. Now let me check if `markdown-generation/scripts/` is now empty and should be cleaned up. Let me also check if there's a `markdown-generation/scripts/__init__.py` or any other files.

**Tool: bash**

**Input:**
```json
{
  "description": "Check if scripts dir is now empty",
  "command": "ls -la /Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/scripts/"
}
```

**Output:**
```
total 0
drwxr-xr-x@ 2 dk  staff   64 Jun 23 09:02 .
drwxr-xr-x@ 5 dk  staff  160 Jun  9 14:32 ..

```

---

## Assistant (Build · Big Pickle · 24.9s)

_Thinking:_

Empty. Now I need to update `markdown-generation/SKILL.md` to remove §3, update §2, and update §5 to delegate to `markdown-lint-workflow`.

Let me now plan the changes to `markdown-generation/SKILL.md`:

**§2 (lines 76-98):** Keep steps 1-2 (config init, sync check) — those are unique to generation. Replace steps 3-7 with a single step: "Run the Markdown Lint Workflow protocol."

**§3 (lines 101-200):** Remove entirely — companion scripts have moved to `markdown-lint-workflow`. But keep the cross-reference between §3 Removed and the new skill.

Actually wait — should I remove the section entirely or replace it with a delegation reference? The skill-factory protocol says to keep relative links working. Let me replace §3 with a delegation reference.

**§5.1 (lines 212-236):** Replace with delegation to `markdown-lint-workflow` pipeline.

**§5.3 (lines 270-275):** Update reference from §3.1 to §2.1 of `markdown-lint-workflow`.

Let me now make all the edits to `markdown-generation/SKILL.md`.

Now update `markdown-generation/SKILL.md`. I'll replace §2's lint steps with delegation, remove §3 (companion scripts moved), and update §5.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/SKILL.md",
  "oldString": "## 2. Verification Workflow\n\nBefore finalizing ANY markdown file, the agent MUST:\n\n1. **Config Initialization**: If the project lacks a `.markdownlint.jsonc` file, the agent\n   MUST initialize it using rules from the reference config (`../../../.markdownlint.jsonc`\n   relative to this skill file), incorporating the `MD013` 120-character line length exception.\n2. **Sync Check**: Ensure `.vscode/settings.json` contains `\"markdownlint.configFile\": \".markdownlint.jsonc\"` to\n   synchronize the IDE extension with the project's Industrial standard.\n3. **Auto-Fix**: Run `markdownlint-cli2 --fix <file_path>` from the project root.\n   Use paths **relative** to the project root — absolute paths can cause the\n   tool to silently find 0 files (`Linting: 0 file(s)`) and do nothing.\n4. **Dry-Run Companion Scripts**: Before applying any companion script from §3,\n   MUST run with `--check` first to preview changes, review the proposed diffs,\n   then re-run without `--check` to apply. Dry-run before apply is MANDATORY\n   for every companion script.\n5. **Audit Check**: Run `markdownlint-cli2 <file_path>`.\n6. **Manual Correction**: Fix any remaining semantic or structural errors (e.g., heading increments).\n7. **Fidelity Verification**: Ensure the \"Fidelity Mandate\" (no loss of user technical specifics) is upheld during\n   formatting.",
  "newString": "## 2. Verification Workflow\n\nBefore finalizing ANY markdown file, the agent MUST:\n\n1. **Config Initialization**: If the project lacks a `.markdownlint.jsonc` file, the agent\n   MUST initialize it using rules from the reference config (`../../../.markdownlint.jsonc`\n   relative to this skill file), incorporating the `MD013` 120-character line length exception.\n2. **Sync Check**: Ensure `.vscode/settings.json` contains `\"markdownlint.configFile\": \".markdownlint.jsonc\"` to\n   synchronize the IDE extension with the project's Industrial standard.\n3. **Run Markdown Lint Workflow**: Execute the full\n   **[Markdown Lint Workflow](../general/markdown-lint-workflow/SKILL.md)** 3-step pipeline\n   on the file:\n   - Step 1: `markdownlint-cli2 --fix`\n   - Step 2: Companion scripts in execution order\n   - Step 3: Manual fix + final `markdownlint-cli2` audit\n4. **Fidelity Verification**: Ensure the \"Fidelity Mandate\" (no loss of user technical specifics) is upheld during\n   formatting."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 3.8s)

_Thinking:_

Now I need to replace §3 (Companion Scripts) with a delegation reference. The old §3 spans from line ~99 to line ~200 (approximately). Let me read the current state after the edit.

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/SKILL.md",
  "offset": 85,
  "limit": 125
}
```

**Output:**
```
<path>/Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/SKILL.md</path>
<type>file</type>
<content>
85: 2. **Sync Check**: Ensure `.vscode/settings.json` contains `"markdownlint.configFile": ".markdownlint.jsonc"` to
86:    synchronize the IDE extension with the project's Industrial standard.
87: 3. **Run Markdown Lint Workflow**: Execute the full
88:    **[Markdown Lint Workflow](../general/markdown-lint-workflow/SKILL.md)** 3-step pipeline
89:    on the file:
90:    - Step 1: `markdownlint-cli2 --fix`
91:    - Step 2: Companion scripts in execution order
92:    - Step 3: Manual fix + final `markdownlint-cli2` audit
93: 4. **Fidelity Verification**: Ensure the "Fidelity Mandate" (no loss of user technical specifics) is upheld during
94:    formatting.
95: 
96: ***
97: 
98: ## 3. Companion Scripts
99: 
100: This skill ships seven helper scripts under
101: [`scripts/`](scripts/) for one-shot lint fixes:
102: 
103: - [`fix-table-separators.py`](scripts/fix-table-separators.py) — scans for
104:   compact table separators (`|---|---|`) and rewrites them with proper spacing
105:   (`| --- | --- |`) to satisfy MD060. Use `--check` for dry-run.
106: - [`wrap-long-lines.py`](scripts/wrap-long-lines.py) — wraps prose lines
107:   exceeding the configured `--max` width (default 120) while preserving code
108:   blocks, tables, YAML frontmatter, and list structure. Use `--check` for
109:   dry-run.
110: - [`fix-fenced-code-language.py`](scripts/fix-fenced-code-language.py) — adds
111:   a default language tag (default `text`) to bare opening fenced code blocks
112:   to satisfy MD040. Properly undoes `markdownlint-cli2 --fix` damage that
113:   attaches `text` to closing fences. Use `--default <lang>` to override the
114:   language (default: `text`). Use `--check` for dry-run.
115: - [`fix-emphasis-as-heading.py`](scripts/fix-emphasis-as-heading.py) — strips
116:   emphasis markers (`*...*`, `_..._`) from lines that are standalone
117:   emphasis-as-heading paragraphs to satisfy MD036. Use `--check` for dry-run.
118: - [`fix-list-style.py`](scripts/fix-list-style.py) — converts asterisk
119:   unordered list markers (`*`) to dash style (`-`) to satisfy MD004.
120:   Use `--check` for dry-run.
121: - [`fix-heading-spacing.py`](scripts/fix-heading-spacing.py) — inserts a blank
122:   line before headings that lack one to satisfy MD022. Skips YAML frontmatter
123:   and code blocks. Use `--check` for dry-run.
124: - [`fix-container-fence.py`](scripts/fix-container-fence.py) — detects fenced
125:   code blocks whose outer fence uses 4+ backtick markers with content containing
126:   inner ``` fences (markdown-syntax examples). Adds a `text` language tag to
127:   the opening fence to satisfy MD040 without breaking the inner fences. Use
128:   `--check` for dry-run.
129: 
130: All seven scripts operate in-place on a list of file arguments.
131: 
132: ```bash
133: python3 scripts/fix-table-separators.py --check path/to/file.md
134: python3 scripts/fix-table-separators.py path/to/file.md
135: 
136: python3 scripts/wrap-long-lines.py --max 120 --check path/to/file.md
137: python3 scripts/wrap-long-lines.py --max 120 path/to/file.md
138: 
139: python3 scripts/fix-fenced-code-language.py --check path/to/file.md
140: python3 scripts/fix-fenced-code-language.py path/to/file.md
141: 
142: python3 scripts/fix-emphasis-as-heading.py --check path/to/file.md
143: python3 scripts/fix-emphasis-as-heading.py path/to/file.md
144: 
145: python3 scripts/fix-list-style.py --check path/to/file.md
146: python3 scripts/fix-list-style.py path/to/file.md
147: 
148: python3 scripts/fix-heading-spacing.py --check path/to/file.md
149: python3 scripts/fix-heading-spacing.py path/to/file.md
150: 
151: python3 scripts/fix-container-fence.py --check path/to/file.md
152: python3 scripts/fix-container-fence.py path/to/file.md
153: ```
154: 
155: These are convenience tools for the `## 2. Verification Workflow` step 3
156: (auto-fix) — they target patterns `markdownlint-cli2 --fix` does not resolve.
157: 
158: ### 3.1 Execution Order
159: 
160: When running multiple fix scripts, the following order is **REQUIRED** to avoid
161: re-introducing lint errors:
162: 
163: 1. `fix-table-separators.py`
164: 2. `fix-fenced-code-language.py` (MUST run BEFORE `wrap-long-lines.py` — fence
165:    lines may exceed the width limit and wrapping a fence line before its
166:    language tag has been added produces a broken fence)
167: 3. `fix-container-fence.py`
168: 4. `wrap-long-lines.py`
169: 5. `fix-emphasis-as-heading.py`
170: 6. `fix-list-style.py`
171: 7. `fix-heading-spacing.py`
172: 
173: > **Indent drift after editing / lint-fix.** After running the §3.1 pipeline,
174: > verify that continuation-line indent in edited regions matches the original
175: > file's siblings. `markdownlint-cli2 --fix` and companion scripts can leave
176: > whitespace drift on adjacent lines. Delegate detection and repair to the
177: > [`list-indent-consistency`](../general/list-indent-consistency/SKILL.md)
178: > base skill, then re-run the `markdownlint-cli2` audit before staging.
179: 
180: ### 3.2 Known `markdownlint-cli2 --fix` Caveats
181: 
182: **`markdownlint-cli2 --fix` corrupts bare closing fences.** When it encounters
183: a fenced code block without a language tag (\`\`\`), the built-in `MD040` fix
184: attaches a `text` language tag to **every** \`\`\` line — including the
185: closing fence — producing a broken construct:
186: 
187: ````text
188: ```text
189: code here
190: ```text
191: ````
192: 
193: **Resolution:** Do NOT use `markdownlint-cli2 --fix` for MD040. Instead, run
194: `fix-fenced-code-language.py` which correctly tracks open/close fence state
195: and strips any language tag from closing fences. If `--fix` has already been
196: applied, `fix-fenced-code-language.py` will repair the damage.
197: 
198: ***
199: 
200: ## 4. Related Rules
201: 
202: - **SSOT**: [markdown-generation-rules.md](../../../ai-agent-rules/markdown-generation-rules.md)
203: - **Formatting Protocol**: [ai-rule-standardization-rules.md](../../../ai-agent-rules/ai-rule-standardization-rules.md)
204: 
205: ***
206: 
207: ## 5. CI Integration
208: 
209: ### 5.1 Pipeline Script Execution Order

(Showing lines 85-209 of 272. Use offset=210 to continue.)
</content>
```

---

## Assistant (Build · Big Pickle · 26.4s)

_Thinking:_

Now I need to replace §3 (Companion Scripts) with a delegation reference. The old §3 goes from line 98 to line 198. Let me replace it all with a brief delegation section.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/SKILL.md",
  "oldString": "## 3. Companion Scripts\n\nThis skill ships seven helper scripts under\n[`scripts/`](scripts/) for one-shot lint fixes:\n\n- [`fix-table-separators.py`](scripts/fix-table-separators.py) — scans for\n  compact table separators (`|---|---|`) and rewrites them with proper spacing\n  (`| --- | --- |`) to satisfy MD060. Use `--check` for dry-run.\n- [`wrap-long-lines.py`](scripts/wrap-long-lines.py) — wraps prose lines\n  exceeding the configured `--max` width (default 120) while preserving code\n  blocks, tables, YAML frontmatter, and list structure. Use `--check` for\n  dry-run.\n- [`fix-fenced-code-language.py`](scripts/fix-fenced-code-language.py) — adds\n  a default language tag (default `text`) to bare opening fenced code blocks\n  to satisfy MD040. Properly undoes `markdownlint-cli2 --fix` damage that\n  attaches `text` to closing fences. Use `--default <lang>` to override the\n  language (default: `text`). Use `--check` for dry-run.\n- [`fix-emphasis-as-heading.py`](scripts/fix-emphasis-as-heading.py) — strips\n  emphasis markers (`*...*`, `_..._`) from lines that are standalone\n  emphasis-as-heading paragraphs to satisfy MD036. Use `--check` for dry-run.\n- [`fix-list-style.py`](scripts/fix-list-style.py) — converts asterisk\n  unordered list markers (`*`) to dash style (`-`) to satisfy MD004.\n  Use `--check` for dry-run.\n- [`fix-heading-spacing.py`](scripts/fix-heading-spacing.py) — inserts a blank\n  line before headings that lack one to satisfy MD022. Skips YAML frontmatter\n  and code blocks. Use `--check` for dry-run.\n- [`fix-container-fence.py`](scripts/fix-container-fence.py) — detects fenced\n  code blocks whose outer fence uses 4+ backtick markers with content containing\n  inner ``` fences (markdown-syntax examples). Adds a `text` language tag to\n  the opening fence to satisfy MD040 without breaking the inner fences. Use\n  `--check` for dry-run.\n\nAll seven scripts operate in-place on a list of file arguments.\n\n```bash\npython3 scripts/fix-table-separators.py --check path/to/file.md\npython3 scripts/fix-table-separators.py path/to/file.md\n\npython3 scripts/wrap-long-lines.py --max 120 --check path/to/file.md\npython3 scripts/wrap-long-lines.py --max 120 path/to/file.md\n\npython3 scripts/fix-fenced-code-language.py --check path/to/file.md\npython3 scripts/fix-fenced-code-language.py path/to/file.md\n\npython3 scripts/fix-emphasis-as-heading.py --check path/to/file.md\npython3 scripts/fix-emphasis-as-heading.py path/to/file.md\n\npython3 scripts/fix-list-style.py --check path/to/file.md\npython3 scripts/fix-list-style.py path/to/file.md\n\npython3 scripts/fix-heading-spacing.py --check path/to/file.md\npython3 scripts/fix-heading-spacing.py path/to/file.md\n\npython3 scripts/fix-container-fence.py --check path/to/file.md\npython3 scripts/fix-container-fence.py path/to/file.md\n```\n\nThese are convenience tools for the `## 2. Verification Workflow` step 3\n(auto-fix) — they target patterns `markdownlint-cli2 --fix` does not resolve.\n\n### 3.1 Execution Order\n\nWhen running multiple fix scripts, the following order is **REQUIRED** to avoid\nre-introducing lint errors:\n\n1. `fix-table-separators.py`\n2. `fix-fenced-code-language.py` (MUST run BEFORE `wrap-long-lines.py` — fence\n   lines may exceed the width limit and wrapping a fence line before its\n   language tag has been added produces a broken fence)\n3. `fix-container-fence.py`\n4. `wrap-long-lines.py`\n5. `fix-emphasis-as-heading.py`\n6. `fix-list-style.py`\n7. `fix-heading-spacing.py`\n\n> **Indent drift after editing / lint-fix.** After running the §3.1 pipeline,\n> verify that continuation-line indent in edited regions matches the original\n> file's siblings. `markdownlint-cli2 --fix` and companion scripts can leave\n> whitespace drift on adjacent lines. Delegate detection and repair to the\n> [`list-indent-consistency`](../general/list-indent-consistency/SKILL.md)\n> base skill, then re-run the `markdownlint-cli2` audit before staging.\n\n### 3.2 Known `markdownlint-cli2 --fix` Caveats\n\n**`markdownlint-cli2 --fix` corrupts bare closing fences.** When it encounters\na fenced code block without a language tag (\\`\\`\\`), the built-in `MD040` fix\nattaches a `text` language tag to **every** \\`\\`\\` line — including the\nclosing fence — producing a broken construct:\n\n````text\n```text\ncode here\n```text\n````\n\n**Resolution:** Do NOT use `markdownlint-cli2 --fix` for MD040. Instead, run\n`fix-fenced-code-language.py` which correctly tracks open/close fence state\nand strips any language tag from closing fences. If `--fix` has already been\napplied, `fix-fenced-code-language.py` will repair the damage.",
  "newString": "## 3. Lint Fix Protocol\n\nCompanion scripts and the full 3-step lint fix pipeline have moved to\n**[Markdown Lint Workflow](../general/markdown-lint-workflow/SKILL.md)**.\n\nThis skill delegates all lint-fix operations there. See that skill for:\n\n- The 7 companion scripts (with descriptions and usage)\n- Required execution order (table separators → fence language → wrap long\n  lines → ...)\n- Known `markdownlint-cli2 --fix` caveats (MD040 fence corruption)\n- The convenience pipeline script `fix-markdown-pipeline.py`"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 3.5s)

_Thinking:_

Now I need to update §5 (CI Integration). Let me read the current §5 after the edit.

**Tool: read**

**Input:**
```json
{
  "offset": 115,
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/SKILL.md",
  "limit": 85
}
```

**Output:**
```
<path>/Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/SKILL.md</path>
<type>file</type>
<content>
115: - **SSOT**: [markdown-generation-rules.md](../../../ai-agent-rules/markdown-generation-rules.md)
116: - **Formatting Protocol**: [ai-rule-standardization-rules.md](../../../ai-agent-rules/ai-rule-standardization-rules.md)
117: 
118: ***
119: 
120: ## 5. CI Integration
121: 
122: ### 5.1 Pipeline Script Execution Order
123: 
124: When automating lint fixing in a CI pipeline or pre-commit hook, run the
125: companion scripts in the order defined in §3.1. The pipeline MUST NOT use
126: `markdownlint-cli2 --fix` for MD040 (use `fix-fenced-code-language.py`
127: instead) per the caveat in §3.2.
128: 
129: Recommended one-shot invocation from the repo root:
130: 
131: ```bash
132: python3 .agents/skills/markdown-generation/scripts/fix-table-separators.py \
133:   --check file.md
134: python3 .agents/skills/markdown-generation/scripts/fix-fenced-code-language.py \
135:   --check file.md
136: python3 .agents/skills/markdown-generation/scripts/wrap-long-lines.py \
137:   --max 120 --check file.md
138: python3 .agents/skills/markdown-generation/scripts/fix-emphasis-as-heading.py \
139:   --check file.md
140: python3 .agents/skills/markdown-generation/scripts/fix-list-style.py \
141:   --check file.md
142: python3 .agents/skills/markdown-generation/scripts/fix-heading-spacing.py \
143:   --check file.md
144: ```
145: 
146: Drop `--check` to apply changes in-place.
147: 
148: ### 5.2 YAML Frontmatter Validation
149: 
150: YAML frontmatter `description` values that contain colons followed by
151: YAML-reserved tokens (e.g., `resetMocks: true`) cause downstream parsers
152: (VS Code preview, `markdownlint-cli2`) to misinterpret the colon as a new
153: YAML key opening.
154: 
155: **Rule:** If a `description` value contains any colon (`:`) that is not
156: trailing whitespace or a URL scheme (`https://`), wrap the entire value in
157: double quotes (`"..."`). Bare unquoted descriptions containing internal
158: colons are FORBIDDEN.
159: 
160: **Correct:**
161: 
162: ```yaml
163: ---
164: description: "Repository-specific composer that uses the generic ai-suite skill for debugging missing toolbar features"
165: ---
166: ```
167: 
168: **Incorrect:**
169: 
170: ```yaml
171: ---
172: description: Repository-specific composer that uses the generic ai-suite skill for debugging missing toolbar features
173: ---
174: ```
175: 
176: The difference is invisible in most Markdown renderers but causes silent
177: YAML parse failures in editor preview panes and schema validators.
178: 
179: ### 5.3 Lint Gate
180: 
181: Every skill authored via the Skill Factory (`skill-factory`) MUST pass the
182: full Verification Workflow (§2) including the companion-script pipeline
183: (§3.1) before it is considered complete. The factory's Post-Drafting
184: Checklist (§3) is the SSOT for the gating criteria; this section is the
185: SSOT for the technical execution order.

(End of file - total 185 lines)
</content>
```

---

## Assistant (Build · Big Pickle · 15.1s)

_Thinking:_

Now I need to update §5.1 to delegate to `markdown-lint-workflow`'s pipeline script instead of listing individual `markdown-generation/scripts/` commands. I also need to update §5.3 to reference `markdown-lint-workflow §2.1`.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/SKILL.md",
  "oldString": "### 5.1 Pipeline Script Execution Order\n\nWhen automating lint fixing in a CI pipeline or pre-commit hook, run the\ncompanion scripts in the order defined in §3.1. The pipeline MUST NOT use\n`markdownlint-cli2 --fix` for MD040 (use `fix-fenced-code-language.py`\ninstead) per the caveat in §3.2.\n\nRecommended one-shot invocation from the repo root:\n\n```bash\npython3 .agents/skills/markdown-generation/scripts/fix-table-separators.py \\\n  --check file.md\npython3 .agents/skills/markdown-generation/scripts/fix-fenced-code-language.py \\\n  --check file.md\npython3 .agents/skills/markdown-generation/scripts/wrap-long-lines.py \\\n  --max 120 --check file.md\npython3 .agents/skills/markdown-generation/scripts/fix-emphasis-as-heading.py \\\n  --check file.md\npython3 .agents/skills/markdown-generation/scripts/fix-list-style.py \\\n  --check file.md\npython3 .agents/skills/markdown-generation/scripts/fix-heading-spacing.py \\\n  --check file.md\n```\n\nDrop `--check` to apply changes in-place.",
  "newString": "### 5.1 Pipeline Script\n\nWhen automating lint fixing in a CI pipeline or pre-commit hook, use the\nconvenience pipeline script from\n**[Markdown Lint Workflow](../general/markdown-lint-workflow/SKILL.md#3-convenience-pipeline-script)**:\n\n```bash\npython3 .agents/skills/general/markdown-lint-workflow/scripts/fix-markdown-pipeline.py \\\n  file.md\n```\n\nThis runs `markdownlint-cli2 --fix`, then all companion scripts in execution\norder, then a final audit — all in one invocation. For individual companion\nscript usage, see the\n[Markdown Lint Workflow skill](../general/markdown-lint-workflow/SKILL.md#2-companion-scripts)."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 11.1s)

_Thinking:_

Now update §5.3 Lint Gate to reference the new skill.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/SKILL.md",
  "oldString": "### 5.3 Lint Gate\n\nEvery skill authored via the Skill Factory (`skill-factory`) MUST pass the\nfull Verification Workflow (§2) including the companion-script pipeline\n(§3.1) before it is considered complete. The factory's Post-Drafting\nChecklist (§3) is the SSOT for the gating criteria; this section is the\nSSOT for the technical execution order.",
  "newString": "### 5.3 Lint Gate\n\nEvery skill authored via the Skill Factory (`skill-factory`) MUST pass the\nfull Verification Workflow (§2) including the\n**[Markdown Lint Workflow](../general/markdown-lint-workflow/SKILL.md)** 3-step\npipeline before it is considered complete. The factory's Post-Drafting\nChecklist (§3) is the SSOT for the gating criteria."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 9.9s)

_Thinking:_

Good. Now update `markdown-generation/AGENTS.md` to reference the new workflow, and update `skill-factory/SKILL.md §3`.

Now update `markdown-generation/AGENTS.md` and `skill-factory/SKILL.md`.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/markdown-generation/AGENTS.md",
  "oldString": "## Mandates\n\n- **Line Length**: 120-character limit (MD013).\n- **Auto-Fix**: Mandatory use of `markdownlint-cli2 --fix` before submission.\n- **Zero Angle Brackets**: Escaping all `<` and `>` tags in technical context.",
  "newString": "## Mandates\n\n- **Line Length**: 120-character limit (MD013).\n- **Lint Fix**: Run the full 3-step\n  **[Markdown Lint Workflow](../general/markdown-lint-workflow/SKILL.md)** pipeline\n  before submission (Step 1: `markdownlint-cli2 --fix`, Step 2: companion scripts\n  in execution order, Step 3: manual fix + audit).\n- **Zero Angle Brackets**: Escaping all `<` and `>` tags in technical context."
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Big Pickle · 7.1s)

_Thinking:_

Now update `skill-factory/SKILL.md §3`. I need to replace the reference from `markdown-generation` to `markdown-lint-workflow` for the linting protocol.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/skill-factory/SKILL.md",
  "oldString": "- **Markdown Audit**: Run the **[Markdown Generation](../markdown-generation/SKILL.md)\n  protocol to ensure 100% lint compliance. The agent MUST re-read\n  every generated/edited markdown file and fix any stray tool-output tags (`</content>`, `<parameter ...>`), duplicated\n  lines, broken or multi-line links, unclosed fences, and embedded absolute paths BEFORE presenting the artifact.\n  Linting MUST be performed by invoking the **`markdownlint-cli2`** binary directly\n  (e.g., `markdownlint-cli2 --fix <path>` then `markdownlint-cli2 <path>`); using `npx markdownlint-cli2` is\n  **FORBIDDEN** per\n  **[Markdown Generation Rules §5](../../../ai-agent-rules/markdown-generation-rules.md#5-validation-rules-markdownlint-cli2)**.\n  Recommended fix-script execution order is documented in\n  **[Markdown Generation §3.1](../markdown-generation/SKILL.md#31-execution-order)**.",
  "newString": "- **Markdown Audit**: Run the\n  **[Markdown Lint Workflow](../general/markdown-lint-workflow/SKILL.md)**\n  3-step pipeline (Step 1: `markdownlint-cli2 --fix`, Step 2: companion scripts\n  in execution order, Step 3: manual fix + audit) to ensure 100% lint compliance.\n  The agent MUST re-read every generated/edited markdown file and fix any stray\n  tool-output tags (`</content>`, `<parameter ...>`), duplicated lines, broken or\n  multi-line links, unclosed fences, and embedded absolute paths BEFORE presenting\n  the artifact.\n  Linting MUST be performed by invoking the **`markdownlint-cli2`** binary directly\n  (e.g., `markdownlint-cli2 --fix <path>` then `markdownlint-cli2 <path>`); using `npx markdownlint-cli2` is\n  **FORBIDDEN** per\n  **[Markdown Generation Rules §5](../../../ai-agent-rules/markdown-generation-rules.md#5-validation-rules-markdownlint-cli2)**.\n  Recommended fix-script execution order is documented in\n  **[Markdown Lint Workflow §2.1](../general/markdown-lint-workflow/SKILL.md#21-execution-order)**."
}
```

**Error:**
```
Could not find oldString in the file. It must match exactly, including whitespace, indentation, and line endings.
```

---

## Assistant (Build · Big Pickle · 3.3s)

_Thinking:_

The edit failed because the indentation didn't match. Let me read the exact content of skill-factory §3 around the Markdown Audit section.

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/skill-factory/SKILL.md",
  "offset": 330,
  "limit": 20
}
```

**Output:**
```
<path>/Users/dk/lab-data/ai-suite/.agents/skills/skill-factory/SKILL.md</path>
<type>file</type>
<content>
330: - **Contextual Hosting**: Documentation (logs, artifacts) MUST reside in the component's `docs/` folder.
331: - **Fidelity Check**: Verify that no technical details from the source conversation were summarized or lost.
332: - **Markdown Audit**: Run the **[Markdown Generation](../markdown-generation/SKILL.md)**
333:   protocol to ensure 100% lint compliance. The agent MUST re-read
334:   every generated/edited markdown file and fix any stray tool-output tags (`</content>`, `<parameter ...>`), duplicated
335:   lines, broken or multi-line links, unclosed fences, and embedded absolute paths BEFORE presenting the artifact.
336:   Linting MUST be performed by invoking the **`markdownlint-cli2`** binary directly
337:   (e.g., `markdownlint-cli2 --fix <path>` then `markdownlint-cli2 <path>`); using `npx markdownlint-cli2` is
338:   **FORBIDDEN** per
339:   **[Markdown Generation Rules §5](../../../ai-agent-rules/markdown-generation-rules.md#5-validation-rules-markdownlint-cli2)**.
340:   Recommended fix-script execution order is documented in
341:   **[Markdown Generation §3.1](../markdown-generation/SKILL.md#31-execution-order)**.
342: - **Bridge Audit**: Confirm `<skill-dir>/AGENTS.md` exists, carries NO YAML frontmatter (no leading `---` block), contains the five required sections from §2.3.2 (`# <Skill> — Companion Bridge` / `## Purpose` / `## When This Skill Applies` / `## Operational Procedure` / `## Cross-References`), and is within the 40–120 line size guidance from §2.3.5. A skill with no bridge file is INCOMPLETE.
343: - **Registration Audit**: Confirm the new skill row was inserted into the root `AGENTS.md` skills table at the correct
344:   alphabetical (case-insensitive) position by the **Skill** column, NOT appended to the end. Spot-check the rows
345:   immediately above and below to verify the sort order holds.
346: - **Organization Audit**: Confirm the new skill's placement obeys the domain taxonomy in
347:   [`skill-library-domain-grouping` §1](../general/skill-library-domain-grouping/SKILL.md#1-domain-taxonomy).
348:   The parent folder MUST have ≤10 items; if the addition would exceed the threshold, the agent
349:   MUST propose a sub-grouping before adding.

(Showing lines 330-349 of 710. Use offset=350 to continue.)
</content>

<system-reminder>
Instructions from: /Users/dk/lab-data/ai-suite/.agents/skills/skill-factory/AGENTS.md
# AGENTS.md (Skill Factory)

Refer to [SKILL.md](./SKILL.md) for the active operational protocol for generating "Skill-First" AI Agent capabilities with absolute data fidelity and zero-leak portability.

## Mandates

- **Fidelity Scan**: Mandatory identification of all user specifics before drafting.
- **Zero Omission**: Technical workflows and dependencies MUST NOT be summarized or removed.
- **Redaction Integration**: Automatically apply the **Redaction & Portability** skill to all factory-generated output.
- **Invocation Convention** (mandate #7): Skill docs MUST use simplified invocation forms; run `scripts/verify-doc-invocations.py` as a post-creation audit step.

</system-reminder>
```

---

## Assistant (Build · Big Pickle · 6.6s)

_Thinking:_

Now I can see the exact whitespace. The indentation uses two spaces per level. Let me match it exactly.

**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/skill-factory/SKILL.md",
  "oldString": "- **Markdown Audit**: Run the **[Markdown Generation](../markdown-generation/SKILL.md)\n  protocol to ensure 100% lint compliance. The agent MUST re-read\n  every generated/edited markdown file and fix any stray tool-output tags (`</content>`, `<parameter ...>`), duplicated\n  lines, broken or multi-line links, unclosed fences, and embedded absolute paths BEFORE presenting the artifact.\n  Linting MUST be performed by invoking the **`markdownlint-cli2`** binary directly\n  (e.g., `markdownlint-cli2 --fix <path>` then `markdownlint-cli2 <path>`); using `npx markdownlint-cli2` is\n  **FORBIDDEN** per\n  **[Markdown Generation Rules §5](../../../ai-agent-rules/markdown-generation-rules.md#5-validation-rules-markdownlint-cli2)**.\n  Recommended fix-script execution order is documented in\n  **[Markdown Generation §3.1](../markdown-generation/SKILL.md#31-execution-order)**.",
  "newString": "- **Markdown Audit**: Run the\n  **[Markdown Lint Workflow](../general/markdown-lint-workflow/SKILL.md)**\n  3-step pipeline (Step 1: `markdownlint-cli2 --fix`, Step 2: companion scripts\n  in execution order, Step 3: manual fix + audit) to ensure 100% lint compliance.\n  The agent MUST re-read every generated/edited markdown file and fix any stray\n  tool-output tags (`</content>`, `<parameter ...>`), duplicated lines, broken or\n  multi-line links, unclosed fences, and embedded absolute paths BEFORE presenting\n  the artifact.\n  Linting MUST be performed by invoking the **`markdownlint-cli2`** binary directly\n  (e.g., `markdownlint-cli2 --fix <path>` then `markdownlint-cli2 <path>`); using `npx markdownlint-cli2` is\n  **FORBIDDEN** per\n  **[Markdown Generation Rules §5](../../../ai-agent-rules/markdown-generation-rules.md#5-validation-rules-markdownlint-cli2)**.\n  Recommended fix-script execution order is documented in\n  **[Markdown Lint Workflow §2.1](../general/markdown-lint-workflow/SKILL.md#21-execution-order)**."
}
```

**Error:**
```
Could not find oldString in the file. It must match exactly, including whitespace, indentation, and line endings.
```

---

## Assistant (Build · Big Pickle · 174.4s)

_Thinking:_

The issue is likely trailing whitespace or invisible characters. Let me try using the bash tool with python to do a precise replacement, since the edit tool is struggling with whitespace matching.

**Tool: bash**

**Input:**
```json
{
  "command": "python3 - <<'PYTHON_EOF'\nfilepath = \"/Users/dk/lab-data/ai-suite/.agents/skills/skill-factory/SKILL.md\"\nwith open(filepath, \"r\") as f:\n    content = f.read()\n\nold = \"\"\"- **Markdown Audit**: Run the **[Markdown Generation](../markdown-generation/SKILL.md)\n  protocol to ensure 100% lint compliance. The agent MUST re-read\n  every generated/edited markdown file and fix any stray tool-output tags (`</content>`, `<parameter ...>`), duplicated\n  lines, broken or multi-line links, unclosed fences, and embedded absolute paths BEFORE presenting the artifact.\n  Linting MUST be performed by invoking the **`markdownlint-cli2`** binary directly\n  (e.g., `markdownlint-cli2 --fix <path>` then `markdownlint-cli2 <path>`); using `npx markdownlint-cli2` is\n  **FORBIDDEN** per\n  **[Markdown Generation Rules §5](../../../ai-agent-rules/markdown-generation-rules.md#5-validation-rules-markdownlint-cli2)**.\n  Recommended fix-script execution order is documented in\n  **[Markdown Generation §3.1](../markdown-generation/SKILL.md#31-execution-order)**.\"\"\"\n\nnew = \"\"\"- **Markdown Audit**: Run the\n  **[Markdown Lint Workflow](../general/markdown-lint-workflow/SKILL.md)**\n  3-step pipeline (Step 1: `markdownlint-cli2 --fix`, Step 2: companion scripts\n  in execution order, Step 3: manual fix + audit) to ensure 100% lint compliance.\n  The agent MUST re-read every generated/edited markdown file and fix any stray\n  tool-output tags (`</content>`, `<parameter ...>`), duplicated lines, broken or\n  multi-line links, unclosed fences, and embedded absolute paths BEFORE presenting\n  the artifact.\n  Linting MUST be performed by invoking the **`markdownlint-cli2`** binary directly\n  (e.g., `markdownlint-cli2 --fix <path>` then `markdownlint-cli2 <path>`); using `npx markdownlint-cli2` is\n  **FORBIDDEN** per\n  **[Markdown Generation Rules §5](../../../ai-agent-rules/markdown-generation-rules.md#5-validation-rules-markdownlint-cli2)**.\n  Recommended fix-script execution order is documented in\n  **[Markdown Lint Workflow §2.1](../general/markdown-lint-workflow/SKILL.md#21-execution-order)**.\"\"\"\n\nif old in content:\n    content = content.replace(old, new)\n    with open(filepath, \"w\") as f:\n        f.write(content)\n    print(\"SUCCESS: replacement applied\")\nelse:\n    print(\"FAIL: old string not found\")\n    # Debug: find approximate location\n    idx = content.find(\"- **Markdown Audit**\")\n    if idx >= 0:\n        print(f\"Found at position {idx}\")\n        print(repr(content[idx:idx+70]))\n        print(\"...\")\n        print(repr(content[idx+300:idx+370]))\nPYTHON_EOF",
  "description": "Replace skill-factory markdown audit section"
}
```

**Output:**
```
FAIL: old string not found
Found at position 26303
'- **Markdown Audit**: Run the **[Markdown Generation](../markdown-gene'
...
'line links, unclosed fences, and embedded absolute paths BEFORE presen'

```

---

## Assistant (Build · Big Pickle · 23.2s)

_Thinking:_

The old string is not matching exactly. The issue is probably trailing spaces or different line endings. Let me read the exact bytes around the Markdown Audit section.

**Tool: bash**

**Input:**
```json
{
  "command": "python3 - <<'PYTHON_EOF'\nfilepath = \"/Users/dk/lab-data/ai-suite/.agents/skills/skill-factory/SKILL.md\"\nwith open(filepath, \"rb\") as f:\n    content = f.read()\n\nidx = content.find(b\"- **Markdown Audit**\")\nif idx >= 0:\n    # Show raw bytes including line endings around the section\n    end = content.find(b\"- **Bridge Audit**\", idx)\n    section = content[idx:end]\n    print(repr(section))\nPYTHON_EOF",
  "description": "Read exact bytes of markdown audit section"
}
```

**Output:**
```
b'- **Markdown Audit**: Run the **[Markdown Generation](../markdown-generation/SKILL.md)**\n  protocol to ensure 100% lint compliance. The agent MUST re-read\n  every generated/edited markdown file and fix any stray tool-output tags (`</content>`, `<parameter ...>`), duplicated\n  lines, broken or multi-line links, unclosed fences, and embedded absolute paths BEFORE presenting the artifact.\n  Linting MUST be performed by invoking the **`markdownlint-cli2`** binary directly\n  (e.g., `markdownlint-cli2 --fix <path>` then `markdownlint-cli2 <path>`); using `npx markdownlint-cli2` is\n  **FORBIDDEN** per\n  **[Markdown Generation Rules \xc2\xa75](../../../ai-agent-rules/markdown-generation-rules.md#5-validation-rules-markdownlint-cli2)**.\n  Recommended fix-script execution order is documented in\n  **[Markdown Generation \xc2\xa73.1](../markdown-generation/SKILL.md#31-execution-order)**.\n'

```

---

## Assistant (Build · Big Pickle · 8.5s)

---

## User

Continue

---

## Assistant (Build · Nemotron 3 Ultra 550B A55B · 186.6s)

_Thinking:_

Now I see the exact bytes - there's a `§` character that's encoded as `\xc2\xa7` (UTF-8) in the bytes. Let me use this exact string for the replacement.

Found it - the `§` characters are UTF-8 encoded. Let me do the replacement with the exact bytes.


**Tool: bash**

**Input:**
```json
{
  "command": "python3 - <<'PYTHON_EOF'\nfilepath = \"/Users/dk/lab-data/ai-suite/.agents/skills/skill-factory/SKILL.md\"\nwith open(filepath, \"r\") as f:\n    content = f.read()\n\nold = \"\"\"- **Markdown Audit**: Run the **[Markdown Generation](../markdown-generation/SKILL.md)**\n  protocol to ensure 100% lint compliance. The agent MUST re-read\n  every generated/edited markdown file and fix any stray tool-output tags (`</content>`, `<parameter ...>`), duplicated\n  lines, broken or multi-line links, unclosed fences, and embedded absolute paths BEFORE presenting the artifact.\n  Linting MUST be performed by invoking the **`markdownlint-cli2`** binary directly\n  (e.g., `markdownlint-cli2 --fix <path>` then `markdownlint-cli2 <path>`); using `npx markdownlint-cli2` is\n  **FORBIDDEN** per\n  **[Markdown Generation Rules §5](../../../ai-agent-rules/markdown-generation-rules.md#5-validation-rules-markdownlint-cli2)**.\n  Recommended fix-script execution order is documented in\n  **[Markdown Generation §3.1](../markdown-generation/SKILL.md#31-execution-order)**.\"\"\"\n\nnew = \"\"\"- **Markdown Audit**: Run the\n  **[Markdown Lint Workflow](../general/markdown-lint-workflow/SKILL.md)**\n  3-step pipeline (Step 1: `markdownlint-cli2 --fix`, Step 2: companion scripts\n  in execution order, Step 3: manual fix + audit) to ensure 100% lint compliance.\n  The agent MUST re-read every generated/edited markdown file and fix any stray\n  tool-output tags (`</content>`, `<parameter ...>`), duplicated lines, broken or\n  multi-line links, unclosed fences, and embedded absolute paths BEFORE presenting\n  the artifact.\n  Linting MUST be performed by invoking the **`markdownlint-cli2`** binary directly\n  (e.g., `markdownlint-cli2 --fix <path>` then `markdownlint-cli2 <path>`); using `npx markdownlint-cli2` is\n  **FORBIDDEN** per\n  **[Markdown Generation Rules §5](../../../ai-agent-rules/markdown-generation-rules.md#5-validation-rules-markdownlint-cli2)**.\n  Recommended fix-script execution order is documented in\n  **[Markdown Lint Workflow §2.1](../general/markdown-lint-workflow/SKILL.md#21-execution-order)**.\"\"\"\n\nif old in content:\n    content = content.replace(old, new)\n    with open(filepath, \"w\") as f:\n        f.write(content)\n    print(\"SUCCESS: replacement applied\")\nelse:\n    print(\"FAIL: old string not found\")\n    # Try finding with regex\n    import re\n    match = re.search(r\"- \\*\\*Markdown Audit\\*\\*.*?Markdown Generation §3\\.1\", content, re.DOTALL)\n    if match:\n        print(\"Found with regex\")\n        print(repr(match.group(0)))\nPYTHON_EOF",
  "description": "Replace skill-factory markdown audit with exact match"
}
```

**Output:**
```
SUCCESS: replacement applied

```

---

## Assistant (Build · Nemotron 3 Ultra 550B A55B · 24.6s)

_Thinking:_

Success. Now I need to:
1. Register the new skill in root AGENTS.md
2. Create AGENTS.md companion bridge for the new skill
3. Run lint on all edited files

Let me also check if there are any other skills that reference markdown-generation's companion scripts or lint workflow that need updating.

Now register the new skill in root AGENTS.md and create the companion bridge.


**Tool: todowrite**

**Input:**
```json
{
  "todos": [
    {
      "content": "Create general/markdown-lint-workflow/ directory structure",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "Write general/markdown-lint-workflow/SKILL.md — 3-step pipeline protocol",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "Create fix-markdown-pipeline.py convenience script",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "Move companion scripts from markdown-generation/scripts/ to markdown-lint-workflow/scripts/",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "Update markdown-generation/SKILL.md — remove §3, update §2 and §5 to delegate",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "Update markdown-generation/AGENTS.md — reference new workflow",
      "priority": "medium",
      "status": "completed"
    },
    {
      "content": "Update skill-factory §3 — reference markdown-lint-workflow",
      "priority": "high",
      "status": "completed"
    },
    {
      "content": "Register new skill in root AGENTS.md",
      "priority": "medium",
      "status": "in_progress"
    },
    {
      "content": "Create AGENTS.md companion bridge for new skill",
      "priority": "medium",
      "status": "pending"
    },
    {
      "content": "Run lint on all edited files",
      "priority": "medium",
      "status": "pending"
    }
  ]
}
```

**Output:**
```
[
  {
    "content": "Create general/markdown-lint-workflow/ directory structure",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Write general/markdown-lint-workflow/SKILL.md — 3-step pipeline protocol",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Create fix-markdown-pipeline.py convenience script",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Move companion scripts from markdown-generation/scripts/ to markdown-lint-workflow/scripts/",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Update markdown-generation/SKILL.md — remove §3, update §2 and §5 to delegate",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Update markdown-generation/AGENTS.md — reference new workflow",
    "status": "completed",
    "priority": "medium"
  },
  {
    "content": "Update skill-factory §3 — reference markdown-lint-workflow",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Register new skill in root AGENTS.md",
    "status": "in_progress",
    "priority": "medium"
  },
  {
    "content": "Create AGENTS.md companion bridge for new skill",
    "status": "pending",
    "priority": "medium"
  },
  {
    "content": "Run lint on all edited files",
    "status": "pending",
    "priority": "medium"
  }
]
```

---

## Assistant (Build · Nemotron 3 Ultra 550B A55B · 314.2s)

_Thinking:_

Now let me find the root AGENTS.md and add the new skill entry in alphabetical order.

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/AGENTS.md",
  "limit": 50,
  "offset": 1
}
```

**Error:**
```
File not found: /Users/dk/lab-data/ai-suite/.agents/skills/AGENTS.md
```

---

## Assistant (Build · Nemotron 3 Ultra 550B A55B · 367.5s)

_Thinking:_

Let me check the actual location of AGENTS.md.

**Tool: bash**

**Input:**
```json
{
  "command": "find /Users/dk/lab-data/ai-suite -name \"AGENTS.md\" -type f 2>/dev/null | head -5",
  "description": "Find root AGENTS.md"
}
```

**Output:**
```
/Users/dk/lab-data/ai-suite/.agents/skills/git-lfs-selective-clone/AGENTS.md
/Users/dk/lab-data/ai-suite/.agents/skills/mise-non-standard-backend-bin-resolve/AGENTS.md
/Users/dk/lab-data/ai-suite/.agents/skills/vscode-nginx-filetype-config/AGENTS.md
/Users/dk/lab-data/ai-suite/.agents/skills/cra-reset-mocks-test-strategy/AGENTS.md
/Users/dk/lab-data/ai-suite/.agents/skills/git-commit-comparison-audit/AGENTS.md

```

---

## Assistant (Build · Nemotron 3 Ultra 550B A55B · 26.1s)

_Thinking:_

There doesn't seem to be a single root AGENTS.md in `.agents/skills/`. The original AGENTS.md I was given in the prompt is at `/Users/dk/lab-data/ai-suite/AGENTS.md` (in the workspace root). Let me check that.

The root AGENTS.md is in the workspace root (as shown in the initial prompt context). Let me read it.


**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/AGENTS.md",
  "limit": 80,
  "offset": 1
}
```

**Output:**
```
<path>/Users/dk/lab-data/ai-suite/AGENTS.md</path>
<type>file</type>
<content>
1: # AGENTS.md
2: 
3: ## ⚠️ Permanent Operating Reminders (read every boot)
4: 
5: 1. **Atomize exploration chains.** Never combine multiple unfamiliar-path
6:    probes into one `&&` / `|` chain with `2>/dev/null` suppression — it
7:    silently hangs when a path is missing. Issue independent shell calls (use
8:    parallel tool calls for unrelated probes). See
9:    [`ai-agent-rules/shell-execution-rules.md` §2.3.1](ai-agent-rules/shell-execution-rules.md).
10: 2. **Prefer Bash heredocs over the editor `edit` AND `create` tools for large writes.**
11:    Both `edit` and `create` hang on large / many-line operations (the
12:    `create` tool stresses the IDE renderer the same way `edit` does when
13:    `file_text` is large — empirically anything > ~10 KB or > ~100 lines).
14:    For whole-file authoring use `cat > file <<'EOF' ... EOF`; for in-place
15:    transforms use `python3 - <<'PY' ... PY`. The `edit` tool is reserved
16:    for small, uniquely-anchored surgical replacements; the `create` tool
17:    is reserved for short new files (< ~10 KB / < ~100 lines). See
18:    [`ai-agent-rules/shell-execution-rules.md` §2.3.2](ai-agent-rules/shell-execution-rules.md).
19: 3. **Never nest heredocs inside heredocs.** When using
20:    `python3 - <<'PY'` whose body contains a Python triple-quoted string,
21:    the inner content MUST NOT contain heredoc-sentinel-looking tokens
22:    (`EOF`, `PY`, `MARKEREOF`, etc.) or fenced code blocks — the outer
23:    heredoc terminates early and the call silently hangs. Use a
24:    two-stage `cat > /tmp/payload <<'ZZZ_UNIQUE_ZZZ'` then a separate
25:    `cat > /tmp/script.py <<'ZZZ_OTHER_ZZZ'` then run the script. Each
26:    stage carries one heredoc with a body-unique sentinel. See
27:    [`ai-agent-rules/shell-execution-rules.md` §2.3.3](ai-agent-rules/shell-execution-rules.md).
28: 4. **Bound tool-output size AND cumulative scrollback to protect the IDE renderer.** Large outputs
29:    streamed into the chat transcript (recursive `grep -r` over many-file
30:    trees, `cat` on minified bundles, full dumps of files like
31:    `workbench.desktop.main.js`) can freeze the VS Code renderer; the user's
32:    only recovery is to force-quit, which reports every in-flight tool call
33:    back as `interrupted` and drops live shell sessions. Default behavior:
34:    redirect large commands to `/tmp/out.txt` first, then `head` / `grep` /
35:    `view` it; prefer the built-in `grep` / `glob` / `view` tools over
36:    shell-side recursive scans; narrow scope with `glob` before `grep`; and
37:    never combine "produce a large output" with "read a large file" in the
38:    same tool-call batch. See
39:    [`ai-agent-rules/shell-execution-rules.md` §2.3.4](ai-agent-rules/shell-execution-rules.md).
40:    Single-output size is necessary but not sufficient — long sessions also
41:    freeze the renderer from cumulative many-small-outputs pressure, so on
42:    long sessions prefer `view_range` over full-file `view`, prefer
43:    file-write over stdout for intermediate artifacts, do NOT re-print
44:    content already in scrollback, skip trailing verification dumps, and
45:    pause-to-consolidate after ~20 tool calls per user message. See
46:    [`ai-agent-rules/shell-execution-rules.md` §2.3.4.1](ai-agent-rules/shell-execution-rules.md).
47:    The full catalogue of freeze patterns, the eleven-item per-call self-audit
48:    checklist, and the post-freeze recovery protocol — collected across
49:    reminders §1–§4 above and reified as one skill — are owned by
50:    [`.agents/skills/ide-renderer-freeze-prevention/SKILL.md`](.agents/skills/ide-renderer-freeze-prevention/SKILL.md).
51: 5. **Prefer scripts over prose instructions — both when authoring AND when
52:     consuming a skill.** Scripts are more deterministic than rules, skills,
53:     or sub-agent prompts.
54:     *Authoring side*: when designing or refactoring a skill/rule/sub-agent,
55:     decompose its procedure — every deterministic step (parse, transform,
56:     validate, file-mutate) MUST live in an executable script under the
57:     skill's `scripts/` directory; prose retains only judgement, branching,
58:     and human-gates.
59:     *Consumer side* (fires on EVERY skill invocation): before executing any
60:     deterministic step described in a skill's prose, FIRST list that skill's
61:     `scripts/` directory (`ls <skill-dir>/scripts/` or the in-process `glob`
62:     tool) and invoke the matching script — do NOT re-derive the logic
63:     ad-hoc from the prose. Re-typing a multi-step recipe inline when the
64:     skill ships a script for it is a violation even when the inline output
65:     is correct, because it bypasses the script's idempotency checks,
66:     env-var validation, and SSOT updates. Fall through to manual recipe
67:     only if no script matches the step.
68:     See
69:     [`.agents/skills/script-over-instruction-decomposition/SKILL.md`](.agents/skills/script-over-instruction-decomposition/SKILL.md)
70:     `## Consumer Discipline — Always Invoke, Never Re-derive`.
71: 6. **Do NOT probe into heavy-filewatcher symlinked trees; address files
72:    by exact path.** Walking a directory that fans out into symlinked
73:    private-config / cloud-sync / IDE-indexed subtrees (specifically
74:    `/Users/dk/Lab_Data/configurations-private/` in this workspace)
75:    triggers fsevents / Spotlight / IDE-indexer cascades that freeze
76:    the IDE renderer; the user must force-recover, which reports every
77:    in-flight tool call as `interrupted`. Read files inside such trees
78:    by EXACT absolute path (e.g.
79:    `cat /Users/dk/Lab_Data/configurations-private/Account-Ledger-Server/act.secrets`);
80:    never `ls`, `find`, or `grep -r` against the tree to discover the

(Showing lines 1-80 of 344. Use offset=81 to continue.)
</content>
```

---

## Assistant (Build · Nemotron 3 Ultra 550B A55B · 351.4s)

_Thinking:_

The skills table is in this AGENTS.md. Let me find it.

**Tool: grep**

**Input:**
```json
{
  "path": "/Users/dk/lab-data/ai-suite",
  "pattern": "^\\| Skill",
  "include": "AGENTS.md"
}
```

**Output:**
```
Found 13 matches
/Users/dk/lab-data/ai-suite/AGENTS.md:
  Line 126: | Skill | Path | When to use |

  Line 299: | Skill Cross-Reference Audit | [`.agents/skills/general/skill-cross-reference-audit/SKILL.md`](.agents/skills/general/skill-cross-reference-audit/SKILL.md) | Automated audit of the skill library for cross-reference issues — detects skills duplicated in both Composition and Related Skills, missing AGENTS.md, missing YAML frontmatter, empty Related Skills sections, and missing Related Skills in skills with Composition sections |

  Line 300: | Skill Factory | [`.agents/skills/skill-factory/SKILL.md`](.agents/skills/skill-factory/SKILL.md) | Industrial protocol for automated creation of "Skill-First" AI Agent skills with high fidelity |

  Line 301: | Skill Library Domain Grouping | [`.agents/skills/general/skill-library-domain-grouping/SKILL.md`](.agents/skills/general/skill-library-domain-grouping/SKILL.md) | Project-specific domain taxonomy and placement rules for the skill library — SSOT consumed by skill-factory and human-scanable-organization |


/Users/dk/lab-data/ai-suite/.agents/skills/table-persistence-implementation/AGENTS.md:
  Line 5: | Skill | Path | When to use |


/Users/dk/lab-data/ai-suite/.agents/skills/python-package-version-update/AGENTS.md:
  Line 5: | Skill | Path | When to use |


/Users/dk/lab-data/ai-suite/.agents/skills/php-mysqli-prepared-statement-modernization/AGENTS.md:
  Line 3: | Skill | Purpose |


/Users/dk/lab-data/ai-suite/.agents/skills/mysql-fk-hardening-workflow/AGENTS.md:
  Line 3: | Skill | Purpose |


/Users/dk/lab-data/ai-suite/.agents/skills/mariadb-check-autoincrement-trigger-fallback/AGENTS.md:
  Line 3: | Skill | Purpose |


/Users/dk/lab-data/ai-suite/.agents/skills/git-feature-branch-atomic-commit/AGENTS.md:
  Line 17: | Skill | Purpose |


/Users/dk/lab-data/ai-suite/.agents/skills/git-divergence-audit/AGENTS.md:
  Line 23: | Skill | Path | Description |


/Users/dk/lab-data/ai-suite/.agents/skills/db-backup-bracketing-protocol/AGENTS.md:
  Line 3: | Skill | Purpose |


/Users/dk/lab-data/ai-suite/.agents/skills/canonical-source-vs-workflow-repo-audit/AGENTS.md:
  Line 3: | Skill | Purpose |

```

---

## Assistant (Build · Nemotron 3 Ultra 550B A55B · 17.9s)

_Thinking:_

The root skills table starts at line 126. Let me read around there to find where to insert the new skill in alphabetical order.

**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/AGENTS.md",
  "limit": 200,
  "offset": 120
}
```

**Output:**
```
<path>/Users/dk/lab-data/ai-suite/AGENTS.md</path>
<type>file</type>
<content>
120:      query (e.g. piped post-processing the tool does not support).
121:    See
122:    [`ai-agent-rules/shell-execution-rules.md` §2.3.1.2](ai-agent-rules/shell-execution-rules.md).
123: 
124: ## Skills
125: 
126: | Skill | Path | When to use |
127: | :--- | :--- | :--- |
128: | Android Feature To Shared Kotlin Lib | [`.agents/skills/android-feature-to-shared-kotlin-lib/SKILL.md`](.agents/skills/android-feature-to-shared-kotlin-lib/SKILL.md) | Extract a vertical feature slice from an Android (Java/Kotlin) app and port it to a shared pure-Kotlin/JVM library consumable by Android, Kotlin CLI, desktop, and server clients via JitPack — with submodule-first commit discipline and CRLF/LF working-tree hygiene |
129: | Anti Gravity Version Checker | [`.agents/skills/antigravity-version-checker/SKILL.md`](.agents/skills/antigravity-version-checker/SKILL.md) | Audit Anti Gravity vs VS Code versions and feature parity |
130: | Archive Size Preflight & Extract | [`.agents/skills/archive-size-preflight-and-extract/SKILL.md`](.agents/skills/archive-size-preflight-and-extract/SKILL.md) | Pre-flight a zip / 7z / tar / tar.gz archive with 7-Zip before extracting — report compressed-on-disk size, uncompressed total, file count, folder count, and compression ratio so the user can decide if there is enough free disk space; then extract reliably to a sibling folder of the same name with progress-only output (`-bso0 -bsp1 -y`) and verify the extracted footprint matches the pre-flight report. Surfaces NTFS 4 KiB cluster-overhead warning when `FileCount > 10 000`. PowerShell-only scripts, no external deps beyond 7-Zip CLI |
131: | Bash Multiline To Single Line | [`.agents/skills/bash-multiline-to-single-line/SKILL.md`](.agents/skills/bash-multiline-to-single-line/SKILL.md) | Flatten bash `\<newline>` continuations into a single physical line (optionally line-range scoped) — used before regex-matching commands against autoApprove patterns |
132: | Brew Upgrade Command Assembly | [`.agents/skills/brew-upgrade-command-assembly/SKILL.md`](.agents/skills/brew-upgrade-command-assembly/SKILL.md) | Base primitive — assemble a Homebrew upgrade command chain from package lists with `HOMEBREW_DOWNLOAD_CONCURRENCY=1`, `--verbose`, correct fetch-after-cleanup ordering |
133: | Brew Upgrade Workflow | [`.agents/skills/brew-upgrade-workflow/SKILL.md`](.agents/skills/brew-upgrade-workflow/SKILL.md) | Composer — discover outdated leaves via `brew outdated --greedy`, filter to `brew leaves`, resolve formula vs cask, apply priority ordering, and delegate command assembly to the base primitive |
134: | Canonical-Source vs Workflow-Repo Audit | [`.agents/skills/canonical-source-vs-workflow-repo-audit/SKILL.md`](.agents/skills/canonical-source-vs-workflow-repo-audit/SKILL.md) | Pre-edit repo-role classification (canonical / workflow-backup / mirror) + soft-reset recovery when the wrong repo was already edited |
135: | Claude Session Exporter | [`.agents/skills/claude-session-exporter/SKILL.md`](.agents/skills/claude-session-exporter/SKILL.md) | Composer — export Claude/MCP session JSONL files into structured markdown with type-based content filtering; uses the `jsonl-content-extractor` base primitive |
136: | Code Explanation | [`.agents/skills/code-explanation/SKILL.md`](.agents/skills/code-explanation/SKILL.md) | Deep-dive, pedagogical code documentation standards |
137: | Command Auto-Approve Onboarding | [`.agents/skills/command-autoapprove-onboarding/SKILL.md`](.agents/skills/command-autoapprove-onboarding/SKILL.md) | Orchestrator — decompose any shell command (single / chained / multi-line / script), classify each segment via `is-this-command-safe` (extending its cheatsheet & safety-table when binaries are missing), then onboard the verdict into `chat.tools.terminal.autoApprove` via the `vscode-autoapprove-entry-consolidation` reuse-before-add algorithm; ships the §5.1 safe-chain pattern for whitelisting `;`-chained SAFE one-liners under `matchCommandLine: true`, plus `scripts/test-regex-accept.py` + `specs/*.spec.json` as the replayable regex acceptance harness |
138: | Commit Edit | [`.agents/skills/git-commit-edit/SKILL.md`](.agents/skills/git-commit-edit/SKILL.md) | User asks to edit, fix, or remove files from an existing commit via interactive rebase |
139: | Copilot Activity History Split | [`.agents/skills/copilot-activity-history-split/SKILL.md`](.agents/skills/copilot-activity-history-split/SKILL.md) | User asks to split a Microsoft / GitHub Copilot activity-history CSV export into one CSV per Conversation, sorted chronologically with the Human turn placed first on tied timestamps |
140: | Copilot Chat History Analysis | [`.agents/skills/copilot-chat-history-analysis/SKILL.md`](.agents/skills/copilot-chat-history-analysis/SKILL.md) | Deep analysis of exported AI chat history CSV files — parse structure, identify user intent and underlying process, audit AI execution quality (correctness, template consistency, meta-pattern recognition, artifact production), and assess human satisfaction using evidence-based signal dictionaries |
141: | CRA resetMocks Test Strategy | [`.agents/skills/cra-reset-mocks-test-strategy/SKILL.md`](.agents/skills/cra-reset-mocks-test-strategy/SKILL.md) | Survive CRA's jest.resetAllMocks() in jest.mock factories — identify vulnerable jest.fn() patterns, apply plain-fn and wrapper-fn mitigations, and detect regressions with a diagnostic script |
142: | DB Backup Bracketing Protocol | [`.agents/skills/db-backup-bracketing-protocol/SKILL.md`](.agents/skills/db-backup-bracketing-protocol/SKILL.md) | Composer over `github-actions-workflow-dispatch`: pre+post / post-only / none bracket patterns around destructive DB ops with recovery-anchor logging |
143: | Deleted Files Audit | [`.agents/skills/deleted-files-audit/SKILL.md`](.agents/skills/deleted-files-audit/SKILL.md) | User deletes files and asks to verify, or `git status` shows pending deletions |
144: | Directory Tree Audit | [`.agents/skills/general/directory-tree-audit/SKILL.md`](.agents/skills/general/directory-tree-audit/SKILL.md) | Recursively audits a directory tree, counts items per folder, and flags those exceeding a configurable threshold — provides the raw structural data for organization decisions |
145: | Dev-Env Private Config Symlink | [`.agents/skills/dev-env-private-config-symlink/SKILL.md`](.agents/skills/dev-env-private-config-symlink/SKILL.md) | Symlink developer-private configuration (.env, JSON, HTTP-client envs) from a sibling configurations-private repo into an app working tree across Gitpod, Cloud Shell, NeverInstall, Ubuntu, macOS, Windows — with broken-target detection, case-mismatch diagnosis, and per-consumer audit |
146: | Eclipse Launch Stdout Capture | [`.agents/skills/eclipse-launch-stdout-capture/SKILL.md`](.agents/skills/eclipse-launch-stdout-capture/SKILL.md) | Patch an Eclipse PDE `.launch` file so the launched JVM's `System.out`/`System.err` are teed to a file adjacent to the `.launch` — surfaces telemetry/lifecycle output (e.g., `[telemetry ...]`) that bypasses the host's logging appender, using the `org.eclipse.debug.ui.ATTR_CAPTURE_IN_FILE` attribute (note: `.ui.` not `.core.`) with the path `${workspace_loc:/<project>}/<launch-basename>.log`, plus IDE-refresh gotchas (F5/restart, never click *Apply* after disk edit, *Delete* physically removes project-shared launches) |
147: | Eclipse PDE JDK Migration | [`.agents/skills/eclipse-pde-jdk-migration/SKILL.md`](.agents/skills/eclipse-pde-jdk-migration/SKILL.md) | Eclipse PDE/Tycho workspace migration across JDK major versions — survey JRE pins in `.classpath`/`MANIFEST.MF`/`*.launch`/`pom.xml`, drop obsolete PermGen flags, inject JDK 9+ `--add-opens` for JAXB/EMF/Sphinx/Xtend/BeanShell reflection, and resolve IDE-only side issues (target-platform symbolic-name aliasing via PDE Maven `<location>` + bnd `<instructions>`, m2e proxy via `~/.m2/settings.xml`, empty source-folder paradox via `.gitkeep`) without touching CI/Tycho-consumed files |
148: | Eclipse PDE Telemetry Resilience | [`.agents/skills/eclipse-pde-telemetry-resilience/SKILL.md`](.agents/skills/eclipse-pde-telemetry-resilience/SKILL.md) | Add a fire-and-forget HTTP telemetry / tool-usage-logging library to an Eclipse PDE / Tycho `IApplication` — vendor library source (PDE cannot reuse `libs/*.jar` + `Bundle-ClassPath`), deliver native deps (JNA) via target-platform Maven `<location>` (one block per package family, never share `<instructions>`), wrap network I/O in a daemon-thread bulkhead with layered timeouts (10 s HTTP inside 30 s wall-clock), store-and-forward retry files, flushed timestamped lifecycle logging that survives the host's `System.out` swap, and defensive `IApplication.start` integration so telemetry never alters tool exit code |
149: | Env Example Creation | [`.agents/skills/env-example-creation/SKILL.md`](.agents/skills/env-example-creation/SKILL.md) | Generate a sanitized .env.example from an existing .env by replacing sensitive values (credentials, org-specific hosts, internal paths) with canonical placeholders — for developer onboarding and safe-to-commit templates |
150: | FFmpeg Filler Generator | [`.agents/skills/ffmpeg-filler-generator/SKILL.md`](.agents/skills/ffmpeg-filler-generator/SKILL.md) | Base primitive — generate a filler/transition video segment with black background, centered text overlay, and silent audio, with configurable codecs and duration |
151: | FFmpeg Lossless Concat | [`.agents/skills/ffmpeg-lossless-concat/SKILL.md`](.agents/skills/ffmpeg-lossless-concat/SKILL.md) | Base primitive — losslessly concatenate media files using ffmpeg's concat demuxer with `-c copy` (zero re-encoding); verifies codec compatibility first |
152: | FFmpeg Lossless Split | [`.agents/skills/ffmpeg-lossless-split/SKILL.md`](.agents/skills/ffmpeg-lossless-split/SKILL.md) | Base primitive — losslessly split or extract a segment from a media file at a timestamp using ffmpeg `-c copy` (zero re-encoding); validates timestamps before executing |
153: | File Glob Sort By Regex Capture | [`.agents/skills/file-glob-sort-by-regex-capture/SKILL.md`](.agents/skills/file-glob-sort-by-regex-capture/SKILL.md) | Base primitive — list files matching a glob, extract a regex capture group from each filename, sort by the extracted key (int/float/str), and output JSON Lines with filename, path, size, and mtime. Domain-agnostic, reusable by any sort-by-filename-key workflow |
154: | Fnmatch Content Guard Pattern | [`.agents/skills/fnmatch-content-guard-pattern/SKILL.md`](.agents/skills/fnmatch-content-guard-pattern/SKILL.md) | Base primitive — generate fnmatch permission patterns with broad-allow + narrow-deny/ask ordering to simulate content-based filtering that fnmatch alone cannot express. Consumed by `opencode-permission-config` for awk/find/sort content-guard additions |
155: | Folder Comparison | [`.agents/skills/folder-comparison/SKILL.md`](.agents/skills/folder-comparison/SKILL.md) | Compare directories for content-level consistency |
156: | Git / GitHub Auth Fallback | [`.agents/skills/git-github-auth-fallback/SKILL.md`](.agents/skills/git-github-auth-fallback/SKILL.md) | `git push`/`fetch` returns HTTP 401/403 against a GitHub remote — classify wrong-identity-cache vs missing-scope vs needs-fork, then recover via Credential Manager reset, PAT-in-URL (non-interactive), SSH remote swap, or `gh auth login` |
157: | Git Absorbed Branch Decommission | [`.agents/skills/git-absorbed-branch-decommission/SKILL.md`](.agents/skills/git-absorbed-branch-decommission/SKILL.md) | Composer — safely delete a stale branch whose content has been fully absorbed by a sibling / successor branch, via a two-step audit (cheap ancestor check, then patch-id equivalence + tip file-set parity when SHAs differ). Distinct from `git-parallel-branch-decommission` (fans out content to multiple destinations) and `git-branch-promotion` (replaces canonical with a refined branch) |
158: | Git Atomic Commit | [`.agents/skills/git-atomic-commit-construction/SKILL.md`](.agents/skills/git-atomic-commit-construction/SKILL.md) | User asks to commit changes, arrange commits, or stage and commit — working-tree changes need atomic grouping |
159: | Git Branch Promotion | [`.agents/skills/git-branch-promotion/SKILL.md`](.agents/skills/git-branch-promotion/SKILL.md) | Post-processing composer — promote a refined parallel branch (e.g., post-reword `master-2`) onto the canonical branch via cherry-pick equivalence audit, unique-commit cherry-pick, tree-parity verification, and authorized force-push |
160: | Git Clean-Filter Renormalize Backfill | [`.agents/skills/git-clean-filter-renormalize-backfill/SKILL.md`](.agents/skills/git-clean-filter-renormalize-backfill/SKILL.md) | Backfill pre-existing stored Git blobs through a newly-installed clean filter via `git add --renormalize`, with a true-byte-drift guard so live edits are excluded and the resulting commit is purely a formatting / filter change |
161: | Git Commit Comparison Audit | [`.agents/skills/git-commit-comparison-audit/SKILL.md`](.agents/skills/git-commit-comparison-audit/SKILL.md) | User asks to compare two commits, or submodule pointer mismatches are detected |
162: | Git Commit Details Audit | [`.agents/skills/git-commit-details-audit/SKILL.md`](.agents/skills/git-commit-details-audit/SKILL.md) | Industrial protocol for retrieving and analyzing high-fidelity commit metadata, hunks, and pedagogical explanations |
163: | Git Commit Identity Rewrite | [`.agents/skills/git-commit-identity-rewrite/SKILL.md`](.agents/skills/git-commit-identity-rewrite/SKILL.md) | Composer over `git-commit-edit` — rewrites author + committer identity (and optionally dates) of one or more commits by copying from a source commit, with cross-repo parent + submodule pointer cascade |
164: | Git Commit Message Bulk Reword | [`.agents/skills/git-commit-message-bulk-reword/SKILL.md`](.agents/skills/git-commit-message-bulk-reword/SKILL.md) | Range composer over `git-commit-message-reword` — enumerates a contiguous commit range and bulk-rewords non-compliant subjects (e.g., GitHub Web UI `Create/Update X.md`) into Conventional Commits in a single rebase |
165: | Git Commit Message Delivery | [`.agents/skills/git-commit-message-delivery/SKILL.md`](.agents/skills/git-commit-message-delivery/SKILL.md) | Base primitive — safely pass multi-line commit messages containing shell-special characters to `git commit` without escaping failures, and verify commit contents with reliable path listing |
166: | Git Commit Message Reword | [`.agents/skills/git-commit-message-reword/SKILL.md`](.agents/skills/git-commit-message-reword/SKILL.md) | Composer over `git-commit-edit` — reads the project's commit-message rules, classifies a single commit's diff, and rewords it into a Conventional Commits message |
167: | Git Commit Metadata Extraction | [`.agents/skills/git-commit-metadata-extraction/SKILL.md`](.agents/skills/git-commit-metadata-extraction/SKILL.md) | A universal primitive for extracting complete commit metadata from any Git commit (parent SHA, message, file classification) |
168: | Git Cross-Ref File Parity | [`.agents/skills/git-cross-ref-file-parity/SKILL.md`](.agents/skills/git-cross-ref-file-parity/SKILL.md) | Compare the diff introduced for a specific file by any two git refs (commit vs stash, commit vs commit) and report IDENTICAL or DIFFERENT with diff-of-diffs on divergence |
169: | Git Cross-Repository Cherry-Pick | [`.agents/skills/git-cross-repo-cherry-pick/SKILL.md`](.agents/skills/git-cross-repo-cherry-pick/SKILL.md) | User asks to cherry-pick or move commits between unrelated local repositories or submodules |
170: | Git Dependent Branch Restack Cascade | [`.agents/skills/git-dependent-branch-restack-cascade/SKILL.md`](.agents/skills/git-dependent-branch-restack-cascade/SKILL.md) | Composer — after a base branch advances (via cherry-pick promotion, decommission fan-out, or amend), discover every local and remote branch still rooted on the OLD tip, and cascade `rebase --onto <new-tip> <old-tip>` across all of them with per-dependent patch-id parity verification and a per-push authorization gate. Generalizes the personal-sandbox restack pattern to diagnostic, feature-stack, and PR-review dependents |
171: | Git Divergence Audit | [`.agents/skills/git-divergence-audit/SKILL.md`](.agents/skills/git-divergence-audit/SKILL.md) | Industrial protocol for surgical, unit-by-unit comparison of diverged local and remote branches |
172: | Git Drop Commit With Divergent Recreation | [`.agents/skills/git-drop-commit-with-divergent-recreation/SKILL.md`](.agents/skills/git-drop-commit-with-divergent-recreation/SKILL.md) | Composer — safely drop a commit that deletes file X when a later commit re-creates X from a stale copy that has DIVERGED from the deleted version (each side carrying unique content). Performs section-by-section blob comparison, hand-builds a union blob during the add/add rebase conflict, enforces byte-preserving file restoration, and routes around the silent `git commit --amend`-during-rebase pitfall |
173: | Git History Refinement | [`.agents/skills/git-history-refinement/SKILL.md`](.agents/skills/git-history-refinement/SKILL.md) | User asks to refine, split, or reconstruct existing commit history |
174: | Git jq-pretty JSON Filter | [`.agents/skills/git-jq-pretty-json-filter/SKILL.md`](.agents/skills/git-jq-pretty-json-filter/SKILL.md) | Composer — installs a `jq`-based Git clean+textconv filter so minified JSON files render line-by-line in both GitHub web diffs and local `git diff`, with mandatory narrow `.gitattributes` patterns (no wildcards — JSONC safety), three delivery options, and delegates pre-filter backfill to `git-clean-filter-renormalize-backfill` |
175: | Git LFS Selective Clone | [`.agents/skills/git-lfs-selective-clone/SKILL.md`](.agents/skills/git-lfs-selective-clone/SKILL.md) | Clone an LFS repo (and its submodules) without downloading any LFS blobs via the four-filter override (`GIT_LFS_SKIP_SMUDGE` + empty `filter.lfs.smudge` + empty `filter.lfs.process` + `filter.lfs.required=false`), verify pointer-only checkout, then selectively pull only the LFS objects the user needs with `--include` / `--exclude` brace-globs |
176: | Git Parallel Branch Decommission | [`.agents/skills/git-parallel-branch-decommission/SKILL.md`](.agents/skills/git-parallel-branch-decommission/SKILL.md) | Composer — decommission a parallel feature branch (e.g., a long-lived `<branch>-ai_demo` sibling of the canonical `<branch>`) by classifying each unique commit by content type and fanning it out to multiple destinations — canonical team branch, opt-in team branch for non-default instrumentation, personal sandbox for personal-only docs — with mixed commits split per file, parity-verified against every removable item, and gated authorization before deletion |
177: | Git Personal Content Extraction | [`.agents/skills/git-personal-content-extraction/SKILL.md`](.agents/skills/git-personal-content-extraction/SKILL.md) | Composer — purify a single mixed team / feature / ticket branch IN PLACE by classifying every commit as team / personal / mixed, reordering personal commits to the tip, splitting mixed commits per file, resetting the team branch to a team-only tip, and re-inserting the extracted personal commits into their ORIGINAL CHRONOLOGICAL POSITION on a long-lived personal sandbox branch (NOT appended at the tip); executes in risk-managed ROUNDS with per-round backup, authorized push, and a master safety-net audit |
178: | Git Personal Sandbox Remote | [`.agents/skills/git-personal-sandbox-remote/SKILL.md`](.agents/skills/git-personal-sandbox-remote/SKILL.md) | Composer — back up personal-only files (build configs, IDE artifacts, sandbox patches) to an independent personal GitHub repo registered as a `personal` remote alongside `origin`, without polluting the team repo via commits or social-noise-generating forks; orchestrates the REST-fallback create/delete and the PAT-safe push-without-`-u` two-step pattern |
179: | Git Personal Sandbox Restack | [`.agents/skills/git-personal-sandbox-restack/SKILL.md`](.agents/skills/git-personal-sandbox-restack/SKILL.md) | Composer — restack a personal sandbox branch onto the current tip of a moving team / feature / ticket branch via rebase, with a six-axis content-equality audit (patch-id / files-touched / file-set / per-file bytes / tree / tip-byte parity) that proves no personal content was lost before the mandatory force-push authorization |
180: | Git Personal Team Branch Workflow | [`.agents/skills/git-personal-team-branch-workflow/SKILL.md`](.agents/skills/git-personal-team-branch-workflow/SKILL.md) | Composer — proactive session discipline: work on the team branch, commit atomically, then immediately restack `personal/<purpose>` onto the new team tip; keeps personal commits always at the tip with per-commit `[team]`/`[personal]` tagging and the companion incremental-restack script |
181: | Git Post Gitignore Untrack | [`.agents/skills/git-post-gitignore-untrack/SKILL.md`](.agents/skills/git-post-gitignore-untrack/SKILL.md) | After adding/expanding `.gitignore`, untrack files that became ignored but remain in the index, and fold the cleanup into the originating commit (amend) or a follow-up commit |
182: | Git Pre-Execution Safety Stash | [`.agents/skills/git-pre-execution-safety-stash/SKILL.md`](.agents/skills/git-pre-execution-safety-stash/SKILL.md) | Before executing any sequence of ≥ 2 commits (atomic-commit batches, history-refinement runs, rebase chains, hunk-staged splits), capture a verifiable apply-not-pop working-tree snapshot via `git stash push -u -m "safety: ..."` + immediate `git stash apply`, hold it across the sequence, and verify-then-drop only at end-of-session after a clean no-op apply-back; includes IDE file-lock recovery during apply |
183: | Git Rebase | [`.agents/skills/git-rebase-standardization/SKILL.md`](.agents/skills/git-rebase-standardization/SKILL.md) | User asks to rebase branches, manage multi-branch chains, or deduplicate cross-branch commits |
184: | Git Ref Content Audit | [`.agents/skills/git-ref-content-audit/SKILL.md`](.agents/skills/git-ref-content-audit/SKILL.md) | Bulk per-file blob-equality audit between two Git refs (commit/branch/tag/stash including untracked tree at stash^3) — classify every Ref-A file as IDENTICAL / DIFFERENT / MISSING against Ref-B, with verdict line indicating full / partial / non-supersession |
185: | Git Repo Storage Minimization | [`.agents/skills/git-repo-storage-minimization/SKILL.md`](.agents/skills/git-repo-storage-minimization/SKILL.md) | User asks to shrink `.git` size, deinitialize unused submodules, or run `gc`/reflog-expiry/prune without rewriting history |
186: | Git Repository Status | [`.agents/skills/git-repository-status/SKILL.md`](.agents/skills/git-repository-status/SKILL.md) | Industrial protocol for auditing branch divergence, staged/unstaged changes, and repository history |
187: | Git Stash Triage | [`.agents/skills/git-stash-triage/SKILL.md`](.agents/skills/git-stash-triage/SKILL.md) | Industrial protocol for classifying, disposing, and (when appropriate) promoting pre-existing Git stashes to atomic commits or personal-sandbox branches — covers hang-free inspection, content-based classification, apply-not-pop verification, rule-driven disposition, and §4d per-file selective restoration when `git stash apply` fails or fine-grained control is needed |
188: | Git Submodule Addition | [`.agents/skills/git-submodule-addition/SKILL.md`](.agents/skills/git-submodule-addition/SKILL.md) | Automate adding Git submodules with standardized naming and initialization |
189: | Git Submodule Commit Details | [`.agents/skills/git-submodule-commit-details/SKILL.md`](.agents/skills/git-submodule-commit-details/SKILL.md) | Extract complete submodule commit metadata (parent, message, file changes, author, committer, URL) for use in sync messages or audits |
190: | Git Submodule Dead Upstream Audit | [`.agents/skills/git-submodule-dead-upstream-audit/SKILL.md`](.agents/skills/git-submodule-dead-upstream-audit/SKILL.md) | Diagnose unreachable submodule upstreams (404/private/deleted), check local cached history, and search GitHub for forks or mirrors of the recorded SHA before deciding to remove |
191: | Git Submodule Fork Reconfigure | [`.agents/skills/git-submodule-fork-reconfigure/SKILL.md`](.agents/skills/git-submodule-fork-reconfigure/SKILL.md) | Operational protocol for forking submodules on the fly and reconfiguring remotes |
192: | Git Submodule Fork Sync | [`.agents/skills/git-submodule-fork-sync/SKILL.md`](.agents/skills/git-submodule-fork-sync/SKILL.md) | Automates the realignment of `.gitmodules` to track internal submodule forks while securing origin upstreams |
193: | Git Submodule Misconfiguration Audit & Revert | [`.agents/skills/git-submodule-misconfiguration-audit-and-revert/SKILL.md`](.agents/skills/git-submodule-misconfiguration-audit-and-revert/SKILL.md) | Composer — end-to-end remediation of an incorrectly-configured submodule URL in `.gitmodules`: detect detached HEAD + behind-origin, audit `.gitmodules` vs live `origin`, attribute the change to a superproject commit (auditing message direction vs diff direction to catch reversed-direction traps), drop/split that commit via `git-commit-edit`, `git submodule sync`, then hand off to `git-dependent-branch-restack-cascade` (esp. §4.7 for dependents rooted on mid-history commits) |
194: | Git Submodule Missing Revision Recovery | [`.agents/skills/git-submodule-missing-revision-recovery/SKILL.md`](.agents/skills/git-submodule-missing-revision-recovery/SKILL.md) | `git submodule update --init` fails with "Unable to find current revision in submodule path" — fetch upstream into the submodule's local clone, clear stray stubs, and checkout the recorded SHA directly |
195: | Git Submodule Orphan Gitlink Recovery | [`.agents/skills/git-submodule-orphan-gitlink-recovery/SKILL.md`](.agents/skills/git-submodule-orphan-gitlink-recovery/SKILL.md) | Composer — recover submodule pointers recorded in a tree but missing from `.gitmodules`, via SHA-based upstream discovery, fork reconfigure, registration, and unrecoverable-pointer drop |
196: | Git Submodule Pointer Repair | [`.agents/skills/git-submodule-pointer-repair/SKILL.md`](.agents/skills/git-submodule-pointer-repair/SKILL.md) | Industrial protocol for surgically fixing invalid submodule pointers in parent repository history using the Synchronization Horizon algorithm |
197: | Git Submodule Removal | [`.agents/skills/git-submodule-removal/SKILL.md`](.agents/skills/git-submodule-removal/SKILL.md) | Industrial protocol for the atomic and complete removal of Git submodules, purging all tracking and meta-data |
198: | Git Submodule Selective Init (No-LFS) | [`.agents/skills/git-submodule-selective-init-no-lfs/SKILL.md`](.agents/skills/git-submodule-selective-init-no-lfs/SKILL.md) | Atomic — initialize **exactly** the named submodule paths (no `--recursive`, no transitive init) while guaranteeing zero LFS object bytes are fetched (env `GIT_LFS_SKIP_SMUDGE=1` + inline `-c filter.lfs.smudge=`/`-c filter.lfs.process=`/`-c filter.lfs.required=false`); verifies both per-path checkout AND empty `.git/modules/<path>/lfs/objects`. Per-path init-time successor to `git-lfs-selective-clone`, which mandates `--recursive` |
199: | Git Submodule Uninitialized Audit | [`.agents/skills/git-submodule-uninitialized-audit/SKILL.md`](.agents/skills/git-submodule-uninitialized-audit/SKILL.md) | Composer — recursive read-only audit of every submodule pointer (top-level + nested + orphan) with HTTP reachability classification, delegating dead-upstream investigation |
200: | Git Submodule Uninitialized Handler | [`.agents/skills/git-submodule-uninitialized-handler/SKILL.md`](.agents/skills/git-submodule-uninitialized-handler/SKILL.md) | Composer — consumes the uninitialized-audit report and drives every pointer to a fully-initialized state via init, orphan-recovery, fork-reconfigure, or gated removal |
201: | git-stash-parent-commit | [`.agents/skills/git-stash-parent-commit/SKILL.md`](.agents/skills/git-stash-parent-commit/SKILL.md) | Industrial protocol for obtaining the commit hash and subject line that was HEAD when a given Git stash was created. |
202: | GitHub Actions Run Audit | [`.agents/skills/github-actions-run-audit/SKILL.md`](.agents/skills/github-actions-run-audit/SKILL.md) | Composer — audit GitHub Actions workflow runs end-to-end via `gh` CLI: list/view runs, download artifacts, and (by composing `github-repo-commit-fetch` + `github-actions-workflow-dispatch`) verify the workflow committed a fresh artifact and optionally trigger-then-audit |
203: | GitHub Actions Workflow Dispatch | [`.agents/skills/github-actions-workflow-dispatch/SKILL.md`](.agents/skills/github-actions-workflow-dispatch/SKILL.md) | Base — trigger a GitHub Actions `workflow_dispatch` run via `gh workflow run`, optionally polling `gh run list` until the new run reaches completed status |
204: | GitHub CI Lint | [`.agents/skills/github-ci-lint/SKILL.md`](.agents/skills/github-ci-lint/SKILL.md) | C2 composer — generates CI lint workflows by calling B7 (markdown lint) and B8 (python lint) base skills |
205: | GitHub Code of Conduct | [`.agents/skills/github-code-of-conduct/SKILL.md`](.agents/skills/github-code-of-conduct/SKILL.md) | B13 — generate a CODE_OF_CONDUCT.md (Contributor Covenant 2.1) for a GitHub repository |
206: | GitHub Contributing Guide | [`.agents/skills/github-contributing-guide/SKILL.md`](.agents/skills/github-contributing-guide/SKILL.md) | B14 — generate a CONTRIBUTING.md for a GitHub repository |
207: | GitHub Docs | [`.agents/skills/github-docs/SKILL.md`](.agents/skills/github-docs/SKILL.md) | C5 composer — generates community documentation (code of conduct, contributing guide, security policy, support docs) |
208: | GitHub Docs Readme | [`.agents/skills/github-docs-readme/SKILL.md`](.agents/skills/github-docs-readme/SKILL.md) | Base — generate a docs/README.md with standard documentation structure sections |
209: | GitHub Docs Structure | [`.agents/skills/github-docs-structure/SKILL.md`](.agents/skills/github-docs-structure/SKILL.md) | Base — create the standard docs/ directory tree (architecture, decisions, implementation-plans, guides) |
210: | GitHub Folder Structure | [`.agents/skills/github-folder-structure/SKILL.md`](.agents/skills/github-folder-structure/SKILL.md) | Base — create the standard repository skeleton (.github/workflows, .github/ISSUE_TEMPLATE, scripts, docs) |
211: | GitHub Gitignore Template | [`.agents/skills/github-gitignore-template/SKILL.md`](.agents/skills/github-gitignore-template/SKILL.md) | B12 — generate a .gitignore scoped by project language (Python, Node, generic) |
212: | GitHub Issue Template Bug | [`.agents/skills/github-issue-template-bug/SKILL.md`](.agents/skills/github-issue-template-bug/SKILL.md) | B3 — write a bug report issue template to `.github/ISSUE_TEMPLATE/bug.yml` |
213: | GitHub Issue Template Documentation | [`.agents/skills/github-issue-template-documentation/SKILL.md`](.agents/skills/github-issue-template-documentation/SKILL.md) | B5 — write a documentation request issue template to `.github/ISSUE_TEMPLATE/documentation.yml` |
214: | GitHub Issue Template Feature | [`.agents/skills/github-issue-template-feature/SKILL.md`](.agents/skills/github-issue-template-feature/SKILL.md) | B4 — write a feature request issue template to `.github/ISSUE_TEMPLATE/feature.yml` |
215: | GitHub Maturity Model MaC | [`.agents/skills/github-maturity-model-maC/SKILL.md`](.agents/skills/github-maturity-model-maC/SKILL.md) | B19 — add Model as Code maturity markers (shield.io badges) to a repository README |
216: | GitHub PR Edit | [`.agents/skills/gh-pr-edit/SKILL.md`](.agents/skills/gh-pr-edit/SKILL.md) | View and edit GitHub PR title/body via gh CLI with multi-line body support |
217: | GitHub PR Template | [`.agents/skills/github-pr-template/SKILL.md`](.agents/skills/github-pr-template/SKILL.md) | B6 — write a pull request template to `.github/PULL_REQUEST_TEMPLATE.md` |
218: | GitHub Readme Template | [`.agents/skills/github-readme-template/SKILL.md`](.agents/skills/github-readme-template/SKILL.md) | B17 — generate a README.md template for a GitHub repository |
219: | GitHub Repo Commit Fetch | [`.agents/skills/github-repo-commit-fetch/SKILL.md`](.agents/skills/github-repo-commit-fetch/SKILL.md) | Base — read-only fetch primitives for GitHub repo data via `gh api`: list recent commits, fetch one commit's details (msg/files/sha/date), fetch a file at a specific ref — composable by audit, archaeology, and supply-chain skills |
220: | GitHub Repo Create | [`.agents/skills/gh-repo-create/SKILL.md`](.agents/skills/gh-repo-create/SKILL.md) | B1 — create a GitHub repository via `gh repo create` with structured arguments |
221: | GitHub Repo Edit Metadata | [`.agents/skills/gh-repo-edit-metadata/SKILL.md`](.agents/skills/gh-repo-edit-metadata/SKILL.md) | B2 — edit repository description and topics via `gh repo edit` |
222: | GitHub Repo Publish | [`.agents/skills/github-repo-publish/SKILL.md`](.agents/skills/github-repo-publish/SKILL.md) | C7 orchestrator — creates a GitHub repository with full community standards: templates, workflows, docs, and MaC markers |
223: | GitHub Repo Structure | [`.agents/skills/github-repo-structure/SKILL.md`](.agents/skills/github-repo-structure/SKILL.md) | B18 — generate the `.github/` directory structure with issue templates, workflow stubs, and config files |
224: | GitHub Repo Template | [`.agents/skills/github-repo-template/SKILL.md`](.agents/skills/github-repo-template/SKILL.md) | C6 composer — generates the full repository template including community standards and MaC maturity markers |
225: | GitHub Repo Templates | [`.agents/skills/github-repo-templates/SKILL.md`](.agents/skills/github-repo-templates/SKILL.md) | C1 composer — generates all community standard templates (gitignore, code of conduct, contributing, security, support, README, issue/PR templates) |
226: | GitHub REST API Fallback | [`.agents/skills/github-rest-api-fallback/SKILL.md`](.agents/skills/github-rest-api-fallback/SKILL.md) | `gh` CLI is unavailable or unauthenticated — query/mutate GitHub via REST (`api.github.com`) using PowerShell `Invoke-RestMethod` or `curl`, with mandatory `User-Agent`, optional PAT via `$env:GITHUB_TOKEN`, endpoint cookbook for fork discovery / PR / secrets, and rate-limit awareness |
227: | GitHub Secrets Bulk Set | [`.agents/skills/github-secrets-bulk-set/SKILL.md`](.agents/skills/github-secrets-bulk-set/SKILL.md) | Industrial protocol for setting GitHub repository (or environment) secrets in bulk from a local .env-style secrets file using the `gh` CLI |
228: | GitHub Security Policy | [`.agents/skills/github-security-policy/SKILL.md`](.agents/skills/github-security-policy/SKILL.md) | B15 — generate a SECURITY.md for a GitHub repository |
229: | GitHub Support Docs | [`.agents/skills/github-support-docs/SKILL.md`](.agents/skills/github-support-docs/SKILL.md) | B16 — generate a SUPPORT.md for a GitHub repository |
230: | GitHub Sync | [`.agents/skills/github-sync/SKILL.md`](.agents/skills/github-sync/SKILL.md) | C3 composer — generates GitHub metadata sync workflows (description and topics) |
231: | GitHub Workflow Creation | [`.agents/skills/github-workflow-creation/SKILL.md`](.agents/skills/github-workflow-creation/SKILL.md) | Protocol for creating CI/CD workflows with atomic script separation, access control, and optimized deployment patterns |
232: | GitHub Workflows | [`.agents/skills/github-workflows/SKILL.md`](.agents/skills/github-workflows/SKILL.md) | C4 composer — generates all GitHub Actions workflows (lint, PR labeler, sync) |
233: | Gitignore Rules | [`.agents/skills/gitignore-rules/SKILL.md`](.agents/skills/gitignore-rules/SKILL.md) | User asks to audit `.gitignore`, or directory-ignore + negation patterns detected |
234: | Gitignore Whitelist Pattern | [`.agents/skills/gitignore-whitelist-pattern/SKILL.md`](.agents/skills/gitignore-whitelist-pattern/SKILL.md) | Generate a deny-all + whitelist `.gitignore` block for directories that should only contain specific file types (e.g., `.7z` archives) and Git configuration files |
235: | Gitignored Reference Detection | [`.agents/skills/gitignored-reference-detection/SKILL.md`](.agents/skills/gitignored-reference-detection/SKILL.md) | Detect references to gitignored files in committed markdown and replace with public hosted URLs — ensures cross-references survive standalone clones |
236: | Google OAuth Setup | [`.agents/skills/google-oauth-setup/SKILL.md`](.agents/skills/google-oauth-setup/SKILL.md) | Base — manage Google OAuth2 PKCE credential lifecycle: detect expiry, refresh via refresh_token, or initiate browser-based PKCE auth URL → exchange code → save credentials; domain-agnostic, reusable by any Google API workflow |
237: | Harper Linting Suppression | [`.agents/skills/harper-linting-suppression/SKILL.md`](.agents/skills/harper-linting-suppression/SKILL.md) | Protocol for addressing Harper linter false positives |
238: | Human-Scanable Organization | [`.agents/skills/general/human-scanable-organization/SKILL.md`](.agents/skills/general/human-scanable-organization/SKILL.md) | Applies the 8±2 cognitive principle to organize folders for human scanability — composer: consumes directory-tree-audit data and provides domain-grouping methodology |
239: | IDE Renderer Freeze Prevention | [`.agents/skills/ide-renderer-freeze-prevention/SKILL.md`](.agents/skills/ide-renderer-freeze-prevention/SKILL.md) | Atomic SSOT for the ten recurring freeze patterns (command-chaining, recursive bash grep, multi-path arguments, oversize heredocs, inverted-match assumption, Edit/Create tool on large ops, parallel-batch cumulative scrollback, cross-turn drain-window carryover, within-turn cumulative scrollback, session-aggregate lifetime ceiling), the eleven-item per-call self-audit checklist, and the four-step post-freeze recovery protocol — owns the discipline that AGENTS.md §1–§4 articulate as reminders |
240: | Is This Command Safe | [`.agents/skills/is-this-command-safe/SKILL.md`](.agents/skills/is-this-command-safe/SKILL.md) | Vet any shell command before execution — four-tier safety classification (SAFE / SAFE-IF-PIPED / HAS-DESTRUCTIVE-FLAGS / MUTATES), destructive-flag inventory, dangerous-pipeline catalogue, and mandated 5-line verdict template |
241: | Java Classpath Telemetry Integration | [`.agents/skills/java-classpath-telemetry-integration/SKILL.md`](.agents/skills/java-classpath-telemetry-integration/SKILL.md) | Add a fire-and-forget HTTP telemetry / tool-usage-logging library to a plain Java CLI application packaged as a Jar-in-Jar runnable JAR — `libs/` JAR delivery wired into Eclipse `.classpath` + build script + Jar-in-Jar manifest, classpath `<vendor>.properties` resolution with sysprop/env override layers, classpath-resource `version.properties` SSOT, `rsrc:` → `user.dir` resource-path fallback, log4j-based lifecycle logging, `*.spool` store-and-forward retry drained on next process invocation, and defensive `main(...)` integration with `finally`-block `sendLog()` |
242: | Java Vendored Snapshot Compile Check | [`.agents/skills/java-vendored-snapshot-compile-check/SKILL.md`](.agents/skills/java-vendored-snapshot-compile-check/SKILL.md) | Type-check a directory of Java source extracted from a host project you can't build (Eclipse PDE bundle / closed-source SDK / internal product) — enumerate external symbol surface via `Select-String '^import '` + qualified-reference grep, classify into JDK / library-JAR / self / host-project buckets, generate minimal compile-only stubs (no-op bodies, exact signatures, correct packages), compile stubs to `stubs-bin/`, then `javac` the snapshot against `stubs-bin/` + real library JARs and verify patch-introduced inner classes appear in `out/` — proves patch type contract is intact without paying the host-workspace setup cost |
243: | Jira acli Operations | [`.agents/skills/jira-acli-operations/SKILL.md`](.agents/skills/jira-acli-operations/SKILL.md) | User asks to create Jira tickets, comment PR URLs on tickets, or automate acli jira operations |
244: | Jira Automation Rules | [`.agents/skills/jira-automation-rules/SKILL.md`](.agents/skills/jira-automation-rules/SKILL.md) | Build, debug, and harden Jira Cloud native automation rules — triggers, conditions, branches, smart values, web requests, loop guards, Comment dedupe workarounds, field/screen prerequisites, and parent-to-subtask field sync |
245: | Jira InlineCard Comment | [`.agents/skills/jira-inlinecard-comment/SKILL.md`](.agents/skills/jira-inlinecard-comment/SKILL.md) | Create, update, and verify Jira inlineCard comments via API v2 wiki markup with acli-based ADF verification |
246: | Jira Work Item Hierarchy Report | [`.agents/skills/jira-workitem-hierarchy-report/SKILL.md`](.agents/skills/jira-workitem-hierarchy-report/SKILL.md) | Given a JQL query, fetch matching Jira work items, build a parent-child hierarchy tree, and output markdown with clickable links and dev vs testing subtask classification |
247: | JSON Batch File Move | [`.agents/skills/json-batch-file-move/SKILL.md`](.agents/skills/json-batch-file-move/SKILL.md) | Base primitive — read a JSON array of files keyed by destination folder, batch-move files into key-named subdirectories with dry-run support. Metadata-only (os.stat/shutil.move, no file reads) |
248: | JSON Block Indent Override | [`.agents/skills/json-block-indent-override/SKILL.md`](.agents/skills/json-block-indent-override/SKILL.md) | Composer — re-indent lines inside a top-level JSON key's block with auto-quoted target keys and `json.loads` validation. Pipes through the text-block-indent-override base skill |
249: | JSON Deep Sort | [`.agents/skills/json-deep-sort/SKILL.md`](.agents/skills/json-deep-sort/SKILL.md) | Alphabetically sorts primitive JSON arrays and recursively applies sort_keys=True for unified dictionary ordering safely natively |
250: | JSON Diff CLI | [`.agents/skills/json-diff-cli/SKILL.md`](.agents/skills/json-diff-cli/SKILL.md) | Composer — human-readable JSON leaf diff with timestamp formatting, set-based list diff, and summary conclusion. Calls the json-diff-leaf base primitive via subprocess. |
251: | JSON Diff Leaf | [`.agents/skills/json-diff-leaf/SKILL.md`](.agents/skills/json-diff-leaf/SKILL.md) | Base primitive — recursive leaf-value diff of two JSON files. Outputs deterministic, machine-readable JSON change list. Domain-agnostic. |
252: | JSON Group Stats | [`.agents/skills/json-group-stats/SKILL.md`](.agents/skills/json-group-stats/SKILL.md) | Base primitive — group a JSON array by a specified field, emit per-group counts or the grouped records. Domain-agnostic, reusable by any group-by workflow |
253: | JSONL Content Extractor | [`.agents/skills/jsonl-content-extractor/SKILL.md`](.agents/skills/jsonl-content-extractor/SKILL.md) | Base primitive — extract typed content blocks from JSONL files via key-path navigation with optional value narrowing at each level. Domain-agnostic |
254: | Large Text File Stream-Split | [`.agents/skills/large-text-file-stream-split/SKILL.md`](.agents/skills/large-text-file-stream-split/SKILL.md) | Stream-split a very large (> 100 MB) text file (build log, SQL dump, CSV, JSONL) into N byte-exact, LF-aligned chunks any editor can open; ships portable C source + PowerShell build script + self-describing chunk folder layout (predictable filenames, `INDEX.csv`, `INSTRUCTIONS.md`) with byte-for-byte concat reproducibility |
255: | List Indent Consistency | [`.agents/skills/general/list-indent-consistency/SKILL.md`](.agents/skills/general/list-indent-consistency/SKILL.md) | Base primitive — detect and repair inconsistent continuation-line indentation under list items in markdown files. Consumed by skill-factory, markdown-generation, and git-atomic-commit-construction for post-edit indent verification. |
256: | LOC Analysis | [`.agents/skills/loc-analysis/SKILL.md`](.agents/skills/loc-analysis/SKILL.md) | User asks to calculate LOC, measure code changes, or quantify a feature's footprint |
257: | Lower Case Hyphen Naming Convention | [`.agents/skills/lower-case-hyphen-naming/SKILL.md`](.agents/skills/lower-case-hyphen-naming/SKILL.md) | User asks to enforce hyphen naming, or files/dirs with spaces or underscores are detected |
258: | Lower Case Underscore Naming Convention | [`.agents/skills/lower-case-underscore-naming/SKILL.md`](.agents/skills/lower-case-underscore-naming/SKILL.md) | User asks to enforce underscore naming, or files/dirs with hyphens are detected |
259: | macOS Screenshots Folder Split | [`.agents/skills/macos-screenshots-folder-split/SKILL.md`](.agents/skills/macos-screenshots-folder-split/SKILL.md) | Domain composer — convenience wrapper around onedrive-flat-folder-split-by-size with macOS screenshot/recording filename defaults and two-pass (PNG + MOV) execution |
260: | macOS Shell Portability | [`.agents/skills/general/macos-shell-portability/SKILL.md`](.agents/skills/general/macos-shell-portability/SKILL.md) | Reference — macOS shell differences (zsh, BSD vs GNU tools, `; &&` pitfalls, portable command patterns) cross-referenced by brew and general skills |
261: | MariaDB CHECK on AUTO_INCREMENT — Trigger Fallback | [`.agents/skills/mariadb-check-autoincrement-trigger-fallback/SKILL.md`](.agents/skills/mariadb-check-autoincrement-trigger-fallback/SKILL.md) | Error 1901 misleading-attribution pitfall + BEFORE INSERT/UPDATE trigger fallback when CHECK cannot reference AUTO_INCREMENT columns |
262: | Markdown Generation | [`.agents/skills/markdown-generation/SKILL.md`](.agents/skills/markdown-generation/SKILL.md) | Industrial protocol for generating lint-compliant, high-fidelity markdown documentation |
263: | Maven POM Audit | [`.agents/skills/maven-pom-audit/SKILL.md`](.agents/skills/maven-pom-audit/SKILL.md) | User asks to audit pom.xml, or invalid URLs/developer identity detected |
264: | Media Audio Language Detect | [`.agents/skills/media-audio-language-detect/SKILL.md`](.agents/skills/media-audio-language-detect/SKILL.md) | Base — detect the spoken language of a media file's audio track via SpeechRecognition + Google Web Speech API; consumed by youtube-video-upload for pre-upload language auto-detection |
265: | Media Timestamp Summary | [`.agents/skills/media-timestamp-summary/SKILL.md`](.agents/skills/media-timestamp-summary/SKILL.md) | Composer — generate a chronological summary of media files sorted by epoch-ms timestamp embedded in their filenames, with date conversion, time-gap analysis, and file sizes; composes the `file-glob-sort-by-regex-capture` base skill |
266: | MCP Cross-Tool Config Sync | [`.agents/skills/mcp-cross-tool-config-sync/SKILL.md`](.agents/skills/mcp-cross-tool-config-sync/SKILL.md) | Composer — share one MCP server config across VS Code Copilot, JetBrains Copilot, Copilot CLI, Claude Desktop, Cursor, Windsurf, etc. via a 7-phase lifecycle (inventory → backup → schema-probe → wire → generate → symlink → verify → lifecycle ops); delegates schema discovery to [Tool Config Schema Probe](.agents/skills/tool-config-schema-probe/SKILL.md) |
267: | MCP Server Management | [`.agents/skills/mcp-management/SKILL.md`](.agents/skills/mcp-management/SKILL.md) | Industrial protocol for adding, configuring, and verifying MCP servers |
268: | Mise Backend → VS Code Tool Bridge | [`.agents/skills/mise-backend-vscode-tool-bridge/SKILL.md`](.agents/skills/mise-backend-vscode-tool-bridge/SKILL.md) | Composer — wire a tool installed via a non-default mise backend (`github:`, `ubi:`, `asdf:`, `http:`) into the built-in VS Code interpreter settings for the language, across folder `.vscode/settings.json` and workspace `.code-workspace` scopes; feeds `mise-non-standard-backend-bin-resolve` into `vscode-multi-scope-setting-write` |
269: | Mise Non-Standard Backend Bin Resolve | [`.agents/skills/mise-non-standard-backend-bin-resolve/SKILL.md`](.agents/skills/mise-non-standard-backend-bin-resolve/SKILL.md) | Base primitive — resolve the absolute on-disk binary path for a tool installed via a non-default mise backend (`github:`, `ubi:`, `asdf:`, `http:`) where `mise which <tool>` and `mise where <tool>@latest` both fail; sibling of `mise-tool-management` Layer 2 |
270: | Mise Tool Management | [`.agents/skills/mise-tool-management/SKILL.md`](.agents/skills/mise-tool-management/SKILL.md) | Protocols for mise configuration trust, plugin installation & backend selection (HTTPS URL form, never `vfox:` / `asdf:` prefixes), and tool version selection |
271: | MRT Component Test Strategy | [`.agents/skills/mrt-component-test-strategy/SKILL.md`](.agents/skills/mrt-component-test-strategy/SKILL.md) | Test Material React Table components with Jest+RTL under CRA's resetMocks — mock MRT, capture useMaterialReactTable options, isolate component dependencies, and avoid common pitfalls |
272: | MRT Configuration Debug | [`.agents/skills/mrt-configuration-debug/SKILL.md`](.agents/skills/mrt-configuration-debug/SKILL.md) | Debug missing MRT toolbar features (density toggle, fullscreen, filters, etc.), fix `enable*` config props, and verify with playwright-cli |
273: | MySQL Capability Probe (PyMySQL) | [`.agents/skills/mysql-capability-probe-pymysql/SKILL.md`](.agents/skills/mysql-capability-probe-pymysql/SKILL.md) | Probe a live MySQL server for capability flags such as `CLIENT_MULTI_STATEMENTS` using a tiny Python + PyMySQL script, before adopting the capability in production code. Avoids Homebrew `mysql` 9.x (dropped `mysql_native_password`) and a full MariaDB install |
274: | MySQL Foreign-Key Hardening Workflow | [`.agents/skills/mysql-fk-hardening-workflow/SKILL.md`](.agents/skills/mysql-fk-hardening-workflow/SKILL.md) | End-to-end FK hardening composer — probe → sentinel-NULL migrate → backup-bracket → ALTER → self-ref guard → verify |
275: | Near-Duplicate File Comparison | [`.agents/skills/near-duplicate-file-comparison/SKILL.md`](.agents/skills/near-duplicate-file-comparison/SKILL.md) | Two files in the same directory share a base name with a `_old`/`_bak`/`_v1`/`_draft`/`_copy` suffix — apply an eight-dimension forensic rubric (header, imports, structure, algorithm, error reporting, robustness, compile status, functional LOC) to identify the canonical file, flag same-type-same-package compile blockers, and produce a keep/delete/merge verdict |
276: | Noise Removal via Commit Edit | [`.agents/skills/noise-removal-via-commit-edit/SKILL.md`](.agents/skills/noise-removal-via-commit-edit/SKILL.md) | User asks to remove IDE artifact noise (m2e `.project`, `.classpath`, `.settings/`) from an existing commit |
277: | NPM Global Package Path Discovery | [`.agents/skills/npm-global-package-path-discovery/SKILL.md`](.agents/skills/npm-global-package-path-discovery/SKILL.md) | Industrial protocol for locating the exact filesystem path of globally installed npm packages and their executable shims, including mise-managed Node environments |
278: | OneDrive Flat Folder Split By Size | [`.agents/skills/onedrive-flat-folder-split-by-size/SKILL.md`](.agents/skills/onedrive-flat-folder-split-by-size/SKILL.md) | Composer — split a flat folder (e.g., OneDrive with >5000 files) into key-named subfolders using regex capture from filenames. Composes file-glob-sort-by-regex-capture + json-group-stats + json-batch-file-move. Metadata-only (no file reads) |

(Output capped at 50 KB. Showing lines 120-278. Use offset=279 to continue.)
</content>
```

---

## Assistant (Build · Nemotron 3 Ultra 550B A55B · 105.8s)

_Thinking:_

Now I need to find where to insert the new skill. It should go alphabetically by "Markdown Lint Workflow" which would be between "Markdown Generation" (line 262) and "Maven POM Audit" (line 263). Let me insert it after "Markdown Generation".

Now I need to insert the new skill entry in the table. "Markdown Lint Workflow" should go after "Markdown Generation" (line 262) and before "Maven POM Audit" (line 263).


**Tool: edit**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/AGENTS.md",
  "oldString": "| Markdown Generation | [`.agents/skills/markdown-generation/SKILL.md`](.agents/skills/markdown-generation/SKILL.md) | Industrial protocol for generating lint-compliant, high-fidelity markdown documentation |\n| Maven POM Audit | [`.agents/skills/maven-pom-audit/SKILL.md`](.agents/skills/maven-pom-audit/SKILL.md) | User asks to audit pom.xml, or invalid URLs/developer identity detected |",
  "newString": "| Markdown Generation | [`.agents/skills/markdown-generation/SKILL.md`](.agents/skills/markdown-generation/SKILL.md) | Industrial protocol for generating lint-compliant, high-fidelity markdown documentation |\n| Markdown Lint Workflow | [`.agents/skills/general/markdown-lint-workflow/SKILL.md`](.agents/skills/general/markdown-lint-workflow/SKILL.md) | Three-step markdown lint fix pipeline — markdownlint-cli2 --fix, companion scripts, manual fix + audit. Base primitive consumed by markdown-generation and skill-factory |\n| Maven POM Audit | [`.agents/skills/maven-pom-audit/SKILL.md`](.agents/skills/maven-pom-audit/SKILL.md) | User asks to audit pom.xml, or invalid URLs/developer identity detected |"
}
```

**Output:**
```
Edit applied successfully.
```

---

## Assistant (Build · Nemotron 3 Ultra 550B A55B · 35.7s)

_Thinking:_

Now I need to create the AGENTS.md companion bridge for the new skill.

Now create the AGENTS.md companion bridge for the new skill.


**Tool: bash**

**Input:**
```json
{
  "command": "cat > /Users/dk/lab-data/ai-suite/.agents/skills/general/markdown-lint-workflow/AGENTS.md << 'AGENTS_EOF'\n# AGENTS.md (Markdown Lint Workflow)\n\nRefer to [SKILL.md](./SKILL.md) for the active operational protocol for the 3-step markdown lint fix pipeline.\n\n## Mandates\n\n- **Pipeline Steps**: Run the full 3-step pipeline in order — Step 1: `markdownlint-cli2 --fix`, Step 2: companion scripts in §2.1 execution order, Step 3: manual fix + final `markdownlint-cli2` audit.\n- **Script Invocation**: Use the convenience script `scripts/fix-markdown-pipeline.py` for one-shot execution, or call companion scripts individually with `--check` for dry-run.\n- **Execution Order**: Companion scripts MUST run in the order defined in §2.1 to avoid re-introducing lint errors.\n- **MD040 Caveat**: Do NOT use `markdownlint-cli2 --fix` for MD040 — use `fix-fenced-code-language.py` which correctly handles fence state.\n- **Post-Fix Check**: After running the pipeline, verify continuation-line indent with `list-indent-consistency` skill.\n\n## Cross-References\n\n- `markdown-generation` — consumes this skill for post-generation linting\n- `skill-factory` §3 — consumes this skill for post-drafting linting\n- `list-indent-consistency` — detect and repair indent drift after fix scripts\n- `markdownlint-cli2` — the underlying lint tool\nAGENTS_EOF",
  "description": "Create AGENTS.md companion bridge for new skill"
}
```

**Output:**
```
(no output)
```

---

## Assistant (Build · Nemotron 3 Ultra 550B A55B · 40.8s)

_Thinking:_

Now I need to run the lint on all edited files to ensure they pass. Let me run markdownlint-cli2 on the files I've edited.

Actually, let me first run the pipeline script on the new skill's SKILL.md and AGENTS.md, and also on the updated markdown-generation SKILL.md and AGENTS.md, and skill-factory SKILL.md.

But wait - I should also check if there are other skills that reference markdown-generation's companion scripts or lint workflow that need updating. Let me search for any remaining references.

Now let me run lint on all edited files and check for any remaining issues.


**Tool: bash**

**Input:**
```json
{
  "command": "cd /Users/dk/lab-data/ai-suite && markdownlint-cli2 .agents/skills/general/markdown-lint-workflow/SKILL.md .agents/skills/general/markdown-lint-workflow/AGENTS.md .agents/skills/markdown-generation/SKILL.md .agents/skills/markdown-generation/AGENTS.md .agents/skills/skill-factory/SKILL.md AGENTS.md 2>&1 | head -50",
  "description": "Run markdownlint on all edited files"
}
```

**Output:**
```
markdownlint-cli2 v0.22.1 (markdownlint v0.40.0)
Finding: .agents/skills/general/markdown-lint-workflow/SKILL.md .agents/skills/general/markdown-lint-workflow/AGENTS.md .agents/skills/markdown-generation/SKILL.md .agents/skills/markdown-generation/AGENTS.md .agents/skills/skill-factory/SKILL.md AGENTS.md
Linting: 6 file(s)
Summary: 96 error(s)
.agents/skills/general/markdown-lint-workflow/AGENTS.md:7:121 error MD013/line-length Line length [Expected: 120; Actual: 201]
.agents/skills/general/markdown-lint-workflow/AGENTS.md:8:121 error MD013/line-length Line length [Expected: 120; Actual: 177]
.agents/skills/general/markdown-lint-workflow/AGENTS.md:10:121 error MD013/line-length Line length [Expected: 120; Actual: 139]
.agents/skills/general/markdown-lint-workflow/SKILL.md:170 error relative-links Relative links should be valid ["../markdown-generation/SKILL.md" should exist in the file system]
.agents/skills/general/markdown-lint-workflow/SKILL.md:172 error relative-links Relative links should be valid ["../skill-factory/SKILL.md" should exist in the file system]
.agents/skills/markdown-generation/AGENTS.md:3:121 error MD013/line-length Line length [Expected: 120; Actual: 201]
.agents/skills/skill-factory/SKILL.md:72:121 error MD013/line-length Line length [Expected: 120; Actual: 477]
.agents/skills/skill-factory/SKILL.md:109:121 error MD013/line-length Line length [Expected: 120; Actual: 276]
.agents/skills/skill-factory/SKILL.md:174:121 error MD013/line-length Line length [Expected: 120; Actual: 251]
.agents/skills/skill-factory/SKILL.md:211:121 error MD013/line-length Line length [Expected: 120; Actual: 564]
.agents/skills/skill-factory/SKILL.md:222:121 error MD013/line-length Line length [Expected: 120; Actual: 307]
.agents/skills/skill-factory/SKILL.md:228:121 error MD013/line-length Line length [Expected: 120; Actual: 158]
.agents/skills/skill-factory/SKILL.md:229:121 error MD013/line-length Line length [Expected: 120; Actual: 163]
.agents/skills/skill-factory/SKILL.md:230:121 error MD013/line-length Line length [Expected: 120; Actual: 204]
.agents/skills/skill-factory/SKILL.md:231:121 error MD013/line-length Line length [Expected: 120; Actual: 358]
.agents/skills/skill-factory/SKILL.md:232:121 error MD013/line-length Line length [Expected: 120; Actual: 207]
.agents/skills/skill-factory/SKILL.md:236:121 error MD013/line-length Line length [Expected: 120; Actual: 347]
.agents/skills/skill-factory/SKILL.md:242:121 error MD013/line-length Line length [Expected: 120; Actual: 132]
.agents/skills/skill-factory/SKILL.md:243:121 error MD013/line-length Line length [Expected: 120; Actual: 159]
.agents/skills/skill-factory/SKILL.md:244:121 error MD013/line-length Line length [Expected: 120; Actual: 190]
.agents/skills/skill-factory/SKILL.md:245:121 error MD013/line-length Line length [Expected: 120; Actual: 181]
.agents/skills/skill-factory/SKILL.md:249:121 error MD013/line-length Line length [Expected: 120; Actual: 350]
.agents/skills/skill-factory/SKILL.md:255:121 error MD013/line-length Line length [Expected: 120; Actual: 194]
.agents/skills/skill-factory/SKILL.md:256:121 error MD013/line-length Line length [Expected: 120; Actual: 175]
.agents/skills/skill-factory/SKILL.md:258:121 error MD013/line-length Line length [Expected: 120; Actual: 134]
.agents/skills/skill-factory/SKILL.md:262:121 error MD013/line-length Line length [Expected: 120; Actual: 297]
.agents/skills/skill-factory/SKILL.md:346:121 error MD013/line-length Line length [Expected: 120; Actual: 394]
.agents/skills/skill-factory/SKILL.md:372 error MD031/blanks-around-fences Fenced code blocks should be surrounded by blank lines [Context: "```bash"]
.agents/skills/skill-factory/SKILL.md:374 error MD031/blanks-around-fences Fenced code blocks should be surrounded by blank lines [Context: "```"]
.agents/skills/skill-factory/SKILL.md:388:121 error MD013/line-length Line length [Expected: 120; Actual: 244]
.agents/skills/skill-factory/SKILL.md:393:121 error MD013/line-length Line length [Expected: 120; Actual: 179]
.agents/skills/skill-factory/SKILL.md:396:121 error MD013/line-length Line length [Expected: 120; Actual: 352]
.agents/skills/skill-factory/SKILL.md:400:121 error MD013/line-length Line length [Expected: 120; Actual: 354]
.agents/skills/skill-factory/SKILL.md:410:121 error MD013/line-length Line length [Expected: 120; Actual: 372]
.agents/skills/skill-factory/SKILL.md:423:121 error MD013/line-length Line length [Expected: 120; Actual: 741]
.agents/skills/skill-factory/SKILL.md:425:121 error MD013/line-length Line length [Expected: 120; Actual: 165]
.agents/skills/skill-factory/SKILL.md:427:121 error MD013/line-length Line length [Expected: 120; Actual: 168]
.agents/skills/skill-factory/SKILL.md:429:121 error MD013/line-length Line length [Expected: 120; Actual: 320]
.agents/skills/skill-factory/SKILL.md:431:121 error MD013/line-length Line length [Expected: 120; Actual: 147]
.agents/skills/skill-factory/SKILL.md:433:121 error MD013/line-length Line length [Expected: 120; Actual: 335]
.agents/skills/skill-factory/SKILL.md:435:121 error MD013/line-length Line length [Expected: 120; Actual: 292]
.agents/skills/skill-factory/SKILL.md:437:121 error MD013/line-length Line length [Expected: 120; Actual: 560]
.agents/skills/skill-factory/SKILL.md:453:121 error MD013/line-length Line length [Expected: 120; Actual: 235]
.agents/skills/skill-factory/SKILL.md:455:121 error MD013/line-length Line length [Expected: 120; Actual: 216]
.agents/skills/skill-factory/SKILL.md:456:121 error MD013/line-length Line length [Expected: 120; Actual: 405]
.agents/skills/skill-factory/SKILL.md:457:121 error MD013/line-length Line length [Expected: 120; Actual: 360]

```

---

## Assistant (Build · Nemotron 3 Ultra 550B A55B · 148.3s)

_Thinking:_

There are many line length errors and some other issues. The skill-factory has many long lines (tables with long descriptions). That's expected and likely not something I should fix since it's pre-existing.

But there are two issues I introduced:
1. The AGENTS.md files have long lines (expected - table descriptions)
2. The markdown-lint-workflow SKILL.md has relative-links errors for `../markdown-generation/SKILL.md` and `../skill-factory/SKILL.md`

The relative links should exist. Let me check:
- `../markdown-generation/SKILL.md` from `.agents/skills/general/markdown-lint-workflow/` → that would be `.agents/skills/markdown-generation/SKILL.md` which DOES exist
- `../skill-factory/SKILL.md` from `.agents/skills/general/markdown-lint-workflow/` → that would be `.agents/skills/skill-factory/SKILL.md` which DOES exist

But wait - the relative-links rule is checking if the target file exists in the file system. The issue might be that the linter is running from a different working directory. Let me check the config.

Actually, looking at the error more carefully:
```
.agents/skills/general/markdown-lint-workflow/SKILL.md:170 error relative-links Relative links should be valid ["../markdown-generation/SKILL.md" should exist in the file system]
```

This is likely because the relative link validator is checking from the current working directory, not from the file's directory. Let me check how the relative links rule is configured.

Actually, looking at markdown-generation, it has a custom rule for relative links (markdownlint-rule-relative-links). The new skill might not have that configured. Let me check the .markdownlint.jsonc.

Wait, the linter is configured with the project's .markdownlint.jsonc which has the relative-links rule. The issue is that the relative-links rule checks if the target file exists relative to the project root or the file's directory? Let me check.

Actually, the markdownlint-rule-relative-links rule has a `root_path` configuration. Let me check the project's config.

Let me check if this is a pre-existing issue or if I need to add the custom rule configuration to the new skill. But actually, looking at the error, it seems like the relative links ARE valid (the files exist), so maybe it's just a path resolution issue.

Let me first run the fix pipeline on the new skill's SKILL.md and AGENTS.md to fix the line length issues.

The new files have line-length issues and relative link validation issues. Let me run the fix pipeline on them.


**Tool: bash**

**Input:**
```json
{
  "command": "cd /Users/dk/lab-data/ai-suite && python3 .agents/skills/general/markdown-lint-workflow/scripts/fix-markdown-pipeline.py .agents/skills/general/markdown-lint-workflow/SKILL.md .agents/skills/general/markdown-lint-workflow/AGENTS.md 2>&1",
  "description": "Run pipeline on new skill files"
}
```

**Output:**
```
.agents/skills/general/markdown-lint-workflow/AGENTS.md:7:121 error MD013/line-length Line length [Expected: 120; Actual: 201]
.agents/skills/general/markdown-lint-workflow/AGENTS.md:8:121 error MD013/line-length Line length [Expected: 120; Actual: 177]
.agents/skills/general/markdown-lint-workflow/AGENTS.md:10:121 error MD013/line-length Line length [Expected: 120; Actual: 139]
.agents/skills/general/markdown-lint-workflow/SKILL.md:170 error relative-links Relative links should be valid ["../markdown-generation/SKILL.md" should exist in the file system]
.agents/skills/general/markdown-lint-workflow/SKILL.md:172 error relative-links Relative links should be valid ["../skill-factory/SKILL.md" should exist in the file system]
.agents/skills/general/markdown-lint-workflow/SKILL.md:20:1 error MD004/ul-style Unordered list style [Expected: dash; Actual: asterisk]
.agents/skills/general/markdown-lint-workflow/SKILL.md:70:1 error MD004/ul-style Unordered list style [Expected: dash; Actual: asterisk]
.agents/skills/general/markdown-lint-workflow/SKILL.md:144:1 error MD004/ul-style Unordered list style [Expected: dash; Actual: asterisk]
.agents/skills/general/markdown-lint-workflow/SKILL.md:166:1 error MD004/ul-style Unordered list style [Expected: dash; Actual: asterisk]
.agents/skills/general/markdown-lint-workflow/SKILL.md:170 error relative-links Relative links should be valid ["../markdown-generation/SKILL.md" should exist in the file system]
.agents/skills/general/markdown-lint-workflow/SKILL.md:172 error relative-links Relative links should be valid ["../skill-factory/SKILL.md" should exist in the file system]
============================================================
STEP 1: markdownlint-cli2 --fix
============================================================
[step-1] markdownlint-cli2 --fix .agents/skills/general/markdown-lint-workflow/SKILL.md .agents/skills/general/markdown-lint-workflow/AGENTS.md
markdownlint-cli2 v0.22.1 (markdownlint v0.40.0)
Finding: .agents/skills/general/markdown-lint-workflow/SKILL.md .agents/skills/general/markdown-lint-workflow/AGENTS.md
Linting: 2 file(s)
Summary: 5 error(s)
[INFO] --fix finished (non-zero exit is normal when unfixable issues remain)

============================================================
STEP 2: Companion scripts
============================================================
[  fix-table-separators.py] /Users/dk/.local/share/mise/installs/python/3.11.9/bin/python3 /Users/dk/lab-data/ai-suite/.agents/skills/general/markdown-lint-workflow/scripts/fix-table-separators.py .agents/skills/general/markdown-lint-workflow/SKILL.md .agents/skills/general/markdown-lint-workflow/AGENTS.md
Checking .agents/skills/general/markdown-lint-workflow/SKILL.md...
Checking .agents/skills/general/markdown-lint-workflow/AGENTS.md...
[  fix-fenced-code-language.py] /Users/dk/.local/share/mise/installs/python/3.11.9/bin/python3 /Users/dk/lab-data/ai-suite/.agents/skills/general/markdown-lint-workflow/scripts/fix-fenced-code-language.py .agents/skills/general/markdown-lint-workflow/SKILL.md .agents/skills/general/markdown-lint-workflow/AGENTS.md
[  fix-container-fence.py] /Users/dk/.local/share/mise/installs/python/3.11.9/bin/python3 /Users/dk/lab-data/ai-suite/.agents/skills/general/markdown-lint-workflow/scripts/fix-container-fence.py .agents/skills/general/markdown-lint-workflow/SKILL.md .agents/skills/general/markdown-lint-workflow/AGENTS.md
[  wrap-long-lines.py] /Users/dk/.local/share/mise/installs/python/3.11.9/bin/python3 /Users/dk/lab-data/ai-suite/.agents/skills/general/markdown-lint-workflow/scripts/wrap-long-lines.py --max 120 .agents/skills/general/markdown-lint-workflow/SKILL.md .agents/skills/general/markdown-lint-workflow/AGENTS.md
Checking .agents/skills/general/markdown-lint-workflow/SKILL.md...
Checking .agents/skills/general/markdown-lint-workflow/AGENTS.md...
  Wrapped .agents/skills/general/markdown-lint-workflow/AGENTS.md
[  fix-emphasis-as-heading.py] /Users/dk/.local/share/mise/installs/python/3.11.9/bin/python3 /Users/dk/lab-data/ai-suite/.agents/skills/general/markdown-lint-workflow/scripts/fix-emphasis-as-heading.py .agents/skills/general/markdown-lint-workflow/SKILL.md .agents/skills/general/markdown-lint-workflow/AGENTS.md
  Fixed .agents/skills/general/markdown-lint-workflow/SKILL.md
[  fix-list-style.py] /Users/dk/.local/share/mise/installs/python/3.11.9/bin/python3 /Users/dk/lab-data/ai-suite/.agents/skills/general/markdown-lint-workflow/scripts/fix-list-style.py .agents/skills/general/markdown-lint-workflow/SKILL.md .agents/skills/general/markdown-lint-workflow/AGENTS.md
[  fix-heading-spacing.py] /Users/dk/.local/share/mise/installs/python/3.11.9/bin/python3 /Users/dk/lab-data/ai-suite/.agents/skills/general/markdown-lint-workflow/scripts/fix-heading-spacing.py .agents/skills/general/markdown-lint-workflow/SKILL.md .agents/skills/general/markdown-lint-workflow/AGENTS.md

============================================================
STEP 3: Final audit
============================================================
[audit] markdownlint-cli2 .agents/skills/general/markdown-lint-workflow/SKILL.md .agents/skills/general/markdown-lint-workflow/AGENTS.md
markdownlint-cli2 v0.22.1 (markdownlint v0.40.0)
Finding: .agents/skills/general/markdown-lint-workflow/SKILL.md .agents/skills/general/markdown-lint-workflow/AGENTS.md
Linting: 2 file(s)
Summary: 6 error(s)

Remaining lint issues found. See output above.

```

---

## Assistant (Build · Nemotron 3 Ultra 550B A55B · 196.5s)

_Thinking:_

The remaining errors are:
1. MD013 line-length on AGENTS.md (table descriptions too long) - these are in the table cells, need manual fix
2. MD004 unordered list style (asterisk instead of dash) on SKILL.md - wait, fix-list-style should have fixed this? Let me check the SKILL.md - it seems the list style was not fixed in the first pass.

Wait, the output shows "Fixed .agents/skills/general/markdown-lint-workflow/SKILL.md" for fix-emphasis-as-heading.py, but the unordered list style errors persisted. Let me check if fix-list-style.py was run - it was listed but didn't show "Fixed". Let me check the file.

Actually, the MD004 errors are on lines 20, 70, 144, 166. Those are likely in the YAML frontmatter or some other part that fix-list-style.py doesn't handle (it might only handle body lists). Let me check the SKILL.md.

Also, the relative-links errors - the files DO exist. The issue is likely the root_path configuration. Let me check if the relative-links rule is even enabled in the project's config.

Let me also run the pipeline on the updated markdown-generation files.

Let me run the pipeline on the other updated files too.


**Tool: bash**

**Input:**
```json
{
  "command": "cd /Users/dk/lab-data/ai-suite && python3 .agents/skills/general/markdown-lint-workflow/scripts/fix-markdown-pipeline.py .agents/skills/markdown-generation/SKILL.md .agents/skills/markdown-generation/AGENTS.md 2>&1",
  "description": "Run pipeline on markdown-generation files"
}
```

**Output:**
```
.agents/skills/markdown-generation/AGENTS.md:3:121 error MD013/line-length Line length [Expected: 120; Actual: 201]
.agents/skills/markdown-generation/SKILL.md:20:1 error MD004/ul-style Unordered list style [Expected: asterisk; Actual: dash]
.agents/skills/markdown-generation/SKILL.md:21:1 error MD004/ul-style Unordered list style [Expected: asterisk; Actual: dash]
.agents/skills/markdown-generation/SKILL.md:23:1 error MD004/ul-style Unordered list style [Expected: asterisk; Actual: dash]
.agents/skills/markdown-generation/SKILL.md:27:1 error MD004/ul-style Unordered list style [Expected: asterisk; Actual: dash]
.agents/skills/markdown-generation/SKILL.md:28:1 error MD004/ul-style Unordered list style [Expected: asterisk; Actual: dash]
.agents/skills/markdown-generation/SKILL.md:29:1 error MD004/ul-style Unordered list style [Expected: asterisk; Actual: dash]
.agents/skills/markdown-generation/SKILL.md:33:1 error MD004/ul-style Unordered list style [Expected: asterisk; Actual: dash]
.agents/skills/markdown-generation/SKILL.md:35:1 error MD004/ul-style Unordered list style [Expected: asterisk; Actual: dash]
.agents/skills/markdown-generation/SKILL.md:41:1 error MD004/ul-style Unordered list style [Expected: asterisk; Actual: dash]
.agents/skills/markdown-generation/SKILL.md:42:1 error MD004/ul-style Unordered list style [Expected: asterisk; Actual: dash]
.agents/skills/markdown-generation/SKILL.md:43:1 error MD004/ul-style Unordered list style [Expected: asterisk; Actual: dash]
.agents/skills/markdown-generation/SKILL.md:44:1 error MD004/ul-style Unordered list style [Expected: asterisk; Actual: dash]
.agents/skills/markdown-generation/SKILL.md:50:1 error MD004/ul-style Unordered list style [Expected: asterisk; Actual: dash]
.agents/skills/markdown-generation/SKILL.md:51:1 error MD004/ul-style Unordered list style [Expected: asterisk; Actual: dash]
.agents/skills/markdown-generation/SKILL.md:52:5 error MD004/ul-style Unordered list style [Expected: asterisk; Actual: dash]
.agents/skills/markdown-generation/SKILL.md:53:5 error MD004/ul-style Unordered list style [Expected: asterisk; Actual: dash]
.agents/skills/markdown-generation/SKILL.md:54:5 error MD004/ul-style Unordered list style [Expected: asterisk; Actual: dash]
.agents/skills/markdown-generation/SKILL.md:91:4 error MD004/ul-style Unordered list style [Expected: asterisk; Actual: dash]
.agents/skills/markdown-generation/SKILL.md:92:4 error MD004/ul-style Unordered list style [Expected: asterisk; Actual: dash]
.agents/skills/markdown-generation/SKILL.md:93:4 error MD004/ul-style Unordered list style [Expected: asterisk; Actual: dash]
.agents/skills/markdown-generation/SKILL.md:106:1 error MD004/ul-style Unordered list style [Expected: asterisk; Actual: dash]
.agents/skills/markdown-generation/SKILL.md:107:1 error MD004/ul-style Unordered list style [Expected: asterisk; Actual: dash]
.agents/skills/markdown-generation/SKILL.md:109:1 error MD004/ul-style Unordered list style [Expected: asterisk; Actual: dash]
.agents/skills/markdown-generation/SKILL.md:110:1 error MD004/ul-style Unordered list style [Expected: asterisk; Actual: dash]
.agents/skills/markdown-generation/SKILL.md:116:1 error MD004/ul-style Unordered list style [Expected: asterisk; Actual: dash]
.agents/skills/markdown-generation/SKILL.md:117:1 error MD004/ul-style Unordered list style [Expected: asterisk; Actual: dash]
============================================================
STEP 1: markdownlint-cli2 --fix
============================================================
[step-1] markdownlint-cli2 --fix .agents/skills/markdown-generation/SKILL.md .agents/skills/markdown-generation/AGENTS.md
markdownlint-cli2 v0.22.1 (markdownlint v0.40.0)
Finding: .agents/skills/markdown-generation/SKILL.md .agents/skills/markdown-generation/AGENTS.md
Linting: 2 file(s)
Summary: 1 error(s)
[INFO] --fix finished (non-zero exit is normal when unfixable issues remain)

============================================================
STEP 2: Companion scripts
============================================================
[  fix-table-separators.py] /Users/dk/.local/share/mise/installs/python/3.11.9/bin/python3 /Users/dk/lab-data/ai-suite/.agents/skills/general/markdown-lint-workflow/scripts/fix-table-separators.py .agents/skills/markdown-generation/SKILL.md .agents/skills/markdown-generation/AGENTS.md
Checking .agents/skills/markdown-generation/SKILL.md...
Checking .agents/skills/markdown-generation/AGENTS.md...
[  fix-fenced-code-language.py] /Users/dk/.local/share/mise/installs/python/3.11.9/bin/python3 /Users/dk/lab-data/ai-suite/.agents/skills/general/markdown-lint-workflow/scripts/fix-fenced-code-language.py .agents/skills/markdown-generation/SKILL.md .agents/skills/markdown-generation/AGENTS.md
[  fix-container-fence.py] /Users/dk/.local/share/mise/installs/python/3.11.9/bin/python3 /Users/dk/lab-data/ai-suite/.agents/skills/general/markdown-lint-workflow/scripts/fix-container-fence.py .agents/skills/markdown-generation/SKILL.md .agents/skills/markdown-generation/AGENTS.md
[  wrap-long-lines.py] /Users/dk/.local/share/mise/installs/python/3.11.9/bin/python3 /Users/dk/lab-data/ai-suite/.agents/skills/general/markdown-lint-workflow/scripts/wrap-long-lines.py --max 120 .agents/skills/markdown-generation/SKILL.md .agents/skills/markdown-generation/AGENTS.md
Checking .agents/skills/markdown-generation/SKILL.md...
  Wrapped .agents/skills/markdown-generation/SKILL.md
Checking .agents/skills/markdown-generation/AGENTS.md...
  Wrapped .agents/skills/markdown-generation/AGENTS.md
[  fix-emphasis-as-heading.py] /Users/dk/.local/share/mise/installs/python/3.11.9/bin/python3 /Users/dk/lab-data/ai-suite/.agents/skills/general/markdown-lint-workflow/scripts/fix-emphasis-as-heading.py .agents/skills/markdown-generation/SKILL.md .agents/skills/markdown-generation/AGENTS.md
  Fixed .agents/skills/markdown-generation/SKILL.md
[  fix-list-style.py] /Users/dk/.local/share/mise/installs/python/3.11.9/bin/python3 /Users/dk/lab-data/ai-suite/.agents/skills/general/markdown-lint-workflow/scripts/fix-list-style.py .agents/skills/markdown-generation/SKILL.md .agents/skills/markdown-generation/AGENTS.md
[  fix-heading-spacing.py] /Users/dk/.local/share/mise/installs/python/3.11.9/bin/python3 /Users/dk/lab-data/ai-suite/.agents/skills/general/markdown-lint-workflow/scripts/fix-heading-spacing.py .agents/skills/markdown-generation/SKILL.md .agents/skills/markdown-generation/AGENTS.md

============================================================
STEP 3: Final audit
============================================================
[audit] markdownlint-cli2 .agents/skills/markdown-generation/SKILL.md .agents/skills/markdown-generation/AGENTS.md
markdownlint-cli2 v0.22.1 (markdownlint v0.40.0)
Finding: .agents/skills/markdown-generation/SKILL.md .agents/skills/markdown-generation/AGENTS.md
Linting: 2 file(s)
Summary: 26 error(s)

Remaining lint issues found. See output above.

```

---

## Assistant (Build · Nemotron 3 Ultra 550B A55B · 183.3s)

_Thinking:_

Interesting - the markdown-generation SKILL.md has MD004 errors with "Expected: asterisk; Actual: dash" - that's the opposite of what I saw for the new skill! The markdown-generation skill uses dashes for lists, and the linter is now expecting asterisks. This is because the markdownlint config has MD004 set to expect asterisk style by default.

Wait, let me check the .markdownlint.jsonc config - the fix-list-style.py script converts asterisk to dash, but the linter might be configured to prefer asterisk!

Let me check the config. This is strange - the fix-list-style.py script converts asterisk to dash to satisfy MD004 (which by default expects consistent style, usually dash), but the config might have been customized.

Actually, looking at the error message: "Expected: asterisk; Actual: dash" - this means the linter is configured to expect asterisk style, not dash!

Let me check the .markdownlint.jsonc.

The linter config expects asterisk, but the scripts convert to dash. Let me check the markdownlint config.


**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/.markdownlint.jsonc"
}
```

**Error:**
```
File not found: /Users/dk/lab-data/ai-suite/.markdownlint.jsonc
```

---

## Assistant (Build · Nemotron 3 Ultra 550B A55B · 8792.7s)

_Thinking:_

No .markdownlint.jsonc at root. Let me check the ai-agent-rules for the reference config.

**Tool: bash**

**Input:**
```json
{
  "command": "find /Users/dk/lab-data/ai-suite -name \".markdownlint.jsonc\" -type f 2>/dev/null",
  "description": "Find markdownlint config"
}
```

**Output:**
```
(no output)
```

---

## Assistant (Build · Nemotron 3 Ultra 550B A55B · 717.4s)

_Thinking:_

There's no .markdownlint.jsonc in the project. Let me check the markdownlint-cli2 default behavior. By default, MD004 expects consistent style (dash or asterisk) but doesn't enforce which one. However, looking at the errors, they show "Expected: asterisk" - which suggests maybe the default has changed, or there's a default config somewhere.

Wait, looking at the errors more carefully:
- For markdown-lint-workflow SKILL.md: "Expected: dash; Actual: asterisk" (meaning it wants dash)
- For markdown-generation SKILL.md: "Expected: asterisk; Actual: dash" (meaning it wants asterisk)

This is contradictory. Let me check if there's a .markdownlint-cli2.jsonc or something. Or maybe the linter is inferring the style from the first list it sees.

Actually, let me re-read the errors:
- markdown-lint-workflow SKILL.md line 20: "MD004/ul-style Unordered list style [Expected: dash; Actual: asterisk]"
- markdown-generation SKILL.md line 20: "MD004/ul-style Unordered list style [Expected: asterisk; Actual: dash]"

This suggests markdownlint is inferring the style from the first list in each file. The markdown-lint-workflow SKILL.md probably has a dash list first, and markdown-generation SKILL.md has an asterisk list first.

Let me check the first list in each file.

Actually, the fix-list-style.py script should normalize to dash style. Let me check what it does.

Wait, looking at the markdown-generation SKILL.md - it has a lot of lists using dashes. But the error says "Expected: asterisk" which means the linter saw an asterisk list first.

Let me look at the raw file around line 20 of markdown-generation SKILL.md.

Actually, the issue might be that the YAML frontmatter or some other content has an asterisk list that's being picked up. Or maybe the config in the project root is different from what I think.

Let me just run the fix pipeline again but this time, the fix-list-style.py didn't seem to fix the errors in markdown-lint-workflow. Let me check why.

Let me check what's happening with the list style.


**Tool: read**

**Input:**
```json
{
  "filePath": "/Users/dk/lab-data/ai-suite/.agents/skills/general/markdown-lint-workflow/SKILL.md",
  "limit": 30,
  "offset": 15
}
```

**Output:**
```
<path>/Users/dk/lab-data/ai-suite/.agents/skills/general/markdown-lint-workflow/SKILL.md</path>
<type>file</type>
<content>
15: 
16: The companion scripts under [`scripts/`](scripts/) handle patterns that
17: `markdownlint-cli2 --fix` does not resolve (line length, table alignment, fence
18: language tags, list style, heading spacing, etc.).
19: 
20: *
21: 
22: ## 1. The 3-Step Pipeline
23: 
24: Before finalizing ANY markdown file, run these steps in order:
25: 
26: ### Step 1: Auto-Fix
27: 
28: ```bash
29: markdownlint-cli2 --fix <file_path>
30: ```
31: 
32: - Run from the project root where `.markdownlint.jsonc` lives.
33: - Use paths **relative** to the project root — absolute paths can cause the
34:   tool to silently find 0 files (`Linting: 0 file(s)`) and do nothing.
35: 
36: **Caveat:** `markdownlint-cli2 --fix` corrupts bare closing fences for MD040.
37: Do NOT rely on `--fix` for MD040 — Step 2 handles it correctly. See §2.2.
38: 
39: ### Step 2: Companion Scripts
40: 
41: Run ALL companion scripts from [§2](#2-companion-scripts) in the
42: [required execution order](#21-execution-order). Each script accepts
43: `--check` for a dry-run preview; omit `--check` to apply changes in-place.
44: 

(Showing lines 15-44 of 177. Use offset=45 to continue.)
</content>

<system-reminder>
Instructions from: /Users/dk/lab-data/ai-suite/.agents/skills/general/markdown-lint-workflow/AGENTS.md
# AGENTS.md (Markdown Lint Workflow)

Refer to [SKILL.md](./SKILL.md) for the active operational protocol for the 3-step markdown lint fix pipeline.

## Mandates

- **Pipeline Steps**: Run the full 3-step pipeline in order — Step 1: `markdownlint-cli2 --fix`, Step 2: companion
scripts in §2.1 execution order, Step 3: manual fix + final `markdownlint-cli2` audit.
- **Script Invocation**: Use the convenience script `scripts/fix-markdown-pipeline.py` for one-shot execution, or call
companion scripts individually with `--check` for dry-run.
- **Execution Order**: Companion scripts MUST run in the order defined in §2.1 to avoid re-introducing lint errors.
- **MD040 Caveat**: Do NOT use `markdownlint-cli2 --fix` for MD040 — use `fix-fenced-code-language.py` which correctly
handles fence state.
- **Post-Fix Check**: After running the pipeline, verify continuation-line indent with `list-indent-consistency` skill.

## Cross-References

- `markdown-generation` — consumes this skill for post-generation linting
- `skill-factory` §3 — consumes this skill for post-drafting linting
- `list-indent-consistency` — detect and repair indent drift after fix scripts
- `markdownlint-cli2` — the underlying lint tool

</system-reminder>
```

---

## Assistant (Build · Nemotron 3 Ultra 550B A55B · 253.1s)

_Thinking:_

There's an empty line 20 with just `*` - that's an asterisk list item! That's what's causing the MD004 error. The linter sees this and expects asterisk style, but the rest of the document uses dashes.

Let me check line 70, 144, 166 too.

I need to fix these stray asterisk items. They might be from my heredoc creation. Let me check the file more carefully and fix them.

There's a stray asterisk on line 20. Let me check all the error lines and fix them.


**Tool: bash**

**Input:**
```json
{
  "command": "sed -n '20p;70p;144p;166p' /Users/dk/lab-data/ai-suite/.agents/skills/general/markdown-lint-workflow/SKILL.md",
  "description": "Check error lines in new skill"
}
```

**Output:**
```
*
*
*
*

```

---

## Assistant (Build · Nemotron 3 Ultra 550B A55B · 1335.4s)

---

## User

Continue

---

## Assistant (Build · Qwen3 Coder 480B A35B Instruct · 1.5s)

---

## User

Continue

---

## User

---

## Assistant (Compaction · Qwen2.5 Coder 32b Instruct · 0.3s)

---

## User

Continue

---

## Assistant (Compaction · usdcode · 0.2s)

---

## User

Continue

---

## Assistant (Compaction · DeepSeek V4 Pro · 452.0s)

---

