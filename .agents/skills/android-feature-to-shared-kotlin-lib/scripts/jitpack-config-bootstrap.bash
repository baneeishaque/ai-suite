#!/usr/bin/env bash
# jitpack-config-bootstrap.bash
# Configures a Kotlin/JVM library Gradle module for JitPack publication:
#  - injects the maven-publish block into <module>/build.gradle.kts
#  - creates jitpack.yml at the repo root pinning JDK and the publish task
#
# Idempotent: re-running on an already-configured module is a no-op.
#
# Usage:
#   ./jitpack-config-bootstrap.bash --module <path-to-module> \
#                                 --group  com.github.<vcs-owner> \
#                                 --version 1.0.0 \
#                                 [--jdk openjdk21] [--repo-root .]

set -uo pipefail

MODULE=""
GROUP=""
VERSION=""
JDK="openjdk21"
REPO_ROOT="."

while [[ $# -gt 0 ]]; do
    case "$1" in
        --module)    MODULE="$2"; shift 2;;
        --group)     GROUP="$2"; shift 2;;
        --version)   VERSION="$2"; shift 2;;
        --jdk)       JDK="$2"; shift 2;;
        --repo-root) REPO_ROOT="$2"; shift 2;;
        -h|--help)   sed -n '2,15p' "$0"; exit 0;;
        *) echo "Unknown arg: $1" >&2; exit 2;;
    esac
done

if [[ -z "$MODULE" || -z "$GROUP" || -z "$VERSION" ]]; then
    echo "Usage: $0 --module <path> --group com.github.<owner> --version <v>" >&2
    exit 2
fi

BUILD="$MODULE/build.gradle.kts"
if [[ ! -f "$BUILD" ]]; then
    echo "Not found: $BUILD" >&2
    exit 2
fi

# Idempotency check: skip if maven-publish already present.
if grep -q "maven-publish" "$BUILD"; then
    echo "[skip] maven-publish already configured in $BUILD"
else
    # Append the publishing block to the end of the file.
    cat >> "$BUILD" <<EOF

// --- JitPack publishing (added by jitpack-config-bootstrap.bash) ---
apply(plugin = "maven-publish")

group = "$GROUP"
version = "$VERSION"

java {
    withSourcesJar()
}

publishing {
    publications {
        create<MavenPublication>("mavenJava") {
            from(components["java"])
        }
    }
}
EOF
    echo "[done] appended maven-publish block to $BUILD"
fi

JITPACK="$REPO_ROOT/jitpack.yml"
MODULE_NAME=$(basename "$MODULE")
if [[ -f "$JITPACK" ]]; then
    echo "[skip] $JITPACK already exists; leaving alone"
else
    cat > "$JITPACK" <<EOF
jdk:
  - $JDK
install:
  - ./gradlew :$MODULE_NAME:publishToMavenLocal
EOF
    echo "[done] created $JITPACK"
fi

echo
echo "Next steps:"
echo "  1. Verify the build:  ./gradlew :$MODULE_NAME:publishToMavenLocal"
echo "  2. Tag the release in VCS so JitPack can resolve the version."
echo "  3. Consumers depend on: $GROUP:<repo-name>:<tag>"
