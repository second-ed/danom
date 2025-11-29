import functools
from collections.abc import Callable
from typing import (
    Self,
)

from danom._err import Err
from danom._ok import Ok
from danom._result import P, Result, T


def safe(func: Callable[[P], T]) -> Callable[[P], Result]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result:
        try:
            return Ok(func(*args, **kwargs))
        except Exception as e:  # noqa: BLE001
            return Err((args, kwargs), e)

    return wrapper


def safe_method(func: Callable[[P], T]) -> Callable[[P], Result]:
    @functools.wraps(func)
    def wrapper(self: Self, *args: P.args, **kwargs: P.kwargs) -> Result:
        try:
            return Ok(func(self, *args, **kwargs))
        except Exception as e:  # noqa: BLE001
            return Err((self, args, kwargs), e)

    return wrapper
