# danom
# API Reference

## Ok

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