import random
import pytest
from visu.interpreter import run_source


class TestSnapshotIsolation:
    @pytest.mark.parametrize("n", range(1, 50))
    def test_snapshots_are_independent(self, n):
        lines = ["array a = []"]
        for i in range(n):
            lines.append(f"a.push({i})")
        snapshots, error = run_source("\n".join(lines))
        assert error is None
        for idx, snap in enumerate(snapshots):
            if idx == 0:
                assert len(snap.structures["a"].items) == 0
            else:
                assert len(snap.structures["a"].items) == idx

    @pytest.mark.parametrize("n", range(1, 30))
    def test_variable_snapshots(self, n):
        lines = []
        for i in range(n):
            lines.append(f"x = {i}")
        snapshots, error = run_source("\n".join(lines))
        assert error is None
        for idx, snap in enumerate(snapshots):
            assert snap.variables["x"] == idx

    @pytest.mark.parametrize("n", range(2, 20))
    def test_mutation_doesnt_affect_previous(self, n):
        lines = ["array a = [1, 2, 3]"]
        for i in range(n):
            lines.append(f"a[0] = {i}")
        snapshots, error = run_source("\n".join(lines))
        assert error is None
        assert snapshots[0].structures["a"].items[0].value == 1
        for idx in range(1, len(snapshots)):
            val = snapshots[idx].structures["a"].items[0].value
            assert val == idx - 1


class TestSnapshotCount:
    @pytest.mark.parametrize("n", range(0, 20))
    def test_for_loop_snapshot_count(self, n):
        src = f"x = 0\nfor i from 0 to {n}:\n    x = x + 1\nend"
        snapshots, error = run_source(src)
        assert error is None
        assert len(snapshots) > 0

    @pytest.mark.parametrize("n", range(1, 15))
    def test_each_statement_creates_snapshot(self, n):
        lines = [f"x = {i}" for i in range(n)]
        snapshots, error = run_source("\n".join(lines))
        assert error is None
        assert len(snapshots) == n


class TestSnapshotLineTracking:
    @pytest.mark.parametrize("n", range(1, 20))
    def test_line_numbers_increase(self, n):
        lines = [f"x = {i}" for i in range(n)]
        snapshots, error = run_source("\n".join(lines))
        assert error is None
        for i, snap in enumerate(snapshots):
            assert snap.line == i + 1

    @pytest.mark.parametrize("n", range(2, 10))
    def test_for_loop_line_tracking(self, n):
        src = f"x = 0\nfor i from 0 to {n}:\n    x = x + 1\nend"
        snapshots, error = run_source(src)
        assert error is None
        for snap in snapshots:
            assert snap.line >= 1


class TestSnapshotMessages:
    @pytest.mark.parametrize("kind", ["array", "stack", "queue", "deque", "list", "set"])
    def test_creation_message(self, kind):
        src = f"{kind} x = []"
        snapshots, error = run_source(src)
        assert error is None
        assert "created" in snapshots[-1].message

    def test_graph_creation_message(self):
        snapshots, error = run_source("graph g = directed")
        assert error is None
        assert "created" in snapshots[-1].message

    @pytest.mark.parametrize("val", range(-10, 11))
    def test_assign_message(self, val):
        snapshots, error = run_source(f"x = {val}")
        assert error is None
        assert str(val) in snapshots[-1].message

    @pytest.mark.parametrize("cond", [True, False])
    def test_if_message(self, cond):
        cond_str = "true" if cond else "false"
        snapshots, error = run_source(f"if {cond_str}:\n    x = 1\nend")
        assert error is None
        assert str(cond) in snapshots[0].message


class TestHighlightTracking:
    @pytest.mark.parametrize("n", range(1, 20))
    def test_push_highlights_new_item(self, n):
        lines = ["array a = []"]
        for i in range(n):
            lines.append(f"a.push({i})")
        snapshots, error = run_source("\n".join(lines))
        assert error is None
        for idx in range(1, len(snapshots)):
            hl = snapshots[idx].highlights.get("a", [])
            assert len(hl) <= 1

    @pytest.mark.parametrize("i,j", [(0, 1), (0, 2), (1, 2), (0, 3)])
    def test_swap_highlights_two_items(self, i, j):
        src = f"array a = [10, 20, 30, 40]\nswap(a, {i}, {j})"
        snapshots, error = run_source(src)
        assert error is None
        hl = snapshots[-1].highlights.get("a", [])
        assert len(hl) == 2

    @pytest.mark.parametrize("n", range(1, 15))
    def test_highlight_clears_between_statements(self, n):
        lines = ["array a = [1, 2, 3]"]
        for i in range(n):
            lines.append(f"x = {i}")
        snapshots, error = run_source("\n".join(lines))
        assert error is None
        for snap in snapshots[1:]:
            assert not snap.highlights.get("a", [])


class TestOutputTracking:
    @pytest.mark.parametrize("n", range(1, 25))
    def test_output_accumulates(self, n):
        lines = [f"print({i})" for i in range(n)]
        snapshots, error = run_source("\n".join(lines))
        assert error is None
        for idx in range(n):
            snap = snapshots[idx]
            expected_lines = [str(i) for i in range(idx + 1)]
            assert snap.output == "\n".join(expected_lines)

    @pytest.mark.parametrize("n", range(1, 15))
    def test_output_persists_after_non_print(self, n):
        lines = [f"print({i})" for i in range(n)]
        lines.append("x = 0")
        snapshots, error = run_source("\n".join(lines))
        assert error is None
        expected = "\n".join(str(i) for i in range(n))
        assert snapshots[-1].output == expected


class TestMultiStructureSnapshots:
    @pytest.mark.parametrize("seed", range(40))
    def test_all_structures_in_snapshot(self, seed):
        rng = random.Random(seed)
        n = rng.randint(1, 5)
        lines = []
        names = []
        for i in range(n):
            name = f"a{i}"
            names.append(name)
            lines.append(f"array {name} = []")
        for name in names:
            lines.append(f"{name}.push(1)")
        snapshots, error = run_source("\n".join(lines))
        assert error is None
        final = snapshots[-1]
        for name in names:
            assert name in final.structures
