# Decorators

Topic folder for learning Python decorators, from fundamentals to
production-grade patterns.

## Contents

- **01_concepts.md** — full written explanation of every decorator concept:
  first-class functions, basic decorators, `*args`/`**kwargs`,
  `functools.wraps`, decorator factories, class-based decorators,
  decorating methods, built-in decorators (`@property`, `@staticmethod`,
  `@classmethod`, `@lru_cache`), chaining, use cases, and pitfalls.
- **02_easy_examples.py** — beginner-friendly, runnable examples: a basic
  wrapper, a logging decorator, a timer, and proof that `functools.wraps`
  preserves metadata.
- **03_medium_examples.py** — decorator factories (arguments to the
  decorator itself), manual memoization vs. `functools.lru_cache`,
  a stateful class-based decorator, argument validation, chaining
  multiple decorators, and decorating instance methods.
- **04_hard_examples.py** — production-style patterns: retry with
  exponential backoff, a thread-safe rate limiter, a singleton class
  decorator, a plugin registry, a descriptor-based per-instance cached
  property, and return-value validation.

## How to use this folder

1. Read `01_concepts.md` top to bottom — each section maps directly to
   the examples below it.
2. Run the example files in order and read the code alongside the output:

   ```
   python 02_easy_examples.py
   python 03_medium_examples.py
   python 04_hard_examples.py
   ```

3. Try modifying an example (e.g. change `retry`'s `max_attempts`, or add
   a new plugin to the registry) to confirm you understand *why* it
   behaves the way it does, not just *that* it works.

All examples have been run and verified to execute without errors.
