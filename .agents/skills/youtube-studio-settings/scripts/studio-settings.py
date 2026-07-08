#!/usr/bin/env python3
"""
studio-settings.py — Apply YouTube Studio settings via layered browser
automation backends.

Auto-selects backend based on platform:
  macOS  → JXA first → undetected_chromedriver → stealth
  other  → undetected_chromedriver → stealth

Settings that are NOT available via the YouTube Data API v3 must be set
through YouTube Studio's web interface.

Usage:
  python3 studio-settings.py <VIDEO_ID> \\
      [--comments-off] [--age-restrict-18plus] \\
      [--no-subscriber-feed] [--no-remixing] \\
      [--caption-cert-not-aired-us] \\
      [--backend {auto,jxa,undetected,stealth}] [--dump]
"""
import argparse
import json
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def parse_args():
    p = argparse.ArgumentParser(
        description="Apply YouTube Studio settings via browser automation"
    )
    p.add_argument("video_id", help="YouTube video ID")
    p.add_argument("--comments-off", action="store_true", help="Disable comments")
    p.add_argument("--age-restrict-18plus", action="store_true", help="Set 18+ age restriction")
    p.add_argument("--no-subscriber-feed", action="store_true", help="Don't publish to subscriber feed")
    p.add_argument("--no-remixing", action="store_true", help="Don't allow remixing")
    p.add_argument("--caption-cert-not-aired-us", action="store_true", help="Set caption certification to never aired in US")
    p.add_argument("--backend", choices=["auto", "jxa", "undetected", "stealth"], default="auto", help="Backend to use")
    p.add_argument("--dump", action="store_true", help="Dump interactive elements and exit (for debugging)")
    return p.parse_args()


def build_settings(args):
    s = {
        "comments_off": args.comments_off,
        "age_restrict_18plus": args.age_restrict_18plus,
        "no_subscriber_feed": args.no_subscriber_feed,
        "no_remixing": args.no_remixing,
        "caption_cert_not_aired_us": args.caption_cert_not_aired_us,
        "dump_mode": args.dump,
    }
    # Remove False values for cleaner env
    return {k: v for k, v in s.items() if v}


def is_macos():
    return sys.platform == "darwin"


def run_jxa(video_id, settings):
    script = os.path.join(SCRIPT_DIR, "studio-settings--jxa.jxa")
    if not os.path.exists(script):
        return None, "JXA script not found"
    env = os.environ.copy()
    env["YT_VIDEO_ID"] = video_id
    env["YT_SETTINGS"] = json.dumps(settings)
    r = subprocess.run(
        ["osascript", "-l", "JavaScript", script],
        capture_output=True, text=True, timeout=120, env=env,
    )
    print(r.stdout, end="")
    if r.stderr:
        print(r.stderr, file=sys.stderr, end="")
    if r.returncode == 0:
        return True, None
    elif r.returncode == 1:
        return True, None  # partial failure, return OK but stderr has details
    else:
        return False, f"JXA exited with code {r.returncode}: {r.stderr}"


def run_undetected(video_id, settings):
    script = os.path.join(SCRIPT_DIR, "studio-settings--undetected.py")
    if not os.path.exists(script):
        return None, "undetected script not found"
    env = os.environ.copy()
    env["YT_VIDEO_ID"] = video_id
    env["YT_SETTINGS"] = json.dumps(settings)
    r = subprocess.run(
        [sys.executable, script],
        capture_output=True, text=True, timeout=180, env=env,
    )
    print(r.stdout, end="")
    if r.stderr:
        print(r.stderr, file=sys.stderr, end="")
    if r.returncode in (0, 1):
        return True, None
    return False, f"undetected exited with code {r.returncode}: {r.stderr}"


def run_stealth(video_id, settings):
    script = os.path.join(SCRIPT_DIR, "studio-settings--stealth.py")
    if not os.path.exists(script):
        return None, "stealth script not found"
    env = os.environ.copy()
    env["YT_VIDEO_ID"] = video_id
    env["YT_SETTINGS"] = json.dumps(settings)
    r = subprocess.run(
        [sys.executable, script],
        capture_output=True, text=True, timeout=180, env=env,
    )
    print(r.stdout, end="")
    if r.stderr:
        print(r.stderr, file=sys.stderr, end="")
    if r.returncode in (0, 1):
        return True, None
    return False, f"stealth exited with code {r.returncode}: {r.stderr}"


def main():
    args = parse_args()
    settings = build_settings(args)

    setting_flags = [v for k, v in settings.items() if k != "dump_mode"]
    if not any(v for v in setting_flags if v is True):
        print("ERROR: At least one setting flag is required", file=sys.stderr)
        sys.exit(1)

    backend = args.backend
    if backend == "auto":
        backend = "jxa" if is_macos() else "undetected"

    backends = {
        "jxa": ("JXA (macOS automation)", run_jxa),
        "undetected": ("undetected_chromedriver", run_undetected),
        "stealth": ("Playwright stealth", run_stealth),
    }

    # Determine which backends to try
    backend_order = []
    if backend == "jxa" and is_macos():
        backend_order = ["jxa", "undetected", "stealth"]
    elif backend == "undetected":
        backend_order = ["undetected", "stealth"]
    else:
        backend_order = [backend]

    last_error = None
    for name in backend_order:
        label, runner = backends[name]
        print(f"Trying backend: {label}...")
        success, error = runner(args.video_id, settings)
        if success is True:
            print(f"Backend {label} succeeded")
            return
        elif success is None:
            print(f"  Skipped: {error}")
            continue
        else:
            print(f"  Failed: {error}")
            last_error = error
            continue

    print("ERROR: All backends failed", file=sys.stderr)
    if last_error:
        print(f"Last error: {last_error}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
