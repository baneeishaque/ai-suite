<!-- title: Android Emulator AVD multiple instances research -->

# Android Emulator: Multiple Instances of the Same AVD

**Research date: 17 November 2026.** This is a beginner-friendly investigation of the Android Emulator
failure that occurs when a second emulator process is started for an AVD that is already running,
and of the supported way to run several instances of one AVD.

## The short answer

The Android Emulator serializes access to a single AVD. Starting a second process for the same AVD
fails with:

```text
FATAL | Running multiple emulators with the same AVD is an experimental feature.
Please use -read-only flag to enable this feature.
```

The supported opt-in is the emulator flag `-read-only`. Its built-in help text says:

```text
-read-only  allow running multiple instances of emulators on the same AVD, but cannot save snapshot.
```

So the goal is achievable, but only as an experimental/read-only mode: each extra instance must use
`-read-only`, and none of those instances can save a Quick Boot snapshot. Unique console/ADB ports
and separate GRPC tokens are still required in practice.

## What was investigated

- The failing local launch logs in
  [avd-launch-4 output](../../../../scratch/e92567a59ffeSe7EoyclPIhVA8/avd-launch-4_2026-11-17_08-57-51.out).
- The installed emulator's own CLI help (`emulator -help` and `emulator -help-all`).
- Community issues, prior implementations, wrappers, plugins, and maintainer responses found through
  GitHub code/issue search.
- The relevant session evidence in
  [the current session log directory](../../../../.opencode/logs/ses_e15a945d3ffewaq71F84Zo43kY).

## Start here

1. Read the [investigation report](investigation-report.md) for the observed failure, root cause,
   supported flag, and caveats.
2. Read [research sources](research-sources.md) for source links, search coverage, and unresolved
   questions.

## Documentation layout

```text
docs/research/android/avd-multiple-instances/
├── AGENTS.md
├── README.md
├── investigation-report.md
└── research-sources.md
```

## Evidence and version context

- Emulator version observed locally: `36.3.6.0` (build `14324226`).
- AVD name observed locally: `Android_API_36_ARM64_Phone_PlayStore_2`.
- System image observed locally:
  `/opt/homebrew/share/android-commandlinetools/system-images/android-36/google_apis_playstore/arm64-v8a/`.
- The AVD is commissioned for deletion, so it was not used for new experiments while writing this
  documentation; conclusions below come from captured logs and installed CLI help.

## Current repository context

- Repository HEAD at documentation time:
  `e868bb643c9742c53678691e73a05d3cca223922`
  ([local](.),
  [baneeishaque/ai-suite commit](https://github.com/baneeishaque/ai-suite/commit/e868bb643c9742c53678691e73a05d3cca223922),
  [baneeishaque/ai-suite-private commit](https://github.com/baneeishaque/ai-suite-private/commit/e868bb643c9742c53678691e73a05d3cca223922)).
- OpenCode session log directory for this session:
  [ses_e15a945d3ffewaq71F84Zo43kY](../../../../.opencode/logs/ses_e15a945d3ffewaq71F84Zo43kY).
