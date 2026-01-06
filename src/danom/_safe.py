import functools
from collections.abc import Callable
from typing import ParamSpec

from danom._result import Err, Ok, Result

P = ParamSpec("P")


def safe[U, E](func: Callable[..., U]) -> Callable[..., Result[U, E]]:
    """Decorator for functions that wraps the function in a try except returns `Ok` on success else `Err`.

    .. code-block:: python

        from danom import safe

        @safe
        def add_one(a: int) -> int:
            return a + 1

        add_one(1) == Ok(inner=2)
    """

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[U, E]:
        try:
            return Ok(func(*args, **kwargs))
        except Exception as e:  # noqa: BLE001
            return Err(input_args=(args, kwargs), error=e)

    return wrapper


def safe_method[U, E](func: Callable[..., U]) -> Callable[..., Result[U, E]]:
    """The same as `safe` except it forwards on the `self` of the class instance to the wrapped function.

    .. code-block:: python

        from danom import safe_method

        class Adder:
            def __init__(self, result: int = 0) -> None:
                self.result = result

            @safe_method
            def add_one(self, a: int) -> int:
                return self.result + 1

        Adder.add_one(1) == Ok(inner=1)
    """

    @functools.wraps(func)
    def wrapper(self, *args: P.args, **kwargs: P.kwargs) -> Result[U, E]:  # noqa: ANN001
        try:
            return Ok(func(self, *args, **kwargs))
        except Exception as e:  # noqa: BLE001
            return Err(input_args=(self, args, kwargs), error=e)

    return wrapper
