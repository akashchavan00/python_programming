# Generators & Iterators

Topic folder for learning Python generators and iterators, from the
underlying protocol to production-style lazy pipelines and coroutine
patterns.

## Contents

- **01_concepts.md** — full written explanation: the iterator protocol
  (`__iter__`/`__next__`), writing a manual iterator class, generator
  functions and `yield`, why generators matter (laziness/memory),
  generator expressions, two-way communication with `.send()`,
  `yield from`, generators that `return` a value, `.close()` and cleanup,
  the `itertools` toolbox, and how generators/iterators/iterables relate.
- **02_easy_examples.py** — the manual iterator protocol, a custom
  iterator class vs. the equivalent generator function, a simple
  filtering generator, and generator expressions vs. list comprehensions.
- **03_medium_examples.py** — memory comparison (list vs. generator),
  `yield from` for flattening nested data, a chained lazy data pipeline,
  capturing a generator's return value, and `itertools` building blocks
  (`count`, `islice`, `chain`, `groupby`, `takewhile`/`dropwhile`).
- **04_hard_examples.py** — two-way coroutine-style generators with
  `.send()`, a generator-based state machine, an infinite lazy prime
  stream via `__iter__`, `itertools.tee` for independent derived streams,
  guaranteed cleanup with `.close()`, and a lazy sliding-window generator.

## How to use this folder

1. Read `01_concepts.md` top to bottom — each section maps directly to
   the examples below it.
2. Run the example files in order and read the code alongside the output:

   ```
   python 02_easy_examples.py
   python 03_medium_examples.py
   python 04_hard_examples.py
   ```

3. Try extending an example (e.g. add a new stage to the pipeline in
   `03_medium_examples.py`, or add a new state to the traffic light in
   `04_hard_examples.py`) to confirm you understand *why* it behaves the
   way it does, not just *that* it works.

All examples have been run and verified to execute without errors.
