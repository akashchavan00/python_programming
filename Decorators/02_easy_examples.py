"""
EASY LEVEL — Decorator Examples
=================================
Goal: get comfortable with the basic decorator pattern before moving on
to arguments, factories, and classes. Read 01_concepts.md sections 1-5
alongside these examples.

Run this file directly:  python 02_easy_examples.py
"""

import functools
import time


# ---------------------------------------------------------------------------
# Example 1: The simplest possible decorator (no arguments, no return value)
# ---------------------------------------------------------------------------
def shout(func):
    """Runs func, then prints a farewell message."""
    def wrapper():
        func()
        print("...and that's a wrap!")
    return wrapper


@shout
def say_hello():
    print("Hello there!")


# ---------------------------------------------------------------------------
# Example 2: A decorator that logs when a function starts and finishes
# ---------------------------------------------------------------------------
def log_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[LOG] Starting '{func.__name__}'")
        result = func(*args, **kwargs)
        print(f"[LOG] Finished '{func.__name__}'")
        return result
    return wrapper


@log_calls
def add(a, b):
    """Return the sum of a and b."""
    return a + b


# ---------------------------------------------------------------------------
# Example 3: A simple timing decorator
# ---------------------------------------------------------------------------
def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[TIMER] '{func.__name__}' took {elapsed:.6f} seconds")
        return result
    return wrapper


@timer
def slow_square(n):
    """Pretend to do some work, then return n squared."""
    time.sleep(0.2)
    return n * n


# ---------------------------------------------------------------------------
# Example 4: A decorator that only prints a greeting (no wrapped return value)
# ---------------------------------------------------------------------------
def greet_before(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("Hi! About to run a function for you.")
        return func(*args, **kwargs)
    return wrapper


@greet_before
def farewell(name):
    print(f"Goodbye, {name}!")


# ---------------------------------------------------------------------------
# Example 5: Proving that functools.wraps preserves metadata
# ---------------------------------------------------------------------------
@log_calls
def multiply(a, b):
    """Return the product of a and b."""
    return a * b


if __name__ == "__main__":
    print("=" * 60)
    print("Example 1: basic wrapper")
    print("=" * 60)
    say_hello()

    print("\n" + "=" * 60)
    print("Example 2: logging decorator")
    print("=" * 60)
    result = add(3, 4)
    print(f"add(3, 4) = {result}")

    print("\n" + "=" * 60)
    print("Example 3: timing decorator")
    print("=" * 60)
    result = slow_square(5)
    print(f"slow_square(5) = {result}")

    print("\n" + "=" * 60)
    print("Example 4: greeting decorator")
    print("=" * 60)
    farewell("Akash")

    print("\n" + "=" * 60)
    print("Example 5: functools.wraps preserves metadata")
    print("=" * 60)
    print(f"multiply.__name__ = {multiply.__name__!r}")  # 'multiply', not 'wrapper'
    print(f"multiply.__doc__  = {multiply.__doc__!r}")
    print(f"multiply(6, 7)    = {multiply(6, 7)}")
