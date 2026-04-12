from __future__ import annotations

from .errors import LexError
from .nodes import Token

KEYWORDS = {
    "array", "stack", "queue", "deque", "list", "set", "map", "graph",
    "directed", "undirected",
    "if", "else", "end", "for", "from", "to", "while",
    "true", "false", "null",
    "and", "or", "not",
    "print", "swap", "highlight",
}


class Lexer:

    def __init__(self, src: str):
        self.src = src
        self.pos = 0
        self.line = 1
        self.tokens: list[Token] = []

    def tokenize(self) -> list[Token]:
        while self.pos < len(self.src):
            c = self.src[self.pos]
            if c == "\n":
                self._emit("NEWLINE", None)
                self.line += 1
                self.pos += 1
            elif c in " \t\r":
                self.pos += 1
            elif c == "#":
                self._skip_comment()
            elif c.isdigit() or self._neg_number_here(c):
                self._read_number()
            elif c in "\"'":
                self._read_string(c)
            elif c.isalpha() or c == "_":
                self._read_word()
            else:
                self._read_symbol(c)
        self._emit("EOF", None)
        return self.tokens

    def _emit(self, kind: str, value):
        self.tokens.append(Token(kind, value, self.line))

    def _skip_comment(self):
        while self.pos < len(self.src) and self.src[self.pos] != "\n":
            self.pos += 1

    def _neg_number_here(self, c: str) -> bool:
        if c != "-" or self.pos + 1 >= len(self.src):
            return False
        if not self.src[self.pos + 1].isdigit():
            return False
        last = self.tokens[-1] if self.tokens else None
        if last is None:
            return True
        return last.kind in ("OP", "LP", "LB", "COMMA", "NEWLINE", "ASSIGN", "COLON")

    def _read_number(self):
        start = self.pos
        if self.src[self.pos] == "-":
            self.pos += 1
        while self.pos < len(self.src) and (self.src[self.pos].isdigit() or self.src[self.pos] == "."):
            self.pos += 1
        raw = self.src[start:self.pos]
        value = float(raw) if "." in raw else int(raw)
        self._emit("NUMBER", value)

    def _read_string(self, quote: str):
        start_line = self.line
        self.pos += 1
        start = self.pos
        while self.pos < len(self.src) and self.src[self.pos] != quote:
            if self.src[self.pos] == "\n":
                self.line += 1
            self.pos += 1
        if self.pos >= len(self.src):
            raise LexError(f"Unterminated string at line {start_line}")
        self._emit("STRING", self.src[start:self.pos])
        self.pos += 1

    def _read_word(self):
        start = self.pos
        while self.pos < len(self.src) and (self.src[self.pos].isalnum() or self.src[self.pos] == "_"):
            self.pos += 1
        word = self.src[start:self.pos]
        if word in KEYWORDS:
            self._emit(word.upper(), word)
        else:
            self._emit("IDENT", word)

    def _read_symbol(self, c: str):
        two = self.src[self.pos:self.pos + 2]
        if two in ("==", "!=", "<=", ">=", "->"):
            self._emit("OP" if two != "->" else "ARROW", two)
            self.pos += 2
            return
        one = {
            "+": ("OP", "+"),
            "-": ("OP", "-"),
            "*": ("OP", "*"),
            "/": ("OP", "/"),
            "%": ("OP", "%"),
            "<": ("OP", "<"),
            ">": ("OP", ">"),
            "=": ("ASSIGN", "="),
            "(": ("LP", "("),
            ")": ("RP", ")"),
            "[": ("LB", "["),
            "]": ("RB", "]"),
            ",": ("COMMA", ","),
            ":": ("COLON", ":"),
            ".": ("DOT", "."),
        }.get(c)
        if one is None:
            raise LexError(f"Unexpected character {c!r} at line {self.line}")
        self._emit(*one)
        self.pos += 1


def tokenize(src: str) -> list[Token]:
    return Lexer(src).tokenize()
