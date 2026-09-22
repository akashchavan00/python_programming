# Python Decorators — Complete Concept Guide

Decorators are one of Python's most powerful features for writing clean,
reusable, and expressive code. This guide covers everything from the
fundamentals to advanced patterns used in real production code.

---

## 1. Prerequisite: Functions Are First-Class Objects

Before understanding decorators, you must understand that in Python,
functions are objects like any other. This means a function can be:

- Assigned to a variable
- Passed as an argument to another function
- Returned from another function
- Stored in data structures (lists, dicts, etc.)

```python
def greet(name):
    return f"Hello, {name}!"

say_hello = greet          # assign function to a variable
print(say_hello("Akash"))  # call it through the new name

def call_it(func, value):  # pass a function as an argument
    return func(value)

print(call_it(greet, "World"))
```

This ability to treat functions as values is what makes decorators possible.

---

## 2. What Is a Decorator?

A decorator is a function that takes another function (or class) as input,
adds some extra behavior to it, and returns a new function (or the same/
modified object) — **without permanently modifying the original function's
source code**.

The classic syntax:

```python
@my_decorator
def say_hello():
    print("Hello!")
```

is exactly equivalent to:

```python
def say_hello():
    print("Hello!")

say_hello = my_decorator(say_hello)
```

The `@` syntax is just "syntactic sugar" — a shorter, more readable way to
write `func = decorator(func)`.

---

## 3. Writing Your First Decorator

```python
def my_decorator(func):
    def wrapper():
        print("Something happens BEFORE the function runs.")
        func()
        print("Something happens AFTER the function runs.")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

say_hello()
# Output:
# Something happens BEFORE the function runs.
# Hello!
# Something happens AFTER the function runs.
```

Key idea: `my_decorator` returns a brand new function (`wrapper`) that
"wraps" the original function, running extra code around the original call.

---

## 4. Handling Arguments: `*args` and `**kwargs`

The simple wrapper above breaks if the decorated function takes arguments,
because `wrapper()` accepts none. The fix is to make `wrapper` accept and
forward any arguments using `*args` and `**kwargs`:

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result!r}")
        return result
    return wrapper

@my_decorator
def add(a, b):
    return a + b

add(2, 3)
```

This pattern (`*args, **kwargs` in the wrapper, and returning the result)
is the standard, reusable template for almost every decorator you'll write.

---

## 5. Preserving Metadata with `functools.wraps`

A decorated function loses its original `__name__`, `__doc__`, and other
metadata, because it has literally become the `wrapper` function:

```python
@my_decorator
def add(a, b):
    """Add two numbers."""
    return a + b

print(add.__name__)  # 'wrapper'  <-- wrong! We want 'add'
print(add.__doc__)   # None       <-- lost the docstring
```

`functools.wraps` fixes this by copying over the original function's
metadata onto the wrapper:

```python
import functools

def my_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

**Rule of thumb: always use `@functools.wraps(func)` on your wrapper
function.** It costs nothing and prevents confusing bugs (broken
introspection, broken documentation tools, broken debuggers).

---

## 6. Decorators That Take Their Own Arguments

Sometimes you want to configure the decorator itself, e.g.
`@retry(times=3)`. This requires an extra outer layer — a
"decorator factory": a function that *returns* a decorator.

```python
import functools

def repeat(times):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(times=3)
def greet(name):
    print(f"Hello, {name}!")

greet("Akash")   # prints "Hello, Akash!" three times
```

There are three levels of nested functions here:
1. `repeat(times)` — the outer factory, takes the decorator's own arguments.
2. `decorator(func)` — the actual decorator, takes the function to wrap.
3. `wrapper(*args, **kwargs)` — the replacement function that runs at call time.

---

## 7. Class-Based Decorators

Instead of a nested function, you can implement a decorator as a class
that defines `__call__`. This is useful when the decorator needs to keep
state across calls (e.g. counting how many times a function was called).

```python
import functools

class CountCalls:
    def __init__(self, func):
        functools.update_wrapper(self, func)  # like functools.wraps, for classes
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"Call #{self.count} of {self.func.__name__}")
        return self.func(*args, **kwargs)

@CountCalls
def say_hi():
    print("Hi!")

say_hi()
say_hi()
print(say_hi.count)  # 2
```

---

## 8. Decorating Class Methods

Decorators work on methods too. The only wrinkle is that instance methods
receive `self` as their first argument, which is automatically handled
because `*args` in the wrapper captures it along with everything else.

```python
def log_call(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        print(f"Calling {func.__name__} on {self!r}")
        return func(self, *args, **kwargs)
    return wrapper

class Account:
    def __init__(self, balance):
        self.balance = balance

    @log_call
    def deposit(self, amount):
        self.balance += amount
```

---

## 9. Built-in Decorators You Already Use

Python ships with several decorators in the standard library:

- **`@staticmethod`** — marks a method that doesn't need `self` or `cls`;
  it behaves like a plain function namespaced inside the class.
- **`@classmethod`** — passes the class itself (`cls`) instead of an
  instance; commonly used for alternative constructors.
- **`@property`** — turns a method into a read-only attribute, enabling
  computed attributes and encapsulation (with `@x.setter` for writes).
- **`@functools.lru_cache(maxsize=None)`** — memoizes a function's return
  values, caching results for previously seen arguments (huge speedup for
  expensive/recursive functions like Fibonacci).
- **`@functools.total_ordering`** — fills in missing comparison methods
  (`__le__`, `__gt__`, `__ge__`) if you define `__eq__` and one of them.
- **`@abc.abstractmethod`** — marks a method that subclasses must override.

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def area(self):
        return 3.14159 * self._radius ** 2

    @staticmethod
    def unit_circle():
        return Circle(1)

    @classmethod
    def from_diameter(cls, diameter):
        return cls(diameter / 2)
```

---

## 10. Chaining Multiple Decorators

You can stack decorators. They apply **bottom-up** (the one closest to the
function runs first, then wraps outward):

```python
@decorator_a
@decorator_b
def func():
    ...

# Equivalent to:
func = decorator_a(decorator_b(func))
```

So `decorator_b` wraps `func` first, and `decorator_a` wraps the result.
When you call `func()`, `decorator_a`'s code runs first (outermost),
then it calls into `decorator_b`'s code, which finally calls the original
`func`.

---

## 11. Common Real-World Use Cases

- **Logging** — record when a function is called and with what arguments.
- **Timing / profiling** — measure how long a function takes to run.
- **Caching / memoization** — avoid redundant expensive computation.
- **Retry logic** — automatically retry a flaky operation (e.g. network
  calls) with optional backoff.
- **Access control / authorization** — check permissions before allowing
  a function to run (common in web frameworks like Flask/Django).
- **Input validation** — check argument types/values before running.
- **Rate limiting** — restrict how often a function can be called.
- **Registration** — collect functions into a registry (plugin systems,
  route handlers in web frameworks like `@app.route("/")`).

---

## 12. Common Pitfalls

1. **Forgetting `*args, **kwargs`** — makes the decorator only work on
   functions with the exact signature you hardcoded.
2. **Forgetting `functools.wraps`** — breaks introspection, `help()`,
   and tools that rely on `__name__`/`__doc__`.
3. **Mutable default state shared across calls** — if a decorator stores
   state (like a cache) at the wrong scope, it can leak between unrelated
   function calls.
4. **Decorator order confusion** — remember decorators apply bottom-up;
   order matters when decorators are not independent of each other
   (e.g. a caching decorator above a logging decorator behaves
   differently than the reverse).
5. **Class-based decorators and multiple instances** — if you decorate a
   method with a class-based decorator, remember the decorator instance
   is shared across *all* instances of the class, not per-instance,
   unless you specifically design around it (descriptors solve this).

---

## 13. Summary Cheat Sheet

| Concept                        | Syntax                                   |
|--------------------------------|-------------------------------------------|
| Basic decorator                | `@decorator` above `def func():`          |
| Decorator with arguments       | `@decorator(arg1, arg2)`                  |
| Preserve metadata               | `@functools.wraps(func)` inside decorator |
| Class-based decorator          | class with `__call__`                     |
| Built-in property              | `@property`, `@x.setter`                  |
| Built-in caching                | `@functools.lru_cache(maxsize=None)`      |
| Chaining                        | Stack `@a` then `@b`; `b` runs first      |

This folder's example files (`02_easy_examples.py`, `03_medium_examples.py`,
`04_hard_examples.py`) put every one of these concepts into runnable code,
from beginner-friendly logging decorators up to production-grade retry and
plugin-registry patterns.
