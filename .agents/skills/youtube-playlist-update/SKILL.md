---
name: youtube-playlist-update
description: Update YouTube playlist metadata (title, description, privacy) via the Data API v3 playlists.update endpoint.
category: YouTube
---

# YouTube Playlist Update Skill (v1)

This is a **base** skill. It calls the YouTube Data API v3 `playlists.update` endpoint to modify a playlist's title, description, and/or privacy status. Requires valid OAuth credentials obtained via [`google-oauth-setup`](../google-oauth-setup/SKILL.md). Reusable by any YouTube workflow needing to rename or reconfigure a playlist (upload, content organization, channel management).

***

## 1. Scope & Intent

- **In scope**: Authenticate via cached OAuth credentials, fetch current playlist state via `playlists.list`, apply deltas for title/description/privacy, PUT updated playlist via `playlists.update`, print updated metadata.
- **Out of scope**:
    - OAuth token management (delegated to [`google-oauth-setup`](../google-oauth-setup/SKILL.md)).
    - Creating, listing, or deleting playlists.
    - Adding videos to a playlist (delegated to [`youtube-playlist-item-add`](../youtube-playlist-item-add/SKILL.md)).
    - Any non-YouTube API.

***

## 2. Environment & Dependencies

### 2.1 Runtime

- **Python 3.12+** — scripts use `argparse`, `json`, `requests`. Verify:

  ```bash
  python3 --version
  ```

- **`requests`** library. Verify:

  ```bash
  python3 -c "import requests; print('OK')"
  ```

### 2.2 Required Files

| File | Source |
|------|--------|
| Valid OAuth credential cache (with `access_token`) | [`google-oauth-setup`](../google-oauth-setup/SKILL.md) §3 |

***

## 3. Protocol

### 3.1 Step 1 — Ensure Valid Credentials

Before updating a playlist, verify the credential cache exists and the access token is valid. Delegate to [`google-oauth-setup`](../google-oauth-setup/SKILL.md):

```bash
# Refresh if expired
python3 .agents/skills/google-oauth-setup/scripts/oauth-token-refresh.py \
  --client-secrets <client_secrets.json> \
  --credentials <credentials.json> \
  --output <credentials.json>
```

If the refresh fails (expired refresh token), run the full PKCE flow:

```bash
python3 .agents/skills/google-oauth-setup/scripts/oauth-setup.py \
  --client-secrets <client_secrets.json> \
  --scopes "https://www.googleapis.com/auth/youtube" \
  --output <credentials.json>
```

### 3.2 Step 2 — Update Playlist Metadata

```bash
python3 .agents/skills/youtube-playlist-update/scripts/playlist-update.py \
  <PLAYLIST_ID> \
  --credentials <path> \
  [--title "<New Title>"] \
  [--description "<New Description>"] \
  [--privacy private]
```

#### 3.2.1 Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `playlist_id` | Yes (positional) | YouTube playlist ID (e.g., `PL1Bh2vwTl5j2pkjtp_pLOX_Jgt88cyMBX`). |
| `--credentials` | Yes | Path to OAuth credential cache JSON (must contain `access_token`). |
| `--title` | No | New playlist title. Omit to keep current title. |
| `--description` | No | New playlist description. Omit to keep current description. |
| `--privacy` | No | New privacy status: `private`, `unlisted`, or `public`. Omit to keep current status. |

At least one of `--title`, `--description`, or `--privacy` should be provided. If none are provided, the script fetches and prints the current state without making changes.

### 3.3 Step 3 — Interpret Output

The script prints the updated playlist metadata:

```text
Updated: PL1Bh2vwTl5j2pkjtp_pLOX_Jgt88cyMBX
  Title:       Sanath Next.js Website — Standups
  Description: Standup recordings for Sanath Next.js Website projects
  Privacy:     private
```

Confirm the playlist ID and new values are correct.

***

## 4. Script Reference

### 4.1 `scripts/playlist-update.py`

Update YouTube playlist metadata (title, description, privacy).

```text
python3 .agents/skills/youtube-playlist-update/scripts/playlist-update.py \
  <PLAYLIST_ID> --credentials <path> \
  [--title "<Title>"] [--description "<Desc>"] [--privacy private]
```

The script:

1. Loads credentials JSON and validates required fields.
2. Calls `GET https://www.googleapis.com/youtube/v3/playlists?part=snippet,status&id=<PLAYLIST_ID>` to fetch current state.
3. Applies user-supplied deltas to the playlist snippet/status (only provided fields are modified).
4. Calls `PUT https://www.googleapis.com/youtube/v3/playlists?part=snippet,status` with the merged payload.
5. On success, prints the updated playlist ID, title, description, and privacy status. Exits 0.
6. On failure (auth error, network error, playlist not found), prints diagnostic and exits 1.

***

## 5. Edge Cases

- **401 Unauthorized**: Access token is expired or invalid. Run `oauth-token-refresh.py` from [`google-oauth-setup`](../google-oauth-setup/SKILL.md) and retry.
- **403 Forbidden**: The OAuth scope does not include YouTube. Re-run `oauth-setup.py` with `--scopes "https://www.googleapis.com/auth/youtube"`.
- **Playlist not found (404)**: The specified playlist ID does not exist or belongs to another user. The script exits 1 with an error.
- **No changes requested**: If `--title`, `--description`, and `--privacy` are all omitted, the script fetches and prints the current state without making API changes, then exits 0.
- **Title too long**: YouTube limits playlist titles to 150 characters. The API returns a 400 error — the script prints the diagnostic and exits 1.
- **Privacy mismatch**: Some brand accounts may restrict `unlisted` or `public` privacy. Use `private` by default.
- **Concurrent edits**: If another process modifies the playlist between the GET and PUT, the PUT overwrites those changes. Ensure no other session is editing the same playlist.

***

## 6. Prohibited Actions

- The agent MUST NOT hardcode a playlist ID or new title/description — always present current state and let the user confirm changes.
- The agent MUST NOT update a playlist without user confirmation of the playlist ID and the new values.
- The agent MUST NOT skip the credential refresh step — a stale token will return 401.
- The agent MUST NOT use this skill to delete playlists, add/remove videos, or change playlist owner.

***

## 7. Composition by Higher-Level Skills

| Composer Skill | Composition Mechanism |
|----------------|-----------------------|

***

## 8. Composition Rationale

This skill is a **base** skill: it owns only the YouTube playlist metadata update API call (GET current state + PUT with deltas). It delegates all OAuth lifecycle management to [`google-oauth-setup`](../google-oauth-setup/SKILL.md) and is itself composed by video upload and channel organization workflows when playlists need renaming. Separating playlist update from create/list/item-add allows each operation to be reused independently (e.g., bulk playlist audit, channel rebranding).

***

## 9. Related Skills

- [`youtube-playlist-create`](../youtube-playlist-create/SKILL.md) — for creating new playlists.
- [`youtube-playlist-list`](../youtube-playlist-list/SKILL.md) — for discovering playlist IDs.
- [`youtube-playlist-item-add`](../youtube-playlist-item-add/SKILL.md) — for adding videos to playlists.
- [`youtube-video-snippet-update`](../youtube-video-snippet-update/SKILL.md) — base skill for updating video title/description/tags (often paired with playlist operations during channel tidying).
- [`youtube-video-upload`](../youtube-video-upload/SKILL.md) — composer that may trigger playlist rename during setup.
