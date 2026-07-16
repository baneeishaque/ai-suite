# Teams Chat Export → Work Log Processing Walkthrough

**Session**: `0c1d09aacffehMxzFP6YJNoAhC` — work-log-from-teams-meeting-export
**Date**: 2026-07-14
**Version**: v1

---

## Overview

This walkthrough documents the complete end-to-end pipeline for processing Microsoft Teams chat exports (from [teamschatexporter.com](https://teamschatexporter.com/)) into structured per-meeting folders with rich metadata, cross-referenced against rough work logs, and generating formatted work log entries.

---

## Input Artifacts

| Source | Description |
|--------|-------------|
| `TeamsExport_Anjitha, Dileena, Muhammed, +3_2026-07-06_07-35-19.zip` | Teams Chat Exporter ZIP (JSON, HTML, CSV, PDF, TXT) |
| `teams-files-2026-07-06.zip` | Shared files (images, previews) |
| `teams-messages-2026-07-06.csv/.html` | Message extractor output |
| Rough work logs | `mar2026-rough.txt`, `may2026-rough.txt`, etc. |

---

## Processing Pipeline

### Step 1: Symlink / Ingest OneDrive Export

```bash
ln -s "/Users/dk/Library/CloudStorage/OneDrive-OMPVentureFZ-LLC/Backups/oleovista-acer-teams-chats" \
      /Users/dk/lab-data/oleovista-acers/oleovista-acer-teams-chats
```

> Later superseded by committing files directly to git.

---

### Step 2: Rename Export ZIP to Kebab Case

```bash
# Original: TeamsExport_Anjitha, Dileena, Muhammed, +3_2026-07-06_07-35-19.zip
# Renamed:  teams-export-anjitha-dileena-muhammed-3-2026-07-06-07-35-19.zip
```

---

### Step 3: Create Per-Chat Folder

```
oleovista-acer-teams-chats/anjitha-dileena-muhammed-3_2026-03-25_2026-05-07_2026-07-04/
```

Naming: `<participants>_<meeting-dates>` (kebab-case, dates are meeting dates, not export date).

---

### Step 4: Unzip & Organize

```bash
unzip teams-export-*.zip -d teams-chat-exporter_<export-timestamp>/
```

Extracted files:
- `teams-export.{json,html,csv,pdf,txt}`
- Internal folder `TeamsExport_Anjitha, Dileena, Muhammed, +3_2026-07-06_07-35-19/`

---

### Step 5: Generate Per-Meeting Folders (from JSON)

**Script**: `scripts/work-log/convert-teams-json.py`

1. Parse `teams-export.json` → extract individual meetings by `meeting_started`/`meeting_ended` boundaries
2. For each meeting, create folder: `meeting-YYYY-MM-DD_HHMMSS_HHMMSS-<topic-slug>/`
3. Split HTML at meeting boundaries (preserves rich content: attachments, formatting, threads)

**Output structure**:
```
teams-chat-exporter_2026-07-06_073519/
├── teams-export.{csv,html,json,pdf,txt}
├── meeting-2026-03-25_124811_125811-jira-ticket-discussion-with-praveena/
│   ├── teams-export.html
│   ├── teams-export.json
│   └── meeting-notes.yaml
├── meeting-2026-05-07_121730_123808-praveena-call/
│   ├── teams-export.html
│   ├── teams-export.json
│   └── meeting-notes.yaml
└── meeting-2026-07-04_152232_212511-local-testing-env-setup-and-staging-data-reconciliation/
    ├── teams-export.html
    ├── teams-export.json
    └── meeting-notes.yaml
```

---

### Step 6: Set Meeting Folder End Times (Label vs Timestamp)

**Rule**: Use the **greater** of:
- `meeting_ended` timestamp (Teams system time)
- `meeting_started` + `duration_label` (the "⏱ Xh Ym Zs" label on "Meeting ended" divider)

| Meeting | Timestamp Duration | Label Duration | Delta | Chosen |
|---------|-------------------|----------------|-------|--------|
| Mar 25 | 1m 56s | 10m | 8m 4s | label |
| May 7 | 17m 8s | 20m 38s | 3m 30s | label |
| Jul 4 | 5h 56m 35s | 6h 2m 39s | 6m 4s | label |

Folder end time = `start + max(ts_duration, label_duration)`

---

### Step 7: Create `meeting-notes.yaml` Per Meeting

Rich metadata including:
- `folder_name`, `description`, `timestamps` (UTC + IST)
- `duration_discrepancy` (ts vs label, delta, note)
- `participants` list
- `messages` count
- `post_meeting_chat` / `key_topics` structured as arrays of objects
- `derived_from_work_log` linking to rough log line

**Example (Mar 25)**:
```yaml
folder_name: meeting-2026-03-25_124811_125811-jira-ticket-discussion-with-praveena
derived_from_work_log: |
  mar2026-rough.txt line 138:
  "Jira start 12:25, praveena call discussion of ticket, calendar analysis,
   up to including shemeem evide call & it's return call 13:10"
  The 2-min meeting (12:48-12:50 IST) falls within this broader activity
  block — the Praveena ticket discussion portion.
timestamps:
  meeting_started_utc: "2026-03-25T07:18:11.973Z"
  meeting_ended_utc: "2026-03-25T07:20:07.556Z"
  duration_label: "10m"
duration_discrepancy:
  ts_based: "0:01:56"
  label_based: "0:10:00"
  delta: "0:08:04"
  note: "The 10m label is 8m longer than timestamp span. Possibly includes pre-meeting wait. Folder end time uses greater value (label-based)."
participants:
  - Banee Ishaque K
  - PRAVEENA AK
  - Muhammed Shemeem  # joined after meeting, per "join fron end" msg
messages: 3
post_meeting_chat:
  entries:
    - speaker: PRAVEENA AK
      time_ist: "13:31"
      message: "hi"
    - speaker: PRAVEENA AK
      time_ist: "13:36"
      message: "onnukudi vilikkavo (Malayalam: shall I call you?)"
    - speaker: Muhammed Shemeem
      time_ist: "13:36"
      message: "join fron end"
  note: "Messages posted 41-46 min after meeting ended. PRAVEENA checking in, then asking if she should call Shemeem; Shemeem responds 'join fron end' matching work log 'shemeem evide call'."
```

---

### Step 8: Cross-Reference with Rough Work Logs

Enhance rough log entries with precise meeting times (IST, label-based end):

**mar2026-rough.txt:138** (before):
```
1. Jira start 12:25, praveena call discussion of ticket, calendar analysis, up to including shemeem evide call & it's return call 13:10
```

**After**:
```
1. Jira start 12:25, praveena call discussion of ticket (12:48 to 12:58 Teams meeting with Shemeem & PRAVEENA), calendar analysis, up to including shemeem evide call & it's return call 13:10
```

**may2026-rough.txt:28** (before):
```
Praveena Call, Aishwarya Call (Rebuild Status), Shemeem Call, Praveena Call, ...
```

**After**:
```
Praveena Call (12:17 to 12:38 Teams meeting with Shemeem & PRAVEENA), Aishwarya Call (Rebuild Status), Shemeem Call, Praveena Call, ...
```

---

### Step 9: Create Formatted Work Log Entries

Format: `DD/MM/YYYY Day HH:MM:SS HH:MM:SS "Title - Participants"`

| Meeting | Formatted Entry |
|---------|-----------------|
| Mar 25 | `25/03/2026 Wednesday 12:48:11 12:58:11 "Teams Meeting: Jira Ticket Discussion with Praveena - Banee Ishaque K, PRAVEENA AK, Muhammed Shemeem"` |
| May 7 | `07/05/2026 Thursday 12:17:30 12:38:08 "Teams Meeting: Praveena Call - Banee Ishaque K, Muhammed Shemeem, PRAVEENA AK"` |
| Jul 4 | `04/07/2026 Saturday 15:22:32 21:25:11 "Teams Meeting: Local Testing Env Setup and Staging Data Reconciliation - Anjitha Sebastian, Banee Ishaque K, Dileena Beegum, Muhammed Shemeem, PRAVEENA AK, Razik Kamal"` |

Files created/updated:
- `mar2026.txt` (1 line)
- `may2026.txt` (1 line)
- `jul2026.txt` (1 line)

---

### Step 10: Shorten Exported Files

Rename `teams-export-anjitha-dileena-muhammed-3-2026-07-06-07-35-19.*` → `teams-export.*` (CSV, HTML, JSON, PDF, TXT)

Parent folder renamed to include export timestamp:
```
teams-chat-exporter_2026-07-06_073519/
├── teams-export.csv
├── teams-export.html
├── teams-export.json
├── teams-export.pdf
├── teams-export.txt
└── meeting-*/...
```

---

### Step 11: Analyze Message Extractor Output

`teams-message-extractor-chat-export/teams-messages-2026-07-06/` contains:
- `teams-messages-2026-07-06.html` — threaded message view
- `image-*.jpg` — shared images
- `url-preview-for-acers.png` — URL preview

Used for supplementary context (attachments, threading).

---

### Step 12: Atomic Git Commits

Each logical unit = one commit:

| # | Commit | Scope |
|---|--------|-------|
| 1 | `feat(work-log): enrich mar2026-rough.txt with Mar 25 meeting` | rough log |
| 2 | `feat(work-log): enrich may2026-rough.txt with May 7 meeting` | rough log |
| 3 | `feat(work-log): add mar2026.txt formatted entry` | formatted |
| 4 | `feat(work-log): add may2026.txt formatted entry` | formatted |
| 5 | `feat(work-log): add jul2026.txt formatted entry` | formatted |
| 6 | `feat(teams-chats): add chat exporter data for anjitha-dileena-muhammed-3` | full exporter dir |
| 7 | `feat(teams-chats): add message extractor data for anjitha-dileena-muhammed-3` | message extractor dir |
| 8 | `feat(teams-chats): add opencode session exports for teams chat processing` | session exports |

13 work-log files + 3 teams-chat directories = **16 atomic commits** (max atomicity).

---

### Step 13: Document Workflow

This walkthrough file created per planning artifact naming convention:
```
docs/2026-07-14_0c1d09aacffehMxzFP6YJNoAhC_work-log-from-teams-meeting-export_walkthrough_v1.md
```

---

## Key Decisions & Rationale

| Decision | Rationale |
|----------|-----------|
| Label-based end time > timestamp end | Captures pre-meeting wait / post-meeting wrap-up |
| Per-meeting folders | Self-contained, linkable, versionable |
| `meeting-notes.yaml` structured | Machine-parseable, diff-friendly, cross-referenceable |
| Split HTML not JSON | JSON lacks rich content (attachments, formatting, thread structure) |
| Rough log enrichment inline | Preserves diary flow, adds precision |
| Separate formatted entries | Standardized, queryable, reporting-ready |
| Timestamp format with seconds (`HH:MM:SS`) | Precision matching label resolution |

---

## Future Extensions (T9 — Meeting Intelligence Pipeline)

| Source | Method | Output |
|--------|--------|--------|
| Teams recording URL | Fetch transcript (if available) | Structured transcript |
| OneDrive recording | Download video | Local copy |
| Audio track | Whisper / Google Speech (Malayalam + English) | Fallback transcript |
| Cross-reference | Chat + Teams transcript + audio transcript | Enriched meeting notes |
| LLM processing | Extract minutes, action items, tasks, agendas | Structured deliverables |
| Store | Per-meeting folder | `meeting-minutes.md`, `action-items.yaml`, etc. |

---

## Related Artifacts

| File | Purpose |
|------|---------|
| `session-tracker.yaml` | Task tracking for this pipeline |
| `.vscode/bookmarks.json` | Breakpoints across session exports |
| `scripts/work-log/convert-teams-json.py` | JSON → per-meeting HTML/JSON splitter |
| `scripts/work-log/analyze_time.py` | Time analysis utilities |
| `docs/teams-chat-export-workflow.md` | Earlier partial documentation |

---

## Verification Checklist

- [x] All 3 meetings have per-meeting folders with `meeting-notes.yaml`
- [x] Rough logs enhanced with precise meeting times
- [x] Formatted entries created in `mar2026.txt`, `may2026.txt`, `jul2026.txt`
- [x] Exported files shortened, parent folder timestamped
- [x] 16 atomic commits pushed to `oleovista-acers` master
- [x] Lint-clean YAML (2-space indent, valid structure)
- [x] This walkthrough saved per naming convention