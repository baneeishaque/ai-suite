# Usage: uv run prompt.py [<ref|query>] [options]
#
# Options:
#   --exact        exact ref match only, no fuzzy fallback
#   --no-fzf       use Python matching instead of fzf
#   --copy         copy result to clipboard instead of stdout
#   --json         output entry as JSON
#   --tag <name>   filter entries by tag (can repeat for AND)
#   --recent       show most-used refs from history
#   --list         list all entries formatted
#   --list-refs    list all refs (machine-parseable)
#
# Alias in .zshrc:
#   commit-prompt() { uv run /path/to/prompt.py "$@"; }
#
# /// pyproject.toml
# [project]
# name = "commit-prompt"
# version = "1.0.0"
# requires-python = ">=3.10"
# dependencies = [
#     "pyyaml>=6.0",
#     "rapidfuzz>=3.0",
# ]
# ///

import json
import os
import sys
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from collections import defaultdict

YAML_PATH = os.path.join(os.path.dirname(__file__), "commit.yml")
HISTORY_DIR = os.path.join(os.path.expanduser("~"), ".local", "share", "commit-prompt")
HISTORY_PATH = os.path.join(HISTORY_DIR, "history.jsonl")

try:
    import yaml
except ImportError:
    print("Missing pyyaml. Run via uv:\n  uv run prompt.py <args>")
    sys.exit(1)

HAS_FZF = shutil.which("fzf") is not None
HAS_BAT = shutil.which("bat") is not None

try:
    from rapidfuzz import fuzz, process as rp_process
    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False


def die(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def fzf_required_err():
    die(
        "fzf not found. Install: brew install fzf\n"
        "Or run with --no-fzf:\n"
        "  uv run prompt.py --no-fzf <query>"
    )


def load():
    with open(YAML_PATH) as f:
        return yaml.safe_load(f)


def expand_snippets(text, snippets):
    if not snippets or "{ " not in text and "{" not in text:
        return text
    for name, value in snippets.items():
        text = text.replace(f"{{{name}}}", value)
    return text


def resolve_add_on(entries, entry, snippets, _seen=None):
    raw = entry.get("add_on", "").strip()
    add_on = expand_snippets(raw, snippets)
    compose_ref = entry.get("compose")
    if not compose_ref:
        return add_on
    if _seen is None:
        _seen = set()
    if compose_ref in _seen:
        return add_on
    _seen.add(compose_ref)
    base = None
    for e in entries:
        if e.get("ref") == compose_ref:
            base = e
            break
    if not base:
        return add_on
    base_add_on = resolve_add_on(entries, base, snippets, _seen)
    if not base_add_on:
        return add_on
    if not add_on:
        return base_add_on
    sep = " " if base_add_on[-1] == "." or add_on[0] == "." else ". "
    return f"{base_add_on}{sep}{add_on}"


def reconstruct(common, entries, entry, snippets):
    prefix = entry.get("prefix", "").strip()
    add_on = resolve_add_on(entries, entry, snippets)
    common = common.strip()
    if not add_on and not prefix:
        return common
    if not common:
        return prefix or add_on
    if prefix:
        result = prefix.rstrip(". ") + ". " + common
        if add_on:
            sep = " " if common[-1] == "." or add_on[0] == "." else ". "
            result += sep + add_on
        return result
    if not add_on:
        return common
    sep = " " if common[-1] == "." or add_on[0] == "." else ". "
    return f"{common}{sep}{add_on}"


def fmt_list(entries):
    lines = []
    for e in entries:
        ref = e.get("ref", "") or "(no ref)"
        add_on = e.get("add_on", "")[:80]
        tags = e.get("tags", [])
        tag_str = f"  [{','.join(tags)}]" if tags else ""
        parts = []
        if e.get("compose"):
            parts.append(f"compose:{e['compose']}")
        if e.get("prefix"):
            parts.append(f"prefix:{e['prefix'][:40]}")
        desc = " | ".join(parts) + "  " if parts else "  "
        lines.append(f"  {ref:<30}{tag_str} {desc}{add_on}")
    return "\n".join(lines)


def clipboard_write(text):
    if sys.platform == "darwin":
        subprocess.run(["pbcopy"], input=text, text=True)
    elif sys.platform.startswith("linux"):
        for cmd in (["xclip", "-selection", "clipboard"], ["xsel", "-b"]):
            if shutil.which(cmd[0]):
                subprocess.run(cmd, input=text, text=True)
                return
        die("No clipboard tool found. Install xclip: brew install xclip")
    elif sys.platform == "win32":
        subprocess.run(["clip"], input=text, text=True)
    else:
        die("Clipboard not supported on this platform")


def emit(text, copy_mode, json_mode=False, entry=None):
    if json_mode and entry:
        obj = {
            "ref": entry.get("ref"),
            "add_on": entry.get("add_on"),
            "tags": entry.get("tags", []),
            "full_prompt": text,
        }
        output = json.dumps(obj, indent=2)
    else:
        output = text
    print(output)
    if copy_mode:
        clipboard_write(output)


def record_history(ref, query):
    os.makedirs(HISTORY_DIR, exist_ok=True)
    line = json.dumps({
        "ref": ref,
        "query": query,
        "ts": datetime.now(timezone.utc).isoformat(),
    })
    with open(HISTORY_PATH, "a") as f:
        f.write(line + "\n")


def get_recent(limit=10):
    if not os.path.exists(HISTORY_PATH):
        return []
    counts = defaultdict(int)
    with open(HISTORY_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                ref = entry.get("ref")
                if ref:
                    counts[ref] += 1
            except json.JSONDecodeError:
                continue
    sorted_refs = sorted(counts.items(), key=lambda x: -x[1])
    return sorted_refs[:limit]


def filter_by_tag(entries, tags):
    if not tags:
        return entries
    result = []
    for e in entries:
        etags = set(e.get("tags", []))
        if all(t in etags for t in tags):
            result.append(e)
    return result


# ── Matching backends ────────────────────────────────────────────


def pick_tui_fzf(entries, common, snippets):
    tmpdir = tempfile.mkdtemp(prefix="cprompt-")
    try:
        lines = []
        for i, e in enumerate(entries):
            ref = e.get("ref", "") or ""
            add_on = e.get("add_on", "") or ""
            full = reconstruct(common, entries, e, snippets)
            fpath = os.path.join(tmpdir, str(i))
            with open(fpath, "w") as f:
                f.write(full)
            lines.append(f"{ref}\t{add_on}\t{i}")
        previewer = "bat -l text --color=always --paging=never" if HAS_BAT else "cat"
        proc = subprocess.run(
            ["fzf", "--with-nth=1,2", "--delimiter=\t",
             "--preview", f"{previewer} {tmpdir}/" + "{3}",
             "--preview-window", "up:3:wrap"],
            input="\n".join(lines),
            capture_output=True, text=True, timeout=30,
        )
    except FileNotFoundError:
        fzf_required_err()
    except subprocess.TimeoutExpired:
        return None
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
    if not proc.stdout.strip():
        return None
    idx = int(proc.stdout.strip().rsplit("\t", 1)[-1])
    return entries[idx]


def exact_match(entries, query):
    for e in entries:
        if e.get("ref") == query:
            return e
    return None


def fuzzy_fzf(entries, query):
    lines = []
    for i, e in enumerate(entries):
        ref = e.get("ref", "") or ""
        add_on = e.get("add_on", "") or ""
        lines.append(f"{ref}\t{add_on}\t{i}")
    try:
        proc = subprocess.run(
            ["fzf", "--filter", query, "--delimiter=\t", "--with-nth=1,2"],
            input="\n".join(lines),
            capture_output=True, text=True, timeout=10,
        )
    except FileNotFoundError:
        fzf_required_err()
    except subprocess.TimeoutExpired:
        return None, []
    if not proc.stdout.strip():
        return None, []
    results = []
    for line in proc.stdout.strip().split("\n"):
        parts = line.rsplit("\t", 1)
        if len(parts) == 2:
            results.append(entries[int(parts[1])])
    if len(results) == 1:
        return results[0], []
    return None, results


def fuzzy_rapidfuzz(entries, query, cutoff=40):
    if not HAS_RAPIDFUZZ:
        die("RapidFuzz not available. Run without --no-fzf, or install: pip install rapidfuzz")
    texts = []
    for e in entries:
        ref = e.get("ref", "") or ""
        add_on = e.get("add_on", "") or ""
        texts.append(f"{ref} {add_on}" if ref else add_on)
    scored = rp_process.extract(
        query, texts, scorer=fuzz.token_set_ratio, score_cutoff=cutoff, limit=10
    )
    results = [entries[idx] for _, _, idx in scored]
    if len(results) == 1:
        return results[0], []
    return None, results


# ── Main ──────────────────────────────────────────────────────────


def main():
    raw = sys.argv
    use_exact = "--exact" in raw
    use_rapidfuzz = "--no-fzf" in raw
    copy_mode = "--copy" in raw
    json_mode = "--json" in raw
    show_recent = "--recent" in raw
    has_list = "--list" in raw
    has_list_refs = "--list-refs" in raw

    tag_filter = []
    positional = []
    skip_next = False
    for i, a in enumerate(sys.argv[1:], 1):
        if skip_next:
            skip_next = False
            continue
        if a == "--tag" and i + 1 < len(sys.argv):
            tag_filter.append(sys.argv[i + 1])
            skip_next = True
        elif a.startswith("--"):
            continue
        else:
            positional.append(a)
    sys.argv = [sys.argv[0]] + positional
    has_noquery = len(sys.argv) < 2

    # --recent: show usage stats
    if show_recent:
        recent = get_recent()
        if not recent:
            print("No history yet.")
            return
        print("Most-used refs:")
        for ref, count in recent:
            print(f"  {ref:<30}  ({count} uses)")
        return

    data = load()
    common = data.get("defaults", {}).get("common_prompt", "")
    snippets = data.get("defaults", {}).get("snippets", {})
    entries = data.get("entries", [])

    if not entries:
        die("No entries found in commit.yml")

    # Apply tag filter
    if tag_filter:
        entries = filter_by_tag(entries, tag_filter)
        if not entries:
            die(f"No entries match tag(s): {', '.join(tag_filter)}")

    if has_list:
        print(fmt_list(entries))
        return

    if has_list_refs:
        for e in entries:
            ref = e.get("ref", "")
            if ref:
                print(ref)
        return

    # No query → interactive TUI
    if has_noquery:
        if use_rapidfuzz:
            die("Interactive TUI requires fzf. Pass a query argument, or omit --no-fzf.")
        if not HAS_FZF:
            fzf_required_err()
        entry = pick_tui_fzf(entries, common, snippets)
        if entry:
            full = reconstruct(common, entries, entry, snippets)
            emit(full, copy_mode, json_mode, entry)
            record_history(entry.get("ref", ""), "")
            return
        sys.exit(1)

    query = sys.argv[1].strip()
    entry = exact_match(entries, query)

    if entry:
        full = reconstruct(common, entries, entry, snippets)
        emit(full, copy_mode, json_mode, entry)
        record_history(entry.get("ref", ""), query)
        return

    if use_exact:
        die(f"No exact match for '{query}'.")

    # Fuzzy match
    if use_rapidfuzz:
        entry, multi = fuzzy_rapidfuzz(entries, query)
    else:
        if not HAS_FZF:
            fzf_required_err()
        entry, multi = fuzzy_fzf(entries, query)

    if entry:
        full = reconstruct(common, entries, entry, snippets)
        emit(full, copy_mode, json_mode, entry)
        record_history(entry.get("ref", ""), query)
        return

    if multi:
        print(f"Multiple matches for '{query}':")
        for i, e in enumerate(multi[:5]):
            ref = e.get("ref", "") or "(no ref)"
            add_on = e.get("add_on", "")[:80]
            print(f"  {i+1}. [{ref}] {add_on}")
        return

    die(f"No match for '{query}'.")


if __name__ == "__main__":
    main()
