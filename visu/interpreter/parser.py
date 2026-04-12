from __future__ import annotations

from .errors import ParseError
from .nodes import Node, Token


STRUCT_KEYWORDS = ("ARRAY", "STACK", "QUEUE", "DEQUE", "LIST", "SET", "MAP", "GRAPH")


class Parser:

    def __init__(self, tokens: list[Token]):
        self.toks = tokens
        self.pos = 0

    def peek(self, k: int = 0) -> Token:
        return self.toks[self.pos + k]

    def eat(self, kind: str | None = None) -> Token:
        t = self.toks[self.pos]
        if kind is not None and t.kind != kind:
            raise ParseError(f"Line {t.line}: expected {kind}, got {t.kind} ({t.value!r})")
        self.pos += 1
        return t

    def match(self, *kinds: str) -> bool:
        return self.peek().kind in kinds

    def skip_newlines(self):
        while self.peek().kind == "NEWLINE":
            self.pos += 1

    def parse(self) -> list[Node]:
        stmts: list[Node] = []
        self.skip_newlines()
        while not self.match("EOF"):
            stmts.append(self._statement())
            self.skip_newlines()
        return stmts

    def _statement(self) -> Node:
        t = self.peek()
        kind = t.kind
        if kind in STRUCT_KEYWORDS:
            return self._decl()
        if kind == "IF":
            return self._if()
        if kind == "WHILE":
            return self._while()
        if kind == "FOR":
            return self._for()
        if kind == "PRINT":
            return self._builtin_call("print", "PRINT")
        if kind == "SWAP":
            return self._builtin_call("swap", "SWAP")
        if kind == "HIGHLIGHT":
            return self._builtin_call("highlight", "HIGHLIGHT")
        if kind == "IDENT":
            return self._ident_stmt()
        raise ParseError(f"Line {t.line}: unexpected token {kind} ({t.value!r})")

    def _decl(self) -> Node:
        kw = self.eat()
        name = self.eat("IDENT").value
        self.eat("ASSIGN")

        if kw.value == "graph":
            direction_tok = self.peek()
            if direction_tok.kind == "DIRECTED":
                self.eat()
                directed = True
            elif direction_tok.kind == "UNDIRECTED":
                self.eat()
                directed = False
            else:
                raise ParseError(
                    f"Line {kw.line}: graph must be 'directed' or 'undirected'"
                )
            return Node(
                "decl",
                kw.line,
                {"type": "graph", "name": name, "directed": directed, "expr": None},
            )

        expr = self._expr()
        return Node("decl", kw.line, {"type": kw.value, "name": name, "expr": expr})

    def _ident_stmt(self) -> Node:
        ident = self.eat("IDENT")
        name = ident.value
        if self.match("LB"):
            self.eat("LB")
            idx = self._expr()
            self.eat("RB")
            self.eat("ASSIGN")
            val = self._expr()
            return Node("index_assign", ident.line, {"name": name, "index": idx, "value": val})
        if self.match("DOT"):
            self.eat("DOT")
            method = self._method_name()
            self.eat("LP")
            args = self._args()
            self.eat("RP")
            return Node("method", ident.line, {"name": name, "method": method, "args": args})
        if self.match("ASSIGN"):
            self.eat("ASSIGN")
            val = self._expr()
            return Node("assign", ident.line, {"name": name, "value": val})
        raise ParseError(f"Line {ident.line}: unexpected token after {name}")

    def _builtin_call(self, node_kind: str, token_kind: str) -> Node:
        t = self.eat(token_kind)
        self.eat("LP")
        args = self._args()
        self.eat("RP")
        return Node(node_kind, t.line, {"args": args})

    def _method_name(self) -> str:
        tok = self.peek()
        if tok.kind == "IDENT" or (isinstance(tok.value, str) and tok.value.isidentifier()):
            self.eat()
            return tok.value
        raise ParseError(f"Line {tok.line}: expected method name, got {tok.kind}")

    def _args(self) -> list[Node]:
        args: list[Node] = []
        if self.match("RP"):
            return args
        args.append(self._expr())
        while self.match("COMMA"):
            self.eat("COMMA")
            args.append(self._expr())
        return args

    def _block(self, terminators: tuple[str, ...]) -> list[Node]:
        stmts: list[Node] = []
        self.skip_newlines()
        while not self.match(*terminators, "EOF"):
            stmts.append(self._statement())
            self.skip_newlines()
        return stmts

    def _if(self) -> Node:
        t = self.eat("IF")
        cond = self._expr()
        self.eat("COLON")
        then_body = self._block(("ELSE", "END"))
        else_body: list[Node] = []
        if self.match("ELSE"):
            self.eat("ELSE")
            if self.match("COLON"):
                self.eat("COLON")
            else_body = self._block(("END",))
        self.eat("END")
        return Node("if", t.line, {"cond": cond, "then": then_body, "else": else_body})

    def _while(self) -> Node:
        t = self.eat("WHILE")
        cond = self._expr()
        self.eat("COLON")
        body = self._block(("END",))
        self.eat("END")
        return Node("while", t.line, {"cond": cond, "body": body})

    def _for(self) -> Node:
        t = self.eat("FOR")
        var = self.eat("IDENT").value
        self.eat("FROM")
        start = self._expr()
        self.eat("TO")
        stop = self._expr()
        self.eat("COLON")
        body = self._block(("END",))
        self.eat("END")
        return Node("for", t.line, {"var": var, "start": start, "stop": stop, "body": body})

    def _expr(self) -> Node:
        return self._or()

    def _or(self) -> Node:
        left = self._and()
        while self.match("OR"):
            t = self.eat()
            right = self._and()
            left = Node("binop", t.line, {"op": "or", "left": left, "right": right})
        return left

    def _and(self) -> Node:
        left = self._not()
        while self.match("AND"):
            t = self.eat()
            right = self._not()
            left = Node("binop", t.line, {"op": "and", "left": left, "right": right})
        return left

    def _not(self) -> Node:
        if self.match("NOT"):
            t = self.eat()
            return Node("unop", t.line, {"op": "not", "operand": self._not()})
        return self._cmp()

    def _cmp(self) -> Node:
        left = self._add()
        if self.match("OP") and self.peek().value in ("==", "!=", "<", ">", "<=", ">="):
            t = self.eat()
            right = self._add()
            left = Node("binop", t.line, {"op": t.value, "left": left, "right": right})
        return left

    def _add(self) -> Node:
        left = self._mul()
        while self.match("OP") and self.peek().value in ("+", "-"):
            t = self.eat()
            right = self._mul()
            left = Node("binop", t.line, {"op": t.value, "left": left, "right": right})
        return left

    def _mul(self) -> Node:
        left = self._unary()
        while self.match("OP") and self.peek().value in ("*", "/", "%"):
            t = self.eat()
            right = self._unary()
            left = Node("binop", t.line, {"op": t.value, "left": left, "right": right})
        return left

    def _unary(self) -> Node:
        if self.match("OP") and self.peek().value == "-":
            t = self.eat()
            return Node("unop", t.line, {"op": "-", "operand": self._unary()})
        return self._primary()

    def _primary(self) -> Node:
        t = self.peek()
        k = t.kind
        if k == "NUMBER":
            self.eat()
            return Node("num", t.line, {"value": t.value})
        if k == "STRING":
            self.eat()
            return Node("str", t.line, {"value": t.value})
        if k == "TRUE":
            self.eat()
            return Node("bool", t.line, {"value": True})
        if k == "FALSE":
            self.eat()
            return Node("bool", t.line, {"value": False})
        if k == "NULL":
            self.eat()
            return Node("null", t.line, {})
        if k == "LB":
            self.eat("LB")
            items: list[Node] = []
            if not self.match("RB"):
                items.append(self._expr())
                while self.match("COMMA"):
                    self.eat("COMMA")
                    items.append(self._expr())
            self.eat("RB")
            return Node("array_lit", t.line, {"items": items})
        if k == "LP":
            self.eat("LP")
            e = self._expr()
            self.eat("RP")
            return e
        if k == "IDENT":
            self.eat()
            if self.match("LB"):
                self.eat("LB")
                idx = self._expr()
                self.eat("RB")
                return Node("index", t.line, {"name": t.value, "index": idx})
            if self.match("DOT"):
                self.eat("DOT")
                attr = self._method_name()
                if self.match("LP"):
                    self.eat("LP")
                    args = self._args()
                    self.eat("RP")
                    return Node(
                        "method_expr",
                        t.line,
                        {"name": t.value, "method": attr, "args": args},
                    )
                return Node("attr", t.line, {"name": t.value, "attr": attr})
            return Node("var", t.line, {"name": t.value})
        raise ParseError(f"Line {t.line}: unexpected {k} in expression")


def parse(tokens: list[Token]) -> list[Node]:
    return Parser(tokens).parse()
