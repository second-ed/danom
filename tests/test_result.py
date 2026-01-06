from contextlib import nullcontext

import pytest

from src.danom import Err, Ok, Result
from tests.conftest import add_one


@pytest.mark.parametrize(
    ("monad", "inner"),
    [
        pytest.param(Ok, 0),
        pytest.param(Ok, "ok"),
        pytest.param(Err, 0),
        pytest.param(Result, 0),
    ],
)
def test_unit(monad, inner):
    assert monad.unit(inner) == Ok(inner)


@pytest.mark.parametrize(
    ("left", "right", "expected_result"),
    [
        pytest.param(Ok(), Err(), False),
        pytest.param(Ok(), Ok(), True),
        pytest.param(Err(), Err(), True),
    ],
)
def test_result_equality(left, right, expected_result):
    assert (left == right) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result", "expected_context"),
    [
        pytest.param(Result, None, pytest.raises(TypeError)),
    ],
)
def test_result_unwrap(monad, expected_result, expected_context):
    with expected_context:
        assert monad().unwrap() == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result", "expected_context"),
    [
        pytest.param(Ok(None), None, nullcontext()),
        pytest.param(Ok(0), 0, nullcontext()),
        pytest.param(Ok("ok"), "ok", nullcontext()),
        pytest.param(
            Err(error=TypeError("should raise this")),
            None,
            pytest.raises(TypeError),
        ),
        pytest.param(
            Err(error=ValueError("should raise this")),
            None,
            pytest.raises(ValueError),
        ),
        pytest.param(
            Err("some other err representation"),
            None,
            pytest.raises(ValueError),
        ),
    ],
)
def test_unwrap(monad, expected_result, expected_context):
    with expected_context:
        assert monad.unwrap() == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result"),
    [
        pytest.param(Ok(None), True),
        pytest.param(Err(), False),
    ],
)
def test_is_ok(monad, expected_result):
    assert monad.is_ok() == expected_result


@pytest.mark.parametrize(
    ("monad", "func", "expected_result"),
    [
        pytest.param(Ok(0), add_one, Ok(1)),
        pytest.param(Err(), add_one, Err()),
    ],
)
def test_map(monad, func, expected_result):
    assert monad.map(func) == expected_result


class OnlyIsOk(Result):
    def is_ok(self) -> bool:
        return False


class OnlyUnwrap(Result):
    def unwrap(self) -> None:
        return None


@pytest.mark.parametrize(
    "cls",
    [
        pytest.param(OnlyIsOk),
        pytest.param(OnlyUnwrap),
    ],
)
def test_raises_not_implemented(cls):
    with pytest.raises(TypeError):
        cls()


@pytest.mark.parametrize(
    ("err", "expected_details"),
    [
        pytest.param(TypeError("an invalid type"), []),
        pytest.param("A primative err", []),
    ],
)
def test_err_details(err, expected_details):
    monad = Err(error=err)
    assert monad.details == expected_details
