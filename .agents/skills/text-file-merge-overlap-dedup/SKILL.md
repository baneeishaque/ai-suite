---
name: text-file-merge-overlap-dedup
description: Merge two text files with overlapping/duplicated content at the boundary, detecting the overlap via rolling-hash longest common substring and producing a single deduplicated output.
category: File Handling
---

# Text File Merge with Overlap Deduplication Skill (v1)

When a large text file is split into parts and the split point falls inside a logical section, the resulting parts often have overlapping content at the boundary (end of part 1 duplicates start of part 2). This skill merges such parts into a single file by automatically detecting and removing the duplicated overlap.

The core primitive is **domain-agnostic**: it works on any UTF-8 text files (logs, SQL dumps, session exports, CSV, JSONL) where the overlap consists of identical line sequences.

***

## 1. When to Use This Skill

Use this skill when ALL of the following hold:

- You have **exactly two text files** that are sequential parts of a larger original
- The end of file 1 **overlaps** with the start of file 2 (identical line sequences)
- You need a **single merged file** with the overlap removed (lossless round-trip via metadata)
- The overlap is **contiguous lines** — not interleaved or fuzzy-matched

Do NOT use when:

- Files are unrelated (use standard `diff` or `comm`)
- More than two parts (chain merges: merge 1+2, then result+3)
- Overlap is non-textual or binary (use binary joiners)
- You need semantic deduplication (e.g., "same meaning, different wording")

***

## 2. Environment & Dependencies

| Requirement | Verification | Notes |
|-------------|--------------|-------|
| Python 3.12+ | `python3 --version` | Tier 1 per [Scripting Language Selection Rules](../../../ai-agent-rules/scripting-language-selection-rules.md) |
| No external packages | Standard library only | `hashlib`, `argparse`, `pathlib`, `sys` |

***

## 3. Protocol

### 3.1 Step 1 — Merge with Overlap Detection

```bash
python3 scripts/merge_overlap.py \
  --file1 <path-to-part-1> \
  --file2 <path-to-part-2> \
  --output <path-to-merged> \
  [--min-overlap-lines 10] \
  [--report-json <path>]
```

**Parameters:**

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--file1` | Yes | — | First file (earlier part) |
| `--file2` | Yes | — | Second file (later part) |
| `--output` | Yes | — | Merged output file path |
| `--min-overlap-lines` | No | 10 | Minimum contiguous matching lines to qualify as overlap |
| `--report-json` | No | stdout | Path to write overlap metadata JSON |

**Algorithm (rolling-hash LCS):**

1. Read both files as line arrays (normalizing line endings to `\n`)
2. Take suffix of file1 (last `window` lines) and prefix of file2 (first `window` lines), where `window = min(len(file1), len(file2), 5000)` — caps memory for huge files
3. Compute rolling hash (Rabin-Karp, base 257, mod 2^61-1) for all substrings of length `min_overlap` to `window` in both windows
4. Find longest common substring (contiguous line sequence) appearing in both windows
5. If length ≥ `min_overlap_lines`: overlap confirmed at those line indices
6. Output = file1 lines + file2 lines[overlap_length:]
7. Write overlap report JSON:
```json
{
  "file1_lines": 13433,
  "file2_lines": 14663,
  "overlap_start_file1": 13159,
  "overlap_start_file2": 0,
  "overlap_line_count": 274,
  "merged_lines": 27822,
  "algorithm": "rolling-hash-lcs",
  "min_overlap_lines": 10
}
```

**Exit codes:** 0 = success, 1 = no overlap found ≥ threshold, 2 = I/O error, 3 = invalid args.

### 3.2 Step 2 — Verify Round-Trip (Mandatory)

```bash
python3 scripts/verify_merge.py \
  --merged <merged-file> \
  --file1 <original-file1> \
  --file2 <original-file2> \
  --report <report-json-from-step-1>
```

Reconstructs file1 and file2 from merged + report, compares SHA-256 hashes to originals. Exits 0 only if both match byte-for-byte.

***

## 4. Script Reference

### 4.1 `scripts/merge_overlap.py`

Implements the rolling-hash longest common substring algorithm on line arrays. Key functions:

- `read_lines(path)` → `list[str]` — reads UTF-8, normalizes CRLF→LF, strips trailing newline only on last line if absent in source
- `rolling_hashes(lines, k)` → `dict[hash, list[int]]` — maps hash of k-line window to all start indices
- `find_overlap(lines1, lines2, min_k)` → `tuple[int, int, int]` — returns `(start1, start2, length)` or raises `NoOverlapError`
- `write_merged(lines1, lines2, overlap_len, output_path)` — writes deduplicated merge
- `main()` — CLI entry point, writes JSON report

### 4.2 `scripts/verify_merge.py`

- Reads merged file and report JSON
- Reconstructs file1 = merged[:overlap_start1 + overlap_len]
- Reconstructs file2 = merged[overlap_start1:] (since file2 tail follows overlap in merged)
- Computes SHA-256 of reconstructions vs originals
- Prints PASS/FAIL with hash values

***

## 5. Composition Rationale

This is a **base skill** — it owns ONLY the generic overlap detection and merge primitive. It has zero knowledge of opencode, session formats, or any domain.

Known composers (bidirectional discoverability):

| Composer | Composition Mechanism |
|----------|----------------------|
| [`opencode-session-merge`](../../../oleovista-acers/.agents/skills/opencode-session-merge/SKILL.md) | Shells out to `merge_overlap.py` via relative path; adds session-header-aware overlap hints |

The base skill is deliberately minimal so other domains (log rotation, SQL dump splits, CSV chunk merges) can compose it without carrying opencode baggage.

***

## 6. Related Skills

- [`large-text-file-stream-split`](../large-text-file-stream-split/SKILL.md) — inverse operation (split large file into chunks); uses different algorithm (byte-balanced LF cuts)
- [`near-duplicate-file-comparison`](../near-duplicate-file-comparison/SKILL.md) — forensic comparison of two similar files to decide canonical vs duplicate; different intent (judgement vs mechanical merge)

***

## 7. Hand-Back Verdict

After applying this skill, emit a 5-row verdict table:

| Item | Value |
|------|-------|
| File 1 / lines | e.g. `part1.txt` / 13,433 |
| File 2 / lines | e.g. `part2.txt` / 14,663 |
| Overlap detected | e.g. 274 lines (file1[13159:] == file2[:274]) |
| Merged output / lines | e.g. `merged.txt` / 27,822 |
| Round-trip verification | **MUST be PASS** — both SHA-256 hashes match |