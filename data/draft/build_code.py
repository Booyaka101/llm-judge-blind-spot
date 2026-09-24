"""Builds code.json from the item definitions below."""
import json
from pathlib import Path

ITEMS = []


def item(task, code, expl, padded, subtle, subtle_defect, subtle_type,
         obvious, obvious_defect, entry, tests):
    ITEMS.append(dict(task=task, code=code.strip("\n"), expl=expl, padded=padded,
                      subtle=subtle, subtle_defect=subtle_defect,
                      subtle_type=subtle_type, obvious=obvious,
                      obvious_defect=obvious_defect, entry=entry,
                      tests=tests.strip("\n") + "\n"))


def swap_line(code, old, new):
    lines = code.split("\n")
    hits = [i for i, line in enumerate(lines) if line == old]
    assert len(hits) == 1, (old, hits)
    lines[hits[0]] = new
    return "\n".join(lines)


def answer(code, prose):
    return f"```python\n{code}\n```\n\n{prose}"


# 1 ---------------------------------------------------------------------------
item(
    task=(
        "Write a Python function `merge_intervals(intervals)` that takes a list of "
        "`[start, end]` integer pairs (each with start <= end, in any order) and merges "
        "every group of overlapping intervals. Intervals that only touch, where one's end "
        "equals another's start, count as overlapping and must be merged. Return a new "
        "list of `[start, end]` lists sorted by start; an empty input returns `[]`. Do not "
        "modify the input list or its inner lists. Include a short explanation."
    ),
    code='''
def merge_intervals(intervals):
    merged = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged
''',
    expl=(
        "Sorting by start puts every interval that could join the current run immediately "
        "after it. Each interval either extends the last merged interval, when its start is "
        "at or before that interval's end, or starts a new one. Because the comparison is "
        "inclusive, touching intervals such as [1, 4] and [4, 5] merge into [1, 5]. The "
        "output is built from fresh lists, so the caller's intervals are never modified."
    ),
    padded=(
        "The task is to take a list of intervals, combine any of them that overlap or touch, "
        "and hand back the merged result ordered by start. Sorting by start puts every "
        "interval that could join the current run immediately after it. Each interval either "
        "extends the last merged interval, when its start is at or before that interval's "
        "end, or starts a new one. Because the comparison is inclusive, touching intervals "
        "such as [1, 4] and [4, 5] merge into [1, 5]. The output is built from fresh lists, "
        "so the caller's intervals are never modified. Keeping the logic to a single loop "
        "makes the function short and easy to read. "
        "As with any utility like this, it is worth exercising it with a range of inputs, "
        "including edge cases, to confirm it behaves as expected."
    ),
    subtle=("        if merged and start <= merged[-1][1]:",
            "        if merged and start < merged[-1][1]:"),
    subtle_defect=(
        "The merge test uses `start < merged[-1][1]` instead of `<=`, so intervals that only "
        "touch are not merged: `merge_intervals([[1, 4], [4, 5]])` returns `[[1, 4], [4, 5]]` "
        "instead of `[[1, 5]]`, violating the spec. The explanation still claims the "
        "comparison is inclusive."
    ),
    subtle_type="boundary-comparison",
    obvious=("    return merged", "    return intervals"),
    obvious_defect=(
        "The function returns the input `intervals` instead of `merged`, so nothing is ever "
        "merged or sorted."
    ),
    entry="merge_intervals",
    tests=r'''
assert merge_intervals([[1, 3], [2, 6], [8, 10]]) == [[1, 6], [8, 10]]
assert merge_intervals([[1, 4], [4, 5]]) == [[1, 5]]
assert merge_intervals([]) == []
assert merge_intervals([[5, 7], [1, 2]]) == [[1, 2], [5, 7]]
assert merge_intervals([[1, 10], [2, 3], [4, 5]]) == [[1, 10]]
assert merge_intervals([[3, 3]]) == [[3, 3]]
data = [[2, 4], [1, 3], [6, 6], [6, 8]]
assert merge_intervals(data) == [[1, 4], [6, 8]]
assert data == [[2, 4], [1, 3], [6, 6], [6, 8]]
''',
)

# 2 ---------------------------------------------------------------------------
item(
    task=(
        "Write a Python function `moving_average(xs, k)` that returns the mean of every "
        "contiguous window of length `k` in the list of numbers `xs`, in order from left to "
        "right, as floats. There are `len(xs) - k + 1` windows; if `k > len(xs)` return `[]`. "
        "You may assume `k >= 1`. The function should run in O(n) time. Include a short "
        "explanation."
    ),
    code='''
def moving_average(xs, k):
    if k > len(xs):
        return []
    window = sum(xs[:k])
    averages = [window / k]
    for i in range(k, len(xs)):
        window += xs[i] - xs[i - k]
        averages.append(window / k)
    return averages
''',
    expl=(
        "The first window's sum is computed once, and each later window is obtained by adding "
        "the element entering on the right and subtracting the one leaving on the left. That "
        "keeps the whole pass linear instead of re-summing k elements per window. The loop "
        "visits every index from k to the end of the list, so all len(xs) - k + 1 windows are "
        "produced, and a list shorter than k gives an empty result."
    ),
    padded=(
        "The goal is to compute a moving average over a list, producing one mean for each "
        "window of k consecutive values, in left-to-right order. The first window's sum is "
        "computed once, and each later window is obtained by adding the element entering on "
        "the right and subtracting the one leaving on the left. That keeps the whole pass "
        "linear instead of re-summing k elements per window. The loop visits every index from "
        "k to the end of the list, so all len(xs) - k + 1 windows are produced, and a list "
        "shorter than k gives an empty result. Sliding-window techniques like this are a "
        "common pattern and are generally considered good practice. The code is compact and "
        "readable, and it would be sensible to back it with a handful of unit tests covering "
        "typical and boundary inputs."
    ),
    subtle=("    for i in range(k, len(xs)):",
            "    for i in range(k, len(xs) - 1):"),
    subtle_defect=(
        "The loop stops at `len(xs) - 2`, so the final window is never produced: "
        "`moving_average([1, 2, 3, 4, 5], 2)` returns `[1.5, 2.5, 3.5]` instead of "
        "`[1.5, 2.5, 3.5, 4.5]`. The explanation still says every index to the end is visited."
    ),
    subtle_type="off-by-one-range",
    obvious=("    for i in range(k, len(xs)):",
             "    for i in range(k, k):"),
    obvious_defect=(
        "The loop is `range(k, k)`, which is empty, so only the first window's average is "
        "ever returned."
    ),
    entry="moving_average",
    tests=r'''
assert moving_average([1, 2, 3, 4, 5], 2) == [1.5, 2.5, 3.5, 4.5]
assert moving_average([1, 2, 3], 3) == [2.0]
assert moving_average([1, 2], 3) == []
assert moving_average([4], 1) == [4.0]
assert moving_average([2, 4, 6, 8], 1) == [2.0, 4.0, 6.0, 8.0]
assert moving_average([10, 0, 10, 0], 2) == [5.0, 5.0, 5.0]
''',
)

# 3 ---------------------------------------------------------------------------
item(
    task=(
        "Write a Python function `max_drawdown(values)` for a series of numbers such as a "
        "cumulative profit-and-loss curve, so values may be negative or zero. The drawdown at "
        "position j is the largest value at any position i <= j minus `values[j]`. Return the "
        "maximum drawdown over all positions. This is 0 for an empty list, a single value, or "
        "a series that never falls. Include a short explanation."
    ),
    code='''
def max_drawdown(values):
    """Return the largest drop from a running peak to a later value, or 0."""
    peak = float("-inf")
    worst = 0
    for value in values:
        if value > peak:
            peak = value
        elif peak - value > worst:
            worst = peak - value
    return worst
''',
    expl=(
        "The function walks the series once, tracking the highest value seen so far as the "
        "running peak. Whenever a value does not set a new peak, its distance below that peak "
        "is a candidate drawdown and the largest one is kept. Starting the peak at negative "
        "infinity means the first value always becomes the initial peak, so series that are "
        "entirely negative are handled correctly."
    ),
    padded=(
        "Here we need the maximum drawdown of a numeric series, meaning the biggest fall from "
        "an earlier high point to a later value, with 0 when the series never falls. The "
        "function walks the series once, tracking the highest value seen so far as the "
        "running peak. Whenever a value does not set a new peak, its distance below that peak "
        "is a candidate drawdown and the largest one is kept. Starting the peak at negative "
        "infinity means the first value always becomes the initial peak, so series that are "
        "entirely negative are handled correctly. The variable names were chosen to make the "
        "intent clear at a glance. It is a good idea to add tests that cover both "
        "ordinary and unusual series."
    ),
    subtle=('    peak = float("-inf")', "    peak = 0"),
    subtle_defect=(
        "The running peak starts at 0 instead of negative infinity, so a phantom peak of 0 "
        "exists before the first value. For an all-negative series this inflates the result: "
        "`max_drawdown([-5, -3, -10])` returns 10 instead of 7, and `max_drawdown([-2, -1])` "
        "returns 2 instead of 0. The explanation still describes the negative-infinity start."
    ),
    subtle_type="wrong-initial-accumulator",
    obvious=("    return worst", "    return 0"),
    obvious_defect="The function always returns the constant 0, discarding the computed drawdown.",
    entry="max_drawdown",
    tests=r'''
assert max_drawdown([100, 120, 90, 130, 80]) == 50
assert max_drawdown([1, 2, 3]) == 0
assert max_drawdown([]) == 0
assert max_drawdown([5]) == 0
assert max_drawdown([3, 1, 4, 1, 5, 9, 2, 6]) == 7
assert max_drawdown([-5, -3, -10]) == 7
assert max_drawdown([-2, -1]) == 0
''',
)

# 4 ---------------------------------------------------------------------------
item(
    task=(
        "Write a Python function `trimmed_mean(values, trim)` that discards the `trim` "
        "smallest and the `trim` largest numbers from the list `values` and returns the "
        "arithmetic mean of the rest as a float. `trim` is a non-negative integer, and "
        "`trim = 0` means the plain mean. If `2 * trim >= len(values)`, raise `ValueError`. "
        "The caller's list must not be modified, not even reordered. Include a short "
        "explanation."
    ),
    code='''
def trimmed_mean(values, trim):
    """Mean of values after dropping the trim smallest and trim largest."""
    if 2 * trim >= len(values):
        raise ValueError("trim too large for the number of values")
    ordered = list(values)
    ordered.sort()
    kept = ordered[trim:len(ordered) - trim]
    return sum(kept) / len(kept)
''',
    expl=(
        "The function sorts a copy of the input, then slices off trim elements from each end "
        "and averages what is left. The slice uses an explicit upper bound of "
        "len(ordered) - trim rather than -trim, because ordered[0:-0] would be empty when trim "
        "is zero. The guard up front rejects any trim that would leave nothing to average, and "
        "the caller's list keeps its original order."
    ),
    padded=(
        "The request is for a trimmed mean: throw away the most extreme values at both ends "
        "and average whatever remains, without touching the list that was passed in. The "
        "function sorts a copy of the input, then slices off trim elements from each end and "
        "averages what is left. The slice uses an explicit upper bound of len(ordered) - trim "
        "rather than -trim, because ordered[0:-0] would be empty when trim is zero. The guard "
        "up front rejects any trim that would leave nothing to average, and the caller's list "
        "keeps its original order. Writing it in small, clearly named steps keeps the function "
        "approachable for other developers. A few unit tests around the boundaries would be a "
        "sensible addition, as they are for most statistical helpers of this kind."
    ),
    subtle=("    ordered = list(values)", "    ordered = values"),
    subtle_defect=(
        "`ordered = values` aliases the caller's list instead of copying it, so "
        "`ordered.sort()` reorders the caller's list in place, which the spec forbids. The "
        "returned mean is still correct, and the explanation still claims a copy is sorted."
    ),
    subtle_type="input-mutation",
    obvious=("    return sum(kept) / len(kept)", "    return sum(kept)"),
    obvious_defect="The function returns the sum of the kept values, never dividing by their count, so it is not a mean.",
    entry="trimmed_mean",
    tests=r'''
assert trimmed_mean([1, 2, 3, 4, 100], 1) == 3.0
assert trimmed_mean([5, 1, 3], 0) == 3.0
assert trimmed_mean([10, 20], 0) == 15.0
assert trimmed_mean([7, 7, 1, 9], 1) == 7.0
data = [9, 1, 5, 3, 7]
assert trimmed_mean(data, 1) == 5.0
assert data == [9, 1, 5, 3, 7]
for bad in (([1, 2], 1), ([], 0), ([4, 5, 6], 2)):
    try:
        trimmed_mean(*bad)
    except ValueError:
        pass
    else:
        raise AssertionError(f"expected ValueError for {bad}")
''',
)

# 5 ---------------------------------------------------------------------------
item(
    task=(
        "Write a Python function `median(nums)` that returns the median of a list of "
        "integers. For an odd length return the middle element (an int); for an even length "
        "return the mean of the two middle elements as a float, e.g. `median([1, 2]) == 1.5`. "
        "Raise `ValueError` for an empty list, and do not modify the input. Include a short "
        "explanation."
    ),
    code='''
def median(nums):
    if not nums:
        raise ValueError("median of empty list")
    ordered = sorted(nums)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2
''',
    expl=(
        "The values are copied and sorted with sorted(), so the input is untouched. For an odd "
        "count the element at the midpoint index is the median. For an even count the two "
        "elements straddling the midpoint are averaged with true division, which gives 1.5 for "
        "[1, 2] rather than truncating."
    ),
    padded=(
        "The median is the middle value of the data once it is in order, with the two middle "
        "values averaged when there is an even number of them. The values are copied and "
        "sorted with sorted(), so the input is untouched. For an odd count the element at the "
        "midpoint index is the median. For an even count the two elements straddling the "
        "midpoint are averaged with true division, which gives 1.5 for [1, 2] rather than "
        "truncating. The implementation is deliberately simple. Testing with lists of different sizes is a good habit."
    ),
    subtle=("    return (ordered[mid - 1] + ordered[mid]) / 2",
            "    return (ordered[mid - 1] + ordered[mid]) // 2"),
    subtle_defect=(
        "The even-length case uses floor division `// 2`, so the two middle values are "
        "averaged as an integer: `median([1, 2])` returns 1 instead of 1.5 and "
        "`median([4, 1, 3, 2])` returns 2 instead of 2.5. The explanation still claims true "
        "division."
    ),
    subtle_type="integer-division",
    obvious=("        return ordered[mid]", "        return ordered[0]"),
    obvious_defect="For odd-length input it returns `ordered[0]`, the minimum, instead of the middle element.",
    entry="median",
    tests=r'''
assert median([3, 1, 2]) == 2
assert median([4, 1, 3, 2]) == 2.5
assert median([1, 2]) == 1.5
assert median([5]) == 5
assert median([2, 4]) == 3
assert median([-3, -1, 10, 7]) == 3.0
data = [9, 2, 7]
assert median(data) == 7
assert data == [9, 2, 7]
try:
    median([])
except ValueError:
    pass
else:
    raise AssertionError("expected ValueError for empty list")
''',
)

# 6 ---------------------------------------------------------------------------
item(
    task=(
        "Write a Python function `three_way_partition(xs, pivot)` that rearranges the list "
        "`xs` in place, in a single pass, so that all elements less than `pivot` come first, "
        "then all elements equal to `pivot`, then all elements greater than `pivot`. The list "
        "must remain a permutation of its original contents; order within each group does not "
        "matter. Return a tuple `(lt, gt)` such that `xs[:lt]` are the elements less than "
        "`pivot`, `xs[lt:gt]` are equal to it and `xs[gt:]` are greater. Include a short "
        "explanation."
    ),
    code='''
def three_way_partition(xs, pivot):
    low, mid, high = 0, 0, len(xs) - 1
    while mid <= high:
        if xs[mid] < pivot:
            xs[low], xs[mid] = xs[mid], xs[low]
            low += 1
            mid += 1
        elif xs[mid] > pivot:
            xs[mid], xs[high] = xs[high], xs[mid]
            high -= 1
        else:
            mid += 1
    return low, mid
''',
    expl=(
        "This is the Dutch national flag scheme with three pointers: everything before low is "
        "smaller than the pivot, everything from low up to mid equals it, and everything after "
        "high is larger. A smaller element is swapped down to position low, and a larger one "
        "is swapped up to position high without advancing mid, because the element that "
        "arrives at mid has not been examined yet. An equal element is simply stepped over, "
        "and when mid passes high the returned pair marks the two group boundaries."
    ),
    padded=(
        "The task asks for an in-place, single-pass partition of a list into three groups "
        "around a pivot, with the group boundaries returned as a pair. This is the Dutch "
        "national flag scheme with three pointers: everything before low is smaller than the "
        "pivot, everything from low up to mid equals it, and everything after high is larger. "
        "A smaller element is swapped down to position low, and a larger one is swapped up to "
        "position high without advancing mid, because the element that arrives at mid has not "
        "been examined yet. An equal element is simply stepped over, and when mid passes high "
        "the returned pair marks the two group boundaries. Clear pointer names like these make "
        "in-place algorithms much easier to reason about. It is always worth verifying code of "
        "this sort with a variety of test lists before putting it to use."
    ),
    subtle=("            xs[low], xs[mid] = xs[mid], xs[low]",
            "            xs[low], xs[mid] = xs[low], xs[mid]"),
    subtle_defect=(
        "The swap for a smaller element assigns each slot its own value, so it is a no-op: "
        "small elements are never moved down to `low`, yet `low` is still advanced. Whenever "
        "an equal element precedes a smaller one the prefix `xs[:lt]` contains values that are "
        "not less than the pivot, e.g. `[3, 1, 2]` with pivot 2 ends as `[2, 1, 3]` with "
        "`(1, 2)` returned. The explanation still says smaller elements are swapped down."
    ),
    subtle_type="no-op-swap",
    obvious=("    return low, mid", "    return 0, len(xs)"),
    obvious_defect=(
        "It returns the hard-coded bounds `(0, len(xs))`, claiming every element equals the "
        "pivot regardless of the partition it computed."
    ),
    entry="three_way_partition",
    tests=r'''
def _check(values, pivot):
    xs = list(values)
    result = three_way_partition(xs, pivot)
    assert isinstance(result, tuple) and len(result) == 2
    lt, gt = result
    assert sorted(xs) == sorted(values)
    assert all(x < pivot for x in xs[:lt])
    assert all(x == pivot for x in xs[lt:gt])
    assert all(x > pivot for x in xs[gt:])
    assert lt == sum(v < pivot for v in values)
    assert gt == lt + values.count(pivot)

_check([3, 1, 2], 2)
_check([], 5)
_check([1, 2, 3], 10)
_check([2, 2, 2], 2)
_check([5, 1, 4, 2, 3, 2, 6], 3)
_check([9, 8, 7], 1)
''',
)

# 7 ---------------------------------------------------------------------------
item(
    task=(
        "Write a Python function `lower_bound(xs, target)` that, given a list `xs` sorted in "
        "non-decreasing order, uses binary search to return the smallest index `i` such that "
        "`xs[i] >= target`. If every element is less than `target`, including when `xs` is "
        "empty, return `len(xs)`. Include a short explanation."
    ),
    code='''
def lower_bound(xs, target):
    lo, hi = 0, len(xs)
    while lo < hi:
        mid = (lo + hi) // 2
        if xs[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo
''',
    expl=(
        "The search keeps a half-open range [lo, hi) that always contains the answer, starting "
        "with hi = len(xs) so that the past-the-end position is a possible result. If the "
        "middle element is below the target, the answer must lie to its right; otherwise the "
        "middle itself is a candidate and the range shrinks to end there. When lo meets hi the "
        "range has collapsed onto the first index whose element is at least the target."
    ),
    padded=(
        "What is needed is the leftmost position in a sorted list where the target could be "
        "inserted, found with binary search rather than a linear scan. The search keeps a "
        "half-open range [lo, hi) that always contains the answer, starting with hi = len(xs) "
        "so that the past-the-end position is a possible result. If the middle element is "
        "below the target, the answer must lie to its right; otherwise the middle itself is a "
        "candidate and the range shrinks to end there. When lo meets hi the range has "
        "collapsed onto the first index whose element is at least the target. Binary search is "
        "famously easy to get subtly wrong, so writing it carefully and keeping it small pays "
        "off. It is good practice to pair a function like this with thorough tests."
    ),
    subtle=("    lo, hi = 0, len(xs)", "    lo, hi = 0, len(xs) - 1"),
    subtle_defect=(
        "`hi` starts at `len(xs) - 1`, so the past-the-end index can never be returned: "
        "`lower_bound([1, 3, 5, 7], 8)` returns 3 instead of 4. The explanation still says hi "
        "starts at len(xs)."
    ),
    subtle_type="off-by-one-bound",
    obvious=("    return lo", "    return target"),
    obvious_defect="The function returns the target value itself rather than the index it found.",
    entry="lower_bound",
    tests=r'''
assert lower_bound([1, 3, 5, 7], 4) == 2
assert lower_bound([1, 3, 5, 7], 1) == 0
assert lower_bound([1, 3, 5, 7], 7) == 3
assert lower_bound([1, 3, 5, 7], 8) == 4
assert lower_bound([], 5) == 0
assert lower_bound([2, 2, 2], 2) == 0
assert lower_bound([1, 2, 2, 3], 2) == 1
assert lower_bound([1, 3], 0) == 0
''',
)

# 8 ---------------------------------------------------------------------------
item(
    task=(
        "Write a Python function `top_k_words(text, k)` that splits `text` on whitespace, "
        "lowercases each word, and returns the `k` most frequent words as a list of "
        "`(word, count)` tuples. Order by count descending, and break ties by word in "
        "ascending alphabetical order. If there are fewer than `k` distinct words return them "
        "all, and if `k <= 0` return `[]`. Include a short explanation."
    ),
    code='''
def top_k_words(text, k):
    if k <= 0:
        return []
    counts = {}
    for word in text.lower().split():
        counts[word] = counts.get(word, 0) + 1
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return ranked[:k]
''',
    expl=(
        "Words are lowercased and counted in a dictionary in a single pass. Sorting by the key "
        "(-count, word) puts higher counts first and, among equal counts, orders words "
        "alphabetically, so the result is deterministic. Slicing the sorted list returns at "
        "most k pairs, and the early return handles non-positive k, where a negative slice "
        "bound would otherwise drop items from the end instead."
    ),
    padded=(
        "The function should report the k most common words in a piece of text, ignoring "
        "case, along with how often each one occurs. Words are lowercased and counted in a "
        "dictionary in a single pass. Sorting by the key (-count, word) puts higher counts "
        "first and, among equal counts, orders words alphabetically, so the result is "
        "deterministic. Slicing the sorted list returns at most k pairs, and the early return "
        "handles non-positive k, where a negative slice bound would otherwise drop items from "
        "the end instead. Word counting comes up often, and a clear implementation like this "
        "one is easy to adapt and maintain. It is wise to try it on a few sample inputs."
    ),
    subtle=("    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))",
            "    ranked = sorted(counts.items(), key=lambda item: (item[1], item[0]), reverse=True)"),
    subtle_defect=(
        "Sorting on `(count, word)` with `reverse=True` reverses the tie-break too, so equal "
        "counts come out in descending alphabetical order: `top_k_words('b a c b a', 2)` "
        "returns `[('b', 2), ('a', 2)]` instead of `[('a', 2), ('b', 2)]`. The explanation "
        "still describes the `(-count, word)` key."
    ),
    subtle_type="tie-break-order",
    obvious=("    return ranked[:k]", "    return ranked"),
    obvious_defect="It returns the whole ranked list, ignoring `k` entirely.",
    entry="top_k_words",
    tests=r'''
assert top_k_words("the cat the dog the cat", 2) == [("the", 3), ("cat", 2)]
assert top_k_words("b a c b a", 2) == [("a", 2), ("b", 2)]
assert top_k_words("Apple apple BANANA", 5) == [("apple", 2), ("banana", 1)]
assert top_k_words("", 3) == []
assert top_k_words("x y", 0) == []
assert top_k_words("x y z", -1) == []
assert top_k_words("z y x", 2) == [("x", 1), ("y", 1)]
assert top_k_words("  one\ttwo\n two  ", 1) == [("two", 2)]
''',
)

# 9 ---------------------------------------------------------------------------
item(
    task=(
        "Write a Python function `group_by(items, key_fn, into=None)` that groups `items` by "
        "`key_fn(item)`, returning a dict that maps each key to a list of the items with that "
        "key, in their original order. If `into` is given, add to that dict (appending to any "
        "existing lists) and return it. If `into` is omitted, every call must start from a "
        "fresh empty dict. Include a short explanation."
    ),
    code='''
def group_by(items, key_fn, into=None):
    groups = into if into is not None else {}
    for item in items:
        key = key_fn(item)
        if key not in groups:
            groups[key] = []
        groups[key].append(item)
    return groups
''',
    expl=(
        "The function picks its target dict up front: the caller's dict when one is passed, "
        "otherwise a new one created on this call. Each item's key is computed once, an empty "
        "list is created the first time a key appears, and the item is appended, which "
        "preserves input order within each group. Because the default is None rather than a "
        "dict literal, separate calls without into never share state."
    ),
    padded=(
        "The job here is to bucket a sequence of items by a key function, optionally adding "
        "to a dictionary the caller already has. The function picks its target dict up front: "
        "the caller's dict when one is passed, otherwise a new one created on this call. Each "
        "item's key is computed once, an empty list is created the first time a key appears, "
        "and the item is appended, which preserves input order within each group. Because the "
        "default is None rather than a dict literal, separate calls without into never share "
        "state. Grouping helpers like this show up in many codebases, and keeping them small "
        "and explicit makes them easy to trust. A couple of quick tests, including repeated "
        "calls, would round it off nicely."
    ),
    subtle=("def group_by(items, key_fn, into=None):",
            "def group_by(items, key_fn, into={}):"),
    subtle_defect=(
        "The default for `into` is a single dict literal created once at definition time, so "
        "`into is not None` is always true and every call that omits `into` appends to the "
        "same shared dict: after `group_by([1, 2, 3, 4], lambda n: n % 2)`, a call "
        "`group_by(['a', 'bb', 'c'], len)` returns `{1: [1, 3, 'a', 'c'], 0: [2, 4], 2: ['bb']}`. "
        "The explanation still claims the default is None."
    ),
    subtle_type="mutable-default-argument",
    obvious=("    return groups", "    return into"),
    obvious_defect="It returns `into` instead of `groups`, so any call without `into` returns None.",
    entry="group_by",
    tests=r'''
first = group_by([1, 2, 3, 4], lambda n: n % 2)
assert first == {1: [1, 3], 0: [2, 4]}
second = group_by(["a", "bb", "c"], len)
assert second == {1: ["a", "c"], 2: ["bb"]}
assert group_by([], len) == {}
target = {"x": [0]}
result = group_by([5, 6], lambda _: "x", target)
assert result is target
assert target == {"x": [0, 5, 6]}
assert list(group_by("banana", lambda c: c)) == ["b", "a", "n"]
''',
)

# 10 --------------------------------------------------------------------------
item(
    task=(
        "Write a Python function `first_unique(nums)` that returns the element of the list of "
        "integers `nums` that occurs exactly once and appears earliest in the list by "
        "position. Return `None` if no element occurs exactly once, including for an empty "
        "list. Include a short explanation."
    ),
    code='''
def first_unique(nums):
    """Return the earliest element of nums that occurs exactly once, or None."""
    counts = {}
    for x in nums:
        counts[x] = counts.get(x, 0) + 1
    for x in nums:
        if counts[x] == 1:
            return x
    return None
''',
    expl=(
        "A first pass counts how often each value occurs. The second pass walks nums in its "
        "original order and returns the first value whose count is exactly one, which is by "
        "construction the earliest unique element. If the walk finishes without a match there "
        "is no unique element and None is returned."
    ),
    padded=(
        "We are looking for the first number in the list, reading from the left, that appears "
        "only once, or None when there is no such number. A first pass counts how often each "
        "value occurs. The second pass walks nums in its original order and returns the first "
        "value whose count is exactly one, which is by construction the earliest unique "
        "element. If the walk finishes without a match there is no unique element and None is "
        "returned. Two simple loops keep each step easy to follow. "
        "It is a good idea to confirm the behaviour with a few small example lists."
    ),
    subtle=("    for x in nums:\n        if counts[x] == 1:", None),
    subtle_defect=(
        "The second loop iterates over `set(nums)`, whose order is unrelated to list position "
        "(for small ints CPython yields them roughly in ascending order), so it returns some "
        "unique element rather than the earliest: `first_unique([5, 3, 5, 1])` returns 1 "
        "instead of 3. The explanation still says the loop walks nums in original order."
    ),
    subtle_type="unordered-iteration",
    obvious=("        if counts[x] == 1:", "        if counts[x] > 1:"),
    obvious_defect="The check is `counts[x] > 1`, so it returns the first repeated element instead of the first unique one.",
    entry="first_unique",
    tests=r'''
assert first_unique([5, 3, 5, 1]) == 3
assert first_unique([2, 2]) is None
assert first_unique([]) is None
assert first_unique([7]) == 7
assert first_unique([4, 4, 9, 8, 9]) == 8
assert first_unique([6, 1, 6, 2, 1]) == 2
''',
)

# 11 --------------------------------------------------------------------------
item(
    task=(
        "Write a Python function `parse_duration(text)` that converts a duration string such "
        "as `'1h30m15s'` to a whole number of seconds. The string has up to three parts in the "
        "fixed order hours (`h`), minutes (`m`), seconds (`s`). Each part is a non-negative "
        "integer immediately followed by its unit letter; any part may be omitted but at least "
        "one must be present, and nothing else is allowed (no spaces, signs, decimals or other "
        "characters). Raise `ValueError` for any string that does not match this format "
        "exactly. Include a short explanation."
    ),
    code='''
import re

_PATTERN = re.compile(r"(?:(\\d+)h)?(?:(\\d+)m)?(?:(\\d+)s)?")


def parse_duration(text):
    match = _PATTERN.fullmatch(text)
    if not text or match is None:
        raise ValueError(f"invalid duration: {text!r}")
    hours, minutes, seconds = (int(g) if g else 0 for g in match.groups())
    return hours * 3600 + minutes * 60 + seconds
''',
    expl=(
        "A single regular expression describes the whole format, with each unit as an "
        "optional group in the required order. fullmatch ensures the entire string conforms, "
        "so trailing junk or out-of-order units are rejected, and the empty string, which the "
        "all-optional pattern would otherwise accept, is rejected explicitly. Missing parts "
        "default to zero before hours, minutes and seconds are combined into a total."
    ),
    padded=(
        "The function has to turn compact duration strings like 1h30m15s into a number of "
        "seconds and reject anything that does not follow the format. A single regular "
        "expression describes the whole format, with each unit as an optional group in the "
        "required order. fullmatch ensures the entire string conforms, so trailing junk or "
        "out-of-order units are rejected, and the empty string, which the all-optional "
        "pattern would otherwise accept, is rejected explicitly. Missing parts default to zero "
        "before hours, minutes and seconds are combined into a total. Compiling the pattern "
        "once at module level is a common and tidy way to organise this kind of parser. "
        "Parsers deserve careful testing, so it would be worth checking a mix of valid and "
        "invalid strings."
    ),
    subtle=("    match = _PATTERN.fullmatch(text)", "    match = _PATTERN.match(text)"),
    subtle_defect=(
        "`re.match` only anchors at the start, and because every group is optional it always "
        "succeeds on a non-empty string, so malformed input is silently accepted: "
        "`parse_duration('1h30x')` returns 3600, `parse_duration('5m ')` returns 300 and "
        "`parse_duration('abc')` returns 0 instead of raising ValueError. The explanation still "
        "claims fullmatch is used."
    ),
    subtle_type="partial-match-anchoring",
    obvious=("    return hours * 3600 + minutes * 60 + seconds",
             "    return hours + minutes + seconds"),
    obvious_defect="It adds the raw numbers without unit multipliers, so '1h30m' gives 31 instead of 5400.",
    entry="parse_duration",
    tests=r'''
assert parse_duration("1h30m15s") == 5415
assert parse_duration("45s") == 45
assert parse_duration("2h") == 7200
assert parse_duration("90m") == 5400
assert parse_duration("1h5s") == 3605
assert parse_duration("0s") == 0
for bad in ["", "abc", "1h30x", "30s1h", "1.5h", " 5m", "5m "]:
    try:
        parse_duration(bad)
    except ValueError:
        pass
    else:
        raise AssertionError(f"expected ValueError for {bad!r}")
''',
)

# 12 --------------------------------------------------------------------------
item(
    task=(
        "Write a Python function `is_balanced(s)` that returns `True` if every bracket in the "
        "string `s` is properly matched and nested, considering the pairs `()`, `[]` and `{}`, "
        "and `False` otherwise. All other characters are ignored, and the empty string is "
        "balanced. Include a short explanation."
    ),
    code='''
def is_balanced(s):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack
''',
    expl=(
        "Opening brackets are pushed onto a stack, and each closing bracket must match the "
        "most recent unmatched opener, which is popped. A closer that arrives with an empty "
        "stack or pairs with the wrong opener fails immediately. After the scan the string is "
        "balanced only if the stack is empty, since any opener still on it was never closed."
    ),
    padded=(
        "The question is whether the brackets in a string are correctly paired and nested, "
        "with every other character ignored. Opening brackets are pushed onto a stack, and "
        "each closing bracket must match the most recent unmatched opener, which is popped. A "
        "closer that arrives with an empty stack or pairs with the wrong opener fails "
        "immediately. After the scan the string is balanced only if the stack is empty, since "
        "any opener still on it was never closed. The stack-based approach is the classic "
        "technique for this problem and is widely recognised by other developers. As a "
        "general habit, running it against a handful of balanced and unbalanced samples is a "
        "sensible way to gain confidence in it."
    ),
    subtle=("    return not stack", "    return True"),
    subtle_defect=(
        "The final line returns True unconditionally instead of checking that the stack is "
        "empty, so unclosed openers are accepted: `is_balanced('(()')` and `is_balanced('[')` "
        "return True. The explanation still says the stack must be empty."
    ),
    subtle_type="missing-final-check",
    obvious=('        if ch in "([{":', '        if ch in ")]}":'),
    obvious_defect=(
        "The push branch tests for closing brackets instead of opening ones, so openers are "
        "ignored and closers are pushed; even '()' returns False."
    ),
    entry="is_balanced",
    tests=r'''
assert is_balanced("") is True
assert is_balanced("()[]{}") is True
assert is_balanced("{[()()]}") is True
assert is_balanced("f(a[i]) + {x}") is True
assert is_balanced("(]") is False
assert is_balanced("([)]") is False
assert is_balanced(")(") is False
assert is_balanced("(()") is False
assert is_balanced("[") is False
''',
)

# 13 --------------------------------------------------------------------------
item(
    task=(
        "Write a Python function `flatten(nested)` that takes a list whose elements may be "
        "lists or tuples nested to any depth, and returns a new flat list of all elements "
        "that are neither lists nor tuples, in left-to-right order. Strings and every other "
        "type count as single elements, and empty sublists contribute nothing. Include a "
        "short explanation."
    ),
    code='''
def flatten(nested):
    """Return a flat list of the non-list, non-tuple leaves of nested, in order."""
    flat = []
    for item in nested:
        if isinstance(item, (list, tuple)):
            flat.extend(flatten(item))
        else:
            flat.append(item)
    return flat
''',
    expl=(
        "The function walks the top-level items, recursing into any list or tuple and "
        "extending the output with the flattened result. Anything else, strings included, is "
        "appended as a single element, which keeps strings from being split into characters. "
        "Order is preserved because items are processed left to right and each recursive "
        "result is spliced in where its container was."
    ),
    padded=(
        "Flattening means taking an arbitrarily nested structure of lists and tuples and "
        "producing a single list of the values inside it. The function walks the top-level "
        "items, recursing into any list or tuple and extending the output with the flattened "
        "result. Anything else, strings included, is appended as a single element, which keeps "
        "strings from being split into characters. Order is preserved because items are "
        "processed left to right and each recursive result is spliced in where its container "
        "was. Recursion maps naturally onto nested data, which keeps the code short and "
        "readable. It is good practice to test a function like this on several shapes of "
        "input before relying on it."
    ),
    subtle=("        if isinstance(item, (list, tuple)):",
            "        if isinstance(item, list):"),
    subtle_defect=(
        "The type check only matches `list`, so tuples are appended whole instead of being "
        "flattened: `flatten([1, (2, 3)])` returns `[1, (2, 3)]` instead of `[1, 2, 3]`. The "
        "explanation still says the function recurses into any list or tuple."
    ),
    subtle_type="type-check-too-narrow",
    obvious=("            flat.extend(flatten(item))", "            flat.append(item)"),
    obvious_defect=(
        "The container branch appends the sublist as-is instead of recursing, so both branches "
        "do the same thing and nothing is flattened."
    ),
    entry="flatten",
    tests=r'''
assert flatten([1, [2, [3, 4]], 5]) == [1, 2, 3, 4, 5]
assert flatten([]) == []
assert flatten([[], [[]]]) == []
assert flatten([1, (2, 3), [4, (5, [6])]]) == [1, 2, 3, 4, 5, 6]
assert flatten(["ab", ["c"]]) == ["ab", "c"]
assert flatten([(1, 2)]) == [1, 2]
assert flatten([0, None, [False]]) == [0, None, False]
''',
)

# 14 --------------------------------------------------------------------------
item(
    task=(
        "Write a Python function `two_sum(nums, target)` that returns a tuple of indices "
        "`(i, j)` with `i < j` and `nums[i] + nums[j] == target`. If several pairs qualify, "
        "return the one with the smallest `j`, and among those the smallest `i`. An element "
        "cannot be paired with itself. Return `None` if there is no such pair. Use a single "
        "pass with a dictionary. Include a short explanation."
    ),
    code='''
def two_sum(nums, target):
    """Indices (i, j), i < j, of the earliest pair summing to target, or None."""
    seen = {}
    for j, x in enumerate(nums):
        i = seen.get(target - x)
        if i is not None:
            return i, j
        seen.setdefault(x, j)
    return None
''',
    expl=(
        "The dictionary maps each value to the first index where it appeared. For each "
        "position j the function looks up the complement target - x among earlier elements "
        "only, so an element is never paired with itself and the first hit has the smallest "
        "possible j. setdefault keeps the earliest index for repeated values, which makes i "
        "the smallest partner for that j."
    ),
    padded=(
        "This is the familiar two-sum problem: find two different positions in the list whose "
        "values add up to the target, preferring the earliest such pair. The dictionary maps "
        "each value to the first index where it appeared. For each position j the function "
        "looks up the complement target - x among earlier elements only, so an element is "
        "never paired with itself and the first hit has the smallest possible j. setdefault "
        "keeps the earliest index for repeated values, which makes i the smallest partner for "
        "that j. Using a dictionary like this is a well-known idiom that most Python developers "
        "will recognise immediately. Covering it with a few straightforward tests is, as "
        "usual, a worthwhile step."
    ),
    subtle=("        if i is not None:", "        if i:"),
    subtle_defect=(
        "`if i:` treats index 0 as missing because 0 is falsy, so any pair whose first element "
        "is at index 0 is skipped: `two_sum([2, 7, 11, 15], 9)` returns None instead of "
        "`(0, 1)`."
    ),
    subtle_type="falsy-zero-check",
    obvious=("            return i, j", "            return None"),
    obvious_defect="When a pair is found the function returns None instead of the indices, so it can never return a pair.",
    entry="two_sum",
    tests=r'''
assert two_sum([2, 7, 11, 15], 9) == (0, 1)
assert two_sum([3, 2, 4], 6) == (1, 2)
assert two_sum([3, 3], 6) == (0, 1)
assert two_sum([1, 2, 3], 7) is None
assert two_sum([], 0) is None
assert two_sum([5], 10) is None
assert two_sum([2, 5, 3, 2], 4) == (0, 3)
assert two_sum([1, 4, 1, 4], 5) == (0, 1)
''',
)


def main():
    out = []
    for n, it in enumerate(ITEMS, 1):
        code = it["code"]
        old, new = it["subtle"]
        if new is None:
            subtle_code = code.replace("    for x in nums:\n        if counts[x] == 1:",
                                       "    for x in set(nums):\n        if counts[x] == 1:")
            assert subtle_code != code
        else:
            subtle_code = swap_line(code, old, new)
        obvious_code = swap_line(code, *it["obvious"])
        out.append({
            "id": f"code-{n:02d}",
            "domain": "code",
            "task": it["task"],
            "clean": answer(code, it["expl"]),
            "subtle": answer(subtle_code, it["expl"]),
            "subtle_defect": it["subtle_defect"],
            "subtle_defect_type": it["subtle_type"],
            "obvious": answer(obvious_code, it["expl"]),
            "obvious_defect": it["obvious_defect"],
            "padded": answer(code, it["padded"]),
            "verify": {"entry_point": it["entry"], "tests": it["tests"]},
        })
    path = Path(__file__).with_name("code.json")
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(out)} items to {path}")


if __name__ == "__main__":
    main()
