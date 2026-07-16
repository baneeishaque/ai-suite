#!/usr/bin/env python3
"""
studio-settings--stealth.py — Apply YouTube Studio settings via
Playwright + playwright-stealth. Last-resort fallback.

Reads YT_VIDEO_ID and YT_SETTINGS (JSON) from environment.
Settings dict keys:
  comments_off            bool
  age_restrict_18plus     bool
  no_subscriber_feed      bool
  no_remixing             bool
  caption_cert_not_aired_us  bool
  dump_mode               bool

Exit: 0 ok, 1 partial failure, 2 critical error
"""
import json
import os
import sys
import time

from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout


def get_env(key):
    v = os.environ.get(key)
    if not v:
        print(f"ERROR: {key} env var required", file=sys.stderr)
        sys.exit(2)
    return v


def page_eval(page, fn_body):
    return page.evaluate(f"(() => {{ {fn_body} }})()")


def find_by_text(page, selector, text, timeout=8):
    """Find visible element matching CSS selector whose text contains text."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        found = page_eval(
            page,
            f"""
            var t = {json.dumps(text)};
            var els = Array.from(document.querySelectorAll({json.dumps(selector)}));
            var m = els.find(function(e){{
                return e.offsetParent !== null &&
                    (e.textContent || '').toLowerCase().includes(t.toLowerCase());
            }});
            if (m) {{ m.scrollIntoView({{block:'center'}}); return true; }}
            return false;
            """,
        )
        if found:
            return True
        time.sleep(0.3)
    return False


def click_text(page, text, timeout=8):
    return find_by_text(
        page,
        "button,a,[role=button],[role=submit],ytcp-dropdown-trigger,tp-yt-paper-radio-button",
        text,
        timeout,
    )


def select_dropdown(page, trigger_text, option_text, timeout=10):
    deadline = time.time() + timeout
    while time.time() < deadline:
        clicked = page_eval(
            page,
            f"""
            var t = {json.dumps(trigger_text)};
            var els = Array.from(document.querySelectorAll('ytcp-dropdown-trigger'));
            var m = els.find(function(e){{
                return e.offsetParent !== null &&
                    (e.textContent || '').toLowerCase().includes(t.toLowerCase());
            }});
            if (m) {{ m.scrollIntoView({{block:'center'}}); m.click(); return true; }}
            return false;
            """,
        )
        if clicked:
            time.sleep(1)
            return find_by_text(
                page,
                "tp-yt-paper-item,[role=menuitem],[role=option]",
                option_text,
                5,
            )
        time.sleep(0.3)
    return False


def checkbox_state(page, label):
    return page_eval(
        page,
        f"""
        var label = {json.dumps(label)};
        var els = Array.from(document.querySelectorAll('[role=checkbox],ytcp-checkbox-lit'));
        var m = els.find(function(e){{
            return e.offsetParent !== null &&
                ((e.getAttribute('aria-label') || '') + (e.textContent || '')).toLowerCase().includes(label);
        }});
        if (!m) return 'not_found';
        var ac = m.getAttribute('aria-checked');
        if (ac === 'true') return 'checked';
        if (ac === 'false') return 'unchecked';
        if (m.checked) return 'checked';
        return 'unchecked';
        """,
    )


def dump_interactive(page):
    return page_eval(
        page,
        """
        var els = Array.from(document.querySelectorAll(
            'button,[role=button],[role=radio],[role=checkbox],' +
            'select,[role=listbox],a,ytcp-dropdown-trigger,tp-yt-paper-menu-item'
        ));
        return els.filter(function(e) {
            var r = e.getBoundingClientRect();
            return r.width > 0 && r.height > 0;
        }).map(function(e) {
            return [
                e.tagName,
                e.id || '',
                (e.textContent || '').trim().slice(0, 80),
                e.getAttribute('role') || e.type || '',
                e.getAttribute('aria-checked') || String(e.checked || ''),
                'true',
                (e.getAttribute('aria-label') || '').slice(0, 50),
            ].join('|');
        }).join('\\n');
        """,
    )


def main():
    video_id = get_env("YT_VIDEO_ID")
    settings = json.loads(get_env("YT_SETTINGS"))

    profile_dir = os.path.expanduser("~/.cache/studio-chrome-profile")
    os.makedirs(profile_dir, exist_ok=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=False,
            channel="chrome",
        )

        try:
            try:
                from playwright_stealth import stealth_sync
                page = browser.pages[0] if browser.pages else browser.new_page()
                stealth_sync(page)
            except ImportError:
                print("WARNING: playwright_stealth not installed, falling back to plain Playwright")
                page = browser.pages[0] if browser.pages else browser.new_page()

            page.set_viewport_size({"width": 1440, "height": 900})

            page.goto(
                f"https://studio.youtube.com/video/{video_id}/edit",
                wait_until="load",
                timeout=30000,
            )
            page.wait_for_timeout(2000)

            # Wait for Studio to load
            try:
                page.wait_for_function(
                    "document.title.toLowerCase().includes('studio')",
                    timeout=25000,
                )
            except PwTimeout:
                print("ERROR: Page did not load within 30s", file=sys.stderr)
                sys.exit(2)

            page.wait_for_timeout(1500)

            # Expand "Show more"
            page_eval(
                page,
                """
                window.scrollTo(0, document.body.scrollHeight);
                var els = Array.from(document.querySelectorAll(
                    'button,[role=submit],[role=button],a,span,div'
                ));
                var tx = els.find(function(e) {
                    var t = e.textContent.toLowerCase().replace(/\\s+/g, ' ').trim();
                    return t === 'show more' || t === 'show less';
                });
                if (tx) {
                    tx.scrollIntoView({behavior:'instant', block:'center'});
                    if (tx.textContent.replace(/\\s+/g, ' ').trim().toLowerCase() === 'show more') {
                        tx.click();
                        return 'show_more_clicked';
                    }
                    return 'show_less_found';
                }
                return 'not_found';
                """,
            )
            page.wait_for_timeout(2000)

            # Dump mode
            if settings.get("dump_mode"):
                page.wait_for_timeout(1000)
                print(dump_interactive(page))
                return

            changes = []
            errors = []

            # Comments off
            if settings.get("comments_off"):
                print("Disabling comments...")
                if select_dropdown(page, "Comments", "Off"):
                    changes.append("comments_off")
                else:
                    errors.append("comments_off: could not select Off")
                page.wait_for_timeout(500)

            # Age restriction 18+
            if settings.get("age_restrict_18plus"):
                print("Setting age restriction 18+...")
                age_clicked = page_eval(
                    page,
                    """
                    var e = Array.from(document.querySelectorAll('button')).find(
                        function(e) { return e.textContent.toLowerCase().includes('age restriction'); }
                    );
                    if (e) { e.scrollIntoView({behavior:'instant', block:'center'}); e.click(); return true; }
                    return false;
                    """,
                )
                page.wait_for_timeout(2000)
                if age_clicked:
                    radio_clicked = page_eval(
                        page,
                        """
                        var e = Array.from(document.querySelectorAll('tp-yt-paper-radio-button')).find(
                            function(e) { return e.textContent.toLowerCase().includes('over 18'); }
                        );
                        if (e) { e.scrollIntoView({behavior:'instant', block:'center'}); e.click(); return true; }
                        return false;
                        """,
                    )
                    if radio_clicked:
                        changes.append("age_restrict_18plus")
                    else:
                        errors.append("age_restrict_18plus: 18+ radio not found")
                else:
                    errors.append("age_restrict_18plus: button not found")
                page.wait_for_timeout(500)

            # No subscriber feed
            if settings.get("no_subscriber_feed"):
                print("Disabling subscriber feed...")
                state = checkbox_state(page, "notify subscribers")
                print(f"Subscriber feed state: {state}")
                if state in ("checked", True):
                    host_clicked = page_eval(
                        page,
                        f"""
                        var label = 'notify subscribers';
                        var host = Array.from(document.querySelectorAll('ytcp-checkbox-lit')).find(
                            function(e) {{
                                var txt = (e.textContent || '') + (e.getAttribute('aria-label') || '');
                                return e.offsetParent !== null && txt.toLowerCase().includes(label);
                            }}
                        );
                        if (host) {{ host.scrollIntoView({{behavior:'instant', block:'center'}}); host.click(); return true; }}
                        return false;
                        """,
                    )
                    page.wait_for_timeout(1500)
                    new_state = checkbox_state(page, "notify subscribers")
                    if new_state == "unchecked":
                        changes.append("no_subscriber_feed")
                    else:
                        errors.append("no_subscriber_feed: click did not toggle")
                elif state == "unchecked":
                    changes.append("no_subscriber_feed (already)")
                else:
                    errors.append(f"no_subscriber_feed: could not determine state ({state})")
                page.wait_for_timeout(500)

            # Caption certification
            if settings.get("caption_cert_not_aired_us"):
                print("Setting caption certification (never aired)...")
                if (select_dropdown(page, "Caption certification", "never aired")
                        or select_dropdown(page, "Caption certification", "not aired")
                        or select_dropdown(page, "Caption certification", "United States")):
                    changes.append("caption_cert_not_aired_us")
                else:
                    errors.append("caption_cert_not_aired_us: option not found")
                page.wait_for_timeout(500)

            # No remixing
            if settings.get("no_remixing"):
                print("Disabling remixing...")
                remix_clicked = page_eval(
                    page,
                    """
                    var e = document.querySelector('#opt-out-radio-button');
                    if (e && e.offsetParent !== null) { e.click(); return true; }
                    return false;
                    """,
                ) or click_text(page, "Don't allow remixing", 5) or click_text(page, "don't allow", 5)
                if remix_clicked:
                    changes.append("no_remixing")
                else:
                    errors.append("no_remixing: element not found")
                page.wait_for_timeout(500)

            # Save
            real_changes = [c for c in changes if "(already)" not in c]
            if real_changes:
                print("Clicking Save...")
                saved = page_eval(
                    page,
                    """
                    var els = Array.from(document.querySelectorAll('button')).filter(
                        function(e) { return e.offsetParent !== null; }
                    );
                    var m = els.find(function(e) { return e.textContent.trim().toLowerCase() === 'save'; });
                    if (m) { m.scrollIntoView({behavior:'instant', block:'center'}); m.click(); return true; }
                    return false;
                    """,
                )
                if saved:
                    page.wait_for_timeout(2500)
                    toast = page_eval(
                        page,
                        """
                        var e = document.querySelector('ytcp-toast-manager');
                        return e ? e.textContent.trim() : null;
                        """,
                    )
                    print(f"Save toast: {toast or '(not visible)'}")
                    changes.append("saved")
                else:
                    errors.append("save: Save button not found")
            else:
                print("No changes to save")

            print(f"Changes: {json.dumps(changes)}")
            if errors:
                print(f"Errors: {json.dumps(errors)}", file=sys.stderr)
                sys.exit(1)

        finally:
            browser.close()


if __name__ == "__main__":
    main()
