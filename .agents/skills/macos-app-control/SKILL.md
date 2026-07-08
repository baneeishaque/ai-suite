---
name: macos-app-control
description: "Detect, launch, navigate, and interact with macOS applications via JXA (JavaScript for Automation). Generic base skill for any macOS desktop automation."
category: macOS Automation
---

# macOS App Control Skill (v1)

This is a **base** skill. It provides a generic CLI for controlling macOS
applications via JXA (JavaScript for Automation). Domain-agnostic —
usable by any workflow needing to detect, launch, navigate, or interact
with macOS desktop applications.

***

## 1. Scope & Intent

- **In scope**:
    - Detect if a macOS application is running
    - Launch a macOS application
    - Show an application's main window
    - Bring an application to foreground
    - Send keyboard shortcuts to an application
    - Click menu items in an application
    - Open URLs in Google Chrome (existing profile)
- **Out of scope**:
    - DOM interaction within applications (use Playwright for web)
    - Network interception (use browser-network-interception)
    - Video downloading (use video-download-manifest)
    - Windows/Linux (JXA is macOS-native)

***

## 2. Environment & Dependencies

### 2.1 Runtime

- **macOS 14+** (JXA is macOS-native)
- **Python 3.12+**

### 2.2 Dependencies

None — JXA is built into macOS.

### 2.3 Required Setup

- **Accessibility permissions**: Grant Terminal/iTerm accessibility
  access in System Settings → Privacy & Security → Accessibility.

### 2.4 Required Skill Loading

Before executing this skill, the agent MUST load:

```text
macos-app-control/SKILL.md (this file)
```

***

## 3. Protocol

### 3.1 Step 1 — Run Control Script

```bash
python3 .agents/skills/macos-app-control/scripts/macos-app-control.py \
  <subcommand> [args] [--modifiers <mods>] [--menu <path>] [--json]
```

### 3.2 Subcommands

| Subcommand | Args | Description |
|------------|------|-------------|
| `app-running` | `<app-name>` | Check if app is running (exit 0=yes, 1=no) |
| `app-launch` | `<app-name>` | Launch app |
| `app-show` | `<app-name>` | Show app main window |
| `app-activate` | `<app-name>` | Bring app to foreground |
| `send-keys` | `<key>` | Send keyboard shortcut |
| `menu-click` | `<app-name>` | Click menu item |
| `chrome-open` | `<url>` | Open URL in Chrome |
| `chrome-open-tab` | `<url>` | Open URL in new Chrome tab |

### 3.3 Optional Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--modifiers` | No | — | Keyboard modifiers (e.g., `command down,shift down`) |
| `--menu` | No | — | Menu path (e.g., `Microsoft Teams>Show Main Window`) |
| `--json` | No | false | Output JSON with structured result |

### 3.4 Output Contract

- **stdout**: Command output (app name, URL, etc.)
- **stderr**: Error messages
- **Exit 0**: Success
- **Exit 1**: Failure (app not found, menu not found, etc.)
- **Exit 2**: Error (missing arguments, etc.)

### 3.5 Script

| Script | Language | Purpose |
|--------|----------|---------|
| [`scripts/macos-app-control.py`](scripts/macos-app-control.py) | Python | CLI wrapper — parses args, calls JXA, outputs result |
| [`scripts/macos-app-control.jxa`](scripts/macos-app-control.jxa) | JXA | macOS app control — detection, launch, navigation, keystrokes |

***

## 4. Edge Cases

- **App not installed**: `app-launch` will fail with JXA error.
- **App not running**: `app-running` returns exit 1. `app-show` and
  `app-activate` will attempt to launch.
- **Accessibility not granted**: JXA will fail with permission error.
  Grant access in System Settings → Privacy & Security → Accessibility.
- **Chrome not running**: `chrome-open` will launch Chrome.
- **Menu item not found**: `menu-click` returns exit 1 with error message.

***

## 5. Composition by Higher-Level Skills

| Composer Skill | Composition Mechanism |
|----------------|----------------------|
| [`browser-network-interception`](../browser-network-interception/SKILL.md) | Uses `chrome-open` subcommand to open Chrome with specific profile for network interception. |
| [`teams-recording-download`](../teams-recording-download/SKILL.md) | Uses `app-running`, `app-launch`, `app-show`, `send-keys`, and `chrome-open` subcommands for 3-tier Teams recording download workflow. |

***

## 6. Composition Rationale

This skill is a **base** skill: it owns only the generic macOS app
control primitive via JXA. It delegates all web automation (DOM
interaction, network interception) to browser-based skills and all
video processing to media skills. Separating macOS app control from
domain-specific workflows (Teams, YouTube, etc.) allows reuse by any
desktop automation task needing to detect, launch, or interact with
macOS applications.

Bidirectional discoverability: all known consumers list this skill in
their `## Composition Reference` sections.

## Related Skills

- [`browser-network-interception`](../browser-network-interception/SKILL.md) — base skill for
  browser network interception (uses this skill for Chrome control)
- [`teams-recording-download`](../teams-recording-download/SKILL.md) — composer skill
  that orchestrates Teams workflow using this skill
