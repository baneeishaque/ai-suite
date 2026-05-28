#!/usr/bin/env python3
"""
jitpack-config-bootstrap.py
===========================

Configures a Kotlin/JVM library Gradle module for JitPack publication:

* injects the ``maven-publish`` block into ``<module>/build.gradle.kts``
* creates ``jitpack.yml`` at the repo root pinning JDK and the publish task

Idempotent: re-running on an already-configured module is a no-op.

Usage
-----
    python3 jitpack-config-bootstrap.py \
        --module <path-to-module> \
        --group  com.github.<vcs-owner> \
        --version 1.0.0 \
        [--jdk openjdk21] [--repo-root .]

Exit codes
----------
0  success (whether or not anything was changed)
2  bad arguments / missing inputs

Tier
----
Tier-1 (Python) per ``scripting-language-selection-rules.md`` — file
templating, idempotency via substring search, no native-binary
orchestration. Ported from ``jitpack-config-bootstrap.bash`` per
``script-language-tier-port``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PUBLISH_BLOCK_TEMPLATE = """

// --- JitPack publishing (added by jitpack-config-bootstrap.py) ---
apply(plugin = "maven-publish")

group = "{group}"
version = "{version}"

java {{
    withSourcesJar()
}}

publishing {{
    publications {{
        create<MavenPublication>("mavenJava") {{
            from(components["java"])
        }}
    }}
}}
"""


JITPACK_TEMPLATE = """jdk:
  - {jdk}
install:
  - ./gradlew :{module_name}:publishToMavenLocal
"""


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Bootstrap JitPack publishing config for a Kotlin/JVM module.")
    ap.add_argument("--module", required=True)
    ap.add_argument("--group", required=True)
    ap.add_argument("--version", required=True)
    ap.add_argument("--jdk", default="openjdk21")
    ap.add_argument("--repo-root", default=".")
    args = ap.parse_args(argv)

    module = Path(args.module)
    build = module / "build.gradle.kts"
    if not build.is_file():
        print(f"Not found: {build}", file=sys.stderr)
        return 2

    if "maven-publish" in build.read_text():
        print(f"[skip] maven-publish already configured in {build}")
    else:
        block = PUBLISH_BLOCK_TEMPLATE.format(group=args.group, version=args.version)
        with build.open("a") as fh:
            fh.write(block)
        print(f"[done] appended maven-publish block to {build}")

    jitpack = Path(args.repo_root) / "jitpack.yml"
    module_name = module.name
    if jitpack.is_file():
        print(f"[skip] {jitpack} already exists; leaving alone")
    else:
        jitpack.write_text(JITPACK_TEMPLATE.format(jdk=args.jdk, module_name=module_name))
        print(f"[done] created {jitpack}")

    print()
    print("Next steps:")
    print(f"  1. Verify the build:  ./gradlew :{module_name}:publishToMavenLocal")
    print("  2. Tag the release in VCS so JitPack can resolve the version.")
    print(f"  3. Consumers depend on: {args.group}:<repo-name>:<tag>")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
