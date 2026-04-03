import pytest

from danom import Either, Left, Right
from tests.conftest import add_one


@pytest.mark.parametrize(
    ("monad", "inner"),
    [
        pytest.param(Right, 0),
        pytest.param(Right, "ok"),
        pytest.param(Left, 0),
        pytest.param(Either, 0),
    ],
)
def test_unit(monad, inner):
    assert monad.unit(inner) == Right(inner)


@pytest.mark.parametrize(
    ("left", "right", "expected_result"),
    [
        pytest.param(Right(), Left(), False),
        pytest.param(Right(), Right(), True),
        pytest.param(Left(), Left(), True),
    ],
)
def test_result_equality(left, right, expected_result):
    assert (left == right) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result", "expected_context"),
    [pytest.param(Either, None, pytest.raises(TypeError))],
)
def test_result_unwrap(monad, expected_result, expected_context):
    with expected_context:
        assert monad().unwrap() == expected_result


@pytest.mark.parametrize(
    "monad", [pytest.param(Right, id="for Right monad"), pytest.param(Left, id="for Left monad")]
)
@pytest.mark.parametrize("inner", [pytest.param(0), pytest.param("something"), pytest.param([])])
def test_unwrap(monad, inner):
    assert monad(inner).unwrap() == inner


@pytest.mark.parametrize(
    ("monad", "expected_result"), [pytest.param(Right(), True), pytest.param(Left(), False)]
)
def test_is_ok(monad, expected_result):
    assert monad.is_ok() == expected_result


@pytest.mark.parametrize(
    ("monad", "func", "expected_result"),
    [pytest.param(Right(0), add_one, Right(1)), pytest.param(Left(), add_one, Left())],
)
def test_map(monad, func, expected_result):
    assert monad.map(func) == expected_result


@pytest.mark.parametrize(
    ("monad", "func", "expected_result"),
    [pytest.param(Right(0), add_one, Right(0)), pytest.param(Left(0), add_one, Left(1))],
)
def test_map_err(monad, func, expected_result):
    assert monad.map_err(func) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result"), [pytest.param(Right(), True), pytest.param(Left(), False)]
)
def test_staticmethod_result_is_ok(monad, expected_result):
    assert Either.either_is_ok(monad) == expected_result


@pytest.mark.parametrize(
    "monad", [pytest.param(Right, id="for Right monad"), pytest.param(Left, id="for Left monad")]
)
@pytest.mark.parametrize("inner", [pytest.param(0), pytest.param("something"), pytest.param([])])
def test_staticmethod_result_unwrap(monad, inner):
    assert Either.either_unwrap(monad(inner)) == inner
