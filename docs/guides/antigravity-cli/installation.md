# Installation, Upgrade, and Removal

> **Primary path:** Homebrew cask `antigravity-cli` · **Installed command:** `agy` ·
> **Config:** `~/.gemini/antigravity-cli/`

## Choose an installation method

| Method | Command | Binary location | Best for |
| --- | --- | --- | --- |
| Homebrew cask | `brew install --cask antigravity-cli` | `$HOMEBREW_PREFIX/bin/agy` | macOS users who already manage tools with Homebrew |
| Official installer | `curl -fsSL https://antigravity.google/cli/install.sh \| bash` | `~/.local/bin/agy` | Linux, or macOS without Homebrew |
| Windows PowerShell | `irm https://antigravity.google/cli/install.ps1 \| iex` | `%LOCALAPPDATA%\agy\bin` | Windows |
| Windows CMD | `curl -fsSL https://antigravity.google/cli/install.cmd -o install.cmd && install.cmd && del install.cmd` | `%LOCALAPPDATA%\agy\bin` | Windows without PowerShell |

Pick **one** method per machine. The cask and the official installer both create an `agy` command, but in
different directories, and the one earlier in `PATH` silently wins.

## Prerequisites

| Requirement | Detail |
| --- | --- |
| macOS | 12 Monterey or newer |
| Architecture | Apple Silicon or 64-bit Intel |
| Homebrew | A working `brew` with the default `homebrew/cask` tap |
| Browser | Needed for the first OAuth sign-in unless you use an API key or ADC |
| Keyring | Apple Keychain must be unlocked for silent token reuse |

Linux builds exist upstream (`linux-x64` and `linux-arm`), but this cask is primarily documented for macOS.
Homebrew on Linux may install it; verify the artifact and sandbox behaviour on your distribution.

## Install with Homebrew

```bash
brew install --cask antigravity-cli
```

What happens:

1. Homebrew downloads the tarball for your architecture from
   `storage.googleapis.com/antigravity-public/antigravity-cli/`.
2. It verifies the archive against the cask's SHA-256.
3. It stages the archive under `$(brew --caskroom)/antigravity-cli/<version>/`.
4. It creates the symlink `$HOMEBREW_PREFIX/bin/agy` pointing at the staged `antigravity` executable.

No `sudo` is required for a standard Homebrew prefix.

## Verify the install

```bash
command -v agy
agy --version
brew info --cask antigravity-cli
```

Expected shape:

- `command -v agy` prints the first `agy` on `PATH` (normally `/opt/homebrew/bin/agy` on Apple Silicon or
  `/usr/local/bin/agy` on Intel).
- `agy --version` prints the CLI version; compare it with the cask version before trusting `brew` metadata.
- `brew info --cask antigravity-cli` shows the cask version, source, and artifact list.

If `command -v agy` prints nothing, see [troubleshooting.md](troubleshooting.md).

## First launch

```bash
mkdir -p ~/src/agy-demo
cd ~/src/agy-demo
agy
```

The first interactive launch configures:

1. **Color scheme** — dark, light, Solarized, colorblind-friendly variants, Tokyo Night, or terminal default.
2. **Rendering mode** — Alt-Screen (full-screen buffer) or Inline (sequential output in terminal history).
3. **Workspace trust** — confirmation before the agent indexes the directory.

Then the CLI either reuses a keyring token or opens the browser for sign-in. For headless or CI use, see
[configuration.md](configuration.md) for API-key and ADC authentication.

## PATH precedence and duplicate installs

Two independent installs produce two different binaries:

| Source | Path |
| --- | --- |
| Homebrew cask | `$HOMEBREW_PREFIX/bin/agy` |
| Official installer | `~/.local/bin/agy` |

Diagnose:

```bash
type -a agy
ls -l "$(command -v agy)"
```

If both exist, decide which one you want and remove the other, or reorder `PATH` deliberately. A common
mistake is to install with Homebrew, then run the official installer later, and end up executing
`~/.local/bin/agy` while reading Homebrew's version metadata.

The official installer also edits shell profiles to add `~/.local/bin` to `PATH` and may purge legacy
`agy` / `antigravity` aliases. Its documented opt-outs are:

```bash
curl -fsSL https://antigravity.google/cli/install.sh | bash -s -- --skip-path --skip-aliases
```

## Upgrade

### Vendor-owned updates (default)

`auto_updates true` means the binary updates itself in the background. Homebrew will not upgrade the cask
on a plain `brew upgrade`. This is the intended default: let the vendor updater keep the binary current.

Check the binary independently of Homebrew:

```bash
agy --version
```

### Homebrew-owned updates

If you want Homebrew to be the only updater:

```bash
export AGY_CLI_DISABLE_AUTO_UPDATE=true
brew upgrade --cask --greedy-auto-updates antigravity-cli
```

Persist `AGY_CLI_DISABLE_AUTO_UPDATE=true` in `~/.zshrc` or `~/.bashrc` if you adopt this policy.

> **Downgrade hazard:** `--greedy-auto-updates` installs the tap's version even when the self-updated binary
> is newer. Compare `agy --version` with `brew info --cask antigravity-cli` before forcing an upgrade.

### Reinstall without changing version

```bash
brew reinstall --cask antigravity-cli
```

This is useful when the symlink or Caskroom contents are damaged but the version is already correct.

## Pin and downgrade

```bash
# Stop Homebrew from touching the cask
brew pin antigravity-cli

# Later, allow upgrades again
brew unpin antigravity-cli
```

Pinning does not disable the vendor self-updater. If you need a truly frozen version, also set
`AGY_CLI_DISABLE_AUTO_UPDATE=true`.

A controlled downgrade is safest by uninstalling, then installing the older cask revision from the
Homebrew cask Git history. Do not assume `brew install --cask antigravity-cli@1.4.7` exists; versioned
cask tokens are not guaranteed.

## Uninstall

### Standard removal

```bash
brew uninstall --cask antigravity-cli
```

This removes the Caskroom artifact and the `agy` symlink. It leaves the config directory intact, so a later
reinstall keeps your settings, keybindings, and trusted-workspace list.

### Full removal, including configuration

```bash
# 1. Purge the keyring entry from inside the CLI
agy
# then run: /logout

# 2. Remove the app and its config directory
brew uninstall --cask --zap antigravity-cli
```

`--zap` executes the cask's `zap trash: "~/.gemini/antigravity-cli"` stanza, which moves the config
directory to the Trash. It does not touch the OS keyring; `/logout` handles that.

Verify nothing remains:

```bash
command -v agy
ls -la ~/.gemini/antigravity-cli 2>&1
```

### Manual installer removal

If you used the official installer instead of the cask:

```bash
rm -f ~/.local/bin/agy
rm -rf ~/.gemini/antigravity-cli
```

On Windows, remove `%LOCALAPPDATA%\agy\bin` from `PATH` and delete the directory.

## Manual tarball install

Only use this when you cannot use Homebrew or the official installer. The cask's exact artifacts are:

| Platform | URL | SHA-256 |
| --- | --- | --- |
| macOS Apple Silicon | `https://storage.googleapis.com/antigravity-public/antigravity-cli/1.4.8-5447777392656384/darwin-arm/cli_mac_arm64.tar.gz` | `ecd1f7b35927bc23ed4496139aeb0e39b99c4b1c63d5f1f3b8fc25ab515e7631` |
| macOS Intel | `https://storage.googleapis.com/antigravity-public/antigravity-cli/1.4.8-5447777392656384/darwin-x64/cli_mac_x64.tar.gz` | `ce851c99afb9a21a8c0cadebb1b7155a951ffba76749081f0fd2c06b0a7b29c3` |

Procedure:

```bash
tmpdir=$(mktemp -d)
cd "$tmpdir"
curl -fL --connect-timeout 10 --max-time 300 -O \
  https://storage.googleapis.com/antigravity-public/antigravity-cli/1.4.8-5447777392656384/darwin-arm/cli_mac_arm64.tar.gz
shasum -a 256 cli_mac_arm64.tar.gz
tar -xzf cli_mac_arm64.tar.gz
install -m 0755 antigravity ~/.local/bin/agy
```

Substitute the Intel URL and checksum on an Intel Mac. Verify `shasum` output matches the table before
running the binary.

## CI and enterprise notes

- **CI without a browser:** authenticate with a Gemini API key (`modelProvider: "gemini"` plus
  `GEMINI_API_KEY`) or ADC (`AGY_ADC_AUTH=true`), or pre-seed a keyring token on the runner.
- **Homebrew on ephemeral runners:** install the cask, then disable the vendor updater for the job if you
  need deterministic versions.
- **Business and enterprise accounts:** `auto` mode is not available; the CLI falls back to `default` mode.
- **Proxy environments:** the terminal sandbox has its own `sandboxProxy` setting; do not assume the shell's
  `HTTPS_PROXY` is inherited by sandboxed commands.

## Related

- [README.md](README.md) — overview and the three common mistakes
- [cask-reference.md](cask-reference.md) — version encoding, checksums, livecheck
- [configuration.md](configuration.md) — authentication, settings, permissions
- [troubleshooting.md](troubleshooting.md) — PATH, keyring, updater locks
