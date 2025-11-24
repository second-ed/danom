from typing import Any, Self

import pytest

from src.danom import safe, safe_method
from src.danom.result import Result


@safe
def mock_func(a: int, b: int) -> Result[int, Exception]:
    return a + b


@safe
def mock_func_raises(_a: Any) -> Result[None, Exception]:
    raise TypeError


def test_valid_safe_pipeline():
    pipeline = mock_func(1, 2).and_then(mock_func, b=1).and_then(mock_func, b=1)
    assert pipeline.is_ok()
    assert pipeline.unwrap() == 5


def test_invalid_safe_pipeline():
    pipeline = mock_func(1, 2).and_then(mock_func_raises).and_then(mock_func, b=1)
    assert not pipeline.is_ok()

    with pytest.raises(TypeError):
        assert pipeline.unwrap()


class Adder:
    def __init__(self):
        self.result = 0

    @safe_method
    def add(self, a: int, b: int) -> Self:
        self.result += a + b
        return self

    @safe_method
    def cls_raises(self, *args, **kwargs) -> None:
        raise ValueError


def test_valid_safe_method_pipeline():
    cls = Adder()
    res = cls.add(2, 2).add(2, 2).add(2, 2)
    assert res.is_ok()
    assert res.unwrap().result == 12


def test_invalid_safe_method_pipeline():
    cls = Adder()
    res = cls.add(2, 2).cls_raises().add(2, 2)
    assert not res.is_ok()
    with pytest.raises(ValueError):
        res.unwrap()
