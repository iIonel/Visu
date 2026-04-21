import random
import pytest
from visu.interpreter import run_source


def _final(src):
    snapshots, error = run_source(src)
    assert error is None, f"Unexpected error: {error}"
    return snapshots[-1]


class TestForLoop:
    @pytest.mark.parametrize("start,stop", [
        (0, n) for n in range(0, 30)
    ] + [
        (5, n) for n in range(5, 25)
    ] + [
        (n, 0) for n in range(0, 20)
    ])
    def test_for_range_sum(self, start, stop):
        src = f"total = 0\nfor i from {start} to {stop}:\n    total = total + i\nend"
        s = _final(src)
        step = 1 if stop >= start else -1
        expected = sum(range(start, stop, step))
        assert s.variables["total"] == expected

    @pytest.mark.parametrize("n", range(1, 30))
    def test_for_accumulates_correctly(self, n):
        src = f"array a = []\nfor i from 0 to {n}:\n    a.push(i)\nend"
        s = _final(src)
        assert [item.value for item in s.structures["a"].items] == list(range(n))

    @pytest.mark.parametrize("outer,inner", [
        (n, m) for n in range(1, 8) for m in range(1, 8)
    ])
    def test_nested_for(self, outer, inner):
        src = f"count = 0\nfor i from 0 to {outer}:\n    for j from 0 to {inner}:\n        count = count + 1\n    end\nend"
        s = _final(src)
        assert s.variables["count"] == outer * inner


class TestWhileLoop:
    @pytest.mark.parametrize("n", range(0, 30))
    def test_while_countdown(self, n):
        src = f"x = {n}\ncount = 0\nwhile x > 0:\n    x = x - 1\n    count = count + 1\nend"
        s = _final(src)
        assert s.variables["count"] == n
        assert s.variables["x"] == 0

    @pytest.mark.parametrize("n", range(1, 20))
    def test_while_collect(self, n):
        src = f"array a = []\ni = 0\nwhile i < {n}:\n    a.push(i)\n    i = i + 1\nend"
        s = _final(src)
        assert [item.value for item in s.structures["a"].items] == list(range(n))

    def test_while_false_never_executes(self):
        src = "x = 0\nwhile false:\n    x = 1\nend"
        s = _final(src)
        assert s.variables["x"] == 0


class TestIfElse:
    @pytest.mark.parametrize("val,expected", [
        (v, "pos" if v > 0 else ("zero" if v == 0 else "neg"))
        for v in range(-20, 21)
    ])
    def test_if_else_classification(self, val, expected):
        src = f"""\
x = {val}
if x > 0:
    result = "pos"
else:
    if x == 0:
        result = "zero"
    else:
        result = "neg"
    end
end
"""
        s = _final(src)
        assert s.variables["result"] == expected

    @pytest.mark.parametrize("a,b", [(a, b) for a in range(-5, 6) for b in range(-5, 6)])
    def test_if_max(self, a, b):
        src = f"if {a} > {b}:\n    m = {a}\nelse:\n    m = {b}\nend"
        s = _final(src)
        assert s.variables["m"] == max(a, b)

    @pytest.mark.parametrize("a,b", [(a, b) for a in range(-5, 6) for b in range(-5, 6)])
    def test_if_min(self, a, b):
        src = f"if {a} < {b}:\n    m = {a}\nelse:\n    m = {b}\nend"
        s = _final(src)
        assert s.variables["m"] == min(a, b)

    @pytest.mark.parametrize("n", range(-10, 11))
    def test_if_abs(self, n):
        src = f"x = {n}\nif x < 0:\n    x = 0 - x\nend"
        s = _final(src)
        assert s.variables["x"] == abs(n)

    @pytest.mark.parametrize("cond", [True, False])
    def test_if_true_false_literal(self, cond):
        cond_str = "true" if cond else "false"
        src = f"x = 0\nif {cond_str}:\n    x = 1\nend"
        s = _final(src)
        assert s.variables["x"] == (1 if cond else 0)


class TestNestedControlFlow:
    @pytest.mark.parametrize("n", range(1, 12))
    def test_fizzbuzz(self, n):
        src = f"""\
array result = []
for i from 1 to {n + 1}:
    if i % 3 == 0:
        result.push(0)
    else:
        result.push(i)
    end
end
"""
        s = _final(src)
        result = [item.value for item in s.structures["result"].items]
        expected = [0 if i % 3 == 0 else i for i in range(1, n + 1)]
        assert result == expected

    @pytest.mark.parametrize("n", range(2, 15))
    def test_collect_evens(self, n):
        vals = ", ".join(str(i) for i in range(n))
        src = f"""\
array a = [{vals}]
array evens = []
for i from 0 to a.length:
    if a[i] % 2 == 0:
        evens.push(a[i])
    end
end
"""
        s = _final(src)
        result = [item.value for item in s.structures["evens"].items]
        assert result == [i for i in range(n) if i % 2 == 0]

    @pytest.mark.parametrize("seed", range(30))
    def test_while_inside_for(self, seed):
        rng = random.Random(seed)
        n = rng.randint(1, 8)
        src = f"""\
total = 0
for i from 0 to {n}:
    j = i
    while j > 0:
        total = total + 1
        j = j - 1
    end
end
"""
        s = _final(src)
        expected = sum(range(n))
        assert s.variables["total"] == expected


class TestPrintOutput:
    @pytest.mark.parametrize("n", range(1, 20))
    def test_print_sequence(self, n):
        lines = []
        for i in range(n):
            lines.append(f"print({i})")
        snapshots, error = run_source("\n".join(lines))
        assert error is None
        output = snapshots[-1].output
        expected = "\n".join(str(i) for i in range(n))
        assert output == expected

    @pytest.mark.parametrize("val", [0, 1, -1, 42, 100, -100, 999])
    def test_print_single_value(self, val):
        snapshots, error = run_source(f"print({val})")
        assert error is None
        assert snapshots[-1].output == str(val)

    @pytest.mark.parametrize("vals", [
        (1, 2, 3),
        (0, 0, 0),
        (10, 20),
        (1,),
    ])
    def test_print_multiple_values(self, vals):
        args = ", ".join(str(v) for v in vals)
        snapshots, error = run_source(f"print({args})")
        assert error is None
        assert snapshots[-1].output == " ".join(str(v) for v in vals)

    @pytest.mark.parametrize("s", ["hello", "world", "", "test 123", "a b c"])
    def test_print_string(self, s):
        snapshots, error = run_source(f'print("{s}")')
        assert error is None
        assert snapshots[-1].output == s
