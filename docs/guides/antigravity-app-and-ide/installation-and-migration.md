# Installation, Upgrade, and Migration

> **Primary paths:** `brew install --cask antigravity` · `brew install --cask antigravity-ide` ·
> **Verified:** 2026-10-27

## Choose the right cask

| You want | Command | App bundle | CLI command |
| --- | --- | --- | --- |
| Antigravity 2 agent platform | `brew install --cask antigravity` | `Antigravity.app` | none |
| Antigravity IDE | `brew install --cask antigravity-ide` | `Antigravity IDE.app` | `agy-ide` or `antigravity-ide` |
| Both GUI apps | Install both casks | Both bundles | `agy-ide` / `antigravity-ide` from the IDE |
| Terminal CLI only | `brew install --cask antigravity-cli` | none | `agy` |

If you are unsure which product you used before the May 2026 split, read
[product-history.md](product-history.md) first. The short version is that the old `antigravity` cask
was the IDE, and the current `antigravity` cask is the App.

## Prerequisites

| Requirement | `antigravity` | `antigravity-ide` |
| --- | --- | --- |
| macOS | 13 Ventura or newer | 12 Monterey or newer |
| Architecture | Apple Silicon or 64-bit Intel | Apple Silicon or 64-bit Intel |
| Homebrew | Working `brew` with `homebrew/cask` | Working `brew` with `homebrew/cask` |
| Browser | Needed for Google sign-in | Needed for Google sign-in |
| Disk | Enough space for an Electron app | Enough space for an Electron app |

The App cask is stricter than Google's download page, which has said macOS 12 for the App. The cask
declares `depends_on macos: :ventura`, so Homebrew refuses to install it on macOS 12. Treat the cask
as authoritative for Homebrew installs and see
[troubleshooting.md](troubleshooting.md#macos-version-mismatch) if that discrepancy matters to you.

## Install the App

```bash
brew install --cask antigravity
```

What happens:

1. Homebrew downloads the DMG for your architecture from
   `storage.googleapis.com/antigravity-public/antigravity-hub/`.
2. It verifies the DMG against the cask's SHA-256.
3. It stages the DMG under `$(brew --caskroom)/antigravity/<version>/`.
4. It installs `Antigravity.app` to `/Applications/Antigravity.app`.

No `sudo` is required for a standard Homebrew prefix.

Verify:

```bash
brew info --cask antigravity | head -n 8
ls -ld /Applications/Antigravity.app
mdls -name kMDItemCFBundleIdentifier /Applications/Antigravity.app
mdls -name kMDItemVersion /Applications/Antigravity.app
```

Expected bundle identifier: `com.google.antigravity`.

Launch:

```bash
open -a "Antigravity"
```

The App's own onboarding handles sign-in and workspace setup. The cask installs no command-line
binary, so there is no `antigravity` command to run.

## Install the IDE

```bash
brew install --cask antigravity-ide
```

What happens:

1. Homebrew downloads the DMG for your architecture from `edgedl.me.gvt1.com`.
2. It verifies the DMG against the cask's SHA-256.
3. It stages the DMG under `$(brew --caskroom)/antigravity-ide/<version>/`.
4. It installs `Antigravity IDE.app` to `/Applications/Antigravity IDE.app`.
5. It creates two symlinks in `$HOMEBREW_PREFIX/bin`: `agy-ide` and `antigravity-ide`, both pointing
   at the IDE's bundled `antigravity-ide` executable.

Verify:

```bash
brew info --cask antigravity-ide | head -n 8
ls -ld "/Applications/Antigravity IDE.app"
mdls -name kMDItemCFBundleIdentifier "/Applications/Antigravity IDE.app"
mdls -name kMDItemVersion "/Applications/Antigravity IDE.app"
command -v agy-ide
command -v antigravity-ide
agy-ide --version
```

Expected bundle identifier: `com.google.antigravity-ide`.

Launch:

```bash
open -a "Antigravity IDE"
```

## Install both

Both GUI casks can coexist. Homebrew does not declare `conflicts_with` for either one, and the apps
use different bundles and identifiers after the split.

| Resource | App | IDE |
| --- | --- | --- |
| App path | `/Applications/Antigravity.app` | `/Applications/Antigravity IDE.app` |
| Bundle identifier | `com.google.antigravity` | `com.google.antigravity-ide` |
| Config root | `~/.antigravity` | `~/.antigravity-ide` |
| Gemini data | `~/.gemini/antigravity` | `~/.gemini/antigravity-ide` |
| Application Support | `~/Library/Application Support/Antigravity` | `~/Library/Application Support/Antigravity IDE` |
| CLI binary | none | `agy-ide`, `antigravity-ide` |

The Dock shows two icons: the App has a white background icon, the IDE has a black grid icon. If you
want only one product, uninstall the other cask; see [Uninstall](#uninstall).

## Migrate from the pre-split `antigravity`

The pre-split `antigravity` cask installed the IDE as `Antigravity.app` with bundle identifier
`com.google.antigravity`. The current `antigravity` cask installs the App with the same app path and
the same bundle identifier. That is why upgrading felt like losing the IDE.

### Step 1 — Identify what you have

```bash
brew list --cask | grep -E '^(antigravity|antigravity-ide)$'
brew info --cask antigravity | head -n 8
ls -ld /Applications/Antigravity.app "/Applications/Antigravity IDE.app" 2>&1
mdls -name kMDItemCFBundleIdentifier /Applications/Antigravity.app 2>&1
mdls -name kMDItemCFBundleIdentifier "/Applications/Antigravity IDE.app" 2>&1
```

| Observation | Meaning |
| --- | --- |
| Only `Antigravity.app` exists and opens the agent platform | You have the App, not the IDE |
| Only `Antigravity.app` exists and opens the editor | You have the pre-split IDE (1.x) |
| `Antigravity IDE.app` exists | You have the post-split IDE |
| Both bundles exist | You have both products installed |

### Step 2 — Decide the target layout

| Target | Action |
| --- | --- |
| App only | Keep `antigravity`; uninstall `antigravity-ide` if present |
| IDE only | Install `antigravity-ide`; optionally uninstall `antigravity` |
| Both | Keep both casks |
| CLI only | Install `antigravity-cli`; the GUI casks are optional |

### Step 3 — Install the missing cask

To restore the IDE:

```bash
brew install --cask antigravity-ide
```

This installs `Antigravity IDE.app` alongside `Antigravity.app`. The old `Antigravity.app` is not
renamed or moved. If the old 1.x IDE was replaced by the App, the IDE comes back under a new app name
and a new bundle identifier.

To restore a command named `agy`, install the CLI cask:

```bash
brew install --cask antigravity-cli
```

The App cask has no binary. The IDE cask provides `agy-ide` and `antigravity-ide`, not `agy`.

### Step 4 — Understand the data paths

The cask `zap` lists are the best evidence of where each product stores data:

| Data | New App | New IDE |
| --- | --- | --- |
| Config root | `~/.antigravity` | `~/.antigravity-ide` |
| Gemini data | `~/.gemini/antigravity` | `~/.gemini/antigravity-ide` |
| Application Support | `~/Library/Application Support/Antigravity` | `~/Library/Application Support/Antigravity IDE` |
| Caches | `~/Library/Caches/com.google.antigravity` | `~/Library/Caches/com.google.antigravity-ide` |
| Preferences | `~/Library/Preferences/com.google.antigravity.plist` | `~/Library/Preferences/com.google.antigravity-ide.plist` |
| Saved state | `~/Library/Saved Application State/com.google.Antigravity.savedState` | `~/Library/Saved Application State/com.google.antigravity-ide.savedState` |

The 1.x IDE's `zap` list covered `~/.antigravity/`, `~/Library/Application Support/Antigravity`, the
`com.google.antigravity` caches, HTTP storages, preferences, and saved state. The new App reuses those
paths and adds `~/.gemini/antigravity` and `~/Library/Logs/Antigravity`. The new IDE uses new paths.

This table is an inference from the cask sources, not a Google migration guarantee. The pattern is
clear: the new App inherited the old IDE's paths, and the new IDE uses new paths. Consequences:

- The new App may read the old IDE's configuration and recent-workspace data.
- The new IDE may start with fresh configuration because its paths are new.
- Zapping the App can delete the old IDE's data, because the paths overlap.

Do not delete the old directories until you have launched both apps and confirmed what each one reads.

### Step 5 — Migrate settings manually if needed

Google does not document an automatic migration path for the new IDE. If you want the old IDE
settings in the new IDE, treat it as a manual copy:

1. Quit both apps.
2. Back up the old directories:

   ```bash
   cp -R ~/.antigravity ~/.antigravity.pre-migration.bak
   cp -R ~/.gemini/antigravity ~/.gemini/antigravity.pre-migration.bak
   ```

3. Launch the new IDE once, then quit it, so it creates its own directories.
4. Copy only the specific files you need from the backup into `~/.antigravity-ide` or
   `~/.gemini/antigravity-ide`.
5. Do not copy caches, lock files, or updater state.
6. Keep the backups until the new IDE is configured and verified.

If the new IDE does not recognize a copied file, remove it and let the IDE recreate its default. Do not
copy the old app bundle or preferences plist wholesale; the bundle identifiers differ.

### Step 6 — Remove the old layout

If you want the App only:

```bash
brew uninstall --cask antigravity-ide
```

If you want the IDE only:

```bash
brew uninstall --cask antigravity
```

> **Warning:** `brew uninstall --cask --zap antigravity` trashes `~/.antigravity`,
> `~/.gemini/antigravity`, and the other App paths. Those include the legacy `~/.antigravity` path the
> pre-split IDE used. If you still need the old IDE data, back it up before zapping the App.

## Upgrade

### Vendor-owned updates (default)

Both GUI casks declare `auto_updates true`, so the apps update themselves through Google's Electron
ShipIt updater. A plain `brew upgrade` skips them. This is the intended default: let the vendor
updater keep the app current.

Check the installed versions independently of Homebrew:

```bash
mdls -name kMDItemVersion /Applications/Antigravity.app
mdls -name kMDItemVersion "/Applications/Antigravity IDE.app"
```

### Homebrew-owned updates

If you want Homebrew to be the only updater:

```bash
brew upgrade --cask --greedy-auto-updates antigravity
brew upgrade --cask --greedy-auto-updates antigravity-ide
```

> **Downgrade hazard:** `--greedy-auto-updates` installs the tap's version even when the app's
> self-updated version is newer. Compare the app version with `brew info --cask` before forcing an
> upgrade.

### Upgrade only one product

```bash
# App only
brew upgrade --cask --greedy-auto-updates antigravity

# IDE only
brew upgrade --cask --greedy-auto-updates antigravity-ide
```

### Reinstall without changing version

```bash
brew reinstall --cask antigravity
brew reinstall --cask antigravity-ide
```

This is useful when an app bundle or symlink is damaged but the version is already correct.

## Pin and downgrade

```bash
# Stop Homebrew from touching a cask
brew pin antigravity
brew pin antigravity-ide

# Later, allow upgrades again
brew unpin antigravity
brew unpin antigravity-ide
```

Pinning does not disable the vendor self-updater. If you need a truly frozen version, you must also
prevent the app from updating itself through its own settings or by controlling network access; the
casks do not expose a documented environment variable for this.

A controlled downgrade is safest by uninstalling, then installing the older cask revision from the
Homebrew cask Git history. Do not assume versioned tokens such as `antigravity@2.25` exist; versioned
cask tokens are not guaranteed.

## Uninstall

### App

```bash
brew uninstall --cask antigravity
```

This removes the Caskroom artifact and `Antigravity.app`. It leaves the app's data paths intact, so a
later reinstall keeps your settings.

Full removal, including data:

```bash
brew uninstall --cask --zap antigravity
```

`--zap` moves the paths in the cask's `zap` list to the Trash. See the warning in
[Step 6](#step-6--remove-the-old-layout) if you also need the old IDE data.

### IDE

```bash
brew uninstall --cask antigravity-ide
```

Full removal, including data:

```bash
brew uninstall --cask --zap antigravity-ide
```

This removes `Antigravity IDE.app`, the `agy-ide` and `antigravity-ide` symlinks, and the IDE-specific
data paths. It does not touch the App's paths.

### CLI

The CLI cask has its own removal procedure; see
[the CLI installation guide](../antigravity-cli/installation.md#uninstall).

### Verify removal

```bash
ls -ld /Applications/Antigravity.app "/Applications/Antigravity IDE.app" 2>&1
command -v agy-ide
command -v antigravity-ide
ls -la ~/.antigravity ~/.gemini/antigravity 2>&1
ls -la ~/.antigravity-ide ~/.gemini/antigravity-ide 2>&1
```

Use `trash` rather than `rm -rf` for any manual cleanup on macOS. `trash` is recoverable; `rm -rf` is
not.

## Manual DMG install

Only use this when you cannot use Homebrew. The cask's exact artifacts for the current versions are:

| Product | Platform | URL | SHA-256 |
| --- | --- | --- | --- |
| App | Apple Silicon | `https://storage.googleapis.com/antigravity-public/antigravity-hub/2.26.0-6546645232517120/darwin-arm/Antigravity.dmg` | `f9d707e367bc5f7c87627defa125dcffabc81b03b4844bc361da9e4821e89ad0` |
| App | Intel | `https://storage.googleapis.com/antigravity-public/antigravity-hub/2.26.0-6546645232517120/darwin-x64/Antigravity.dmg` | `8865972294803ab8720e9562d4faf3742f075364c09b6087aa554f2740c45927` |
| IDE | Apple Silicon | `https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/2.6.0-5526304964083712/darwin-arm/Antigravity%20IDE.dmg` | `7971e71ffaec88f9d9480ea2bcc80aebaee59c0ac06df6f0141ef59046b49c9c` |
| IDE | Intel | `https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/2.6.0-5526304964083712/darwin-x64/Antigravity%20IDE.dmg` | `4e13a2073e666ac66b7e25e5a8943938f4bc0a17aea19ac1061dadfa80690e3b` |

Procedure:

```bash
# Download the DMG for your architecture, then verify it
shasum -a 256 ~/Downloads/Antigravity.dmg

# Mount it and copy the app to /Applications
hdiutil attach ~/Downloads/Antigravity.dmg
ls /Volumes
cp -R "/Volumes/<volume>/Antigravity.app" /Applications/
hdiutil detach "/Volumes/<volume>"
```

For the IDE, substitute `Antigravity%20IDE.dmg` and `Antigravity IDE.app`. The mounted volume name may
differ from the app name; use `ls /Volumes` to find it. Do not bypass Gatekeeper if the checksum does
not match.

## Brewfile

```ruby
cask "antigravity"
cask "antigravity-ide"
cask "antigravity-cli"
```

`brew bundle` installs all three. Remove the lines for products you do not want.

## CI and enterprise notes

- **GUI apps are not CI tools.** For automation, use the CLI cask and the `agy` command.
- **Managed Macs:** use `brew bundle` with the casks you need. Both GUI casks require a logged-in GUI
  session for first-run sign-in.
- **Deterministic versions:** pin the cask and prevent vendor self-updates. The casks do not expose a
  documented environment variable that disables the GUI updater.
- **Tap version:** use `brew upgrade --cask --greedy-auto-updates` only when you deliberately want the
  tap's version, and check for a downgrade first.
- **No Linux or Windows artifacts:** the Homebrew casks are macOS-only. Use Google's native installers
  on other platforms.

## Related

- [README.md](README.md) — overview and decision table
- [product-history.md](product-history.md) — why the old token changed meaning
- [cask-reference.md](cask-reference.md) — checksums, livecheck, artifacts
- [troubleshooting.md](troubleshooting.md) — wrong app, missing commands, version skew
- [the CLI installation guide](../antigravity-cli/installation.md) — `agy` install and removal
