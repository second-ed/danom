import functools
from collections.abc import Callable
from typing import (
    Self,
)

from danom._err import Err
from danom._ok import Ok
from danom._result import P, Result


def safe[T, U](func: Callable[[T], U]) -> Callable[[T], Result]:
    """Decorator for functions that wraps the function in a try except returns `Ok` on success else `Err`.

    ```python
    >>> @safe
    ... def add_one(a: int) -> int:
    ...     return a + 1

    >>> add_one(1) == Ok(inner=2)
    ```
    """

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result:
        try:
            return Ok(func(*args, **kwargs))
        except Exception as e:  # noqa: BLE001
            return Err(input_args=(args, kwargs), error=e)

    return wrapper


def safe_method[T, U, E](func: Callable[[T], U]) -> Callable[[T], Result[U, E]]:
    """The same as `safe` except it forwards on the `self` of the class instance to the wrapped function.

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
    """

    @functools.wraps(func)
    def wrapper(self: Self, *args: P.args, **kwargs: P.kwargs) -> Result[U, E]:
        try:
            return Ok(func(self, *args, **kwargs))
        except Exception as e:  # noqa: BLE001
            return Err(input_args=(self, args, kwargs), error=e)

    return wrapper
