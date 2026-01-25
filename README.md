# danom

[![PyPI Downloads](https://static.pepy.tech/personalized-badge/danom?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=BLUE&left_text=downloads)](https://pepy.tech/projects/danom) ![coverage](./coverage.svg)

# API Reference

[danom API docs](https://second-ed.github.io/danom/)


## Stream

An immutable lazy iterator with functional operations.

#### Why bother?
Readability counts, abstracting common operations helps reduce cognitive complexity when reading code.

#### Comparison
Take this imperative pipeline of operations, it iterates once over the data, skipping the value if it fails one of the filter checks:

```python
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


## Result

`Result` monad. Consists of `Ok` and `Err` for successful and failed operations respectively.
Each monad is a frozen instance to prevent further mutation. `Err` provides the `details` attribute which returns the full traceback as a list of dictionaries.


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
├── docs
│   └── source
│       └── conf.py
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
│   ├── test_monad_laws.py
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

(generated with repo-mapper-rs)
::
```