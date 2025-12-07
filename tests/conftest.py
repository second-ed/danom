from typing import Any, Self

from src.danom import safe, safe_method
from src.danom._result import Result


def has_len(value: str) -> bool:
    return len(value) > 0


def add_one(x: int) -> int:
    return x + 1


def divisible_by_3(x: int) -> bool:
    return x % 3 == 0


def divisible_by_5(x: int) -> bool:
    return x % 5 == 0


@safe
def safe_add(a: int, b: int) -> Result[int, Exception]:
    return a + b


@safe
def safe_raise_type_error(_a: Any) -> Result[None, Exception]:  # noqa: ANN401
    raise TypeError


@safe
def safe_get_error_type(exception: Exception) -> str:
    return exception.__class__.__name__


class Adder:
    def __init__(self) -> None:
        self.result = 0

    @safe_method
    def add(self, a: int, b: int) -> Self:
        self.result += a + b
        return self

    @safe_method
    def cls_raises(self, *_args: tuple, **_kwargs: dict) -> None:
        raise ValueError
