"""
EASY LEVEL — Generators & Iterators Examples
===============================================
Goal: get comfortable with the iterator protocol, basic `yield`, and
generator expressions. Read 01_concepts.md sections 1-5 alongside these.

Run this file directly:  python 02_easy_examples.py
"""


# ---------------------------------------------------------------------------
# Example 1: The manual iterator protocol with iter()/next()
# ---------------------------------------------------------------------------
def demo_iterator_protocol():
    fruits = ["apple", "banana", "cherry"]   # iterable
    it = iter(fruits)                        # get an iterator from it
    print(next(it))
    print(next(it))
    print(next(it))
    try:
        next(it)
    except StopIteration:
        print("No more fruits! StopIteration raised as expected.")


# ---------------------------------------------------------------------------
# Example 2: A simple custom iterator class (the "hard way")
# ---------------------------------------------------------------------------
class Countdown:
    """Counts down from `start` to 1 using the manual iterator protocol."""
    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value


# ---------------------------------------------------------------------------
# Example 3: The same countdown, written as a generator function
# ---------------------------------------------------------------------------
def countdown_gen(start):
    """Counts down from `start` to 1 using yield -- far less code."""
    current = start
    while current > 0:
        yield current
        current -= 1


# ---------------------------------------------------------------------------
# Example 4: A simple "even numbers" generator
# ---------------------------------------------------------------------------
def even_numbers(limit):
    """Yield even numbers from 0 up to (but not including) limit."""
    for n in range(limit):
        if n % 2 == 0:
            yield n


# ---------------------------------------------------------------------------
# Example 5: Generator expressions vs. list comprehensions
# ---------------------------------------------------------------------------
def demo_generator_expression():
    numbers = [1, 2, 3, 4, 5]

    squares_list = [n * n for n in numbers]        # eager: builds full list
    squares_gen = (n * n for n in numbers)          # lazy: builds a generator

    print(f"squares_list = {squares_list}")
    print(f"squares_gen  = {squares_gen}")           # shows <generator object ...>
    print(f"list(squares_gen) = {list(squares_gen)}")  # consuming it materializes values


if __name__ == "__main__":
    print("=" * 60)
    print("Example 1: manual iterator protocol")
    print("=" * 60)
    demo_iterator_protocol()

    print("\n" + "=" * 60)
    print("Example 2: custom iterator class (Countdown)")
    print("=" * 60)
    for n in Countdown(3):
        print(n)

    print("\n" + "=" * 60)
    print("Example 3: the same countdown as a generator function")
    print("=" * 60)
    for n in countdown_gen(3):
        print(n)

    print("\n" + "=" * 60)
    print("Example 4: even numbers generator")
    print("=" * 60)
    print(list(even_numbers(10)))

    print("\n" + "=" * 60)
    print("Example 5: generator expressions vs list comprehensions")
    print("=" * 60)
    demo_generator_expression()
