import pytest

from visu.interpreter.errors import ParseError
from visu.interpreter.lexer import tokenize
from visu.interpreter.parser import parse


def p(src):
    return parse(tokenize(src))


def test_empty_program_produces_no_nodes():
    assert p("") == []


def test_array_declaration_with_literal():
    nodes = p("array a = [1, 2, 3]")
    assert len(nodes) == 1
    n = nodes[0]
    assert n.kind == "decl"
    assert n.data["type"] == "array"
    assert n.data["name"] == "a"
    assert n.data["expr"].kind == "array_lit"
    assert len(n.data["expr"].data["items"]) == 3


def test_empty_structure_declarations():
    for kw in ["stack", "queue", "deque", "list", "set", "map"]:
        nodes = p(f"{kw} x = []")
        assert nodes[0].data["type"] == kw


def test_graph_declaration_directed_and_undirected():
    d = p("graph g = directed")[0]
    u = p("graph g = undirected")[0]
    assert d.data["type"] == "graph" and d.data["directed"] is True
    assert u.data["type"] == "graph" and u.data["directed"] is False


def test_simple_assignment():
    n = p("x = 42")[0]
    assert n.kind == "assign"
    assert n.data["name"] == "x"
    assert n.data["value"].kind == "num"
    assert n.data["value"].data["value"] == 42


def test_index_assignment():
    n = p("a[0] = 5")[0]
    assert n.kind == "index_assign"
    assert n.data["name"] == "a"


def test_method_call_statement():
    n = p("a.push(7)")[0]
    assert n.kind == "method"
    assert n.data["name"] == "a"
    assert n.data["method"] == "push"
    assert len(n.data["args"]) == 1


def test_method_call_no_args():
    n = p("s.pop()")[0]
    assert n.kind == "method"
    assert n.data["args"] == []


def test_print_statement_multiple_args():
    n = p("print(1, 2, 3)")[0]
    assert n.kind == "print"
    assert len(n.data["args"]) == 3


def test_swap_and_highlight():
    s = p("swap(a, 0, 1)")[0]
    h = p("highlight(a, 2)")[0]
    assert s.kind == "swap"
    assert h.kind == "highlight"


def test_if_else_end_block():
    src = """
if x > 0:
    print(x)
else:
    print(0)
end
""".strip()
    n = p(src)[0]
    assert n.kind == "if"
    assert n.data["cond"].kind == "binop"
    assert len(n.data["then"]) == 1
    assert len(n.data["else"]) == 1


def test_if_without_else():
    n = p("if true:\n    print(1)\nend")[0]
    assert n.kind == "if"
    assert n.data["else"] == []


def test_for_loop():
    n = p("for i from 0 to 5:\n    print(i)\nend")[0]
    assert n.kind == "for"
    assert n.data["var"] == "i"
    assert n.data["start"].data["value"] == 0
    assert n.data["stop"].data["value"] == 5


def test_while_loop():
    n = p("while x < 10:\n    x = x + 1\nend")[0]
    assert n.kind == "while"
    assert n.data["cond"].kind == "binop"
    assert len(n.data["body"]) == 1


def test_binop_precedence_multiplication_before_addition():
    n = p("x = 1 + 2 * 3")[0]
    expr = n.data["value"]
    assert expr.kind == "binop" and expr.data["op"] == "+"
    right = expr.data["right"]
    assert right.kind == "binop" and right.data["op"] == "*"


def test_parentheses_override_precedence():
    n = p("x = (1 + 2) * 3")[0]
    expr = n.data["value"]
    assert expr.kind == "binop" and expr.data["op"] == "*"
    left = expr.data["left"]
    assert left.kind == "binop" and left.data["op"] == "+"


def test_comparison_and_logical_precedence():
    n = p("x = a < 5 and b > 3")[0]
    expr = n.data["value"]
    assert expr.kind == "binop" and expr.data["op"] == "and"
    assert expr.data["left"].data["op"] == "<"
    assert expr.data["right"].data["op"] == ">"


def test_unary_minus_and_not():
    n = p("x = -5")[0]
    assert n.data["value"].kind in ("num", "unop")
    n2 = p("x = not true")[0]
    assert n2.data["value"].kind == "unop"
    assert n2.data["value"].data["op"] == "not"


def test_attr_access_expression():
    n = p("x = a.length")[0]
    expr = n.data["value"]
    assert expr.kind == "attr"
    assert expr.data["attr"] == "length"


def test_method_expression_in_assignment():
    n = p("x = m.get(\"key\")")[0]
    expr = n.data["value"]
    assert expr.kind == "method_expr"
    assert expr.data["method"] == "get"


def test_index_expression():
    n = p("x = a[2]")[0]
    expr = n.data["value"]
    assert expr.kind == "index"
    assert expr.data["name"] == "a"


def test_bool_and_null_literals():
    assert p("x = true")[0].data["value"].data["value"] is True
    assert p("x = false")[0].data["value"].data["value"] is False
    assert p("x = null")[0].data["value"].kind == "null"


def test_parse_error_missing_bracket():
    with pytest.raises(ParseError):
        p("array a = [1, 2, 3")


def test_parse_error_missing_end():
    with pytest.raises(ParseError):
        p("if true:\n    print(1)")


def test_parse_error_unexpected_token():
    with pytest.raises(ParseError):
        p("array = [1]")
