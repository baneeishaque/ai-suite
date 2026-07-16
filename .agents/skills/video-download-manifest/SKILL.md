---
name: video-download-manifest
description: Download video from a manifest or playlist URL using ffmpeg. Generic base skill for any workflow that captures a video stream URL.
category: Media Processing
---

# Video Download from Manifest Skill (v1)

This is a **base** skill. It downloads a video from a manifest, playlist,
or direct video URL using ffmpeg with codec copy (no re-encoding).
Domain-agnostic — usable by any workflow that captures a video stream URL
from browser network interception or API response.

***

## 1. Scope & Intent

- **In scope**:
    - Download video from HLS manifest (`.m3u8`), DASH manifest, or
    direct video URL
    - Use ffmpeg with `-codec copy` (lossless, no re-encoding)
    - Create output directory if needed
    - Report file size on completion
- **Out of scope**:
    - Video transcoding or format conversion
    - Network interception (delegated to
    [`browser-network-interception`](../browser-network-interception/SKILL.md))
    - Authentication or login flow
    - Any domain-specific logic (delegated to composer skills)

***

## 2. Environment & Dependencies

### 2.1 Runtime

- **macOS 14+**, Linux, Windows
- **Python 3.12+**

### 2.2 Dependencies

- **ffmpeg** installed and on PATH

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

### 2.3 Required Skill Loading

Before executing this skill, the agent MUST load:

```text
video-download-manifest/SKILL.md (this file)
```

***

## 3. Protocol

### 3.1 Step 1 — Run Download Script

```bash
python3 .agents/skills/video-download-manifest/scripts/download-from-manifest.py \
  --manifest-url "<url>" \
  --output "<path>" \
  [--timeout 600]
```

### 3.2 Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--manifest-url` | Yes | — | Manifest, playlist, or direct video URL |
| `--output` | Yes | — | Output file path (e.g., `~/Downloads/video.mp4`) |
| `--timeout` | No | `600` | ffmpeg timeout in seconds |

### 3.3 Output Contract

- **stdout**: Download progress messages and final result
- **Exit 0**: Download successful
- **Exit 1**: ffmpeg failed or download error

### 3.4 Script

| Script | Language | Purpose |
|--------|----------|---------|
| [`scripts/download-from-manifest.py`](scripts/download-from-manifest.py) | Python | ffmpeg download — accepts manifest URL, outputs video file |

***

## 4. Edge Cases

- **Invalid URL**: ffmpeg exits with non-zero code; stderr is reported.
- **Network interruption**: ffmpeg may partially download. Re-run to
  resume (ffmpeg overwrites with `-y` flag).
- **Output directory missing**: Script creates it automatically.
- **Large files**: Default timeout is 600s (10 minutes). Increase
  `--timeout` for very large recordings.

***

## 5. Composition by Higher-Level Skills

| Composer Skill | Composition Mechanism |
|----------------|----------------------|
| [`teams-recording-download`](../teams-recording-download/SKILL.md) | Calls `scripts/download-from-manifest.py` with the captured manifest URL to download the Teams recording video file. |

***

## 6. Composition Rationale

This skill is a **base** skill: it owns only the ffmpeg video download
primitive. It delegates all network interception and URL discovery to
[`browser-network-interception`](../browser-network-interception/SKILL.md).
Separating the download step from URL discovery allows reuse by any
workflow that captures a video stream URL — Teams recordings, YouTube
streams, custom video players, or API-served media.

## Related Skills

- [`browser-network-interception`](../browser-network-interception/SKILL.md) — base skill
  for capturing manifest URLs from network traffic
- [`teams-recording-download`](../teams-recording-download/SKILL.md) — composer skill
  that uses this base for Teams recording downloads
