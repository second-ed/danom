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
            id="If you call ``and_`` on an ``Ok`` with an ``Err`` as the arg then the ``Err`` takes precedence over the ``Ok``.",
        ),
        pytest.param(
            Err("early error"),
            Ok("foo"),
            Err("early error"),
            id="If you call ``and_`` on an ``Err`` with an ``Ok`` as the arg then the ``Err`` still takes precedence over the ``Ok``.",
        ),
        pytest.param(
            Err("not a 2"),
            Err("late error"),
            Err("not a 2"),
            id="If you call ``and_`` on an ``Err`` with an ``Err`` as the arg then the first ``Err`` is returned and the second is discarded.",
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
        pytest.param(
            Ok(2),
            must_be_less_than_10,
            Ok(2),
            id="An ``Ok`` passed to ``and_then`` returns the ``Ok`` produced by the function.",
        ),
        pytest.param(
            Ok(20),
            must_be_less_than_10,
            Err("too high"),
            id="When the function passed to ``and_then`` produces an ``Err``, that ``Err`` becomes the result.",
        ),
        pytest.param(
            Err("not a number"),
            must_be_less_than_10,
            Err("not a number"),
            id="An existing ``Err`` passes through ``and_then`` unchanged, without calling the function.",
        ),
    ],
)
def test_and_then(request, monad: Result, fn, expected_result) -> None:
    assert example(monad.and_then, fn, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result"),
    [
        pytest.param(
            Ok(2), Ok(2), id="Cloning an ``Ok`` creates a separate ``Ok`` with the same value."
        ),
        pytest.param(
            Err(2), Err(2), id="Cloning an ``Err`` creates a separate ``Err`` with the same value."
        ),
    ],
)
def test_cloned(request, monad: Result, expected_result) -> None:
    assert example(monad.cloned, description=request.node.callspec.id) == expected_result
    assert id(monad) != id(expected_result)


@pytest.mark.parametrize(
    ("monad", "expected_result"),
    [
        pytest.param(Ok(2), Null(), id="An ``Ok`` has no error, so ``err`` returns ``Null``."),
        pytest.param(
            Err("Nothing here"),
            Some("Nothing here"),
            id="If you call ``err`` on an ``Err`` then ``Some`` with the wrapped error is returned.",
        ),
    ],
)
def test_err(request, monad: Result, expected_result) -> None:
    assert example(monad.err, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "msg", "expected_result", "expected_context"),
    [
        pytest.param(
            Ok(2),
            "must be positive",
            2,
            nullcontext(),
            id="``expect`` extracts the value from an ``Ok``.",
        ),
        pytest.param(
            Err(),
            "must be positive",
            None,
            pytest.raises(ValueError),
            id="``expect`` raises ``ValueError`` for an ``Err`` and uses the supplied message.",
        ),
    ],
)
def test_expect(request, monad: Result, msg, expected_result, expected_context) -> None:
    with expected_context:
        assert example(monad.expect, msg, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "msg", "expected_result", "expected_context"),
    [
        pytest.param(
            Err(2),
            "must be err",
            2,
            nullcontext(),
            id="``expect_err`` extracts the error from an ``Err``.",
        ),
        pytest.param(
            Ok(),
            "must be err",
            None,
            pytest.raises(ValueError),
            id="``expect_err`` raises ``ValueError`` for an ``Ok`` and uses the supplied message.",
        ),
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
        pytest.param(
            Ok(Ok(Ok(2))),
            Ok(Ok(2)),
            id="If you call ``flatten`` on three nested ``Ok`` values then two nested ``Ok`` values are returned. Only the outer monad is removed",
        ),
        pytest.param(
            Ok(Ok(2)),
            Ok(2),
            id="This is made obvious calling ``flatten`` on a doubly wrapped value returning just the inner monad.",
        ),
        pytest.param(
            Ok(2),
            Ok(2),
            id="Calling ``flatten`` if the inner is not a monad of the same type is a no-op.",
        ),
        pytest.param(Err(), Err(), id="An ``Err`` passes through ``flatten`` unchanged."),
    ],
)
def test_flatten(request, monad: Result, expected_result) -> None:
    assert example(monad.flatten, description=request.node.callspec.id) == expected_result


def append_to_list(x) -> None:
    x.append(2)


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [
        pytest.param(
            Ok([1]),
            append_to_list,
            Ok([1]),
            id="If you call ``inspect`` on an ``Ok`` then the original ``Ok`` is returned after the function is called, this is used for logging or side outputs that shouldn't disrupt the existing flow.",
        ),
        pytest.param(
            Err("un-appendable"),
            append_to_list,
            Err("un-appendable"),
            id="If you call ``inspect`` on an ``Err`` then the ``Err`` is returned and the function is not called.",
        ),
    ],
)
def test_inspect(request, monad: Result, fn, expected_result) -> None:
    assert example(monad.inspect, fn, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [
        pytest.param(
            Err([1]),
            append_to_list,
            Err([1]),
            id="If you call ``inspect_err`` on an ``Err`` then the original ``Err`` is returned after the function is called, it's essentially the inverse of ``inspect``.",
        ),
        pytest.param(
            Ok("un-appendable"),
            append_to_list,
            Ok("un-appendable"),
            id="Similarly to calling ``inspect`` on an ``Err``, if you call ``inspect_err`` on an ``Ok`` then the ``Ok`` is returned and the function is not called.",
        ),
    ],
)
def test_inspect_err(request, monad: Result, fn, expected_result) -> None:
    assert example(monad.inspect_err, fn, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result"),
    [
        pytest.param(Ok(2), False, id="``is_err`` reports ``False`` for an ``Ok``."),
        pytest.param(Err(2), True, id="For an ``Err``, ``is_err`` reports ``True``."),
    ],
)
def test_is_err(request, monad: Result, expected_result) -> None:
    assert example(monad.is_err, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [
        pytest.param(
            Err(1),
            is_even,
            False,
            id="``is_err_and`` requires both the monad to be an ``Err`` and the returned value of the passed in callable to be ``True``, for example, if you called ``is_err_and`` with a function that checks for evenness on an ``Err(1)`` then the result is ``False``.",
        ),
        pytest.param(
            Err(2),
            is_even,
            True,
            id="Therefore, if you call ``is_err_and`` on an ``Err`` with a function that returns ``True`` then ``True`` is returned.",
        ),
        pytest.param(
            Ok(2),
            is_even,
            False,
            id="Whereas, if you call ``is_err_and`` on an ``Ok`` with a function then ``False`` is returned and the function is not called.",
        ),
    ],
)
def test_is_err_and(request, monad: Result, fn, expected_result) -> None:
    assert example(monad.is_err_and, fn, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result"),
    [
        pytest.param(Ok(2), True, id="``is_ok`` reports ``True`` for an ``Ok``."),
        pytest.param(Err(2), False, id="For an ``Err``, ``is_ok`` reports ``False``."),
    ],
)
def test_is_ok(request, monad: Result, expected_result) -> None:
    assert example(monad.is_ok, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [
        pytest.param(
            Ok(1),
            is_even,
            False,
            id="When the predicate rejects an ``Ok``, ``is_ok_and`` reports ``False``.",
        ),
        pytest.param(
            Ok(2),
            is_even,
            True,
            id="When the predicate accepts an ``Ok``, ``is_ok_and`` reports ``True``.",
        ),
        pytest.param(
            Err(2),
            is_even,
            False,
            id="An ``Err`` makes ``is_ok_and`` report ``False`` without calling the predicate.",
        ),
    ],
)
def test_is_ok_and(request, monad: Result, fn, expected_result) -> None:
    assert example(monad.is_ok_and, fn, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [
        pytest.param(
            Ok(1),
            add_one,
            Ok(2),
            id="Mapping an ``Ok`` applies the function and wraps its result in a new ``Ok``.",
        ),
        pytest.param(
            Err(1),
            add_one,
            Err(1),
            id="Mapping an ``Err`` leaves it unchanged and skips the function.",
        ),
    ],
)
def test_map(request, monad: Result, fn, expected_result) -> None:
    assert example(monad.map, fn, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [
        pytest.param(
            Err(1),
            add_one,
            Err(2),
            id="Mapping an ``Err`` applies the function and wraps its result in a new ``Err``.",
        ),
        pytest.param(
            Ok(1),
            add_one,
            Ok(1),
            id="Mapping an ``Ok`` leaves it unchanged and skips the function.",
        ),
    ],
)
def test_map_err(request, monad: Result, fn, expected_result) -> None:
    assert example(monad.map_err, fn, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "default", "fn", "expected_result"),
    [
        pytest.param(
            Ok("foo"),
            42,
            len,
            3,
            id="For an ``Ok``, ``map_or`` uses the function result instead of the default.",
        ),
        pytest.param(
            Err(), 42, len, 42, id="For an ``Err``, ``map_or`` returns the supplied default."
        ),
    ],
)
def test_map_or(request, monad: Result, default, fn, expected_result) -> None:
    assert (
        example(monad.map_or, default, fn, description=request.node.callspec.id) == expected_result
    )


@pytest.mark.parametrize(
    ("monad", "default", "fn", "expected_result"),
    [
        pytest.param(
            Ok("foo"),
            get_42,
            len,
            3,
            id="An ``Ok`` makes ``map_or_else`` use the mapping function.",
        ),
        pytest.param(
            Err(), get_42, len, 42, id="An ``Err`` makes ``map_or_else`` use the default function."
        ),
    ],
)
def test_map_or_else(request, monad: Result, default, fn, expected_result) -> None:
    assert (
        example(monad.map_or_else, default, fn, description=request.node.callspec.id)
        == expected_result
    )


@pytest.mark.parametrize(
    ("monad", "expected_result"),
    [
        pytest.param(Ok(2), Some(2), id="An ``Ok`` converts to ``Some`` through ``ok``."),
        pytest.param(Err(2), Null(), id="An ``Err`` converts to ``Null`` through ``ok``."),
    ],
)
def test_ok(request, monad: Result, expected_result) -> None:
    assert example(monad.ok, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "res", "expected_result"),
    [
        pytest.param(
            Ok(2),
            Err("foo"),
            Ok(2),
            id="An ``Ok`` keeps its value when ``or_`` receives an ``Err``.",
        ),
        pytest.param(
            Err("foo"), Ok(100), Ok(100), id="An ``Err`` gives way to an ``Ok`` passed to ``or_``."
        ),
        pytest.param(
            Ok(2), Ok(100), Ok(2), id="When both values are ``Ok``, ``or_`` keeps the first one."
        ),
        pytest.param(
            Err("foo"),
            Err("foo"),
            Err("foo"),
            id="When both values are ``Err``, ``or_`` keeps the first error.",
        ),
    ],
)
def test_or_(request, monad: Result, res, expected_result) -> None:
    assert example(monad.or_, res, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [
        pytest.param(
            Ok("barbarians"),
            get_ok_vikings,
            Ok("barbarians"),
            id="An ``Ok`` passes through ``or_else`` without calling the function.",
        ),
        pytest.param(
            Err("foo"),
            get_ok_vikings,
            Ok("vikings"),
            id="For an ``Err``, ``or_else`` returns the ``Ok`` produced by the function.",
        ),
        pytest.param(
            Err("foo"),
            Err,
            Err("foo"),
            id="If the fallback also produces an ``Err``, ``or_else`` keeps the original error.",
        ),
    ],
)
def test_or_else(request, monad: Result, fn, expected_result) -> None:
    assert example(monad.or_else, fn, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result", "expected_context"),
    [
        pytest.param(
            Ok(Some(5)),
            Some(Ok(5)),
            nullcontext(),
            id="Transposing ``Ok(Some(value))`` produces ``Some(Ok(value))``.",
        ),
        pytest.param(
            Ok(Null()), Null(), nullcontext(), id="Transposing ``Ok(Null())`` produces ``Null``."
        ),
        pytest.param(
            Err(), Some(Err()), nullcontext(), id="Transposing an ``Err`` wraps it in ``Some``."
        ),
        pytest.param(
            Ok(2),
            None,
            pytest.raises(TypeError),
            id="Transposing an ``Ok`` with an unsupported value raises ``TypeError``.",
        ),
    ],
)
def test_transpose(request, monad: Result, expected_result, expected_context) -> None:
    with expected_context:
        assert example(monad.transpose, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result", "expected_context"),
    [
        pytest.param(Ok(2), 2, nullcontext(), id="``unwrap`` extracts the value from an ``Ok``."),
        pytest.param(
            Err(),
            None,
            pytest.raises(TypeError),
            id="``unwrap`` raises ``TypeError`` when the result is an ``Err``.",
        ),
    ],
)
def test_unwrap(request, monad: Result, expected_result, expected_context) -> None:
    with expected_context:
        assert example(monad.unwrap, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result", "expected_context"),
    [
        pytest.param(
            Err("failed"),
            "failed",
            nullcontext(),
            id="``unwrap_err`` extracts the error from an ``Err``.",
        ),
        pytest.param(
            Ok(2),
            None,
            pytest.raises(TypeError),
            id="``unwrap_err`` raises ``TypeError`` when the result is an ``Ok``.",
        ),
    ],
)
def test_unwrap_err(request, monad: Result, expected_result, expected_context) -> None:
    with expected_context:
        assert example(monad.unwrap_err, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "default", "expected_result"),
    [
        pytest.param(
            Ok("car"),
            "bike",
            "car",
            id="With an ``Ok``, ``unwrap_or`` returns the value and ignores the default.",
        ),
        pytest.param(
            Err(), "bike", "bike", id="With an ``Err``, ``unwrap_or`` returns the default."
        ),
    ],
)
def test_unwrap_or(request, monad: Result, default, expected_result) -> None:
    assert (
        example(monad.unwrap_or, default, description=request.node.callspec.id) == expected_result
    )


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [
        pytest.param(
            Ok(4),
            get_42,
            4,
            id="An ``Ok`` makes ``unwrap_or_else`` return its value without calling the function.",
        ),
        pytest.param(
            Err(), get_42, 42, id="An ``Err`` makes ``unwrap_or_else`` return the function result."
        ),
    ],
)
def test_unwrap_or_else(request, monad: Result, fn, expected_result) -> None:
    assert (
        example(monad.unwrap_or_else, fn, description=request.node.callspec.id) == expected_result
    )
