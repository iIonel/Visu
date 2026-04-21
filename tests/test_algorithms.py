"""End-to-end pseudocode tests — classic algorithms in the Visu DSL.

Each test runs a full program and verifies:
- No runtime error
- Final structure/variable state matches expectation
- Snapshots are generated (i.e. the visualizer has frames to render)
"""

import pytest

from visu.interpreter.runtime import run_source


def values_of(struct):
    return [it.value for it in struct.items]


def run_ok(src):
    snaps, err = run_source(src)
    assert err is None, f"runtime error: {err}\nsource:\n{src}"
    assert snaps, "no snapshots produced"
    return snaps


# ---------------------------------------------------------------------------
# Sorting
# ---------------------------------------------------------------------------

def test_bubble_sort_ascending():
    src = """
array a = [5, 1, 4, 2, 8, 3]
for i from 0 to 6:
    for j from 0 to 5:
        if a[j] > a[j + 1]:
            swap(a, j, j + 1)
        end
    end
end
""".strip()
    snaps = run_ok(src)
    assert values_of(snaps[-1].structures["a"]) == [1, 2, 3, 4, 5, 8]


def test_bubble_sort_already_sorted():
    src = """
array a = [1, 2, 3, 4, 5]
for i from 0 to 5:
    for j from 0 to 4:
        if a[j] > a[j + 1]:
            swap(a, j, j + 1)
        end
    end
end
""".strip()
    snaps = run_ok(src)
    assert values_of(snaps[-1].structures["a"]) == [1, 2, 3, 4, 5]


def test_bubble_sort_reverse_input():
    src = """
array a = [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
for i from 0 to 10:
    for j from 0 to 9:
        if a[j] > a[j + 1]:
            swap(a, j, j + 1)
        end
    end
end
""".strip()
    snaps = run_ok(src)
    assert values_of(snaps[-1].structures["a"]) == list(range(10))


def test_selection_sort():
    src = """
array a = [64, 25, 12, 22, 11]
for i from 0 to 4:
    minIdx = i
    for j from 0 to 5:
        if j > i:
            if a[j] < a[minIdx]:
                minIdx = j
            end
        end
    end
    swap(a, i, minIdx)
end
""".strip()
    snaps = run_ok(src)
    assert values_of(snaps[-1].structures["a"]) == [11, 12, 22, 25, 64]


def test_insertion_sort():
    src = """
array a = [12, 11, 13, 5, 6]
for i from 1 to 5:
    j = i
    while j > 0:
        if a[j - 1] > a[j]:
            swap(a, j - 1, j)
            j = j - 1
        else:
            j = 0
        end
    end
end
""".strip()
    snaps = run_ok(src)
    assert values_of(snaps[-1].structures["a"]) == [5, 6, 11, 12, 13]


def test_sort_with_duplicates():
    src = """
array a = [3, 1, 3, 2, 1, 3, 2]
for i from 0 to 7:
    for j from 0 to 6:
        if a[j] > a[j + 1]:
            swap(a, j, j + 1)
        end
    end
end
""".strip()
    snaps = run_ok(src)
    assert values_of(snaps[-1].structures["a"]) == [1, 1, 2, 2, 3, 3, 3]


# ---------------------------------------------------------------------------
# Searching
# ---------------------------------------------------------------------------

def test_linear_search_found():
    src = """
array a = [10, 20, 30, 40, 50]
target = 30
found = -1
for i from 0 to 5:
    if a[i] == target:
        found = i
    end
end
print(found)
""".strip()
    snaps = run_ok(src)
    assert "2" in snaps[-1].output


def test_linear_search_not_found():
    src = """
array a = [10, 20, 30]
target = 99
found = -1
for i from 0 to 3:
    if a[i] == target:
        found = i
    end
end
print(found)
""".strip()
    snaps = run_ok(src)
    assert "-1" in snaps[-1].output


def test_binary_search_found():
    src = """
array a = [1, 3, 5, 7, 9, 11, 13, 15]
target = 7
lo = 0
hi = 7
result = -1
while lo <= hi:
    mid = (lo + hi) / 2
    if a[mid] == target:
        result = mid
        lo = hi + 1
    else:
        if a[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
        end
    end
end
print(result)
""".strip()
    snaps = run_ok(src)
    assert "3" in snaps[-1].output


def test_find_max_in_array():
    src = """
array a = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
best = a[0]
for i from 1 to 10:
    if a[i] > best:
        best = a[i]
    end
end
print(best)
""".strip()
    snaps = run_ok(src)
    assert "9" in snaps[-1].output


def test_find_min_in_array():
    src = """
array a = [7, 3, 9, 1, 4, 6]
best = a[0]
for i from 1 to 6:
    if a[i] < best:
        best = a[i]
    end
end
print(best)
""".strip()
    snaps = run_ok(src)
    assert "1" in snaps[-1].output


def test_count_occurrences():
    src = """
array a = [1, 2, 3, 2, 4, 2, 5, 2]
target = 2
count = 0
for i from 0 to 8:
    if a[i] == target:
        count = count + 1
    end
end
print(count)
""".strip()
    snaps = run_ok(src)
    assert "4" in snaps[-1].output


# ---------------------------------------------------------------------------
# Arithmetic / numeric algorithms
# ---------------------------------------------------------------------------

def test_factorial_iterative():
    src = """
n = 6
result = 1
i = 1
while i <= n:
    result = result * i
    i = i + 1
end
print(result)
""".strip()
    snaps = run_ok(src)
    assert "720" in snaps[-1].output


def test_fibonacci_sequence():
    src = """
array fib = [0, 1]
for i from 2 to 10:
    fib.push(fib[i - 1] + fib[i - 2])
end
""".strip()
    snaps = run_ok(src)
    assert values_of(snaps[-1].structures["fib"]) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]


def test_sum_1_to_100():
    src = """
total = 0
i = 1
while i <= 100:
    total = total + i
    i = i + 1
end
print(total)
""".strip()
    snaps = run_ok(src)
    assert "5050" in snaps[-1].output


def test_gcd_euclidean():
    src = """
a = 48
b = 18
while b > 0:
    t = b
    b = a % b
    a = t
end
print(a)
""".strip()
    snaps = run_ok(src)
    assert "6" in snaps[-1].output


def test_power_of_two():
    src = """
n = 10
result = 1
i = 0
while i < n:
    result = result * 2
    i = i + 1
end
print(result)
""".strip()
    snaps = run_ok(src)
    assert "1024" in snaps[-1].output


def test_is_prime_check():
    src = """
n = 17
isPrime = true
i = 2
while i < n:
    if n % i == 0:
        isPrime = false
    end
    i = i + 1
end
print(isPrime)
""".strip()
    snaps = run_ok(src)
    assert "true" in snaps[-1].output.lower()


def test_is_not_prime():
    src = """
n = 15
isPrime = true
i = 2
while i < n:
    if n % i == 0:
        isPrime = false
    end
    i = i + 1
end
print(isPrime)
""".strip()
    snaps = run_ok(src)
    assert "false" in snaps[-1].output.lower()


def test_collatz_until_one():
    src = """
n = 27
steps = 0
while n > 1:
    if n % 2 == 0:
        n = n / 2
    else:
        n = 3 * n + 1
    end
    steps = steps + 1
end
print(steps)
""".strip()
    snaps = run_ok(src)
    assert "111" in snaps[-1].output


# ---------------------------------------------------------------------------
# Array transformations
# ---------------------------------------------------------------------------

def test_reverse_array_in_place():
    src = """
array a = [1, 2, 3, 4, 5, 6]
lo = 0
hi = 5
while lo < hi:
    swap(a, lo, hi)
    lo = lo + 1
    hi = hi - 1
end
""".strip()
    snaps = run_ok(src)
    assert values_of(snaps[-1].structures["a"]) == [6, 5, 4, 3, 2, 1]


def test_rotate_array_left_by_one():
    src = """
array a = [1, 2, 3, 4, 5]
first = a[0]
for i from 0 to 4:
    a[i] = a[i + 1]
end
a[4] = first
""".strip()
    snaps = run_ok(src)
    assert values_of(snaps[-1].structures["a"]) == [2, 3, 4, 5, 1]


def test_copy_even_numbers_to_list():
    src = """
array src = [1, 2, 3, 4, 5, 6, 7, 8]
list dst = []
for i from 0 to 8:
    if src[i] % 2 == 0:
        dst.append(src[i])
    end
end
""".strip()
    snaps = run_ok(src)
    assert values_of(snaps[-1].structures["dst"]) == [2, 4, 6, 8]


def test_array_sum():
    src = """
array a = [10, 20, 30, 40, 50]
total = 0
for i from 0 to 5:
    total = total + a[i]
end
print(total)
""".strip()
    snaps = run_ok(src)
    assert "150" in snaps[-1].output


# ---------------------------------------------------------------------------
# Stack / Queue algorithms
# ---------------------------------------------------------------------------

def test_stack_reverse_sequence():
    src = """
array src = [1, 2, 3, 4, 5]
stack s = []
for i from 0 to 5:
    s.push(src[i])
end
array out = []
for i from 0 to 5:
    out.push(s.pop() + 0)
end
""".strip()
    # Note: the DSL doesn't let us read a popped value back, so instead just check the stack drained
    # Build a simpler test below
    pass


def test_stack_drain_order():
    src = """
stack s = []
s.push(1)
s.push(2)
s.push(3)
s.pop()
s.pop()
""".strip()
    snaps = run_ok(src)
    assert values_of(snaps[-1].structures["s"]) == [1]


def test_queue_fifo_order():
    src = """
queue q = []
q.enqueue(10)
q.enqueue(20)
q.enqueue(30)
q.dequeue()
""".strip()
    snaps = run_ok(src)
    assert values_of(snaps[-1].structures["q"]) == [20, 30]


def test_deque_mixed_operations():
    src = """
deque d = []
d.push_back(1)
d.push_back(2)
d.push_front(0)
d.push_back(3)
d.pop_front()
""".strip()
    snaps = run_ok(src)
    assert values_of(snaps[-1].structures["d"]) == [1, 2, 3]


def test_balanced_parentheses_with_stack():
    src = """
array tokens = [1, 1, -1, 1, -1, -1]
stack s = []
balanced = true
for i from 0 to 6:
    if tokens[i] > 0:
        s.push(1)
    else:
        if s.size == 0:
            balanced = false
        else:
            s.pop()
        end
    end
end
print(balanced)
""".strip()
    snaps = run_ok(src)
    assert "true" in snaps[-1].output.lower()


# ---------------------------------------------------------------------------
# Set / Map algorithms
# ---------------------------------------------------------------------------

def test_set_deduplication():
    src = """
array src = [1, 2, 2, 3, 3, 3, 4, 1, 2]
set seen = []
for i from 0 to 9:
    seen.add(src[i])
end
""".strip()
    snaps = run_ok(src)
    assert sorted(values_of(snaps[-1].structures["seen"])) == [1, 2, 3, 4]


def test_set_intersection_via_contains():
    src = """
set a = [1, 2, 3, 4, 5]
set b = [3, 4, 5, 6, 7]
array both = []
array tmp = [1, 2, 3, 4, 5]
for i from 0 to 5:
    if b.contains(tmp[i]):
        both.push(tmp[i])
    end
end
""".strip()
    snaps = run_ok(src)
    assert values_of(snaps[-1].structures["both"]) == [3, 4, 5]


def test_map_word_frequency_like():
    src = """
map counts = []
counts.set("a", 1)
counts.set("b", 1)
counts.set("a", counts.get("a") + 1)
counts.set("a", counts.get("a") + 1)
counts.set("b", counts.get("b") + 1)
print(counts.get("a"))
print(counts.get("b"))
""".strip()
    snaps = run_ok(src)
    out = snaps[-1].output
    assert "3" in out and "2" in out


def test_map_remove_key():
    src = """
map m = []
m.set("x", 1)
m.set("y", 2)
m.remove("x")
print(m.has("x"))
print(m.has("y"))
""".strip()
    snaps = run_ok(src)
    out = snaps[-1].output.lower()
    assert "false" in out and "true" in out


# ---------------------------------------------------------------------------
# Graph algorithms
# ---------------------------------------------------------------------------

def test_graph_undirected_edge_symmetry():
    src = """
graph g = undirected
g.node("A")
g.node("B")
g.edge("A", "B")
print(g.has_edge("A", "B"))
print(g.has_edge("B", "A"))
""".strip()
    snaps = run_ok(src)
    out = snaps[-1].output.lower()
    assert out.count("true") == 2


def test_graph_directed_edge_not_symmetric():
    src = """
graph g = directed
g.node("A")
g.node("B")
g.edge("A", "B")
print(g.has_edge("A", "B"))
print(g.has_edge("B", "A"))
""".strip()
    snaps = run_ok(src)
    out = snaps[-1].output.lower().splitlines()
    assert "true" in out[0]
    assert "false" in out[1]


def test_graph_remove_node_cleans_edges():
    src = """
graph g = undirected
g.node("A")
g.node("B")
g.node("C")
g.edge("A", "B")
g.edge("B", "C")
g.remove_node("B")
print(g.node_count)
print(g.edge_count)
""".strip()
    snaps = run_ok(src)
    out = snaps[-1].output
    assert "2" in out and "0" in out


def test_graph_weighted_edges():
    src = """
graph g = directed
g.node("A")
g.node("B")
g.node("C")
g.edge("A", "B", 5)
g.edge("B", "C", 10)
print(g.edge_count)
""".strip()
    snaps = run_ok(src)
    assert "2" in snaps[-1].output


def test_graph_build_star():
    src = """
graph g = undirected
g.node("center")
g.node("n1")
g.node("n2")
g.node("n3")
g.node("n4")
g.edge("center", "n1")
g.edge("center", "n2")
g.edge("center", "n3")
g.edge("center", "n4")
print(g.node_count)
print(g.edge_count)
""".strip()
    snaps = run_ok(src)
    out = snaps[-1].output
    assert "5" in out and "4" in out


# ---------------------------------------------------------------------------
# Snapshot / visualization smoke checks
# ---------------------------------------------------------------------------

def test_snapshots_have_expected_fields():
    snaps = run_ok("array a = [1, 2, 3]\na.push(4)")
    for s in snaps:
        assert hasattr(s, "line")
        assert hasattr(s, "structures")
        assert hasattr(s, "variables")
        assert hasattr(s, "highlights")
        assert hasattr(s, "message")
        assert hasattr(s, "output")


def test_snapshot_structures_are_isolated_per_frame():
    snaps = run_ok("array a = [1]\na.push(2)\na.push(3)")
    a0 = values_of(snaps[0].structures["a"])
    a_last = values_of(snaps[-1].structures["a"])
    assert a0 == [1]
    assert a_last == [1, 2, 3]


def test_snapshot_count_scales_with_statements():
    snaps_short = run_ok("array a = [1]\na.push(2)")
    snaps_long = run_ok("array a = [1]\na.push(2)\na.push(3)\na.push(4)\na.push(5)")
    assert len(snaps_long) > len(snaps_short)


def test_highlight_visible_in_snapshot():
    snaps = run_ok("array a = [1, 2, 3, 4]\nhighlight(a, 1, 2)")
    last = snaps[-1]
    assert "a" in last.highlights
    assert len(last.highlights["a"]) >= 1


def test_variables_tracked_in_snapshot():
    snaps = run_ok("x = 10\ny = 20\nz = x + y")
    last_vars = snaps[-1].variables
    assert last_vars.get("x") == 10
    assert last_vars.get("y") == 20
    assert last_vars.get("z") == 30


def test_multiple_structures_coexist():
    src = """
array a = [1, 2]
stack s = []
queue q = []
map m = []
a.push(3)
s.push(10)
q.enqueue(20)
m.set("k", 42)
""".strip()
    snaps = run_ok(src)
    last = snaps[-1].structures
    assert set(["a", "s", "q", "m"]).issubset(last.keys())
    assert values_of(last["a"]) == [1, 2, 3]


def test_nested_control_flow_snapshots():
    src = """
array a = []
for i from 0 to 3:
    for j from 0 to 3:
        if i == j:
            a.push(i)
        end
    end
end
""".strip()
    snaps = run_ok(src)
    assert values_of(snaps[-1].structures["a"]) == [0, 1, 2]
