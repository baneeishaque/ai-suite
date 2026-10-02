#!/usr/bin/env python3
"""
shell-command-permission-verifier — BASE.

Reads the five shell-command permission backends from their native config files,
replays each command in a spec against each engine, and asserts the verdict.

Engines (one function per backend, each returning "allow"|"ask"|"ask_user"|"deny"):

  opencode-glob  — opencode.json `permission.bash` object: pattern->action, last-match-wins
                   over the wildcard matcher (findLast), default "ask".
  kilo-glob     — ~/.config/kilo/kilo.jsonc `permission.bash` object: identical algorithm
                   to opencode (kilo is a fork; same matcher).
  claude-fnmatch — Claude `~/.config/Claude/settings.json` `permissions.allow` list of
                   strings: any fnmatch match -> "allow", else "ask".
  copilot-regex  — VS Code `chat.tools.terminal.autoApprove` list of anchored `^...$` regexes
                   (stored as /regex/flags strings): any re.search match -> "allow", else "ask".
  gemini-regex-toml — ~/.gemini/policies/safe-commands.toml `[[rule]]` tables: highest
                   priority tier whose first matching rule wins, else default "ask_user".

Spec fixture format (JSON):
  {
    "description": "human label",
    "commands": [
      {"command": "<exact shell string>", "expect": {"opencode":"allow","kilo":"allow",...}}
    ]
  }

Usage:
  verify-verdicts.py                          # run all bundled specs/
  verify-verdicts.py spec-foo.json            # run one spec relative to specs/
  verify-verdicts.py --tools opencode,kilo    # restrict engines
  verify-verdicts.py --json                   # machine-readable
  verify-verdicts.py --strict                 # exit 1 on any mismatch
"""
from __future__ import annotations
import argparse
import fnmatch
import fnmatch as _fnmatch
import hashlib
import json
import os
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPECS = HERE.parent / "specs"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BOLD = "\033[1m"
RESET = "\033[0m"


# --------------------------------------------------------------------------- #
# Config path resolution (env overrides → canonical <user-home> paths)        #
# --------------------------------------------------------------------------- #
def _home() -> str:
    return os.path.expanduser("~")


DEFAULTS = {
    "opencode": os.path.join(os.environ.get("XDG_CONFIG_HOME", _home() + "/.config"), "opencode", "opencode.json"),
    "kilo":     os.path.join(_home(), ".config", "kilo", "kilo.jsonc"),
    "claude":   os.path.join(_home(), ".claude", "settings.json"),
    "copilot":  os.path.join(_home(), "Library", "Application Support", "Code - Insiders", "User", "settings.json"),
    "gemini":   os.path.join(_home(), ".gemini", "policies", "safe-commands.toml"),
}

ENV_KEYS = {
    "opencode": "OPENCODE_CONFIG",
    "kilo":     "KILO_CONFIG",
    "claude":   "CLAUDE_CONFIG",
    "copilot":  "COPILOT_SETTINGS",
    "gemini":   "GEMINI_SAFE_COMMANDS",
}


def config_path(tool: str) -> str:
    v = os.environ.get(ENV_KEYS[tool])
    if v:
        return v
    return DEFAULTS[tool]


# --------------------------------------------------------------------------- #
# JSONC parsing (robust: comments + trailing commas, control-char safe)        #
# --------------------------------------------------------------------------- #
def parse_jsonc(text: str) -> str:
    """Strip // line and /* block */ comments and trailing commas, respecting
    string literals. Returns JSON text that json.loads can consume
    (strict=False tolerates control chars inside strings, matching opencode's
    read-jsonc.py that already validated these configs)."""
    out = []
    i = 0
    n = len(text)
    in_str = False
    esc = False
    slash = False  # possible start of // or /*
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                # handle "" escape? opencode configs are JSONC not JSON5; keep simple
                in_str = False
            i += 1
            slash = False
            continue
        if slash:
            if c == "/":
                # line comment: skip to end of line
                j = text.find("\n", i + 1)
                if j == -1:
                    i = n
                else:
                    i = j + 1
                slash = False
                continue
            if c == "*":
                # block comment: skip to */
                j = text.find("*/", i + 1)
                if j == -1:
                    i = n
                else:
                    i = j + 2
                slash = False
                continue
            # not a comment; emit the pending '/'
            out.append("/")
            slash = False
            # do not advance; handle c in main switch
        if c == "/" and not in_str:
            slash = True
            i += 1
            continue
        if c == '"':
            in_str = True
        out.append(c)
        i += 1
    # strip trailing commas before } or ] (outside strings — recompute simply)
    text = re.sub(r",\s*([}\]])", r"\1", "".join(out))
    return text


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return json.loads(parse_jsonc(raw), strict=False)


# --------------------------------------------------------------------------- #
# Opencode wildcard matcher — ported verbatim from @opencode-ai/core util/wildcard.ts
# --------------------------------------------------------------------------- #
_SPECIALS = re.compile(r"[.+\^\$\{\}\(\)\|[\]\\]")


def wildcard_match(input_str: str, pattern: str) -> bool:
    normalized = input_str.replace("\\", "/")
    escaped = pattern.replace("\\", "/")
    # TS: replace(/[.+^${}()|[\]\\]/g, "\\$&") — escape specials EXCEPT space and '-'
    escaped = _SPECIALS.sub(lambda m: "\\" + m.group(0), escaped)
    escaped = escaped.replace("*", ".*")
    escaped = escaped.replace("?", ".")
    if escaped.endswith(" .*"):
        escaped = escaped[:-3] + "( .*)?"
    # opencode builds new RegExp("^"+escaped+"$", "s")
    return re.fullmatch(escaped, normalized, re.DOTALL) is not None


# --------------------------------------------------------------------------- #
# Engines                                                                     #
# --------------------------------------------------------------------------- #
@dataclass
class Verdict:
    command: str
    results: dict[str, str]
    expected: dict[str, str] | None


class Engine:
    name: str = "base"

    def verdict(self, command: str) -> str:
        raise NotImplementedError


class OpencodeEngine(Engine):
    """pattern->action object, last-match-wins, default ask."""

    def __init__(self, tool: str, path: str, key: str = "bash") -> None:
        self.tool = tool
        self.name = tool
        self.path = path
        self.key = key
        cfg = load_json(path)
        self.rules = cfg.get("permission", {}).get(key, {})

    def verdict(self, command: str) -> str:
        # rules is a dict pattern->action; object insertion order == file order
        matched_action = "ask"
        for pattern, action in self.rules.items():
            if wildcard_match(command, pattern):
                matched_action = action
        return matched_action


class KiloEngine(OpencodeEngine):
    def __init__(self, path: str) -> None:
        super().__init__("kilo", path)


class ClaudeEngine(Engine):
    """fnmatch over allow list, any match -> allow else ask."""

    def __init__(self, path: str) -> None:
        self.name = "claude"
        self.path = path
        cfg = load_json(path)
        self.allow = cfg.get("permissions", {}).get("allow", [])

    def verdict(self, command: str) -> str:
        for pat in self.allow:
            if fnmatch.fnmatchcase(command, pat):
                return "allow"
        return "ask"


class CopilotEngine(Engine):
    """anchored regex list (VS Code chat.tools.terminal.autoApprove)."""

    def __init__(self, path: str) -> None:
        self.name = "copilot"
        self.path = path
        import json as _j
        with open(path, encoding="utf-8") as f:
            cfg = _j.load(f)
        raw = cfg.get("chat.tools.terminal.autoApprove", [])
        self.regexes: list[re.Pattern] = []
        for entry in raw:
            pat = entry
            flags = 0
            if len(pat) >= 2 and pat[0] == "/" and pat[-1] == "/":
                pat = pat[1:-1]
            elif len(pat) >= 3 and pat[0] == "/" and "/" in pat[1:]:
                idx = pat.rfind("/")
                pat = pat[1:idx]
                flagstr = pat[idx + 1:]  # placeholder, real parse above
            # flags after trailing slash
            flags = 0
            if pat.startswith("/") and "/" in pat[1:]:
                pass
            # robust: entry like /^...$/i
            m = re.match(r"^/(.*)/([a-z]*)$", entry)
            if m:
                pat = m.group(1)
                flagstr = m.group(2)
                if "i" in flagstr:
                    flags |= re.IGNORECASE
            else:
                pat = entry.strip("/")
            self.regexes.append(re.compile(pat, flags))

    def verdict(self, command: str) -> str:
        for rx in self.regexes:
            if rx.search(command):
                return "allow"
        return "ask"


class GeminiEngine(Engine):
    """[[rule]] tables, highest priority tier first-match-wins, else ask_user."""

    def __init__(self, path: str) -> None:
        self.name = "gemini"
        self.path = path
        with open(path, "rb") as f:
            data = tomllib.load(f)
        rules = data.get("rule", [])
        # sort by priority desc, stable (ties: document order preserved via stable sort)
        self.rules = sorted(rules, key=lambda r: r.get("priority", 0), reverse=True)

    @staticmethod
    def _match(rule: dict, command: str) -> bool:
        prefixes = rule.get("commandPrefix")
        if prefixes:
            for p in prefixes:
                if command.startswith(p):
                    return True
            return False
        rx = rule.get("commandRegex")
        if rx:
            return re.search(rx, command) is not None
        return False

    def verdict(self, command: str) -> str:
        top_pri = None
        for rule in self.rules:
            p = rule.get("priority", 0)
            if not self._match(rule, command):
                continue
            if top_pri is None:
                top_pri = p
            if p == top_pri:
                return "allow" if rule.get("decision") == "allow" else "ask_user"
        return "ask_user"


class MissingEngine(Engine):
    """Config file absent — verdicts always 'none' (engine skipped)."""

    def __init__(self, tool: str) -> None:
        self.tool = tool
        self.name = tool

    def verdict(self, command: str) -> str:
        return "none"


def build_engines() -> dict[str, Engine]:
    out: dict[str, Engine] = {}
    for tool in ALL_TOOLS:
        path = config_path(tool)
        if not os.path.exists(path):
            out[tool] = MissingEngine(tool)
            continue
        try:
            if tool == "opencode":
                out[tool] = OpencodeEngine(tool, path)
            elif tool == "kilo":
                out[tool] = KiloEngine(path)
            elif tool == "claude":
                out[tool] = ClaudeEngine(path)
            elif tool == "copilot":
                out[tool] = CopilotEngine(path)
            elif tool == "gemini":
                out[tool] = GeminiEngine(path)
        except Exception as exc:  # noqa: BLE001
            out[tool] = MissingEngine(tool)
            if not os.environ.get("VERIFY_QUIET"):
                print(f"{YELLOW}warn: {tool} engine failed to load ({path}): {exc}{RESET}", file=sys.stderr)
    return out


ALL_TOOLS = ["opencode", "kilo", "claude", "copilot", "gemini"]


# --------------------------------------------------------------------------- #
# Spec runner                                                                 #
# --------------------------------------------------------------------------- #
def run_spec(spec: dict, engines: dict[str, Engine], selected: list[str]) -> list[Verdict]:
    vds: list[Verdict] = []
    for entry in spec.get("commands", []):
        cmd = entry["command"]
        expected = entry.get("expect", {})
        results = {}
        for tool in selected:
            eng = engines.get(tool)
            if eng is None:
                continue
            results[tool] = eng.verdict(cmd)
        vds.append(Verdict(command=cmd, results=results, expected=expected))
    return vds


def _spec_pass(vd: Verdict) -> bool:
    """A spec asserts verdicts only for the engines it names (keys of `expected`).
    Tools absent from `expected` are intentionally not checked (specs are scoped
    to the engines that actually carry the command)."""
    for tool, exp in vd.expected.items():
        if vd.results.get(tool) != exp:
            return False
    return True


def fmt_verdict(v: str) -> str:
    colors = {
        "allow": GREEN,
        "ask": YELLOW,
        "ask_user": YELLOW,
        "deny": RED,
        "none": "\033[37m",
    }
    c = colors.get(v, "")
    return f"{c}{v:<9}{RESET}"


def print_table(vds: list[Verdict], tools: list[str], as_json: bool, strict: bool, spec_desc: str) -> int:
    if as_json:
        rows = []
        for vd in vds:
            rows.append({"command": vd.command, "results": vd.results,
                         "expected": vd.expected, "pass": _spec_pass(vd)})
        fails = sum(1 for r in rows if not r["pass"])
        print(json.dumps({"description": spec_desc, "tools": tools, "results": rows, "fails": fails}, indent=2))
        return 0

    print(f"{BOLD}{spec_desc}{RESET}")
    print(f"{'command':<40} " + " ".join(f"{t:<9}" for t in tools))
    print("-" * (40 + len(tools) * 10))
    fails = 0
    for vd in vds:
        ok = _spec_pass(vd)
        if not ok:
            fails += 1
        flag = "PASS" if ok else "FAIL"
        color = GREEN if ok else RED
        print(f"{color}{flag} {RESET}{vd.command:<37} " + " ".join(fmt_verdict(vd.results.get(t, "none")) for t in tools))
        if not ok:
            print(f"  {BOLD}expected:{RESET} {vd.expected}")
    print(f"{GREEN}ALL PASS{RESET}" if not fails else f"{RED}{fails} FAIL{RESET}")
    return 1 if (strict and fails) else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("specs", nargs="*", default=["__all__"],
                    help="spec file name(s) in specs/ (default: all *.json)")
    ap.add_argument("--tools", default=",".join(ALL_TOOLS), help="comma list, default: all")
    ap.add_argument("--cmd", help="single command to verdict (then exit; --tools applies)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true", help="exit 1 on any mismatch")
    args = ap.parse_args(argv)

    selected = [t for t in args.tools.split(",") if t]
    unknown = [t for t in selected if t not in ALL_TOOLS]
    if unknown:
        print(f"{RED}unknown tools: {unknown}{RESET}", file=sys.stderr)
        return 2

    engines = build_engines()
    if args.cmd is not None:
        results = {}
        for t in selected:
            eng = engines.get(t)
            if isinstance(eng, MissingEngine):
                results[t] = "none"
            else:
                results[t] = eng.verdict(args.cmd)
        if args.json:
            print(json.dumps({"command": args.cmd, "results": results}, indent=2))
        else:
            print(f"{BOLD}{args.cmd}{RESET}")
            for t in selected:
                print(f"  {t:<9}: {fmt_verdict(results.get(t, 'none'))}")
        return 0

    missing = [t for t in selected if not os.path.exists(config_path(t))]
    if missing and not args.json:
        print(f"{YELLOW}config not found (engine returns none): {missing}{RESET}", file=sys.stderr)

    spec_files: list[Path] = []
    if args.specs == ["__all__"]:
        spec_files = sorted(SPECS.glob("*.spec.json"))
    else:
        for s in args.specs:
            spec_files.append(SPECS / s if not os.path.isabs(s) else Path(s))

    if not spec_files:
        print(f"{YELLOW}no specs found in {SPECS}{RESET}", file=sys.stderr)
        return 2

    total = 0
    total_fails = 0
    for sp in spec_files:
        with open(sp, encoding="utf-8") as f:
            spec = json.load(f)
        vds = run_spec(spec, engines, selected)
        total += len(vds)
        rc = print_table(vds, selected, args.json, args.strict, spec.get("description", sp.name))
        # tally fails = specs that assert a verdict for an engine but mismatched
        for vd in vds:
            if not _spec_pass(vd):
                total_fails += 1
        if rc:
            total_fails += 1  # spec-level fail marker
    if not args.json:
        print(f"\n{total} commands checked, {total_fails} mismatch{'es' if total_fails != 1 else ''}")
    return 1 if (args.strict and total_fails) else 0


if __name__ == "__main__":
    sys.exit(main())
