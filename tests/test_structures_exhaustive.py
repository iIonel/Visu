import random
import pytest
from visu.interpreter import run_source


def _final(src):
    snapshots, error = run_source(src)
    assert error is None, f"Unexpected error: {error}"
    return snapshots[-1]


def _values(snapshot, name):
    st = snapshot.structures[name]
    return [item.value for item in st.items]


def _map_pairs(snapshot, name):
    st = snapshot.structures[name]
    return [(e.key, e.value) for e in st.items]


def _graph_node_keys(snapshot, name):
    st = snapshot.structures[name]
    return [n.key for n in st.items]


def _graph_edges(snapshot, name):
    st = snapshot.structures[name]
    return [(e.src, e.dst, e.weight) for e in st.edges]


class TestArrayOperations:
    @pytest.mark.parametrize("size", range(0, 30))
    def test_array_creation(self, size):
        vals = ", ".join(str(i) for i in range(size))
        s = _final(f"array a = [{vals}]")
        assert _values(s, "a") == list(range(size))

    @pytest.mark.parametrize("n", range(1, 50))
    def test_array_push_sequence(self, n):
        lines = ["array a = []"]
        for i in range(n):
            lines.append(f"a.push({i})")
        s = _final("\n".join(lines))
        assert _values(s, "a") == list(range(n))

    @pytest.mark.parametrize("n", range(1, 40))
    def test_array_push_then_pop_all(self, n):
        lines = ["array a = []"]
        for i in range(n):
            lines.append(f"a.push({i})")
        for _ in range(n):
            lines.append("a.pop()")
        s = _final("\n".join(lines))
        assert _values(s, "a") == []

    @pytest.mark.parametrize("seed", range(50))
    def test_array_insert_random(self, seed):
        rng = random.Random(seed)
        expected = []
        lines = ["array a = []"]
        for i in range(10):
            idx = rng.randint(0, len(expected))
            expected.insert(idx, i)
            lines.append(f"a.insert({idx}, {i})")
        s = _final("\n".join(lines))
        assert _values(s, "a") == expected

    @pytest.mark.parametrize("seed", range(40))
    def test_array_remove_random(self, seed):
        rng = random.Random(seed)
        size = rng.randint(5, 15)
        expected = list(range(size))
        lines = [f"array a = [{', '.join(str(v) for v in expected)}]"]
        for _ in range(min(5, size)):
            if not expected:
                break
            idx = rng.randint(0, len(expected) - 1)
            expected.pop(idx)
            lines.append(f"a.remove({idx})")
        s = _final("\n".join(lines))
        assert _values(s, "a") == expected

    @pytest.mark.parametrize("size", range(2, 25))
    def test_array_swap_first_last(self, size):
        arr = list(range(size))
        vals = ", ".join(str(v) for v in arr)
        s = _final(f"array a = [{vals}]\nswap(a, 0, {size - 1})")
        result = _values(s, "a")
        assert result[0] == size - 1
        assert result[-1] == 0

    @pytest.mark.parametrize("seed", range(50))
    def test_array_index_assign(self, seed):
        rng = random.Random(seed)
        size = rng.randint(1, 20)
        arr = list(range(size))
        lines = [f"array a = [{', '.join(str(v) for v in arr)}]"]
        idx = rng.randint(0, size - 1)
        new_val = rng.randint(100, 200)
        arr[idx] = new_val
        lines.append(f"a[{idx}] = {new_val}")
        s = _final("\n".join(lines))
        assert _values(s, "a") == arr

    @pytest.mark.parametrize("n", range(1, 30))
    def test_array_length(self, n):
        vals = ", ".join(str(i) for i in range(n))
        s = _final(f"array a = [{vals}]\nx = a.length")
        assert s.variables["x"] == n


class TestStackOperations:
    @pytest.mark.parametrize("n", range(1, 60))
    def test_stack_push_pop_lifo(self, n):
        lines = ["stack s = []", "array order = []"]
        for i in range(n):
            lines.append(f"s.push({i})")
        for _ in range(n):
            lines.append(f"order.push(s[s.length - 1])")
            lines.append("s.pop()")
        s = _final("\n".join(lines))
        assert _values(s, "order") == list(range(n - 1, -1, -1))
        assert _values(s, "s") == []

    @pytest.mark.parametrize("seed", range(60))
    def test_stack_interleaved_push_pop(self, seed):
        rng = random.Random(seed)
        stack = []
        lines = ["stack s = []"]
        for _ in range(20):
            if not stack or rng.random() < 0.6:
                v = rng.randint(0, 100)
                stack.append(v)
                lines.append(f"s.push({v})")
            else:
                stack.pop()
                lines.append("s.pop()")
        s = _final("\n".join(lines))
        assert _values(s, "s") == stack


class TestQueueOperations:
    @pytest.mark.parametrize("n", range(1, 60))
    def test_queue_enqueue_dequeue_fifo(self, n):
        lines = ["queue q = []", "array order = []"]
        for i in range(n):
            lines.append(f"q.enqueue({i})")
        for _ in range(n):
            lines.append("order.push(q[0])")
            lines.append("q.dequeue()")
        s = _final("\n".join(lines))
        assert _values(s, "order") == list(range(n))
        assert _values(s, "q") == []

    @pytest.mark.parametrize("seed", range(60))
    def test_queue_interleaved(self, seed):
        rng = random.Random(seed)
        queue = []
        lines = ["queue q = []"]
        for _ in range(20):
            if not queue or rng.random() < 0.6:
                v = rng.randint(0, 100)
                queue.append(v)
                lines.append(f"q.enqueue({v})")
            else:
                queue.pop(0)
                lines.append("q.dequeue()")
        s = _final("\n".join(lines))
        assert _values(s, "q") == queue


class TestDequeOperations:
    @pytest.mark.parametrize("n", range(1, 40))
    def test_deque_push_front_sequence(self, n):
        lines = ["deque d = []"]
        for i in range(n):
            lines.append(f"d.push_front({i})")
        s = _final("\n".join(lines))
        assert _values(s, "d") == list(range(n - 1, -1, -1))

    @pytest.mark.parametrize("n", range(1, 40))
    def test_deque_push_back_sequence(self, n):
        lines = ["deque d = []"]
        for i in range(n):
            lines.append(f"d.push_back({i})")
        s = _final("\n".join(lines))
        assert _values(s, "d") == list(range(n))

    @pytest.mark.parametrize("seed", range(80))
    def test_deque_random_ops(self, seed):
        rng = random.Random(seed)
        deque = []
        lines = ["deque d = []"]
        for _ in range(15):
            op = rng.choice(["pf", "pb", "xf", "xb"])
            if op == "pf":
                v = rng.randint(0, 100)
                deque.insert(0, v)
                lines.append(f"d.push_front({v})")
            elif op == "pb":
                v = rng.randint(0, 100)
                deque.append(v)
                lines.append(f"d.push_back({v})")
            elif op == "xf" and deque:
                deque.pop(0)
                lines.append("d.pop_front()")
            elif op == "xb" and deque:
                deque.pop()
                lines.append("d.pop_back()")
        s = _final("\n".join(lines))
        assert _values(s, "d") == deque


class TestLinkedListOperations:
    @pytest.mark.parametrize("n", range(1, 40))
    def test_list_append_sequence(self, n):
        lines = ["list l = []"]
        for i in range(n):
            lines.append(f"l.append({i})")
        s = _final("\n".join(lines))
        assert _values(s, "l") == list(range(n))

    @pytest.mark.parametrize("n", range(1, 40))
    def test_list_prepend_sequence(self, n):
        lines = ["list l = []"]
        for i in range(n):
            lines.append(f"l.prepend({i})")
        s = _final("\n".join(lines))
        assert _values(s, "l") == list(range(n - 1, -1, -1))

    @pytest.mark.parametrize("seed", range(60))
    def test_list_mixed_append_prepend(self, seed):
        rng = random.Random(seed)
        lst = []
        lines = ["list l = []"]
        for _ in range(15):
            v = rng.randint(0, 100)
            if rng.random() < 0.5:
                lst.append(v)
                lines.append(f"l.append({v})")
            else:
                lst.insert(0, v)
                lines.append(f"l.prepend({v})")
        s = _final("\n".join(lines))
        assert _values(s, "l") == lst

    @pytest.mark.parametrize("size", range(1, 25))
    def test_list_remove_first(self, size):
        vals = list(range(size))
        src_vals = ", ".join(str(v) for v in vals)
        s = _final(f"list l = [{src_vals}]\nl.remove(0)")
        assert _values(s, "l") == vals[1:]

    @pytest.mark.parametrize("size", range(1, 25))
    def test_list_remove_last(self, size):
        vals = list(range(size))
        src_vals = ", ".join(str(v) for v in vals)
        s = _final(f"list l = [{src_vals}]\nl.remove({size - 1})")
        assert _values(s, "l") == vals[:-1]


class TestSetOperations:
    @pytest.mark.parametrize("n", range(1, 40))
    def test_set_add_unique(self, n):
        lines = ["set u = []"]
        for i in range(n):
            lines.append(f"u.add({i})")
        s = _final("\n".join(lines))
        assert sorted(_values(s, "u")) == list(range(n))

    @pytest.mark.parametrize("n", range(1, 30))
    def test_set_add_duplicates_ignored(self, n):
        lines = ["set u = []"]
        for i in range(n):
            lines.append(f"u.add({i})")
            lines.append(f"u.add({i})")
        s = _final("\n".join(lines))
        assert len(_values(s, "u")) == n

    @pytest.mark.parametrize("seed", range(60))
    def test_set_add_remove(self, seed):
        rng = random.Random(seed)
        s_set = set()
        lines = ["set u = []"]
        for _ in range(15):
            v = rng.randint(0, 10)
            if rng.random() < 0.7 or v not in s_set:
                s_set.add(v)
                lines.append(f"u.add({v})")
            elif v in s_set:
                s_set.discard(v)
                lines.append(f"u.remove({v})")
        s = _final("\n".join(lines))
        assert sorted(_values(s, "u")) == sorted(s_set)

    @pytest.mark.parametrize("seed", range(50))
    def test_set_contains(self, seed):
        rng = random.Random(seed)
        present = set(rng.sample(range(20), rng.randint(1, 10)))
        lines = ["set u = []"]
        for v in present:
            lines.append(f"u.add({v})")
        target = rng.randint(0, 19)
        lines.append(f"x = u.contains({target})")
        s = _final("\n".join(lines))
        assert s.variables["x"] == (target in present)

    @pytest.mark.parametrize("n", range(0, 30))
    def test_set_size(self, n):
        lines = ["set u = []"]
        for i in range(n):
            lines.append(f"u.add({i})")
        lines.append("x = u.size")
        s = _final("\n".join(lines))
        assert s.variables["x"] == n

    @pytest.mark.parametrize("vals", [
        [1, 2, 2, 3],
        [5, 5, 5],
        [1, 2, 3, 4, 5],
        [10, 10, 20, 20, 30, 30],
    ])
    def test_set_init_dedup(self, vals):
        src_vals = ", ".join(str(v) for v in vals)
        s = _final(f"set u = [{src_vals}]")
        result = _values(s, "u")
        assert sorted(result) == sorted(set(vals))


class TestMapOperations:
    @pytest.mark.parametrize("n", range(1, 50))
    def test_map_set_sequence(self, n):
        lines = ["map m = []"]
        for i in range(n):
            lines.append(f'm.set("{i}", {i * 10})')
        s = _final("\n".join(lines))
        pairs = _map_pairs(s, "m")
        assert len(pairs) == n
        for k, v in pairs:
            assert v == int(k) * 10

    @pytest.mark.parametrize("n", range(1, 30))
    def test_map_overwrite(self, n):
        lines = ["map m = []"]
        lines.append(f'm.set("key", 0)')
        for i in range(1, n + 1):
            lines.append(f'm.set("key", {i})')
        s = _final("\n".join(lines))
        pairs = _map_pairs(s, "m")
        assert len(pairs) == 1
        assert pairs[0] == ("key", n)

    @pytest.mark.parametrize("seed", range(50))
    def test_map_get(self, seed):
        rng = random.Random(seed)
        n = rng.randint(1, 15)
        lines = ["map m = []"]
        expected = {}
        for i in range(n):
            k = f"k{i}"
            v = rng.randint(0, 100)
            expected[k] = v
            lines.append(f'm.set("{k}", {v})')
        target_key = f"k{rng.randint(0, n - 1)}"
        lines.append(f'x = m.get("{target_key}")')
        s = _final("\n".join(lines))
        assert s.variables["x"] == expected[target_key]

    @pytest.mark.parametrize("seed", range(50))
    def test_map_has(self, seed):
        rng = random.Random(seed)
        n = rng.randint(1, 10)
        lines = ["map m = []"]
        keys = set()
        for i in range(n):
            k = f"k{i}"
            keys.add(k)
            lines.append(f'm.set("{k}", {i})')
        target = f"k{rng.randint(0, 15)}"
        lines.append(f'x = m.has("{target}")')
        s = _final("\n".join(lines))
        assert s.variables["x"] == (target in keys)

    @pytest.mark.parametrize("seed", range(40))
    def test_map_remove(self, seed):
        rng = random.Random(seed)
        n = rng.randint(2, 10)
        d = {}
        lines = ["map m = []"]
        for i in range(n):
            d[f"k{i}"] = i
            lines.append(f'm.set("k{i}", {i})')
        to_remove = f"k{rng.randint(0, n - 1)}"
        del d[to_remove]
        lines.append(f'm.remove("{to_remove}")')
        s = _final("\n".join(lines))
        pairs = _map_pairs(s, "m")
        assert len(pairs) == len(d)

    @pytest.mark.parametrize("n", range(0, 30))
    def test_map_size(self, n):
        lines = ["map m = []"]
        for i in range(n):
            lines.append(f'm.set("k{i}", {i})')
        lines.append("x = m.size")
        s = _final("\n".join(lines))
        assert s.variables["x"] == n


class TestGraphOperations:
    @pytest.mark.parametrize("n", range(1, 40))
    def test_graph_add_nodes(self, n):
        lines = ["graph g = directed"]
        for i in range(n):
            lines.append(f'g.node("{i}")')
        s = _final("\n".join(lines))
        keys = _graph_node_keys(s, "g")
        assert len(keys) == n

    @pytest.mark.parametrize("n", range(2, 25))
    def test_graph_chain_edges(self, n):
        lines = ["graph g = directed"]
        for i in range(n):
            lines.append(f'g.node("{i}")')
        for i in range(n - 1):
            lines.append(f'g.edge("{i}", "{i + 1}")')
        s = _final("\n".join(lines))
        edges = _graph_edges(s, "g")
        assert len(edges) == n - 1

    @pytest.mark.parametrize("n", range(2, 20))
    def test_graph_complete(self, n):
        lines = ["graph g = directed"]
        for i in range(n):
            lines.append(f'g.node("{i}")')
        expected_edges = 0
        for i in range(n):
            for j in range(n):
                if i != j:
                    lines.append(f'g.edge("{i}", "{j}")')
                    expected_edges += 1
        s = _final("\n".join(lines))
        assert len(_graph_edges(s, "g")) == expected_edges

    @pytest.mark.parametrize("directed", [True, False])
    @pytest.mark.parametrize("n", range(2, 15))
    def test_graph_direction(self, directed, n):
        d = "directed" if directed else "undirected"
        lines = [f"graph g = {d}"]
        for i in range(n):
            lines.append(f'g.node("{i}")')
        lines.append('g.edge("0", "1")')
        lines.append('x = g.has_edge("0", "1")')
        lines.append('y = g.has_edge("1", "0")')
        s = _final("\n".join(lines))
        assert s.variables["x"] is True
        if directed:
            assert s.variables["y"] is False
        else:
            assert s.variables["y"] is True

    @pytest.mark.parametrize("seed", range(40))
    def test_graph_remove_node(self, seed):
        rng = random.Random(seed)
        n = rng.randint(3, 10)
        lines = ["graph g = directed"]
        for i in range(n):
            lines.append(f'g.node("{i}")')
        for i in range(n - 1):
            lines.append(f'g.edge("{i}", "{i + 1}")')
        to_remove = str(rng.randint(0, n - 1))
        lines.append(f'g.remove_node("{to_remove}")')
        s = _final("\n".join(lines))
        keys = _graph_node_keys(s, "g")
        assert to_remove not in keys
        for e in _graph_edges(s, "g"):
            assert e[0] != to_remove and e[1] != to_remove

    @pytest.mark.parametrize("seed", range(40))
    def test_graph_neighbors(self, seed):
        rng = random.Random(seed)
        n = rng.randint(3, 8)
        lines = ["graph g = directed"]
        for i in range(n):
            lines.append(f'g.node("{i}")')
        adj = {str(i): [] for i in range(n)}
        for i in range(n - 1):
            adj[str(i)].append(str(i + 1))
            lines.append(f'g.edge("{i}", "{i + 1}")')
        target = str(rng.randint(0, n - 2))
        lines.append(f'x = g.neighbors("{target}")')
        s = _final("\n".join(lines))
        assert s.variables["x"] == adj[target]

    @pytest.mark.parametrize("seed", range(30))
    def test_graph_weighted_edges(self, seed):
        rng = random.Random(seed)
        lines = ["graph g = directed"]
        lines.append('g.node("A")')
        lines.append('g.node("B")')
        w = rng.randint(1, 100)
        lines.append(f'g.edge("A", "B", {w})')
        s = _final("\n".join(lines))
        edges = _graph_edges(s, "g")
        assert len(edges) == 1
        assert edges[0] == ("A", "B", w)

    @pytest.mark.parametrize("n", range(1, 20))
    def test_graph_node_count(self, n):
        lines = ["graph g = directed"]
        for i in range(n):
            lines.append(f'g.node("{i}")')
        lines.append("x = g.node_count")
        s = _final("\n".join(lines))
        assert s.variables["x"] == n

    @pytest.mark.parametrize("n", range(2, 15))
    def test_graph_edge_count(self, n):
        lines = ["graph g = directed"]
        for i in range(n):
            lines.append(f'g.node("{i}")')
        for i in range(n - 1):
            lines.append(f'g.edge("{i}", "{i + 1}")')
        lines.append("x = g.edge_count")
        s = _final("\n".join(lines))
        assert s.variables["x"] == n - 1

    @pytest.mark.parametrize("seed", range(30))
    def test_graph_set_value(self, seed):
        rng = random.Random(seed)
        v = rng.randint(0, 1000)
        s = _final(f'graph g = directed\ng.node("X", 0)\ng.set_value("X", {v})\nx = g.get_value("X")')
        assert s.variables["x"] == v

    @pytest.mark.parametrize("seed", range(30))
    def test_graph_remove_edge(self, seed):
        rng = random.Random(seed)
        n = rng.randint(3, 8)
        lines = ["graph g = directed"]
        for i in range(n):
            lines.append(f'g.node("{i}")')
        edge_pairs = []
        for i in range(n - 1):
            lines.append(f'g.edge("{i}", "{i + 1}")')
            edge_pairs.append((str(i), str(i + 1)))
        idx = rng.randint(0, len(edge_pairs) - 1)
        src, dst = edge_pairs[idx]
        lines.append(f'g.remove_edge("{src}", "{dst}")')
        s = _final("\n".join(lines))
        assert len(_graph_edges(s, "g")) == len(edge_pairs) - 1


class TestMultipleStructures:
    @pytest.mark.parametrize("seed", range(40))
    def test_array_and_stack(self, seed):
        rng = random.Random(seed)
        n = rng.randint(1, 10)
        lines = ["array a = []", "stack s = []"]
        for i in range(n):
            lines.append(f"a.push({i})")
            lines.append(f"s.push({i})")
        s = _final("\n".join(lines))
        assert _values(s, "a") == list(range(n))
        assert _values(s, "s") == list(range(n))

    @pytest.mark.parametrize("seed", range(40))
    def test_three_structures(self, seed):
        rng = random.Random(seed)
        n = rng.randint(1, 8)
        lines = ["array a = []", "queue q = []", "set u = []"]
        for i in range(n):
            lines.append(f"a.push({i})")
            lines.append(f"q.enqueue({i})")
            lines.append(f"u.add({i})")
        s = _final("\n".join(lines))
        assert _values(s, "a") == list(range(n))
        assert _values(s, "q") == list(range(n))
        assert sorted(_values(s, "u")) == list(range(n))
