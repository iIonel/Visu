import pytest

from visu.interpreter.runtime import Interpreter, run_source


def values_of(struct):
    return [it.value for it in struct.items]


def last(src):
    snaps, err = run_source(src)
    assert err is None, f"unexpected runtime error: {err}"
    assert snaps, "expected at least one snapshot"
    return snaps[-1]


def test_array_declaration_and_push():
    snap = last("array a = [1, 2, 3]\na.push(4)")
    assert values_of(snap.structures["a"]) == [1, 2, 3, 4]


def test_array_pop_and_length():
    snap = last("array a = [1, 2, 3]\na.pop()\nprint(a.length)")
    assert values_of(snap.structures["a"]) == [1, 2]
    assert snap.output.strip().endswith("2")


def test_array_index_read_and_write():
    snap = last("array a = [10, 20, 30]\na[1] = 99\nprint(a[1])")
    assert values_of(snap.structures["a"]) == [10, 99, 30]
    assert "99" in snap.output


def test_array_insert_and_remove():
    snap = last("array a = [1, 2, 3]\na.insert(1, 9)\na.remove(0)")
    assert values_of(snap.structures["a"]) == [9, 2, 3]


def test_stack_push_pop_semantics():
    snap = last("stack s = []\ns.push(1)\ns.push(2)\ns.push(3)\ns.pop()")
    assert values_of(snap.structures["s"]) == [1, 2]


def test_queue_enqueue_dequeue_fifo():
    snap = last("queue q = []\nq.enqueue(1)\nq.enqueue(2)\nq.enqueue(3)\nq.dequeue()")
    assert values_of(snap.structures["q"]) == [2, 3]


def test_deque_front_and_back_operations():
    snap = last(
        "deque d = []\n"
        "d.push_back(1)\n"
        "d.push_back(2)\n"
        "d.push_front(0)\n"
        "d.pop_back()\n"
    )
    assert values_of(snap.structures["d"]) == [0, 1]


def test_set_add_and_uniqueness():
    snap = last("set s = []\ns.add(1)\ns.add(2)\ns.add(1)")
    assert sorted(values_of(snap.structures["s"])) == [1, 2]


def test_set_contains_query():
    snap = last(
        "set s = []\n"
        "s.add(1)\n"
        "s.add(2)\n"
        "x = s.contains(2)\n"
        "print(x)\n"
    )
    assert "true" in snap.output.lower()


def test_map_set_get_has():
    src = (
        "map m = []\n"
        "m.set(\"a\", 1)\n"
        "m.set(\"b\", 2)\n"
        "print(m.get(\"a\"))\n"
        "print(m.has(\"c\"))\n"
    )
    snap = last(src)
    out = snap.output.lower()
    assert "1" in out and "false" in out


def test_graph_directed_nodes_and_edges():
    src = (
        "graph g = directed\n"
        "g.node(\"A\")\n"
        "g.node(\"B\")\n"
        "g.node(\"C\")\n"
        "g.edge(\"A\", \"B\")\n"
        "g.edge(\"B\", \"C\")\n"
    )
    snap = last(src)
    g = snap.structures["g"]
    assert len(g.items) == 3
    assert len(g.edges) == 2
    assert g.directed is True


def test_graph_has_node_and_edge_count():
    src = (
        "graph g = undirected\n"
        "g.node(\"A\")\n"
        "g.node(\"B\")\n"
        "g.edge(\"A\", \"B\")\n"
        "print(g.has_node(\"A\"))\n"
        "print(g.edge_count)\n"
    )
    snap = last(src)
    out = snap.output.lower()
    assert "true" in out
    assert "1" in out


def test_variables_and_arithmetic():
    snap = last("x = 1 + 2 * 3\nprint(x)")
    assert "7" in snap.output


def test_modulo_and_division():
    snap = last("print(10 % 3)\nprint(10 / 4)")
    out = snap.output
    assert "1" in out
    assert "2.5" in out


def test_boolean_logic_and_or_not():
    snap = last("print(true and false)\nprint(true or false)\nprint(not true)")
    out = snap.output.lower()
    assert out.count("false") >= 2
    assert "true" in out


def test_if_then_branch():
    snap = last(
        "x = 10\n"
        "if x > 5:\n"
        "    print(\"big\")\n"
        "else:\n"
        "    print(\"small\")\n"
        "end\n"
    )
    assert "big" in snap.output


def test_if_else_branch():
    snap = last(
        "x = 1\n"
        "if x > 5:\n"
        "    print(\"big\")\n"
        "else:\n"
        "    print(\"small\")\n"
        "end\n"
    )
    assert "small" in snap.output


def test_for_loop_accumulates():
    snap = last(
        "array a = []\n"
        "for i from 0 to 5:\n"
        "    a.push(i)\n"
        "end\n"
    )
    assert values_of(snap.structures["a"]) == [0, 1, 2, 3, 4]


def test_while_loop_terminates():
    snap = last(
        "x = 0\n"
        "while x < 3:\n"
        "    x = x + 1\n"
        "end\n"
        "print(x)\n"
    )
    assert "3" in snap.output


def test_swap_builtin():
    snap = last("array a = [1, 2, 3]\nswap(a, 0, 2)")
    assert values_of(snap.structures["a"]) == [3, 2, 1]


def test_snapshots_track_line_numbers():
    snaps, err = run_source("array a = [1]\na.push(2)\na.push(3)")
    assert err is None
    lines = [s.line for s in snaps]
    assert lines == sorted(lines)
    assert lines[0] >= 1


def test_division_by_zero_raises_runtime_error():
    snaps, err = run_source("x = 1 / 0")
    assert err is not None
    assert "zero" in err.lower() or "0" in err


def test_unknown_variable_raises_runtime_error():
    snaps, err = run_source("print(doesnotexist)")
    assert err is not None


def test_infinite_loop_is_bounded():
    snaps, err = run_source("while true:\n    x = 1\nend")
    assert err is not None


def test_interpreter_instance_reuse():
    i1 = Interpreter()
    snaps1 = i1.run("array a = [1, 2]\na.push(3)")
    assert values_of(snaps1[-1].structures["a"]) == [1, 2, 3]

    i2 = Interpreter()
    snaps2 = i2.run("stack s = []\ns.push(42)")
    assert values_of(snaps2[-1].structures["s"]) == [42]


def test_highlight_builtin_produces_highlights():
    snaps, err = run_source("array a = [1, 2, 3]\nhighlight(a, 0, 2)")
    assert err is None
    last_snap = snaps[-1]
    hl = last_snap.highlights.get("a", [])
    assert len(hl) >= 1
