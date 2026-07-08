---
name: teams-recording-download
description: "Download Microsoft Teams meeting recordings with a 3-tier fallback: (A) Teams desktop app via JXA + Chrome via Playwright, (C) Chrome only, (B) Teams remote debugging. Captures video manifest URL and downloads via ffmpeg."
category: Media Processing / Composition
---

# Teams Recording Download Skill (v1)

This is a **composer** skill. It orchestrates Teams-specific workflow
(app detection, web navigation, meeting search) and delegates network
interception and video download to base skills. No base logic is
re-implemented — every sub-step delegates to the appropriate base skill.

***

## 1. Scope & Intent

- **In scope**:
    - 3-tier fallback architecture (A → C → B)
    - Tier A: Teams desktop app via JXA + Chrome via Playwright
    - Tier C: Chrome only (JXA on macOS, Playwright elsewhere)
    - Tier B: Teams with remote debugging (last resort)
    - Navigate Teams app to find recordings (Calendar, Chat)
    - Capture video manifest URL via network interception (Playwright)
    - Download recording via ffmpeg
- **Out of scope**:
    - Downloading non-recording files from Teams
    - Microsoft Graph API integration
    - Processing chat messages or files

***

## 2. Environment & Dependencies

### 2.1 Runtime

- **macOS 14+** (Tier A: JXA for Teams + Chrome control)
- **Python 3.12+**
- **Windows/Linux** (Tier C only: Chrome via Playwright)

### 2.2 Dependencies

```bash
pip install playwright playwright-stealth
brew install ffmpeg
```

### 2.3 Required Setup

- **Google Chrome** with a logged-in Microsoft account (for
  teams.microsoft.com). Uses the default Chrome profile.
- **ffmpeg** installed and on PATH.
- **JXA permissions**: Grant Terminal/iTerm accessibility access in
  System Settings → Privacy & Security → Accessibility.

### 2.4 Required Skill Loading

Before executing this skill, the agent MUST load all SKILL.md files:

```text
macos-app-control/SKILL.md
browser-network-interception/SKILL.md
video-download-manifest/SKILL.md
teams-recording-download/SKILL.md (this file)
```

***

## 3. Protocol

### 3.1 Step 1 — Verify Dependencies

```bash
python3 .agents/skills/teams-recording-download/scripts/teams-recording-download--setup.py
```

### 3.2 Step 2 — Run Download Script

```bash
python3 .agents/skills/teams-recording-download/scripts/teams-recording-download.py \
  --date "YYYY-MM-DD" \
  --topic "<meeting-topic>" \
  [--output <path.mp4>] \
  [--source {auto,calendar,chat}] \
  [--dry-run]
```

### 3.3 Arguments

| Argument | Required | Default | Description |
| ---------- | ---------- | --------- | ------------- |
| `--date` | Yes | — | Meeting date (`YYYY-MM-DD`) |
| `--topic` | Yes | — | Meeting topic keyword to search |
| `--output` | No | `~/Downloads/teams-recording-<date>.mp4` | Output file path |
| `--source` | No | `auto` | Where to look: `auto`, `calendar`, `chat` |
| `--tier` | No | `auto` | Tier: `A` (JXA+Chrome), `C` (Chrome-only), `B` (remote-debug), `auto` (try all) |
| `--dry-run` | No | false | Find manifest URL only, don't download |

### 3.4 Orchestrator Flow

```text
3-TIER FALLBACK (auto mode):

TIER A (macOS + JXA):
  1. Check JXA availability (osascript)
  2. Check Teams running via JXA → launch if not
  3. Navigate Teams app (search, Calendar)
  4. Open Teams web in Chrome via JXA
  5. Playwright captures manifest URL from Chrome
  6. If found → download, DONE

TIER C (Chrome only):
  7. If JXA not available or Tier A failed
  8. Open Chrome to teams.microsoft.com (JXA on macOS, Playwright elsewhere)
  9. Playwright navigates and captures manifest URL
  10. If found → download, DONE

TIER B (Teams remote debugging):
  11. If Tier C failed
  12. Launch Teams with --remote-debugging-port=9222
  13. Connect Playwright to localhost:9222
  14. Capture manifest URL from Teams process
  15. If found → download, DONE

ALL TIERS:
  16. If no tier succeeded → error
  17. Call video-download-manifest with captured URL
  18. Print result
```

### 3.5 Backend Scripts

| Script | Language | Purpose |
| -------- | ---------- | --------- |
| [`scripts/teams-recording-download.py`](scripts/teams-recording-download.py) | Python | Orchestrator — app detection, delegates to base scripts |
| [`scripts/teams-recording-download--setup.py`](scripts/teams-recording-download--setup.py) | Python | Dependency verification |

***

## 4. Edge Cases

- **JXA not available (non-macOS)**: Falls back to Tier C (Chrome only).
- **Teams app fails to launch**: Falls back to Tier C (Chrome only).
- **JXA permissions not granted**: Falls back to Tier C (Chrome only).
  Grant accessibility access in System Settings → Privacy & Security →
  Accessibility.
- **Tier A fails**: Automatically tries Tier C, then Tier B.
- **Tier C fails**: Automatically tries Tier B (remote debugging).
- **Remote debugging not available**: Tier B fails, reports error.
- **Not logged in**: Browser shows login page. Script pauses, user logs
  in manually, then script continues.
- **Multiple meetings match**: Script prints numbered list, user selects
  via stdin input.
- **No recording found**: Script reports error with what was found.
- **View-only recording**: Works — manifest URL is still accessible
  via network interception.
- **Chrome already running**: Opens new tab in existing Chrome instance.
- **Calendar doesn't show old recordings**: Falls back to Chat search.
- **Teams UI changes**: Text-content selectors used (not CSS classes)
  for resilience.

***

## 5. Composition Reference

| Base / Support Skill | Usage | Composition Mechanism |
| ---------------------- | ------- | ---------------------- |
| [`macos-app-control`](../macos-app-control/SKILL.md) | macOS app control | Calls `macos-app-control.py` with subcommands (`app-running`, `app-launch`, `app-show`, `send-keys`, `chrome-open`) for Teams desktop app detection, launch, navigation, and Chrome control |
| [`browser-network-interception`](../browser-network-interception/SKILL.md) | Network interception | Calls `scripts/intercept-network.py` with `--pattern videomanifest` and `--backend jxa` to capture video manifest URLs from Teams web traffic |
| [`video-download-manifest`](../video-download-manifest/SKILL.md) | Video download | Calls `scripts/download-from-manifest.py` with captured manifest URL to download recording via ffmpeg |

***

## 6. Composition Rationale

This skill is a **composer**: it owns the end-to-end Teams recording
download workflow but delegates every meaningful sub-step to base skills:

1. **[`macos-app-control`](../macos-app-control/SKILL.md)** —
   invoked for Teams desktop app detection, launch, navigation, and
   Chrome control. The composer passes app names and keyboard shortcuts;
   the base executes JXA commands.
2. **[`browser-network-interception`](../browser-network-interception/SKILL.md)** —
   invoked to capture video manifest URLs from network traffic. The
   composer passes the Teams web URL, `videomanifest` pattern, and
   `jxa` backend; the base returns matched URLs.
3. **[`video-download-manifest`](../video-download-manifest/SKILL.md)** —
   invoked to download the video from the captured manifest URL. The
   composer passes the URL and output path; the base runs ffmpeg.

The composer's domain-specific value-add over either base alone:
3-tier fallback architecture (A → C → B) that maximizes success rate
across platforms. Tier A uses JXA for Teams desktop app navigation
and Chrome opening (zero detection risk), Tier C falls back to
Chrome-only via Playwright, and Tier B uses Teams remote debugging
as a last resort. The composer also handles Teams app detection and
launch, meeting search by date + topic keyword, user selection from
multiple matches, and orchestration of the full pipeline. Inlining
either base would duplicate logic that other workflows (e.g., YouTube
stream capture, custom player automation) also consume.

Bidirectional discoverability: all base skills list this composer in
their `## Composition by Higher-Level Skills` tables.

## Related Skills

- [`youtube-studio-settings`](../youtube-studio-settings/SKILL.md) — browser automation
  for YouTube Studio (similar layered pattern)
- [`youtube-video-upload`](../youtube-video-upload/SKILL.md) — YouTube upload workflow (uses similar base + composer
architecture)
