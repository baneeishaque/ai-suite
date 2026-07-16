# Teams Chat Export Processing Workflow

**Session**: `0c1d09aacffehMxzFP6YJNoAhC`
**Date**: 2026-07-10
**Chat**: `anjitha-dileena-muhammed-3_2026-03-25_2026-05-07_2026-07-04`

---

## Overview

This document describes the end-to-end pipeline for processing Microsoft Teams chat exports (from [teamschatexporter.com](https://teamschatexporter.com/)) into structured, per-meeting folders with rich metadata, linked to work logs.

---

## Directory Structure

```
oleovista-acer-teams-chats/
├── anjitha-dileena-muhammed-3_2026-03-25_2026-05-07_2026-07-04/
│   ├── teams-chat-exporter_2026-07-06_073519/
│   │   ├── teams-export.{json,html,csv,pdf,txt}
│   │   ├── meeting-2026-03-25_124811_125811-jira-ticket-discussion-with-praveena/
│   │   │   ├── teams-export.html
│   │   │   ├── teams-export.json
│   │   │   └── meeting-notes.yaml
│   │   ├── meeting-2026-05-07_121730_123808-praveena-call/
│   │   │   ├── teams-export.html
│   │   │   ├── teams-export.json
│   │   │   └── meeting-notes.yaml
│   │   └── meeting-2026-07-04_152232_212511-local-testing-env-setup-and-staging-data-reconciliation/
│   │       ├── teams-export.html
│   │       ├── teams-export.json
│   │       └── meeting-notes.yaml
│   └── teams-message-extractor-chat-export/
│       └── teams-messages-2026-07-06/
│           ├── teams-messages-2026-07-06.html
│           ├── image-*.jpg
│           └── url-preview-for-acers.png
└── opencode-session-exports/
    └── session-ses_0c1d09aacffehMxzFP6YJNoAhC-*.md
```

---

## Processing Steps

### Step 1: Symlink OneDrive Export Folder

```bash
# Source: OneDrive backup folder
ln -s "/Users/dk/Library/CloudStorage/OneDrive-OMPVentureFZ-LLC/Backups/oleovista-acer-teams-chats" \
      /Users/dk/lab-data/oleovista-acers/oleovista-acer-teams-chats
```

> Later superseded by committing files directly to git.

---

### Step 2: Rename Export ZIP to Kebab Case

```bash
# Original: TeamsExport_Anjitha, Dileena, Muhammed, +3_2026-07-06_07-35-19.zip
# Renamed: teams-export_anjitha-dileena-muhammed-3_2026-07-06_07-35-19.zip
```

---

### Step 3: Create Per-Chat Folder

```
oleovista-acer-teams-chats/anjitha-dileena-muhammed-3_2026-03-25_2026-05-07_2026-07-04/
```

Naming: `<participants>_<date-range>` (kebab-case, dates from export)

---

### Step 4: Move & Unzip Export

```bash
unzip teams-export_*.zip -d teams-chat-exporter_<export-timestamp>/
```

Extracted files: `teams-export.{json,html,csv,pdf,txt}`

---

### Step 5: Rename Extracted Files to Kebab Case

All files inside `teams-chat-exporter_*/` renamed to lowercase kebab-case.

---

### Step 6: Generate Per-Meeting Folders (from JSON)

Parse `teams-export.json` → extract individual meetings by `meeting_started`/`meeting_ended` boundaries.

```python
# Script: scripts/work-log/convert-teams-json.py
# Input: teams-export.json
# Output: meeting-<date>_<start>_<end>-<slug>/{teams-export.html, teams-export.json}
```

**Meeting folder naming**: `meeting-YYYY-MM-DD_HHMMSS_HHMMSS-<topic-slug>`

---

### Step 7: Split HTML at Meeting Boundaries

**Problem**: Teams Chat Exporter's HTML is a single file; meetings span the whole conversation.

**Solution**: Use JSON timestamps to split HTML at each meeting boundary, preserving rich content (attachments, formatting) that JSON lacks.

```python
# For each meeting in JSON:
#   1. Find start/end timestamps in HTML
#   2. Extract HTML segment
#   3. Write to meeting-*/teams-export.html
```

---

### Step 8: Update Meeting Folder End Times

**Rule**: Use the **greater** of:
- `meeting_ended` timestamp (from Teams)
- `meeting_started` + `duration_label` (the "⏱ Xh Ym Zs" label on "Meeting ended" divider)

**Rationale**: Label duration often exceeds timestamp span (includes pre-meeting wait, post-meeting wrap-up).

| Meeting | Timestamp Duration | Label Duration | Delta | Chosen |
|---------|-------------------|----------------|-------|--------|
| Mar 25  | 1m 56s            | 10m            | 8m 4s | label  |
| May 7   | 17m 8s            | 20m 38s        | 3m 30s| label  |
| Jul 4   | 5h 56m 35s        | 6h 2m 39s      | 6m 4s | label  |

Folder end time = `start + max(ts_duration, label_duration)`

---

### Step 9: Create `meeting-notes.yaml`

Per meeting, generate structured metadata:

```yaml
folder_name: meeting-2026-07-04_152232_212511-local-testing-env-setup-and-staging-data-reconciliation

description: |
  Setting up local backend & frontend testing environment for Praveena & Razik
  (staging DB dump + .env config) + API trade processing/reconciliation script
  shared by Dileena.

timestamps:
  meeting_started_utc: "2026-07-04T09:52:32.166Z"
  meeting_ended_utc: "2026-07-04T15:49:07.777Z"
  duration_label: "6h 2m 39s"

duration_discrepancy:
  ts_based: "5:56:35"
  label_based: "6:02:39"
  delta: "0:06:04"
  note: "Label is 6m 4s longer. Folder end time uses greater value (label-based)."

participants:
  - Anjitha Sebastian
  - Banee Ishaque K
  - Dileena Beegum
  - Muhammed Shemeem
  - PRAVEENA AK
  - Razik Kamal

messages: 12
key_topics:
  - description: "acers-staging-04-07-2026.dump"
    detail: "staging DB dump shared by Dileena"
  - description: "api-processing-optimized"
    detail: "backend branch"
  - description: ".env configuration"
    detail: "REACT_APP_BACKEND_URL for staging and local"
  - description: "Local testing environment setup"
    detail: "for Praveena and Razik"
  - description: "API_Pending_Trades reconciliation script"
    detail: "Dileena Python code"
  - description: "NODE_OPTIONS memory config"
    detail: "max-old-space-size"
```

---

### Step 10: Cross-Reference with Work Logs

Update rough log files (`mar2026-rough.txt`, `may2026-rough.txt`) with precise meeting timestamps extracted from `meeting-notes.yaml`.

Create formatted work log entries (`mar2026.txt`, `may2026.txt`, `jul2026.txt`):

```
DD/MM/YYYY Day HH:MM:SS HH:MM:SS "Title - Participants"
```

Example:
```
25/03/2026 Wednesday 12:48:11 12:58:11 "Jira Ticket Discussion with Praveena - Banee Ishaque K, PRAVEENA AK, Muhammed Shemeem"
```

---

### Step 11: Analyze Chat Exports

Review `teams-message-extractor-chat-export/` output for additional context (images, URL previews, message threading).

---

### Step 12: Enrich Meeting Intelligence (Pipeline T9)

**Sources**:
- OneDrive recordings (video)
- Teams-generated transcripts (from recording URLs)
- Audio transcription fallback (Malayalam + English mix)

**Steps**:
1. Fetch Teams transcript (if available)
2. Download recording URLs from Teams/OneDrive
3. Extract audio → transcribe (Whisper/Google Speech)
4. Cross-reference: chat log + Teams transcript + audio transcript
5. Produce enriched artifacts:
   - Meeting minutes
   - Action items (owner, deadline, status)
   - Task lists
   - Distilled agendas
   - Improved meeting names/descriptions

**Storage**: Per-meeting folder under chat directory.

---

### Step 13: Commit to Git (Atomic)

Each logical unit = one commit:

| Commit | Scope |
|--------|-------|
| `feat(work-log): add nov2025.txt...` | Legacy formatted entries |
| `feat(work-log): add mar2026-rough.txt...` | Rough logs (per month) |
| `feat(work-log): add mar2026.txt...` | Formatted entries (per meeting) |
| `feat(teams-chats): add chat exporter data...` | Full `teams-chat-exporter_*/` |
| `feat(teams-chats): add message extractor data...` | `teams-message-extractor-*/` |
| `feat(teams-chats): add opencode session exports...` | Session MD files |

**Maximum atomicity**: One file per commit for work-logs; one directory per commit for teams-chats.

---

## Key Artifacts

| File | Purpose |
|------|---------|
| `teams-export.json` | Source of truth for meeting boundaries, timestamps, participants |
| `teams-export.html` | Rich content (attachments, formatting, threads) |
| `meeting-notes.yaml` | Structured metadata per meeting |
| `*-rough.txt` | Daily rough notes (enriched with meeting times) |
| `*.txt` (formatted) | Structured time entries for reporting |
| `session-*.md` | OpenCode session exports (audit trail) |

---

## Duration Discrepancy Handling

| Scenario | Resolution |
|----------|------------|
| Label > Timestamp span | Use label-based end time (captures pre/post meeting) |
| Timestamp > Label | Use timestamp (rare) |
| Both equal | Either |

Documented in `meeting-notes.yaml` under `duration_discrepancy`.

---

## Naming Conventions

| Artifact | Pattern |
|----------|---------|
| Chat folder | `<participants>_<start-date>_<end-date>` |
| Export subfolder | `teams-chat-exporter_<export-timestamp>` |
| Meeting folder | `meeting-<date>_<start-hms>_<end-hms>-<topic-slug>` |
| Meeting notes | `meeting-notes.yaml` |
| Work log (rough) | `<mon><year>-rough.txt` |
| Work log (formatted) | `<mon><year>.txt` |
| Session export | `session-ses_<id>-<part>.md` |

All lowercase kebab-case.

---

## Related Files

- `session-tracker.yaml` — Task tracking for this pipeline
- `.vscode/bookmarks.json` — Workflow checkpoints in session exports
- `scripts/work-log/convert-teams-json.py` — JSON → per-meeting HTML/JSON splitter
- `scripts/work-log/analyze_time.py` — Time analysis utilities

---

## Future Improvements

- [ ] Automate Steps 6–9 via single script
- [ ] Add OneDrive/Teams API integration for recording/transcript fetch
- [ ] Build meeting intelligence pipeline (T9)
- [ ] Generate meeting minutes automatically from cross-referenced sources