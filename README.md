# danom

[![PyPI Downloads](https://static.pepy.tech/personalized-badge/danom?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=BLUE&left_text=downloads)](https://pepy.tech/projects/danom) ![coverage](./coverage.svg)

# API Reference

## Stream

An immutable lazy iterator with functional operations.

#### Why bother?
Readability counts, abstracting common operations helps reduce cognitive complexity when reading code.

#### Comparison
Take this imperative pipeline of operations, it iterates once over the data, skipping the value if it fails one of the filter checks:

```python
>>> from danom import Stream
>>> res = []
...
>>> for x in range(1_000_000):
...     item = triple(x)
...
...     if not is_gt_ten(item):
...         continue
...
...     item = min_two(item)
...
...     if not is_even_num(item):
...         continue
...
...     item = square(item)
...
...     if not is_lt_400(item):
...         continue
...
...     res.append(item)
>>> [100, 256]
```
number of tokens: `90`

number of keywords: `11`

keyword breakdown: `{'for': 1, 'in': 1, 'if': 3, 'not': 3, 'continue': 3}`

After a bit of experience with python you might use list comprehensions, however this is arguably _less_ clear and iterates multiple times over the same data
```python
>>> from danom import Stream
>>> mul_three = [triple(x) for x in range(1_000_000)]
>>> gt_ten = [x for x in mul_three if is_gt_ten(x)]
>>> sub_two = [min_two(x) for x in gt_ten]
>>> is_even = [x for x in sub_two if is_even_num(x)]
>>> squared = [square(x) for x in is_even]
>>> lt_400 = [x for x in squared if is_lt_400(x)]
>>> [100, 256]
```
number of tokens: `92`

number of keywords: `15`

keyword breakdown: `{'for': 6, 'in': 6, 'if': 3}`

This still has a lot of tokens that the developer has to read to understand the code. The extra keywords add noise that cloud the actual transformations.

Using a `Stream` results in this:
```python
>>> from danom import Stream
>>> (
...     Stream.from_iterable(range(1_000_000))
...     .map(triple)
...     .filter(is_gt_ten)
...     .map(min_two)
...     .filter(is_even_num)
...     .map(square)
...     .filter(is_lt_400)
...     .collect()
... )
>>> (100, 256)
```
number of tokens: `60`

number of keywords: `0`

keyword breakdown: `{}`

The business logic is arguably much clearer like this.


### `Stream.async_collect`
```python
Stream.async_collect(self) -> 'tuple'
```
Async version of collect. Note that all functions in the stream should be `Awaitable`.

```python
>>> from danom import Stream
>>> Stream.from_iterable(file_paths).map(async_read_files).async_collect()
```

If there are no operations in the `Stream` then this will act as a normal collect.

```python
>>> from danom import Stream
>>> Stream.from_iterable(file_paths).async_collect()
```


### `Stream.collect`
```python
Stream.collect(self) -> 'tuple'
```
Materialise the sequence from the `Stream`.

```python
>>> from danom import Stream
>>> stream = Stream.from_iterable([0, 1, 2, 3]).map(add_one)
>>> stream.collect() == (1, 2, 3, 4)
```


### `Stream.filter`
```python
Stream.filter(self, *fns: 'Callable[[T], bool]') -> 'Self'
```
Filter the stream based on a predicate. Will return a new `Stream` with the modified sequence.

```python
>>> from danom import Stream
>>> Stream.from_iterable([0, 1, 2, 3]).filter(lambda x: x % 2 == 0).collect() == (0, 2)
```

Simple functions can be passed in sequence to compose more complex filters
```python
>>> from danom import Stream
>>> Stream.from_iterable(range(20)).filter(divisible_by_3, divisible_by_5).collect() == (0, 15)
```


### `Stream.fold`
```python
Stream.fold(self, initial: 'T', fn: 'Callable[[T], U]', *, workers: 'int' = 1, use_threads: 'bool' = False) -> 'U'
```
Fold the results into a single value. `fold` triggers an action so will incur a `collect`.

```python
>>> from danom import Stream
>>> Stream.from_iterable([1, 2, 3, 4]).fold(0, lambda a, b: a + b) == 10
>>> Stream.from_iterable([[1], [2], [3], [4]]).fold([0], lambda a, b: a + b) == [0, 1, 2, 3, 4]
>>> Stream.from_iterable([1, 2, 3, 4]).fold(1, lambda a, b: a * b) == 24
```

As `fold` triggers an action, the parameters will be forwarded to the `par_collect` call if the `workers` are greater than 1.
This will only effect the `collect` that is used to create the iterable to reduce, not the `fold` operation itself.
```python
>>> from danom import Stream
>>> Stream.from_iterable([1, 2, 3, 4]).map(some_expensive_fn).fold(0, add, workers=4, use_threads=False)
```


### `Stream.from_iterable`
```python
Stream.from_iterable(it: 'Iterable') -> 'Self'
```
This is the recommended way of creating a `Stream` object.

```python
>>> from danom import Stream
>>> Stream.from_iterable([0, 1, 2, 3]).collect() == (0, 1, 2, 3)
```


### `Stream.map`
```python
Stream.map(self, *fns: 'Callable[[T], U]') -> 'Self'
```
Map a function to the elements in the `Stream`. Will return a new `Stream` with the modified sequence.

```python
>>> from danom import Stream
>>> Stream.from_iterable([0, 1, 2, 3]).map(add_one).collect() == (1, 2, 3, 4)
```

This can also be mixed with `safe` functions:
```python
>>> from danom import Stream
>>> Stream.from_iterable([0, 1, 2, 3]).map(add_one).collect() == (Ok(inner=1), Ok(inner=2), Ok(inner=3), Ok(inner=4))

>>> @safe
... def two_div_value(x: float) -> float:
...     return 2 / x

>>> Stream.from_iterable([0, 1, 2, 4]).map(two_div_value).collect() == (Err(error=ZeroDivisionError('division by zero')), Ok(inner=2.0), Ok(inner=1.0), Ok(inner=0.5))
```

Simple functions can be passed in sequence to compose more complex transformations
```python
>>> from danom import Stream
>>> Stream.from_iterable(range(5)).map(mul_two, add_one).collect() == (1, 3, 5, 7, 9)
```


### `Stream.par_collect`
```python
Stream.par_collect(self, workers: 'int' = 4, *, use_threads: 'bool' = False) -> 'tuple'
```
Materialise the sequence from the `Stream` in parallel.

```python
>>> from danom import Stream
>>> stream = Stream.from_iterable([0, 1, 2, 3]).map(add_one)
>>> stream.par_collect() == (1, 2, 3, 4)
```

Use the `workers` arg to select the number of workers to use. Use `-1` to use all available processors (except 1).
Defaults to `4`.
```python
>>> from danom import Stream
>>> stream = Stream.from_iterable([0, 1, 2, 3]).map(add_one)
>>> stream.par_collect(workers=-1) == (1, 2, 3, 4)
```

For smaller I/O bound tasks use the `use_threads` flag as True.
If False the processing will use `ProcessPoolExecutor` else it will use `ThreadPoolExecutor`.
```python
>>> from danom import Stream
>>> stream = Stream.from_iterable([0, 1, 2, 3]).map(add_one)
>>> stream.par_collect(use_threads=True) == (1, 2, 3, 4)
```

Note that all operations should be pickle-able, for that reason `Stream` does not support lambdas or closures.


### `Stream.partition`
```python
Stream.partition(self, fn: 'Callable[[T], bool]', *, workers: 'int' = 1, use_threads: 'bool' = False) -> 'tuple[Self, Self]'
```
Similar to `filter` except splits the True and False values. Will return a two new `Stream` with the partitioned sequences.

Each partition is independently replayable.
```python
>>> from danom import Stream
>>> part1, part2 = Stream.from_iterable([0, 1, 2, 3]).partition(lambda x: x % 2 == 0)
>>> part1.collect() == (0, 2)
>>> part2.collect() == (1, 3)
```

As `partition` triggers an action, the parameters will be forwarded to the `par_collect` call if the `workers` are greater than 1.
```python
>>> from danom import Stream
>>> Stream.from_iterable(range(10)).map(add_one, add_one).partition(divisible_by_3, workers=4)
>>> part1.map(add_one).par_collect() == (4, 7, 10)
>>> part2.collect() == (2, 4, 5, 7, 8, 10, 11)
```


### `Stream.tap`
```python
Stream.tap(self, *fns: 'Callable[[T], None]') -> 'Self'
```
Tap the values to another process that returns None. Will return a new `Stream` with the modified sequence.

The value passed to the tap function will be deep-copied to avoid any modification to the `Stream` item for downstream consumers.

```python
>>> from danom import Stream
>>> Stream.from_iterable([0, 1, 2, 3]).tap(log_value).collect() == (0, 1, 2, 3)
```

Simple functions can be passed in sequence for multiple `tap` operations
```python
>>> from danom import Stream
>>> Stream.from_iterable([0, 1, 2, 3]).tap(log_value, print_value).collect() == (0, 1, 2, 3)
```

`tap` is useful for logging and similar actions without effecting the individual items, in this example eligible and dormant users are logged using `tap`:

```python
>>> from danom import Stream
>>> active_users, inactive_users = (
...     Stream.from_iterable(users).map(parse_user_objects).partition(inactive_users)
... )
...
>>> active_users.filter(eligible_for_promotion).tap(log_eligible_users).map(
...     construct_promo_email, send_with_confirmation
... ).collect()
...
>>> inactive_users.tap(log_inactive_users).map(
...     create_dormant_user_entry, add_to_dormant_table
... ).collect()
```


## Result

`Result` monad. Consists of `Ok` and `Err` for successful and failed operations respectively.
Each monad is a frozen instance to prevent further mutation.


### `Result.and_then`
```python
Result.and_then(self, func: 'Callable[[T], Result[U]]', **kwargs: 'dict') -> 'Result[U]'
```
Pipe another function that returns a monad. For `Err` will return original error.

```python
>>> from danom import Err, Ok
>>> Ok(1).and_then(add_one) == Ok(2)
>>> Ok(1).and_then(raise_err) == Err(error=TypeError())
>>> Err(error=TypeError()).and_then(add_one) == Err(error=TypeError())
>>> Err(error=TypeError()).and_then(raise_value_err) == Err(error=TypeError())
```


### `Result.is_ok`
```python
Result.is_ok(self) -> 'bool'
```
Returns `True` if the result type is `Ok`.
Returns `False` if the result type is `Err`.

```python
>>> from danom import Err, Ok
>>> Ok().is_ok() == True
>>> Err().is_ok() == False
```


### `Result.map`
```python
Result.map(self, func: 'Callable[[T], U]', **kwargs: 'dict') -> 'Result[U]'
```
Pipe a pure function and wrap the return value with `Ok`.
Given an `Err` will return self.

```python
>>> from danom import Err, Ok
>>> Ok(1).map(add_one) == Ok(2)
>>> Err(error=TypeError()).map(add_one) == Err(error=TypeError())
```


### `Result.match`
```python
Result.match(self, if_ok_func: 'Callable[[T], Result]', if_err_func: 'Callable[[T], Result]') -> 'Result'
```
Map `ok_func` to `Ok` and `err_func` to `Err`

```python
>>> from danom import Err, Ok
>>> Ok(1).match(add_one, mock_get_error_type) == Ok(inner=2)
>>> Ok("ok").match(double, mock_get_error_type) == Ok(inner='okok')
>>> Err(error=TypeError()).match(double, mock_get_error_type) == Ok(inner='TypeError')
```


### `Result.unit`
```python
Result.unit(inner: 'T') -> 'Ok[T]'
```
Unit method. Given an item of type `T` return `Ok(T)`

```python
>>> from danom import Err, Ok, Result
>>> Result.unit(0) == Ok(inner=0)
>>> Ok.unit(0) == Ok(inner=0)
>>> Err.unit(0) == Ok(inner=0)
```


### `Result.unwrap`
```python
Result.unwrap(self) -> 'T'
```
Unwrap the `Ok` monad and get the inner value.
Unwrap the `Err` monad will raise the inner error.
```python
>>> from danom import Err, Ok
>>> Ok().unwrap() == None
>>> Ok(1).unwrap() == 1
>>> Ok("ok").unwrap() == 'ok'
>>> Err(error=TypeError()).unwrap() raise TypeError(...)
```


## safe

### `safe`
```python
safe(func: collections.abc.Callable[[T], U]) -> collections.abc.Callable[[T], danom._result.Result]
```
Decorator for functions that wraps the function in a try except returns `Ok` on success else `Err`.

```python
>>> from danom import safe
>>> @safe
... def add_one(a: int) -> int:
...     return a + 1

>>> add_one(1) == Ok(inner=2)
```


## safe_method

### `safe_method`
```python
safe_method(func: collections.abc.Callable[[T], U]) -> collections.abc.Callable[[T], danom._result.Result]
```
The same as `safe` except it forwards on the `self` of the class instance to the wrapped function.

```python
>>> from danom import safe_method
>>> class Adder:
...     def __init__(self, result: int = 0) -> None:
...         self.result = result
...
...     @safe_method
...     def add_one(self, a: int) -> int:
...         return self.result + 1

>>> Adder.add_one(1) == Ok(inner=1)
```


## compose

### `compose`
```python
compose(*fns: collections.abc.Callable[[T], U]) -> collections.abc.Callable[[T], U]
```
Compose multiple functions into one.

The functions will be called in sequence with the result of one being used as the input for the next.

```python
>>> from danom import compose
>>> add_two = compose(add_one, add_one)
>>> add_two(0) == 2
>>> add_two_is_even = compose(add_one, add_one, is_even)
>>> add_two_is_even(0) == True
```


## all_of

### `all_of`
```python
all_of(*fns: collections.abc.Callable[[T], bool]) -> collections.abc.Callable[[T], bool]
```
True if all of the given functions return True.

```python
>>> from danom import all_of
>>> is_valid_user = all_of(is_subscribed, is_active, has_2fa)
>>> is_valid_user(user) == True
```


## any_of

### `any_of`
```python
any_of(*fns: collections.abc.Callable[[T], bool]) -> collections.abc.Callable[[T], bool]
```
True if any of the given functions return True.

```python
>>> from danom import any_of
>>> is_eligible = any_of(has_coupon, is_vip, is_staff)
>>> is_eligible(user) == True
```


## identity

### `identity`
```python
identity(x: T) -> T
```
Basic identity function.

```python
>>> from danom import identity
>>> identity("abc") == "abc"
>>> identity(1) == 1
>>> identity(ComplexDataType(a=1, b=2, c=3)) == ComplexDataType(a=1, b=2, c=3)
```


## invert

### `invert`
```python
invert(func: collections.abc.Callable[[T], bool]) -> collections.abc.Callable[[T], bool]
```
Invert a boolean function so it returns False where it would've returned True.

```python
>>> from danom import invert
>>> invert(has_len)("abc") == False
>>> invert(has_len)("") == True
```


## new_type

### `new_type`
```python
new_type(name: 'str', base_type: 'type', validators: 'Callable | Sequence[Callable] | None' = None, converters: 'Callable | Sequence[Callable] | None' = None, *, frozen: 'bool' = True)
```
Create a NewType based on another type.

```python
>>> from danom import new_type
>>> def is_positive(value):
...     return value >= 0

>>> ValidBalance = new_type("ValidBalance", float, validators=[is_positive])
>>> ValidBalance("20") == ValidBalance(inner=20.0)
```

Unlike an inherited class, the type will not return `True` for an isinstance check.
```python
>>> isinstance(ValidBalance(20.0), ValidBalance) == True
>>> isinstance(ValidBalance(20.0), float) == False
```

The methods of the given `base_type` will be forwarded to the specialised type.
Alternatively the map method can be used to return a new type instance with the transformation.
```python
>>> from danom import new_type
>>> def has_len(email: str) -> bool:
... return len(email) > 0

>>> Email = new_type("Email", str, validators=[has_len])
>>> Email("some_email@domain.com").upper() == "SOME_EMAIL@DOMAIN.COM"
>>> Email("some_email@domain.com").map(str.upper) == Email(inner='SOME_EMAIL@DOMAIN.COM')
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
│   ├── update_cov.py
│   └── update_readme.py
├── src
│   └── danom
│       ├── __init__.py
│       ├── _new_type.py
│       ├── _result.py
│       ├── _safe.py
│       ├── _stream.py
│       └── _utils.py
├── tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_new_type.py
│   ├── test_result.py
│   ├── test_safe.py
│   ├── test_stream.py
│   └── test_utils.py
├── .pre-commit-config.yaml
├── README.md
├── pyproject.toml
├── ruff.toml
└── uv.lock
::
```