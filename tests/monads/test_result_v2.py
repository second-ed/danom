from contextlib import nullcontext
from typing import cast

import pytest

from danom._monads._option import Null, Some
from danom._monads._result_v2 import Err, Ok, Result
from dev_tools.create_examples.collection.example import example
from tests.conftest import add_one, get_42, get_ok_vikings, is_even


@pytest.mark.parametrize(
    ("monad", "res", "expected_result"),
    [
        pytest.param(Ok(2), Err("late error"), Err("late error")),
        pytest.param(Err("early error"), Ok("foo"), Err("early error")),
        pytest.param(Err("not a 2"), Err("late error"), Err("not a 2")),
        pytest.param(Ok(2), Ok("different result type"), Ok("different result type")),
    ],
)
def test_and_(monad: Result, res, expected_result) -> None:
    assert example(monad.and_, res) == expected_result


def must_be_less_than_10(x: int) -> Result[int, str]:
    return cast(Result[int, str], Ok(x) if x < 10 else Err("too high"))


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [
        pytest.param(Ok(2), must_be_less_than_10, Ok(2)),
        pytest.param(Ok(20), must_be_less_than_10, Err("too high")),
        pytest.param(Err("not a number"), must_be_less_than_10, Err("not a number")),
    ],
)
def test_and_then(monad: Result, fn, expected_result) -> None:
    assert example(monad.and_then, fn) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result"), [pytest.param(Ok(2), Ok(2)), pytest.param(Err(2), Err(2))]
)
def test_cloned(monad: Result, expected_result) -> None:
    assert example(monad.cloned) == expected_result
    assert id(monad) != id(expected_result)


@pytest.mark.parametrize(
    ("monad", "expected_result"),
    [pytest.param(Ok(2), Null()), pytest.param(Err("Nothing here"), Some("Nothing here"))],
)
def test_err(monad: Result, expected_result) -> None:
    assert example(monad.err) == expected_result


@pytest.mark.parametrize(
    ("monad", "msg", "expected_result", "expected_context"),
    [
        pytest.param(Ok(2), "must be positive", 2, nullcontext()),
        pytest.param(Err(), "must be positive", None, pytest.raises(ValueError)),
    ],
)
def test_expect(monad: Result, msg, expected_result, expected_context) -> None:
    with expected_context:
        assert example(monad.expect, msg) == expected_result


@pytest.mark.parametrize(
    ("monad", "msg", "expected_result", "expected_context"),
    [
        pytest.param(Err(2), "must be err", 2, nullcontext()),
        pytest.param(Ok(), "must be err", None, pytest.raises(ValueError)),
    ],
)
def test_expect_err(monad: Result, msg, expected_result, expected_context) -> None:
    with expected_context:
        assert example(monad.expect_err, msg) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result"),
    [
        pytest.param(Ok(Ok(Ok(2))), Ok(Ok(2))),
        pytest.param(Ok(Ok(2)), Ok(2)),
        pytest.param(Ok(2), Ok(2)),
        pytest.param(Err(), Err()),
    ],
)
def test_flatten(monad: Result, expected_result) -> None:
    assert example(monad.flatten) == expected_result


def append_to_list(x) -> None:
    x.append(2)


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [
        pytest.param(Ok([1]), append_to_list, Ok([1])),
        pytest.param(Err("un-appendable"), append_to_list, Err("un-appendable")),
    ],
)
def test_inspect(monad: Result, fn, expected_result) -> None:
    assert example(monad.inspect, fn) == expected_result


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [
        pytest.param(Err([1]), append_to_list, Err([1])),
        pytest.param(Ok("un-appendable"), append_to_list, Ok("un-appendable")),
    ],
)
def test_inspect_err(monad: Result, fn, expected_result) -> None:
    assert example(monad.inspect_err, fn) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result"), [pytest.param(Ok(2), False), pytest.param(Err(2), True)]
)
def test_is_err(monad: Result, expected_result) -> None:
    assert example(monad.is_err) == expected_result


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [
        pytest.param(Err(1), is_even, False),
        pytest.param(Err(2), is_even, True),
        pytest.param(Ok(2), is_even, False),
    ],
)
def test_is_err_and(monad: Result, fn, expected_result) -> None:
    assert example(monad.is_err_and, fn) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result"), [pytest.param(Ok(2), True), pytest.param(Err(2), False)]
)
def test_is_ok(monad: Result, expected_result) -> None:
    assert example(monad.is_ok) == expected_result


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [
        pytest.param(Ok(1), is_even, False),
        pytest.param(Ok(2), is_even, True),
        pytest.param(Err(2), is_even, False),
    ],
)
def test_is_ok_and(monad: Result, fn, expected_result) -> None:
    assert example(monad.is_ok_and, fn) == expected_result


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [pytest.param(Ok(1), add_one, Ok(2)), pytest.param(Err(1), add_one, Err(1))],
)
def test_map(monad: Result, fn, expected_result) -> None:
    assert example(monad.map, fn) == expected_result


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [pytest.param(Err(1), add_one, Err(2)), pytest.param(Ok(1), add_one, Ok(1))],
)
def test_map_err(monad: Result, fn, expected_result) -> None:
    assert example(monad.map_err, fn) == expected_result


@pytest.mark.parametrize(
    ("monad", "default", "fn", "expected_result"),
    [pytest.param(Ok("foo"), 42, len, 3), pytest.param(Err(), 42, len, 42)],
)
def test_map_or(monad: Result, default, fn, expected_result) -> None:
    assert example(monad.map_or, default, fn) == expected_result


@pytest.mark.parametrize(
    ("monad", "default", "fn", "expected_result"),
    [pytest.param(Ok("foo"), get_42, len, 3), pytest.param(Err(), get_42, len, 42)],
)
def test_map_or_else(monad: Result, default, fn, expected_result) -> None:
    assert example(monad.map_or_else, default, fn) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result"), [pytest.param(Ok(2), Some(2)), pytest.param(Err(2), Null())]
)
def test_ok(monad: Result, expected_result) -> None:
    assert example(monad.ok) == expected_result


@pytest.mark.parametrize(
    ("monad", "res", "expected_result"),
    [
        pytest.param(Ok(2), Err("foo"), Ok(2)),
        pytest.param(Err("foo"), Ok(100), Ok(100)),
        pytest.param(Ok(2), Ok(100), Ok(2)),
        pytest.param(Err("foo"), Err("foo"), Err("foo")),
    ],
)
def test_or_(monad: Result, res, expected_result) -> None:
    assert example(monad.or_, res) == expected_result


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [
        pytest.param(Ok("barbarians"), get_ok_vikings, Ok("barbarians")),
        pytest.param(Err("foo"), get_ok_vikings, Ok("vikings")),
        pytest.param(Err("foo"), Err, Err("foo")),
    ],
)
def test_or_else(monad: Result, fn, expected_result) -> None:
    assert example(monad.or_else, fn) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result", "expected_context"),
    [
        pytest.param(Ok(Some(5)), Some(Ok(5)), nullcontext()),
        pytest.param(Ok(Null()), Null(), nullcontext()),
        pytest.param(Err(), Some(Err()), nullcontext()),
        pytest.param(Ok(2), None, pytest.raises(TypeError)),
    ],
)
def test_transpose(monad: Result, expected_result, expected_context) -> None:
    with expected_context:
        assert example(monad.transpose) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result", "expected_context"),
    [pytest.param(Ok(2), 2, nullcontext()), pytest.param(Err(), None, pytest.raises(TypeError))],
)
def test_unwrap(monad: Result, expected_result, expected_context) -> None:
    with expected_context:
        assert example(monad.unwrap) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result", "expected_context"),
    [
        pytest.param(Err("failed"), "failed", nullcontext()),
        pytest.param(Ok(2), None, pytest.raises(TypeError)),
    ],
)
def test_unwrap_err(monad: Result, expected_result, expected_context) -> None:
    with expected_context:
        assert example(monad.unwrap_err) == expected_result


@pytest.mark.parametrize(
    ("monad", "default", "expected_result"),
    [pytest.param(Ok("car"), "bike", "car"), pytest.param(Err(), "bike", "bike")],
)
def test_unwrap_or(monad: Result, default, expected_result) -> None:
    assert example(monad.unwrap_or, default) == expected_result


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [pytest.param(Ok(4), get_42, 4), pytest.param(Err(), get_42, 42)],
)
def test_unwrap_or_else(monad: Result, fn, expected_result) -> None:
    assert example(monad.unwrap_or_else, fn) == expected_result
