# Work-Log from Teams Meeting Export — Walkthrough v2

**Session:** `0c1d09aacffehMxzFP6YJNoAhC` (title: work-log-from-teams-meeting-export)
**Source:** merged session export `oleovista-acer-teams-chats/opencode-session-exports/session-ses_0c1d09aacffehMxzFP6YJNoAhC-merged.md` (8,472 lines)
**Tracker:** `ai-suite/session-tracker.yaml` session id `0c1d09aacffehMxzFP6YJNoAhC`, tasks L0T1–L0T12
**Date of workflow execution:** 2026-07-09 to 2026-07-10
**Input file:** `TeamsExport_Anjitha, Dileena, Muhammed, +3_2026-07-06_07-35-19.zip`

---

## Overview

This walkthrough documents the end-to-end pipeline performed in the session: from a raw Teams chat export ZIP file to organized per-meeting folders with HTML/JSON splits, enriched meeting notes cross-referenced with work logs, and structured formatted work-log entries. The pipeline is designed to be applied to any other Teams meeting export file.

Two Teams chat export generators were used for this chat:

| Generator | Output Format | Subfolder |
| :--- | :--- | :--- |
| **Teams Chat Exporter** (Chrome extension, teamschatexporter.com) | CSV + HTML + JSON + PDF + TXT | `teams-chat-exporter` |
| **Teams Message Extractor — Chat Export** | single TXT (flat messages) | `teams-message-extractor-chat-export` |

Pre-existing reusable scripts in the repo:

| Script | Path | Purpose |
| :--- | :--- | :--- |
| `convert-teams-json.py` | `oleovista-acers/scripts/work-log/convert-teams-json.py` | Convert Teams JSON export to structured `DD/MM/YYYY Day HH:MM:SS HH:MM:SS "Description"` work-log lines |
| `analyze_time.py` | `oleovista-acers/scripts/work-log/analyze_time.py` | Analyze structured work-log files — compute total hours, remaining hours per day |

---

## Phase 1: Symlink (L0T3)

**Prose:** Symlink the OneDrive Teams chat export folder into the repo.

**Steps:**

1. The source is `Banee Ishaque's OneDrive → Backups → oleovista-acer-teams-chats` containing the ZIP file.
2. Full OneDrive path on macOS: `/Users/dk/Library/CloudStorage/OneDrive-OMPVentureFZ-LLC/Backups/oleovista-acer-teams-chats/`
3. Create a symlink at `<repo-root>/oleovista-acer-teams-chats` pointing to the OneDrive folder.
   ```bash
   ln -s "/Users/dk/Library/CloudStorage/OneDrive-OMPVentureFZ-LLC/Backups/oleovista-acer-teams-chats" \
     /Users/dk/lab-data/oleovista-acers/oleovista-acer-teams-chats
   ```

**Note:** This was done before the session started. In subsequent sessions, files were added directly into git instead of relying on the symlink. If the files are already in git, skip this phase.

---

## Phase 2: Rename ZIP to Kebab-Case (L0T4)

**Prose:** Rename the raw export file from its generated name to lowercase kebab-case.

**Input:** `TeamsExport_Anjitha, Dileena, Muhammed, +3_2026-07-06_07-35-19.zip`

**Steps:**

1. Identify the ZIP file in `oleovista-acer-teams-chats/`.
2. Derive a kebab-case name:
   - Prefix: `teams-export`
   - Participants slug: `anjitha-dileena-muhammed-3` (the "+3" is compressed)
   - Export timestamp: `2026-07-06-07-35-19` (year-month-day-hour-minute-second, extracted from the original filename)
   - Extension: `.zip`
3. Rename:
   ```bash
   cd /Users/dk/lab-data/oleovista-acers/oleovista-acer-teams-chats
   mv "TeamsExport_Anjitha, Dileena, Muhammed, +3_2026-07-06_07-35-19.zip" \
     "teams-export-anjitha-dileena-muhammed-3-2026-07-06-07-35-19.zip"
   ```

**Result:** `teams-export-anjitha-dileena-muhammed-3-2026-07-06-07-35-19.zip`

---

## Phase 3: Organize — Extract and Structure (L0T5)

This is the largest organizational phase. It has 7 sub-tasks (L1T1–L1T7) in the tracker. The session executed these with significant refinements.

### ST1: Create Folder per Chat (L1T1)

**Steps:**

1. Derive a chat-level folder name from the participants and date range:
   - Participants slug: `anjitha-dileena-muhammed-3`
   - Meeting dates (discovered later): `2026-03-25`, `2026-05-07`, `2026-07-04`
   - Initial format: `<participants-slug>_<first-date>_<last-date>`
   - Initial name: `anjitha-dileena-muhammed-3_2026-03-25_2026-07-04`
2. Create the parent folder under `oleovista-acer-teams-chats/`:
   ```bash
   mkdir anjitha-dileena-muhammed-3_2026-03-25_2026-07-04
   ```

**Later refinement (session continuation):** The date range was dropped in favor of listing individual meeting days, because meetings don't span continuous ranges. Final name after all refinements:
   ```
   anjitha-dileena-muhammed-3_2026-03-25_2026-05-07_2026-07-04
   ```

### ST2: Move ZIP (L1T2)

**Steps:**

1. Move the renamed ZIP into the chat folder:
   ```bash
   mv teams-export-anjitha-dileena-muhammed-3-2026-07-06-07-35-19.zip \
     anjitha-dileena-muhammed-3_2026-03-25_2026-07-04/
   ```

### ST3: Unzip (L1T3)

**Steps:**

1. Unzip inside the chat folder:
   ```bash
   cd anjitha-dileena-muhammed-3_2026-03-25_2026-07-04
   unzip teams-export-anjitha-dileena-muhammed-3-2026-07-06-07-35-19.zip
   ```
2. The ZIP produces files named `<Chat>_2026-07-06_07-35-19.<ext>` — CSV, HTML, JSON, PDF, TXT — plus any embedded media/images.

### ST4: Rename Inner Files (L1T4)

**Goals:**
1. Rename extracted files to kebab-case.
2. Separate files into subfolders by generator.
3. Split HTML embeddings into a `media/` subfolder.

**Steps:**

1. Create subfolders for each export generator:
   ```
   teams-chat-exporter/
   teams-message-extractor-chat-export/
   ```
   (These represent the two generators used. Only `teams-chat-exporter` was used for this specific zip; the other folder is for the second generator's output.)

2. Rename the extracted files to generic names like `teams-export.csv`, `teams-export.html`, `teams-export.json`, `teams-export.pdf`, `teams-export.txt`.

3. Move files into `teams-chat-exporter/`.

4. Extract embedded base64 images from the HTML into a `media/` subfolder inside `teams-chat-exporter/`.

**Later refinement:** Files are renamed to simple `teams-export.<ext>`. The exporter generation timestamp (`2026-07-06_073519`) is encoded into the *parent subfolder name* instead:
   ```
   teams-chat-exporter_2026-07-06_073519/
   ```
   This keeps per-exporter provenance traceable without repeating the timestamp in every filename.

### ST5: Generate Per-Meeting Folders with HTML + JSON (L1T5)

**Prose:** Split the full-chat export into per-meeting subfolders. Each subfolder gets a copy of the meeting-specific HTML and JSON from the original export.

**Steps:**

1. Parse the JSON file (`teams-export.json`) to identify meeting boundaries.
   - Detect `"Meeting started"` and `"Meeting ended"` system messages from the `messageType` field.
   - Treat `"added <participant>"` messages as pre-meeting context.

2. For each meeting detected, create a subfolder named:
   ```
   meeting-<YYYY-MM-DD>_<IST-start-HHMM>_<IST-end-HHMM>-<topic>/
   ```
   inside `teams-chat-exporter/`.

3. Extract the messages for that meeting from the JSON and write a partial JSON file into the meeting subfolder.

**Timestamp computation rules:**

- All timestamps in the export are in **UTC** (e.g., `2026-03-25T07:18:11.973Z`).
- Convert to **IST** (+5:30) for folder naming.
- The meeting date used in the folder name is the **IST date** of the meeting start (this matters when meetings start before midnight UTC and span into the next IST day).
- Initial format: `HHMM` (hours+minutes). Later refined to `HHMMSS` (with seconds).

**Duration handling:**

- The Teams Chat Exporter places a `⏱ <duration>` label on the "Meeting ended" divider (e.g., `⏱ 10m`, `⏱ 20m 38s`, `⏱ 6h 2m 39s`).
- This label often **differs** from the actual `Meeting started → Meeting ended` timestamp span.
- Initial approach: use the label-based end time as the folder end time (it's always greater).
- **Final rule (ST7):** Folder end time = `max(meeting-ended-timestamp, start + duration-label)`.

### ST6: Split Original HTML at Meeting Boundaries (L1T6)

**IMPORTANT REFINEMENT:** The initial approach split meetings by generating partial HTML from JSON. This produced minimal HTML missing the rich content (embedded images, proper CSS, participant avatars, divider styling). The session then switched to **splitting the original HTML file** at meeting boundaries.

**Steps:**

1. Parse the full `teams-export.html` file structure.
2. Identify meeting boundary markers:
   - Opening: `<div class="divider-block">` with `Meeting started` header.
   - Closing: `<div class="divider-block">` with `Meeting ended` header.
3. For each meeting, extract the HTML segment between its start and end markers.
4. Wrap each extracted segment with the original `<html><head><style>...` preamble and closing `</body></html>` tags (copying the `<style>` block and `<script>` block from the original).
5. Write the resulting per-meeting HTML to `<meeting-folder>/teams-export.html`.
6. Also write a per-meeting JSON extracted from the full JSON to `<meeting-folder>/teams-export.json`.

**Key detail:** The HTML preamble includes embedded CSS styles and a `<script>` block for the compact-view toggle and image modal. These must be preserved in each per-meeting HTML for the file to render correctly standalone.

### ST7: Duration-Label vs Timestamp-Span Correction (L1T7)

**Prose:** Correct meeting folder end times to use the greater of the two possible end times.

**Steps:**

1. For each meeting, compute two end times:
   - **Timestamp-based:** `Meeting ended` UTC timestamp → IST.
   - **Label-based:** `Meeting started` UTC + `⏱ <duration>` label → IST.

2. Use `max(ts_based, label_based)` as the folder end time.

3. Document the discrepancy in a per-meeting `meeting-notes.yaml` file.

**Example discrepancies for the 3 meetings in this export:**

| Meeting | TS Span | Label Duration | Delta | Folder End Uses |
| :--- | :--- | :--- | :--- | :--- |
| Mar 25 intro | 1m 56s | 10m | +8m 04s | Label (10m) |
| May 7 sync | 17m 08s | 20m 38s | +3m 30s | Label (20m38s) |
| Jul 4 staging | 5h 56m 35s | 6h 2m 39s | +6m 04s | Label (6h2m39s) |

**Per-meeting `meeting-notes.yaml` template:**
```yaml
folder_name: meeting-<date>_<start-HHMMSS>_<end-HHMMSS>-<topic>

timestamps:
  meeting_started_utc: "<ISO-8601>"
  meeting_ended_utc: "<ISO-8601>"
  duration_label: "<⏱ value>"

duration_discrepancy:
  ts_based: "<H:MM:SS>"
  label_based: "<H:MM:SS>"
  delta: "<H:MM:SS>"
  note: >
    The "⏱ <duration>" label on "Meeting ended" is <delta> longer than the
    actual Meeting started → Meeting ended timestamp span. Folder end time
    uses the greater value (label-based).

participants:
  - <name1>
  - <name2>

messages: <count>
```

---

## Phase 4: Add Seconds to Folder Timestamps (Unmarked Continuation)

**Prose:** The user requested that folder timestamp portions use `HHMMSS` (with seconds) instead of `HHMM`.

**Steps:**

1. For each meeting, compute precise IST start and end times including seconds.
2. Rename folders to include seconds:
   ```
   HHMM → HHMMSS
   ```
3. Update all references — `meeting-notes.yaml` folder_name fields, `session-tracker.yaml` entries.

**Example:**
```
meeting-2026-03-25_1248_1258-intro
    → meeting-2026-03-25_124811_125811-intro
```
IST start: 07:18:11 UTC + 5:30 = 12:48:11 — seconds (11) now included.

---

## Phase 5: Meeting Naming from Work Logs (L0T6 + Continuation)

**Prose:** The initial meeting topics (e.g., "intro", "sync") were AI-generated assumptions. The user directed a systematic cross-reference against their existing rough work logs to derive accurate meeting names.

### 5A: Locate Work Logs

**Path:** `/Users/dk/lab-data/oleovista-acers/work-logs/`

**Available logs:**

| File | Format | Coverage |
| :--- | :--- | :--- |
| `mar2026-rough.txt` | Rough diary | March 2026 |
| `may2026-rough.txt` | Rough diary | May 2026 |
| `jun2026-rough.txt` | Rough diary | June 2026 |
| `apr2026-rough.txt` | Rough diary | April 2026 |
| `feb2026-rough.txt` | Combined (structured top + rough bottom) | February 2026 |
| `jan2026.txt` | Structured formatted | January 2026 |
| `jan2026.md` | Markdown table (generated from .txt) | January 2026 |
| `feb2026.txt` | Structured formatted | February 2026 |
| `dec2025.txt` | Structured formatted | December 2025 |
| `nov2025.txt` | Structured formatted | November 2025 |

**Two work-log formats coexist:**

1. **Rough logs** (`*rough.txt`): Freeform chronological diary. Each day starts with a date header, followed by numbered activity entries with times and descriptions. Format varies — some entries are detailed with exact times, others are compact lists.

2. **Structured formatted logs** (`<month><year>.txt`): One line per activity in the format:
   ```
   DD/MM/YYYY Day HH:MM:SS HH:MM:SS "Description"
   ```
   Examples from `feb2026.txt`:
   ```
   17/02/2026 Tuesday 16:50:28 17:16:41 "Teams Meeting (Aiswarya KJ): Call with Aiswarya and 2 others - Banee Ishaque K, Anushad PK, Aiswarya KJ"
   17/02/2026 Tuesday 17:24:02 18:28:33 "Teams Meeting (Banee Ishaque): Call with Aiswarya and 2 others - Banee Ishaque K, Anushad PK, Aiswarya KJ"
   ```

### 5B: Cross-Reference Each Meeting

For each meeting detected from the Teams chat export, search the corresponding rough work log for the date.

**Meeting 1 (Mar 25, 12:48–12:50 IST):**

- Match: `mar2026-rough.txt:138` — `"Jira start 12:25, praveena call discussion of ticket, calendar analysis, up to including shemeem evide call & it's return call 13:10"`
- The 2-min meeting falls within the 12:25–13:10 activity block.
- Participants match: Banee Ishaque K, PRAVEENA AK, Muhammed Shemeem.
- Post-meeting messages confirm the "shemeem evide call" reference.
- **Final name:** `jira-ticket-discussion-with-praveena`

**Meeting 2 (May 7, 12:17–12:38 IST):**

- Match: `may2026-rough.txt:28` — `"Praveena Call"` (appears twice in that day's entries).
- Participants: Banee, Shemeem, PRAVEENA. 0 chat messages (voice-only call).
- **Final name:** `praveena-call`

**Meeting 3 (Jul 4, 15:22–21:25 IST):**

- No existing rough log entry for July 4.
- Messages in the meeting: staging DB dump shared, API-optimization mention, `.env` files, `REACT_APP_BACKEND_URL` for staging, `NODE_OPTIONS` memory config, Python `API_Pending_Trades` reconciliation script.
- User provided context: the meeting was about setting up local backend & frontend testing environment for Praveena & Razik.
- AI reviewed the HTML content and identified 3 topic clusters: (1) local env setup, (2) staging DB, (3) API trade reconciliation script.
- **Final name** (user chose AI recommendation): `local-testing-env-setup-and-staging-data-reconciliation`

### 5C: Rename Folders and Update All Artifacts

**Steps for each meeting rename:**

1. Rename the meeting folder:
   ```bash
   mv meeting-<date>_<HHMMSS>_<HHMMSS>-<old-topic> \
       meeting-<date>_<HHMMSS>_<HHMMSS>-<new-topic>
   ```

2. Rewrite `meeting-notes.yaml` with:
   - Updated `folder_name`
   - `derived_from_work_log` field citing the rough log file+line and explaining the match
   - Full participant list (including those who joined after meeting start)
   - Post-meeting chat context (if any)
   - `key_topics` list (for meetings with messages)

3. Update `ai-suite/session-tracker.yaml`:
   - Replace folder name in the L1T7 `discrepancies` section
   - Add `work_log_ref` field citing the rough log source

**Final folder listing after Phase 5C:**
```
teams-chat-exporter_2026-07-06_073519/
  meeting-2026-03-25_124811_125811-jira-ticket-discussion-with-praveena/
    teams-export.html
    teams-export.json
    meeting-notes.yaml
  meeting-2026-05-07_121730_123808-praveena-call/
    teams-export.html
    teams-export.json
    meeting-notes.yaml
  meeting-2026-07-04_152232_212511-local-testing-env-setup-and-staging-data-reconciliation/
    teams-export.html
    teams-export.json
    meeting-notes.yaml
  teams-export.csv
  teams-export.html
  teams-export.json
  teams-export.pdf
  teams-export.txt
```

---

## Phase 6: Rename Remaining Shared Files (Unmarked Continuation)

**Prose:** Shorten the shared export files (CSV, HTML, JSON, PDF, TXT) to just `teams-export.<ext>` and encode the generation timestamp in the parent subfolder name.

**Steps:**

1. Rename the 5 shared files to bare `teams-export.<ext>`:
   ```bash
   cd teams-chat-exporter
   mv teams-export-anjitha-dileena-muhammed-3-2026-07-06-07-35-19.csv teams-export.csv
   mv teams-export-anjitha-dileena-muhammed-3-2026-07-06-07-35-19.html teams-export.html
   mv teams-export-anjitha-dileena-muhammed-3-2026-07-06-07-35-19.json teams-export.json
   mv teams-export-anjitha-dileena-muhammed-3-2026-07-06-07-35-19.pdf teams-export.pdf
   mv teams-export-anjitha-dileena-muhammed-3-2026-07-06-07-35-19.txt teams-export.txt
   ```

2. Rename the parent subfolder to include the generation timestamp:
   ```bash
   mv teams-chat-exporter teams-chat-exporter_2026-07-06_073519
   ```

---

## Phase 7: Rename Chat-Level Folder to Meeting Days (Unmarked Continuation)

**Prose:** Replace the date range in the chat-level folder name with individual meeting dates.

**Before:** `anjitha-dileena-muhammed-3_2026-03-25_2026-07-04` (range)
**After:** `anjitha-dileena-muhammed-3_2026-03-25_2026-05-07_2026-07-04` (3 discrete dates)

**Steps:**

```bash
mv anjitha-dileena-muhammed-3_2026-03-25_2026-07-04 \
    anjitha-dileena-muhammed-3_2026-03-25_2026-05-07_2026-07-04
```

---

## Phase 8: Work-Log Enrichment (Unmarked Continuation)

**Prose:** Add meeting information to both rough and structured work logs — the ultimate purpose of the pipeline.

### 8A: Update Rough Work Logs

For meetings where the rough log already has an entry for that date, enrich the existing entry with meeting-specific details. For meetings where no rough log exists, create one.

**Steps:**

1. **Mar 25** — Entry already exists at `mar2026-rough.txt:138`. Enrich with meeting details:
   ```
   Before:
   1. Jira start 12:25, praveena call discussion of ticket, calendar analysis,
      up to including shemeem evide call & it's return call 13:10

   After:
   1. Jira start 12:25, praveena call discussion of ticket (Teams meeting 12:48-12:58,
      10m label, participants: Banee, PRAVEENA AK, Muhammed Shemeem joined after),
      calendar analysis, up to including shemeem evide call & it's return call 13:10
   ```

2. **May 7** — Entry already exists at `may2026-rough.txt:28` as `"Praveena Call"`. Enrich similarly with timestamp, duration, and participants.

3. **Jul 4** — No `jul2026-rough.txt` exists. Create it:
   ```
   July 4 2026 Saturday
   ======================
   1. 15:22 to 21:25 Teams Meeting: Local Testing Env Setup & Staging Data
      Reconciliation with Anjitha, Dileena, Shemeem, Praveena & Razik —
      staging DB dump setup, .env config, API reconciliation script,
      local backend/frontend testing env for Praveena & Razik
   ```

### 8B: Create Structured Formatted Work Logs

Create or update structured `<month><year>.txt` files with one-line formatted entries.

**Format:** `DD/MM/YYYY Day HH:MM:SS HH:MM:SS "Description"`

**Steps:**

1. For months without a structured `.txt` file, create one:
   ```
   mar2026.txt, may2026.txt, jul2026.txt
   ```

2. For each meeting, compute the formatted entry:
   - Start/end times from `meeting-notes.yaml` (IST, HH:MM:SS, the greater-of-two end time).
   - Description follows the pattern: `"Teams Meeting: <topic> - <participant names>"`
   - Use exact participant names as they appear in the Teams export.

3. Write entries:

   **`mar2026.txt`:**
   ```
   25/03/2026 Wednesday 12:48:11 12:58:11 "Teams Meeting: Jira Ticket Discussion with Praveena - Banee Ishaque K, PRAVEENA AK, Muhammed Shemeem"
   ```

   **`may2026.txt`:**
   ```
   07/05/2026 Thursday 12:17:30 12:38:08 "Teams Meeting: Praveena Call - Banee Ishaque K, Muhammed Shemeem, PRAVEENA AK"
   ```

   **`jul2026.txt`:**
   ```
   04/07/2026 Saturday 15:22:32 21:25:11 "Teams Meeting: Local Testing Env Setup and Staging Data Reconciliation - Anjitha Sebastian, Banee Ishaque K, Dileena Beegum, Muhammed Shemeem, PRAVEENA AK, Razik Kamal"
   ```

### 8C: Verify with Existing Tools

The structured formatted log files can be consumed by the pre-existing scripts:

- `convert-teams-json.py` — reads Teams JSON export (via stdin), extracts call events (`Event/Call` with `callStarted`/`callEnded`), computes UTC→IST timestamps, and outputs formatted `DD/MM/YYYY Day HH:MM:SS HH:MM:SS "Description"` lines. This is an alternative path: feed the per-meeting JSON directly into this script to auto-generate entries.

- `analyze_time.py` — reads structured work-log `.txt` files, parses the `DD/MM/YYYY Day HH:MM:SS HH:MM:SS "Description"` format, computes durations, totals by day, and outputs a table with remaining-hours tracking.

---

## Phase 9: Followup Tasks (L0T7–L0T12 — In Session Tracker, Status Pending or Done)

These were defined in the tracker but not fully executed in this session. They are part of the broader workflow for a fully analyzed chat export.

| Task | Status | Description |
| :--- | :--- | :--- |
| L0T7 | pending | Decide followup actions based on analysis of a particular chat |
| L0T8 | pending | Execute followup actions |
| L0T9 | pending | Enrich meeting intelligence from recordings & transcripts (multi-source pipeline: Teams transcript → video download → audio transcription → cross-reference with chat) |
| L0T10 | pending | Execute followup actions of exchange trades optimization release (frontend branch + backend branch + database analysis + testing process formulation — extensive multi-level task tree) |
| L0T11 | done | Create a workflow for analyzing Microsoft Teams chat export files (the walkthrough you are reading) |
| L0T12 | pending | Document the workflow (referenced in `oleovista-acers/.vscode/bookmarks.json`) |

---

## Complete Pipeline Summary

The end-to-end workflow for a new Teams export file:

```
INPUT: <TeamsExport_...>.zip

1. SYMLINK (if not already in git)
   └─ ln -s <OneDrive-path> <repo>/oleovista-acer-teams-chats

2. RENAME ZIP TO KEBAB-CASE (L0T4)
   └─ teams-export-<participants-slug>-<export-timestamp>.zip

3. CREATE CHAT FOLDER (L0T5 ST1)
   └─ <participants-slug>_<meeting-date-1>_<meeting-date-2>_...

4. MOVE + UNZIP (L0T5 ST2–ST3)
   └─ unzip → CSV, HTML, JSON, PDF, TXT files

5. ORGANIZE BY GENERATOR (L0T5 ST4)
   ├─ teams-chat-exporter_<export-timestamp>/
   │   ├─ media/  (extracted HTML images)
   │   └─ teams-export.{csv,html,json,pdf,txt}
   └─ teams-message-extractor-chat-export/

6. DETECT MEETINGS FROM JSON (L0T5 ST5)
   └─ parse "Meeting started" / "Meeting ended" system messages

7. SPLIT HTML AT MEETING BOUNDARIES (L0T5 ST6)
   └─ extract per-meeting HTML segments with full preamble

8. COMPUTE TIMESTAMPS (L0T5 ST7 + continuation)
   ├─ UTC → IST (+5:30)
   ├─ end = max(meeting-ended-ts, start + duration-label)
   ├─ format: HHMMSS (with seconds)
   └─ document discrepancies in meeting-notes.yaml

9. NAME MEETINGS FROM WORK LOGS (L0T6 + continuation)
   ├─ search rough work log for matching date
   ├─ match participants + time window
   ├─ derive topic from work-log entry or meeting content
   └─ write meeting-notes.yaml with work_log_ref

10. RENAME SHARED FILES (continuation)
    └─ teams-export.<ext> inside timestamped generator folder

11. RENAME CHAT FOLDER TO DISCRETE DATES (continuation)
    └─ <slug>_<date1>_<date2>_<date3> (not range)

12. ENRICH WORK LOGS (continuation)
    ├─ rough logs: add meeting details to existing day entries
    ├─ rough logs: create new month file if missing (e.g. jul2026-rough.txt)
    └─ structured logs: create <month><year>.txt with formatted entries

OUTPUT:
    oleovista-acer-teams-chats/
      <participants-slug>_<date1>_<date2>_<date3>/
        teams-chat-exporter_<export-timestamp>/
          teams-export.{csv,html,json,pdf,txt}
          media/
          meeting-<YYYY-MM-DD>_<HHMMSS-IST-start>_<HHMMSS-IST-end>-<topic>/
            teams-export.html
            teams-export.json
            meeting-notes.yaml
        teams-message-extractor-chat-export/
      work-logs/
        <month><year>-rough.txt  (enriched)
        <month><year>.txt        (new structured entries)
```

---

## Key Decisions and Gotchas

1. **Timestamp source:** Export filenames contain export-generation timestamps, NOT meeting dates. Actual meeting dates come ONLY from JSON `timestamp` fields or HTML `datetime` attributes.

2. **UTC → IST conversion:** All meeting times are UTC in the export. Convert to IST (+5:30) for folder names and work-log entries. The folder date must be the IST date, not the UTC date.

3. **Duration-label discrepancy:** The `⏱` label on "Meeting ended" system divider differs from the actual `Meeting started → Meeting ended` timestamp span in every meeting. Always use `max(ts-span, label)`. Document the delta in `meeting-notes.yaml`.

4. **HTML splitting vs JSON generation:** Generating per-meeting HTML from JSON produces incomplete HTML (missing embedded images, CSS, participant avatars). Always split the ORIGINAL HTML at meeting boundary markers, preserving the `<style>` and `<script>` preamble blocks.

5. **Add-member messages:** System messages like `"X added Y"` that appear before `"Meeting started"` are pre-meeting context. They belong to the meeting folder (not a separate meeting).

6. **Meeting naming:** Never rely on AI-generated assumptions. Cross-reference with existing rough work logs. If no work-log entry exists, name based on actual message content, reviewed in the per-meeting HTML.

7. **Folder name format:** The chat-level folder should list discrete meeting dates, not a range. Timestamps include seconds (`HHMMSS`).

8. **Two work-log formats coexist:** Rough (`*rough.txt`) is freeform diary. Structured (`<month><year>.txt`) is one-line-per-entry with exact timestamps. Both must be updated.

9. **Existing tools:** `convert-teams-json.py` auto-generates structured entries from JSON. `analyze_time.py` computes totals from structured files. Use these as verification steps, not as the primary pipeline.

---

## File Tree After Execution

```
oleovista-acer-teams-chats/
  anjitha-dileena-muhammed-3_2026-03-25_2026-05-07_2026-07-04/
    teams-chat-exporter_2026-07-06_073519/
      teams-export.csv
      teams-export.html
      teams-export.json
      teams-export.pdf
      teams-export.txt
      media/
      meeting-2026-03-25_124811_125811-jira-ticket-discussion-with-praveena/
        teams-export.html
        teams-export.json
        meeting-notes.yaml
      meeting-2026-05-07_121730_123808-praveena-call/
        teams-export.html
        teams-export.json
        meeting-notes.yaml
      meeting-2026-07-04_152232_212511-local-testing-env-setup-and-staging-data-reconciliation/
        teams-export.html
        teams-export.json
        meeting-notes.yaml
    teams-message-extractor-chat-export/
  work-logs/
    feb2026-rough.txt
    feb2026.txt
    jan2026.txt
    jan2026.md
    mar2026-rough.txt         (enriched line 138)
    mar2026.txt               (created: 1 entry for Mar 25)
    apr2026-rough.txt
    may2026-rough.txt         (enriched line 28)
    may2026.txt               (created: 1 entry for May 7)
    jun2026-rough.txt
    jul2026-rough.txt         (created: 1 entry for Jul 4)
    jul2026.txt               (created: 1 entry for Jul 4)
    nov2025.txt
    dec2025.txt
```

---

Traceability: walkthrough derived from merged session `ses_0c1d09aacffehMxzFP6YJNoAhC` (8,472 lines), cross-referenced with `ai-suite/session-tracker.yaml` session `0c1d09aacffehMxzFP6YJNoAhC` (tasks L0T1–L0T12).
