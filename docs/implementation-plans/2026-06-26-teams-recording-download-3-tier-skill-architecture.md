# [Teams Recording Download — 3-Tier Skill Architecture] (v1)

## Rule Compliance Reference

- [ai-agent-planning-rules.md](../../ai-suite/ai-agent-rules/ai-agent-planning-rules.md) — Core planning protocol, versioning, maximum literal detail
- [ai-rule-standardization-rules.md](../../ai-suite/ai-agent-rules/ai-rule-standardization-rules.md) — Skill-First Architecture, Layered Composition Mandate, SSOT, Skill-Name Precision
- [skill-factory/SKILL.md](../../ai-suite/.agents/skills/skill-factory/SKILL.md) — Skill generation protocol, base vs composer layering, AGENTS.md bridge, registration

## User Questions & Answers

| Question | Answer |
|----------|--------|
| Can we navigate Teams app interface to find recordings? | Yes — via JXA menu bar navigation and keyboard shortcuts (Cmd+Shift+C for Calendar, Cmd+E for search). The accessibility tree is shallow (Electron), but menu items and keystrokes work. |
| Can we identify video URL from Teams app video play window? | No — the Electron web content is not exposed via System Events. Network interception requires sudo/tcpdump or CDP. |
| Should Teams web interface be a fallback? | Yes — Tier C (Chrome only) is the fallback when JXA is not available or Tier A fails. |
| What about sudo for tcpdump? | Not needed — Playwright in Chrome handles all network interception. The Teams app is only for navigation, not network capture. |

## Problem Statement

The `teams-recording-download` skill has a 3-tier fallback architecture (A → C → B) but:

1. The JXA helper script (`teams-jxa-helper.jxa`) is trapped inside the composer skill — it's a reusable macOS app control primitive that other skills could consume.
2. The `browser-network-interception` skill hardcodes Playwright as the only backend — no JXA option for zero-detection Chrome control.
3. The 3-tier architecture is implemented in code but not properly documented in SKILL.md files.
4. There is no reusable base skill for macOS app control via JXA.

## Proposed Changes

### New Skills

#### 1. `macos-app-control` (BASE)

**Location:** `/Users/dk/lab-data/ai-suite/.agents/skills/macos-app-control/`

**Purpose:** Generic macOS application control via JXA (JavaScript for Automation). Domain-agnostic — usable by any workflow needing to detect, launch, navigate, or interact with macOS applications.

**Files:**
- `SKILL.md` — Base skill documentation
- `AGENTS.md` — Companion bridge
- `scripts/macos-app-control.py` — Python wrapper around JXA helper
- `scripts/macos-app-control.jxa` — JXA functions (migrated from `teams-jxa-helper.jxa`)

**CLI Contract:**
```bash
python3 scripts/macos-app-control.py <subcommand> [args]
```

**Subcommands:**
| Subcommand | Args | Output | Description |
|------------|------|--------|-------------|
| `app-running` | `<app-name>` | exit 0=yes, 1=no | Check if app is running |
| `app-launch` | `<app-name>` | exit 0=success | Launch app |
| `app-show` | `<app-name>` | exit 0=success | Show main window |
| `app-activate` | `<app-name>` | exit 0=success | Bring app to foreground |
| `send-keys` | `<keys>` `--modifiers <mods>` | exit 0=success | Send keyboard shortcut |
| `menu-click` | `<app-name>` `--menu <path>` | exit 0=success | Click menu item |
| `chrome-open` | `<url>` `--new-tab` | exit 0=success | Open URL in Chrome |
| `chrome-open-profile` | `<url>` `--profile <path>` | exit 0=success | Open URL in Chrome with specific profile |

**Design Decisions:**
- Python wrapper provides structured output (JSON option) and error handling
- JXA helper is the same file currently at `teams-recording-download/scripts/teams-jxa-helper.jxa`, generalized
- App name is passed as argument (not hardcoded to Teams)
- Keyboard shortcut parsing: `Cmd+Shift+C` → `{"command down": true, "shift down": true, "c": true}`

### Modified Skills

#### 2. `browser-network-interception` (BASE) — Update

**Location:** `/Users/dk/lab-data/ai-suite/.agents/skills/browser-network-interception/`

**Changes:**
- Add `--backend {playwright,jxa}` argument to `intercept-network.py`
- JXA backend: Use `macos-app-control` to open Chrome, then attach Playwright to the running instance
- Playwright backend: Current behavior (default)
- Update SKILL.md to document both backends
- Add `macos-app-control` to Composition Reference

**New CLI arguments:**
| Argument | Default | Description |
|----------|---------|-------------|
| `--backend` | `playwright` | Backend: `playwright` (default) or `jxa` (macOS, opens Chrome via JXA) |

**JXA backend flow:**
1. Use `macos-app-control chrome-open <url>` to open URL in real Chrome
2. Wait for Chrome to load
3. Attach Playwright to Chrome via `browser_type.connect_over_cdp("http://localhost:9222")`
4. Monitor network responses

**Note:** JXA backend requires Chrome to be launched with `--remote-debugging-port=9222`. The `macos-app-control chrome-open` command will handle this.

#### 3. `teams-recording-download` (COMPOSER) — Update

**Location:** `/Users/dk/lab-data/ai-suite/.agents/skills/teams-recording-download/`

**Changes:**
- Remove `teams-jxa-helper.jxa` (migrated to `macos-app-control`)
- Update orchestrator to use `macos-app-control` instead of direct JXA calls
- Update SKILL.md with complete 3-tier architecture documentation
- Add `macos-app-control` to Composition Reference
- Update Backend Scripts table

**Updated composition:**
```
teams-recording-download (COMPOSER)
  |-- macos-app-control (BASE) -- JXA macOS app control
  |-- browser-network-interception (BASE) -- network interception
  |-- video-download-manifest (BASE) -- ffmpeg download
```

## Execution Steps

### Step 1: Create `macos-app-control` base skill

1. Create directory: `/Users/dk/lab-data/ai-suite/.agents/skills/macos-app-control/`
2. Create `scripts/` directory
3. Migrate `teams-jxa-helper.jxa` → `scripts/macos-app-control.jxa`
   - Generalize: accept app name as argument instead of hardcoding "Microsoft Teams"
   - Add new subcommands: `app-running`, `app-launch`, `app-show`, `app-activate`, `send-keys`, `menu-click`
   - Keep existing: `chrome-open`, `chrome-open-tab`
4. Create `scripts/macos-app-control.py` — Python wrapper
   - Parse subcommand and args
   - Call JXA helper via `osascript -l JavaScript`
   - Output JSON with `--json` flag
   - Exit codes: 0=success, 1=failure, 2=error
5. Create `SKILL.md` — Base skill documentation
6. Create `AGENTS.md` — Companion bridge

### Step 2: Update `browser-network-interception`

1. Update `scripts/intercept-network.py`:
   - Add `--backend` argument
   - JXA backend: Use `macos-app-control chrome-open` to open Chrome
   - JXA backend: Connect Playwright via CDP
   - Keep Playwright backend as default
2. Update `SKILL.md`:
   - Document both backends
   - Add `macos-app-control` to Composition Reference
   - Update CLI arguments table

### Step 3: Update `teams-recording-download`

1. Update `scripts/teams-recording-download.py`:
   - Import `macos-app-control` script path
   - Replace `jxa_run()` calls with `macos-app-control` calls
   - Remove direct JXA helper references
2. Update `scripts/teams-recording-download--setup.py`:
   - Add `macos-app-control` dependency check
3. Delete `scripts/teams-jxa-helper.jxa` (migrated)
4. Update `SKILL.md`:
   - Complete 3-tier architecture documentation
   - Updated composition reference
   - Updated backend scripts table

### Step 4: Register new skill

1. Run `agents-md-stage-row.py` to add `macos-app-control` to root `AGENTS.md`
2. Verify alphabetical position in skills table

### Step 5: Verify

1. Run `markdownlint-cli2` on all modified SKILL.md files
2. Run companion scripts (wrap-long-lines, fix-table-separators, etc.)
3. Run `python3 scripts/macos-app-control.py --help` to verify CLI
4. Test `macos-app-control.py app-running "Microsoft Teams"` (should return exit 0)
5. Test `macos-app-control.py chrome-open "https://example.com"` (should open Chrome)

## Files to Create

| File | Purpose |
|------|---------|
| `/Users/dk/lab-data/ai-suite/.agents/skills/macos-app-control/SKILL.md` | Base skill doc |
| `/Users/dk/lab-data/ai-suite/.agents/skills/macos-app-control/AGENTS.md` | Companion bridge |
| `/Users/dk/lab-data/ai-suite/.agents/skills/macos-app-control/scripts/macos-app-control.py` | Python wrapper |
| `/Users/dk/lab-data/ai-suite/.agents/skills/macos-app-control/scripts/macos-app-control.jxa` | JXA functions |

## Files to Modify

| File | Changes |
|------|---------|
| `/Users/dk/lab-data/ai-suite/.agents/skills/browser-network-interception/SKILL.md` | Add JXA backend docs |
| `/Users/dk/lab-data/ai-suite/.agents/skills/browser-network-interception/scripts/intercept-network.py` | Add `--backend` arg, JXA backend |
| `/Users/dk/lab-data/ai-suite/.agents/skills/teams-recording-download/SKILL.md` | 3-tier docs, updated composition |
| `/Users/dk/lab-data/ai-suite/.agents/skills/teams-recording-download/scripts/teams-recording-download.py` | Use macos-app-control |
| `/Users/dk/lab-data/ai-suite/.agents/skills/teams-recording-download/scripts/teams-recording-download--setup.py` | Add macos-app-control check |
| `/Users/dk/lab-data/ai-suite/AGENTS.md` | Add macos-app-control row |

## Files to Delete

| File | Reason |
|------|--------|
| `/Users/dk/lab-data/ai-suite/.agents/skills/teams-recording-download/scripts/teams-jxa-helper.jxa` | Migrated to macos-app-control |

## Verification

1. `markdownlint-cli2` on all modified SKILL.md files → 0 errors
2. `python3 scripts/macos-app-control.py --help` → shows subcommands
3. `python3 scripts/macos-app-control.py app-running "Microsoft Teams"` → exit 0
4. `python3 scripts/macos-app-control.py chrome-open "https://example.com"` → opens Chrome
5. `python3 scripts/teams-recording-download.py --help` → shows `--tier` arg
6. `python3 scripts/teams-recording-download--setup.py` → all OK
7. Root `AGENTS.md` skills table → macos-app-control at correct alphabetical position
