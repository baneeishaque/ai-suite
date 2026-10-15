#!/usr/bin/env python3
"""CST-aware JSONC read / sort / format primitive.

Preserves comments (``//`` and ``/* */``) and string/number lexemes through a
concrete-syntax-tree round-trip, and applies merge-friendly trailing commas in
JSONC mode (every item of every multi-line object/array, including the last).

Tier: 1 (Python 3.12+) per ai-agent-rules/scripting-language-selection-rules.md
§2.1 — stdlib-only text parsing and serialization; the §3–§5 alternatives
(shell glue, systems languages, ecosystem runtimes) do not apply.

Usage:
    python3 scripts/jsonc_cst.py read   <file>
    python3 scripts/jsonc_cst.py sort   <file> [--mode auto|jsonc|strict]
                                               [--indent N] [--in-place | --output PATH]
    python3 scripts/jsonc_cst.py format <file> [--mode auto|jsonc|strict]
                                               [--indent N] [--in-place | --output PATH]

Exit codes:
    0 — success
    1 — I/O error or JSONC parse error
    2 — usage error (argparse)
    3 — ``--mode strict`` conflicts with comments present in the input
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


class JsoncError(Exception):
    """Raised on malformed JSONC input or invalid invocation."""


# ---------------------------------------------------------------------------
# Tokenizer
# ---------------------------------------------------------------------------

PUNCTUATION = {
    "{": "LBRACE",
    "}": "RBRACE",
    "[": "LBRACKET",
    "]": "RBRACKET",
    ":": "COLON",
    ",": "COMMA",
}
COMMENT_KINDS = ("LINE_COMMENT", "BLOCK_COMMENT")
NUMBER_RE = re.compile(r"-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?")
LITERAL_RE = re.compile(r"true|false|null")


@dataclass
class Token:
    kind: str
    raw: str
    line: int
    col: int


def tokenize(text: str) -> list[Token]:
    """Split JSONC source into punctuation, scalar, and comment tokens."""
    tokens: list[Token] = []
    i, line, col, n = 0, 1, 1, len(text)

    def advance(count: int) -> None:
        nonlocal i, line, col
        for _ in range(count):
            if text[i] == "\n":
                line += 1
                col = 1
            else:
                col += 1
            i += 1

    while i < n:
        ch = text[i]
        if ch in " \t\r\n":
            advance(1)
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "/":
            end = text.find("\n", i)
            if end == -1:
                end = n
            raw = text[i:end].removesuffix("\r")
            tokens.append(Token("LINE_COMMENT", raw, line, col))
            advance(end - i)
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "*":
            end = text.find("*/", i + 2)
            if end == -1:
                raise JsoncError(f"unterminated block comment at line {line}")
            end += 2
            tokens.append(Token("BLOCK_COMMENT", text[i:end], line, col))
            advance(end - i)
            continue
        if ch == '"':
            j = i + 1
            while j < n:
                if text[j] == "\\":
                    j += 2
                    continue
                if text[j] == '"':
                    break
                if text[j] == "\n":
                    raise JsoncError(f"unterminated string at line {line}")
                j += 1
            if j >= n:
                raise JsoncError(f"unterminated string at line {line}")
            j += 1
            tokens.append(Token("STRING", text[i:j], line, col))
            advance(j - i)
            continue
        if ch in PUNCTUATION:
            tokens.append(Token(PUNCTUATION[ch], ch, line, col))
            advance(1)
            continue
        match = NUMBER_RE.match(text, i)
        if match:
            raw = match.group(0)
            tokens.append(Token("NUMBER", raw, line, col))
            advance(len(raw))
            continue
        match = LITERAL_RE.match(text, i)
        if match:
            raw = match.group(0)
            tokens.append(Token("LITERAL", raw, line, col))
            advance(len(raw))
            continue
        raise JsoncError(f"unexpected character {ch!r} at line {line} col {col}")

    tokens.append(Token("EOF", "", line, col))
    return tokens


# ---------------------------------------------------------------------------
# Concrete syntax tree
# ---------------------------------------------------------------------------


@dataclass
class Comment:
    raw: str
    kind: str  # "line" | "block"


@dataclass
class Scalar:
    raw: str
    kind: str  # "string" | "number" | "literal"


@dataclass
class Member:
    key_raw: str
    key: str
    value: object
    leading: list[Comment] = field(default_factory=list)
    trailing: list[Comment] = field(default_factory=list)


@dataclass
class Element:
    value: object
    leading: list[Comment] = field(default_factory=list)
    trailing: list[Comment] = field(default_factory=list)


@dataclass
class JObject:
    members: list[Member] = field(default_factory=list)
    dangling: list[Comment] = field(default_factory=list)


@dataclass
class JArray:
    elements: list[Element] = field(default_factory=list)
    dangling: list[Comment] = field(default_factory=list)


@dataclass
class Document:
    leading: list[Comment]
    root: object
    trailing: list[Comment]


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def take(self) -> Token:
        token = self.tokens[self.pos]
        self.pos += 1
        return token

    def next_significant(self) -> Token:
        index = self.pos
        while self.tokens[index].kind in COMMENT_KINDS:
            index += 1
        return self.tokens[index]

    def collect_comments(self) -> list[Comment]:
        comments: list[Comment] = []
        while self.peek().kind in COMMENT_KINDS:
            token = self.take()
            kind = "line" if token.kind == "LINE_COMMENT" else "block"
            comments.append(Comment(token.raw, kind))
        return comments

    def parse_document(self) -> Document:
        leading = self.collect_comments()
        root = self.parse_value()
        trailing = self.collect_comments()
        token = self.peek()
        if token.kind != "EOF":
            raise JsoncError(f"unexpected {token.raw!r} at line {token.line}")
        return Document(leading, root, trailing)

    def parse_value(self):
        token = self.peek()
        if token.kind == "LBRACE":
            return self.parse_object()
        if token.kind == "LBRACKET":
            return self.parse_array()
        if token.kind in ("STRING", "NUMBER", "LITERAL"):
            self.take()
            kind = {"STRING": "string", "NUMBER": "number", "LITERAL": "literal"}[token.kind]
            return Scalar(token.raw, kind)
        raise JsoncError(f"expected a value at line {token.line} col {token.col}")

    def parse_tail(self) -> tuple[list[Comment], bool]:
        """Consume the separator comma plus same-line trailing comments.

        Returns the trailing comments and whether a comma was seen, so the
        caller can enforce that members/elements are comma-separated.
        """
        trailing: list[Comment] = []
        end_line = self.tokens[self.pos - 1].line
        comma_seen = False
        while True:
            token = self.peek()
            if token.kind == "COMMA" and not comma_seen:
                comma_seen = True
                end_line = token.line
                self.take()
                continue
            if token.kind in COMMENT_KINDS and token.line == end_line:
                self.take()
                kind = "line" if token.kind == "LINE_COMMENT" else "block"
                trailing.append(Comment(token.raw, kind))
                continue
            break
        return trailing, comma_seen

    def parse_object(self) -> JObject:
        self.take()  # {
        obj = JObject()
        pending: list[Comment] = []
        while True:
            pending.extend(self.collect_comments())
            token = self.peek()
            if token.kind == "RBRACE":
                obj.dangling = pending
                self.take()
                return obj
            if token.kind != "STRING":
                raise JsoncError(f"expected a string key at line {token.line} col {token.col}")
            self.take()
            colon = self.peek()
            if colon.kind != "COLON":
                raise JsoncError(f"expected ':' at line {colon.line} col {colon.col}")
            self.take()
            value = self.parse_value()
            trailing, comma_seen = self.parse_tail()
            if not comma_seen and self.next_significant().kind != "RBRACE":
                nxt = self.next_significant()
                raise JsoncError(f"expected ',' or '}}' at line {nxt.line} col {nxt.col}")
            obj.members.append(Member(token.raw, json.loads(token.raw), value, pending, trailing))
            pending = []

    def parse_array(self) -> JArray:
        self.take()  # [
        arr = JArray()
        pending: list[Comment] = []
        while True:
            pending.extend(self.collect_comments())
            token = self.peek()
            if token.kind == "RBRACKET":
                arr.dangling = pending
                self.take()
                return arr
            value = self.parse_value()
            trailing, comma_seen = self.parse_tail()
            if not comma_seen and self.next_significant().kind != "RBRACKET":
                nxt = self.next_significant()
                raise JsoncError(f"expected ',' or ']' at line {nxt.line} col {nxt.col}")
            arr.elements.append(Element(value, pending, trailing))
            pending = []


# ---------------------------------------------------------------------------
# Feature scan, sorting, plain-JSON projection
# ---------------------------------------------------------------------------


def scan_features(tokens: list[Token]) -> tuple[bool, bool]:
    """Return (has_comments, has_trailing_comma) for mode auto-detection."""
    has_comments = any(token.kind in COMMENT_KINDS for token in tokens)
    has_trailing_comma = False
    for index, token in enumerate(tokens):
        if token.kind != "COMMA":
            continue
        j = index + 1
        while tokens[j].kind in COMMENT_KINDS:
            j += 1
        if tokens[j].kind in ("RBRACE", "RBRACKET"):
            has_trailing_comma = True
            break
    return has_comments, has_trailing_comma


def is_sortable_scalar(node: object) -> bool:
    """Mirror of the legacy deep-sort primitive: strings, numbers, booleans."""
    if not isinstance(node, Scalar):
        return False
    if node.kind in ("string", "number"):
        return True
    return node.kind == "literal" and node.raw in ("true", "false")


def scalar_sort_key(node: Scalar):
    if node.kind == "string":
        return (0, json.loads(node.raw).lower())
    if node.kind == "number":
        value = json.loads(node.raw)
        return (1, value if isinstance(value, int) else float(value), node.raw)
    return (2, 0 if node.raw == "false" else 1)


def sort_tree(node: object) -> None:
    """Recursively sort object keys (case-sensitive) and primitive arrays."""
    if isinstance(node, JObject):
        for member in node.members:
            sort_tree(member.value)
        node.members.sort(key=lambda member: member.key)
    elif isinstance(node, JArray):
        for element in node.elements:
            sort_tree(element.value)
        if node.elements and all(is_sortable_scalar(element.value) for element in node.elements):
            node.elements.sort(key=lambda element: scalar_sort_key(element.value))


def to_plain(node: object):
    """Project the CST onto plain Python data (comments dropped)."""
    if isinstance(node, Scalar):
        return json.loads(node.raw)
    if isinstance(node, JObject):
        return {member.key: to_plain(member.value) for member in node.members}
    if isinstance(node, JArray):
        return [to_plain(element.value) for element in node.elements]
    raise JsoncError(f"unexpected node type: {type(node).__name__}")


# ---------------------------------------------------------------------------
# Serializer
# ---------------------------------------------------------------------------


class Serializer:
    def __init__(self, indent: int = 2, jsonc: bool = False, newline: str = "\n"):
        self.indent = indent
        self.jsonc = jsonc
        self.newline = newline
        self.lines: list[str] = []

    def pad(self, level: int) -> str:
        return " " * (self.indent * level)

    def normalized(self, raw: str) -> str:
        return raw.replace("\r\n", "\n").replace("\n", self.newline)

    def emit_comment(self, comment: Comment, level: int) -> None:
        self.lines.append(self.pad(level) + self.normalized(comment.raw))

    def emit_trailing(self, trailing: list[Comment]) -> None:
        if trailing:
            self.lines[-1] += "  " + " ".join(self.normalized(c.raw) for c in trailing)

    def emit_value(self, node: object, level: int, prefix: str) -> None:
        if isinstance(node, Scalar):
            self.lines.append(prefix + node.raw)
            return
        if isinstance(node, JObject):
            if not node.members and not node.dangling:
                self.lines.append(prefix + "{}")
                return
            self.lines.append(prefix + "{")
            child = self.pad(level + 1)
            for index, member in enumerate(node.members):
                for comment in member.leading:
                    self.emit_comment(comment, level + 1)
                self.emit_value(member.value, level + 1, child + member.key_raw + ": ")
                if self.jsonc or index < len(node.members) - 1:
                    self.lines[-1] += ","
                self.emit_trailing(member.trailing)
            for comment in node.dangling:
                self.emit_comment(comment, level + 1)
            self.lines.append(self.pad(level) + "}")
            return
        if isinstance(node, JArray):
            if not node.elements and not node.dangling:
                self.lines.append(prefix + "[]")
                return
            self.lines.append(prefix + "[")
            child = self.pad(level + 1)
            for index, element in enumerate(node.elements):
                for comment in element.leading:
                    self.emit_comment(comment, level + 1)
                self.emit_value(element.value, level + 1, child)
                if self.jsonc or index < len(node.elements) - 1:
                    self.lines[-1] += ","
                self.emit_trailing(element.trailing)
            for comment in node.dangling:
                self.emit_comment(comment, level + 1)
            self.lines.append(self.pad(level) + "]")
            return
        raise JsoncError(f"unexpected node type: {type(node).__name__}")

    def render(self, document: Document) -> str:
        for comment in document.leading:
            self.emit_comment(comment, 0)
        self.emit_value(document.root, 0, "")
        for comment in document.trailing:
            self.emit_comment(comment, 0)
        return self.newline.join(self.lines) + self.newline


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def resolve_mode(
    requested: str, path: Path, has_comments: bool, has_trailing_comma: bool
) -> str:
    if requested in ("jsonc", "strict"):
        return requested
    if path.suffix.lower() == ".jsonc":
        return "jsonc"
    if has_comments or has_trailing_comma:
        return "jsonc"
    return "strict"


def load(path: Path) -> tuple[str, list[Token], bool, bool]:
    text = path.read_bytes().decode("utf-8-sig")
    tokens = tokenize(text)
    has_comments, has_trailing_comma = scan_features(tokens)
    return text, tokens, has_comments, has_trailing_comma


def read_command(path: Path) -> int:
    _, tokens, _, _ = load(path)
    data = to_plain(Parser(tokens).parse_document().root)
    sys.stdout.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return 0


def transform_command(
    path: Path,
    mode_requested: str,
    indent: int,
    do_sort: bool,
    in_place: bool,
    output: str | None,
) -> int:
    text, tokens, has_comments, has_trailing_comma = load(path)
    mode = resolve_mode(mode_requested, path, has_comments, has_trailing_comma)
    if mode == "strict" and has_comments:
        print(
            f"ERROR: {path} contains comments but --mode strict was requested; "
            "strict JSON cannot represent comments. Use --mode jsonc.",
            file=sys.stderr,
        )
        return 3
    document = Parser(tokens).parse_document()
    if do_sort:
        sort_tree(document.root)
    newline = "\r\n" if "\r\n" in text else "\n"
    serializer = Serializer(indent=indent, jsonc=(mode == "jsonc"), newline=newline)
    rendered = serializer.render(document)
    if in_place:
        path.write_bytes(rendered.encode("utf-8"))
    elif output:
        Path(output).write_bytes(rendered.encode("utf-8"))
    else:
        sys.stdout.write(rendered)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="jsonc_cst.py",
        description=(
            "CST-aware JSONC read / sort / format: comments are preserved and "
            "JSONC output gets merge-friendly trailing commas on every item."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    read_parser = sub.add_parser("read", help="strip comments/trailing commas and print strict JSON")
    read_parser.add_argument("file")

    commands = (
        ("sort", "deep-sort object keys and primitive arrays, preserving comments"),
        ("format", "re-emit with canonical indentation and merge-friendly trailing commas"),
    )
    for name, help_text in commands:
        sub_parser = sub.add_parser(name, help=help_text)
        sub_parser.add_argument("file")
        sub_parser.add_argument("--mode", choices=("auto", "jsonc", "strict"), default="auto")
        sub_parser.add_argument("--indent", type=int, default=2)
        target = sub_parser.add_mutually_exclusive_group()
        target.add_argument("--in-place", action="store_true")
        target.add_argument("--output", metavar="PATH")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path = Path(args.file)
    try:
        if not path.is_file():
            raise JsoncError(f"file not found: {path}")
        if args.command == "read":
            return read_command(path)
        return transform_command(
            path,
            args.mode,
            args.indent,
            do_sort=(args.command == "sort"),
            in_place=args.in_place,
            output=args.output,
        )
    except JsoncError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
