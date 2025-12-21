import pytest

from src.danom import Err


@pytest.mark.parametrize(
    ("monad", "expected_result", "expected_context"),
    [
        pytest.param(
            Err(error=TypeError("should raise this"), input_args=()),
            None,
            pytest.raises(TypeError),
        ),
        pytest.param(
            Err(error=ValueError("should raise this"), input_args=()),
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
def test_err_unwrap(monad, expected_result, expected_context):
    with expected_context:
        assert monad.unwrap() == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result"),
    [
        pytest.param(Err(error=TypeError("should raise this"), input_args=()), False),
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
