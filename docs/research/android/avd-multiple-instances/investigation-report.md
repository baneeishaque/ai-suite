<!-- title: Android Emulator AVD multiple instances investigation report -->

# Investigation Report: Multiple Instances of One AVD

## 1. Observed failure

The local launch sequence attempted to start several emulator processes for the same AVD,
`Android_API_36_ARM64_Phone_PlayStore_2`. The first process booted successfully. Later attempts
stopped during compatibility checks with:

```text
FATAL | Running multiple emulators with the same AVD is an experimental feature.
Please use -read-only flag to enable this feature.
```

The captured failing log is
[avd-launch-4 output](../../../../scratch/e92567a59ffeSe7EoyclPIhVA8/avd-launch-4_2026-11-17_08-57-51.out).
The same message appears in
[avd-launch-3 output](../../../../scratch/e92567a59ffeSe7EoyclPIhVA8/avd-launch-3_2026-11-17_08-57-51.out).
The successful first process is visible in
[avd-launch output](../../../../scratch/e92567a59ffeSe7EoyclPIhVA8/avd-launch_2026-11-17_08-57-51.out)
and [avd-launch-2 output](../../../../scratch/e92567a59ffeSe7EoyclPIhVA8/avd-launch-2_2026-11-17_08-57-51.out).

## 2. What an AVD is

An Android Virtual Device (AVD) is a named emulator configuration plus its writable disk images.
The emulator creates a lock around the AVD so that two ordinary processes do not corrupt the same
`userdata`, `cache`, `encryptionkey`, or snapshot files. That is why the default behavior is
"one running emulator per AVD."

## 3. Root cause

The second and later processes tried to open the same AVD while the first process still held it.
The emulator treats same-AVD concurrency as experimental and refuses unless the caller explicitly
asks for read-only mode. This is not a disk-space, GPU, or RAM failure: the logs show all
compatibility checks (`hasSufficientDiskSpace`, `hasSufficientHwGpu`, `hasSufficientSystem`)
passing before the fatal message.

## 4. Supported solution: `-read-only`

The installed emulator's own help text defines the flag:

```text
-read-only  allow running multiple instances of emulators on the same AVD, but cannot save snapshot.
```

Therefore the working command shape is:

```text
emulator -avd <AVD_NAME> -read-only ...
```

Important consequences:

- The flag is experimental opt-in. It exists specifically for concurrent instances of one AVD.
- Read-only instances cannot save a snapshot, so Quick Boot save/restore behavior is disabled or
  degraded for those instances.
- The AVD's writable state is not shared safely for writes. Treat each read-only instance as a
  disposable view of the same base image.
- Unique ports are still needed. Use explicit console ports such as `-port 5554`, `-port 5556`,
  and matching ADB serials, or let the emulator allocate distinct ports.
- GRPC tokens, crash-data paths, and snapshot storage must not collide. In practice, running two
  instances with the same data directory can still create races even with `-read-only`.

## 5. Related emulator options that matter

From the installed help:

- `-wifi-mac-address <mac>` applies only when an AVD is loaded from a snapshot using read-only mode.
- `-no-snapshot`, `-no-snapshot-save`, and `-no-snapshot-load` can be used to force full boots and
  avoid snapshot races.
- `-port <port>` fixes the console port and makes ADB serial selection predictable.

## 6. Maintainer and community response

### 6.1 Flutter tooling

Flutter issue
[flutter/flutter#48894](https://github.com/flutter/flutter/issues/48894)
records the same crash:

```text
ERROR: Running multiple emulators with the same AVD is an experimental feature.
Please use -read-only flag to enable this feature.
```

The issue is closed. The comments do not contain a maintainer fix that changes emulator behavior;
they are user workarounds (delete old emulators, recreate the AVD). The issue author suggested
parsing the message and reporting a tool exit instead of crashing, but that is a client-side
robustness change, not an emulator change.

### 6.2 Google's emulator CLI

The authoritative behavior is documented by the emulator binary itself through `-help` and
`-help-all`. The help text is the maintainer-facing contract for this feature. No separate
published documentation page was found that explains multi-instance same-AVD mode in more detail.

### 6.3 Android Studio / IDE plugins

No maintainer response or plugin was found that transparently enables same-AVD multi-instance
mode. IDE launchers generally assume one instance per AVD. If an IDE starts a second instance,
it either fails with the same fatal message or requires manual `-read-only` arguments.

## 7. Prior implementations and workarounds found

| Project | What it does | Relevance |
| --- | --- | --- |
| [RoutineMiku/apkstart](https://github.com/RoutineMiku/apkstart) | Detects `Running multiple emulators with the same AVD`, stale `hardware-qemu.ini.lock`, and orphaned AVD locks; cleans them automatically. | Directly addresses the failure mode by removing stale locks rather than using `-read-only`. |
| [sambitcreate/aiden-agent](https://github.com/sambitcreate/aiden-agent) | Retries emulator startup while the AVD is still locked by an old instance; documents the 6-minute erase flow. | Shows production handling of AVD-lock contention. |
| [flexn-io/renative](https://github.com/flexn-io/renative) | Maps `Running multiple emulators with the same AVD` to `TARGET_EXISTS`. | Shows how build tools classify the error. |
| [DiemasMichiels/emulator](https://github.com/DiemasMichiels/emulator) | VS Code extension that detects the same error in emulator output. | Plugin-level awareness, not a fix. |
| [dodorare/android-tools-rs](https://github.com/dodorare/android-tools-rs) | Rust wrapper exposing `read_only()` and emitting `-read-only`. | Clean example of how to pass the flag programmatically. |
| [PiotrNap/bonfire-mobile-app](https://github.com/PiotrNap/bonfire-mobile-app) | Shell script launching two emulators with `-read-only` and explicit ports. | Practical multi-instance command pattern. |
| [KivMob CI script](https://github.com/MichaelStott/KivMob) | Health-checks logs for `multiple emulators with the same AVD` or `read-only flag to enable`. | CI guard pattern. |
| Chromium `tools/android/avd/avd.py` | Contains help text for `-read-only` in AVD helper wrappers. | Prior art in a large codebase. |
| [mattermost/mattermost-mobile](https://github.com/mattermost/mattermost-mobile) | Detox script comments explain why same-AVD launches fail. | Test-infrastructure awareness. |

## 8. Recommended approach

1. Prefer separate AVDs for normal development and testing. This avoids read-only limitations entirely.
2. If one AVD must be shared, launch the first instance normally and every additional instance with
   `-read-only`.
3. Give each instance a distinct console port and ADB serial.
4. Disable snapshot save/load for concurrent instances, or use `-no-snapshot-save` and
   `-no-snapshot-load`, to avoid snapshot races.
5. Treat read-only instances as ephemeral. Do not rely on them to persist installed apps or data.
6. Detect stale locks (`*.lock`, `hardware-qemu.ini.lock`) before retrying, as in `RoutineMiku/apkstart`.
7. In CI, fail fast with a clear message instead of crashing the whole toolchain.

## 9. Caveats and unresolved questions

- The official help text does not specify whether read-only instances share one writable overlay or
  each gets an isolated temporary overlay. That behavior should be verified before relying on
  persisted state.
- Performance, memory, and snapshot behavior of concurrent instances on Apple Silicon were not
  benchmarked here.
- No maintainer statement was found that promises long-term support for same-AVD multi-instance mode;
  it remains explicitly experimental.
- The commissioned-for-deletion AVD was not used for new experiments while writing this document.
