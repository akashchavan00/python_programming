"""
HARD LEVEL — Decorator Examples
==================================
Goal: production-style patterns — retry with exponential backoff, thread
safety, a plugin/registry system, a decorator that works correctly on
both functions AND methods (using a descriptor), a singleton decorator,
and a rate limiter. These combine everything from 01_concepts.md.

Run this file directly:  python 04_hard_examples.py
"""

import functools
import random
import threading
import time


# ---------------------------------------------------------------------------
# Example 1: Retry decorator with exponential backoff and exception filtering
# ---------------------------------------------------------------------------
def retry(max_attempts=3, exceptions=(Exception,), base_delay=0.1, backoff=2):
    """
    Retry the decorated function on failure.

    max_attempts : total attempts before giving up
    exceptions   : tuple of exception types that should trigger a retry
    base_delay   : delay (seconds) before the first retry
    backoff      : multiplier applied to the delay after each failed attempt
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            last_exc = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    print(f"[RETRY] attempt {attempt}/{max_attempts} for "
                          f"'{func.__name__}' failed: {exc}")
                    if attempt < max_attempts:
                        time.sleep(delay)
                        delay *= backoff
            raise last_exc
        return wrapper
    return decorator


# Simulate a flaky network call that fails a couple of times before succeeding
_attempt_counter = {"n": 0}


@retry(max_attempts=4, exceptions=(ConnectionError,), base_delay=0.05)
def flaky_network_call():
    _attempt_counter["n"] += 1
    if _attempt_counter["n"] < 3:
        raise ConnectionError("simulated network blip")
    return "success!"


# ---------------------------------------------------------------------------
# Example 2: Thread-safe rate limiter decorator (token-less, simple window)
# ---------------------------------------------------------------------------
def rate_limited(max_calls, period_seconds):
    """Allow at most `max_calls` calls to func within any `period_seconds` window."""
    def decorator(func):
        lock = threading.Lock()
        call_times = []

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with lock:
                now = time.monotonic()
                # drop timestamps outside the current window
                while call_times and now - call_times[0] > period_seconds:
                    call_times.pop(0)
                if len(call_times) >= max_calls:
                    raise RuntimeError(
                        f"Rate limit exceeded: {max_calls} calls per "
                        f"{period_seconds}s for '{func.__name__}'"
                    )
                call_times.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator


@rate_limited(max_calls=3, period_seconds=1)
def ping():
    return "pong"


# ---------------------------------------------------------------------------
# Example 3: Singleton decorator — only one instance of a class ever exists
# ---------------------------------------------------------------------------
def singleton(cls):
    """Class decorator that turns a class into a singleton."""
    instances = {}
    lock = threading.Lock()

    @functools.wraps(cls, updated=[])
    def get_instance(*args, **kwargs):
        if cls not in instances:
            with lock:
                if cls not in instances:  # double-checked locking
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance


@singleton
class ConfigManager:
    def __init__(self):
        print("[SINGLETON] Creating the one and only ConfigManager")
        self.settings = {}


# ---------------------------------------------------------------------------
# Example 4: Plugin registry pattern using a decorator
# ---------------------------------------------------------------------------
class PluginRegistry:
    """Collects functions into a named registry via decoration."""
    _registry = {}

    @classmethod
    def register(cls, name):
        def decorator(func):
            cls._registry[name] = func
            return func
        return decorator

    @classmethod
    def run(cls, name, *args, **kwargs):
        if name not in cls._registry:
            raise KeyError(f"No plugin registered under {name!r}")
        return cls._registry[name](*args, **kwargs)


@PluginRegistry.register("uppercase")
def to_upper(text):
    return text.upper()


@PluginRegistry.register("reverse")
def reverse_text(text):
    return text[::-1]


# ---------------------------------------------------------------------------
# Example 5: A descriptor-based decorator that works correctly as a bound
# method AND caches results per-instance (unlike a naive class decorator,
# which would share state across all instances).
# ---------------------------------------------------------------------------
class cached_property:
    """
    A from-scratch reimplementation of functools.cached_property to show
    how descriptors let a decorator behave correctly per-instance when
    applied to a method. The computed value is stored on the instance's
    __dict__ the first time it's accessed, so it only runs once per object.
    """
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func

    def __set_name__(self, owner, name):
        self.attr_name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        if self.attr_name not in instance.__dict__:
            print(f"[CACHED_PROPERTY] computing '{self.attr_name}' "
                  f"for {instance!r}")
            instance.__dict__[self.attr_name] = self.func(instance)
        return instance.__dict__[self.attr_name]


class Report:
    def __init__(self, rows):
        self.rows = rows

    @cached_property
    def total(self):
        # Expensive computation only happens once per Report instance
        time.sleep(0.1)
        return sum(self.rows)


# ---------------------------------------------------------------------------
# Example 6: A decorator that validates AND transforms return values,
# combining functools.wraps, *args/**kwargs, and error handling
# ---------------------------------------------------------------------------
def ensure_positive(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if result < 0:
            raise ValueError(
                f"'{func.__name__}' returned a negative value: {result}"
            )
        return result
    return wrapper


@ensure_positive
def account_balance_after_fee(balance, fee):
    return balance - fee


if __name__ == "__main__":
    print("=" * 60)
    print("Example 1: retry with exponential backoff")
    print("=" * 60)
    print(f"Result: {flaky_network_call()}")

    print("\n" + "=" * 60)
    print("Example 2: thread-safe rate limiting")
    print("=" * 60)
    for i in range(3):
        print(f"ping() -> {ping()}")
    try:
        ping()  # 4th call within the same second should be rejected
    except RuntimeError as e:
        print(f"Caught expected error: {e}")

    print("\n" + "=" * 60)
    print("Example 3: singleton class decorator")
    print("=" * 60)
    cfg1 = ConfigManager()
    cfg2 = ConfigManager()
    print(f"cfg1 is cfg2: {cfg1 is cfg2}")  # True -- same instance

    print("\n" + "=" * 60)
    print("Example 4: plugin registry pattern")
    print("=" * 60)
    print(PluginRegistry.run("uppercase", "hello world"))
    print(PluginRegistry.run("reverse", "hello world"))

    print("\n" + "=" * 60)
    print("Example 5: descriptor-based per-instance caching")
    print("=" * 60)
    report_a = Report([1, 2, 3])
    report_b = Report([10, 20, 30])
    print(f"report_a.total = {report_a.total}")  # computes
    print(f"report_a.total = {report_a.total}")  # cached, no recompute
    print(f"report_b.total = {report_b.total}")  # computes separately

    print("\n" + "=" * 60)
    print("Example 6: validating return values")
    print("=" * 60)
    print(f"account_balance_after_fee(100, 20) = {account_balance_after_fee(100, 20)}")
    try:
        account_balance_after_fee(10, 50)
    except ValueError as e:
        print(f"Caught expected error: {e}")
