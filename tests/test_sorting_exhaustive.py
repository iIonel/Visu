import random
import pytest
from visu.interpreter import run_source

SEED_BASE = 42

def _random_array(seed, size, lo=-100, hi=100):
    rng = random.Random(seed)
    return [rng.randint(lo, hi) for _ in range(size)]

def _bubble_sort_src(arr):
    vals = ", ".join(str(v) for v in arr)
    return f"""\
array a = [{vals}]
for i from 0 to a.length:
    for j from 0 to a.length - 1:
        if a[j] > a[j + 1]:
            swap(a, j, j + 1)
        end
    end
end
"""

def _selection_sort_src(arr):
    vals = ", ".join(str(v) for v in arr)
    return f"""\
array a = [{vals}]
for i from 0 to a.length:
    min_idx = i
    for j from i to a.length:
        if a[j] < a[min_idx]:
            min_idx = j
        end
    end
    if min_idx != i:
        swap(a, i, min_idx)
    end
end
"""

def _insertion_sort_src(arr):
    vals = ", ".join(str(v) for v in arr)
    return f"""\
array a = [{vals}]
if a.length > 1:
    for i from 1 to a.length:
        key = a[i]
        j = i - 1
        done = false
        while done == false:
            if j >= 0:
                if a[j] > key:
                    a[j + 1] = a[j]
                    j = j - 1
                else:
                    done = true
                end
            else:
                done = true
            end
        end
        a[j + 1] = key
    end
end
"""

SORT_ALGOS = [
    ("bubble", _bubble_sort_src),
    ("selection", _selection_sort_src),
    ("insertion", _insertion_sort_src),
]

SMALL_SIZES = list(range(0, 8))
MEDIUM_SIZES = [10, 15, 20, 25, 30]

def _make_sort_params():
    params = []
    for algo_name, algo_fn in SORT_ALGOS:
        for size in SMALL_SIZES:
            for seed in range(80):
                params.append((algo_name, algo_fn, seed, size))
        for size in MEDIUM_SIZES:
            for seed in range(40):
                params.append((algo_name, algo_fn, seed + 1000, size))
    return params

SORT_PARAMS = _make_sort_params()

@pytest.mark.parametrize("algo_name,algo_fn,seed,size", SORT_PARAMS,
                         ids=[f"{p[0]}-seed{p[2]}-n{p[3]}" for p in SORT_PARAMS])
def test_sort_correctness(algo_name, algo_fn, seed, size):
    arr = _random_array(seed, size)
    src = algo_fn(arr)
    snapshots, error = run_source(src)
    assert error is None, f"{algo_name} error on {arr}: {error}"
    assert len(snapshots) > 0
    final = snapshots[-1]
    if size == 0:
        return
    result = [final.structures["a"].items[i].value for i in range(len(final.structures["a"].items))]
    assert result == sorted(arr), f"{algo_name} failed: input={arr}, got={result}"

def _make_already_sorted_params():
    params = []
    for algo_name, algo_fn in SORT_ALGOS:
        for size in range(1, 20):
            params.append((algo_name, algo_fn, size, "asc"))
            params.append((algo_name, algo_fn, size, "desc"))
    return params

PRESORTED_PARAMS = _make_already_sorted_params()

@pytest.mark.parametrize("algo_name,algo_fn,size,order", PRESORTED_PARAMS,
                         ids=[f"{p[0]}-{p[3]}-n{p[2]}" for p in PRESORTED_PARAMS])
def test_sort_presorted(algo_name, algo_fn, size, order):
    if order == "asc":
        arr = list(range(size))
    else:
        arr = list(range(size, 0, -1))
    src = algo_fn(arr)
    snapshots, error = run_source(src)
    assert error is None
    result = [snapshots[-1].structures["a"].items[i].value for i in range(size)]
    assert result == sorted(arr)

def _make_duplicates_params():
    params = []
    for algo_name, algo_fn in SORT_ALGOS:
        for seed in range(60):
            rng = random.Random(seed + 5000)
            size = rng.randint(2, 20)
            val = rng.randint(-10, 10)
            arr = [val] * size
            params.append((algo_name, algo_fn, arr))
    return params

DUPS_PARAMS = _make_duplicates_params()

@pytest.mark.parametrize("algo_name,algo_fn,arr", DUPS_PARAMS,
                         ids=[f"{p[0]}-allsame-n{len(p[2])}" for p in DUPS_PARAMS])
def test_sort_all_duplicates(algo_name, algo_fn, arr):
    src = algo_fn(arr)
    snapshots, error = run_source(src)
    assert error is None
    result = [snapshots[-1].structures["a"].items[i].value for i in range(len(arr))]
    assert result == sorted(arr)

def _make_negative_params():
    params = []
    for algo_name, algo_fn in SORT_ALGOS:
        for seed in range(50):
            arr = _random_array(seed + 9000, random.Random(seed).randint(2, 15), -1000, -1)
            params.append((algo_name, algo_fn, arr))
    return params

NEG_PARAMS = _make_negative_params()

@pytest.mark.parametrize("algo_name,algo_fn,arr", NEG_PARAMS,
                         ids=[f"{p[0]}-neg-n{len(p[2])}" for p in NEG_PARAMS])
def test_sort_all_negative(algo_name, algo_fn, arr):
    src = algo_fn(arr)
    snapshots, error = run_source(src)
    assert error is None
    result = [snapshots[-1].structures["a"].items[i].value for i in range(len(arr))]
    assert result == sorted(arr)

def _make_single_element_params():
    params = []
    for algo_name, algo_fn in SORT_ALGOS:
        for val in range(-20, 21):
            params.append((algo_name, algo_fn, val))
    return params

SINGLE_PARAMS = _make_single_element_params()

@pytest.mark.parametrize("algo_name,algo_fn,val", SINGLE_PARAMS,
                         ids=[f"{p[0]}-single-{p[2]}" for p in SINGLE_PARAMS])
def test_sort_single_element(algo_name, algo_fn, val):
    src = algo_fn([val])
    snapshots, error = run_source(src)
    assert error is None
    result = [snapshots[-1].structures["a"].items[0].value]
    assert result == [val]

def _make_two_element_params():
    params = []
    for algo_name, algo_fn in SORT_ALGOS:
        for a in range(-5, 6):
            for b in range(-5, 6):
                params.append((algo_name, algo_fn, a, b))
    return params

TWO_PARAMS = _make_two_element_params()

@pytest.mark.parametrize("algo_name,algo_fn,a,b", TWO_PARAMS,
                         ids=[f"{p[0]}-two-{p[2]}_{p[3]}" for p in TWO_PARAMS])
def test_sort_two_elements(algo_name, algo_fn, a, b):
    src = algo_fn([a, b])
    snapshots, error = run_source(src)
    assert error is None
    result = [snapshots[-1].structures["a"].items[i].value for i in range(2)]
    assert result == sorted([a, b])
