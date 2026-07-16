# [YouTube Channel Organization & Skill Audit] (v1)

## Rule Compliance Reference

- [AI Agent Planning Rules](../../ai-agent-rules/ai-agent-planning-rules.md) — §2 Core Planning Directive, §5 Anti-Summarization, §10 Task Artifact Sync
- [AI Rule Standardization Rules](../../ai-agent-rules/ai-rule-standardization-rules.md) — §2 Skill-First Architecture, §4 Script SSOT Mandate, §2 Layered Composition Mandate
- [Skill Factory SKILL.md](../.agents/skills/skill-factory/SKILL.md) — §2.0 Layering Decision, §2.1 Directory Structure, §2.2 SKILL.md Composition, §2.3 AGENTS.md, §2.4 Registration, §3 Post-Drafting Checklist, §2.2.1 Script Authoring Mandates

## Session Audit — What We Did

This session covered two major workflows:

### Workflow A — Existing Video Organization
1. Listed all 20 channel videos via YouTube Data API `playlistItems.list` on the uploads playlist
2. Listed all 32 existing channel playlists
3. Checked contents of key playlists (Oleovista Technologies, Staging Server, etc.)
4. Categorized videos into playlists based on user direction:
   - Staging Server (added 2 older videos)
   - Acer Demos (new playlist, 1 video)
   - Client Demos (new playlist, 1 video)
   - Daily Standup (Dec 2025) (new playlist, 3 videos)
   - Daily Standup (Jun 2026) (new playlist, 1 video)
   - Daily Standup (general) (new playlist, all 4)
   - Oleovista Technologies (org-wide, all already present)

### Workflow B — YouTube Upload (pending, 3 frontend standup mp4s)
- 3 mp4 files verified via ffprobe (h264 1920x1080, ~2-2.5 hrs each)
- OAuth refreshed, playlists created
- Upload blocked by user to prioritize organization first

## Gap Analysis vs Existing Skills

| Operation | Existing Skill | Gap |
|---|---|---|
| List playlists | `youtube-playlist-list` ✅ | None |
| Create playlist | ❌ No base skill | Need `youtube-playlist-create` |
| List channel videos | ❌ No base skill | Need `youtube-channel-video-list` |
| Add existing video to playlist | ❌ No base skill | Need `youtube-playlist-item-add` |
| Organize videos into playlists | ❌ No composer | Need composer combining listing + add |
| Upload video | `youtube-video-upload` ✅ | None |
| OleoVista org conventions | `youtube-upload-oleovista` ✅ | None (but could be updated) |

**Key insight**: The organization workflow (list channel → list playlists → categorize → add to playlists) is a reusable pattern. The primitive operations (create playlist, add playlist item, list channel videos) are atomic, domain-agnostic, and belong as base skills. The categorization logic belongs in a composer.

## Proposed Skill Architecture

### New Base Skills (in `ai-suite/.agents/skills/`)

| Skill | Type | Purpose |
|---|---|---|
| `youtube-playlist-create` | Base | Create a new YouTube playlist with title, description, privacy. Wraps `playlists.insert`. Deterministic output: playlist ID. |
| `youtube-playlist-item-add` | Base | Add an existing video to a playlist. Wraps `playlistItems.insert`. Deterministic output: success/failure. |
| `youtube-channel-video-list` | Base | List all uploaded videos on the authenticated channel. Wraps `playlistItems.list` on the uploads playlist. Deterministic output: JSON list of `{video_id, title, published_at}`. |

### New Composer Skill (in `ai-suite/.agents/skills/`)

| Skill | Type | Purpose |
|---|---|---|
| `youtube-channel-video-organize` | Composer | List all channel videos → list playlists → present to user → add selected videos to selected playlists. Orchestrates the 3 base skills above + `youtube-playlist-list`. |

### Updates to Existing Skills

| Skill | Change |
|---|---|
| `youtube-upload-oleovista` (oleovista-acers) | Add playlist naming conventions (Acer Demos, Client Demos, Daily Standup patterns), add `youtube-playlist-create` delegation step for topic-specific playlist creation |
| `youtube-playlist-list` (ai-suite) | Add oleovista-upload-oleovista and youtube-channel-video-organize to Composition by Higher-Level Skills table |
| `youtube-video-upload` (ai-suite) | Add youtube-playlist-create and youtube-playlist-item-add to Composition Reference |
| `youtube-channel-video-list` (ai-suite) | Register in root AGENTS.md |

### Script Language Selection

| Script | Tier Evaluation | Chosen Tier | Citation |
|---|---|---|---|
| `youtube-playlist-create/scripts/playlist-create.py` | Python 3.12+ with googleapiclient, no shell glue needed | Tier 1 (Python) | §3.1 — Standard Data API wrapper |
| `youtube-playlist-item-add/scripts/playlist-item-add.py` | Python 3.12+ with googleapiclient, no shell glue needed | Tier 1 (Python) | §3.1 — Standard Data API wrapper |
| `youtube-channel-video-list/scripts/channel-video-list.py` | Python 3.12+ with googleapiclient, pagination logic | Tier 1 (Python) | §3.1 — Standard Data API wrapper |
| `youtube-channel-video-organize/scripts/organize.py` | Python 3.12+, orchestrates multiple base scripts | Tier 1 (Python) | §3.1 — Orchestration composer |

## Files to Create/Modify

### Create (`ai-suite/.agents/skills/`)

| Path | Artifacts |
|---|---|
| `youtube-playlist-create/SKILL.md` | SKILL.md with protocol, AGENTS.md, `scripts/playlist-create.py` |
| `youtube-playlist-create/AGENTS.md` | Companion bridge |
| `youtube-playlist-create/scripts/playlist-create.py` | CLI: `--title --description --privacy` → outputs playlist ID |
| `youtube-playlist-item-add/SKILL.md` | SKILL.md with protocol, AGENTS.md, `scripts/playlist-item-add.py` |
| `youtube-playlist-item-add/AGENTS.md` | Companion bridge |
| `youtube-playlist-item-add/scripts/playlist-item-add.py` | CLI: `<video_id> <playlist_id>` → adds to playlist |
| `youtube-channel-video-list/SKILL.md` | SKILL.md with protocol, AGENTS.md, `scripts/channel-video-list.py` |
| `youtube-channel-video-list/AGENTS.md` | Companion bridge |
| `youtube-channel-video-list/scripts/channel-video-list.py` | CLI: `--credentials` → JSON output of all videos |
| `youtube-channel-video-organize/SKILL.md` | Composer SKILL.md with protocol |
| `youtube-channel-video-organize/AGENTS.md` | Companion bridge |
| `youtube-channel-video-organize/scripts/organize.py` | Orchestrator: list → categorize → add |

### Modify

| Path | Change |
|---|---|
| `ai-suite/.agents/skills/youtube-playlist-list/SKILL.md` | Add composers to Composition by Higher-Level Skills |
| `ai-suite/.agents/skills/youtube-video-upload/SKILL.md` | Add new base skills to Composition Reference |
| `ai-suite/AGENTS.md` | Register 4 new skills at alphabetical positions |
| `oleovista-acers/.agents/skills/youtube-upload-oleovista/SKILL.md` | Add playlist naming conventions + create-playlist step |
| `oleovista-acers/AGENTS.md` | No change needed unless updating description |

## Verification

1. Run `markdownlint-cli2 --fix` then `markdownlint-cli2` on all new/modified `.md` files
2. Verify each script runs with `--help` and produces expected output
3. Confirm no cross-repo relative links (redaction-portability §0.1)
4. Confirm all AGENTS.md follow §2.3 format (no frontmatter, 5 sections, 40-120 lines)
5. Confirm root AGENTS.md entries are alphabetically sorted
