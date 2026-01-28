from functools import partial

import pytest

from tests.conftest import Adder, safe_add, safe_get_error_type, safe_raise_type_error


def test_valid_safe_pipeline():
    pipeline = (
        safe_add(1, 2)
        .and_then(safe_add, b=1)
        .and_then(safe_add, b=1)
        .and_then(partial(safe_add, b=1))
        .or_else(safe_get_error_type)
    )
    assert pipeline.is_ok()
    assert pipeline.unwrap() == 6


def test_invalid_safe_pipeline():
    pipeline = safe_add(1, 2).and_then(safe_raise_type_error).and_then(safe_add, b=1)
    assert not pipeline.is_ok()

    with pytest.raises(TypeError):
        assert pipeline.unwrap()


def test_invalid_safe_pipeline_with_match():
    pipeline = (
        safe_add(1, 2)
        .and_then(safe_raise_type_error)
        .and_then(safe_add, b=1)
        .and_then(partial(safe_add, b=1))
        .or_else(safe_get_error_type)
    )
    assert pipeline.is_ok()
    assert pipeline.unwrap() == "TypeError"


def test_valid_safe_method_pipeline():
    cls = Adder()
    res = cls.add(2, 2).and_then(lambda cls: cls.add(2, 2)).and_then(lambda cls: cls.add(2, 2))
    assert res.is_ok()
    assert res.unwrap().result == 12


def test_invalid_safe_method_pipeline():
    cls = Adder()
    res = cls.add(2, 2).and_then(lambda cls: cls.cls_raises()).and_then(lambda cls: cls.add(2, 2))
    assert not res.is_ok()
    with pytest.raises(ValueError):
        res.unwrap()
