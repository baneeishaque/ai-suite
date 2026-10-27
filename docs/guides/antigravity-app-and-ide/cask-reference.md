# Cask Reference — `antigravity` and `antigravity-ide`

> **Tap HEAD:** `896f63b6900bcf77a396b171525a221e1e379c9e` ·
> **Versions:** `2.26.0,6546645232517120` / `2.6.0,5526304964083712` · **Read on:** 2026-10-27

This page documents both GUI casks field by field: how their versions are encoded, which artifact each
platform downloads, what the checksums are, how livecheck discovers releases, and what `brew` does on
install, upgrade, and uninstall. The CLI cask is documented separately in
[the CLI guide](../antigravity-cli/cask-reference.md).

## Shared facts

| Property | `antigravity` | `antigravity-ide` |
| --- | --- | --- |
| Tap | `homebrew/cask` | `homebrew/cask` |
| `auto_updates` | `true` | `true` |
| `deprecated` / `disabled` | `false` / `false` | `false` / `false` |
| `caveats` | `null` | `null` |
| `conflicts_with` | `null` | `null` |
| Minimum macOS | 13 Ventura | 12 Monterey |
| App bundle | `Antigravity.app` | `Antigravity IDE.app` |
| Bundle identifier (from `uninstall quit:`) | `com.google.antigravity` | `com.google.antigravity-ide` |
| CLI binaries | none | `agy-ide`, `antigravity-ide` |
| Linux artifact | none | none |
| Analytics (30 / 90 / 365 days) | 4,323 / 9,509 / 62,707 | 1,344 / 3,691 / 9,191 |

Neither cask declares `conflicts_with`, so Homebrew will not block installing both. The bundle
identifier in this table is the one declared by `uninstall quit:`; it is also the identifier macOS uses
for the app. The JSON API does not expose a separate `bundle_id` field.

## Cask: `antigravity`

### Identity

| JSON field | Value |
| --- | --- |
| `token` / `full_token` | `antigravity` |
| `name` | Google Antigravity |
| `desc` | Agent orchestration platform |
| `homepage` | `https://antigravity.google/product/antigravity-2` |
| `tap` | `homebrew/cask` |
| `ruby_source_path` | `Casks/a/antigravity.rb` |
| `ruby_source_checksum.sha256` | `d8817f4cacc7b9e9e8416566d5560cb0797c3c6126fc6e364d4c51b5749ffc9b` |
| `version` | `2.26.0,6546645232517120` |
| `auto_updates` | `true` |
| `deprecated` / `disabled` | `false` / `false` |
| `caveats` | `null` |
| `conflicts_with` | `null` |

### Version encoding

The cask uses a two-part CSV version:

```ruby
version "2.26.0,6546645232517120"
```

| Component | Value | Meaning |
| --- | --- | --- |
| `version.csv.first` | `2.26.0` | Human-facing semantic version |
| `version.csv.second` | `6546645232517120` | Build or revision identifier used in the download path |

The download URL joins the two with a hyphen, so the published directory is
`2.26.0-6546645232517120`. Livecheck performs the reverse transformation: it reads the version and
build from the updater manifest and joins them with a comma.

### Download URL construction

The Ruby source builds one URL template for both macOS architectures:

```ruby
arch arm: "arm", intel: "x64"

url "https://storage.googleapis.com/antigravity-public/antigravity-hub/" \
    "#{version.csv.first}-#{version.csv.second}/darwin-#{arch}/Antigravity.dmg"
```

That expands to two concrete artifacts:

| Host platform | URL path | File |
| --- | --- | --- |
| macOS Apple Silicon | `darwin-arm/Antigravity.dmg` | `Antigravity.dmg` |
| macOS Intel | `darwin-x64/Antigravity.dmg` | `Antigravity.dmg` |

The directory uses `arm` / `x64`, not `arm64` / `x86_64`. That is why the cask declares a dedicated
`arch` variable.

### SHA-256 matrix

Checksums for version `2.26.0,6546645232517120`:

| Platform | Cask key | SHA-256 |
| --- | --- | --- |
| macOS Apple Silicon | `arm` | `f9d707e367bc5f7c87627defa125dcffabc81b03b4844bc361da9e4821e89ad0` |
| macOS Intel | `intel` | `8865972294803ab8720e9562d4faf3742f075364c09b6087aa554f2740c45927` |

In the JSON API, the top-level `url` and `sha256` are the **Apple Silicon** artifact. The `variations`
object carries the Intel override: its macOS version keys (`golden_gate`, `tahoe`, `sequoia`, `sonoma`,
and `ventura`) all point at the `darwin-x64` DMG. The `x86_64_linux` and `arm64_linux` keys are
placeholders: their checksums are `null`, and the `x86_64_linux` URL points at the macOS Intel DMG.
There is no Linux artifact in this cask.

### Artifacts

```ruby
app "Antigravity.app"

uninstall quit: "com.google.antigravity"

zap trash: [
  "~/.antigravity",
  "~/.gemini/antigravity",
  "~/Library/Application Support/Antigravity",
  "~/Library/Application Support/com.apple.sharedfilelist/com.apple.LSSharedFileList.ApplicationRecentDocuments/com.google.antigravity.sfl*",
  "~/Library/Caches/com.google.antigravity",
  "~/Library/Caches/com.google.antigravity.ShipIt",
  "~/Library/HTTPStorages/com.google.antigravity",
  "~/Library/Logs/Antigravity",
  "~/Library/Preferences/ByHost/com.google.antigravity.ShipIt.*.plist",
  "~/Library/Preferences/com.google.antigravity.plist",
  "~/Library/Saved Application State/com.google.Antigravity.savedState",
]
```

| Artifact | Effect |
| --- | --- |
| `app "Antigravity.app"` | Installs the app bundle to `/Applications/Antigravity.app` |
| `uninstall quit: "com.google.antigravity"` | Quits the app before uninstalling |
| `zap trash: [...]` | On `brew uninstall --cask --zap`, moves the listed configuration, cache, and preference paths to the Trash |

The `zap` list includes the legacy `~/.antigravity` path from the 1.x IDE and adds
`~/.gemini/antigravity`. The new App inherited the old app name and bundle identifier; that
inheritance is the root cause of the in-place replacement described in
[product-history.md](product-history.md#what-antigravity-20-changed).

### Platform support

`depends_on macos: :ventura` means macOS 13 Ventura is the minimum. The API reports
`depends_on.macos >= 13`.

The API's variation keys are:

```text
golden_gate, tahoe, sequoia, sonoma, ventura, x86_64_linux, arm64_linux
```

Only the macOS keys are real artifacts. `golden_gate`, `tahoe`, `sequoia`, `sonoma`, and `ventura`
all resolve to the Intel DMG on Intel hosts and to the base artifact on Apple Silicon. The Linux keys
are placeholders with `null` checksums. There is no Windows artifact in this cask.

### Livecheck

```ruby
livecheck do
  url "https://antigravity-hub-auto-updater-974169037036.us-central1.run.app/" \
      "manifest/latest-#{livecheck_arch}-mac.yml?noCache=#{Time.now.to_i}"
  regex(%r{/v?(\d+(?:\.\d+)+)(?:-(\d+)?)/darwin-#{arch}/Antigravity\.(?:dmg|zip)}i)
  strategy :electron_builder do |yaml, regex|
    yaml["files"]&.map do |item|
      match = item["url"]&.match(regex)
      next if match.blank?

      match[2].present? ? "#{match[1]},#{match[2]}" : match[1]
    end
  end
end
```

| Property | Value |
| --- | --- |
| Manifest endpoint | `https://antigravity-hub-auto-updater-974169037036.us-central1.run.app/manifest/latest-<arch>-mac.yml` |
| `livecheck_arch` values | `arm64` (Apple Silicon), `x64` (Intel) |
| Strategy | `:electron_builder` (YAML manifest) |
| Extraction | Version and optional build from the `darwin-<arch>/Antigravity.dmg` URL, joined with a comma |
| Cache busting | `?noCache=<epoch seconds>` |

Livecheck asks the vendor's **auto-updater manifest**, not the product download page. That is
consistent with `auto_updates true` and means livecheck can see a release before the cask page
reflects it.

### Auto-update semantics

`auto_updates true` has two consequences:

1. **The app updates itself.** The Electron ShipIt updater uses
   `~/Library/Caches/com.google.antigravity.ShipIt` and
   `~/Library/Preferences/ByHost/com.google.antigravity.ShipIt.*.plist`.
2. **Homebrew treats the cask as self-managed.** A plain `brew upgrade` skips casks with
   `auto_updates true`. To force the tap's version, use:

   ```bash
   brew upgrade --cask --greedy-auto-updates antigravity
   ```

`--greedy` is broader: it also includes casks pinned to `version :latest`. `--greedy-auto-updates`
selects only `auto_updates true` casks, which is the precise flag for this cask.

Forcing the tap version is only safe when the tap version is at least as new as the app's self-updated
version. If the vendor has already updated beyond the tap, `--greedy-auto-updates` can replace a newer
app with an older one. Check both sides first:

```bash
mdls -name kMDItemVersion /Applications/Antigravity.app
brew info --cask antigravity | head -n 5
```

### Annotated cask source

The complete Ruby source at tap HEAD, reproduced for auditability:

```ruby
cask "antigravity" do
  arch arm: "arm", intel: "x64"
  livecheck_arch = on_arch_conditional arm: "arm64", intel: "x64"

  version "2.26.0,6546645232517120"
  sha256 arm:   "f9d707e367bc5f7c87627defa125dcffabc81b03b4844bc361da9e4821e89ad0",
         intel: "8865972294803ab8720e9562d4faf3742f075364c09b6087aa554f2740c45927"

  url "https://storage.googleapis.com/antigravity-public/antigravity-hub/#{version.csv.first}-#{version.csv.second}/darwin-#{arch}/Antigravity.dmg"
  name "Google Antigravity"
  desc "Agent orchestration platform"
  homepage "https://antigravity.google/product/antigravity-2"

  livecheck do
    url "https://antigravity-hub-auto-updater-974169037036.us-central1.run.app/manifest/latest-#{livecheck_arch}-mac.yml?noCache=#{Time.now.to_i}"
    regex(%r{/v?(\d+(?:\.\d+)+)(?:-(\d+)?)/darwin-#{arch}/Antigravity\.(?:dmg|zip)}i)
    strategy :electron_builder do |yaml, regex|
      yaml["files"]&.map do |item|
        match = item["url"]&.match(regex)
        next if match.blank?

        match[2].present? ? "#{match[1]},#{match[2]}" : match[1]
      end
    end
  end

  auto_updates true
  depends_on macos: :ventura

  app "Antigravity.app"

  uninstall quit: "com.google.antigravity"

  zap trash: [
    "~/.antigravity",
    "~/.gemini/antigravity",
    "~/Library/Application Support/Antigravity",
    "~/Library/Application Support/com.apple.sharedfilelist/com.apple.LSSharedFileList.ApplicationRecentDocuments/com.google.antigravity.sfl*",
    "~/Library/Caches/com.google.antigravity",
    "~/Library/Caches/com.google.antigravity.ShipIt",
    "~/Library/HTTPStorages/com.google.antigravity",
    "~/Library/Logs/Antigravity",
    "~/Library/Preferences/ByHost/com.google.antigravity.ShipIt.*.plist",
    "~/Library/Preferences/com.google.antigravity.plist",
    "~/Library/Saved Application State/com.google.Antigravity.savedState",
  ]
end
```

> The original file uses single long `url` and livecheck `url` lines. They are wrapped above for
> readability; behaviour is unchanged.

## Cask: `antigravity-ide`

### Identity

| JSON field | Value |
| --- | --- |
| `token` / `full_token` | `antigravity-ide` |
| `name` | Google Antigravity IDE |
| `desc` | AI Coding Agent IDE |
| `homepage` | `https://antigravity.google/product/antigravity-ide` |
| `tap` | `homebrew/cask` |
| `ruby_source_path` | `Casks/a/antigravity-ide.rb` |
| `ruby_source_checksum.sha256` | `4910ec2d8bf7b0fb48ba6b704238611cc05f20a523b3e4b4c94e111bc6a0a49f` |
| `version` | `2.6.0,5526304964083712` |
| `auto_updates` | `true` |
| `deprecated` / `disabled` | `false` / `false` |
| `caveats` | `null` |
| `conflicts_with` | `null` |

### Version encoding

```ruby
version "2.6.0,5526304964083712"
```

| Component | Value | Meaning |
| --- | --- | --- |
| `version.csv.first` | `2.6.0` | Human-facing semantic version |
| `version.csv.second` | `5526304964083712` | Build or revision identifier used in the download path |

The download directory is `2.6.0-5526304964083712`.

### Download URL construction

```ruby
arch arm: "arm", intel: "x64"

url "https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/" \
    "#{version.csv.first}-#{version.csv.second}/darwin-#{arch}/Antigravity%20IDE.dmg"
```

| Host platform | URL path | File |
| --- | --- | --- |
| macOS Apple Silicon | `darwin-arm/Antigravity%20IDE.dmg` | `Antigravity IDE.dmg` |
| macOS Intel | `darwin-x64/Antigravity%20IDE.dmg` | `Antigravity IDE.dmg` |

The space in the filename is percent-encoded as `%20`.

### SHA-256 matrix

Checksums for version `2.6.0,5526304964083712`:

| Platform | Cask key | SHA-256 |
| --- | --- | --- |
| macOS Apple Silicon | `arm` | `7971e71ffaec88f9d9480ea2bcc80aebaee59c0ac06df6f0141ef59046b49c9c` |
| macOS Intel | `intel` | `4e13a2073e666ac66b7e25e5a8943938f4bc0a17aea19ac1061dadfa80690e3b` |

The JSON API follows the same pattern as the App cask: top-level `url` and `sha256` are Apple Silicon;
`variations.<macos_version>` carries the Intel override. The Linux keys are placeholders with `null`
checksums and no Linux artifact.

### Artifacts

```ruby
app "Antigravity IDE.app"
binary "#{appdir}/Antigravity IDE.app/Contents/Resources/app/bin/antigravity-ide", target: "agy-ide"
binary "#{appdir}/Antigravity IDE.app/Contents/Resources/app/bin/antigravity-ide"

uninstall quit: "com.google.antigravity-ide"

zap trash: [
  "~/.antigravity-ide",
  "~/.antigravity-ide-server",
  "~/.gemini/antigravity-ide",
  "~/Library/Application Support/Antigravity IDE",
  "~/Library/Application Support/com.apple.sharedfilelist/com.apple.LSSharedFileList.ApplicationRecentDocuments/com.google.antigravity-ide.sfl*",
  "~/Library/Caches/com.google.antigravity-ide",
  "~/Library/Caches/com.google.antigravity-ide.ShipIt",
  "~/Library/HTTPStorages/com.google.antigravity-ide",
  "~/Library/Preferences/com.google.antigravity-ide.plist",
  "~/Library/Saved Application State/com.google.antigravity-ide.savedState",
]
```

| Artifact | Effect |
| --- | --- |
| `app "Antigravity IDE.app"` | Installs the app bundle to `/Applications/Antigravity IDE.app` |
| `binary ... target: "agy-ide"` | Symlinks the IDE's `antigravity-ide` executable to `$HOMEBREW_PREFIX/bin/agy-ide` |
| `binary ...` (second line) | Symlinks the same executable to `$HOMEBREW_PREFIX/bin/antigravity-ide` |
| `uninstall quit: "com.google.antigravity-ide"` | Quits the IDE before uninstalling |
| `zap trash: [...]` | On `brew uninstall --cask --zap`, moves the IDE-specific paths to the Trash |

Both binaries point at the same executable. The `agy-ide` name is the short convenience command; the
`antigravity-ide` name matches the product and the cask token.

### Platform support

`depends_on macos: :monterey` means macOS 12 Monterey is the minimum. The API reports
`depends_on.macos >= 12`.

The API's variation keys are:

```text
golden_gate, tahoe, sequoia, sonoma, ventura, monterey, x86_64_linux, arm64_linux
```

Only the macOS keys are real artifacts. The Linux keys are placeholders with `null` checksums. There
is no Windows artifact in this cask.

### Livecheck

```ruby
livecheck do
  url "https://antigravity-ide-auto-updater-974169037036.us-central1.run.app/" \
      "api/update/darwin#{livecheck_arch}/stable/latest"
  regex(%r{/stable/([^/]+)/}i)
  strategy :json do |json, regex|
    match = json["url"]&.match(regex)
    next if match.blank?

    match[1]&.tr("-", ",").to_s
  end
end
```

| Property | Value |
| --- | --- |
| Update endpoint | `https://antigravity-ide-auto-updater-974169037036.us-central1.run.app/api/update/darwin<arch>/stable/latest` |
| `livecheck_arch` values | `-arm64` (Apple Silicon), empty (Intel) |
| Strategy | `:json` |
| Extraction | First path segment after `/stable/`, with `-` converted to `,` |

On Apple Silicon the URL is `.../darwin-arm64/stable/latest`; on Intel it is
`.../darwin/stable/latest`. The cask achieves this with
`livecheck_arch = on_arch_conditional arm: "-arm64"`.

### Auto-update semantics

The IDE has the same `auto_updates true` contract as the App:

- The Electron ShipIt updater uses `~/Library/Caches/com.google.antigravity-ide.ShipIt`.
- A plain `brew upgrade` skips the cask.
- To force the tap's version:

  ```bash
  brew upgrade --cask --greedy-auto-updates antigravity-ide
  ```

Check both sides before forcing:

```bash
mdls -name kMDItemVersion "/Applications/Antigravity IDE.app"
brew info --cask antigravity-ide | head -n 5
```

### Annotated cask source

The complete Ruby source at tap HEAD:

```ruby
cask "antigravity-ide" do
  arch arm: "arm", intel: "x64"
  livecheck_arch = on_arch_conditional arm: "-arm64"

  version "2.6.0,5526304964083712"
  sha256 arm:   "7971e71ffaec88f9d9480ea2bcc80aebaee59c0ac06df6f0141ef59046b49c9c",
         intel: "4e13a2073e666ac66b7e25e5a8943938f4bc0a17aea19ac1061dadfa80690e3b"

  url "https://edgedl.me.gvt1.com/edgedl/release2/j0qc3/antigravity/stable/#{version.csv.first}-#{version.csv.second}/darwin-#{arch}/Antigravity%20IDE.dmg"
  name "Google Antigravity IDE"
  desc "AI Coding Agent IDE"
  homepage "https://antigravity.google/product/antigravity-ide"

  livecheck do
    url "https://antigravity-ide-auto-updater-974169037036.us-central1.run.app/api/update/darwin#{livecheck_arch}/stable/latest"
    regex(%r{/stable/([^/]+)/}i)
    strategy :json do |json, regex|
      match = json["url"]&.match(regex)
      next if match.blank?

      match[1]&.tr("-", ",").to_s
    end
  end

  auto_updates true
  depends_on macos: :monterey

  app "Antigravity IDE.app"
  binary "#{appdir}/Antigravity IDE.app/Contents/Resources/app/bin/antigravity-ide", target: "agy-ide"
  binary "#{appdir}/Antigravity IDE.app/Contents/Resources/app/bin/antigravity-ide"

  uninstall quit: "com.google.antigravity-ide"

  zap trash: [
    "~/.antigravity-ide",
    "~/.antigravity-ide-server",
    "~/.gemini/antigravity-ide",
    "~/Library/Application Support/Antigravity IDE",
    "~/Library/Application Support/com.apple.sharedfilelist/com.apple.LSSharedFileList.ApplicationRecentDocuments/com.google.antigravity-ide.sfl*",
    "~/Library/Caches/com.google.antigravity-ide",
    "~/Library/Caches/com.google.antigravity-ide.ShipIt",
    "~/Library/HTTPStorages/com.google.antigravity-ide",
    "~/Library/Preferences/com.google.antigravity-ide.plist",
    "~/Library/Saved Application State/com.google.antigravity-ide.savedState",
  ]
end
```

> The original file uses single long `url` and livecheck `url` lines. They are wrapped above for
> readability; behaviour is unchanged.

## Cross-cask comparison

| Dimension | `antigravity` | `antigravity-ide` |
| --- | --- | --- |
| Product role | Agent orchestration platform | AI coding IDE |
| Version scheme | `semver,build` CSV | `semver,build` CSV |
| Download host | `storage.googleapis.com` | `edgedl.me.gvt1.com` |
| App bundle | `Antigravity.app` | `Antigravity IDE.app` |
| Bundle identifier | `com.google.antigravity` | `com.google.antigravity-ide` |
| CLI binaries | none | `agy-ide`, `antigravity-ide` |
| Minimum macOS | 13 Ventura | 12 Monterey |
| Livecheck strategy | `:electron_builder` (YAML) | `:json` |
| Livecheck host | `antigravity-hub-auto-updater-...` | `antigravity-ide-auto-updater-...` |
| Update mechanism | Electron ShipIt | Electron ShipIt |
| Coexistence | No `conflicts_with` | No `conflicts_with` |

## API field reference

Fields most useful for automation:

| Field | Use |
| --- | --- |
| `version` | CSV version to compare against the installed app |
| `url` | Default (Apple Silicon) DMG |
| `sha256` | Default (Apple Silicon) checksum |
| `variations.<platform>` | Per-platform URL, checksum, and dependency overrides |
| `artifacts` | Machine-readable install, binary, uninstall, and zap actions |
| `depends_on.macos` | Minimum macOS |
| `auto_updates` | Whether plain `brew upgrade` skips the cask |
| `tap_git_head` | Exact tap commit the JSON was generated from |
| `analytics.install` | Install counts for 30, 90, and 365 days |

## Maintenance checklist when either version bumps

1. Re-read both cask sources; confirm the `version` CSV still has two components.
2. Confirm the `sha256` keys still exist (`arm`, `intel`).
3. Confirm the App still installs `Antigravity.app` with `uninstall quit: "com.google.antigravity"`.
4. Confirm the IDE still installs `Antigravity IDE.app` with `uninstall quit: "com.google.antigravity-ide"`.
5. Confirm the IDE's two `binary` targets are still `agy-ide` and `antigravity-ide`.
6. Confirm the `zap` paths have not moved; they are the best evidence of configuration locations.
7. Re-check both livecheck hosts, paths, and strategies; Google has changed service URLs before.
8. Update the version and checksums in this folder.
9. Re-run the verification commands below.

## Verification commands

```bash
# Both cask metadata as Homebrew sees it
brew info --cask antigravity
brew info --cask antigravity-ide

# Machine-readable cask JSON
curl -fsSL --connect-timeout 10 --max-time 30 \
  https://formulae.brew.sh/api/cask/antigravity.json | jq '.version, .sha256, .artifacts'
curl -fsSL --connect-timeout 10 --max-time 30 \
  https://formulae.brew.sh/api/cask/antigravity-ide.json | jq '.version, .sha256, .artifacts'

# Cask sources at the recorded tap HEAD
curl -fsSL --connect-timeout 10 --max-time 30 \
  https://raw.githubusercontent.com/Homebrew/homebrew-cask/896f63b6900bcf77a396b171525a221e1e379c9e/Casks/a/antigravity.rb
curl -fsSL --connect-timeout 10 --max-time 30 \
  https://raw.githubusercontent.com/Homebrew/homebrew-cask/896f63b6900bcf77a396b171525a221e1e379c9e/Casks/a/antigravity-ide.rb

# Installed apps and their bundle identifiers
mdls -name kMDItemCFBundleIdentifier /Applications/Antigravity.app
mdls -name kMDItemCFBundleIdentifier "/Applications/Antigravity IDE.app"

# Installed versions
mdls -name kMDItemVersion /Applications/Antigravity.app
mdls -name kMDItemVersion "/Applications/Antigravity IDE.app"

# IDE command-line shims
command -v agy-ide
command -v antigravity-ide
```

## Related

- [README.md](README.md) — overview and decision table
- [product-history.md](product-history.md) — how the split happened
- [installation-and-migration.md](installation-and-migration.md) — install, migrate, upgrade, remove
- [troubleshooting.md](troubleshooting.md) — version skew and bundle-ID collision
