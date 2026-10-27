# Product History — From One Cask to Three

> **Scope:** `antigravity` 1.x, the Antigravity 2.0 split, and the 27-hour IDE gap · **Verified:** 2026-10-27

The current three-cask layout is the result of a product split, not a simple cask rename. The original
`antigravity` cask installed the IDE. Antigravity 2.0 introduced a separate agent platform, and
Homebrew followed with a separate IDE cask one day later. This page records the sequence and the
evidence for each step.

## Timeline

| Date (UTC) | Event | Evidence |
| --- | --- | --- |
| 2025-11-18 | Original `antigravity` cask added. It installed the IDE as `Antigravity.app`, bundle `com.google.antigravity`, with an `agy` binary shim and macOS 12 minimum. | PR [#237135](https://github.com/Homebrew/homebrew-cask/pull/237135) |
| During the 1.x era | Cask path moved from `Casks/g/google-antigravity.rb` to `Casks/a/antigravity.rb`. | Commit `3f7175924f`; review by `bevanjkay` |
| 2026-04-16 | Last pre-split release: `1.23.2`. | Commit `72cab260f1` |
| 2026-05-19 | Google announces Antigravity 2.0. The announcement says "there is no IDE" and describes the new agent platform; it also says existing installs auto-update to 2.0 and asks users to keep the IDE. | Google's Antigravity 2.0 announcement; product page <https://antigravity.google/product/antigravity-2> |
| 2026-05-21 06:07 | `antigravity-cli` `1.0.0` merged. | PR [#265183](https://github.com/Homebrew/homebrew-cask/pull/265183) |
| 2026-05-21 06:11 | `antigravity` `2.0.1` merged. The token now points at the App. | PR [#265182](https://github.com/Homebrew/homebrew-cask/pull/265182) |
| 2026-05-21 to 2026-05-22 | **IDE gap:** `antigravity` is the App, and no `antigravity-ide` cask exists yet. Users who upgrade lose the IDE. | Absence of `antigravity-ide` before #265184 |
| 2026-05-22 05:58 | User `sramekmichal` reports the IDE loss on the IDE PR. | [#265184 comment](https://github.com/Homebrew/homebrew-cask/pull/265184#issuecomment-4515581344) |
| 2026-05-22 08:57 | `antigravity-ide` `2.0.2` merged. The IDE is available again under a new token. | PR [#265184](https://github.com/Homebrew/homebrew-cask/pull/265184) |
| 2026-05-22 10:28 | `singularitti` asks for a plain-language explanation of the three casks. | [#265489 comment](https://github.com/Homebrew/homebrew-cask/pull/265489#issuecomment-4517872767) |
| 2026-05-22 10:49 | `0xCAFEBABEx0` answers with the three-product mapping. | [#265489 comment](https://github.com/Homebrew/homebrew-cask/pull/265489#issuecomment-4518005201) |
| After the Q&A | PR #265489 closed as unnecessary; the answer is recorded in the comment, not merged. | PR [#265489](https://github.com/Homebrew/homebrew-cask/pull/265489) |
| After the split | `antigravity-ide` livecheck/outdated issue #280806 opened; fixed by PR #280831 (`2.5.5`). | Issue [#280806](https://github.com/Homebrew/homebrew-cask/issues/280806); PR [#280831](https://github.com/Homebrew/homebrew-cask/pull/280831) |
| 2026-10-27 | Current versions: `antigravity` `2.26.0`, `antigravity-ide` `2.6.0`. | Cask JSON APIs |

## The 1.x cask was the IDE

The original cask was added in November 2025 and described itself as the IDE:

| Field | 1.x value |
| --- | --- |
| `name` | Google Antigravity |
| `desc` | AI Coding Agent IDE |
| `homepage` | `https://antigravity.google/` |
| `app` | `Antigravity.app` |
| Bundle identifier | `com.google.antigravity` |
| CLI entry point | `agy` (shim) |
| Minimum macOS | 12 Monterey |

Its app bundle was `Antigravity.app`, its bundle identifier was `com.google.antigravity`, and it
exposed the IDE's command-line entry point as `agy`. That history explains two persistent
misunderstandings:

1. Users remember `agy` as the IDE command. After the split, `agy` is the separate CLI cask, and the
   IDE's commands are `agy-ide` and `antigravity-ide`.
2. Users remember `antigravity` as the IDE token. After the split, `antigravity` is the agent platform,
   and the IDE token is `antigravity-ide`.

The 1.x line ended at `1.23.2` on 2026-04-16. It is historical and is not what the current
`antigravity` token installs.

## What Antigravity 2.0 changed

Google's 2026-05-19 announcement introduced a new agent orchestration platform and drew a line between
it and the IDE. The announcement's phrase "there is no IDE" refers to the new Antigravity 2.0
experience, not to the removal of the IDE product. Google also kept the IDE available and told
existing users that their installs would auto-update to 2.0 while inviting them to keep the IDE.

Homebrew expressed that split as three tokens:

| Product | Cask token | App bundle | Bundle identifier | Minimum macOS |
| --- | --- | --- | --- | --- |
| Antigravity 2 agent platform | `antigravity` | `Antigravity.app` | `com.google.antigravity` | 13 Ventura |
| Antigravity IDE | `antigravity-ide` | `Antigravity IDE.app` | `com.google.antigravity-ide` | 12 Monterey |
| Antigravity CLI | `antigravity-cli` | none | none | 12 Monterey |

The critical inheritance is the first row. The new App took the old IDE's app name and bundle
identifier. The new IDE received a new app name and a new bundle identifier. That is why an upgrade of
the old `antigravity` token replaced the IDE in place, while the new IDE can be installed alongside
the App.

## Why the IDE disappeared for about 27 hours

The split was merged in two stages:

- `antigravity` 2.0.1 merged on 2026-05-21 at 06:11 UTC.
- `antigravity-ide` 2.0.2 merged on 2026-05-22 at 08:57 UTC.

The difference is about 26 hours and 46 minutes, commonly described as "about 27 hours". During that
window:

- `brew upgrade --cask antigravity` installed the 2.x App.
- No `antigravity-ide` token existed, so there was no direct way to reinstall the IDE from Homebrew.
- The old 1.x IDE and the new 2.x App shared the same app path and bundle identifier, so the upgrade
  replaced the IDE rather than adding a second app.

The IDE was not deleted from the product line. The cask for it simply landed one day after the cask
for the App. Once #265184 merged, `brew install --cask antigravity-ide` restored the IDE under a new
app bundle and a new token.

## Dock icon identification

The two apps are visually distinct once you know the convention:

| Product | Dock icon |
| --- | --- |
| Antigravity 2 App | White background |
| Antigravity IDE | Black grid |

If you see two Antigravity icons, you probably have both apps installed. If you see one icon and it
opens the wrong product, check the app bundle path with the commands in
[troubleshooting.md](troubleshooting.md#identify-which-app-you-have).

## What did not change

- Both GUI casks are Electron applications with `auto_updates true`; both use Google's updater
  infrastructure.
- Both are macOS-only in Homebrew. The JSON API exposes `x86_64_linux` and `arm64_linux` variation
  keys, but their checksums are `null` and there is no Linux artifact in either cask.
- Both are independent of the CLI cask. The CLI's command remains `agy`.
- Neither cask declares `conflicts_with`, so the two GUI apps can coexist after the split.

## Current state (2026-10-27)

| Field | `antigravity` | `antigravity-ide` |
| --- | --- | --- |
| Version | `2.26.0,6546645232517120` | `2.6.0,5526304964083712` |
| App path | `/Applications/Antigravity.app` | `/Applications/Antigravity IDE.app` |
| Bundle identifier | `com.google.antigravity` | `com.google.antigravity-ide` |
| Minimum macOS | 13 Ventura | 12 Monterey |
| Analytics (30 / 90 / 365 days) | 4,323 / 9,509 / 62,707 | 1,344 / 3,691 / 9,191 |

## Related

- [README.md](README.md) — overview and decision table
- [cask-reference.md](cask-reference.md) — field-by-field cask reference
- [installation-and-migration.md](installation-and-migration.md) — migration procedure
- [maintainer-discussion.md](maintainer-discussion.md) — exact PR and issue record
- [sources.md](sources.md) — full source list and verification commands
