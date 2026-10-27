# Troubleshooting

> **Scope:** Wrong app opens, missing commands, bundle-ID collision, Gatekeeper, version skew, and
> livecheck · **Verified:** 2026-10-27

## Quick symptom table

| Symptom | Likely cause | Go to |
| --- | --- | --- |
| `brew upgrade` replaced my IDE with a different app | Pre-split cask semantics; the App took the old IDE's identity | [IDE replaced by App](#ide-replaced-by-app) |
| `/Applications/Antigravity.app` opens the agent platform, not the IDE | You have the App, not the IDE | [Identify which app you have](#identify-which-app-you-have) |
| `antigravity: command not found` | The GUI casks install no `antigravity` command | [Command names](#command-names) |
| `agy: command not found` | `agy` belongs to `antigravity-cli`, not the GUI casks | [Command names](#command-names) |
| `agy-ide: command not found` | The IDE cask is not installed, or its bin directory is not on `PATH` | [Command names](#command-names) |
| Two Antigravity icons in the Dock | Both GUI apps are installed | [Coexistence](#coexistence) |
| Can't tell which icon is which | White background vs black grid | [Dock icons](#dock-icons) |
| `brew info --cask antigravity` shows 2.x but I want the IDE | The token changed meaning after the split | [IDE replaced by App](#ide-replaced-by-app) |
| `antigravity-ide` reported outdated even when current | Historical livecheck issue | [Livecheck and outdated cask](#livecheck-and-outdated-cask) |
| "App is damaged" or an `xattr` error | Quarantine or a historical shim issue | [Gatekeeper and quarantine](#gatekeeper-and-quarantine) |
| SHA-256 mismatch during install | Corrupted download or changed artifact | [Checksum mismatch](#checksum-mismatch) |
| App requires macOS 13 but Google says 12 | The cask pins Ventura | [macOS version mismatch](#macos-version-mismatch) |
| "Bad CPU type" or wrong DMG | Architecture mismatch | [Architecture mismatch](#architecture-mismatch) |
| Homebrew version and app version disagree | Vendor self-update | [Version skew](#version-skew) |
| Uninstall left settings behind | `brew uninstall` without `--zap` | [Uninstall leftovers](#uninstall-leftovers) |
| Old IDE settings are missing in the new IDE | New IDE uses new configuration paths | [Configuration paths](#configuration-paths) |
| LaunchServices opens the wrong app | Old IDE and new App share a bundle identifier | [Bundle ID collision](#bundle-id-collision) |

## Identify which app you have

```bash
ls -ld /Applications/Antigravity.app "/Applications/Antigravity IDE.app" 2>&1
mdls -name kMDItemCFBundleIdentifier /Applications/Antigravity.app 2>&1
mdls -name kMDItemCFBundleIdentifier "/Applications/Antigravity IDE.app" 2>&1
brew list --cask | grep -E '^(antigravity|antigravity-ide)$'
```

| App path | Bundle identifier | Product | Cask |
| --- | --- | --- | --- |
| `/Applications/Antigravity.app` | `com.google.antigravity` | Antigravity 2 App | `antigravity` |
| `/Applications/Antigravity IDE.app` | `com.google.antigravity-ide` | Antigravity IDE | `antigravity-ide` |

If only `Antigravity.app` exists and it opens the agent platform, you have the App. Install
`antigravity-ide` if you also want the IDE. If `Antigravity.app` opens an editor, you are still on the
pre-split 1.x IDE; install the current casks to move to the split layout.

## IDE replaced by App

This is the most common post-split complaint. The pre-split `antigravity` cask installed the IDE as
`Antigravity.app` with bundle identifier `com.google.antigravity`. The current `antigravity` cask
installs the App with the same app path and bundle identifier. Between 2026-05-21 and 2026-05-22,
there was no `antigravity-ide` cask yet, so an upgrade replaced the IDE in place.

Fix:

```bash
brew install --cask antigravity-ide
```

This installs `Antigravity IDE.app` alongside the App. Both can coexist. If you want the App gone:

```bash
brew uninstall --cask antigravity
```

Do not add `--zap` until you have backed up any old IDE data under `~/.antigravity` and
`~/.gemini/antigravity`; the App's `zap` list uses those same paths.

There is no supported way to make the current `antigravity` token install the 1.x IDE again. The 1.x
line ended at `1.23.2`; use `antigravity-ide` for the IDE.

## Command names

| Command | Provided by | Notes |
| --- | --- | --- |
| `agy` | `antigravity-cli` | Terminal client |
| `agy-ide` | `antigravity-ide` | IDE command-line shim |
| `antigravity-ide` | `antigravity-ide` | Same executable as `agy-ide` |
| `antigravity` | none | Neither GUI cask installs a command with this name |

Diagnose:

```bash
type -a agy agy-ide antigravity-ide 2>&1
brew list --cask | grep antigravity
ls -l "$(brew --prefix)/bin/agy-ide" 2>&1
ls -l "$(brew --prefix)/bin/antigravity-ide" 2>&1
```

- Missing `agy`: install `antigravity-cli`.
- Missing `agy-ide` or `antigravity-ide`: install `antigravity-ide`.
- Missing `antigravity`: expected; the App has no binary.

If a command exists but the wrong one runs, `type -a` shows every match in `PATH` order. Remove the
duplicate or reorder `PATH` deliberately.

## Coexistence

Both GUI apps can coexist because they use different bundles and identifiers after the split:

| Resource | App | IDE |
| --- | --- | --- |
| App path | `/Applications/Antigravity.app` | `/Applications/Antigravity IDE.app` |
| Bundle identifier | `com.google.antigravity` | `com.google.antigravity-ide` |
| Config root | `~/.antigravity` | `~/.antigravity-ide` |
| CLI binary | none | `agy-ide`, `antigravity-ide` |

Two Dock icons are expected if both are installed. If you want only one, uninstall the other cask. See
[installation-and-migration.md](installation-and-migration.md#uninstall).

## Dock icons

| Product | Dock icon |
| --- | --- |
| Antigravity 2 App | White background |
| Antigravity IDE | Black grid |

If you see one icon and it opens the wrong product, check the app bundle path with
[Identify which app you have](#identify-which-app-you-have). If you see two icons, both apps are
installed; that is not a bug.

## Bundle ID collision

The old 1.x IDE and the new 2.x App share the bundle identifier `com.google.antigravity`. The new IDE
uses `com.google.antigravity-ide`, so the collision is historical, not a current conflict between the
two post-split apps.

Consequences:

- `open -b com.google.antigravity` targets the App (or the old IDE if it is still installed at the same
  path).
- `open -b com.google.antigravity-ide` targets the new IDE.
- The old IDE and the new App cannot coexist at `/Applications/Antigravity.app`; the 2.x App replaced
  the 1.x IDE in place.
- Uninstalling the App quits `com.google.antigravity`, which is the same identifier the old IDE used.

Diagnose:

```bash
mdls -name kMDItemCFBundleIdentifier /Applications/Antigravity.app
mdls -name kMDItemCFBundleIdentifier "/Applications/Antigravity IDE.app"
osascript -e 'id of app "Antigravity"'
osascript -e 'id of app "Antigravity IDE"'
```

If LaunchServices opens the wrong app after a migration, log out and back in, or reinstall the
affected cask. Avoid deleting LaunchServices databases manually.

## Configuration paths

The cask `zap` lists show where each product stores data:

| Data | App | IDE |
| --- | --- | --- |
| Config root | `~/.antigravity` | `~/.antigravity-ide` |
| Gemini data | `~/.gemini/antigravity` | `~/.gemini/antigravity-ide` |
| Application Support | `~/Library/Application Support/Antigravity` | `~/Library/Application Support/Antigravity IDE` |
| Caches | `~/Library/Caches/com.google.antigravity` | `~/Library/Caches/com.google.antigravity-ide` |
| Preferences | `~/Library/Preferences/com.google.antigravity.plist` | `~/Library/Preferences/com.google.antigravity-ide.plist` |
| Saved state | `~/Library/Saved Application State/com.google.Antigravity.savedState` | `~/Library/Saved Application State/com.google.antigravity-ide.savedState` |

If the new IDE seems to have lost your settings, it may simply be reading new paths. The App inherited
the old IDE's paths; the new IDE did not. Check both:

```bash
ls -la ~/.antigravity ~/.gemini/antigravity 2>&1
ls -la ~/.antigravity-ide ~/.gemini/antigravity-ide 2>&1
```

For a manual migration, back up the old directories, launch the new IDE once, quit it, and copy only
the files you need. Do not copy caches, lock files, or updater state. Keep the backups until the new
IDE is configured.

To reset the new IDE, quit it and move its directories to the Trash:

```bash
trash ~/.antigravity-ide
trash ~/.gemini/antigravity-ide
```

If `trash` is not installed, move the directories to the Trash in Finder. Do not use `rm -rf`.

## Livecheck and outdated cask

`antigravity-ide` had a livecheck/outdated issue after the split: `brew outdated --cask` could report
the IDE even when the installed app was current. The fix landed in PR #280831 (`2.5.5`). The current
version is `2.6.0`.

Diagnose:

```bash
brew update
brew livecheck --cask antigravity-ide
brew info --cask antigravity-ide
```

If livecheck fails, retry after `brew update`; the vendor endpoint can lag. Do not bypass checksums to
work around a livecheck failure. If the cask is genuinely behind the vendor release, report it to
Homebrew with the `brew livecheck` output.

## Gatekeeper and quarantine

Symptoms include "App is damaged and can't be opened", an `xattr` error, or a refusal to launch after a
manual download. The historical `agy` xattr issue on the pre-split cask was fixed by PR #246184; that
was a CLI shim problem, not a GUI app problem.

Inspect quarantine attributes:

```bash
xattr -l /Applications/Antigravity.app
xattr -l "/Applications/Antigravity IDE.app"
```

Verify the download before changing attributes:

```bash
shasum -a 256 ~/Downloads/Antigravity.dmg
```

Compare the output with [cask-reference.md](cask-reference.md#sha-256-matrix). If the checksum matches
and the app still refuses to launch, reinstall through Homebrew:

```bash
brew reinstall --cask antigravity
brew reinstall --cask antigravity-ide
```

Do not blindly run `xattr -dr com.apple.quarantine` on an app from an unknown source. Remove quarantine
only after verifying the checksum and the source.

## Checksum mismatch

Homebrew verifies the DMG during install. To see the expected and downloaded values:

```bash
brew fetch --cask --force antigravity
brew fetch --cask --force antigravity-ide
```

The command prints the downloaded artifact's SHA-256. Compare it with the platform row in
[cask-reference.md](cask-reference.md#sha-256-matrix).

A mismatch usually means a corrupted download or a changed artifact. Retry once; if it persists, report
it to Homebrew rather than bypassing the check.

## macOS version mismatch

| Cask | Cask minimum | Google's download page |
| --- | --- | --- |
| `antigravity` | macOS 13 Ventura | Has said macOS 12 |
| `antigravity-ide` | macOS 12 Monterey | macOS 12 |

Check your system and the cask metadata:

```bash
sw_vers
brew info --cask antigravity | head -n 8
brew info --cask antigravity-ide | head -n 8
```

If you are on macOS 12 and want the App, Homebrew will refuse because the cask requires 13. Use the IDE
or upgrade macOS. If you are on macOS 13 or newer, both casks are installable. The discrepancy is a
cask policy, not a download limitation; report it if Google changes the requirement.

## Architecture mismatch

```bash
uname -m
sysctl -n sysctl.proc_translated 2>/dev/null
```

- `arm64` with `sysctl.proc_translated` = `0`: native Apple Silicon.
- `x86_64` with `sysctl.proc_translated` = `1`: a process running under Rosetta.
- `x86_64` with `0`: Intel Mac.

Homebrew selects `darwin-arm` or `darwin-x64` automatically. If you download a DMG manually, pick the
matching row in [cask-reference.md](cask-reference.md#sha-256-matrix). A "bad CPU type" error usually
means the wrong architecture or a Rosetta shell.

## Version skew

Both GUI casks declare `auto_updates true`, so the app can be newer than the cask metadata. Compare:

```bash
mdls -name kMDItemVersion /Applications/Antigravity.app
mdls -name kMDItemVersion "/Applications/Antigravity IDE.app"
brew info --cask antigravity | head -n 5
brew info --cask antigravity-ide | head -n 5
```

| Observation | Meaning | Action |
| --- | --- | --- |
| App newer than cask | Vendor self-update ran; tap lags | Leave it, or wait for the tap |
| App older than cask | Tap advanced but the cask was not upgraded | `brew upgrade --cask --greedy-auto-updates <token>` |
| Same version | Consistent | None |

Do not run `--greedy` or `--greedy-auto-updates` blindly. They install the tap's version even when the
app is newer, which is a downgrade.

## Uninstall leftovers

`brew uninstall --cask antigravity` removes the app but leaves its data. `--zap` moves the cask's `zap`
paths to the Trash. The same applies to `antigravity-ide`.

Verify:

```bash
ls -la ~/.antigravity ~/.gemini/antigravity 2>&1
ls -la ~/.antigravity-ide ~/.gemini/antigravity-ide 2>&1
ls -la ~/Library/Application\ Support/Antigravity 2>&1
ls -la ~/Library/Application\ Support/Antigravity\ IDE 2>&1
```

> **Warning:** Zapping the App also trashes `~/.antigravity` and `~/.gemini/antigravity`, which are the
> pre-split IDE's paths. Back up any old IDE data before `brew uninstall --cask --zap antigravity`.

Use `trash` for manual cleanup. It is recoverable; `rm -rf` is not.

## Reporting

- **Cask metadata, checksums, livecheck, or install failures:** open an issue against
  [Homebrew/homebrew-cask](https://github.com/Homebrew/homebrew-cask/issues).
- **App or IDE product bugs:** use Google Antigravity's support channels, linked from
  <https://antigravity.google/support>.

Collect this before asking for help:

```bash
brew info --cask antigravity
brew info --cask antigravity-ide
brew list --cask | grep antigravity
mdls -name kMDItemCFBundleIdentifier /Applications/Antigravity.app
mdls -name kMDItemCFBundleIdentifier "/Applications/Antigravity IDE.app"
mdls -name kMDItemVersion /Applications/Antigravity.app
mdls -name kMDItemVersion "/Applications/Antigravity IDE.app"
sw_vers
uname -m
```

Redact account identifiers, tokens, and project IDs before sharing.

## Related

- [README.md](README.md) — overview and decision table
- [product-history.md](product-history.md) — the split and the IDE-loss window
- [cask-reference.md](cask-reference.md) — checksums, livecheck, artifacts
- [installation-and-migration.md](installation-and-migration.md) — install, migrate, upgrade, remove
