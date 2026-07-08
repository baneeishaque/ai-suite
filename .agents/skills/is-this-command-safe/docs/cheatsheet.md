---
name: Shell Command Safety Cheatsheet
description: Curated allowlist of common inspection-toolkit commands with safety verdicts and destructive-flag warnings.
category: Core Agent Behavior
---

# Shell Command Safety Cheatsheet

Quick-reference allowlist for commands a cautious developer or AI-agent supervisor wants
pre-vetted. Each entry uses the four-tier classification defined in
[`SKILL.md §3`](../SKILL.md#3-safety-classification-four-tiers).

Verdict key: ✅ SAFE · 🟡 SAFE-IF-PIPED · ⚠️ HAS-DESTRUCTIVE-FLAGS · ❌ MUTATES

***

## Simplified Safety Table

| Command / Binary | Verdict | Destructive form(s) | Safe alternative / dry-run |
| :--- | :---: | :--- | :--- |
| `awk` | ⚠️ | `system("…")` · `\| sh` · `getline cmd \| …` · `-f <script>` | pure-projection forms only: `awk '{print $1}' <file>`, `awk -F: '{…}' <file>` |
| `brew leaves` | ✅ | — | n/a |
| `brew list` | ✅ | — | n/a |
| `brew outdated` | ✅ | — | n/a |
| `cat` | ⚠️ | `cat > <file>` (overwrites); ONLY safe exception: hardcoded `cat > /tmp/cmds-parity.txt << EOF` → `batch-coverage-check.py` chain | read-only: `cat <file>`; or pipe-sink `<safe-cmd> \| cat` (read-only pass-through, pager-equivalent) |
| `cd` | ✅ | — | n/a |
| `echo` | ✅ | — | n/a |
| `ffprobe` | ✅ | — | n/a |
| `diff` | ✅ | — | n/a |
| `find` | 🟡 | `-delete` · `-exec rm` · `-exec mv` · `-exec sed -i` | `find … -print` first |
| `git branch -a` | ✅ | — | n/a |
| `git branch -vv` | ✅ | — | n/a |
| `git branch --show-current` | ✅ | — | n/a |
| `git check-ignore` | ✅ | — | n/a |
| `git diff` | ✅ | — | n/a |
| `git log` | ✅ | — | n/a |
| `git ls-files` | 🟡 | `\| xargs rm` · `\| xargs sed -i` | `git ls-files` alone |
| `git ls-tree` | 🟡 | downstream `xargs` | inspect output alone first |
| `git merge-base` | ✅ | — | n/a |
| `git show` | ✅ | — | n/a |
| `git stash list` | ✅ | — | n/a |
| `git status` | ✅ | — | n/a |
| `grep` | 🟡 | `\| xargs rm` · `\| xargs sed -i` | `grep` alone |
| `head` | ✅ | — | n/a |
| `less` | ✅ | — | n/a |
| `ls` | 🟡 | `\| xargs rm` | `ls` alone |
| `xargs` | 🟡 | `xargs rm` · `xargs sed -i` · `xargs sh` · `xargs cp` · `xargs mv` | `xargs grep` · `xargs head` · `xargs tail` · `xargs wc` · `xargs cat` (read-only downstream only) |
| `lsof` | ✅ | — | n/a |
| `markdownlint-cli2` | ✅ / ⚠️ | `--fix` (edits files in-place) | omit `--fix` |
| `mdfind` | 🟡 | downstream `xargs` | `mdfind` alone |
| `mdls` | ✅ | — | n/a |
| `mkdir` | ❌ | always mutates | `ls -d <path>` to check existence first |
| `python3` | ⚠️ | depends on script invoked | hardcode trusted script path in regex |
| `pwd` | ✅ | — | n/a |
| `sed` | ⚠️ | `-i` (in-place edit) | print-only: `sed -n 'N,Mp' <file>` |
| `sort` | 🟡 | `-o <file>` (writes sorted output, may clobber) | `sort <file>` alone (stdout) |
| `tail` | ✅ | — | n/a |
| `true` | ✅ | — | n/a |
| `wc` | ✅ | — | n/a |
| `which` | ✅ | — | n/a |
| `/usr/libexec/java_home` | ✅ | — | n/a |

***

## File Search & Metadata

### `find`

- **Verdict**: 🟡 SAFE-IF-PIPED
- **What it does**: Traverses the filesystem and prints matching paths. By itself it is read-only.
- **Destructive forms**:
  - `find / -name "*.log" -delete` → deletes every match.
  - `find . -name "*.txt" -exec rm {} \;` → runs `rm` on each match.
  - `find . -name "*.js" -exec sed -i 's/foo/bar/g' {} \;` → in-place edit.
- **Safe workflow**: always run without action flags first to preview results, then add `-delete`
  or `-exec` only after confirming the match set.

```bash
# Safe preview
find /path -name "*.log" -print

# Only after confirming — destructive
find /path -name "*.log" -delete
```
- **Safe-chain participation (entry [37])**: a conservative
  `find <paths> <flag>* [| head|tail|sort|grep]` arm is included so
  `find ... && echo && find ... && du ...` chains auto-approve. The standalone
  `find | xargs grep` form remains in entry [39].

### `mdfind`

- **Verdict**: 🟡 SAFE-IF-PIPED
- **What it does**: macOS Spotlight metadata search. Read-only output; safe alone.
- **Destructive form**: `mdfind … | xargs rm` — pipeline inherits downstream destructiveness.
- **Safe workflow**: inspect `mdfind` output alone before piping.

### `mdls`

- **Verdict**: ✅ SAFE
- **What it does**: Lists macOS extended metadata attributes (kMDItem*) of a file. Read-only.

### `ffprobe`

- **Verdict**: ✅ SAFE
- **What it does**: Multimedia stream analyzer (FFmpeg project). Reads media files and prints
  container format, codec info, resolution, bitrate, duration, metadata, and stream details to
  stdout. Supports JSON, XML, CSV, and plain-text output formats via `-print_format` / `-of`.
- **Notable flags**: `-show_format`, `-show_streams`, `-show_entries`, `-select_streams`,
  `-print_format json`, `-v quiet` — all read-only information extraction flags.
- **Contrast**: `ffmpeg` (the transcoder) is a separate binary with MUTATES capability and is
  NOT covered by this row.
- **Pipeline caution**: `ffprobe` output piped to a destructive downstream (`xargs rm`,
  `xargs sed -i`) inherits the same mutating risk as any `SAFE-IF-PIPED` binary — evaluate
  the full pipeline, not just ffprobe alone.

***

## Text Search

### `awk`

- **Verdict**: ⚠️ SAFE-WITH-QUALIFICATION — pattern-scanning language. Safety depends on the
  script body, not the binary alone.
- **SAFE**: pure projection / aggregation that only reads input and writes to stdout,
  e.g. `awk '{print $1}' file.txt`, `awk -F: '{print $1, $3}' /etc/passwd`,
  `awk '/^[a-z]/ {print NR": "$0}' file`.
- **MUTATES (refuse / classify by the embedded command)**:
  - `awk 'BEGIN{system("rm -rf ~")}'` — `system(…)` executes a shell command.
  - `awk '{print}' | sh` — pipeline target is a shell.
  - `awk '{cmd="…"; cmd | getline x}'` — `getline … | "cmd"` runs an external command.
  - `awk -f script.awk` — loads an external script whose contents must be vetted.
- **Auto-approve pattern**: pin to inline scripts that do **not** contain `system(`,
  do **not** end in `| sh`, and do **not** use `-f`. Never auto-approve a generic
  `awk .*` catch-all.

### `grep`

- **Verdict**: 🟡 SAFE-IF-PIPED
- **What it does**: Searches file contents for patterns. Does not modify files.
- **Destructive pipeline**:
  - `grep -rl "debug" . | xargs rm` → deletes all files containing "debug".
  - `grep -rl "old" . | xargs sed -i 's/old/new/g'` → in-place mass replace.
- **Safe workflow**: run `grep` alone to confirm the match set, then decide on downstream action.
- **Auto-approve flag forms**: the arg slot MUST admit four shapes — bare token, single-quoted
  string, double-quoted string, **and** `--<long-flag>=<quoted-glob>` (e.g. `--include="*.kt"`,
  `--exclude='*.bak'`). The first three cover positional pattern + path args; the fourth covers
  long-option flags whose value is a quoted glob, which `ripgrep`-style multi-extension scans rely
  on. Example arg-alternation slot:
  `( ([^;&|<>$\`()'" ]+|'[^']*'|"[^"]*"|--[a-z-]+="[^"]*"|--[a-z-]+='[^']*'))+`.

- **Concatenated quoted/bareword arg form**: shells permit `""Account"\|fun..."`
  (empty-string + bareword + quoted-string concatenated as a single argv token). Entry [25]
  in settings.json allows this by repeating the per-token alternation: `( (TOKEN)+)+`.

### `sed`

- **Verdict**: ⚠️ SAFE-WITH-QUALIFICATION — safety depends on the flag set.
- **SAFE**: print-only forms that emit to stdout, e.g. `sed -n '1,200p' <file>`,
  `sed 's/old/new/' <file>` (stream substitution to stdout). No file is modified.
- **MUTATES**: `sed -i …` (or BSD `sed -i ''`) edits files in-place. Never auto-approve
  any invocation containing `-i`.
- **Auto-approve pattern**: pin to specific print-only invocations,
  e.g. `/^sed -n '[0-9]+(,[0-9]+)?p'( [^;&|<>$`()]+)?$/`. Never a generic `sed .*` catch-all.

***

## File Viewing

### `cat`

- **Verdict**: ⚠️ SAFE-WITH-QUALIFICATION — safety depends on usage form.
- **SAFE**: `cat <file>` — reads and prints. Read-only.
- **SAFE (pipe sink)**: `<safe-upstream> | cat` — `cat` with no positional
  argument is a read-only pass-through of stdin, functionally equivalent to
  appending `--no-pager` (or omitting a pager) on tools like `git`. Safe as
  a downstream sink in pipelines whose upstream is already classified SAFE,
  alongside `head`, `tail`, `wc`, `grep`, `sed -n 'N,Mp'`. Auto-approve
  patterns that admit a trailing `( \| (head|tail)( -N)?| \| sed -n 'N,Mp'| \| cat)?`
  slot are canonical — see the `git (status|log|diff|ls-files)` entry under
  [§5.5 of vscode-autoapprove-entry-consolidation](../../vscode-autoapprove-entry-consolidation/SKILL.md#55-tight-token-whitelist-vs-generic-arg-slot).
- **MUTATES**: `cat > <file>` — redirect writes/truncates target file.
- **EXCEPTION (SAFE, hardcoded only)**: The specific chain below is auto-approved as a single
  pattern. No other `cat > /tmp/...` form qualifies:
  ```
  cat > /tmp/cmds-parity.txt << 'EOF'
  <any content>
  EOF

  python3 .../command-autoapprove-onboarding/scripts/batch-coverage-check.py \
      --commands /tmp/cmds-parity.txt \
      --ssot .../safety-table.csv \
      --settings ".../settings.json"
  ```
  Safe because: the tmp file is write-only scratch (not a system path), the consumer is a
  read-only audit script (`batch-coverage-check.py`), and both segments are hardcoded in the
  regex — not a generic `/tmp` or "same filename" rule.
  See [Hardcoded Tmp-Write→Read Exception Pattern](#hardcoded-tmp-writeread-exception-pattern) for the full eligibility criteria.

### `head`

- **Verdict**: ✅ SAFE — Prints first N lines. Read-only.

### `tail`

- **Verdict**: ✅ SAFE — Prints last N lines (or follows a growing file). Read-only.

### `less`

- **Verdict**: ✅ SAFE — Paginated viewer. No mutation.

### `ls`

- **Verdict**: 🟡 SAFE-IF-PIPED — Lists directory contents. Read-only alone. Downstream `\| xargs rm` etc. upgrades verdict.
- **Auto-approve pattern**: pin to a per-segment shape that admits an optional
  `2>&1` and an optional `| (head|tail|wc)` suffix, and allow `&&`-chaining of
  multiple `ls` segments (each segment must itself match the same shape). Example:
  `/^ls( -[a-zA-Z]+)? [^;&|<>$`()]+( 2>&1| 2>/dev/null)?( \| (head|tail|wc)( -[0-9a-z]+)?)?( && ls( -[a-zA-Z]+)? [^;&|<>$`()]+( 2>&1| 2>/dev/null)?( \| (head|tail|wc)( -[0-9a-z]+)?)?)*$/`. The stderr-redirect slot is a tight whitelist of `2>&1` / `2>/dev/null` only — never a generic `2>FILE` form, which could clobber the destination. A trailing fallback slot accepts `|| true`, `|| echo "msg"`, or `|| echo 'msg'` only — the fallback target is constrained to SAFE builtins; arbitrary commands like `|| rm …` or `|| sh` are rejected.
  Because every segment is constrained to `ls`, no MUTATES binary can be smuggled
  via the `&&` chain.
- **Sink expansion**: the per-segment sink alternation MAY include `\| grep …` (with its full
  flag + quoted-arg shape) alongside `\| (head|tail|wc)` and `\| sed -n 'N,Mp'`. `grep` here
  acts as a downstream read-only filter on the directory listing — equivalent to running
  `ls … | grep -iE "<pattern>"`. The grep sub-pattern MUST retain its own anti-chaining class
  and quoted-arg alternation so that `ls / | grep foo | xargs rm` is still rejected.

### `wc`

- **Verdict**: ✅ SAFE — Counts lines, words, bytes. Read-only.

### `sort`

- **Verdict**: 🟡 SAFE-IF-PIPED — Lexicographic sorter. Reads input, writes sorted output
  to stdout by default. Read-only in default form.
- **MUTATES**: `sort -o <file>` writes the sorted output to `<file>`, potentially clobbering
  it. Refuse / classify as MUTATES whenever `-o` is present.
- **Auto-approve pattern**: pin to no-`-o` invocations, e.g.
  `/^sort( -[a-zA-Z]+)*( [^;&|<>$`()]+)*( \| (head|tail)( -[0-9]+)?)?$/`.
- **Pipeline-sink usage**: also admitted as `find ... | sort | head -N` in entry [39].

### `du`

- **Verdict**: ✅ SAFE — Disk usage reporter. Read-only; no write capability.
- **Safe forms**: `du -sh <paths> 2>/dev/null` (summarize sizes), multiple path args OK.
- **Auto-approve pattern**: `^du( -[a-zA-Z]+)*( ([^;&|<>$`()'\" ]+|'[^']*'|\"[^\"]*\"))+( 2>/dev/null| 2>&1)?$`
- **Safe-chain participation (entry [37])**: `du -FLAGS <paths> [2>/dev/null]`
  is admitted as an arm so `find ... && du ... && du ...` chains auto-approve.

### `readlink`

- **Verdict**: ✅ SAFE — Resolves and prints a symlink's target path. Read-only; writes only to stdout.
- **Safe forms**: `readlink <path>`, `readlink -f <path>` (canonicalize), `readlink <path> 2>&1`.
- **Auto-approve form (in safe-chain entry [37])**: `readlink( -[a-zA-Z]+)?( <path>)+( 2>&1| 2>/dev/null)?`

### `which`

- **Verdict**: ✅ SAFE — Locates an executable in `PATH`. Read-only.

### `xargs`

- **Verdict**: 🟡 SAFE-IF-PIPED-INTO-READ-ONLY-CMD — Argument-list builder; inherits the
  destructiveness of its downstream command.
- **DESTRUCTIVE forms (NEVER auto-approve)**: `xargs rm`, `xargs sed -i`, `xargs sh`,
  `xargs cp`, `xargs mv`, `xargs <any-mutating-cmd>`.
- **SAFE forms (auto-approve OK)**: `xargs grep` · `xargs head` · `xargs tail` ·
  `xargs wc` · `xargs cat` — downstream binary is read-only.
- **Auto-approve rule**: NEVER write a generic `xargs .*` pattern. Always whitelist the
  exact downstream binary: `\| xargs (grep|head|tail|wc|cat) ...`.
- **Typical pipeline**: `find <args> | xargs grep -<flags> <quoted-PAT>` for code search
  across files. See entry [39] in settings.json for the full regex.

### `/usr/libexec/java_home`

- **Verdict**: ✅ SAFE — macOS JVM discovery utility. Read-only; lists installed JVMs
  and their home paths. Safe forms: `-V` (list all), `-v <version>` (show path).
- **Auto-approve pattern**: `^/usr/libexec/java_home( -[A-Za-z]+)*( 2>&1| 2>/dev/null)?( \| head( -[0-9]+)?)?$`

***

## Diffing

### `diff`

- **Verdict**: ✅ SAFE — Compares files line-by-line, output only. No files modified.

### `git diff`

- **Verdict**: ✅ SAFE — Shows working-tree or commit-to-commit diffs. Read-only.
- **EXCEPTION (SAFE, hardcoded chain only)**: The specific chain below is auto-approved as a
  single regex. Filename is hardcoded; no other `>` target qualifies:

  ```
  git [-C <path>] diff [--cached] [-- <path>] > /tmp/settings_diff.txt; \
      wc -l /tmp/settings_diff.txt && head [-N] /tmp/settings_diff.txt
  ```
  Safe because: the redirect target is a hardcoded `/tmp` scratch path (not a system file),
  both downstream consumers (`wc -l`, `head`) are read-only against that same hardcoded path,
  and separators (`;`, `&&`) are pinned — no generic `git diff > <anything>` rule.
  See [Hardcoded Tmp-Write→Read Exception Pattern](#hardcoded-tmp-writeread-exception-pattern)
  for the full eligibility criteria.

***

## Git Read-Only Inspection

All the commands in this section are ✅ SAFE when invoked as documented.
Destructive git commands (`push --force`, `reset --hard`, `clean -fd`, `rebase`) are catalogued
in [`SKILL.md §4`](../SKILL.md#4-destructive-flag-inventory-non-exhaustive-authoritative).

### `git status`

- **Verdict**: ✅ SAFE — Reports staged, unstaged, and untracked changes. Read-only.

### `git log`

- **Verdict**: ✅ SAFE — Enumerates commit history with metadata. Read-only.

### `git ls-tree`

- **Verdict**: 🟡 SAFE-IF-PIPED — Lists tree objects. Output can be piped; classify the full
  pipeline if a downstream command is added.

### `git branch -a` / `git branch -vv` / `git branch --show-current`

- **Verdict**: ✅ SAFE — Lists local and remote-tracking branches (with upstream info). Read-only.

### `git ls-files`

- **Verdict**: 🟡 SAFE-IF-PIPED — Lists tracked files. Same downstream-pipeline concerns as `git ls-tree`. Safe alone.

### `git merge-base`

- **Verdict**: ✅ SAFE — Finds the best common ancestor between two commits. Read-only.

### `git check-ignore`

- **Verdict**: ✅ SAFE — Tests whether paths would be excluded by `.gitignore` rules. Read-only.

### `git rev-parse`

- **Verdict**: ✅ SAFE — Resolves a revision expression (SHA, ref name, `HEAD^`, `HEAD~N`,
  `<sha>^{tree}`) to a full SHA, or prints repo-layout paths (`--git-dir`, `--show-toplevel`,
  `--is-inside-work-tree`). Read-only.

### `git show`

- **Verdict**: ✅ SAFE — Shows commit objects, diffs, tree entries, blobs. Read-only.
- **Auto-approve form (in safe-chain entry [37])**: `show [0-9a-f]{6,40}( --stat| --name-only| --name-status)*( -- <path>...)?` — pins the first arg to a hex SHA so `git show -- /etc/passwd` (no SHA) is rejected.

### `git stash list`

- **Verdict**: ✅ SAFE — Enumerates the stash stack (`stash@{N}` refs with subjects). Read-only.
- **Contrast**: `git stash push`, `git stash pop`, `git stash apply`, `git stash drop`,
  `git stash clear` all modify the stash stack or working tree and are ❌ MUTATES — NOT covered
  by this row.

### `git stash show`

- **Verdict**: ✅ SAFE — Displays summary or diff of a stash entry (`stash@{N}`). Read-only.
- **Safe forms**: `git stash show`, `git stash show stash@{0} --stat`, `... --name-only`.
- **Auto-approve form**: `stash show( stash@\{[0-9]+\})?( --stat| --name-only)?` (inside safe-chain entry [37]).

***

## System / Process Inspection

### `lsof`

- **Verdict**: ✅ SAFE — Lists open files, sockets, and PIDs. Read-only.
- **Note**: `lsof` may require `sudo` to see processes owned by other users; `sudo` itself does
  not change the safety tier of `lsof`.

### `pwd`

- **Verdict**: ✅ SAFE — Prints the current working directory. Shell builtin (also `/bin/pwd`). Read-only; no filesystem mutation.
- **Flags**: `-L` (logical, default — honors `$PWD` / symlinks) and `-P` (physical — resolves symlinks). Neither mutates state.
- **Arguments**: `pwd` accepts no path arguments.
- **Suggested regex**: `/^pwd( -[LP])?$/` (no arg slot beyond the optional flag).

***

## Linters & Analysis Tools

### `markdownlint-cli2`

- **Verdict**: ✅ SAFE (without `--fix`) / ⚠️ HAS-DESTRUCTIVE-FLAGS (with `--fix`)
- **Without `--fix`**: linting only — reports rule violations, no files changed.
- **With `--fix`**: modifies Markdown files in-place. Confirm the match set by running without
  `--fix` first.

- **Sink expansion (auto-approve OK)**: `markdownlint-cli2 ... 2>&1 | (head|tail|wc) -N` ·
  `... 2>&1 | grep -<flags> <quoted-PAT>` — read-only downstream filters for tallying or
  matching specific lint codes. Entry [28] in settings.json admits these sinks while
  preserving the `(?! .*--fix)` destructive-flag exclusion.

***

## Script Interpreter

### `python` (Windows alias)

- **Verdict**: ⚠️ SAFE-WITH-QUALIFICATION — Windows / launcher-installed alias for `python3`.
- **Same rules as `python3`**: classify by the **script** being invoked, never the interpreter
  alone. See the `python3` section below for the SAFE / MUTATES classification table — every
  row applies identically when the interpreter is spelled `python`.
- **Auto-approve pattern**: hardcoded path regex anchored to the specific trusted script;
  never a generic `python .*` catch-all.

### `python3`

- **Verdict**: ⚠️ SAFE-WITH-QUALIFICATION — safety depends entirely on the script being invoked.
- **SAFE** (read-only scripts): `python3 <script> --help`, audit scripts, find/coverage scripts that
  only read files (e.g., `batch-coverage-check.py`, `find-entry.py`).
- **MUTATES** (write scripts): `edit-entry.py`, `fix-indents.py`, and any script that writes to
  `settings.json`, `safety-table.csv`, or other files.
- **Rule**: Always classify by the **script** being invoked, not the interpreter alone.
- **Auto-approve pattern**: Use a hardcoded path regex anchored to the specific trusted script,
  never a generic `python3 .*` catch-all.

| Invocation | Verdict |
| :--- | :--- |
| `python3 .../find-entry.py --list` | ✅ SAFE (read-only) |
| `python3 .../batch-coverage-check.py` | ✅ SAFE (read-only) |
| `python3 .../edit-entry.py --help` | ✅ SAFE (help flag only) |
| `python3 .../edit-entry.py --add …` | ❌ MUTATES (writes settings.json) |
| `python3 .../fix-indents.py` | ❌ MUTATES (rewrites settings.py) |

### `java`

- **Verdict**: ⚠️ SAFE-WITH-QUALIFICATION — safety depends on what the JVM is asked to run.
- **SAFE**: `java -version`, `java -help`, classpath inspection (`-XshowSettings`).
- **MUTATES**: `java -jar <unknown.jar>`, `java <MainClass>` — runs arbitrary code that may
  write files, mutate state, perform network I/O.
- **Auto-approve pattern**: pin to specific safe flags only (e.g., `/^java -version$/`),
  never a generic `java .*` catch-all.

***

## PowerShell Cmdlets (Read-Only)

The following cmdlets are pure read-only or output-only and SAFE to auto-approve with an
anchored anti-chaining regex `/^<Cmdlet>( [^;&|<>$\`()]+)+$/`. The anti-chaining char class
is mandatory — without it, `Cmdlet args; Remove-Item -Recurse C:\` would match.

| Cmdlet | Role | Verdict |
| :--- | :--- | :--- |
| `Get-ChildItem` | Directory listing (alias `gci`/`ls`/`dir`) | ✅ SAFE |
| `Get-Content` | File reader (alias `cat`/`gc`/`type`) | ✅ SAFE |
| `Get-Date` | Date/time emitter | ✅ SAFE |
| `Get-Process` | Process listing | ✅ SAFE |
| `Select-String` | grep-equivalent | ✅ SAFE |
| `Test-Path` | Existence check | ✅ SAFE |
| `Split-Path` | Pure path-component splitter | ✅ SAFE |
| `Get-Item`, `Get-FileHash`, `Get-Command` | Metadata / hash / lookup | ✅ SAFE |
| `Push-Location`, `Pop-Location`, `Set-Location` | Directory-stack navigation | ✅ SAFE |
| `Sort-Object`, `Group-Object`, `Select-Object`, `ForEach-Object`, `Where-Object`, `Format-Table`, `Out-String` | Pipeline transforms / formatters | ✅ SAFE (cmdlet itself) |
| `Write-Host` | Console output | ✅ SAFE |

**Important — scriptblock executors**: `ForEach-Object { … }` and `Where-Object { … }` accept
a scriptblock whose body is **arbitrary code**. The cmdlet name is SAFE, but a loose-prefix
auto-approve entry (`"ForEach-Object": true`) effectively approves any code. Do NOT add a
bare-prefix entry for these — only onboard specific anchored pipeline shapes.

**MUTATES cmdlets — auto-approve only with explicit user confirmation**:
`Copy-Item`, `Move-Item`, `Remove-Item`, `Set-Content`, `Add-Content`, `Out-File`,
`New-Item`, `Rename-Item`.

***

## Filesystem Mutation (for contrast)

### `mkdir`

- **Verdict**: ❌ MUTATES — Creates directories. Always mutates the filesystem.
- **Idempotent but still MUTATES**: `mkdir -p <path>` avoids errors if the path exists, but the
  operation itself is still a mutation — a new directory may be created.
- **Safe check before**: `ls -d <path> 2>/dev/null` to test existence without creating.

***

## Package Management Inspection

### `brew leaves`

- **Verdict**: ✅ SAFE — Lists explicitly installed (leaf) formulae. Read-only.
- **Common flag**: `--installed-on-request` narrows output to user-requested installs (excludes
  packages auto-installed as dependencies).
- **Contrast**: `brew install`, `brew upgrade`, `brew uninstall`, `brew cleanup` are all ❌ MUTATES
  and are NOT covered by this row.

### `brew list`

- **Verdict**: ✅ SAFE — Lists installed packages. Read-only.
- **Common flags**: `--cask` (casks only), `--formula` (formulae only). Both remain read-only.

### `brew outdated`

- **Verdict**: ✅ SAFE — Lists outdated formulae/casks. Read-only.
- **Common flag**: `--greedy` includes casks with `auto_updates` or `version :latest`.
- **Contrast**: `brew upgrade` (with or without `--greedy`) is ❌ MUTATES.

***

## Shell Builtins

### `cd`

- **Verdict**: ✅ SAFE — Changes the shell working directory. No filesystem mutation.

### `echo`

- **Verdict**: ✅ SAFE — Prints arguments to stdout.

### `true`

- **Verdict**: ✅ SAFE — No-op builtin returning exit 0. Common as `|| true` fallback after a non-fatal grep / test.

***

## Non-CLI Tokens

### `agy`

- **Not a shell binary.** `agy` refers to the **Google Antigravity** IDE-embedded agentic
  assistant (an AI agent layer on top of VS Code). It is not a command-line tool and has no
  applicable shell safety verdict under this skill. For Antigravity agent behavior, consult the
  [Antigravity Version Checker skill](../../antigravity-version-checker/SKILL.md).

***

## Dangerous Pipeline Catalogue

The following pipeline patterns are always `MUTATES` regardless of the source binary:

| Pattern | Effect |
| :--- | :--- |
| `<any> \| xargs rm` | Deletes files matching the upstream output. |
| `<any> \| xargs sed -i` | In-place edits files matching the upstream output. |
| `<any> > existing-file` | Truncates and overwrites the target file. |
| `<any> \| tee existing-file` | Truncates and overwrites (without `-a`). |
| `<any> \| sh` / `\| bash` | Executes upstream output as shell commands. |
| `$(rm …)` / `` `rm …` `` | Inline mutation inside a larger command. |

***

## Hardcoded Tmp-Write→Read Exception Pattern

A `>` truncating redirect is `MUTATES` by default (per §4 of the SKILL and the
Dangerous Pipeline Catalogue above). One narrow class of chains may be
auto-approved despite the `>` token, IFF every clause below holds:

1. **Hardcoded target filename**: the `>` target is a literal `/tmp/<fixed-name>`
   string baked into the regex — never a generic `/tmp/.*` or "same-stem"
   capture. A new scratch filename requires a new entry.
2. **Scratch path**: the target lives under `/tmp` (or another universally
   scratch-only directory). System paths (`/etc`, `/usr`, `/var`, `~`, repo
   working trees) are NEVER eligible.
3. **Read-only consumers**: every downstream segment after the `>` is a
   read-only binary classified `SAFE` in this SSOT (`wc`, `head`, `tail`,
   `sed -n …p`, `cat`, `grep`) and operates on the SAME hardcoded path.
4. **Pinned separators**: only `;` and `&&` may appear between segments —
   never `||`, `|`, `&`, no command substitution, no second `>` redirect.
5. **Per-segment anti-chaining**: every argument slot inside every segment
   keeps the `[^;&|<>$BTICK()]` class (where `BTICK` denotes a literal
   backtick) so no segment can be smuggled past the splitter.

Documented instances in this SSOT:

| Anchor binary | Reference | Chain shape |
| :--- | :--- | :--- |
| `cat` | [§ `cat`](#cat) | `cat > /tmp/cmds-parity.txt << EOF … python3 …/batch-coverage-check.py --commands /tmp/cmds-parity.txt …` |
| `git diff` | [§ `git diff`](#git-diff) | `git [-C <path>] diff [--cached] [-- <path>] > /tmp/settings_diff.txt; wc -l /tmp/settings_diff.txt && head [-N] /tmp/settings_diff.txt` |

Each instance MUST link back to this pattern section so the criteria above
are the single source of truth — never duplicate the rules in the
per-binary section.

When a new occurrence arises:

1. Verify all five clauses above.
2. Add the per-binary `EXCEPTION` block referencing this pattern by section
   anchor (do not restate the rules).
3. Author a `command-autoapprove-onboarding/specs/hardcoded-chain-*.spec.json`
   capturing the regex + accept/reject assertions (the spec is required by
   parity with [§5.1 safe-chain entries](../../command-autoapprove-onboarding/SKILL.md#step-51--safe-chain-entries-opt-in)).

***

## Adding New Entries

Follow the Append-Only Protocol in [`SKILL.md §8`](../SKILL.md#8-extending-the-allowlist-append-only-protocol).
Add the new row to [`safety-table.csv`](./safety-table.csv) and a new section here at the correct
alphabetical position within its category.
