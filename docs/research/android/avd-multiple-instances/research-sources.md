<!-- title: Android Emulator AVD multiple instances research sources -->

# Research Sources: AVD Multiple Instances

**Research date: 17 November 2026.** This document lists primary sources, search coverage, and unresolved
questions for the investigation of running multiple Android Emulator instances on one AVD.

## Local evidence

| Source | Path | What it provides |
| --- | --- | --- |
| Failing launch log | [avd-launch-3 output](../../../../scratch/e92567a59ffeSe7EoyclPIhVA8/avd-launch-3_2026-11-17_08-57-51.out) | Second failed launch with the experimental-feature fatal. |
| Failing launch log | [avd-launch-4 output](../../../../scratch/e92567a59ffeSe7EoyclPIhVA8/avd-launch-4_2026-11-17_08-57-51.out) | Third failed launch with the experimental-feature fatal. |
| Successful launch log | [avd-launch output](../../../../scratch/e92567a59ffeSe7EoyclPIhVA8/avd-launch_2026-11-17_08-57-51.out) | First successful boot of the AVD. |
| Successful launch log | [avd-launch-2 output](../../../../scratch/e92567a59ffeSe7EoyclPIhVA8/avd-launch-2_2026-11-17_08-57-51.out) | Another successful boot of the AVD. |
| Emulator CLI help | Installed at `/opt/homebrew/share/android-commandlinetools/emulator/emulator` | Definition of `-read-only` and related snapshot/port options. |
| Session log directory | [ses_e15a945d3ffewaq71F84Zo43kY](../../../../.opencode/logs/ses_e15a945d3ffewaq71F84Zo43kY) | OpenCode session evidence for this investigation. |

## Official / maintainer evidence

| Source | URL | What it provides |
| --- | --- | --- |
| Android Emulator CLI help | Local `emulator -help` and `emulator -help-all` | `-read-only`: allow running multiple instances of emulators on the same AVD, but cannot save snapshot. |
| Flutter issue #48894 | [github.com/flutter/flutter/issues/48894](https://github.com/flutter/flutter/issues/48894) | Same fatal message; closed issue; user workarounds only. |

## Community implementations and wrappers

| Source | URL | What it provides |
| --- | --- | --- |
| RoutineMiku/apkstart | [github.com/RoutineMiku/apkstart](https://github.com/RoutineMiku/apkstart) | Lock detection and cleanup for same-AVD failures. |
| sambitcreate/aiden-agent | [github.com/sambitcreate/aiden-agent](https://github.com/sambitcreate/aiden-agent) | Retry and erase flow while an AVD is locked. |
| flexn-io/renative | [github.com/flexn-io/renative](https://github.com/flexn-io/renative) | Error classification as `TARGET_EXISTS`. |
| DiemasMichiels/emulator | [github.com/DiemasMichiels/emulator](https://github.com/DiemasMichiels/emulator) | VS Code plugin detection of the same error. |
| dodorare/android-tools-rs | [github.com/dodorare/android-tools-rs](https://github.com/dodorare/android-tools-rs) | Rust wrapper with `read_only()` support. |
| PiotrNap/bonfire-mobile-app | [github.com/PiotrNap/bonfire-mobile-app](https://github.com/PiotrNap/bonfire-mobile-app) | Shell script using `-read-only` and explicit ports. |
| MichaelStott/KivMob | [github.com/MichaelStott/KivMob](https://github.com/MichaelStott/KivMob) | CI health-check pattern for same-AVD failures. |
| Chromium AVD helper | [chromium/chromium tools/android/avd/avd.py](https://github.com/chromium/chromium/blob/main/tools/android/avd/avd.py) | Prior art containing `-read-only` help text. |
| mattermost/mattermost-mobile | [github.com/mattermost/mattermost-mobile](https://github.com/mattermost/mattermost-mobile) | Detox script comments about same-AVD launches. |

## Search queries performed

| Query | Tool | Purpose | Key finding |
| --- | --- | --- | --- |
| `gh search issues "Running multiple emulators with the same AVD is an experimental feature"` | GitHub CLI | Find maintainer/user responses | Found flutter/flutter#48894 and several tooling issues. |
| `gh search issues "Please use -read-only flag to enable this feature"` | GitHub CLI | Find all projects hitting the failure | Found CI, Flutter, Detox, and tooling references. |
| `gh search code "Running multiple emulators with the same AVD"` | GitHub CLI | Find implementations and error handling | Found lock cleanup, error classification, and CI guards. |
| `gh search code "multiple instances of emulators on the same AVD"` | GitHub CLI | Find wrappers exposing `-read-only` | Found Chromium AVD helper and language wrappers. |
| `gh search code "-read-only" "emulator -avd"` | GitHub CLI | Find concrete multi-instance command patterns | Found shell scripts and CI helpers. |
| `emulator -help` and `emulator -help-all` | Installed binary | Get authoritative flag definition | `-read-only` enables multiple instances but disables snapshot saving. |

## Extensions and plugins considered

| Name | Type | Relevance |
| --- | --- | --- |
| DiemasMichiels/emulator | VS Code extension | Detects the same-AVD failure in emulator output. |
| toroxx/vscode-avdmanager | VS Code extension | AVD management; no same-AVD multi-instance support found. |
| jenkinsci/android-emulator-plugin | Jenkins plugin | Android emulator provisioning; no same-AVD multi-instance support found. |

## Unresolved questions

1. Whether read-only instances use a shared temporary overlay or isolated overlays is not stated in the
   installed help text.
2. No maintainer statement was found that guarantees long-term support for same-AVD multi-instance mode.
3. The commissioned-for-deletion AVD was not used for new experiments, so concurrent-instance behavior
   was not re-measured locally.
4. Whether Android Studio can pass `-read-only` automatically for a second instance was not verified.

## Repository context

- Repository HEAD:
  `e868bb643c9742c53678691e73a05d3cca223922`
  ([local](.),
  [baneeishaque/ai-suite commit](https://github.com/baneeishaque/ai-suite/commit/e868bb643c9742c53678691e73a05d3cca223922),
  [baneeishaque/ai-suite-private commit](https://github.com/baneeishaque/ai-suite-private/commit/e868bb643c9742c53678691e73a05d3cca223922)).
