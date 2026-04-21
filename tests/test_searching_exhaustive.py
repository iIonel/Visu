import random
import pytest
from visu.interpreter import run_source


def _final(src):
    snapshots, error = run_source(src)
    assert error is None, f"Unexpected error: {error}"
    return snapshots[-1]


def _linear_search_src(arr, target):
    vals = ", ".join(str(v) for v in arr)
    return f"""\
array a = [{vals}]
found = -1
for i from 0 to a.length:
    if a[i] == {target}:
        if found == -1:
            found = i
        end
    end
end
"""


def _merge_sorted_src(arr1, arr2):
    v1 = ", ".join(str(v) for v in arr1)
    v2 = ", ".join(str(v) for v in arr2)
    return f"""\
array a = [{v1}]
array b = [{v2}]
array merged = []
i = 0
j = 0
done = false
while done == false:
    if i >= a.length:
        if j >= b.length:
            done = true
        else:
            merged.push(b[j])
            j = j + 1
        end
    else:
        if j >= b.length:
            merged.push(a[i])
            i = i + 1
        else:
            if a[i] <= b[j]:
                merged.push(a[i])
                i = i + 1
            else:
                merged.push(b[j])
                j = j + 1
            end
        end
    end
end
"""


def _make_linear_search_params():
    params = []
    for seed in range(200):
        rng = random.Random(seed)
        size = rng.randint(1, 30)
        arr = [rng.randint(-20, 20) for _ in range(size)]
        target = rng.choice(arr) if rng.random() < 0.7 else rng.randint(-25, 25)
        params.append((arr, target, seed))
    return params


LINEAR_PARAMS = _make_linear_search_params()


@pytest.mark.parametrize("arr,target,seed", LINEAR_PARAMS,
                         ids=[f"lin-seed{p[2]}" for p in LINEAR_PARAMS])
def test_linear_search(arr, target, seed):
    src = _linear_search_src(arr, target)
    s = _final(src)
    found = s.variables["found"]
    if target in arr:
        assert found == arr.index(target), f"Expected {arr.index(target)}, got {found}"
    else:
        assert found == -1


def _make_merge_params():
    params = []
    for seed in range(200):
        rng = random.Random(seed)
        s1 = rng.randint(0, 15)
        s2 = rng.randint(0, 15)
        arr1 = sorted(rng.randint(-50, 50) for _ in range(s1))
        arr2 = sorted(rng.randint(-50, 50) for _ in range(s2))
        params.append((arr1, arr2, seed))
    return params


MERGE_PARAMS = _make_merge_params()


@pytest.mark.parametrize("arr1,arr2,seed", MERGE_PARAMS,
                         ids=[f"merge-seed{p[2]}" for p in MERGE_PARAMS])
def test_merge_sorted(arr1, arr2, seed):
    src = _merge_sorted_src(arr1, arr2)
    s = _final(src)
    result = [item.value for item in s.structures["merged"].items]
    assert result == sorted(arr1 + arr2)


def _count_occurrences_src(arr, target):
    vals = ", ".join(str(v) for v in arr)
    return f"""\
array a = [{vals}]
count = 0
for i from 0 to a.length:
    if a[i] == {target}:
        count = count + 1
    end
end
"""


def _make_count_params():
    params = []
    for seed in range(200):
        rng = random.Random(seed)
        size = rng.randint(1, 25)
        arr = [rng.randint(0, 5) for _ in range(size)]
        target = rng.randint(0, 5)
        params.append((arr, target, seed))
    return params


COUNT_PARAMS = _make_count_params()


@pytest.mark.parametrize("arr,target,seed", COUNT_PARAMS,
                         ids=[f"count-seed{p[2]}" for p in COUNT_PARAMS])
def test_count_occurrences(arr, target, seed):
    src = _count_occurrences_src(arr, target)
    s = _final(src)
    assert s.variables["count"] == arr.count(target)


def _find_min_src(arr):
    vals = ", ".join(str(v) for v in arr)
    return f"""\
array a = [{vals}]
min_val = a[0]
for i from 1 to a.length:
    if a[i] < min_val:
        min_val = a[i]
    end
end
"""


def _find_max_src(arr):
    vals = ", ".join(str(v) for v in arr)
    return f"""\
array a = [{vals}]
max_val = a[0]
for i from 1 to a.length:
    if a[i] > max_val:
        max_val = a[i]
    end
end
"""


def _make_minmax_params():
    params = []
    for seed in range(150):
        rng = random.Random(seed)
        size = rng.randint(1, 30)
        arr = [rng.randint(-100, 100) for _ in range(size)]
        params.append((arr, seed))
    return params


MINMAX_PARAMS = _make_minmax_params()


@pytest.mark.parametrize("arr,seed", MINMAX_PARAMS,
                         ids=[f"min-seed{p[1]}" for p in MINMAX_PARAMS])
def test_find_min(arr, seed):
    src = _find_min_src(arr)
    s = _final(src)
    assert s.variables["min_val"] == min(arr)


@pytest.mark.parametrize("arr,seed", MINMAX_PARAMS,
                         ids=[f"max-seed{p[1]}" for p in MINMAX_PARAMS])
def test_find_max(arr, seed):
    src = _find_max_src(arr)
    s = _final(src)
    assert s.variables["max_val"] == max(arr)


def _sum_src(arr):
    vals = ", ".join(str(v) for v in arr)
    return f"""\
array a = [{vals}]
total = 0
for i from 0 to a.length:
    total = total + a[i]
end
"""


@pytest.mark.parametrize("arr,seed", MINMAX_PARAMS,
                         ids=[f"sum-seed{p[1]}" for p in MINMAX_PARAMS])
def test_sum(arr, seed):
    src = _sum_src(arr)
    s = _final(src)
    assert s.variables["total"] == sum(arr)


def _reverse_src(arr):
    vals = ", ".join(str(v) for v in arr)
    return f"""\
array a = [{vals}]
array b = []
for i from 0 to a.length:
    b.push(a[a.length - 1 - i])
end
"""


@pytest.mark.parametrize("arr,seed", MINMAX_PARAMS,
                         ids=[f"rev-seed{p[1]}" for p in MINMAX_PARAMS])
def test_reverse(arr, seed):
    src = _reverse_src(arr)
    s = _final(src)
    result = [item.value for item in s.structures["b"].items]
    assert result == list(reversed(arr))
