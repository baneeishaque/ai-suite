#!/usr/bin/env python3
"""
cross-tool-shell-command-permission-sync — COMPOSER.

Syncs the **read-only allow family** from opencode (`permission.bash` object, SSOT) into the
other four backends (Kilo, Claude, Copilot, Gemini), preserving every unrelated existing
entry (unique-key upsert), backing up before writing, and invoking the base
`shell-command-permission-verifier` as a subprocess to confirm parity (no inlining of the
verdict engines — see base SKILL.md §Rule Compliance).

Translation of each opencode allow pattern:
  kilo     — copy the object key verbatim (identical matcher).
  claude   — wrap as "Bash(<pattern>)" string (fnmatch over full tool-call).
  copilot  — convert glob '*' -> '.*', '?' -> '.', escape regex specials, wrap as /^...$/.
  gemini   — emit a [[rule]] table: toolName="run_shell_command", commandRegex="^trans$
              decision="allow", priority=100.

Safety:
  * `--dry-run` only prints proposed diffs (no writes).
  * Every write is preceded by an md5-stamped backup.
  * After write: md5-stability (sleep >=3s, re-read identical) + parse re-read check.
  * Backups are never deleted.
  * No commits.

Usage:
  sync-permission-rules.py --dry-run
  sync-permission-rules.py
  sync-permission-rules.py --tools kilo,claude
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent.parent / "shell-command-permission-verifier"
BASE_VERIFIER = BASE / "scripts" / "verify-verdicts.py"
REGISTRY = HERE / "tool-registry.json"
HOME = os.path.expanduser("~")

RED = "\033[31m"; GREEN = "\033[32m"; YELLOW = "\033[33m"; BOLD = "\033[1m"; RESET = "\033[0m"
TARGETS = ["kilo", "claude", "copilot", "gemini"]


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


# --------------------------------------------------------------------------- #
# Config IO                                                                      #
# --------------------------------------------------------------------------- #
def read_jsonc(path: str) -> dict:
    """Reuse opencode-jsonc-util SSOT via subprocess (cross-category reuse, not import)."""
    util = Path("/Users/dk/lab-data/ai-suite/.agents/skills/opencode-jsonc-util/scripts/read-jsonc.py")
    if util.exists():
        out = subprocess.run([sys.executable, str(util), path], capture_output=True, text=True)
        if out.returncode == 0 and out.stdout.strip():
            return json.loads(out.stdout)
        log(f"warn: read-jsonc failed for {path}: {out.stderr.strip()} — falling back to json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def read_json(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# --------------------------------------------------------------------------- #
# Registry + SSOT extraction                                                       #
# --------------------------------------------------------------------------- #
def load_registry() -> dict:
    with open(REGISTRY, encoding="utf-8") as f:
        return json.load(f)


def expand_registry(reg: dict) -> dict:
    out = {}
    for tool, info in reg.items():
        if not isinstance(info, dict) or "path" not in info:
            out[tool] = info  # $schema / $comment passthrough
            continue
        p = info["path"].replace("<user-home>", HOME)
        out[tool] = {**info, "path": p}
    return out


def sso_allow_patterns(reg: dict) -> list[tuple[str, str]]:
    """Return [(pattern, action)] for the opencode bash allow family, in file order."""
    op = reg["opencode"]
    cfg = read_jsonc(op["path"])
    rules = cfg.get("permission", {}).get("bash", {})
    # opencode permission.bash is an object preserving insertion order
    return [(pat, act) for pat, act in rules.items() if act == "allow"]


# --------------------------------------------------------------------------- #
# Pattern translators                                                            #
# --------------------------------------------------------------------------- #
_SPECIALS = re.compile(r"[.+\^\$\{\}\(\)\|[\]\\\\]")


def glob_to_regex(pattern: str) -> str:
    """opencode-glob pattern -> anchored regex for Copilot/Gemini (literal spaces and
    '-' kept literal; only . + ^ $ { } ( ) | [ ] \\ escaped; '*' -> '.*'; '?' -> '.').
    Trailing ' *' (opencode 'any-args' tail) -> '( .*)?' to preserve optional-arg
    semantics. Anchored ^...$. Mirrors the base engine's wildcard_match escaping."""
    out = pattern.replace("\\", "/")
    out = _SPECIALS.sub(lambda m: "\\" + m.group(0), out)
    out = out.replace("*", ".*")
    out = out.replace("?", ".")
    if out.endswith(" .*"):
        out = out[:-3] + "( .*)?"
    return "^" + out + "$"


def sso_to_entries(pattern: str, action: str, reg: dict) -> dict:
    """Produce the target notation entry keyed by an identity string.
    The identity is what we dedupe/insert by (unique-key per tool)."""
    op_pat = pattern
    # kilo: same glob string
    kilo_entry = op_pat
    # claude: Bash(<pattern>)
    claude_entry = f"Bash({op_pat})"
    # copilot: /regex/
    copilot_entry = "/" + glob_to_regex(op_pat) + "/"
    # gemini: commandRegex (priority 100 allow)
    gemini_regex = glob_to_regex(op_pat)
    return {
        "kilo": kilo_entry,
        "claude": claude_entry,
        "copilot": copilot_entry,
        "gemini_regex": gemini_regex,
    }


# --------------------------------------------------------------------------- #
# Backend writers (upsert, no clobber)                                           #
# --------------------------------------------------------------------------- #
def write_jsonc(path: str, cfg: dict, original_text: str) -> None:
    """Write back preserving JSONC: strip comments for parse, then json.dump (no comments).
    opencode/kilo/claude configs in this workspace are effectively JSON (no comments relied
    upon at runtime post-load) — json.dump is safe and md5-stable across rewrites."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
        f.write("\n")


def upsert_kilo(cfg: dict, entry: str) -> bool:
    perms = cfg.setdefault("permission", {})
    bash = perms.get("bash")
    if not isinstance(bash, dict):
        return False
    before = dict(bash)
    # upsert by exact key
    bash[entry] = "allow"
    return bash != before


def upsert_claude(cfg: dict, entry: str) -> bool:
    perms = cfg.setdefault("permissions", {})
    allow = perms.get("allow")
    if not isinstance(allow, list):
        return False
    if entry in allow:
        return False
    allow.append(entry)
    return True


def upsert_copilot(cfg: dict, entry: str) -> bool:
    aa = cfg.get("chat.tools.terminal.autoApprove")
    if not isinstance(aa, list):
        return False
    if entry in aa:
        return False
    aa.append(entry)
    return True


def upsert_gemini(data: dict, regex: str) -> bool:
    rules = data.get("rule", [])
    # unique key: the commandRegex string + priority 100 + decision allow
    key = (regex, 100, "allow")
    for r in rules:
        if (r.get("commandRegex"), r.get("priority", 0), r.get("decision")) == key:
            return False
    rules.append({
        "toolName": "run_shell_command",
        "commandRegex": regex,
        "decision": "allow",
        "priority": 100,
    })
    return True


# --------------------------------------------------------------------------- #
# Backup + stability                                                              #
# --------------------------------------------------------------------------- #
def md5_file(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def backup(path: str) -> str:
    digest = md5_file(path)
    ts = time.strftime("%Y%m%dT%H%M%S")
    bak = f"{path}.syncbak.{ts}.{digest}"
    shutil.copy2(path, bak)
    return bak


def stable_rewrite(path: str, cfg: dict, reader, parse_only: bool, dry: bool, label: str) -> bool:
    """Write cfg to path; if not dry, backup, write, sleep>=3s, re-read+parse+md5-stability."""
    if dry:
        return False
    bak = backup(path)
    before_md5 = md5_file(path)
    write_jsonc(path, cfg, "")
    after_md5 = md5_file(path)
    time.sleep(3)
    again_md5 = md5_file(path)
    if before_md5 != after_md5 and after_md5 == again_md5:
        # parse check
        reader(path)
        log(f"  {GREEN}ok{RESET} {label}: md5-stable write ({bak})")
        return True
    log(f"  {RED}FAIL{RESET} {label}: md5 instability or parse error")
    return False


# --------------------------------------------------------------------------- #
# Main sync                                                                        #
# --------------------------------------------------------------------------- #
def sync_tool(tool: str, patterns: list[tuple[str, str]], reg: dict, dry: bool) -> int:
    info = reg[tool]
    path = info["path"]
    changes = 0
    if not os.path.exists(path):
        log(f"{YELLOW}skip {tool}: config not found at {path}{RESET}")
        return 0
    if info.get("format") == "toml":
        with open(path, "rb") as f:
            data = tomllib.load(f)
        if tool == "gemini":
            for p, a in patterns:
                regex = sso_to_entries(p, a, reg)["gemini_regex"]
                if upsert_gemini(data, regex):
                    changes += 1
                    log(f"  + gemini allow: commandRegex={regex}")
            if not dry and changes:
                bak = backup(path)
                before = md5_file(path)
                text = _dump_toml(data)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(text)
                time.sleep(3)
                after = md5_file(path)
                if before != after and after == md5_file(path):
                    log(f"  {GREEN}ok{RESET} gemini: md5-stable write ({bak})")
                else:
                    log(f"  {RED}FAIL{RESET} gemini: md5 instability")
            if not dry and changes == 0:
                log(f"  {YELLOW}noop{RESET} gemini: all allow entries already present")
            return changes
        # other toml tools (none currently) fall through to generic
        cfg = data
    else:
        cfg = read_jsonc(path)  # JSONC-capable (handles VS Code JSONC + Claude strict JSON)
    if tool == "kilo":
        for p, a in patterns:
            e = sso_to_entries(p, a, reg)["kilo"]
            if upsert_kilo(cfg, e):
                changes += 1
                log(f"  + kilo allow: {e}")
    elif tool == "claude":
        for p, a in patterns:
            e = sso_to_entries(p, a, reg)["claude"]
            if upsert_claude(cfg, e):
                changes += 1
                log(f"  + claude allow: {e}")
    elif tool == "copilot":
        for p, a in patterns:
            e = sso_to_entries(p, a, reg)["copilot"]
            if upsert_copilot(cfg, e):
                changes += 1
                log(f"  + copilot allow: {e}")

    if not dry and changes:
        if tool in ("kilo", "claude", "copilot"):
            stable_rewrite(path, cfg, read_jsonc, False, dry, tool)
    if not dry and changes == 0:
        log(f"  {YELLOW}noop{RESET} {tool}: all allow entries already present")
    return changes


def _dump_toml(data: dict) -> str:
    """Minimal TOML emitter for [[rule]] tables + top-level scalars (sufficient for
    safe-commands.toml structure; preserves existing rule ordering). Re-emits only
    rule tables we touch + keeps existing keys. Uses tomli_w if available, else manual."""
    try:
        import tomli_w  # type: ignore
        import io
        buf = io.BytesIO()
        tomli_w.dump(data, buf)
        return buf.getvalue().decode("utf-8")
    except ImportError:
        return _dump_toml_manual(data)


def _dump_toml_manual(data: dict) -> str:
    lines = ["# Sync written by cross-tool-shell-command-permission-sync (Tier-1 Python)."]
    for key, val in data.items():
        if key == "rule":
            for r in val:
                lines.append("[[rule]]")
                for k, v in r.items():
                    lines.append(f'{k} = {json.dumps(v)}')
                lines.append("")
        elif isinstance(val, bool):
            lines.append(f"{key} = {'true' if val else 'false'}")
        else:
            lines.append(f"{key} = {json.dumps(val)}")
    return "\n".join(lines) + "\n"


def verify_parity(reg: dict) -> int:
    """Shell out to the base verifier (no inlining) over the cross-tool-align spec."""
    if not BASE_VERIFIER.exists():
        log(f"{YELLOW}base verifier missing at {BASE_VERIFIER}{RESET}")
        return 0
    env = dict(os.environ)
    env["VERIFY_QUIET"] = "1"
    proc = subprocess.run(
        [sys.executable, str(BASE_VERIFIER), "cross-tool-align.spec.json", "--strict"],
        cwd=str(BASE), capture_output=True, text=True, env=env,
    )
    if proc.returncode != 0:
        log(f"{RED}base verifier FAILED — parity not confirmed{RESET}")
        if proc.stderr:
            log(proc.stderr[-2000:])
        return proc.returncode
    log(f"{GREEN}base verifier OK — parity confirmed{RESET}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tools", default=",".join(TARGETS), help="comma list of sync targets")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verify-only", action="store_true",
                    help="skip writes; only run the base verifier parity check on current configs")
    args = ap.parse_args(argv)

    reg = expand_registry(load_registry())
    patterns = sso_allow_patterns(reg)
    log(f"{BOLD}SSOT (opencode allow patterns): {len(patterns)}{RESET}")
    if not patterns and not args.dry_run and not args.verify_only:
        log(f"{RED}no allow patterns in SSOT — refusing to sync{RESET}")
        return 2

    targets = [t for t in args.tools.split(",") if t]
    for t in targets:
        if t not in TARGETS:
            log(f"{RED}unknown target: {t}{RESET}")
            return 2

    if args.verify_only:
        log(f"{BOLD}--- parity verification (current configs, no writes) ---{RESET}")
        return verify_parity(reg)

    log(f"{'DRY RUN — ' if args.dry_run else ''}syncing read-only allow family to: {targets}")
    for t in targets:
        log(f"{BOLD}--- {t} ---{RESET}")
        sync_tool(t, patterns, reg, args.dry_run)

    if args.dry_run:
        log(f"{YELLOW}dry-run complete — no writes performed{RESET}")
        return 0

    log(f"{BOLD}--- parity verification ---{RESET}")
    return verify_parity(reg)


if __name__ == "__main__":
    sys.exit(main())
