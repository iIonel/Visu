import random
import pytest
from visu.interpreter import run_source


def _final(src):
    snapshots, error = run_source(src)
    assert error is None, f"Unexpected error: {error}"
    return snapshots[-1]


class TestEmptyStructures:
    @pytest.mark.parametrize("kind", ["array", "stack", "queue", "deque", "list", "set"])
    def test_empty_creation(self, kind):
        s = _final(f"{kind} x = []")
        assert len(s.structures["x"].items) == 0

    @pytest.mark.parametrize("kind", ["array", "stack", "queue", "deque", "list", "set"])
    def test_empty_length(self, kind):
        s = _final(f"{kind} x = []\nn = x.length")
        assert s.variables["n"] == 0

    def test_empty_map(self):
        s = _final("map m = []\nn = m.size")
        assert s.variables["n"] == 0

    def test_empty_graph(self):
        s = _final("graph g = directed\nn = g.node_count\ne = g.edge_count")
        assert s.variables["n"] == 0
        assert s.variables["e"] == 0


class TestSingleElement:
    @pytest.mark.parametrize("kind", ["array", "stack", "queue", "deque", "list"])
    @pytest.mark.parametrize("val", [-100, -1, 0, 1, 100])
    def test_single_element(self, kind, val):
        s = _final(f"{kind} x = [{val}]")
        assert s.structures["x"].items[0].value == val

    @pytest.mark.parametrize("val", [-100, -1, 0, 1, 100])
    def test_single_set_element(self, val):
        s = _final(f"set u = [{val}]")
        assert s.structures["u"].items[0].value == val


class TestBoundaryValues:
    @pytest.mark.parametrize("val", [0, -0, 0.0, -0.0])
    def test_zero_values(self, val):
        s = _final(f"x = {val}")
        assert s.variables["x"] == 0

    @pytest.mark.parametrize("val", [999999, -999999, 123456789])
    def test_large_numbers(self, val):
        s = _final(f"x = {val}")
        assert s.variables["x"] == val

    @pytest.mark.parametrize("val", [0.1, 0.01, 0.001, 3.14159, 2.71828])
    def test_float_values(self, val):
        s = _final(f"x = {val}")
        assert abs(s.variables["x"] - val) < 1e-10

    @pytest.mark.parametrize("n", range(0, 20))
    def test_nested_arrays(self, n):
        inner = ", ".join(str(i) for i in range(n))
        s = _final(f"x = [[{inner}]]")
        assert s.variables["x"] == [list(range(n))]


class TestStringEdgeCases:
    @pytest.mark.parametrize("s", [
        "", " ", "  ", "a", "ab", "abc",
        "hello world", "123", "!@#$%",
        "a b c d e f", "newline",
    ])
    def test_string_values(self, s):
        result = _final(f'x = "{s}"')
        assert result.variables["x"] == s

    @pytest.mark.parametrize("n", range(1, 20))
    def test_repeated_string(self, n):
        s = "a" * n
        result = _final(f'x = "{s}"')
        assert result.variables["x"] == s


class TestMapEdgeCases:
    @pytest.mark.parametrize("n", range(1, 30))
    def test_map_sequential_keys(self, n):
        lines = ["map m = []"]
        for i in range(n):
            lines.append(f'm.set("{i}", {i})')
        lines.append("x = m.size")
        s = _final("\n".join(lines))
        assert s.variables["x"] == n

    @pytest.mark.parametrize("seed", range(50))
    def test_map_overwrite_keeps_size(self, seed):
        rng = random.Random(seed)
        lines = ["map m = []"]
        keys = [f"k{i}" for i in range(5)]
        for k in keys:
            lines.append(f'm.set("{k}", 0)')
        for _ in range(10):
            k = rng.choice(keys)
            v = rng.randint(0, 100)
            lines.append(f'm.set("{k}", {v})')
        lines.append("x = m.size")
        s = _final("\n".join(lines))
        assert s.variables["x"] == len(keys)

    @pytest.mark.parametrize("key_type", ["int", "str", "bool"])
    def test_map_different_key_types(self, key_type):
        if key_type == "int":
            src = 'map m = []\nm.set(42, "val")\nx = m.get(42)'
        elif key_type == "str":
            src = 'map m = []\nm.set("key", "val")\nx = m.get("key")'
        else:
            src = 'map m = []\nm.set(true, "val")\nx = m.get(true)'
        s = _final(src)
        assert s.variables["x"] == "val"


class TestGraphEdgeCases:
    @pytest.mark.parametrize("n", range(1, 15))
    def test_graph_isolated_nodes(self, n):
        lines = ["graph g = directed"]
        for i in range(n):
            lines.append(f'g.node("{i}")')
        lines.append("x = g.node_count")
        lines.append("y = g.edge_count")
        s = _final("\n".join(lines))
        assert s.variables["x"] == n
        assert s.variables["y"] == 0

    @pytest.mark.parametrize("directed", [True, False])
    def test_single_edge(self, directed):
        d = "directed" if directed else "undirected"
        src = f"""\
graph g = {d}
g.node("A")
g.node("B")
g.edge("A", "B", 5)
x = g.has_edge("A", "B")
"""
        s = _final(src)
        assert s.variables["x"] is True

    @pytest.mark.parametrize("n", range(2, 10))
    def test_graph_star_topology(self, n):
        lines = ["graph g = undirected"]
        for i in range(n):
            lines.append(f'g.node("{i}")')
        for i in range(1, n):
            lines.append(f'g.edge("0", "{i}")')
        lines.append('neigh = g.neighbors("0")')
        lines.append("x = neigh.length")
        s = _final("\n".join(lines))
        assert s.variables["x"] == n - 1

    @pytest.mark.parametrize("key", ["A", "hello", "123", "x y z"])
    def test_graph_string_keys(self, key):
        src = f'graph g = directed\ng.node("{key}")\nx = g.has_node("{key}")'
        s = _final(src)
        assert s.variables["x"] is True

    @pytest.mark.parametrize("val", [0, 42, "hello", True, None])
    def test_graph_node_value_types(self, val):
        if isinstance(val, str):
            src = f'graph g = directed\ng.node("A", "{val}")\nx = g.get_value("A")'
        elif val is True:
            src = f'graph g = directed\ng.node("A", true)\nx = g.get_value("A")'
        elif val is None:
            src = f'graph g = directed\ng.node("A")\nx = g.get_value("A")'
        else:
            src = f'graph g = directed\ng.node("A", {val})\nx = g.get_value("A")'
        s = _final(src)
        assert s.variables["x"] == val


class TestSetEdgeCases:
    @pytest.mark.parametrize("seed", range(50))
    def test_set_add_remove_add(self, seed):
        rng = random.Random(seed)
        vals = [rng.randint(0, 5) for _ in range(5)]
        lines = ["set u = []"]
        current = set()
        for v in vals:
            current.add(v)
            lines.append(f"u.add({v})")
        to_remove = list(current)[:2] if len(current) >= 2 else list(current)
        for v in to_remove:
            current.discard(v)
            lines.append(f"u.remove({v})")
        for v in to_remove:
            current.add(v)
            lines.append(f"u.add({v})")
        s = _final("\n".join(lines))
        result = sorted(item.value for item in s.structures["u"].items)
        assert result == sorted(current)


class TestDequeEdgeCases:
    @pytest.mark.parametrize("seed", range(50))
    def test_deque_alternating(self, seed):
        rng = random.Random(seed)
        expected = []
        lines = ["deque d = []"]
        for i in range(10):
            v = rng.randint(0, 100)
            if i % 2 == 0:
                expected.append(v)
                lines.append(f"d.push_back({v})")
            else:
                expected.insert(0, v)
                lines.append(f"d.push_front({v})")
        s = _final("\n".join(lines))
        assert [item.value for item in s.structures["d"].items] == expected


class TestComplexAlgorithms:
    @pytest.mark.parametrize("seed", range(30))
    def test_word_frequency(self, seed):
        rng = random.Random(seed)
        words = [rng.choice(["a", "b", "c", "d", "e"]) for _ in range(rng.randint(3, 15))]
        vals = ", ".join(f'"{w}"' for w in words)
        src = f"""\
array words = [{vals}]
map counts = []
for i from 0 to words.length:
    w = words[i]
    if counts.has(w):
        counts.set(w, counts.get(w) + 1)
    else:
        counts.set(w, 1)
    end
end
"""
        s = _final(src)
        from collections import Counter
        expected = Counter(words)
        for entry in s.structures["counts"].items:
            assert entry.value == expected[entry.key]

    @pytest.mark.parametrize("seed", range(30))
    def test_stack_reverse(self, seed):
        rng = random.Random(seed)
        n = rng.randint(1, 15)
        arr = [rng.randint(0, 100) for _ in range(n)]
        vals = ", ".join(str(v) for v in arr)
        src = f"""\
array a = [{vals}]
stack s = []
for i from 0 to a.length:
    s.push(a[i])
end
array reversed = []
while s.length > 0:
    reversed.push(s[s.length - 1])
    s.pop()
end
"""
        s = _final(src)
        result = [item.value for item in s.structures["reversed"].items]
        assert result == list(reversed(arr))

    @pytest.mark.parametrize("seed", range(30))
    def test_queue_round_robin(self, seed):
        rng = random.Random(seed)
        n = rng.randint(2, 8)
        src_lines = ["queue q = []"]
        for i in range(n):
            src_lines.append(f"q.enqueue({i})")
        src_lines.append("array order = []")
        src_lines.append("rounds = 0")
        src_lines.append(f"while rounds < {n}:")
        src_lines.append("    order.push(q[0])")
        src_lines.append("    q.dequeue()")
        src_lines.append("    rounds = rounds + 1")
        src_lines.append("end")
        s = _final("\n".join(src_lines))
        result = [item.value for item in s.structures["order"].items]
        assert result == list(range(n))
