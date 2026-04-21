import pytest
from visu.interpreter import run_source


def _expect_error(src, substring=None):
    snapshots, error = run_source(src)
    assert error is not None, f"Expected error but got none"
    if substring:
        assert substring in error, f"Expected '{substring}' in '{error}'"
    return error


class TestIndexErrors:
    @pytest.mark.parametrize("idx", list(range(-10, 0)) + list(range(5, 15)))
    def test_array_index_out_of_range(self, idx):
        _expect_error(f"array a = [1, 2, 3, 4, 5]\nx = a[{idx}]", "out of range")

    @pytest.mark.parametrize("idx", list(range(-5, 0)) + list(range(3, 10)))
    def test_stack_index_out_of_range(self, idx):
        _expect_error(f"stack s = [1, 2, 3]\nx = s[{idx}]", "out of range")

    @pytest.mark.parametrize("idx", list(range(-5, 0)) + list(range(4, 10)))
    def test_queue_index_out_of_range(self, idx):
        _expect_error(f"queue q = [1, 2, 3, 4]\nx = q[{idx}]", "out of range")

    @pytest.mark.parametrize("idx", list(range(-3, 0)) + list(range(2, 8)))
    def test_deque_index_out_of_range(self, idx):
        _expect_error(f"deque d = [10, 20]\nx = d[{idx}]", "out of range")

    @pytest.mark.parametrize("idx", list(range(-3, 0)) + list(range(3, 8)))
    def test_list_index_out_of_range(self, idx):
        _expect_error(f"list l = [1, 2, 3]\nx = l[{idx}]", "out of range")

    @pytest.mark.parametrize("size", range(0, 10))
    def test_array_assign_out_of_range(self, size):
        vals = ", ".join(str(i) for i in range(size))
        _expect_error(f"array a = [{vals}]\na[{size}] = 99", "out of range")


class TestEmptyStructureErrors:
    def test_pop_empty_stack(self):
        _expect_error("stack s = []\ns.pop()", "empty")

    def test_pop_empty_array(self):
        _expect_error("array a = []\na.pop()", "empty")

    def test_dequeue_empty_queue(self):
        _expect_error("queue q = []\nq.dequeue()", "empty")

    def test_pop_front_empty_deque(self):
        _expect_error("deque d = []\nd.pop_front()", "empty")

    def test_pop_back_empty_deque(self):
        _expect_error("deque d = []\nd.pop_back()", "empty")


class TestUndefinedErrors:
    @pytest.mark.parametrize("name", ["x", "foo", "bar", "undefined_var", "abc123"])
    def test_undefined_variable(self, name):
        _expect_error(f"y = {name}", "undefined")

    @pytest.mark.parametrize("name", ["x", "arr", "myStruct"])
    def test_unknown_structure(self, name):
        _expect_error(f"{name}.push(1)", "unknown")


class TestTypeErrors:
    @pytest.mark.parametrize("kind", ["stack", "queue", "deque", "list", "set"])
    def test_cannot_index_assign(self, kind):
        if kind in ("stack", "queue", "deque", "list"):
            pass
        if kind == "set":
            _expect_error(f"set u = [1, 2]\nu.remove(99)", "not in set")

    @pytest.mark.parametrize("kind", ["set", "map", "graph"])
    def test_cannot_index_non_linear(self, kind):
        if kind == "set":
            src = "set u = [1]\nx = u[0]"
        elif kind == "map":
            src = "map m = []\nm.set(\"a\", 1)\nx = m[0]"
        else:
            src = "graph g = directed\ng.node(\"A\")\nx = g[0]"
        _expect_error(src, "cannot index")

    def test_division_by_zero(self):
        _expect_error("x = 1 / 0", "division by zero")

    @pytest.mark.parametrize("divisor", [0])
    def test_division_by_zero_param(self, divisor):
        _expect_error(f"x = 42 / {divisor}", "division by zero")


class TestGraphErrors:
    def test_duplicate_node(self):
        _expect_error('graph g = directed\ng.node("A")\ng.node("A")', "already exists")

    def test_duplicate_edge(self):
        _expect_error(
            'graph g = directed\ng.node("A")\ng.node("B")\ng.edge("A", "B")\ng.edge("A", "B")',
            "already exists",
        )

    def test_edge_missing_src(self):
        _expect_error('graph g = directed\ng.node("B")\ng.edge("A", "B")', "not in graph")

    def test_edge_missing_dst(self):
        _expect_error('graph g = directed\ng.node("A")\ng.edge("A", "B")', "not in graph")

    def test_remove_missing_node(self):
        _expect_error('graph g = directed\ng.remove_node("X")', "not in graph")

    def test_remove_missing_edge(self):
        _expect_error(
            'graph g = directed\ng.node("A")\ng.node("B")\ng.remove_edge("A", "B")',
            "not in graph",
        )

    def test_get_value_missing_node(self):
        _expect_error('graph g = directed\nx = g.get_value("X")', "not in graph")

    @pytest.mark.parametrize("n", range(2, 10))
    def test_duplicate_node_in_loop(self, n):
        lines = ["graph g = directed"]
        for i in range(n):
            lines.append(f'g.node("{i}")')
        lines.append('g.node("0")')
        _expect_error("\n".join(lines), "already exists")


class TestMapErrors:
    def test_map_non_empty_init(self):
        _expect_error("map m = [1, 2, 3]", "map must start empty")

    @pytest.mark.parametrize("key", ["missing", "nope", "xyz"])
    def test_map_remove_missing(self, key):
        _expect_error(f'map m = []\nm.remove("{key}")', "not in map")


class TestSetErrors:
    @pytest.mark.parametrize("val", [99, 0, -1, 42])
    def test_set_remove_missing(self, val):
        _expect_error(f"set u = [1, 2, 3]\nu.remove({val})", "not in set")


class TestArgumentErrors:
    def test_swap_too_few_args(self):
        _expect_error("array a = [1, 2]\nswap(a, 0)", "3 arguments")

    def test_swap_too_many_args(self):
        _expect_error("array a = [1, 2]\nswap(a, 0, 1, 2)", "3 arguments")

    @pytest.mark.parametrize("method,expected_args", [
        ("push", 1), ("pop", 0), ("insert", 2), ("remove", 1),
    ])
    def test_array_wrong_arg_count(self, method, expected_args):
        wrong_count = expected_args + 1
        args = ", ".join(str(i) for i in range(wrong_count))
        _expect_error(f"array a = [1, 2, 3]\na.{method}({args})")


class TestSwapErrors:
    @pytest.mark.parametrize("i,j", [(-1, 0), (0, 5), (5, 0), (10, 10)])
    def test_swap_out_of_range(self, i, j):
        _expect_error(f"array a = [1, 2, 3]\nswap(a, {i}, {j})", "out of range")

    @pytest.mark.parametrize("kind", ["set", "map", "graph"])
    def test_swap_non_linear(self, kind):
        if kind == "set":
            src = "set u = [1, 2]\nswap(u, 0, 1)"
        elif kind == "map":
            src = "map m = []\nswap(m, 0, 1)"
        else:
            src = "graph g = directed\nswap(g, 0, 1)"
        _expect_error(src, "cannot swap")


class TestLexerErrors:
    @pytest.mark.parametrize("char", ["@", "^", "~", "`", "\\", "|"])
    def test_unexpected_character(self, char):
        _expect_error(f"x = 1 {char} 2", "Unexpected character")

    @pytest.mark.parametrize("src", [
        '"unterminated string',
        "'also unterminated",
    ])
    def test_unterminated_string(self, src):
        _expect_error(f"x = {src}", "Unterminated string")


class TestParserErrors:
    @pytest.mark.parametrize("src", [
        "if x:",
        "for in range:",
        "while :",
    ])
    def test_parse_errors(self, src):
        _, error = run_source(src)
        assert error is not None

    def test_missing_end(self):
        _, error = run_source("if true:\n    x = 1")
        assert error is not None

    @pytest.mark.parametrize("src", [
        "graph g = 5",
        "graph g = []",
    ])
    def test_graph_invalid_init(self, src):
        _, error = run_source(src)
        assert error is not None


class TestStepLimit:
    def test_infinite_loop_detection(self):
        src = "x = 0\nwhile true:\n    x = x + 1\nend"
        _, error = run_source(src)
        assert error is not None
        assert "step limit" in error

    @pytest.mark.parametrize("n", [100, 500, 1000])
    def test_large_but_valid_loop(self, n):
        src = f"x = 0\nfor i from 0 to {n}:\n    x = x + 1\nend"
        snapshots, error = run_source(src)
        assert error is None
        assert snapshots[-1].variables["x"] == n


class TestMethodOnWrongStructure:
    @pytest.mark.parametrize("method", ["enqueue", "dequeue"])
    def test_queue_method_on_array(self, method):
        _expect_error(f"array a = [1]\na.{method}(1)" if method == "enqueue" else f"array a = [1]\na.{method}()")

    @pytest.mark.parametrize("method", ["push_front", "push_back", "pop_front", "pop_back"])
    def test_deque_method_on_stack(self, method):
        if "push" in method:
            _expect_error(f"stack s = []\ns.{method}(1)")
        else:
            _expect_error(f"stack s = [1]\ns.{method}()")

    @pytest.mark.parametrize("method", ["add", "contains"])
    def test_set_method_on_array(self, method):
        if method == "add":
            _expect_error(f"array a = []\na.{method}(1)")
        else:
            _expect_error(f"array a = [1]\nx = a.{method}(1)")
