from functools import partial

import pytest

from danom._result import Err
from tests.conftest import (
    REPO_ROOT,
    Adder,
    div_zero,
    safe_add,
    safe_get_error_type,
    safe_raise_type_error,
)


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


def test_traceback():
    err = div_zero(1)

    expected_lines = [
        "Traceback (most recent call last):",
        '  File "./src/danom/_safe.py", line 31, in wrapper',
        "    return Ok(func(*args, **kwargs))",
        '  File "./tests/conftest.py", line 85, in div_zero',
        "    return x / 0",
        "ZeroDivisionError: division by zero",
    ]

    if not isinstance(err, Err):
        raise TypeError("This should be an Err by now")

    tb_lines = err.traceback.replace(str(REPO_ROOT), ".").splitlines()

    missing_lines = [line for line in expected_lines if line not in tb_lines]

    assert missing_lines == []
