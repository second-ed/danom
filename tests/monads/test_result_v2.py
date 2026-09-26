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
        pytest.param(
            Ok(2),
            Err("late error"),
            Err("late error"),
            id="Calling ``and_`` on an ``Ok`` with an ``Err`` as the arg then the ``Err`` takes precedence over the ``Ok``.",
        ),
        pytest.param(
            Err("early error"),
            Ok("foo"),
            Err("early error"),
            id="Calling ``and_`` on an ``Err`` with an ``Ok`` as the arg then the ``Err`` still takes precedence over the ``Ok``.",
        ),
        pytest.param(
            Err("not a 2"),
            Err("late error"),
            Err("not a 2"),
            id="Calling ``and_`` on an ``Err`` with an ``Err`` as the arg then the first ``Err`` is returned and the second is discarded.",
        ),
        pytest.param(
            Ok(2),
            Ok("different result type"),
            Ok("different result type"),
            id="Whereas, calling ``and_`` on an ``Ok`` with another ``Ok`` as the arg then the first ``Ok`` is discarded and the second is returned.",
        ),
    ],
)
def test_and_(request, monad: Result, res, expected_result) -> None:
    assert example(monad.and_, res, description=request.node.callspec.id) == expected_result


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
def test_and_then(request, monad: Result, fn, expected_result) -> None:
    assert example(monad.and_then, fn, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result"), [pytest.param(Ok(2), Ok(2)), pytest.param(Err(2), Err(2))]
)
def test_cloned(request, monad: Result, expected_result) -> None:
    assert example(monad.cloned, description=request.node.callspec.id) == expected_result
    assert id(monad) != id(expected_result)


@pytest.mark.parametrize(
    ("monad", "expected_result"),
    [pytest.param(Ok(2), Null()), pytest.param(Err("Nothing here"), Some("Nothing here"))],
)
def test_err(request, monad: Result, expected_result) -> None:
    assert example(monad.err, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "msg", "expected_result", "expected_context"),
    [
        pytest.param(Ok(2), "must be positive", 2, nullcontext()),
        pytest.param(Err(), "must be positive", None, pytest.raises(ValueError)),
    ],
)
def test_expect(request, monad: Result, msg, expected_result, expected_context) -> None:
    with expected_context:
        assert example(monad.expect, msg, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "msg", "expected_result", "expected_context"),
    [
        pytest.param(Err(2), "must be err", 2, nullcontext()),
        pytest.param(Ok(), "must be err", None, pytest.raises(ValueError)),
    ],
)
def test_expect_err(request, monad: Result, msg, expected_result, expected_context) -> None:
    with expected_context:
        assert (
            example(monad.expect_err, msg, description=request.node.callspec.id) == expected_result
        )


@pytest.mark.parametrize(
    ("monad", "expected_result"),
    [
        pytest.param(Ok(Ok(Ok(2))), Ok(Ok(2))),
        pytest.param(Ok(Ok(2)), Ok(2)),
        pytest.param(Ok(2), Ok(2)),
        pytest.param(Err(), Err()),
    ],
)
def test_flatten(request, monad: Result, expected_result) -> None:
    assert example(monad.flatten, description=request.node.callspec.id) == expected_result


def append_to_list(x) -> None:
    x.append(2)


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [
        pytest.param(Ok([1]), append_to_list, Ok([1])),
        pytest.param(Err("un-appendable"), append_to_list, Err("un-appendable")),
    ],
)
def test_inspect(request, monad: Result, fn, expected_result) -> None:
    assert example(monad.inspect, fn, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [
        pytest.param(Err([1]), append_to_list, Err([1])),
        pytest.param(Ok("un-appendable"), append_to_list, Ok("un-appendable")),
    ],
)
def test_inspect_err(request, monad: Result, fn, expected_result) -> None:
    assert example(monad.inspect_err, fn, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result"), [pytest.param(Ok(2), False), pytest.param(Err(2), True)]
)
def test_is_err(request, monad: Result, expected_result) -> None:
    assert example(monad.is_err, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [
        pytest.param(Err(1), is_even, False),
        pytest.param(Err(2), is_even, True),
        pytest.param(Ok(2), is_even, False),
    ],
)
def test_is_err_and(request, monad: Result, fn, expected_result) -> None:
    assert example(monad.is_err_and, fn, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result"), [pytest.param(Ok(2), True), pytest.param(Err(2), False)]
)
def test_is_ok(request, monad: Result, expected_result) -> None:
    assert example(monad.is_ok, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [
        pytest.param(Ok(1), is_even, False),
        pytest.param(Ok(2), is_even, True),
        pytest.param(Err(2), is_even, False),
    ],
)
def test_is_ok_and(request, monad: Result, fn, expected_result) -> None:
    assert example(monad.is_ok_and, fn, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [pytest.param(Ok(1), add_one, Ok(2)), pytest.param(Err(1), add_one, Err(1))],
)
def test_map(request, monad: Result, fn, expected_result) -> None:
    assert example(monad.map, fn, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [pytest.param(Err(1), add_one, Err(2)), pytest.param(Ok(1), add_one, Ok(1))],
)
def test_map_err(request, monad: Result, fn, expected_result) -> None:
    assert example(monad.map_err, fn, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "default", "fn", "expected_result"),
    [pytest.param(Ok("foo"), 42, len, 3), pytest.param(Err(), 42, len, 42)],
)
def test_map_or(request, monad: Result, default, fn, expected_result) -> None:
    assert (
        example(monad.map_or, default, fn, description=request.node.callspec.id) == expected_result
    )


@pytest.mark.parametrize(
    ("monad", "default", "fn", "expected_result"),
    [pytest.param(Ok("foo"), get_42, len, 3), pytest.param(Err(), get_42, len, 42)],
)
def test_map_or_else(request, monad: Result, default, fn, expected_result) -> None:
    assert (
        example(monad.map_or_else, default, fn, description=request.node.callspec.id)
        == expected_result
    )


@pytest.mark.parametrize(
    ("monad", "expected_result"), [pytest.param(Ok(2), Some(2)), pytest.param(Err(2), Null())]
)
def test_ok(request, monad: Result, expected_result) -> None:
    assert example(monad.ok, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "res", "expected_result"),
    [
        pytest.param(Ok(2), Err("foo"), Ok(2)),
        pytest.param(Err("foo"), Ok(100), Ok(100)),
        pytest.param(Ok(2), Ok(100), Ok(2)),
        pytest.param(Err("foo"), Err("foo"), Err("foo")),
    ],
)
def test_or_(request, monad: Result, res, expected_result) -> None:
    assert example(monad.or_, res, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [
        pytest.param(Ok("barbarians"), get_ok_vikings, Ok("barbarians")),
        pytest.param(Err("foo"), get_ok_vikings, Ok("vikings")),
        pytest.param(Err("foo"), Err, Err("foo")),
    ],
)
def test_or_else(request, monad: Result, fn, expected_result) -> None:
    assert example(monad.or_else, fn, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result", "expected_context"),
    [
        pytest.param(Ok(Some(5)), Some(Ok(5)), nullcontext()),
        pytest.param(Ok(Null()), Null(), nullcontext()),
        pytest.param(Err(), Some(Err()), nullcontext()),
        pytest.param(Ok(2), None, pytest.raises(TypeError)),
    ],
)
def test_transpose(request, monad: Result, expected_result, expected_context) -> None:
    with expected_context:
        assert example(monad.transpose, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result", "expected_context"),
    [pytest.param(Ok(2), 2, nullcontext()), pytest.param(Err(), None, pytest.raises(TypeError))],
)
def test_unwrap(request, monad: Result, expected_result, expected_context) -> None:
    with expected_context:
        assert example(monad.unwrap, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result", "expected_context"),
    [
        pytest.param(Err("failed"), "failed", nullcontext()),
        pytest.param(Ok(2), None, pytest.raises(TypeError)),
    ],
)
def test_unwrap_err(request, monad: Result, expected_result, expected_context) -> None:
    with expected_context:
        assert example(monad.unwrap_err, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "default", "expected_result"),
    [pytest.param(Ok("car"), "bike", "car"), pytest.param(Err(), "bike", "bike")],
)
def test_unwrap_or(request, monad: Result, default, expected_result) -> None:
    assert (
        example(monad.unwrap_or, default, description=request.node.callspec.id) == expected_result
    )


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [pytest.param(Ok(4), get_42, 4), pytest.param(Err(), get_42, 42)],
)
def test_unwrap_or_else(request, monad: Result, fn, expected_result) -> None:
    assert (
        example(monad.unwrap_or_else, fn, description=request.node.callspec.id) == expected_result
    )
