import random
import pytest
from visu.interpreter import run_source


def _final(src):
    snapshots, error = run_source(src)
    assert error is None, f"Unexpected error: {error}"
    return snapshots[-1]


def _bfs_src(n, edges, start):
    lines = ["graph g = undirected"]
    for i in range(n):
        lines.append(f'g.node("{i}")')
    for a, b in edges:
        lines.append(f'g.edge("{a}", "{b}")')
    lines.append("queue frontier = []")
    lines.append("set visited = []")
    lines.append("array order = []")
    lines.append(f'frontier.enqueue("{start}")')
    lines.append(f'visited.add("{start}")')
    lines.append("while frontier.length > 0:")
    lines.append("    cur = frontier[0]")
    lines.append("    frontier.dequeue()")
    lines.append("    order.push(cur)")
    lines.append("    neigh = g.neighbors(cur)")
    lines.append("    for i from 0 to neigh.length:")
    lines.append("        nxt = neigh[i]")
    lines.append("        if not visited.contains(nxt):")
    lines.append("            visited.add(nxt)")
    lines.append("            frontier.enqueue(nxt)")
    lines.append("        end")
    lines.append("    end")
    lines.append("end")
    return "\n".join(lines)


def _dfs_src(n, edges, start):
    lines = ["graph g = undirected"]
    for i in range(n):
        lines.append(f'g.node("{i}")')
    for a, b in edges:
        lines.append(f'g.edge("{a}", "{b}")')
    lines.append("stack frontier = []")
    lines.append("set visited = []")
    lines.append("array order = []")
    lines.append(f'frontier.push("{start}")')
    lines.append("while frontier.length > 0:")
    lines.append("    cur = frontier[frontier.length - 1]")
    lines.append("    frontier.pop()")
    lines.append("    if not visited.contains(cur):")
    lines.append("        visited.add(cur)")
    lines.append("        order.push(cur)")
    lines.append("        neigh = g.neighbors(cur)")
    lines.append("        for i from 0 to neigh.length:")
    lines.append("            frontier.push(neigh[i])")
    lines.append("        end")
    lines.append("    end")
    lines.append("end")
    return "\n".join(lines)


def _python_bfs(n, edges, start):
    adj = {str(i): [] for i in range(n)}
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    visited = set()
    queue = [start]
    visited.add(start)
    order = []
    while queue:
        cur = queue.pop(0)
        order.append(cur)
        for nxt in adj[cur]:
            if nxt not in visited:
                visited.add(nxt)
                queue.append(nxt)
    return order


def _make_tree_edges(n, seed):
    rng = random.Random(seed)
    edges = []
    for i in range(1, n):
        parent = rng.randint(0, i - 1)
        edges.append((str(parent), str(i)))
    return edges


def _make_bfs_params():
    params = []
    for seed in range(100):
        rng = random.Random(seed)
        n = rng.randint(2, 12)
        edges = _make_tree_edges(n, seed)
        params.append((n, edges, "0", seed))
    return params


BFS_PARAMS = _make_bfs_params()


@pytest.mark.parametrize("n,edges,start,seed", BFS_PARAMS,
                         ids=[f"bfs-seed{p[3]}" for p in BFS_PARAMS])
def test_bfs_visits_all_nodes(n, edges, start, seed):
    src = _bfs_src(n, edges, start)
    s = _final(src)
    order = [item.value for item in s.structures["order"].items]
    assert len(order) == n
    assert set(order) == {str(i) for i in range(n)}


@pytest.mark.parametrize("n,edges,start,seed", BFS_PARAMS,
                         ids=[f"bfs-order-seed{p[3]}" for p in BFS_PARAMS])
def test_bfs_correct_order(n, edges, start, seed):
    src = _bfs_src(n, edges, start)
    s = _final(src)
    order = [item.value for item in s.structures["order"].items]
    expected = _python_bfs(n, edges, start)
    assert order == expected


@pytest.mark.parametrize("n,edges,start,seed", BFS_PARAMS,
                         ids=[f"dfs-seed{p[3]}" for p in BFS_PARAMS])
def test_dfs_visits_all_nodes(n, edges, start, seed):
    src = _dfs_src(n, edges, start)
    s = _final(src)
    order = [item.value for item in s.structures["order"].items]
    assert len(order) == n
    assert set(order) == {str(i) for i in range(n)}


def _degree_count_src(n, edges):
    lines = ["graph g = undirected"]
    for i in range(n):
        lines.append(f'g.node("{i}")')
    for a, b in edges:
        lines.append(f'g.edge("{a}", "{b}")')
    lines.append("array degrees = []")
    for i in range(n):
        lines.append(f'neigh = g.neighbors("{i}")')
        lines.append("degrees.push(neigh.length)")
    return "\n".join(lines)


def _make_degree_params():
    params = []
    for seed in range(80):
        rng = random.Random(seed)
        n = rng.randint(2, 10)
        edges = _make_tree_edges(n, seed)
        params.append((n, edges, seed))
    return params


DEGREE_PARAMS = _make_degree_params()


@pytest.mark.parametrize("n,edges,seed", DEGREE_PARAMS,
                         ids=[f"deg-seed{p[2]}" for p in DEGREE_PARAMS])
def test_degree_count(n, edges, seed):
    src = _degree_count_src(n, edges)
    s = _final(src)
    degrees = [item.value for item in s.structures["degrees"].items]
    adj = {str(i): [] for i in range(n)}
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    expected = [len(adj[str(i)]) for i in range(n)]
    assert degrees == expected


def _make_directed_params():
    params = []
    for seed in range(100):
        rng = random.Random(seed)
        n = rng.randint(2, 8)
        edges = []
        for i in range(1, n):
            src_node = rng.randint(0, i - 1)
            edges.append((str(src_node), str(i)))
        params.append((n, edges, seed))
    return params


DIRECTED_PARAMS = _make_directed_params()


@pytest.mark.parametrize("n,edges,seed", DIRECTED_PARAMS,
                         ids=[f"dir-seed{p[2]}" for p in DIRECTED_PARAMS])
def test_directed_neighbors(n, edges, seed):
    lines = ["graph g = directed"]
    for i in range(n):
        lines.append(f'g.node("{i}")')
    for a, b in edges:
        lines.append(f'g.edge("{a}", "{b}")')
    adj = {str(i): [] for i in range(n)}
    for a, b in edges:
        adj[a].append(b)
    for i in range(n):
        lines.append(f'n{i} = g.neighbors("{i}")')
    s = _final("\n".join(lines))
    for i in range(n):
        assert s.variables[f"n{i}"] == adj[str(i)]


@pytest.mark.parametrize("n,edges,seed", DIRECTED_PARAMS,
                         ids=[f"has-edge-seed{p[2]}" for p in DIRECTED_PARAMS])
def test_has_edge_directed(n, edges, seed):
    lines = ["graph g = directed"]
    for i in range(n):
        lines.append(f'g.node("{i}")')
    for a, b in edges:
        lines.append(f'g.edge("{a}", "{b}")')
    edge_set = set(edges)
    checks = []
    for i in range(min(n, 5)):
        for j in range(min(n, 5)):
            if i != j:
                checks.append((str(i), str(j)))
    for idx, (a, b) in enumerate(checks):
        lines.append(f'c{idx} = g.has_edge("{a}", "{b}")')
    s = _final("\n".join(lines))
    for idx, (a, b) in enumerate(checks):
        assert s.variables[f"c{idx}"] == ((a, b) in edge_set)


@pytest.mark.parametrize("n", range(2, 20))
def test_graph_self_loop(n):
    lines = ["graph g = directed"]
    for i in range(n):
        lines.append(f'g.node("{i}")')
    lines.append(f'g.edge("0", "0")')
    lines.append('x = g.has_edge("0", "0")')
    lines.append("y = g.edge_count")
    s = _final("\n".join(lines))
    assert s.variables["x"] is True
    assert s.variables["y"] == 1


@pytest.mark.parametrize("seed", range(50))
def test_graph_node_values(seed):
    rng = random.Random(seed)
    n = rng.randint(1, 10)
    values = [rng.randint(0, 100) for _ in range(n)]
    lines = ["graph g = directed"]
    for i in range(n):
        lines.append(f'g.node("{i}", {values[i]})')
    for i in range(n):
        lines.append(f'v{i} = g.get_value("{i}")')
    s = _final("\n".join(lines))
    for i in range(n):
        assert s.variables[f"v{i}"] == values[i]


@pytest.mark.parametrize("seed", range(50))
def test_graph_weighted_path_sum(seed):
    rng = random.Random(seed)
    n = rng.randint(2, 8)
    weights = [rng.randint(1, 20) for _ in range(n - 1)]
    lines = ["graph g = directed"]
    for i in range(n):
        lines.append(f'g.node("{i}")')
    for i in range(n - 1):
        lines.append(f'g.edge("{i}", "{i + 1}", {weights[i]})')
    lines.append("x = g.edge_count")
    s = _final("\n".join(lines))
    assert s.variables["x"] == n - 1
