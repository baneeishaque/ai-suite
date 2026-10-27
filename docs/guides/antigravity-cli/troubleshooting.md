# Troubleshooting

> **Scope:** Homebrew cask installs, PATH resolution, keyring access, SSH clipboard, vendor self-updater,
> and version skew · **Verified:** 2026-10-27

## Quick symptom table

| Symptom | Likely cause | Go to |
| --- | --- | --- |
| `agy: command not found` | Binary directory not on `PATH` | [PATH resolution](#path-resolution) |
| The wrong `agy` runs after installing twice | Cask and official installer both present | [Duplicate installs](#duplicate-installs) |
| `secret keyring is locked` or a launch hang | Keychain or Secret Service unavailable | [Keyring access](#keyring-access) |
| `Ctrl+V` image paste fails over SSH | Clipboard not forwarded | [SSH clipboard](#ssh-clipboard) |
| `another background updater process is already active` | Stale `update.lock` | [Updater locks](#updater-locks) |
| `brew upgrade` does nothing | `auto_updates true` | [Homebrew version skew](#homebrew-version-skew) |
| `--greedy` replaced a newer binary with an older one | Tap lagged the vendor updater | [Homebrew version skew](#homebrew-version-skew) |
| CLI starts in `default` instead of `auto` | `auto` unavailable for the account or platform | [Execution-mode fallback](#execution-mode-fallback) |
| Headless run exits with `authentication required` | No cached credentials in a non-interactive environment | [Headless authentication](#headless-authentication) |
| API-key auth exits at startup | `modelProvider` set but `GEMINI_API_KEY` missing | [API-key authentication](#api-key-authentication) |

## PATH resolution

Check what the shell actually resolves:

```bash
type -a agy
command -v agy
echo "$PATH" | tr ':' '\n' | grep -E 'homebrew|\.local/bin'
```

Expected locations:

| Install source | Path |
| --- | --- |
| Homebrew cask, Apple Silicon | `/opt/homebrew/bin/agy` |
| Homebrew cask, Intel | `/usr/local/bin/agy` |
| Official installer | `~/.local/bin/agy` |

If the Homebrew path is missing, confirm the cask is installed and the symlink exists:

```bash
brew list --cask | grep antigravity-cli
ls -l "$(brew --prefix)/bin/agy"
```

If the symlink is missing but the cask is installed, reinstall:

```bash
brew reinstall --cask antigravity-cli
```

If you used the official installer, add `~/.local/bin` to `PATH` in `~/.zshrc` or `~/.bashrc`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Then reload the profile:

```bash
source ~/.zshrc
```

## Duplicate installs

`type -a agy` prints every match in `PATH` order. The first one wins.

```bash
type -a agy
```

If both the cask and the official installer are present, pick one:

```bash
# Keep Homebrew, remove the manual binary
trash ~/.local/bin/agy

# Or keep the manual binary, remove the cask
brew uninstall --cask antigravity-cli
```

Do not simply reorder `PATH` and forget about it; version drift between the two installs is hard to spot
later.

## Keyring access

The CLI stores tokens in the OS keyring: Apple Keychain on macOS, Secret Service over D-Bus on Linux, and
Windows Credential Manager on Windows.

### macOS

1. Open **Keychain Access**.
2. Search for `Antigravity CLI`.
3. Open **Get Info** > **Access Control**.
4. Confirm `agy` is allowed.

For a headless or SSH session, unlock the login keychain interactively:

```bash
security set-keychain-settings -l -u -t 300 ~/Library/Keychains/login.keychain-db
security unlock-keychain ~/Library/Keychains/login.keychain-db
```

Re-lock when finished:

```bash
security lock-keychain ~/Library/Keychains/login.keychain-db
```

### Linux

Ensure GNOME Keyring or KWallet is unlocked and a D-Bus session exists. In a headless shell:

```bash
export $(dbus-launch)
```

If the keyring service is still unreachable, the CLI cannot read cached credentials; use API-key or ADC
authentication for that environment.

## SSH clipboard

Image and media paste uses terminal clipboard protocols that plain SSH does not forward.

1. Use a terminal that supports OSC 52, such as iTerm2 or Ghostty.
2. In iTerm2, enable **Settings** > **General** > **Selection** >
   **Applications in terminal may access clipboard**.
3. Inside `tmux`, enable clipboard forwarding:

   ```tmux
   set -s set-clipboard on
   ```

Text paste generally works without these steps; the failure is specific to graphical clipboard content.

## Updater locks

The vendor updater uses `~/.gemini/antigravity-cli/updater/update.lock` and a 15-minute debounce marker. A
crashed updater can leave the lock behind.

```bash
ls -la ~/.gemini/antigravity-cli/updater/
```

Remove the stale lock:

```bash
# Vendor-documented fix
rm -f ~/.gemini/antigravity-cli/updater/update.lock

# macOS-safe alternative (recoverable)
trash ~/.gemini/antigravity-cli/updater/update.lock
```

Disable vendor auto-update if you manage versions through Homebrew:

```bash
export AGY_CLI_DISABLE_AUTO_UPDATE=true
```

Also confirm your user owns the install directory:

```bash
ls -ld ~/.local/bin
ls -ld "$(brew --prefix)/bin"
```

A read-only or root-owned directory prevents the updater from replacing the binary.

## Homebrew version skew

`auto_updates true` creates two independent version authorities:

```bash
agy --version
brew info --cask antigravity-cli | head -n 5
```

Cases:

| Observation | Meaning | Action |
| --- | --- | --- |
| Binary newer than cask | Vendor self-update ran; tap lags | Leave it, or wait for the tap |
| Binary older than cask | Tap advanced but the cask was not upgraded | `brew upgrade --cask --greedy-auto-updates antigravity-cli` |
| Same version | Consistent | None |

Do not run `--greedy` or `--greedy-auto-updates` blindly. They install the tap's version even when the
binary is newer, which is a downgrade.

If you want Homebrew to own updates permanently:

```bash
export AGY_CLI_DISABLE_AUTO_UPDATE=true
brew upgrade --cask --greedy-auto-updates antigravity-cli
```

## Execution-mode fallback

`auto` mode is Preview and requires the terminal sandbox. It is unavailable:

- to business and enterprise accounts,
- on Windows versions without the required sandbox support,
- on Linux hosts or containers that block unprivileged user namespaces,
- on CLI versions older than `1.3.5` on macOS/Linux or `1.4.4` on Windows.

When unavailable, the CLI starts in `default` and `auto` is absent from `Shift+Tab` cycling and `/config`.
In headless mode, `--mode=auto` prints a warning and continues in `default`.

## Headless authentication

Headless mode uses cached credentials. A non-interactive run with no credentials exits with
`authentication required` rather than opening a browser.

Options:

1. Authenticate once interactively on the same machine or user account.
2. Use a Gemini API key:
   - set `modelProvider: "gemini"` in `settings.json`;
   - export `GEMINI_API_KEY`.
3. Use ADC:
   - run `gcloud auth application-default login`;
   - export `AGY_ADC_AUTH=true`.

## API-key authentication

| Symptom | Cause | Fix |
| --- | --- | --- |
| Exits at startup saying `GEMINI_API_KEY` is not set | `modelProvider: "gemini"` but no key | Export the key or remove `modelProvider` |
| Sign-in screen still appears | `modelProvider` has an unrecognized value | Use exactly `"gemini"` and restart |
| `GOOGLE_API_KEY` or `.env` value ignored | Only `GEMINI_API_KEY` from the environment is read | Export `GEMINI_API_KEY` in the shell |
| First request fails | Key is invalid, revoked, or lacks model access | Verify the key in Google AI Studio |

## Install and archive failures

If `brew install --cask antigravity-cli` fails:

1. Confirm macOS is 12 Monterey or newer.
2. Confirm the architecture matches the artifact:

   ```bash
   uname -m
   ```

   `arm64` uses `cli_mac_arm64.tar.gz`; `x86_64` uses `cli_mac_x64.tar.gz`.

3. Check network reachability to the download host:

   ```bash
   curl -I --connect-timeout 10 --max-time 30 \
     https://storage.googleapis.com/antigravity-public/antigravity-cli/
   ```

4. Re-fetch and let Homebrew verify the checksum again:

   ```bash
   brew fetch --cask --force antigravity-cli
   ```

   The command prints the downloaded artifact's SHA-256. Compare it with the platform row in
   [cask-reference.md](cask-reference.md#sha-256-matrix).

5. Run `brew doctor` and resolve any reported prefix or permission problems.

A checksum mismatch usually indicates a corrupted download or a changed artifact. Retry once; if it
persists, report it to Homebrew rather than bypassing the check.

## Reset the CLI configuration

Back up first; do not delete settings you may want to recover:

```bash
mv ~/.gemini/antigravity-cli/settings.json \
   ~/.gemini/antigravity-cli/settings.json.bak
mv ~/.gemini/antigravity-cli/keybindings.json \
   ~/.gemini/antigravity-cli/keybindings.json.bak
```

The CLI recreates defaults on the next launch. For a complete reset, run `/logout` first, then:

```bash
brew uninstall --cask --zap antigravity-cli
brew install --cask antigravity-cli
```

## Diagnostic bundle

Collect these before asking for help:

```bash
agy --version
command -v agy
type -a agy
brew info --cask antigravity-cli
uname -m
sw_vers
ls -la ~/.gemini/antigravity-cli/
ls -la ~/.gemini/antigravity-cli/updater/
```

Redact account identifiers, tokens, and project IDs before sharing.

## Reporting

- CLI bugs and product issues: Google Antigravity support channels linked from
  <https://antigravity.google/support>.
- Cask metadata, checksum, or install-script problems: open an issue against
  [Homebrew/homebrew-cask](https://github.com/Homebrew/homebrew-cask/issues).

## Related

- [README.md](README.md) — overview
- [installation.md](installation.md) — install and removal
- [cask-reference.md](cask-reference.md) — checksums and updater semantics
- [configuration.md](configuration.md) — auth, permissions, settings
