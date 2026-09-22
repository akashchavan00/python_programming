"""
HARD LEVEL — Generators & Iterators Examples
===============================================
Goal: two-way communication with .send(), generator-based coroutines,
custom lazy classes combining __iter__ with generators, infinite streams
with backpressure-style control, tee'd iterators, and a mini generator-
based state machine. These combine everything from 01_concepts.md.

Run this file directly:  python 04_hard_examples.py
"""

import itertools


# ---------------------------------------------------------------------------
# Example 1: Two-way generators with .send() -- a running-average coroutine
# ---------------------------------------------------------------------------
def running_average():
    """
    A coroutine-style generator: each .send(value) feeds in a new number
    and yields the running average so far. Must be "primed" with next()
    before the first real .send().
    """
    total = 0.0
    count = 0
    average = None
    while True:
        value = yield average
        total += value
        count += 1
        average = total / count


def demo_running_average():
    avg = running_average()
    next(avg)                      # prime it (advances to first `yield`)
    for value in [10, 20, 30, 40]:
        print(f"send({value}) -> running average = {avg.send(value):.2f}")


# ---------------------------------------------------------------------------
# Example 2: A generator-based state machine (traffic light) using .send()
# ---------------------------------------------------------------------------
def traffic_light():
    """
    A tiny state machine driven entirely by generator suspension.
    Sending 'next' advances the light; any other command is ignored.
    """
    state = "RED"
    transitions = {"RED": "GREEN", "GREEN": "YELLOW", "YELLOW": "RED"}
    while True:
        command = yield state
        if command == "next":
            state = transitions[state]


def demo_traffic_light():
    light = traffic_light()
    print(f"initial: {next(light)}")
    for _ in range(4):
        print(f"after 'next': {light.send('next')}")


# ---------------------------------------------------------------------------
# Example 3: A class that is iterable via __iter__ returning a generator
# (the common, idiomatic way to combine classes with generators)
# ---------------------------------------------------------------------------
class PrimeStream:
    """
    An infinite, lazy stream of prime numbers. __iter__ returns a
    generator, so every `for p in PrimeStream()` gets an independent,
    fresh iteration -- unlike a class implementing __next__ directly,
    which would share/mutate state across iterations.
    """
    def __iter__(self):
        primes_found = []
        candidate = 2
        while True:
            if all(candidate % p != 0 for p in primes_found):
                primes_found.append(candidate)
                yield candidate
            candidate += 1


def demo_prime_stream():
    stream = PrimeStream()
    first_10 = list(itertools.islice(stream, 10))
    print(f"first 10 primes: {first_10}")
    # A fresh iteration starts over from scratch -- independent state:
    first_5_again = list(itertools.islice(stream, 5))
    print(f"first 5 primes (new iteration): {first_5_again}")


# ---------------------------------------------------------------------------
# Example 4: itertools.tee -- splitting one iterator into several
# independent ones without re-computing the source
# ---------------------------------------------------------------------------
def expensive_source():
    """Simulates an expensive, single-pass data source."""
    for i in range(1, 6):
        print(f"  [SOURCE] producing {i}")
        yield i


def demo_tee():
    original = expensive_source()
    stream_a, stream_b = itertools.tee(original, 2)

    evens = (x for x in stream_a if x % 2 == 0)
    odds = (x for x in stream_b if x % 2 != 0)

    print("Evens:", list(evens))
    print("Odds :", list(odds))
    # Note: the [SOURCE] print only appears once per value even though we
    # derived two independent filtered streams from it.


# ---------------------------------------------------------------------------
# Example 5: A generator-based context-manager-like resource guard using
# try/finally + .close(), simulating cleanup on early termination
# ---------------------------------------------------------------------------
def managed_resource(name):
    print(f"[RESOURCE] acquiring '{name}'")
    try:
        yield f"handle-to-{name}"
        yield f"still using {name}"
    finally:
        print(f"[RESOURCE] releasing '{name}'")


def demo_managed_resource():
    gen = managed_resource("database-connection")
    handle = next(gen)
    print(f"got: {handle}")
    # Simulate stopping early (e.g. an error occurred) -- .close() still
    # guarantees the `finally` block runs for cleanup.
    gen.close()
    print("generator closed early; cleanup already ran")


# ---------------------------------------------------------------------------
# Example 6: Lazy windowed/batched iteration (sliding window over a stream)
# ---------------------------------------------------------------------------
def sliding_window(iterable, size):
    """Yield overlapping windows of `size` consecutive items, lazily."""
    it = iter(iterable)
    window = tuple(itertools.islice(it, size))
    if len(window) == size:
        yield window
    for item in it:
        window = window[1:] + (item,)
        yield window


def demo_sliding_window():
    data = range(1, 8)
    for w in sliding_window(data, 3):
        print(f"  window: {w}")


if __name__ == "__main__":
    print("=" * 60)
    print("Example 1: two-way generator (.send()) -- running average")
    print("=" * 60)
    demo_running_average()

    print("\n" + "=" * 60)
    print("Example 2: generator-based state machine (traffic light)")
    print("=" * 60)
    demo_traffic_light()

    print("\n" + "=" * 60)
    print("Example 3: infinite lazy prime stream via __iter__")
    print("=" * 60)
    demo_prime_stream()

    print("\n" + "=" * 60)
    print("Example 4: itertools.tee -- independent derived streams")
    print("=" * 60)
    demo_tee()

    print("\n" + "=" * 60)
    print("Example 5: cleanup on early termination with .close()")
    print("=" * 60)
    demo_managed_resource()

    print("\n" + "=" * 60)
    print("Example 6: lazy sliding window over a stream")
    print("=" * 60)
    demo_sliding_window()
