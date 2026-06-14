---
name: webm-recording-merge-with-filler
description: Merge discontinuous webm recording segments into one lossless file with a filler transition (black screen + text overlay) where content is missing.
category: Media-Processing
---

# WebM Recording Merge with Filler Skill (v1)

This is a **composer** skill. It merges two or more discontinuous webm recording segments (e.g. from a meeting that was
paused and resumed) into a single lossless webm file, inserting a **filler transition** (black screen with text overlay)
at each discontinuity to signal to viewers that content was lost between segments.

The filler is generated with Pillow (text image) + ffmpeg (video encoding), then the combined file list is handed to
the [FFmpeg Lossless Concat](../ffmpeg-lossless-concat/SKILL.md) base skill for zero-quality-loss concatenation.

***

## 1. Scope & Intent

- **In scope**: Merge webm files with identical codec properties (VP9 video + Opus audio), generate a 3-second black
  filler with custom text indicating missing content, insert the filler between segments, and losslessly concatenate.
- **Out of scope**:
    - Transcoding or re-encoding existing segments (stream-copied via base skill).
    - Non-webm containers (mp4, mkv, etc. — only webm is verified).
    - Detecting discontinuities automatically (user identifies the gap position).
    - Adding filler in the middle of a continuous segment.
    - Any persistent modification of source files.

***

## 2. Environment & Dependencies

### 2.1 Required Tools

- **ffmpeg** 5.0+ — For filler generation and (via base skill) lossless concat. Verify:

  ```bash
  ffmpeg -version | head -1
  ```

- **ffprobe** (ships with ffmpeg) — Reads codec parameters from input files. Verify:

  ```bash
  ffprobe -version | head -1
  ```

- **Python 3.12+** — With **Pillow** (`pip install Pillow`) for text overlay image generation. Verify:

  ```bash
  python3 -c 'from PIL import Image, ImageDraw, ImageFont; print("Pillow OK")'
  ```

- The base skill script MUST exist at:
  `.agents/skills/ffmpeg-lossless-concat/scripts/ffmpeg_lossless_concat.py`
- **ffmpeg with `libvpx-vp9` encoder** — Verify:

  ```bash
  ffmpeg -encoders 2>/dev/null | grep -i vp9
  ```

- **ffmpeg with `libopus` encoder** — Verify:

  ```bash
  ffmpeg -encoders 2>/dev/null | grep -i opus
  ```

### 2.2 Verification

```bash
# Confirm tools
which ffmpeg ffprobe python3

# Confirm Pillow
python3 -c 'from PIL import Image; print("Pillow:", Image.__version__)'

# Confirm base skill script exists
test -f .agents/skills/ffmpeg-lossless-concat/scripts/ffmpeg_lossless_concat.py && echo "base script OK"

# Confirm VP9 + Opus encoders
ffmpeg -encoders 2>/dev/null | grep -q libvpx-vp9 && echo "VP9 encoder OK"
ffmpeg -encoders 2>/dev/null | grep -q libopus && echo "Opus encoder OK"
```

If any tool is missing, consult the [System-Wide Tool Management](../system-wide-tool-management/SKILL.md) skill.
If Pillow is missing, install it with `pip install Pillow` or `brew install pillow`.

***

## 3. Protocol

### 3.1 Step 1 — Identify and Order Segments

List all webm files and determine their playback order. For typical meeting recordings, the smaller file is the first
segment, the larger is the second. Verify by checking creation timestamps with `ls -lt *.webm` or by asking the user.

### 3.2 Step 2 — Probe Video Properties

Run ffprobe on the first input file to capture the resolution, frame rate, and audio parameters needed for the filler:

```bash
ffprobe -v quiet -print_format json -show_streams first_segment.webm
```

Extract:

- **width** and **height** (video resolution for filler dimensions)
- **r_frame_rate** (e.g. `"30/1"` — frame rate for filler)
- **sample_rate** (audio sample rate for filler silence — typically 48000)

### 3.3 Step 3 — Generate Filler

Run the composer script:

```bash
python3 .agents/skills/webm-recording-merge-with-filler/scripts/generate_filler_and_merge.py \
    --segment first_segment.webm \
    --segment second_segment.webm \
    --filler-text "Recording interrupted" \
    --filler-subtext "— content missing —" \
    --filler-duration 3 \
    --output merged_with_filler.webm
```

The script:

1. Probes all `--segment` files for codec compatibility using the base skill's logic.
2. Determines video resolution and frame rate from the first segment.
3. Generates a text overlay PNG image using Pillow (black background, white + gray text centered).
4. Generates a 3-second filler webm using ffmpeg:
   - `color` source filtered through `overlay` for the text PNG
   - `anullsrc` for silent audio at matching sample rate
   - Encoded with `libvpx-vp9` + `libopus` at high quality (`-crf 10`)
5. Builds the concat file list in segment order, with the filler after the first segment (before subsequent ones).
6. Calls the [base skill's script](../ffmpeg-lossless-concat/scripts/ffmpeg_lossless_concat.py) via `python3` to
   perform lossless concatenation of all segments (including the filler).
7. Cleans up temporary files (PNG, filler webm, concat file list).

#### 3.3.1 Flag Breakdown

| Flag | Purpose |
| :--- | :--- |
| `--segment <path>` | Repeatable — one or more webm file paths in play-order. Segments are concatenated in the order provided. |
| `--filler-text <str>` | Primary text displayed on the filler (e.g. "Recording interrupted"). |
| `--filler-subtext <str>` | Secondary subtitle text below the primary (e.g. "— content missing —"). |
| `--filler-duration <sec>` | Duration of each filler in seconds (default 3). |
| `--output <path>` | Path for the final merged webm file. |

### 3.4 Step 4 — Verify Output

```bash
# Confirm output exists
ls -lh merged_with_filler.webm

# Check its streams match originals
ffprobe -v quiet -show_entries stream=codec_name,width,height merged_with_filler.webm

# Confirm duration ≈ sum of inputs + filler durations
ffprobe -v quiet -show_entries format=duration merged_with_filler.webm

# Visual spot-check by seeking to the filler region
ffplay -ss $(ffprobe -v quiet -show_entries format=duration first_segment.webm -of csv=p=0) merged_with_filler.webm
```

The output file MUST:

- Have the same video codec (VP9) and audio codec (Opus) as the input segments.
- Show the filler text at the gap position.
- Play seamlessly from end of first segment → filler → start of second segment.

***

## 4. Composition Rationale

This skill deliberately **does not** implement lossless concatenation itself. Codec compatibility verification, concat
file list generation, and ffmpeg invocation with `-c copy` are the concerns of the base
[FFmpeg Lossless Concat](../ffmpeg-lossless-concat/SKILL.md) skill.

By composing rather than duplicating:

- A bug fix in the base skill (e.g. better stream-parameter comparison, handling of edge-case codec parameters)
  benefits every composer automatically.
- New composers (e.g. security-camera segment merge, podcast episode join, screen-recording gap fill) all reuse the
  same base — keeping the protocol for verification and lossless concat identical across the fleet.

The composer's domain-specific value over the base alone: it discovers the video resolution, generates a matching filler
segment with text overlay, and orchestrates the multi-stage pipeline (Pillow → ffmpeg filler → base concat) so the user
provides only the source segments and the filler text.

This mirrors the SSOT mandate from
[AI Agent Rule Standardization Rules §4](../../../ai-agent-rules/ai-rule-standardization-rules.md).

***

## 5. Script Reference

[`scripts/generate_filler_and_merge.py`](./scripts/generate_filler_and_merge.py) performs:

1. Parse all `--segment` paths, `--filler-text`, `--filler-subtext`, `--filler-duration`, and `--output`.
2. Run ffprobe on the first segment to extract video width, height, frame rate, and audio sample rate.
3. Create a Pillow `Image.new("RGB", (width, height), "black")`, draw filler text and subtext centered.
   Use a large system font (e.g. `/System/Library/Fonts/Helvetica.ttc` on macOS) or fall back to default.
4. Generate the filler webm:

   ```bash
   ffmpeg -y -f lavfi -i "color=c=black:s={w}x{h}:r={fps}:d={dur}" \
          -f lavfi -i "anullsrc=r={sample_rate}:cl=stereo:d={dur}" \
          -i filler_overlay.png \
          -filter_complex "[0:v][2:v]overlay=0:0" \
          -c:v libvpx-vp9 -crf 10 -b:v 0 \
          -c:a libopus -b:a 256k \
          filler.webm
   ```

5. Build a temporary concat file list with all segments in order, placing the filler after the first segment and
   before each subsequent segment.
6. Resolve the base script via `os.path.dirname(os.path.abspath(__file__))` to locate
   `../../ffmpeg-lossless-concat/scripts/ffmpeg_lossless_concat.py`.
7. Execute the base script with the concat file list and output path.
8. Remove temporary files (filler overlay PNG, filler webm, concat file list).

### 5.1 Argument Breakdown

See §3.3.1 flag table — all flags correspond directly to the script's `argparse` arguments.

***

## 6. Edge Cases & Constraints

- **Non-matching codecs**: If the input segments have different resolutions or codecs, the base skill's verification
  step exits 1 and reports the mismatch. This skill surfaces that error verbatim.
- **Missing Pillow**: The script imports `PIL` at the top and will fail with `ModuleNotFoundError` if Pillow is not
  installed. The error message suggests the install command.
- **No system font found**: The script tries macOS Helvetica, falls back to Linux font paths, then falls back to
  PIL default bitmap font (small, mono, pixelated). The filler is usable but less polished.
- **Very short segments** (< filler duration): The filler may be longer than the first segment. The script does not
  validate this — the concat still produces a valid file but the filler visually dominates.
- **Non-webm inputs**: The script probes regardless of extension, but the filler uses VP9 + Opus (webm-specific
  codecs). For non-webm containers, the filler segment's codecs may not match — the base skill will reject them.
  In that case, modify the script to match the target codecs.

***

## 7. Prohibited Actions

- The Agent MUST NOT inline the base skill's concat logic into this composer — composition through the shared base
  script is mandatory.
- The Agent MUST NOT re-encode the source segments — only the filler is encoded; source segments are stream-copied.
- The Agent MUST NOT hard-code filler duration, text, or styling — these MUST be user-configurable via flags.
- The Agent MUST NOT use system fonts that may not exist on the target OS without a fallback chain.
- The Agent MUST NOT leave temporary files (PNG, filler webm, concat list) on disk after completion.

***

## 8. Related Skills

- [FFmpeg Lossless Concat](../ffmpeg-lossless-concat/SKILL.md) — the base skill this composer invokes for lossless
  concatenation.
- [System-Wide Tool Management](../system-wide-tool-management/SKILL.md) — installs ffmpeg / ffprobe / Python /
  Pillow if any dependency is missing.
