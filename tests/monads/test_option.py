from contextlib import nullcontext

import pytest

from danom import Err, Null, Ok, Option, Some
from tests.conftest import add_one, is_even


@pytest.mark.parametrize(
    ("monad", "opt_b", "expected_result"),
    [
        pytest.param(Some(2), Null(), Null()),
        pytest.param(Null(), Some("foo"), Null()),
        pytest.param(Some(2), Some("foo"), Some("foo")),
        pytest.param(Null(), Null(), Null()),
    ],
)
def test_and_(monad: Option, opt_b, expected_result) -> None:
    assert monad.and_(opt_b) == expected_result


def must_be_less_than_10(x: int) -> Option[int]:
    return Some(x) if x < 10 else Null()


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [
        pytest.param(Some(2), must_be_less_than_10, Some(2)),
        pytest.param(Some(20), must_be_less_than_10, Null()),
        pytest.param(Null(), must_be_less_than_10, Null()),
    ],
)
def test_and_then(monad: Option, fn, expected_result) -> None:
    assert monad.and_then(fn) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result"), [pytest.param(Some(2), [2]), pytest.param(Null(), [])]
)
def test_as_list(monad: Option, expected_result) -> None:
    assert monad.as_list() == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result"), [pytest.param(Some(2), (2,)), pytest.param(Null(), ())]
)
def test_as_tuple(monad: Option, expected_result) -> None:
    assert monad.as_tuple() == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result"), [pytest.param(Some(2), Some(2)), pytest.param(Null(), Null())]
)
def test_cloned(monad: Option, expected_result) -> None:
    assert monad.cloned() == expected_result
    assert id(monad) != id(expected_result)


@pytest.mark.parametrize(
    ("monad", "msg", "expected_result", "expected_context"),
    [
        pytest.param(Some(2), "must be positive", 2, nullcontext()),
        pytest.param(Null(), "must be positive", None, pytest.raises(ValueError)),
    ],
)
def test_expect(monad: Option, msg, expected_result, expected_context) -> None:
    with expected_context:
        assert monad.expect(msg) == expected_result


@pytest.mark.parametrize(
    ("monad", "predicate", "expected_result"),
    [
        pytest.param(Some(3), is_even, Null()),
        pytest.param(Some(4), is_even, Some(4)),
        pytest.param(Null(), is_even, Null()),
    ],
)
def test_filter_(monad: Option, predicate, expected_result) -> None:
    assert monad.filter_(predicate) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result"),
    [
        pytest.param(Some(Some(Some(2))), Some(Some(2))),
        pytest.param(Some(Some(2)), Some(2)),
        pytest.param(Some(2), Some(2)),
        pytest.param(Null(), Null()),
    ],
)
def test_flatten(monad: Option, expected_result) -> None:
    assert monad.flatten() == expected_result


def append_to_list(x) -> None:
    x.append(2)


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [
        pytest.param(Some([1]), append_to_list, Some([1])),
        pytest.param(Null(), append_to_list, Null()),
    ],
)
def test_inspect(monad: Option, fn, expected_result) -> None:
    assert monad.inspect(fn) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result"), [pytest.param(Some(2), False), pytest.param(Null(), True)]
)
def test_is_none(monad: Option, expected_result) -> None:
    assert monad.is_none() == expected_result


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [
        pytest.param(Some(1), is_even, False),
        pytest.param(Some(2), is_even, True),
        pytest.param(Null(), is_even, True),
    ],
)
def test_is_none_or(monad: Option, fn, expected_result) -> None:
    assert monad.is_none_or(fn) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result"), [pytest.param(Some(2), True), pytest.param(Null(), False)]
)
def test_is_some(monad: Option, expected_result) -> None:
    assert monad.is_some() == expected_result


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [
        pytest.param(Some(1), is_even, False),
        pytest.param(Some(2), is_even, True),
        pytest.param(Null(), is_even, False),
    ],
)
def test_is_some_and(monad: Option, fn, expected_result) -> None:
    assert monad.is_some_and(fn) == expected_result


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [pytest.param(Some(1), add_one, Some(2)), pytest.param(Null(), add_one, Null())],
)
def test_map(monad: Option, fn, expected_result) -> None:
    assert monad.map(fn) == expected_result


@pytest.mark.parametrize(
    ("monad", "default", "fn", "expected_result"),
    [pytest.param(Some("foo"), 42, len, 3), pytest.param(Null(), 42, len, 42)],
)
def test_map_or(monad: Option, default, fn, expected_result) -> None:
    assert monad.map_or(default, fn) == expected_result


@pytest.mark.parametrize(
    ("monad", "default", "fn", "expected_result"),
    [pytest.param(Some("foo"), lambda: 42, len, 3), pytest.param(Null(), lambda: 42, len, 42)],
)
def test_map_or_else(monad: Option, default, fn, expected_result) -> None:
    assert monad.map_or_else(default, fn) == expected_result


@pytest.mark.parametrize(
    ("monad", "err", "expected_result"),
    [pytest.param(Some("foo"), 0, Ok("foo")), pytest.param(Null(), 0, Err(0))],
)
def test_ok_or(monad: Option, err, expected_result) -> None:
    assert monad.ok_or(err) == expected_result


@pytest.mark.parametrize(
    ("monad", "err", "expected_result"),
    [pytest.param(Some("foo"), lambda: 0, Ok("foo")), pytest.param(Null(), lambda: 0, Err(0))],
)
def test_ok_or_else(monad: Option, err, expected_result) -> None:
    assert monad.ok_or_else(err) == expected_result


@pytest.mark.parametrize(
    ("monad", "opt_b", "expected_result"),
    [
        pytest.param(Some(2), Null(), Some(2)),
        pytest.param(Null(), Some(100), Some(100)),
        pytest.param(Some(2), Some(100), Some(2)),
        pytest.param(Null(), Null(), Null()),
    ],
)
def test_or_(monad: Option, opt_b, expected_result) -> None:
    assert monad.or_(opt_b) == expected_result


@pytest.mark.parametrize(
    ("monad", "opt_b", "expected_result"),
    [
        pytest.param(Some("barbarians"), lambda: Some("vikings"), Some("barbarians")),
        pytest.param(Null(), lambda: Some("vikings"), Some("vikings")),
        pytest.param(Null(), Null, Null()),
    ],
)
def test_or_else(monad: Option, opt_b, expected_result) -> None:
    assert monad.or_else(opt_b) == expected_result


@pytest.mark.parametrize(
    ("monad", "value", "expected_result"),
    [pytest.param(Some(2), 5, Some(5)), pytest.param(Null(), 3, Null())],
)
def test_replace(monad: Option, value, expected_result) -> None:
    assert monad.replace(value) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result", "expected_context"),
    [
        pytest.param(Some(Ok(2)), Ok(Some(2)), nullcontext()),
        pytest.param(Some(Err(2)), Err(Some(2)), nullcontext()),
        pytest.param(Null(), Ok(Null()), nullcontext()),
        pytest.param(Some(2), None, pytest.raises(TypeError)),
    ],
)
def test_transpose(monad: Option, expected_result, expected_context) -> None:
    with expected_context:
        assert monad.transpose() == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result", "expected_context"),
    [pytest.param(Some(2), 2, nullcontext()), pytest.param(Null(), None, pytest.raises(TypeError))],
)
def test_unwrap(monad: Option, expected_result, expected_context) -> None:
    with expected_context:
        assert monad.unwrap() == expected_result


@pytest.mark.parametrize(
    ("monad", "default", "expected_result"),
    [pytest.param(Some("car"), "bike", "car"), pytest.param(Null(), "bike", "bike")],
)
def test_unwrap_or(monad: Option, default, expected_result) -> None:
    assert monad.unwrap_or(default) == expected_result


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [pytest.param(Some(4), lambda: 20, 4), pytest.param(Null(), lambda: 20, 20)],
)
def test_unwrap_or_else(monad: Option, fn, expected_result) -> None:
    assert monad.unwrap_or_else(fn) == expected_result


@pytest.mark.parametrize(
    ("monad", "other", "expected_result"),
    [
        pytest.param(Some(1), Some("hi"), Some((1, "hi"))),
        pytest.param(Some(1), Null(), Null()),
        pytest.param(Null(), Some(1), Null()),
    ],
)
def test_zip(monad: Option, other, expected_result) -> None:
    assert monad.zip(other) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result"),
    [
        pytest.param(Some((2, 2)), (Some(2), Some(2))),
        pytest.param(Some(4), (Null(), Null())),
        pytest.param(Null(), (Null(), Null())),
    ],
)
def test_unzip(monad: Option, expected_result) -> None:
    assert monad.unzip() == expected_result
