# danom

[![PyPI Downloads](https://static.pepy.tech/personalized-badge/danom?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=BLUE&left_text=downloads)](https://pepy.tech/projects/danom)

# API Reference

## Ok

Frozen instance of an Ok monad used to wrap successful operations.

### `Ok.and_then`
```python
Ok.and_then(self, func: collections.abc.Callable[[~T], danom._result.Result], **kwargs: dict) -> danom._result.Result
```
Pipe another function that returns a monad.

```python
>>> Ok(1).and_then(add_one) == Ok(2)
>>> Ok(1).and_then(raise_err) == Err(error=TypeError())
```


### `Ok.is_ok`
```python
Ok.is_ok(self) -> Literal[True]
```
Returns True if the result type is Ok.

```python
>>> Ok().is_ok() == True
```


### `Ok.match`
```python
Ok.match(self, if_ok_func: collections.abc.Callable[[~T], danom._result.Result], _if_err_func: collections.abc.Callable[[~T], danom._result.Result]) -> danom._result.Result
```
Map Ok func to Ok and Err func to Err

```python
>>> Ok(1).match(add_one, mock_get_error_type) == Ok(inner=2)
>>> Ok("ok").match(double, mock_get_error_type) == Ok(inner='okok')
>>> Err(error=TypeError()).match(double, mock_get_error_type) == Ok(inner='TypeError')
```


### `Ok.unwrap`
```python
Ok.unwrap(self) -> ~T
```
Unwrap the Ok monad and get the inner value.

```python
>>> Ok().unwrap() == None
>>> Ok(1).unwrap() == 1
>>> Ok("ok").unwrap() == 'ok'
```


## Err

Frozen instance of an Err monad used to wrap failed operations.

### `Err.and_then`
```python
Err.and_then(self, _: 'Callable[[T], Result]', **_kwargs: 'dict') -> 'Self'
```
Pipe another function that returns a monad. For Err will return original error.

```python
>>> Err(error=TypeError()).and_then(add_one) == Err(error=TypeError())
>>> Err(error=TypeError()).and_then(raise_value_err) == Err(error=TypeError())
```


### `Err.is_ok`
```python
Err.is_ok(self) -> 'Literal[False]'
```
Returns False if the result type is Err.

```python
Err().is_ok() == False
```


### `Err.match`
```python
Err.match(self, _if_ok_func: 'Callable[[T], Result]', if_err_func: 'Callable[[T], Result]') -> 'Result'
```
Map Ok func to Ok and Err func to Err

```python
>>> Ok(1).match(add_one, mock_get_error_type) == Ok(inner=2)
>>> Ok("ok").match(double, mock_get_error_type) == Ok(inner='okok')
>>> Err(error=TypeError()).match(double, mock_get_error_type) == Ok(inner='TypeError')
```


### `Err.unwrap`
```python
Err.unwrap(self) -> 'None'
```
Unwrap the Err monad will raise the inner error.

```python
>>> Err(error=TypeError()).unwrap() raise TypeError(...)
```


## Stream

A lazy iterator with functional operations.

### `Stream.collect`
```python
Stream.collect(self) -> 'tuple'
```
Materialise the sequence from the `Stream`.

```python
>>> stream = Stream.from_iterable([0, 1, 2, 3]).map(add_one)
>>> stream.collect() == (1, 2, 3, 4)
```


### `Stream.filter`
```python
Stream.filter(self, *fns: 'Callable[[T], bool]') -> 'Self'
```
Filter the stream based on a predicate. Will return a new `Stream` with the modified sequence.

```python
>>> Stream.from_iterable([0, 1, 2, 3]).filter(lambda x: x % 2 == 0).collect() == (0, 2)
```

Simple functions can be passed in sequence to compose more complex filters
```python
>>> Stream.from_iterable(range(20)).filter(divisible_by_3, divisible_by_5).collect() == (0, 15)
```


### `Stream.from_iterable`
```python
Stream.from_iterable(it: 'Iterable') -> 'Self'
```
This is the recommended way of creating a `Stream` object.

```python
>>> Stream.from_iterable([0, 1, 2, 3]).collect() == (0, 1, 2, 3)
```


### `Stream.map`
```python
Stream.map(self, *fns: 'Callable[[T], U]') -> 'Self'
```
Map a function to the elements in the `Stream`. Will return a new `Stream` with the modified sequence.

```python
>>> Stream.from_iterable([0, 1, 2, 3]).map(add_one).collect() == (1, 2, 3, 4)
```

This can also be mixed with `safe` functions:
```python
>>> Stream.from_iterable([0, 1, 2, 3]).map(add_one).collect() == (Ok(inner=1), Ok(inner=2), Ok(inner=3), Ok(inner=4))

>>> @safe
... def two_div_value(x: float) -> float:
...     return 2 / x

>>> Stream.from_iterable([0, 1, 2, 4]).map(two_div_value).collect() == (Err(error=ZeroDivisionError('division by zero')), Ok(inner=2.0), Ok(inner=1.0), Ok(inner=0.5))
```

Simple functions can be passed in sequence to compose more complex transformations
```python
>>> Stream.from_iterable(range(5)).map(mul_two, add_one).collect() == (1, 3, 5, 7, 9)
```


### `Stream.partition`
```python
Stream.partition(self, fn: 'Callable[[T], bool]') -> 'tuple[Self, Self]'
```
Similar to `filter` except splits the True and False values. Will return a two new `Stream` with the partitioned sequences.

Each partition is independently replayable.
```python
>>> part1, part2 = Stream.from_iterable([0, 1, 2, 3]).partition(lambda x: x % 2 == 0)
>>> part1.collect() == (0, 2)
>>> part2.collect() == (1, 3)
```


### `Stream.to_par_stream`
```python
Stream.to_par_stream(self) -> 'ParStream'
```
Convert `Stream` to `ParStream`. This will incur a `collect`.

```python
>>> Stream.from_iterable([0, 1, 2, 3]).to_par_stream().map(some_expensive_cpu_task).collect() == (1, 2, 3, 4)

```


## ParStream

A parallel iterator with functional operations.

### `ParStream.collect`
```python
ParStream.collect(self, workers: 'int' = 4, *, use_threads: 'bool' = False) -> 'tuple'
```
Materialise the sequence from the `ParStream`.

```python
>>> stream = ParStream.from_iterable([0, 1, 2, 3]).map(add_one)
>>> stream.collect() == (1, 2, 3, 4)
```

Use the `workers` arg to select the number of workers to use. Use `-1` to use all available processors (except 1).
Defaults to `4`.
```python
>>> stream = ParStream.from_iterable([0, 1, 2, 3]).map(add_one)
>>> stream.collect(workers=-1) == (1, 2, 3, 4)
```

For smaller I/O bound tasks use the `use_threads` flag as True
```python
>>> stream = ParStream.from_iterable([0, 1, 2, 3]).map(add_one)
>>> stream.collect(use_threads=True) == (1, 2, 3, 4)
```


### `ParStream.filter`
```python
ParStream.filter(self, *fns: 'Callable[[T], bool]') -> 'Self'
```
Filter the par stream based on a predicate. Will return a new `ParStream` with the modified sequence.

```python
>>> ParStream.from_iterable([0, 1, 2, 3]).filter(lambda x: x % 2 == 0).collect() == (0, 2)
```

Simple functions can be passed in sequence to compose more complex filters
```python
>>> ParStream.from_iterable(range(20)).filter(divisible_by_3, divisible_by_5).collect() == (0, 15)
```


### `ParStream.from_iterable`
```python
ParStream.from_iterable(it: 'Iterable') -> 'Self'
```
This is the recommended way of creating a `ParStream` object.

```python
>>> ParStream.from_iterable([0, 1, 2, 3]).collect() == (0, 1, 2, 3)
```


### `ParStream.map`
```python
ParStream.map(self, *fns: 'Callable[[T], U]') -> 'Self'
```
Map functions to the elements in the `ParStream` in parallel. Will return a new `ParStream` with the modified sequence.

```python
>>> ParStream.from_iterable([0, 1, 2, 3]).map(add_one, add_one).collect() == (2, 3, 4, 5)
```


### `ParStream.partition`
```python
ParStream.partition(self, _fn: 'Callable[[T], bool]') -> 'tuple[Self, Self]'
```
Partition isn't implemented for `ParStream`. Convert to `Stream` with the `to_stream()` method and then call partition.

### `ParStream.to_stream`
```python
ParStream.to_stream(self) -> 'Stream'
```
Convert `ParStream` to `Stream`. This will incur a `collect`.

```python
>>> ParStream.from_iterable([0, 1, 2, 3]).to_stream().map(some_memory_hungry_task).collect() == (1, 2, 3, 4)
```


## safe

### `safe`
```python
safe(func: collections.abc.Callable[~P, ~T]) -> collections.abc.Callable[~P, danom._result.Result]
```
Decorator for functions that wraps the function in a try except returns `Ok` on success else `Err`.

```python
>>> @safe
... def add_one(a: int) -> int:
...     return a + 1

>>> add_one(1) == Ok(inner=2)
```


## safe_method

### `safe_method`
```python
safe_method(func: collections.abc.Callable[~P, ~T]) -> collections.abc.Callable[~P, danom._result.Result]
```
The same as `safe` except it forwards on the `self` of the class instance to the wrapped function.

```python
>>> class Adder:
...     def __init__(self, result: int = 0) -> None:
...         self.result = result
...
...     @safe_method
...     def add_one(self, a: int) -> int:
...         return self.result + 1

>>> Adder.add_one(1) == Ok(inner=1)
```

::

# Repo map
```
├── .github
│   └── workflows
│       ├── ci_tests.yaml
│       └── publish.yaml
├── dev_tools
│   ├── __init__.py
│   └── update_readme.py
├── src
│   └── danom
│       ├── __init__.py
│       ├── _err.py
│       ├── _ok.py
│       ├── _result.py
│       ├── _safe.py
│       └── _stream.py
├── tests
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_err.py
│   ├── test_ok.py
│   ├── test_result.py
│   ├── test_safe.py
│   └── test_stream.py
├── .pre-commit-config.yaml
├── README.md
├── pyproject.toml
├── ruff.toml
└── uv.lock
::
```