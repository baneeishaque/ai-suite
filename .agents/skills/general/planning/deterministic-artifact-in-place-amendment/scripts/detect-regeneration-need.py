#!/usr/bin/env python3
"""Decide whether a deterministic artifact must be REGENERATED or can be AMENDED.

Implements the gate that answers: "the generator has no flag for this transformation --
is its existing output still valid?" The verdict is a byte comparison of the shipped
artifact against a freshly generated baseline:

  STALE  - baseline differs; the artifact is out of date, REGENERATE it.
  FRESH  - byte-identical; the artifact is still valid, AMEND it in place.

FRESH is the licence to mutate the artifact directly (strike a section, repair a count)
instead of re-running the generator, which is the correct choice whenever the
generator lacks a flag for the needed change.

The baseline is produced by the CALLER (typically the generator invoked without its
--output flag, writing elsewhere). This script never executes a caller-supplied command,
so there is no command-injection surface.

Read-only contract: this script reads two files and writes nothing except its stdout
JSON.

Tier: Tier 1 (Python) per scripting-language-selection-rules.md section 3 (Tier 1 is
the default) and section 4 (byte comparison + unified diff assembly) -- stdlib only,
no CPU bottleneck, no ecosystem mandate.
"""

from __future__ import annotations

import argparse
import difflib
import json
import pathlib
import sys

DEFAULT_MAX_DIFF_LINES = 120


def read_text(path: pathlib.Path):
    """Return (text, error). `text` is None when the file cannot be read."""
    try:
        return path.read_text(encoding="utf-8"), None
    except (OSError, UnicodeDecodeError) as exc:
        return None, str(exc)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Regenerate-vs-amend gate for a deterministic artifact."
    )
    ap.add_argument("--artifact", required=True, help="Path to the shipped artifact.")
    ap.add_argument("--baseline", required=True, help="Path to a freshly regenerated copy.")
    ap.add_argument(
        "--max-diff-lines",
        type=int,
        default=DEFAULT_MAX_DIFF_LINES,
        help="Truncate the emitted unified diff (default %d)." % DEFAULT_MAX_DIFF_LINES,
    )
    ap.add_argument("--json", action="store_true", help="Emit JSON (default is JSON).")
    args = ap.parse_args()

    artifact_path = pathlib.Path(args.artifact)
    baseline_path = pathlib.Path(args.baseline)

    if not artifact_path.is_file():
        print(json.dumps({"verdict": "MISSING_ARTIFACT", "artifact": str(artifact_path)}, indent=2))
        return 3
    if not baseline_path.is_file():
        print(json.dumps({"verdict": "MISSING_BASELINE", "baseline": str(baseline_path)}, indent=2))
        return 3

    artifact_text, artifact_err = read_text(artifact_path)
    baseline_text, baseline_err = read_text(baseline_path)
    if artifact_err or baseline_err:
        print(
            json.dumps(
                {
                    "verdict": "UNREADABLE",
                    "artifact_error": artifact_err,
                    "baseline_error": baseline_err,
                },
                indent=2,
            )
        )
        return 3

    identical = artifact_text == baseline_text
    payload = {
        "artifact": str(artifact_path),
        "baseline": str(baseline_path),
        "verdict": "FRESH" if identical else "STALE",
        "action": (
            "amend-in-place (generator output still valid)"
            if identical
            else "regenerate (artifact drifted from generator output)"
        ),
        "artifact_bytes": len(artifact_text.encode("utf-8")),
        "baseline_bytes": len(baseline_text.encode("utf-8")),
        "diff": "",
    }

    if not identical:
        diff_lines = list(
            difflib.unified_diff(
                artifact_text.splitlines(),
                baseline_text.splitlines(),
                fromfile=str(artifact_path),
                tofile=str(baseline_path),
                lineterm="",
            )
        )
        truncated = len(diff_lines) > args.max_diff_lines
        payload["diff"] = "\n".join(diff_lines[: args.max_diff_lines])
        payload["diff_truncated"] = truncated
        payload["diff_total_lines"] = len(diff_lines)

    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())