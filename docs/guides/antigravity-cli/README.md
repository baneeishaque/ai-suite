# Google Antigravity CLI — Homebrew Cask Explainer

> **Cask:** [`antigravity-cli`](https://formulae.brew.sh/cask/antigravity-cli) ·
> **Tap:** `homebrew/cask` · **Version explained:** `1.4.8,5447777392656384` ·
> **Verified:** 2026-10-27

Google Antigravity CLI is Google's terminal-first client for Antigravity agents. The Homebrew cask
`antigravity-cli` installs that client as a single self-updating binary and exposes it on `PATH` under the
short command name **`agy`**.

This folder is an independent, source-cited explainer for the cask and the CLI it installs. It is not
Google documentation, and it is not affiliated with Google or Homebrew.

## TL;DR

```bash
brew install --cask antigravity-cli
agy --version
agy
```

The first interactive launch walks through color scheme, rendering mode, and workspace trust, then opens a
browser for Google sign-in (or uses a cached keyring token).

## What the cask actually does

| Action | Detail |
| --- | --- |
| Downloads | `cli_mac_arm64.tar.gz` on Apple Silicon or `cli_mac_x64.tar.gz` on Intel, from `storage.googleapis.com/antigravity-public/` |
| Installs | The archive's `antigravity` executable into the Homebrew Caskroom |
| Exposes | A `$HOMEBREW_PREFIX/bin/agy` symlink pointing at the Caskroom executable |
| Requires | macOS 12 Monterey or newer |
| Self-updates | Yes (`auto_updates true`); the vendor updater uses `~/.gemini/antigravity-cli/updater/` |
| Configuration | `~/.gemini/antigravity-cli/settings.json` and `keybindings.json` |
| Removal | `brew uninstall --cask antigravity-cli`; add `--zap` to trash the config directory too |

## Three things people get wrong

1. **The command is `agy`, not `antigravity`.** The cask stages a binary named `antigravity` and renames it
   to `agy` on `PATH`. Typing `antigravity` will not find this install unless another install provides it.
2. **`brew upgrade` will not upgrade it by default.** Because the cask declares `auto_updates true`,
   Homebrew treats the vendor's updater as authoritative. Use
   `brew upgrade --cask --greedy-auto-updates antigravity-cli` only when you deliberately want the tap's
   version.
3. **Mixing the cask and the official installer leaves two binaries.** The cask writes
   `$HOMEBREW_PREFIX/bin/agy`; the official installer writes `~/.local/bin/agy`. Whichever directory comes
   first in `PATH` wins, so the two can silently diverge in version and configuration.

## Documentation map

| Document | Read it for |
| --- | --- |
| [installation.md](installation.md) | Install, verify, upgrade, pin, uninstall, and avoid duplicate installs |
| [cask-reference.md](cask-reference.md) | Every cask field: version encoding, URLs, SHA-256 matrix, artifacts, livecheck, analytics |
| [configuration.md](configuration.md) | `settings.json`, `keybindings.json`, execution modes, permissions, authentication, environment variables |
| [usage.md](usage.md) | Slash commands, keyboard shortcuts, CLI flags, headless/print mode, CI examples |
| [troubleshooting.md](troubleshooting.md) | PATH, keyring, SSH clipboard, updater locks, and Homebrew-specific version skew |
| [AGENTS.md](AGENTS.md) | Folder ownership and maintenance contract for AI agents |

## At a glance

| Field | Value |
| --- | --- |
| Cask token | `antigravity-cli` |
| Full name | Google Antigravity CLI |
| Description | Terminal interface for Antigravity agents |
| Homepage | <https://antigravity.google/product/antigravity-cli> |
| Version | `1.4.8,5447777392656384` (upstream version `1.4.8`, build `5447777392656384`) |
| Minimum OS | macOS 12 Monterey; Linux builds also published |
| Installed command | `agy` |
| Config directory | `~/.gemini/antigravity-cli/` |
| Cask source | [`Casks/a/antigravity-cli.rb`](https://github.com/Homebrew/homebrew-cask/blob/88bd762a0ccedc906b2956e52e5b85b7acf87cd2/Casks/a/antigravity-cli.rb) |
| Analytics (30 / 90 / 365 days) | 8,978 / 19,898 / 41,459 installs |

## Sources

Vendor documentation:

- Product page: <https://antigravity.google/product/antigravity-cli>
- Quickstart (CLI tab): <https://antigravity.google/docs/getting-started?tab=cli>
- Authentication: <https://antigravity.google/docs/install/?tab=cli>
- CLI reference: <https://antigravity.google/docs/cli/reference/>
- CLI settings and tips: <https://antigravity.google/docs/cli/using/>
- Execution modes: <https://antigravity.google/docs/cli/modes/>
- Headless mode: <https://antigravity.google/docs/cli/headless/>
- Troubleshooting: <https://antigravity.google/docs/cli/troubleshooting/>

Homebrew:

- Cask page: <https://formulae.brew.sh/cask/antigravity-cli>
- Cask JSON API: <https://formulae.brew.sh/api/cask/antigravity-cli.json>
- Cask Ruby source (tap HEAD `88bd762a0ccedc906b2956e52e5b85b7acf87cd2`):
  <https://github.com/Homebrew/homebrew-cask/blob/88bd762a0ccedc906b2956e52e5b85b7acf87cd2/Casks/a/antigravity-cli.rb>

## Verification status

| Claim type | Status |
| --- | --- |
| Cask metadata, URLs, checksums, artifacts | Read from the cask JSON API and the Ruby source on 2026-10-27 |
| CLI behaviour, flags, settings keys | Read from Google's official documentation on 2026-10-27 |
| Local runtime behaviour | **Not reproduced** — `agy` was not installed and the cask was not present in `brew list --cask` on the verification machine |

Treat runtime examples as vendor-documented until you reproduce them on your own machine.
