# android-feature-to-shared-kotlin-lib — Agent Companion

This is the passive-context companion for the
[`android-feature-to-shared-kotlin-lib`](SKILL.md) skill.

**When to invoke:**

- A feature exists in an Android app (Java or Kotlin) and needs to be
  consumed by a non-Android JVM client (Kotlin CLI, desktop, server).
- A Kotlin CLI has a `TODO` stub for behaviour that the Android app
  already implements.
- A multi-platform team wants to introduce a shared Kotlin/JVM library
  consumed by multiple clients (Android + CLI + future desktop / web).
- JitPack distribution is desired (no Maven Central setup yet).

**Refer all operational logic to [SKILL.md](SKILL.md).**

**Related skills:**

- [`git-atomic-commit-construction`](../git-atomic-commit-construction/SKILL.md)
  — atomic commit decomposition for the library + CLI split.
- [`git-submodule-commit-details`](../git-submodule-commit-details/SKILL.md)
  — parent-repo SHA-sync metadata extraction.
- [`dev-env-private-config-symlink`](../dev-env-private-config-symlink/SKILL.md)
  — runtime `.env` / JSON setup for the CLI consumer.
- [`redaction-portability`](../redaction-portability/SKILL.md)
  — path / identity redaction policy.
