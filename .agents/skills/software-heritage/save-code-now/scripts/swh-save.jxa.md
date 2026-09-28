# `swh-save.jxa` + `swh-save-inject.js` — Explainer (Industrial Explainer Pattern 1.4)

## Architecture

| File | Role |
|---|---|
| `swh-save.jxa` | macOS driver: opens `/save/` in existing Chrome, waits for Anubis PoW, injects the worker, polls `window.__swhSaveResult` mailbox, prints JSON array. |
| `swh-save-inject.js` | Page worker: per origin, `POST /api/1/origin/save/git/url/<origin>/` with same-origin credentials, falls back to DOM form-fill + submit polling. Returns a JSON string (Chrome `tab.execute` cannot marshal promises). |
| `origins.txt` | Canonical origin manifest (one URL per line); read by default when no positional args or `--file` given. |

## Deep Technical Breakdown

| Logic | Rationale |
|---|---|
| JXA + existing Chrome instead of `curl`/Playwright | `archive.softwareheritage.org` enforces Anubis PoW that blocks headless HTTP. The user's Chrome holds the clearance cookie and any SWH login — driving it is the only reliable unattended path. Pattern mirrors `scripts/teams-chat-nav/teams-chat-nav.jxa` (sibling inject resolution, mailbox polling). |
| API-first, DOM-fallback inside the page | The Save form and `/api/1/origin/save/git/url/<origin>/` perform the same POST; calling the API from page context avoids brittle selectors, while the DOM fallback survives Save-page redesigns. `credentials: "same-origin"` carries the Anubis/SWH cookies. |
| `ORIGINS_PLACEHOLDER` → `JSON.stringify(origins)` substitution | JXA `execute` accepts one JS string; JSON embedding keeps arbitrary URLs safely quoted — same channel the Teams nav uses for the chat name. |
| `LOAD_WAIT_SECONDS = 12`, 30 × 2s poll | First visit must solve Anubis PoW + boot the app; the promise resolves async but `execute` returns synchronously, hence the mailbox. Timeout yields a JSON error (not a bare stack) so callers can distinguish "challenge still solving — rerun" from real failures. |
| `origins.txt` path resolved from `$0` (script location), not cwd | Per `ai-rule-standardization-rules` portable-script-path mandate: the script reads its own sibling file regardless of where it's invoked from. |

## Common Use Cases

- After a push to either repo: run the JXA, capture the JSON to `ai-session-exports/` as the visit/snapshot audit trail.
- `--file` for CI environments that list origins from a config store.

## Edge Cases

- Chrome not running → JXA auto-launches it (`browser-network-interception` `chrome-open` precedent).
- POST throttled (non-200) → surfaced per-origin in JSON with `http_status`; exit 1.
- Save page still showing Anubis spinner → mailbox timeout → JSON error; rerun after Chrome clears the challenge.

## Recommended Enhancements

- After `save_task_status == succeeded`, auto-chain into `swh-ingest-verify` for a close-the-loop single command.
- Retry loop on `PENDING`/`scheduled` statuses with exponential backoff.
