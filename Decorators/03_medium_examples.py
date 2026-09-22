"""
MEDIUM LEVEL — Decorator Examples
====================================
Goal: decorators that take their own arguments (decorator factories),
class-based decorators, memoization, chaining, and decorating methods.
Read 01_concepts.md sections 6-10 alongside these examples.

Run this file directly:  python 03_medium_examples.py
"""

import functools
import time


# ---------------------------------------------------------------------------
# Example 1: A decorator factory — a decorator that takes its own arguments
# ---------------------------------------------------------------------------
def repeat(times):
    """Run the decorated function `times` times, returning the last result."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            for i in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator


@repeat(times=3)
def greet(name):
    print(f"Hello, {name}!")


# ---------------------------------------------------------------------------
# Example 2: Manual memoization decorator (before reaching for lru_cache)
# ---------------------------------------------------------------------------
def memoize(func):
    """Cache results keyed by the exact arguments used."""
    cache = {}

    @functools.wraps(func)
    def wrapper(*args):
        if args not in cache:
            print(f"[CACHE MISS] computing {func.__name__}{args}")
            cache[args] = func(*args)
        else:
            print(f"[CACHE HIT]  reusing {func.__name__}{args}")
        return cache[args]
    return wrapper


@memoize
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


# ---------------------------------------------------------------------------
# Example 3: functools.lru_cache — the built-in, production-ready version
# ---------------------------------------------------------------------------
@functools.lru_cache(maxsize=None)
def fib_builtin(n):
    if n < 2:
        return n
    return fib_builtin(n - 1) + fib_builtin(n - 2)


# ---------------------------------------------------------------------------
# Example 4: Class-based decorator that tracks call count (stateful)
# ---------------------------------------------------------------------------
class CountCalls:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"[COUNT] Call #{self.count} to '{self.func.__name__}'")
        return self.func(*args, **kwargs)


@CountCalls
def process_order(order_id):
    print(f"Processing order {order_id}")


# ---------------------------------------------------------------------------
# Example 5: A parametrized "validate_types" decorator
# ---------------------------------------------------------------------------
def validate_types(*expected_types):
    """Raise TypeError if positional args don't match the expected types."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for value, expected in zip(args, expected_types):
                if not isinstance(value, expected):
                    raise TypeError(
                        f"{func.__name__} expected {expected.__name__}, "
                        f"got {type(value).__name__} ({value!r})"
                    )
            return func(*args, **kwargs)
        return wrapper
    return decorator


@validate_types(int, int)
def divide(a, b):
    return a / b


# ---------------------------------------------------------------------------
# Example 6: Chaining decorators — order matters
# ---------------------------------------------------------------------------
def bold(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return f"<b>{func(*args, **kwargs)}</b>"
    return wrapper


def italic(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return f"<i>{func(*args, **kwargs)}</i>"
    return wrapper


@bold
@italic
def render(text):
    return text


# ---------------------------------------------------------------------------
# Example 7: Decorating an instance method
# ---------------------------------------------------------------------------
def log_method(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        print(f"[METHOD] {type(self).__name__}.{func.__name__}"
              f"(args={args}, kwargs={kwargs})")
        return func(self, *args, **kwargs)
    return wrapper


class BankAccount:
    def __init__(self, balance=0):
        self.balance = balance

    @log_method
    def deposit(self, amount):
        self.balance += amount
        return self.balance

    @log_method
    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        return self.balance


if __name__ == "__main__":
    print("=" * 60)
    print("Example 1: decorator factory (repeat)")
    print("=" * 60)
    greet("Akash")

    print("\n" + "=" * 60)
    print("Example 2: manual memoization")
    print("=" * 60)
    print(f"fib(10) = {fib(10)}")
    print(f"fib(10) again -> {fib(10)}")  # should be a cache hit

    print("\n" + "=" * 60)
    print("Example 3: functools.lru_cache")
    print("=" * 60)
    start = time.perf_counter()
    print(f"fib_builtin(28) = {fib_builtin(28)}")
    print(f"elapsed: {time.perf_counter() - start:.6f}s (fast thanks to caching)")

    print("\n" + "=" * 60)
    print("Example 4: class-based stateful decorator")
    print("=" * 60)
    process_order("A100")
    process_order("A101")
    print(f"Total calls so far: {process_order.count}")

    print("\n" + "=" * 60)
    print("Example 5: validating argument types")
    print("=" * 60)
    print(f"divide(10, 2) = {divide(10, 2)}")
    try:
        divide(10, "2")
    except TypeError as e:
        print(f"Caught expected error: {e}")

    print("\n" + "=" * 60)
    print("Example 6: chaining decorators (bottom-up application)")
    print("=" * 60)
    print(render("Hello"))  # italic applied first, then bold wraps it

    print("\n" + "=" * 60)
    print("Example 7: decorating instance methods")
    print("=" * 60)
    account = BankAccount(100)
    account.deposit(50)
    account.withdraw(30)
    print(f"Final balance: {account.balance}")
