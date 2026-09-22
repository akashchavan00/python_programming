"""
MEDIUM LEVEL — Generators & Iterators Examples
=================================================
Goal: laziness/memory efficiency, yield from, generator pipelines,
generators that return values, and using itertools. Read 01_concepts.md
sections 4, 5, 7, 8, 10 alongside these examples.

Run this file directly:  python 03_medium_examples.py
"""

import itertools
import sys


# ---------------------------------------------------------------------------
# Example 1: Proving lazy evaluation saves memory (eager list vs generator)
# ---------------------------------------------------------------------------
def squares_list(n):
    return [i * i for i in range(n)]


def squares_gen(n):
    for i in range(n):
        yield i * i


def demo_memory_comparison():
    n = 100_000
    lst = squares_list(n)
    gen = squares_gen(n)
    print(f"List of {n} squares uses  : {sys.getsizeof(lst):,} bytes")
    print(f"Generator object uses     : {sys.getsizeof(gen):,} bytes "
          f"(constant, regardless of n)")


# ---------------------------------------------------------------------------
# Example 2: yield from -- delegating to sub-generators
# ---------------------------------------------------------------------------
def flatten(nested):
    """Recursively flatten an arbitrarily nested list using yield from."""
    for item in nested:
        if isinstance(item, list):
            yield from flatten(item)   # delegate to a recursive sub-generator
        else:
            yield item


# ---------------------------------------------------------------------------
# Example 3: A generator pipeline -- chaining lazy stages together
# ---------------------------------------------------------------------------
def read_records(records):
    """Stage 1: yield raw records one at a time (simulates reading a file)."""
    for r in records:
        yield r


def parse_ints(lines):
    """Stage 2: parse each line into an int, skipping anything invalid."""
    for line in lines:
        try:
            yield int(line)
        except ValueError:
            continue


def filter_positive(numbers):
    """Stage 3: keep only positive numbers."""
    for n in numbers:
        if n > 0:
            yield n


def running_pipeline(raw_data):
    """Compose the stages -- nothing runs until the result is consumed."""
    stage1 = read_records(raw_data)
    stage2 = parse_ints(stage1)
    stage3 = filter_positive(stage2)
    return stage3


# ---------------------------------------------------------------------------
# Example 4: A generator that returns a value, captured via StopIteration
# ---------------------------------------------------------------------------
def sum_until_negative(numbers):
    total = 0
    for n in numbers:
        if n < 0:
            return total   # becomes StopIteration.value
        total += n
        yield n


def demo_generator_return_value():
    gen = sum_until_negative([1, 2, 3, -1, 4])
    values = []
    total = None
    while True:
        try:
            values.append(next(gen))
        except StopIteration as e:
            total = e.value
            break
    print(f"yielded values: {values}")
    print(f"final total (from return): {total}")


# ---------------------------------------------------------------------------
# Example 5: itertools building blocks
# ---------------------------------------------------------------------------
def demo_itertools():
    # islice: lazily take the first N items from a (possibly infinite) iterator
    counter = itertools.count(start=10, step=5)   # infinite: 10, 15, 20, ...
    first_five = list(itertools.islice(counter, 5))
    print(f"itertools.count + islice -> {first_five}")

    # chain: flatten multiple iterables without building a combined list
    combined = list(itertools.chain([1, 2], (3, 4), range(5, 7)))
    print(f"itertools.chain -> {combined}")

    # groupby: group consecutive equal keys (input must be pre-sorted for
    # a "global" group-by effect)
    data = [("fruit", "apple"), ("fruit", "banana"), ("veg", "carrot")]
    for key, group in itertools.groupby(data, key=lambda pair: pair[0]):
        print(f"  group {key!r}: {[item[1] for item in group]}")

    # takewhile / dropwhile
    nums = [1, 3, 5, 8, 9, 11]
    print(f"takewhile(odd) -> {list(itertools.takewhile(lambda x: x % 2 == 1, nums))}")
    print(f"dropwhile(odd) -> {list(itertools.dropwhile(lambda x: x % 2 == 1, nums))}")


if __name__ == "__main__":
    print("=" * 60)
    print("Example 1: memory comparison, list vs generator")
    print("=" * 60)
    demo_memory_comparison()

    print("\n" + "=" * 60)
    print("Example 2: yield from -- flattening nested lists")
    print("=" * 60)
    nested = [1, [2, 3, [4, 5]], 6, [[7, 8], 9]]
    print(f"flatten({nested}) -> {list(flatten(nested))}")

    print("\n" + "=" * 60)
    print("Example 3: generator pipeline")
    print("=" * 60)
    raw_data = ["1", "2", "oops", "-5", "10", "not_a_number", "3"]
    pipeline = running_pipeline(raw_data)
    print(f"raw_data = {raw_data}")
    print(f"pipeline result -> {list(pipeline)}")

    print("\n" + "=" * 60)
    print("Example 4: generator return value via StopIteration")
    print("=" * 60)
    demo_generator_return_value()

    print("\n" + "=" * 60)
    print("Example 5: itertools building blocks")
    print("=" * 60)
    demo_itertools()
