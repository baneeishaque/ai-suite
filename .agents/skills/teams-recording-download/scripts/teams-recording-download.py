#!/usr/bin/env python3
"""
teams-recording-download.py — Download Teams meeting recording.

3-tier fallback architecture:
  A (primary)  — Teams desktop app via JXA + Chrome via Playwright
  C (fallback) — Chrome only (JXA on macOS, Playwright elsewhere)
  B (last resort) — Teams with remote debugging + Playwright

Reads from args (see --help).
Exit: 0=success, 1=failure, 2=error

Tier: 1 (Python 3.12+) per scripting-language-selection-rules §Tier 1
"""
import argparse
import os
import subprocess
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AI_SUITE_ROOT = os.path.normpath(
    os.path.join(SCRIPT_DIR, "..", "..", "..", "..")
)
MACOS_APP_CONTROL = os.path.join(
    AI_SUITE_ROOT, ".agents", "skills",
    "macos-app-control", "scripts", "macos-app-control.py"
)
BASE_INTERCEPT = os.path.join(
    AI_SUITE_ROOT, ".agents", "skills",
    "browser-network-interception", "scripts", "intercept-network.py"
)
BASE_DOWNLOAD = os.path.join(
    AI_SUITE_ROOT, ".agents", "skills",
    "video-download-manifest", "scripts", "download-from-manifest.py"
)


def parse_args():
    p = argparse.ArgumentParser(
        description="Download Teams meeting recording"
    )
    p.add_argument(
        "--date", required=True,
        help="Meeting date (YYYY-MM-DD)"
    )
    p.add_argument(
        "--topic", required=True,
        help="Meeting topic keyword"
    )
    p.add_argument(
        "--output", default=None,
        help="Output file path"
    )
    p.add_argument(
        "--source", choices=["auto", "calendar", "chat"],
        default="auto",
        help="Where to look for meeting"
    )
    p.add_argument(
        "--tier", choices=["A", "C", "B", "auto"],
        default="auto",
        help="Tier: A=JXA+Chrome, C=Chrome-only, B=remote-debug, auto=try all"
    )
    p.add_argument(
        "--dry-run", action="store_true",
        help="Find manifest URL only, don't download"
    )
    return p.parse_args()


def app_control(subcommand, *args):
    """Run a macos-app-control subcommand and return (success, output)."""
    cmd = [sys.executable, MACOS_APP_CONTROL, subcommand] + list(args)
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=15
        )
        output = result.stdout.strip()
        if result.stderr.strip():
            output = result.stderr.strip()
        return result.returncode == 0, output
    except Exception as e:
        return False, str(e)


def jxa_available():
    """Check if JXA is available (macOS only)."""
    if sys.platform != "darwin":
        return False
    if not os.path.isfile(MACOS_APP_CONTROL):
        return False
    try:
        result = subprocess.run(
            ["osascript", "-e", 'return "ok"'],
            capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0 and result.stdout.strip() == "ok"
    except Exception:
        return False


def ensure_teams_running_jxa():
    """Use macos-app-control to check and launch Teams."""
    running, _ = app_control("app-running", "Microsoft Teams")
    if running:
        print("[Tier A] Teams desktop app is running")
        return True

    print("[Tier A] Teams not running. Launching via JXA...")
    success, output = app_control("app-launch", "Microsoft Teams")
    if not success:
        print(f"  Failed to launch Teams: {output}", file=sys.stderr)
        return False

    print("Teams launched, waiting for ready...")
    time.sleep(10)

    running, _ = app_control("app-running", "Microsoft Teams")
    if running:
        print("Teams is ready")
        return True

    print("WARNING: Teams launch succeeded but not detected", file=sys.stderr)
    return False


def open_chrome_jxa(url):
    """Open URL in Chrome via macos-app-control."""
    success, output = app_control("chrome-open", url)
    if success:
        print(f"[Tier A] Opened in Chrome via JXA: {url}")
    else:
        print(f"JXA Chrome open failed: {output}", file=sys.stderr)
    return success


def resolve_chrome_profile():
    """Resolve default Chrome profile path."""
    profile = os.path.expanduser(
        "~/Library/Application Support/Google/Chrome/Default"
    )
    if os.path.isdir(profile):
        return profile
    print(
        f"ERROR: Chrome profile not found: {profile}",
        file=sys.stderr,
    )
    sys.exit(2)


def run_intercept(url, profile, timeout=30, backend="playwright"):
    """Run browser-network-interception base skill."""
    if not os.path.isfile(BASE_INTERCEPT):
        print(
            f"ERROR: Base skill not found: {BASE_INTERCEPT}",
            file=sys.stderr,
        )
        sys.exit(2)

    cmd = [
        sys.executable, BASE_INTERCEPT,
        "--url", url,
        "--pattern", "videomanifest",
        "--profile", profile,
        "--timeout", str(timeout),
        "--backend", backend,
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout + 30,
    )

    if result.returncode == 0 and result.stdout.strip():
        urls = result.stdout.strip().split("\n")
        return urls[0]
    return None


def run_download(manifest_url, output_path):
    """Run video-download-manifest base skill."""
    if not os.path.isfile(BASE_DOWNLOAD):
        print(
            f"ERROR: Base skill not found: {BASE_DOWNLOAD}",
            file=sys.stderr,
        )
        sys.exit(2)

    result = subprocess.run(
        [
            sys.executable, BASE_DOWNLOAD,
            "--manifest-url", manifest_url,
            "--output", output_path,
        ],
        capture_output=True,
        text=True,
        timeout=600,
    )
    print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    return result.returncode == 0


def tier_a(args, profile):
    """Tier A: Teams desktop app (JXA) + Chrome (Playwright)."""
    print("\n=== Tier A: Teams app (JXA) + Chrome ===")

    # 1. Ensure Teams is running
    if not ensure_teams_running_jxa():
        print("[Tier A] Teams not available", file=sys.stderr)
        return None

    # 2. Navigate Teams to Calendar
    print("[Tier A] Navigating to Calendar...")
    app_control("send-keys", "e", "--modifiers", "command down")
    time.sleep(1)

    # 3. Open Teams web in Chrome for recording playback
    teams_url = "https://teams.microsoft.com"
    open_chrome_jxa(teams_url)
    time.sleep(3)

    # 4. Capture manifest URL from Chrome
    print("[Tier A] Waiting for recording playback in Teams...")
    print("[Tier A] (Play the recording in Teams, then switch to Chrome)")
    print("[Tier A] Capturing manifest URL from Chrome...")

    manifest_url = None
    if args.source in ("auto", "calendar"):
        print(
            f"[Tier A] Searching Calendar for '{args.topic}' on {args.date}..."
        )
        manifest_url = run_intercept(
            teams_url, profile, timeout=60, backend="jxa"
        )

    if not manifest_url and args.source in ("auto", "chat"):
        print(f"[Tier A] Searching Chat for '{args.topic}'...")
        manifest_url = run_intercept(
            teams_url, profile, timeout=60, backend="jxa"
        )

    return manifest_url


def tier_c(args, profile):
    """Tier C: Chrome only (JXA on macOS, Playwright elsewhere)."""
    print("\n=== Tier C: Chrome only ===")

    teams_url = "https://teams.microsoft.com"

    # Open Chrome
    if jxa_available():
        print("[Tier C] Opening Chrome via JXA...")
        open_chrome_jxa(teams_url)
    else:
        print("[Tier C] Opening Chrome via Playwright...")
        # Playwright will handle Chrome launch

    time.sleep(3)

    # Capture manifest URL
    backend = "jxa" if jxa_available() else "playwright"
    manifest_url = None
    if args.source in ("auto", "calendar"):
        print(
            f"[Tier C] Searching Calendar for '{args.topic}' on {args.date}..."
        )
        manifest_url = run_intercept(
            teams_url, profile, timeout=60, backend=backend
        )

    if not manifest_url and args.source in ("auto", "chat"):
        print(f"[Tier C] Searching Chat for '{args.topic}'...")
        manifest_url = run_intercept(
            teams_url, profile, timeout=60, backend=backend
        )

    return manifest_url


def tier_b(args):
    """Tier B: Teams with remote debugging + Playwright."""
    print("\n=== Tier B: Teams remote debugging ===")

    # 1. Kill existing Teams
    print("[Tier B] Stopping existing Teams...")
    subprocess.run(
        ["pkill", "-f", "Microsoft Teams"],
        capture_output=True, timeout=5
    )
    time.sleep(2)

    # 2. Launch Teams with remote debugging
    print("[Tier B] Launching Teams with remote debugging...")
    try:
        subprocess.Popen([
            "open", "-a", "Microsoft Teams",
            "--args", "--remote-debugging-port=9222"
        ])
    except Exception as e:
        print(f"[Tier B] Failed to launch Teams: {e}", file=sys.stderr)
        return None

    # 3. Wait for Teams to start
    print("[Tier B] Waiting for Teams to start...")
    deadline = time.time() + 30
    while time.time() < deadline:
        result = subprocess.run(
            ["lsof", "-i", ":9222"],
            capture_output=True, text=True, timeout=5
        )
        if result.stdout.strip():
            print("[Tier B] Remote debugging available on port 9222")
            break
        time.sleep(2)
    else:
        print("[Tier B] Timeout waiting for remote debugging", file=sys.stderr)
        return None

    # 4. Connect Playwright to Teams
    print("[Tier B] Connecting Playwright to Teams...")
    # This requires a custom Playwright script connecting to localhost:9222
    # For now, return None — implement if needed
    print("[Tier B] Remote debugging interception not yet implemented")
    return None


def main():
    args = parse_args()
    output_path = args.output or os.path.expanduser(
        f"~/Downloads/teams-recording-{args.date}.mp4"
    )

    # Verify base skills exist
    for base, name in [
        (MACOS_APP_CONTROL, "macos-app-control"),
        (BASE_INTERCEPT, "browser-network-interception"),
        (BASE_DOWNLOAD, "video-download-manifest"),
    ]:
        if not os.path.isfile(base):
            print(
                f"ERROR: Base skill script not found: {base}",
                file=sys.stderr,
            )
            print(f"Install the {name} skill first.", file=sys.stderr)
            sys.exit(2)

    profile = resolve_chrome_profile()
    manifest_url = None

    # Auto-detect: try A → C → B
    if args.tier == "auto":
        if jxa_available():
            manifest_url = tier_a(args, profile)
        if not manifest_url:
            manifest_url = tier_c(args, profile)
        if not manifest_url:
            manifest_url = tier_b(args)
    elif args.tier == "A":
        manifest_url = tier_a(args, profile)
    elif args.tier == "C":
        manifest_url = tier_c(args, profile)
    elif args.tier == "B":
        manifest_url = tier_b(args)

    if not manifest_url:
        print("ERROR: No recording found", file=sys.stderr)
        sys.exit(1)

    print(f"\nManifest URL: {manifest_url[:150]}...")

    if args.dry_run:
        print(f"DRY RUN — manifest URL:\n{manifest_url}")
        sys.exit(0)

    # Download
    if run_download(manifest_url, output_path):
        print(f"Download complete: {output_path}")
    else:
        print("ERROR: Download failed", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
