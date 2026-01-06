from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Self

from src.danom import safe, safe_method
from src.danom._result import Err, Ok, Result

REPO_ROOT = Path(__file__).parents[1]


def add[T: (str, float, int)](a: T, b: T) -> T:
    return a + b  # ty: ignore[unsupported-operator]


def has_len(value: str) -> bool:
    return len(value) > 0


def add_one(x: float) -> float:
    return x + 1


def double[T: (str, float, int)](x: T) -> T:
    return x * 2  # ty: ignore[unsupported-operator]


def is_even(x: float) -> bool:
    return x % 2 == 0


def divisible_by_3(x: float) -> bool:
    return x % 3 == 0


def divisible_by_5(x: float) -> bool:
    return x % 5 == 0


def lt_10(x: float) -> bool:
    return x < 10  # noqa: PLR2004


async def async_is_file(path: Path) -> bool:
    return path.is_file()


async def async_read_text(path: str) -> str:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, Path(path).read_text)


@safe
def safe_add(a: int, b: int) -> Result[int, Exception]:
    return a + b


def safe_add_one(x: float | str) -> Result[float | str, TypeError]:
    if isinstance(x, (int, float)):
        return Ok(x + 1)
    if isinstance(x, str):
        return Ok(x + "1")
    return Err(TypeError(f"unsupported type: {type(x)}"))


@safe
def safe_double[T: (str, float, int)](x: T) -> T:
    return x * 2  # ty: ignore[unsupported-operator]


@safe
def safe_raise_type_error(_a: Any) -> None:  # noqa: ANN401
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


class ValueLogger:
    def __init__(self, values: list | None = None) -> None:
        self.values = values if values is not None else []

    def __call__[T](self, value: T) -> None:
        self.values.append(value)


class AsyncValueLogger:
    def __init__(self) -> None:
        self.values = set()

    async def __call__[T](self, value: T) -> None:
        self.values.add(value)
