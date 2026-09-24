#!/usr/bin/env python3
"""
studio-settings--undetected.py — Apply YouTube Studio settings via
undetected_chromedriver (Selenium). Cross-platform fallback when JXA is
unavailable.

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

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def get_env(key):
    v = os.environ.get(key)
    if not v:
        print(f"ERROR: {key} env var required", file=sys.stderr)
        sys.exit(2)
    return v


def find_by_text(driver, tag, text, timeout=8):
    """Find first visible element whose textContent contains text."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        els = driver.find_elements(By.TAG_NAME, tag)
        for e in els:
            if e.is_displayed() and text.lower() in (e.text or "").lower():
                return e
        time.sleep(0.3)
    return None


def find_by_text_all(driver, selector, text, timeout=8):
    """Find first visible element matching CSS selector whose text contains text."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        els = driver.find_elements(By.CSS_SELECTOR, selector)
        for e in els:
            if e.is_displayed() and text.lower() in (e.text or "").lower():
                return e
        time.sleep(0.3)
    return None


def click_text(driver, text, timeout=8):
    e = find_by_text_all(
        driver,
        "button,a,[role=button],[role=submit],ytcp-dropdown-trigger,tp-yt-paper-radio-button",
        text,
        timeout,
    )
    if e:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", e)
        e.click()
        return True
    return False


def select_dropdown(driver, trigger_text, option_text, timeout=10):
    e = find_by_text_all(driver, "ytcp-dropdown-trigger", trigger_text, timeout)
    if not e:
        return False
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", e)
    e.click()
    time.sleep(1)
    return click_text(driver, option_text, 5)


def checkbox_state(driver, label):
    els = driver.find_elements(By.CSS_SELECTOR, "[role=checkbox],ytcp-checkbox-lit")
    for e in els:
        if e.is_displayed() and label.lower() in ((e.get_attribute("aria-label") or "") + (e.text or "")).lower():
            ac = e.get_attribute("aria-checked")
            if ac == "true":
                return "checked"
            if ac == "false":
                return "unchecked"
            return "checked" if e.get_attribute("checked") else "unchecked"
    return None


def dump_interactive(driver):
    els = driver.find_elements(
        By.CSS_SELECTOR,
        "button,[role=button],[role=radio],[role=checkbox],"
        "select,[role=listbox],a,ytcp-dropdown-trigger,tp-yt-paper-menu-item",
    )
    lines = []
    for e in els:
        if not e.is_displayed():
            continue
        rect = e.size
        if rect["width"] == 0 and rect["height"] == 0:
            continue
        lines.append(
            "|".join([
                e.tag_name,
                e.get_attribute("id") or "",
                (e.text or "").strip()[:80],
                e.get_attribute("role") or e.get_attribute("type") or "",
                e.get_attribute("aria-checked") or str(e.get_attribute("checked") or ""),
                str(rect["width"] > 0 and rect["height"] > 0),
                (e.get_attribute("aria-label") or "")[:50],
            ])
        )
    return "\n".join(lines)


def main():
    video_id = get_env("YT_VIDEO_ID")
    settings = json.loads(get_env("YT_SETTINGS"))

    profile_dir = os.path.expanduser("~/.cache/studio-chrome-profile")
    os.makedirs(profile_dir, exist_ok=True)

    driver = uc.Chrome(
        user_data_dir=profile_dir,
        headless=False,
        version_main=132,
    )
    try:
        driver.get(f"https://studio.youtube.com/video/{video_id}/edit")
        wait = WebDriverWait(driver, 30)

        # Wait for Studio to load
        try:
            wait.until(lambda d: "studio" in d.title.lower())
        except TimeoutException:
            print("ERROR: Page did not load within 30s", file=sys.stderr)
            sys.exit(2)

        time.sleep(2)

        # Expand "Show more"
        show_more = find_by_text(driver, "button", "Show more", 5)
        if show_more:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", show_more)
            show_more.click()
            time.sleep(2)
        else:
            print("No 'Show more' found -- may already be expanded")

        # Dump mode
        if settings.get("dump_mode"):
            time.sleep(1)
            print(dump_interactive(driver))
            return

        changes = []
        errors = []

        # Comments off
        if settings.get("comments_off"):
            print("Disabling comments...")
            if select_dropdown(driver, "Comments", "Off"):
                changes.append("comments_off")
            else:
                errors.append("comments_off: could not select Off")
            time.sleep(0.5)

        # Age restriction 18+
        if settings.get("age_restrict_18plus"):
            print("Setting age restriction 18+...")
            btn = find_by_text(driver, "button", "Age restriction", 8)
            if btn:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
                btn.click()
                time.sleep(2)
                radio = find_by_text_all(driver, "tp-yt-paper-radio-button", "over 18", 5)
                if radio:
                    radio.click()
                    changes.append("age_restrict_18plus")
                else:
                    errors.append("age_restrict_18plus: 18+ radio not found")
            else:
                errors.append("age_restrict_18plus: button not found")
            time.sleep(0.5)

        # No subscriber feed
        if settings.get("no_subscriber_feed"):
            print("Disabling subscriber feed...")
            state = checkbox_state(driver, "notify subscribers")
            print(f"Subscriber feed state: {state}")
            if state == "checked":
                host = find_by_text_all(driver, "ytcp-checkbox-lit", "notify subscribers", 8)
                if host:
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", host)
                    host.click()
                    time.sleep(1.5)
                    new_state = checkbox_state(driver, "notify subscribers")
                    if new_state == "unchecked":
                        changes.append("no_subscriber_feed")
                    else:
                        errors.append("no_subscriber_feed: click did not toggle")
                else:
                    errors.append("no_subscriber_feed: element not found")
            elif state == "unchecked":
                changes.append("no_subscriber_feed (already)")
            else:
                errors.append(f"no_subscriber_feed: could not determine state ({state})")
            time.sleep(0.5)

        # Caption certification
        if settings.get("caption_cert_not_aired_us"):
            print("Setting caption certification (never aired)...")
            if (select_dropdown(driver, "Caption certification", "never aired")
                    or select_dropdown(driver, "Caption certification", "not aired")
                    or select_dropdown(driver, "Caption certification", "United States")):
                changes.append("caption_cert_not_aired_us")
            else:
                errors.append("caption_cert_not_aired_us: option not found")
            time.sleep(0.5)

        # No remixing
        if settings.get("no_remixing"):
            print("Disabling remixing...")
            try:
                radio = driver.find_element(By.CSS_SELECTOR, "#opt-out-radio-button")
                if radio.is_displayed():
                    radio.click()
                    changes.append("no_remixing")
                else:
                    raise ValueError("not visible")
            except (NoSuchElementException, ValueError):
                if (click_text(driver, "Don't allow remixing", 5)
                        or click_text(driver, "don't allow", 5)):
                    changes.append("no_remixing")
                else:
                    errors.append("no_remixing: element not found")
            time.sleep(0.5)

        # Save
        real_changes = [c for c in changes if "(already)" not in c]
        if real_changes:
            print("Clicking Save...")
            save_btn = find_by_text(driver, "button", "Save", 5)
            if save_btn:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", save_btn)
                save_btn.click()
                time.sleep(2.5)
                print("Save button clicked")
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
        driver.quit()


if __name__ == "__main__":
    main()
