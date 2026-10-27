# Cask Reference — `antigravity-cli`

> **Cask HEAD:** `88bd762a0ccedc906b2956e52e5b85b7acf87cd2` ·
> **Version:** `1.4.8,5447777392656384` · **Read on:** 2026-10-27

This page documents the Homebrew cask itself: how its version is encoded, which artifact each platform
downloads, what the checksums are, how livecheck discovers releases, and what `brew` does on install,
upgrade, and uninstall.

## Identity

| JSON field | Value |
| --- | --- |
| `token` / `full_token` | `antigravity-cli` |
| `name` | Google Antigravity CLI |
| `desc` | Terminal interface for Antigravity agents |
| `homepage` | `https://antigravity.google/product/antigravity-cli` |
| `tap` | `homebrew/cask` |
| `ruby_source_path` | `Casks/a/antigravity-cli.rb` |
| `ruby_source_checksum.sha256` | `f424957bf3236976a2bff0dabcd367f5652e008f3be41474fe17b54d91fdef13` |
| `version` | `1.4.8,5447777392656384` |
| `auto_updates` | `true` |
| `deprecated` / `disabled` | `false` / `false` |
| `caveats` | `null` |
| `conflicts_with` | `null` |

## Version encoding

The cask uses a two-part CSV version:

```ruby
version "1.4.8,5447777392656384"
```

| Component | Value | Meaning |
| --- | --- | --- |
| `version.csv.first` | `1.4.8` | Human-facing semantic version |
| `version.csv.second` | `5447777392656384` | Build or revision identifier used in the download path |

The download URL joins the two with a hyphen, so the published directory is
`1.4.8-5447777392656384`. Livecheck performs the reverse transformation: it extracts the hyphenated
directory name and replaces `-` with `,` to produce the CSV version.

## Download URL construction

The Ruby source builds one URL template for every platform:

```ruby
arch arm: "arm", intel: "x64"
file_arch = on_arch_conditional arm: "arm64", intel: "x64"
livecheck_arch = on_arch_conditional arm: "arm64", intel: "amd64"
os macos: "darwin", linux: "linux"
file_os = on_system_conditional macos: "mac", linux: "linux"

url "https://storage.googleapis.com/antigravity-public/antigravity-cli/" \
    "#{version.csv.first}-#{version.csv.second}/#{os}-#{arch}/cli_#{file_os}_#{file_arch}.tar.gz"
```

That expands to four concrete artifacts:

| Host platform | URL path | Archive |
| --- | --- | --- |
| macOS Apple Silicon | `darwin-arm/cli_mac_arm64.tar.gz` | `cli_mac_arm64.tar.gz` |
| macOS Intel | `darwin-x64/cli_mac_x64.tar.gz` | `cli_mac_x64.tar.gz` |
| Linux x86-64 | `linux-x64/cli_linux_x64.tar.gz` | `cli_linux_x64.tar.gz` |
| Linux ARM64 | `linux-arm/cli_linux_arm64.tar.gz` | `cli_linux_arm64.tar.gz` |

Notice the deliberate asymmetry: the **directory** uses `arm` / `x64`, while the **filename** uses
`arm64` / `x64`. This is why the cask keeps two separate architecture variables (`arch` and `file_arch`).

## SHA-256 matrix

Checksums for version `1.4.8,5447777392656384`:

| Platform | Cask key | SHA-256 |
| --- | --- | --- |
| macOS Apple Silicon | `arm` | `ecd1f7b35927bc23ed4496139aeb0e39b99c4b1c63d5f1f3b8fc25ab515e7631` |
| macOS Intel | `intel` | `ce851c99afb9a21a8c0cadebb1b7155a951ffba76749081f0fd2c06b0a7b29c3` |
| Linux ARM64 | `arm64_linux` | `bbe34c56bdfdcfd9b9a4fd24f7430f7a807777b356b216b41862fb6dd9450c80` |
| Linux x86-64 | `x86_64_linux` | `8b165f0fc584f0f92dd1318dc3a090706ae18aade7d36b0b8623b85aeaf86c52` |

In the JSON API, the top-level `url` and `sha256` are the **Apple Silicon** artifact. The `variations`
object carries the Intel override: its macOS version keys (`monterey`, `ventura`, `sonoma`, `sequoia`,
`tahoe`, `golden_gate`, and `big_sur`) all point at the `darwin-x64` tarball. The `arm64_<version>` forms
are listed in `supported_platforms` but do not appear as separate variations; the base artifact already
covers them. The `big_sur` key appears in `variations`, but Big Sur is **not** in `supported_platforms` and
is excluded by `depends_on macos: :monterey`.

## Artifacts

```ruby
binary "antigravity", target: "agy"
zap trash: "~/.gemini/antigravity-cli"
```

| Artifact | Effect |
| --- | --- |
| `binary "antigravity", target: "agy"` | Symlinks the staged `antigravity` executable to `$HOMEBREW_PREFIX/bin/agy` |
| `zap trash: "~/.gemini/antigravity-cli"` | On `brew uninstall --cask --zap`, moves the CLI config directory to the Trash |

The rename is the single most important detail for users: **the installed command is `agy`**, even though
the downloaded executable and the upstream product are named Antigravity.

The `zap` stanza removes the config directory only. It does not remove the CLI's keyring entry; use the
in-CLI `/logout` command for that.

## Platform support

`depends_on macos: :monterey` inside an `on_macos` block means macOS 12 Monterey is the minimum. The API
reports `depends_on.macos >= 12`.

`supported_platforms` from the API:

```text
golden_gate, arm64_golden_gate, tahoe, arm64_tahoe, sequoia, arm64_sequoia,
sonoma, arm64_sonoma, ventura, arm64_ventura, monterey, arm64_monterey,
x86_64_linux, arm64_linux
```

There is no Windows artifact in this cask. Windows users must use Google's PowerShell or CMD installer.

## Livecheck

```ruby
livecheck do
  url "https://antigravity-cli-auto-updater-974169037036.us-central1.run.app/" \
      "manifests/#{os}_#{livecheck_arch}.json"
  regex(%r{/antigravity-cli/([^/]+)/}i)
  strategy :json do |json, regex|
    match = json["url"]&.match(regex)
    next if match.blank?

    match[1]&.tr("-", ",").to_s
  end
end
```

| Property | Value |
| --- | --- |
| Manifest endpoint | `https://antigravity-cli-auto-updater-974169037036.us-central1.run.app/manifests/<os>_<arch>.json` |
| `os` values | `darwin`, `linux` |
| `livecheck_arch` values | `arm64`, `amd64` |
| Extraction | First path segment after `/antigravity-cli/`, with `-` converted to `,` |

Livecheck therefore asks the vendor's **auto-updater manifest**, not the product download page. This is
consistent with `auto_updates true` and means livecheck can see a release before the cask page reflects it.

## Auto-update semantics

`auto_updates true` has two consequences:

1. **The vendor binary updates itself.** The CLI ships a native background updater with a 15-minute
   debounce marker (`last_check.timestamp`) and an advisory lock (`update.lock`) under
   `~/.gemini/antigravity-cli/updater/`.
2. **Homebrew treats the cask as self-managed.** A plain `brew upgrade` skips casks with
   `auto_updates true`. To force the tap's version, use:

   ```bash
   brew upgrade --cask --greedy-auto-updates antigravity-cli
   ```

   `--greedy` is broader: it also includes casks pinned to `version :latest`. `--greedy-auto-updates`
   selects only `auto_updates true` casks, which is the precise flag for this cask.

Forcing the tap version is only safe when the tap version is at least as new as the binary's self-updated
version. If the vendor has already updated beyond the tap, `--greedy` can replace a newer binary with an
older one. Check both sides first:

```bash
agy --version
brew info --cask antigravity-cli | head -n 5
```

A coherent policy is to pick one owner for updates:

| Policy | How | Trade-off |
| --- | --- | --- |
| Vendor-owned | Leave auto-update enabled; use Homebrew only to install and remove | Fastest fixes, but `brew` metadata can lag the binary |
| Homebrew-owned | `export AGY_CLI_DISABLE_AUTO_UPDATE=true`; update with `brew upgrade --cask --greedy-auto-updates antigravity-cli` | Predictable versioning, but you wait for the tap |

Do not run both policies at once and then assume either one is authoritative.

## Annotated cask source

The complete Ruby source at tap HEAD, reproduced for auditability:

```ruby
cask "antigravity-cli" do
  arch arm: "arm", intel: "x64"
  file_arch = on_arch_conditional arm: "arm64", intel: "x64"
  livecheck_arch = on_arch_conditional arm: "arm64", intel: "amd64"
  os macos: "darwin", linux: "linux"
  file_os = on_system_conditional macos: "mac", linux: "linux"

  version "1.4.8,5447777392656384"
  sha256 arm:          "ecd1f7b35927bc23ed4496139aeb0e39b99c4b1c63d5f1f3b8fc25ab515e7631",
         intel:        "ce851c99afb9a21a8c0cadebb1b7155a951ffba76749081f0fd2c06b0a7b29c3",
         arm64_linux:  "bbe34c56bdfdcfd9b9a4fd24f7430f7a807777b356b216b41862fb6dd9450c80",
         x86_64_linux: "8b165f0fc584f0f92dd1318dc3a090706ae18aade7d36b0b8623b85aeaf86c52"

  on_macos do
    depends_on macos: :monterey
  end

  url "https://storage.googleapis.com/antigravity-public/antigravity-cli/" \
      "#{version.csv.first}-#{version.csv.second}/#{os}-#{arch}/cli_#{file_os}_#{file_arch}.tar.gz"
  name "Google Antigravity CLI"
  desc "Terminal interface for Antigravity agents"
  homepage "https://antigravity.google/product/antigravity-cli"

  livecheck do
    url "https://antigravity-cli-auto-updater-974169037036.us-central1.run.app/" \
        "manifests/#{os}_#{livecheck_arch}.json"
    regex(%r{/antigravity-cli/([^/]+)/}i)
    strategy :json do |json, regex|
      match = json["url"]&.match(regex)
      next if match.blank?

      match[1]&.tr("-", ",").to_s
    end
  end

  auto_updates true

  binary "antigravity", target: "agy"

  zap trash: "~/.gemini/antigravity-cli"
end
```

> The original file uses a single long `url` line and a single long livecheck `url` line. They are wrapped
> above for readability; behaviour is unchanged.

## API field reference

Fields most useful for automation:

| Field | Use |
| --- | --- |
| `version` | CSV version to compare against `agy --version` |
| `url` | Default (Apple Silicon) tarball |
| `sha256` | Default (Apple Silicon) checksum |
| `variations.<platform>` | Per-platform URL, checksum, and dependency overrides |
| `artifacts` | Machine-readable install and zap actions |
| `depends_on.macos` | Minimum macOS |
| `auto_updates` | Whether plain `brew upgrade` skips the cask |
| `tap_git_head` | Exact tap commit the JSON was generated from |
| `analytics.install` | Install counts for 30, 90, and 365 days |

## Maintenance checklist when the version bumps

1. Re-read the cask source; confirm the `version` CSV still has two components.
2. Confirm all four `sha256` keys still exist (`arm`, `intel`, `arm64_linux`, `x86_64_linux`).
3. Confirm the `binary` target is still `agy`.
4. Confirm the `zap` path is still `~/.gemini/antigravity-cli`.
5. Re-check the livecheck manifest host and path; Google has changed service URLs before.
6. Update the version and checksums in this folder's tables.
7. Re-run the verification commands below.

## Verification commands

```bash
# Cask metadata as Homebrew sees it
brew info --cask antigravity-cli

# Machine-readable cask JSON
curl -fsSL --connect-timeout 10 --max-time 30 \
  https://formulae.brew.sh/api/cask/antigravity-cli.json | jq '.version, .sha256, .artifacts'

# Cask source at the recorded tap HEAD
curl -fsSL --connect-timeout 10 --max-time 30 \
  https://raw.githubusercontent.com/Homebrew/homebrew-cask/88bd762a0ccedc906b2956e52e5b85b7acf87cd2/Casks/a/antigravity-cli.rb

# Installed binary and version
command -v agy
agy --version
```

## Related

- [README.md](README.md) — overview and gotchas
- [installation.md](installation.md) — install, upgrade, and removal procedures
- [troubleshooting.md](troubleshooting.md) — version skew and updater-lock recovery
