import functools
import traceback
from collections.abc import Callable
from typing import Concatenate, ParamSpec, TypeVar

from danom._result import Err, Ok, Result

T = TypeVar("T")
P = ParamSpec("P")
U = TypeVar("U")
E = TypeVar("E")


def safe[**P, U](func: Callable[P, U]) -> Callable[P, Result[U, Exception]]:
    """Decorator for functions that wraps the function in a try except returns `Ok` on success else `Err`.

    .. code-block:: python

        from danom import safe

        @safe
        def add_one(a: int) -> int:
            return a + 1

        add_one(1) == Ok(inner=2)
    """

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[U, Exception]:
        try:
            return Ok(func(*args, **kwargs))
        except Exception as e:  # noqa: BLE001
            return Err(
                error=e, input_args=(args, kwargs), traceback=traceback.format_exc()
            )  # ty: ignore[invalid-return-type]

    return wrapper


def safe_method[T, **P, U](
    func: Callable[Concatenate[T, P], U],
) -> Callable[Concatenate[T, P], Result[U, Exception]]:
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
    def wrapper(self: T, *args: P.args, **kwargs: P.kwargs) -> Result[U, Exception]:
        try:
            return Ok(func(self, *args, **kwargs))
        except Exception as e:  # noqa: BLE001
            return Err(
                error=e, input_args=(self, args, kwargs), traceback=traceback.format_exc()
            )  # ty: ignore[invalid-return-type]

    return wrapper
