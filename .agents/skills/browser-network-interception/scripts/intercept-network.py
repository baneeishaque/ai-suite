#!/usr/bin/env python3
"""
intercept-network.py — Open a URL in Chrome, intercept network responses,
output URLs matching patterns to stdout.

Supports two backends:
  - playwright: Launches Chrome via Playwright (default)
  - jxa: Opens URL in existing Chrome via JXA, attaches Playwright via CDP

Reads from args (see --help).
Exit: 0=match found, 1=no match, 2=error

Tier: 1 (Python 3.12+) per scripting-language-selection-rules §Tier 1
"""
import argparse
import os
import subprocess
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MACOS_APP_CONTROL = os.path.normpath(
    os.path.join(SCRIPT_DIR, "..", "..", "macos-app-control", "scripts", "macos-app-control.py")
)


def parse_args():
    p = argparse.ArgumentParser(
        description="Intercept network responses matching patterns"
    )
    p.add_argument("--url", required=True, help="URL to navigate to")
    p.add_argument(
        "--pattern", action="append", required=True,
        help="Substring to match in response URLs (repeatable)"
    )
    p.add_argument(
        "--profile", default="default",
        help="Chrome profile: 'default' or absolute path"
    )
    p.add_argument(
        "--timeout", type=int, default=30,
        help="Max seconds to wait for first match"
    )
    p.add_argument(
        "--wait-after", type=int, default=5,
        help="Seconds to wait after page load"
    )
    p.add_argument(
        "--headless", action="store_true",
        help="Run headless"
    )
    p.add_argument(
        "--backend", choices=["playwright", "jxa"], default="playwright",
        help="Backend: playwright (default) or jxa (macOS, opens existing Chrome)"
    )
    return p.parse_args()


def resolve_profile(profile_name):
    """Resolve Chrome profile path."""
    if profile_name == "default":
        return os.path.expanduser(
            "~/Library/Application Support/Google/Chrome/Default"
        )
    return os.path.expanduser(profile_name)


def run_with_playwright(args, profile_dir):
    """Playwright backend: launch Chrome via Playwright."""
    from playwright.sync_api import sync_playwright

    matched_urls = []

    def on_response(response):
        url = response.url
        for pattern in args.pattern:
            if pattern.lower() in url.lower():
                matched_urls.append(url)
                print(url, flush=True)
                break

    with sync_playwright() as pw:
        browser = pw.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=args.headless,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled"],
        )

        try:
            page = (
                browser.pages[0]
                if browser.pages
                else browser.new_page()
            )
            page.on("response", on_response)

            page.set_viewport_size({"width": 1440, "height": 900})

            print(f"Navigating to: {args.url}", file=sys.stderr)
            page.goto(args.url, wait_until="load", timeout=30000)
            page.wait_for_timeout(args.wait_after * 1000)

            deadline = time.time() + args.timeout
            while time.time() < deadline and not matched_urls:
                page.wait_for_timeout(1000)

            if not matched_urls:
                print("No matching URLs found", file=sys.stderr)
                sys.exit(1)

        finally:
            browser.close()


def run_with_jxa(args):
    """JXA backend: open URL in existing Chrome, attach via CDP."""
    from playwright.sync_api import sync_playwright

    if sys.platform != "darwin":
        print("ERROR: JXA backend requires macOS", file=sys.stderr)
        sys.exit(2)

    # Check if macos-app-control is available
    if not os.path.isfile(MACOS_APP_CONTROL):
        print(
            f"ERROR: macos-app-control not found: {MACOS_APP_CONTROL}",
            file=sys.stderr,
        )
        sys.exit(2)

    # Launch Chrome with remote debugging if not already running
    chrome_debug_port = 9222
    chrome_running = False
    try:
        result = subprocess.run(
            ["pgrep", "-f", "Google Chrome"],
            capture_output=True, timeout=5
        )
        chrome_running = result.returncode == 0
    except Exception:
        pass

    if chrome_running:
        # Check if remote debugging is available
        try:
            result = subprocess.run(
                ["lsof", "-i", f":{chrome_debug_port}"],
                capture_output=True, text=True, timeout=5
            )
            if result.stdout.strip():
                print(f"Chrome remote debugging available on port {chrome_debug_port}", file=sys.stderr)
            else:
                print("Chrome running without remote debugging", file=sys.stderr)
                print("Restarting Chrome with remote debugging...", file=sys.stderr)
                subprocess.run(["pkill", "-f", "Google Chrome"], capture_output=True, timeout=5)
                time.sleep(2)
                chrome_running = False
        except Exception:
            pass

    if not chrome_running:
        # Launch Chrome with remote debugging
        print(f"Launching Chrome with remote debugging on port {chrome_debug_port}...", file=sys.stderr)
        subprocess.Popen([
            "open", "-a", "Google Chrome",
            "--args", f"--remote-debugging-port={chrome_debug_port}"
        ])
        time.sleep(5)

    # Open URL in Chrome via JXA
    print(f"Opening URL via JXA: {args.url}", file=sys.stderr)
    result = subprocess.run(
        [sys.executable, MACOS_APP_CONTROL, "chrome-open", args.url],
        capture_output=True, text=True, timeout=15
    )
    if result.returncode != 0:
        print(f"JXA Chrome open failed: {result.stderr}", file=sys.stderr)
        sys.exit(2)

    time.sleep(args.wait_after)

    # Connect Playwright via CDP
    matched_urls = []

    def on_response(response):
        url = response.url
        for pattern in args.pattern:
            if pattern.lower() in url.lower():
                matched_urls.append(url)
                print(url, flush=True)
                break

    with sync_playwright() as pw:
        try:
            browser = pw.chromium.connect_over_cdp(
                f"http://localhost:{chrome_debug_port}"
            )
        except Exception as e:
            print(f"ERROR: Could not connect to Chrome via CDP: {e}", file=sys.stderr)
            sys.exit(2)

        try:
            # Get the page that was just opened
            contexts = browser.contexts
            if not contexts:
                print("ERROR: No browser contexts found", file=sys.stderr)
                sys.exit(2)

            pages = contexts[0].pages
            if not pages:
                print("ERROR: No pages found", file=sys.stderr)
                sys.exit(2)

            # Find the page with our URL
            page = None
            for p in pages:
                if args.url in p.url:
                    page = p
                    break
            if not page:
                page = pages[0]

            page.on("response", on_response)

            # Wait for matches or timeout
            deadline = time.time() + args.timeout
            while time.time() < deadline and not matched_urls:
                page.wait_for_timeout(1000)

            if not matched_urls:
                print("No matching URLs found", file=sys.stderr)
                sys.exit(1)

        finally:
            # Don't close the browser — it's the user's Chrome
            pass


def main():
    args = parse_args()
    profile_dir = resolve_profile(args.profile)

    if args.backend == "jxa":
        run_with_jxa(args)
    else:
        if not os.path.isdir(profile_dir):
            print(f"ERROR: Chrome profile not found: {profile_dir}", file=sys.stderr)
            sys.exit(2)
        run_with_playwright(args, profile_dir)


if __name__ == "__main__":
    main()
