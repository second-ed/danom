from contextlib import nullcontext

import pytest

from src.danom import Ok


@pytest.mark.parametrize(
    ("monad", "expected_result", "expected_context"),
    [
        pytest.param(Ok(None), None, nullcontext()),
        pytest.param(Ok(0), 0, nullcontext()),
        pytest.param(Ok("ok"), "ok", nullcontext()),
    ],
)
def test_ok_unwrap(monad, expected_result, expected_context):
    with expected_context:
        assert monad.unwrap() == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result"),
    [
        pytest.param(Ok(None), True),
    ],
)
def test_ok_is_ok(monad, expected_result):
    assert monad.is_ok() == expected_result
