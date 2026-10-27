# Google Antigravity App vs IDE — Homebrew Cask Explainer

> **Casks:** `antigravity` · `antigravity-ide` · **Tap:** `homebrew/cask` · **Verified:** 2026-10-27

Google ships two desktop products under the Antigravity name, and Homebrew ships one cask for each.
The names are easy to confuse because the cask called `antigravity` used to install the IDE. Since the
Antigravity 2.0 split in May 2026, `antigravity` installs the **agent orchestration platform** and
`antigravity-ide` installs the **AI coding IDE**.

This folder is an independent, source-cited explainer for both casks and the product split. It is not
Google documentation, and it is not affiliated with Google or Homebrew.

## TL;DR

| You want | Install | App bundle | CLI command |
| --- | --- | --- | --- |
| The Antigravity agent platform (Antigravity 2) | `brew install --cask antigravity` | `Antigravity.app` | none |
| The Antigravity IDE | `brew install --cask antigravity-ide` | `Antigravity IDE.app` | `agy-ide` or `antigravity-ide` |
| The terminal CLI | `brew install --cask antigravity-cli` | none | `agy` |

The two GUI casks can coexist. They use different app bundles, different bundle identifiers, and
different configuration directories after the split. The one exception is historical: the pre-split
IDE and the new App share `/Applications/Antigravity.app` and the bundle identifier
`com.google.antigravity`, so upgrading `antigravity` from 1.x to 2.x replaces the old IDE in place.

## The short version of the rename

| Period | `antigravity` cask installed | IDE available as |
| --- | --- | --- |
| 2025-11-18 to 2026-05-21 | Google Antigravity IDE (`Antigravity.app`) | `antigravity` |
| 2026-05-21 to 2026-05-22 (about 27 hours) | Google Antigravity 2 App | **no cask** |
| 2026-05-22 onward | Google Antigravity 2 App | `antigravity-ide` |

The 27-hour gap is why some users ran `brew upgrade` and found their IDE replaced by a different
application. The IDE was not removed deliberately; its new cask landed one day after the App cask.
See [product-history.md](product-history.md) for the full timeline and the exact maintainer record.

## Three things people get wrong

1. **`antigravity` no longer means the IDE.** Since the 2.0 split, `antigravity` is the agent
   orchestration platform. The IDE is `antigravity-ide`.
2. **The IDE's commands are `agy-ide` and `antigravity-ide`, not `agy`.** `agy` belongs to the
   separate `antigravity-cli` cask. The App cask installs no command-line binary at all.
3. **The apps can coexist, but the old IDE and the new App share an identity.** Both use
   `Antigravity.app` and `com.google.antigravity`. That is why the 1.x-to-2.x upgrade was an in-place
   replacement rather than a side-by-side install. The new IDE uses `Antigravity IDE.app` and
   `com.google.antigravity-ide`, so it can sit next to the App.

## Documentation map

| Document | Read it for |
| --- | --- |
| [product-history.md](product-history.md) | Timeline from the 2025 cask to the 2026 split, the 2.0 announcement, and the IDE-loss window |
| [cask-reference.md](cask-reference.md) | Every field of both casks: versions, URLs, SHA-256 matrix, artifacts, livecheck, annotated Ruby source |
| [installation-and-migration.md](installation-and-migration.md) | Install either or both, migrate from the pre-split cask, upgrade, pin, uninstall |
| [troubleshooting.md](troubleshooting.md) | Wrong app opens, missing commands, bundle-ID collision, Gatekeeper, version skew, livecheck |
| [maintainer-discussion.md](maintainer-discussion.md) | Exact PR/issue quotes, who said what, what the maintainers decided, what remains open |
| [sources.md](sources.md) | Every source, retrieval date, and the commands used to verify the cask facts |
| [AGENTS.md](AGENTS.md) | Folder ownership and maintenance contract for AI agents |

## At a glance

| Field | `antigravity` | `antigravity-ide` |
| --- | --- | --- |
| Full name | Google Antigravity | Google Antigravity IDE |
| Description | Agent orchestration platform | AI Coding Agent IDE |
| Homepage | <https://antigravity.google/product/antigravity-2> | <https://antigravity.google/product/antigravity-ide> |
| Version | `2.26.0,6546645232517120` | `2.6.0,5526304964083712` |
| Minimum macOS | 13 Ventura | 12 Monterey |
| App bundle | `Antigravity.app` | `Antigravity IDE.app` |
| Bundle identifier | `com.google.antigravity` | `com.google.antigravity-ide` |
| CLI binaries | none | `agy-ide`, `antigravity-ide` |
| Auto-updates | `true` (Electron ShipIt) | `true` (Electron ShipIt) |
| Analytics (30 / 90 / 365 days) | 4,323 / 9,509 / 62,707 | 1,344 / 3,691 / 9,191 |
| Cask source | [`Casks/a/antigravity.rb`](https://github.com/Homebrew/homebrew-cask/blob/896f63b6900bcf77a396b171525a221e1e379c9e/Casks/a/antigravity.rb) | [`Casks/a/antigravity-ide.rb`](https://github.com/Homebrew/homebrew-cask/blob/896f63b6900bcf77a396b171525a221e1e379c9e/Casks/a/antigravity-ide.rb) |

## What each app is for

**Google Antigravity (`antigravity`)** is the Antigravity 2 agent orchestration platform. Google's
description is "Agent orchestration platform"; the cask homepage is the `antigravity-2` product page.
It is the successor to the original Antigravity experience, not the IDE.

**Google Antigravity IDE (`antigravity-ide`)** is the AI coding IDE that Google kept available for
users who want the editor-centric workflow. Google's description is "AI Coding Agent IDE". The IDE
ships an Electron app plus two command-line shims that point at the same executable.

**Google Antigravity CLI (`antigravity-cli`)** is the terminal client, installed as `agy`. It is
documented separately in [the CLI guide](../antigravity-cli/README.md).

## Sources

The full source list, including every PR, issue, commit, API endpoint, and retrieval command, is in
[sources.md](sources.md). The primary sources are:

- Homebrew cask pages: <https://formulae.brew.sh/cask/antigravity> and
  <https://formulae.brew.sh/cask/antigravity-ide>
- Homebrew cask JSON APIs: <https://formulae.brew.sh/api/cask/antigravity.json> and
  <https://formulae.brew.sh/api/cask/antigravity-ide.json>
- The cask Ruby sources at tap HEAD `896f63b6900bcf77a396b171525a221e1e379c9e`
- The split PRs: [#265182](https://github.com/Homebrew/homebrew-cask/pull/265182),
  [#265183](https://github.com/Homebrew/homebrew-cask/pull/265183), and
  [#265184](https://github.com/Homebrew/homebrew-cask/pull/265184)
- The exact Q&A: [#265489](https://github.com/Homebrew/homebrew-cask/pull/265489)
- Google product pages: <https://antigravity.google/product/antigravity-2> and
  <https://antigravity.google/product/antigravity-ide>

## Verification status

| Claim type | Status |
| --- | --- |
| Cask metadata, URLs, checksums, artifacts, livecheck | Read from the cask JSON API and Ruby source on 2026-10-27 |
| Product identity, app bundles, bundle identifiers | Read from the cask Ruby source and Homebrew's uninstall/zap declarations on 2026-10-27 |
| PR/issue quotes and merge times | Read from the GitHub API on 2026-10-27 |
| Local runtime behaviour | **Not reproduced** — neither GUI cask was installed on the verification machine |
| Old 1.x cask identity | Read from the Homebrew cask Git history; see [product-history.md](product-history.md) |

Treat runtime examples as vendor- or cask-documented until you reproduce them on your own machine.
