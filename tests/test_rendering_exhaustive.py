import random
import pytest
from visu.interpreter import run_source, Structure, Item, MapEntry, GraphNode, GraphEdge
from visu.render.renderers.base import NaturalLayout
from visu.render.renderers import (
    ArrayRenderer, StackRenderer, QueueRenderer, DequeRenderer,
    LinkedListRenderer, SetRenderer, MapRenderer, GraphRenderer,
)
from visu.render.theme import DARK_THEME, LIGHT_THEME


def _make_linear_structure(kind, name, values):
    items = [Item(i + 1, v) for i, v in enumerate(values)]
    return Structure(kind=kind, name=name, items=items)


def _make_map_structure(name, pairs):
    entries = [MapEntry(i + 1, k, v) for i, (k, v) in enumerate(pairs)]
    return Structure(kind="map", name=name, items=entries)


def _make_graph_structure(name, node_keys, edges=None, directed=True):
    nodes = [GraphNode(i + 1, k) for i, k in enumerate(node_keys)]
    edge_list = []
    if edges:
        for i, (s, d, w) in enumerate(edges):
            edge_list.append(GraphEdge(100 + i, s, d, w))
    return Structure(kind="graph", name=name, items=nodes, edges=edge_list, directed=directed)


THEMES = [("dark", DARK_THEME), ("light", LIGHT_THEME)]


class TestArrayRendererLayout:
    @pytest.mark.parametrize("theme_name,theme", THEMES)
    @pytest.mark.parametrize("n", range(0, 30))
    def test_layout_size(self, theme_name, theme, n):
        renderer = ArrayRenderer(theme)
        s = _make_linear_structure("array", "a", list(range(n)))
        layout = renderer.layout(s)
        if n == 0:
            assert not layout.poses
        else:
            assert len(layout.poses) == n
            assert layout.width > 0
            assert layout.height > 0

    @pytest.mark.parametrize("n", range(2, 20))
    def test_layout_horizontal_order(self, n):
        renderer = ArrayRenderer(DARK_THEME)
        s = _make_linear_structure("array", "a", list(range(n)))
        layout = renderer.layout(s)
        xs = [layout.poses[f"a#{i+1}"].x for i in range(n)]
        for i in range(len(xs) - 1):
            assert xs[i] < xs[i + 1]


class TestStackRendererLayout:
    @pytest.mark.parametrize("theme_name,theme", THEMES)
    @pytest.mark.parametrize("n", range(0, 25))
    def test_layout_size(self, theme_name, theme, n):
        renderer = StackRenderer(theme)
        s = _make_linear_structure("stack", "s", list(range(n)))
        layout = renderer.layout(s)
        if n == 0:
            assert not layout.poses
        else:
            assert len(layout.poses) == n

    @pytest.mark.parametrize("n", range(2, 15))
    def test_layout_vertical_order(self, n):
        renderer = StackRenderer(DARK_THEME)
        s = _make_linear_structure("stack", "s", list(range(n)))
        layout = renderer.layout(s)
        ys = [layout.poses[f"s#{i+1}"].y for i in range(n)]
        for i in range(len(ys) - 1):
            assert ys[i] > ys[i + 1]


class TestQueueRendererLayout:
    @pytest.mark.parametrize("theme_name,theme", THEMES)
    @pytest.mark.parametrize("n", range(0, 25))
    def test_layout_size(self, theme_name, theme, n):
        renderer = QueueRenderer(theme)
        s = _make_linear_structure("queue", "q", list(range(n)))
        layout = renderer.layout(s)
        if n == 0:
            assert not layout.poses
        else:
            assert len(layout.poses) == n

    @pytest.mark.parametrize("n", range(2, 15))
    def test_layout_horizontal(self, n):
        renderer = QueueRenderer(DARK_THEME)
        s = _make_linear_structure("queue", "q", list(range(n)))
        layout = renderer.layout(s)
        xs = [layout.poses[f"q#{i+1}"].x for i in range(n)]
        for i in range(len(xs) - 1):
            assert xs[i] < xs[i + 1]


class TestDequeRendererLayout:
    @pytest.mark.parametrize("theme_name,theme", THEMES)
    @pytest.mark.parametrize("n", range(0, 25))
    def test_layout_size(self, theme_name, theme, n):
        renderer = DequeRenderer(theme)
        s = _make_linear_structure("deque", "d", list(range(n)))
        layout = renderer.layout(s)
        if n == 0:
            assert not layout.poses
        else:
            assert len(layout.poses) == n


class TestLinkedListRendererLayout:
    @pytest.mark.parametrize("theme_name,theme", THEMES)
    @pytest.mark.parametrize("n", range(0, 25))
    def test_layout_size(self, theme_name, theme, n):
        renderer = LinkedListRenderer(theme)
        s = _make_linear_structure("list", "l", list(range(n)))
        layout = renderer.layout(s)
        if n == 0:
            assert not layout.poses
        else:
            assert len(layout.poses) == n

    @pytest.mark.parametrize("n", range(2, 15))
    def test_layout_horizontal(self, n):
        renderer = LinkedListRenderer(DARK_THEME)
        s = _make_linear_structure("list", "l", list(range(n)))
        layout = renderer.layout(s)
        xs = [layout.poses[f"l#{i+1}"].x for i in range(n)]
        for i in range(len(xs) - 1):
            assert xs[i] < xs[i + 1]


class TestSetRendererLayout:
    @pytest.mark.parametrize("theme_name,theme", THEMES)
    @pytest.mark.parametrize("n", range(0, 25))
    def test_layout_size(self, theme_name, theme, n):
        renderer = SetRenderer(theme)
        s = _make_linear_structure("set", "u", list(range(n)))
        layout = renderer.layout(s)
        if n == 0:
            assert not layout.poses
        else:
            assert len(layout.poses) == n
            assert layout.width > 0
            assert layout.height > 0


class TestMapRendererLayout:
    @pytest.mark.parametrize("theme_name,theme", THEMES)
    @pytest.mark.parametrize("n", range(0, 25))
    def test_layout_size(self, theme_name, theme, n):
        renderer = MapRenderer(theme)
        pairs = [(f"k{i}", i * 10) for i in range(n)]
        s = _make_map_structure("m", pairs)
        layout = renderer.layout(s)
        if n == 0:
            assert not layout.poses
        else:
            assert len(layout.poses) == n

    @pytest.mark.parametrize("n", range(2, 15))
    def test_layout_vertical_order(self, n):
        renderer = MapRenderer(DARK_THEME)
        pairs = [(f"k{i}", i) for i in range(n)]
        s = _make_map_structure("m", pairs)
        layout = renderer.layout(s)
        ys = [layout.poses[f"m#{i+1}"].y for i in range(n)]
        for i in range(len(ys) - 1):
            assert ys[i] < ys[i + 1]


class TestGraphRendererLayout:
    @pytest.mark.parametrize("theme_name,theme", THEMES)
    @pytest.mark.parametrize("n", range(0, 20))
    def test_layout_size(self, theme_name, theme, n):
        renderer = GraphRenderer(theme)
        keys = [str(i) for i in range(n)]
        s = _make_graph_structure("g", keys)
        layout = renderer.layout(s)
        if n == 0:
            assert not layout.poses
        else:
            assert len(layout.poses) == n
            assert layout.width > 0
            assert layout.height > 0

    @pytest.mark.parametrize("n", range(1, 15))
    def test_layout_no_overlap(self, n):
        renderer = GraphRenderer(DARK_THEME)
        keys = [str(i) for i in range(n)]
        s = _make_graph_structure("g", keys)
        layout = renderer.layout(s)
        poses = list(layout.poses.values())
        min_dist = 2 * renderer.NODE_RADIUS * 0.5
        for i in range(len(poses)):
            for j in range(i + 1, len(poses)):
                dx = poses[i].x - poses[j].x
                dy = poses[i].y - poses[j].y
                dist = (dx ** 2 + dy ** 2) ** 0.5
                assert dist >= min_dist, f"Nodes {i} and {j} overlap"


class TestLayoutConsistency:
    @pytest.mark.parametrize("seed", range(50))
    def test_same_input_same_layout(self, seed):
        rng = random.Random(seed)
        n = rng.randint(1, 10)
        values = [rng.randint(0, 100) for _ in range(n)]
        renderer = ArrayRenderer(DARK_THEME)
        s = _make_linear_structure("array", "a", values)
        layout1 = renderer.layout(s)
        layout2 = renderer.layout(s)
        for key in layout1.poses:
            assert layout1.poses[key].x == layout2.poses[key].x
            assert layout1.poses[key].y == layout2.poses[key].y

    @pytest.mark.parametrize("seed", range(50))
    def test_graph_same_input_same_layout(self, seed):
        rng = random.Random(seed)
        n = rng.randint(1, 8)
        renderer = GraphRenderer(DARK_THEME)
        keys = [str(i) for i in range(n)]
        s = _make_graph_structure("g", keys)
        layout1 = renderer.layout(s)
        layout2 = renderer.layout(s)
        for key in layout1.poses:
            assert layout1.poses[key].x == layout2.poses[key].x
            assert layout1.poses[key].y == layout2.poses[key].y


class TestFmtMethod:
    from visu.render.renderers.base import StructureRenderer

    @pytest.mark.parametrize("val,expected", [
        (1, "1"),
        (1.0, "1"),
        (1.5, "1.5"),
        (0, "0"),
        (-1, "-1"),
        (-3.0, "-3"),
        (True, "true"),
        (False, "false"),
        (None, "null"),
        ("hello", "hello"),
        ([1, 2, 3], "[1, 2, 3]"),
        ([], "[]"),
        ([True, None, 1.0], "[true, null, 1]"),
        ([[1, 2], [3]], "[[1, 2], [3]]"),
    ])
    def test_fmt(self, val, expected):
        assert self.StructureRenderer._fmt(val) == expected
