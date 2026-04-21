import random
import pytest
from visu.interpreter import run_source


def _eval_expr(expr):
    snapshots, error = run_source(f"x = {expr}")
    assert error is None, f"Error evaluating '{expr}': {error}"
    return snapshots[-1].variables["x"]


class TestArithmetic:
    @pytest.mark.parametrize("a", range(-20, 21))
    @pytest.mark.parametrize("b", range(-20, 21))
    def test_addition(self, a, b):
        assert _eval_expr(f"{a} + {b}") == a + b

    @pytest.mark.parametrize("a", range(-15, 16))
    @pytest.mark.parametrize("b", range(-15, 16))
    def test_subtraction(self, a, b):
        assert _eval_expr(f"{a} - {b}") == a - b

    @pytest.mark.parametrize("a", range(-10, 11))
    @pytest.mark.parametrize("b", range(-10, 11))
    def test_multiplication(self, a, b):
        assert _eval_expr(f"{a} * {b}") == a * b

    @pytest.mark.parametrize("a", range(-10, 11))
    @pytest.mark.parametrize("b", [x for x in range(-10, 11) if x != 0])
    def test_division(self, a, b):
        assert _eval_expr(f"{a} / {b}") == a / b

    @pytest.mark.parametrize("a", range(0, 30))
    @pytest.mark.parametrize("b", range(1, 10))
    def test_modulo(self, a, b):
        assert _eval_expr(f"{a} % {b}") == a % b


class TestComparison:
    OPS = [("==", lambda a, b: a == b),
           ("!=", lambda a, b: a != b),
           ("<", lambda a, b: a < b),
           (">", lambda a, b: a > b),
           ("<=", lambda a, b: a <= b),
           (">=", lambda a, b: a >= b)]

    @pytest.mark.parametrize("op,fn", OPS, ids=[o[0] for o in OPS])
    @pytest.mark.parametrize("a", range(-10, 11))
    @pytest.mark.parametrize("b", range(-10, 11))
    def test_comparison(self, op, fn, a, b):
        result = _eval_expr(f"{a} {op} {b}")
        assert result == fn(a, b), f"{a} {op} {b} = {result}, expected {fn(a, b)}"


class TestBoolean:
    BOOL_VALS = [("true", True), ("false", False)]

    @pytest.mark.parametrize("a_str,a_val", BOOL_VALS)
    @pytest.mark.parametrize("b_str,b_val", BOOL_VALS)
    def test_and(self, a_str, a_val, b_str, b_val):
        assert _eval_expr(f"{a_str} and {b_str}") == (a_val and b_val)

    @pytest.mark.parametrize("a_str,a_val", BOOL_VALS)
    @pytest.mark.parametrize("b_str,b_val", BOOL_VALS)
    def test_or(self, a_str, a_val, b_str, b_val):
        assert _eval_expr(f"{a_str} or {b_str}") == (a_val or b_val)

    @pytest.mark.parametrize("a_str,a_val", BOOL_VALS)
    def test_not(self, a_str, a_val):
        assert _eval_expr(f"not {a_str}") == (not a_val)


class TestPrecedence:
    @pytest.mark.parametrize("a,b,c", [
        (2, 3, 4), (1, 5, 2), (10, 0, 3), (7, 8, 1),
    ])
    def test_mul_before_add(self, a, b, c):
        assert _eval_expr(f"{a} + {b} * {c}") == a + b * c

    @pytest.mark.parametrize("a,b,c", [
        (2, 3, 4), (10, 2, 5), (8, 4, 2), (1, 1, 1),
    ])
    def test_parentheses(self, a, b, c):
        assert _eval_expr(f"({a} + {b}) * {c}") == (a + b) * c

    @pytest.mark.parametrize("seed", range(50))
    def test_complex_expression(self, seed):
        rng = random.Random(seed)
        a, b, c, d = [rng.randint(1, 10) for _ in range(4)]
        assert _eval_expr(f"({a} + {b}) * ({c} - {d})") == (a + b) * (c - d)


class TestStringExpressions:
    @pytest.mark.parametrize("s", [
        "hello", "world", "", "a b c", "123", "special!@#",
    ])
    def test_string_literal(self, s):
        assert _eval_expr(f'"{s}"') == s

    @pytest.mark.parametrize("a,b", [
        ("hello", " world"), ("", "abc"), ("abc", ""), ("a", "b"),
    ])
    def test_string_concat(self, a, b):
        assert _eval_expr(f'"{a}" + "{b}"') == a + b

    @pytest.mark.parametrize("a,b,eq", [
        ("a", "a", True), ("a", "b", False), ("", "", True),
    ])
    def test_string_equality(self, a, b, eq):
        assert _eval_expr(f'"{a}" == "{b}"') == eq


class TestNullExpressions:
    def test_null_literal(self):
        assert _eval_expr("null") is None

    def test_null_equals_null(self):
        assert _eval_expr("null == null") is True

    def test_null_not_equals_zero(self):
        assert _eval_expr("null != 0") is True


class TestArrayLiteralExpressions:
    @pytest.mark.parametrize("n", range(0, 20))
    def test_array_literal(self, n):
        vals = ", ".join(str(i) for i in range(n))
        result = _eval_expr(f"[{vals}]")
        assert result == list(range(n))

    @pytest.mark.parametrize("seed", range(30))
    def test_nested_array_literal(self, seed):
        rng = random.Random(seed)
        inner = [rng.randint(0, 10) for _ in range(3)]
        inner_str = ", ".join(str(v) for v in inner)
        result = _eval_expr(f"[[{inner_str}], [{inner_str}]]")
        assert result == [inner, inner]


class TestVariableExpressions:
    @pytest.mark.parametrize("val", list(range(-50, 51)))
    def test_variable_reassign(self, val):
        snapshots, error = run_source(f"x = 0\nx = {val}")
        assert error is None
        assert snapshots[-1].variables["x"] == val

    @pytest.mark.parametrize("seed", range(50))
    def test_chain_assignment(self, seed):
        rng = random.Random(seed)
        vals = [rng.randint(-100, 100) for _ in range(5)]
        lines = [f"x = {vals[0]}"]
        for v in vals[1:]:
            lines.append(f"x = x + {v}")
        snapshots, error = run_source("\n".join(lines))
        assert error is None
        assert snapshots[-1].variables["x"] == sum(vals)
