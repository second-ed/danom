import pytest

from src.danom._result import Result, T


@pytest.mark.parametrize(
    ("monad", "expected_result", "expected_context"),
    [
        pytest.param(Result, None, pytest.raises(TypeError)),
    ],
)
def test_result_unwrap(monad, expected_result, expected_context):
    with expected_context:
        assert monad().unwrap() == expected_result


class OnlyIsOk(Result):
    def is_ok(self) -> bool:
        return False


class OnlyUnwrap(Result):
    def unwrap(self) -> T:
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
