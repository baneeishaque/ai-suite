#!/usr/bin/env python3
"""
teams-recording-download--setup.py — Verify dependencies for
Teams recording download skill.

Checks: python3, playwright, ffmpeg, base skills, Chrome profile.
Exit: 0=all OK, 1=missing dependencies

Tier: 1 (Python 3.12+) per scripting-language-selection-rules §Tier 1
"""
import os
import subprocess
import sys


def check(label, cmd=None, condition=None):
    """Run a check and print result."""
    if condition is not None:
        ok = condition
    elif cmd is not None:
        result = subprocess.run(
            cmd, capture_output=True, timeout=10
        )
        ok = result.returncode == 0
    else:
        ok = False

    if ok:
        print(f"[OK] {label}")
    else:
        print(f"[MISSING] {label}")
    return ok


def main():
    print("=== Teams Recording Download — Dependency Check ===")
    all_ok = True

    # Check Python
    all_ok &= check(
        "python3",
        cmd=[sys.executable, "--version"],
    )

    # Check playwright
    all_ok &= check(
        "playwright",
        cmd=[
            sys.executable, "-c", "import playwright"
        ],
    )

    # Check Google Chrome (required — we use channel="chrome", not Chromium)
    all_ok &= check(
        "Google Chrome",
        condition=os.path.isdir(
            "/Applications/Google Chrome.app"
        ),
    )

    # Check ffmpeg
    all_ok &= check(
        "ffmpeg",
        cmd=["ffmpeg", "-version"],
    )

    # Check base skills
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ai_suite_root = os.path.normpath(
        os.path.join(script_dir, "..", "..", "..", "..")
    )

    for skill in ["browser-network-interception", "video-download-manifest"]:
        scripts_dir = os.path.join(
            ai_suite_root, ".agents", "skills", skill, "scripts"
        )
        has_script = any(
            f.endswith(".py")
            for f in os.listdir(scripts_dir)
            if os.path.isfile(os.path.join(scripts_dir, f))
        ) if os.path.isdir(scripts_dir) else False

        all_ok &= check(
            f"{skill} base skill",
            condition=has_script,
        )

    # Check Chrome profile
    chrome_profile = os.path.expanduser(
        "~/Library/Application Support/Google/Chrome/Default"
    )
    check(
        f"Chrome profile: {chrome_profile}",
        condition=os.path.isdir(chrome_profile),
    )

    print()
    if all_ok:
        print("=== All dependencies OK ===")
    else:
        print("=== Some dependencies missing — install before running ===")
        sys.exit(1)


if __name__ == "__main__":
    main()
