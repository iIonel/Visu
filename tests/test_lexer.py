import pytest

from visu.interpreter.errors import LexError
from visu.interpreter.lexer import tokenize


def kinds(src):
    return [t.kind for t in tokenize(src) if t.kind != "EOF"]


def values(src):
    return [t.value for t in tokenize(src) if t.kind not in ("EOF", "NEWLINE")]


def test_empty_source_has_only_eof():
    toks = tokenize("")
    assert len(toks) == 1
    assert toks[0].kind == "EOF"


def test_integer_and_float_numbers():
    toks = [t for t in tokenize("1 2.5 100") if t.kind == "NUMBER"]
    assert [t.value for t in toks] == [1, 2.5, 100]
    assert isinstance(toks[0].value, int)
    assert isinstance(toks[1].value, float)


def test_string_literals_single_and_double_quotes():
    toks = [t for t in tokenize('"hello" \'world\'') if t.kind == "STRING"]
    assert [t.value for t in toks] == ["hello", "world"]


def test_keywords_become_uppercase_tokens():
    ks = kinds("array stack queue deque list set map graph")
    assert ks == ["ARRAY", "STACK", "QUEUE", "DEQUE", "LIST", "SET", "MAP", "GRAPH"]


def test_control_flow_keywords():
    ks = kinds("if else end for from to while")
    assert ks == ["IF", "ELSE", "END", "FOR", "FROM", "TO", "WHILE"]


def test_boolean_and_null_keywords():
    ks = kinds("true false null")
    assert ks == ["TRUE", "FALSE", "NULL"]


def test_logical_keywords():
    ks = kinds("and or not")
    assert ks == ["AND", "OR", "NOT"]


def test_identifiers_distinct_from_keywords():
    toks = [t for t in tokenize("foo bar_baz count1") if t.kind == "IDENT"]
    assert [t.value for t in toks] == ["foo", "bar_baz", "count1"]


def test_single_char_operators():
    ks = kinds("+ - * / %")
    assert ks == ["OP"] * 5


def test_multi_char_operators():
    toks = [t for t in tokenize("== != <= >= < >") if t.kind == "OP"]
    assert [t.value for t in toks] == ["==", "!=", "<=", ">=", "<", ">"]


def test_arrow_token():
    toks = tokenize("->")
    assert toks[0].kind == "ARROW"


def test_assign_vs_equal():
    toks = [t for t in tokenize("x = 1\ny == 2")]
    assigns = [t for t in toks if t.kind == "ASSIGN"]
    ops = [t for t in toks if t.kind == "OP"]
    assert len(assigns) == 1
    assert ops[0].value == "=="


def test_brackets_and_punctuation():
    ks = kinds("( ) [ ] , : .")
    assert ks == ["LP", "RP", "LB", "RB", "COMMA", "COLON", "DOT"]


def test_comment_is_ignored():
    toks = tokenize("x = 1 # this is a comment\ny = 2")
    values_list = [t.value for t in toks if t.kind in ("IDENT", "NUMBER")]
    assert values_list == ["x", 1, "y", 2]


def test_newline_tokens_generated():
    toks = tokenize("a = 1\nb = 2\n")
    nl = [t for t in toks if t.kind == "NEWLINE"]
    assert len(nl) >= 2


def test_line_numbers_tracked():
    toks = tokenize("a = 1\nb = 2\nc = 3")
    idents = [t for t in toks if t.kind == "IDENT"]
    assert [t.line for t in idents] == [1, 2, 3]


def test_negative_number_after_assign():
    toks = [t for t in tokenize("x = -5") if t.kind == "NUMBER"]
    assert toks[0].value == -5


def test_subtraction_not_negative_after_ident():
    toks = tokenize("a - 5")
    kinds_list = [t.kind for t in toks]
    assert "OP" in kinds_list
    nums = [t for t in toks if t.kind == "NUMBER"]
    assert nums[0].value == 5


def test_negative_in_array_literal():
    toks = [t for t in tokenize("[-1, -2, 3]") if t.kind == "NUMBER"]
    assert [t.value for t in toks] == [-1, -2, 3]


def test_unterminated_string_raises_lex_error():
    with pytest.raises(LexError):
        tokenize('"oops')


def test_unexpected_character_raises_lex_error():
    with pytest.raises(LexError):
        tokenize("x = @")
