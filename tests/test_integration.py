from visu.interpreter.runtime import run_source


def values_of(struct):
    return [it.value for it in struct.items]


def test_bubble_sort_end_to_end():
    src = """
array a = [5, 2, 4, 1, 3]
for i from 0 to 5:
    for j from 0 to 4:
        if a[j] > a[j + 1]:
            swap(a, j, j + 1)
        end
    end
end
""".strip()
    snaps, err = run_source(src)
    assert err is None
    assert values_of(snaps[-1].structures["a"]) == [1, 2, 3, 4, 5]


def test_sum_with_while_loop():
    src = """
x = 0
i = 1
while i <= 10:
    x = x + i
    i = i + 1
end
print(x)
""".strip()
    snaps, err = run_source(src)
    assert err is None
    assert "55" in snaps[-1].output


def test_graph_neighbors_integration():
    src = """
graph g = directed
g.node("A")
g.node("B")
g.node("C")
g.edge("A", "B")
g.edge("A", "C")
print(g.node_count)
print(g.edge_count)
""".strip()
    snaps, err = run_source(src)
    assert err is None
    out = snaps[-1].output
    assert "3" in out and "2" in out


def test_map_counting_word_occurrences():
    src = """
map counts = []
counts.set("a", 0)
counts.set("a", counts.get("a") + 1)
counts.set("a", counts.get("a") + 1)
counts.set("b", 1)
print(counts.get("a"))
print(counts.get("b"))
""".strip()
    snaps, err = run_source(src)
    assert err is None
    out = snaps[-1].output
    assert "2" in out and "1" in out


def test_multiple_snapshots_generated_per_step():
    src = """
array a = [1, 2, 3]
a.push(4)
a.push(5)
a.pop()
""".strip()
    snaps, err = run_source(src)
    assert err is None
    assert len(snaps) >= 4
