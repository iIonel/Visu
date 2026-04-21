"""Regression tests for DoS-hardening limits (runtime.py).

Monkeypatches MAX_ITEMS_PER_STRUCTURE to a small value so tests run quickly
without generating megabyte-scale snapshot state.
"""

import pytest

from visu.interpreter.runtime import Interpreter, run_source


@pytest.fixture
def small_cap(monkeypatch):
    monkeypatch.setattr(Interpreter, "MAX_ITEMS_PER_STRUCTURE", 20)
    return 20


def test_max_items_blocks_literal(small_cap):
    lit = ", ".join(str(i) for i in range(small_cap + 5))
    snaps, err = run_source(f"array a = [{lit}]")
    assert err is not None
    assert "max item count" in err.lower()


def test_max_items_blocks_array_push(small_cap):
    src = (
        "array a = []\n"
        "i = 0\n"
        f"while i <= {small_cap + 5}:\n"
        "    a.push(i)\n"
        "    i = i + 1\n"
        "end\n"
    )
    snaps, err = run_source(src)
    assert err is not None
    assert "max item count" in err.lower()


def test_max_items_blocks_insert(small_cap):
    lit = ", ".join(str(i) for i in range(small_cap))
    src = f"array a = [{lit}]\na.insert(0, 999)"
    snaps, err = run_source(src)
    assert err is not None
    assert "max item count" in err.lower()


def test_max_items_blocks_deque_push_front(small_cap):
    src = (
        "deque d = []\n"
        "i = 0\n"
        f"while i < {small_cap}:\n"
        "    d.push_back(i)\n"
        "    i = i + 1\n"
        "end\n"
        "d.push_front(-1)\n"
    )
    snaps, err = run_source(src)
    assert err is not None
    assert "max item count" in err.lower()


def test_max_items_blocks_queue_enqueue(small_cap):
    src = (
        "queue q = []\n"
        "i = 0\n"
        f"while i <= {small_cap + 5}:\n"
        "    q.enqueue(i)\n"
        "    i = i + 1\n"
        "end\n"
    )
    snaps, err = run_source(src)
    assert err is not None
    assert "max item count" in err.lower()


def test_max_items_blocks_list_append(small_cap):
    src = (
        "list l = []\n"
        "i = 0\n"
        f"while i <= {small_cap + 5}:\n"
        "    l.append(i)\n"
        "    i = i + 1\n"
        "end\n"
    )
    snaps, err = run_source(src)
    assert err is not None
    assert "max item count" in err.lower()


def test_max_items_blocks_set_add(small_cap):
    src = (
        "set s = []\n"
        "i = 0\n"
        f"while i <= {small_cap + 5}:\n"
        "    s.add(i)\n"
        "    i = i + 1\n"
        "end\n"
    )
    snaps, err = run_source(src)
    assert err is not None
    assert "max item count" in err.lower()


def test_max_items_blocks_map_set(small_cap):
    src = (
        "map m = []\n"
        "i = 0\n"
        f"while i <= {small_cap + 5}:\n"
        "    m.set(i, i)\n"
        "    i = i + 1\n"
        "end\n"
    )
    snaps, err = run_source(src)
    assert err is not None
    assert "max item count" in err.lower()


def test_max_items_blocks_graph_nodes(small_cap):
    src = (
        "graph g = directed\n"
        "i = 0\n"
        f"while i <= {small_cap + 5}:\n"
        "    g.node(i)\n"
        "    i = i + 1\n"
        "end\n"
    )
    snaps, err = run_source(src)
    assert err is not None
    assert "max item count" in err.lower()


def test_max_edges_blocks_graph_edge(monkeypatch):
    monkeypatch.setattr(Interpreter, "MAX_ITEMS_PER_STRUCTURE", 3)
    src = """
graph g = directed
g.node("A")
g.node("B")
g.node("C")
g.edge("A", "B")
g.edge("B", "C")
g.edge("A", "C")
g.edge("C", "A")
""".strip()
    snaps, err = run_source(src)
    assert err is not None
    assert "max edge count" in err.lower()


def test_within_limit_runs_fine(small_cap):
    lit = ", ".join(str(i) for i in range(small_cap - 1))
    snaps, err = run_source(f"array a = [{lit}]")
    assert err is None
    assert len(snaps[-1].structures["a"].items) == small_cap - 1


def test_message_truncation_applied():
    big_list = "[" + ", ".join(str(i) for i in range(2000)) + "]"
    src = f"x = {big_list}\nprint(x)"
    snaps, err = run_source(src)
    assert err is None
    for snap in snaps:
        assert len(snap.message) <= Interpreter.MAX_MESSAGE_CHARS


def test_message_truncation_marker():
    big_list = "[" + ", ".join(str(i) for i in range(2000)) + "]"
    snaps, err = run_source(f"x = {big_list}")
    assert err is None
    long_msgs = [s for s in snaps if len(s.message) == Interpreter.MAX_MESSAGE_CHARS]
    assert long_msgs, "expected at least one truncated message"
    assert long_msgs[0].message.endswith("…")


def test_short_messages_not_truncated():
    snaps, err = run_source("array a = [1, 2, 3]\na.push(4)")
    assert err is None
    for snap in snaps:
        assert "…" not in snap.message


def test_existing_programs_still_work():
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
    final = [it.value for it in snaps[-1].structures["a"].items]
    assert final == [1, 2, 3, 4, 5]
