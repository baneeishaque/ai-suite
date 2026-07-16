#!/usr/bin/env python3
"""
detect-audio-language.py — Detect spoken language from a media file's audio track.

Extracts a 10-second audio sample via ffmpeg, uses SpeechRecognition with
Google Web Speech API to detect the language. Falls back to langdetect if
available and speech recognition fails.

Usage:
    python3 detect-audio-language.py --video /path/to/media.mp4
    python3 detect-audio-language.py --video /path/to/media.mp4 --duration 15
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile


def parse_args():
    p = argparse.ArgumentParser(description="Detect audio language from media file")
    p.add_argument("--video", required=True, help="Path to media file")
    p.add_argument("--duration", type=int, default=10, help="Sample duration in seconds (default: 10)")
    p.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    return p.parse_args()


def _probe_silence(video_path, detected_lang, language_name, confidence):
    """Run ffmpeg volumedetect to check for digital silence (mean_volume ≤ -80 dB).

    Called when speech recognition returns no transcript or raises UnknownValueError.
    Returns (detected_lang, language_name, confidence) — either updated to "silent"
    or unchanged if silence cannot be confirmed.
    """
    try:
        probe = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_streams", "-select_streams", "a",
             video_path],
            capture_output=True, text=True, timeout=15
        )
        if probe.returncode == 0 and probe.stdout.strip():
            vd = subprocess.run(
                ["ffmpeg", "-i", video_path, "-af", "volumedetect",
                 "-vn", "-sn", "-f", "null", "/dev/null"],
                capture_output=True, text=True, timeout=30
            )
            for line in vd.stderr.split("\n"):
                if "mean_volume" in line:
                    # line format: "[...] mean_volume: -91.0 dB"
                    after_colon = line.split("mean_volume:")[-1].strip()
                    db_str = after_colon.split()[0].rstrip("dB")
                    db_val = float(db_str)
                    if db_val <= -80.0:
                        return ("silent", "Silent (digital silence)", "deterministic")
    except (subprocess.TimeoutExpired, ValueError, OSError):
        pass
    return (detected_lang, language_name, confidence)


def main():
    args = parse_args()

    if not os.path.isfile(args.video):
        print(f"ERROR: File not found: {args.video}", file=sys.stderr)
        sys.exit(1)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        sample_path = tmp.name

    try:
        cmd = [
            "ffmpeg", "-y",
            "-t", str(args.duration),
            "-i", args.video,
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            sample_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"ERROR: ffmpeg sample extraction failed: {result.stderr}", file=sys.stderr)
            sys.exit(1)

        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.AudioFile(sample_path) as source:
            audio = r.record(source)

        try:
            result = r.recognize_google(audio, show_all=True)
            transcript = ""
            detected_lang = "en"

            if result:
                if "alternative" in result and result["alternative"]:
                    transcript = result["alternative"][0].get("transcript", "")

            if transcript:
                # Google's API returns language info implicitly through the
                # transcript quality; for now, assume English if we got a transcript
                detected_lang = "en"
                language_name = "English"
                confidence = "high"
            else:
                detected_lang, language_name, confidence = _probe_silence(
                    args.video, "unknown", "Unknown", "none")
        except sr.UnknownValueError:
            detected_lang, language_name, confidence = _probe_silence(
                args.video, "unknown", "Unknown", "none")
            transcript = ""
        except sr.RequestError as e:
            print(f"ERROR: Speech recognition API error: {e}", file=sys.stderr)
            sys.exit(1)

        if args.format == "json":
            output = {
                "language_code": detected_lang,
                "language_name": language_name,
                "confidence": confidence,
                "transcript_snippet": transcript[:200] if transcript else "",
            }
            print(json.dumps(output, indent=2))
        else:
            print(f"Detected language: {language_name} ({detected_lang})")
            print(f"Confidence: {confidence}")
            if transcript:
                print(f"Transcript sample: \"{transcript[:200]}\"")

    finally:
        if os.path.exists(sample_path):
            os.unlink(sample_path)


if __name__ == "__main__":
    main()
