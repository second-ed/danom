import pytest

from src.danom import Err


@pytest.mark.parametrize(
    ("monad", "expected_result", "expected_context"),
    [
        pytest.param(
            Err((), TypeError("should raise this")),
            None,
            pytest.raises(TypeError),
        ),
        pytest.param(
            Err((), ValueError("should raise this")),
            None,
            pytest.raises(ValueError),
        ),
    ],
)
def test_err_unwrap(monad, expected_result, expected_context):
    with expected_context:
        assert monad.unwrap() == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result"),
    [
        pytest.param(Err((), TypeError("should raise this")), False),
    ],
)
def test_err_is_ok(monad, expected_result):
    assert monad.is_ok() == expected_result


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
