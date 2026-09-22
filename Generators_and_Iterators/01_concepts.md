# Python Generators & Iterators — Complete Concept Guide

Generators and iterators are the foundation of how Python handles loops,
lazy evaluation, and memory-efficient data processing. Understanding them
deeply also makes `for` loops, comprehensions, and libraries like
`itertools` and `asyncio` make a lot more sense.

---

## 1. The Iterator Protocol

Anything you can loop over with `for x in obj:` is *iterable*. Under the
hood, Python is doing roughly this:

```python
it = iter(obj)        # calls obj.__iter__()
while True:
    try:
        x = next(it)   # calls it.__next__()
    except StopIteration:
        break
    # ... loop body with x ...
```

Two related but distinct concepts:

- **Iterable** — an object with an `__iter__` method that returns an
  iterator (e.g. a `list`, `tuple`, `dict`, `str`, `set`). You can call
  `iter()` on it repeatedly and get fresh iterators each time.
- **Iterator** — an object with both `__iter__` (returning itself) and
  `__next__` (returning the next value, or raising `StopIteration` when
  exhausted). An iterator is "used up" once — you can't restart it.

```python
numbers = [1, 2, 3]          # iterable, NOT an iterator
it = iter(numbers)           # this IS an iterator
print(next(it))              # 1
print(next(it))              # 2
print(next(it))              # 3
next(it)                     # raises StopIteration
```

---

## 2. Writing Your Own Iterator (the manual, verbose way)

```python
class Countdown:
    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self                     # the object is its own iterator

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value

for n in Countdown(3):
    print(n)      # 3, 2, 1
```

This works, but it's a lot of boilerplate just to produce a sequence of
values. Generators exist to make this dramatically simpler.

---

## 3. Generator Functions: `yield`

A generator function looks like a normal function but uses `yield`
instead of (or alongside) `return`. Calling it doesn't run the body —
it returns a **generator object**, which is automatically both an
iterable and an iterator. Each call to `next()` resumes the function
right where it left off, running until the next `yield` (or the function
ends, which raises `StopIteration`).

```python
def countdown(start):
    current = start
    while current > 0:
        yield current
        current -= 1

for n in countdown(3):
    print(n)      # 3, 2, 1
```

Compare this to the `Countdown` class above — same behavior, far less
code. The function's local state (`current`) is automatically preserved
between `yield`s; you don't need `self` or instance attributes.

### What actually happens step by step

```python
gen = countdown(3)     # nothing runs yet — just creates a generator object
print(next(gen))       # runs until first `yield` -> prints 3, returns 3
print(next(gen))       # resumes after yield, loops, yields 2
print(next(gen))       # yields 1
next(gen)              # loop condition now false, function returns -> StopIteration
```

---

## 4. Why Use Generators? Laziness and Memory Efficiency

The biggest reason to use generators is **lazy evaluation** — values are
produced one at a time, on demand, instead of all at once in memory.

```python
# Eager: builds a full list of 10 million numbers in memory
def squares_list(n):
    return [i * i for i in range(n)]

# Lazy: produces one square at a time, using almost no memory
def squares_gen(n):
    for i in range(n):
        yield i * i
```

`squares_list(10_000_000)` allocates a huge list immediately.
`squares_gen(10_000_000)` uses a constant, tiny amount of memory no
matter how large `n` is, because only one value exists at a time.

This is why functions like `range()`, `map()`, `filter()`, `zip()`, and
dict methods like `.keys()`/`.values()`/`.items()` are lazy/iterator-like
in Python 3 — they avoid building intermediate lists.

---

## 5. Generator Expressions

Just like list comprehensions but with `()` instead of `[]`, generator
expressions create a generator without writing a full function:

```python
squares = (i * i for i in range(10))   # generator expression
print(list(squares))                    # [0, 1, 4, 9, ..., 81]

total = sum(i * i for i in range(1_000_000))  # memory-efficient sum
```

Rule of thumb: use a generator expression when you'll consume the values
once (e.g. feed them into `sum()`, `max()`, a `for` loop); use a list
comprehension `[...]` when you need to iterate multiple times, index
into it, or need `len()`.

---

## 6. `yield` Can Receive Values Too (Two-Way Communication)

`yield` is also an expression, not just a statement — it can receive a
value sent into the generator via `.send()`. This turns a generator into
a rudimentary coroutine.

```python
def running_total():
    total = 0
    while True:
        value = yield total      # pauses here, waiting for a value
        total += value

gen = running_total()
next(gen)              # "prime" the generator (run to the first yield)
print(gen.send(10))    # total = 10 -> prints 10
print(gen.send(5))     # total = 15 -> prints 15
print(gen.send(20))    # total = 35 -> prints 35
```

You must call `next(gen)` once first (or `gen.send(None)`) to advance the
generator to its first `yield` before you can `.send()` a real value.

---

## 7. `yield from` — Delegating to a Sub-Generator

`yield from` delegates iteration to another iterable/generator, yielding
all of its values as if they came from the outer generator directly.
It also correctly forwards `.send()`, exceptions, and return values.

```python
def inner():
    yield 1
    yield 2
    return "inner done"

def outer():
    result = yield from inner()   # yields 1, then 2
    print(f"inner returned: {result}")
    yield 3

list(outer())   # prints "inner returned: inner done", yields [1, 2, 3]
```

`yield from` is especially useful for flattening nested generators and
for building generator pipelines (see the medium examples).

---

## 8. Generators Can `return` a Value

A generator's `return value` doesn't come out of `next()` — it's carried
by the `StopIteration` exception (`StopIteration.value`), which is mostly
useful when combined with `yield from`, as shown above.

```python
def gen():
    yield 1
    return "done"

g = gen()
next(g)                 # 1
try:
    next(g)
except StopIteration as e:
    print(e.value)      # "done"
```

---

## 9. Closing and Cleaning Up: `.close()` and `try/finally`

Generators support `.close()`, which raises `GeneratorExit` inside the
generator at its current suspension point — useful for releasing
resources (files, connections) with `try/finally`:

```python
def read_lines(path):
    f = open(path)
    try:
        for line in f:
            yield line.rstrip("\n")
    finally:
        print("closing file")
        f.close()

gen = read_lines("data.txt")
next(gen)
gen.close()   # triggers the finally block even though we stopped early
```

---

## 10. `itertools` — The Standard Library's Generator Toolbox

The `itertools` module provides fast, memory-efficient, composable
building blocks for working with iterators:

- `itertools.count(start, step)` — infinite counter
- `itertools.cycle(iterable)` — repeats a sequence forever
- `itertools.repeat(value, n)` — repeats a value n times (or forever)
- `itertools.chain(a, b, c)` — flattens multiple iterables into one
- `itertools.islice(it, stop)` — slices an iterator lazily (no negative
  indices, unlike list slicing)
- `itertools.takewhile` / `dropwhile` — stop/start consuming based on a
  predicate
- `itertools.groupby` — groups consecutive equal keys
- `itertools.permutations` / `combinations` — combinatorics
- `itertools.tee` — split one iterator into several independent ones

These functions are themselves generators, so they compose with `yield`,
`yield from`, and each other without ever materializing a full list.

---

## 11. Generators vs. Iterators vs. Iterables — Summary

| Term       | Has `__iter__`? | Has `__next__`? | How you make one                          |
|------------|------------------|-------------------|--------------------------------------------|
| Iterable   | Yes              | Not required      | `list`, `dict`, custom `__iter__` class    |
| Iterator   | Yes (returns self)| Yes              | class with `__iter__` + `__next__`, or `iter(iterable)` |
| Generator  | Yes              | Yes               | function with `yield`, or `(x for x in ...)` |

Every generator is an iterator. Every iterator is (trivially) iterable.
Not every iterable is an iterator (a `list` is iterable but you must call
`iter()` on it to get an iterator).

---

## 12. Common Use Cases

- Streaming large files or datasets line-by-line without loading
  everything into memory.
- Infinite sequences (counters, ID generators, sensor readers).
- Data processing pipelines — chaining generators so each stage
  transforms data lazily (`read -> filter -> transform -> aggregate`).
- Implementing custom, memory-safe iteration for your own classes.
- Cooperative coroutine-style patterns (though `async def`/`await` is now
  preferred for real concurrency, understanding generator-based
  coroutines explains *why* `async`/`await` looks the way it does).

## 13. Common Pitfalls

1. **Generators are single-use.** Once exhausted, you must call the
   generator function again to get a fresh one — you cannot "rewind" it.
2. **Forgetting to `next()`-prime a generator before `.send()`.**
3. **Mixing up generator expressions and list comprehensions** when you
   actually need to iterate the result more than once, or need `len()`.
4. **Holding a reference to a huge generator result** by accidentally
   calling `list(huge_generator)`, defeating the whole memory benefit.
5. **Side effects inside a generator that only run when iterated** — code
   after the first `yield` doesn't execute until `next()` is called again,
   which can surprise people expecting eager execution.

---

## 14. Cheat Sheet

| Concept                          | Syntax                                     |
|-----------------------------------|---------------------------------------------|
| Generator function                | `def f(): yield x`                          |
| Generator expression              | `(x for x in iterable)`                     |
| Delegate to sub-generator         | `yield from other_gen()`                    |
| Receive a value                   | `value = yield x`  then `gen.send(value)`   |
| Get a value from a generator's return | `try: next(g) except StopIteration as e: e.value` |
| Manual iterator protocol          | `__iter__` returns self, `__next__` returns/raises |
| Lazy slicing                      | `itertools.islice(it, n)`                   |

This folder's example files put every one of these concepts into runnable
code, from a basic custom range-like generator up to a lazy, chained data
processing pipeline and a two-way coroutine-style generator.
