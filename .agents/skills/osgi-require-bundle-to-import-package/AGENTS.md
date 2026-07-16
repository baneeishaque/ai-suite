# AGENTS.md — context bridge for `osgi-require-bundle-to-import-package`

Passive context only. The active protocol is in [SKILL.md](SKILL.md).

## What this skill is

A focused remediation skill for one specific OSGi failure shape:
a Tycho/PDE consumer's `Require-Bundle: <bsn>` no longer resolves
because the upstream packager renamed the bundle (typically
Eclipse Orbit `<java.package>` → Maven-Central
`<groupId>.<artifactId>`), even though the **package** the consumer
actually imports is unchanged and still exported by some bundle on
the resolved platform.

## When the orchestrator should invoke it

- Tycho/Maven error: `Missing requirement: ... requires 'osgi.bundle; <bsn> ...' but it could not be found`
- The consuming plugin's source code actually `import`s one or more packages from that bundle
- At least one bundle on the resolved target still exports those packages

## When NOT to invoke it

- The `Require-Bundle` entry is dead (no source uses it) → just delete it
- The IDE target is the only thing wrong and editing the consumer manifest is forbidden → use [`eclipse-pde-jdk-migration` §6](../eclipse-pde-jdk-migration/SKILL.md#6-orion-13-orbit-symbolic-name-mismatch-fixable-without-touching-manifestmf) (target-platform alias via PDE Maven `<location>` + bnd `<instructions>`) instead
- The consumer depends on `Bundle-ClassPath`-style resource propagation, `DynamicImport-Package` behaviour, or split-package participation that `Import-Package` cannot express

## Layering

Atomic — no sub-skills. Composes with neighbours in this repo only:

- [`eclipse-pde-jdk-migration`](../eclipse-pde-jdk-migration/SKILL.md) — opposite-direction sibling (target-side fix vs. consumer-side fix)
- [`maven-pom-audit`](../maven-pom-audit/SKILL.md) — adjacent build-config hygiene

This is a public, organization-neutral skill. It MUST NOT link to or name any private / organization-specific skill repository. Org-specific repos may cite this skill by name as an upstream remediation reference; the reverse direction is forbidden.

## Redaction posture

All examples sanitised per [redaction-portability](../redaction-portability/SKILL.md) Tier-A/B.
Apache project names and Eclipse Orbit identifiers are KEPT (public OSS).
Internal hostnames, internal Maven server IDs, and product code names are placeholdered (`<corp-…>`, `<consumer>`, `<provider-bsn>`).
