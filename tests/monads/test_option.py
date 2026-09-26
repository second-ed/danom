from contextlib import nullcontext

import pytest

from danom import Err, Null, Ok, Option, Some
from dev_tools.create_examples.collection.example import example
from tests.conftest import add_one, get_42, get_some_vikings, is_even


@pytest.mark.parametrize(
    ("monad", "opt_b", "expected_result"),
    [
        pytest.param(
            Some(2),
            Null(),
            Null(),
            id="A ``Some`` combined with ``Null`` through ``and_`` produces ``Null``.",
        ),
        pytest.param(
            Null(),
            Some("foo"),
            Null(),
            id="A ``Null`` combined with an ``Some`` through ``and_`` remains ``Null``.",
        ),
        pytest.param(
            Some(2),
            Some("foo"),
            Some("foo"),
            id="When both options contain values, ``and_`` keeps the second ``Some``.",
        ),
        pytest.param(
            Null(),
            Null(),
            Null(),
            id="Combining two ``Null`` values with ``and_`` produces ``Null``.",
        ),
    ],
)
def test_and_(request, monad: Option, opt_b, expected_result) -> None:
    assert example(monad.and_, opt_b, description=request.node.callspec.id) == expected_result


def must_be_less_than_10(x: int) -> Option[int]:
    return Some(x) if x < 10 else Null()


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [
        pytest.param(
            Some(2),
            must_be_less_than_10,
            Some(2),
            id="A successful function passed to ``and_then`` returns its ``Some`` result.",
        ),
        pytest.param(
            Some(20),
            must_be_less_than_10,
            Null(),
            id="When the function returns ``Null``, ``and_then`` passes that ``Null`` through.",
        ),
        pytest.param(
            Null(),
            must_be_less_than_10,
            Null(),
            id="An existing ``Null`` skips the function passed to ``and_then``.",
        ),
    ],
)
def test_and_then(request, monad: Option, fn, expected_result) -> None:
    assert example(monad.and_then, fn, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result"),
    [
        pytest.param(Some(2), [2], id="A ``Some`` becomes a one-item list through ``as_list``."),
        pytest.param(Null(), [], id="``as_list`` represents ``Null`` as an empty list."),
    ],
)
def test_as_list(request, monad: Option, expected_result) -> None:
    assert example(monad.as_list, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result"),
    [
        pytest.param(Some(2), (2,), id="A ``Some`` becomes a one-item tuple through ``as_tuple``."),
        pytest.param(Null(), (), id="``as_tuple`` represents ``Null`` as an empty tuple."),
    ],
)
def test_as_tuple(request, monad: Option, expected_result) -> None:
    assert example(monad.as_tuple, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result"),
    [
        pytest.param(
            Some(2), Some(2), id="Cloning a ``Some`` creates a separate option with the same value."
        ),
        pytest.param(Null(), Null(), id="Cloning ``Null`` creates a separate ``Null``."),
    ],
)
def test_cloned(request, monad: Option, expected_result) -> None:
    assert example(monad.cloned, description=request.node.callspec.id) == expected_result
    assert id(monad) != id(expected_result)


@pytest.mark.parametrize(
    ("monad", "msg", "expected_result", "expected_context"),
    [
        pytest.param(
            Some(2),
            "must be positive",
            2,
            nullcontext(),
            id="``expect`` extracts the value from a ``Some``.",
        ),
        pytest.param(
            Null(),
            "must be positive",
            None,
            pytest.raises(ValueError),
            id="``expect`` raises ``ValueError`` for ``Null`` and uses the supplied message.",
        ),
    ],
)
def test_expect(request, monad: Option, msg, expected_result, expected_context) -> None:
    with expected_context:
        assert example(monad.expect, msg, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "predicate", "expected_result"),
    [
        pytest.param(
            Some(3),
            is_even,
            Null(),
            id="A ``Some`` that fails the predicate becomes ``Null`` through ``filter_``.",
        ),
        pytest.param(
            Some(4), is_even, Some(4), id="A ``Some`` that passes the predicate remains unchanged."
        ),
        pytest.param(
            Null(),
            is_even,
            Null(),
            id="``filter_`` leaves ``Null`` unchanged without calling the predicate.",
        ),
    ],
)
def test_filter_(request, monad: Option, predicate, expected_result) -> None:
    assert (
        example(monad.filter_, predicate, description=request.node.callspec.id) == expected_result
    )


@pytest.mark.parametrize(
    ("monad", "expected_result"),
    [
        pytest.param(
            Some(Some(Some(2))),
            Some(Some(2)),
            id="Flattening three nested ``Some`` values removes only the outer option.",
        ),
        pytest.param(
            Some(Some(2)),
            Some(2),
            id="Flattening a doubly wrapped value returns the inner ``Some``.",
        ),
        pytest.param(
            Some(2), Some(2), id="Flattening a ``Some`` with a non-option value does nothing."
        ),
        pytest.param(Null(), Null(), id="A ``Null`` passes through ``flatten`` unchanged."),
    ],
)
def test_flatten(request, monad: Option, expected_result) -> None:
    assert example(monad.flatten, description=request.node.callspec.id) == expected_result


def append_to_list(x) -> None:
    x.append(2)


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [
        pytest.param(
            Some([1]),
            append_to_list,
            Some([1]),
            id="Inspecting a ``Some`` calls the function and returns the original option.",
        ),
        pytest.param(
            Null(),
            append_to_list,
            Null(),
            id="Inspecting ``Null`` returns ``Null`` without calling the function.",
        ),
    ],
)
def test_inspect(request, monad: Option, fn, expected_result) -> None:
    assert example(monad.inspect, fn, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result"),
    [
        pytest.param(Some(2), False, id="``is_none`` reports ``False`` for a ``Some``."),
        pytest.param(Null(), True, id="For ``Null``, ``is_none`` reports ``True``."),
    ],
)
def test_is_none(request, monad: Option, expected_result) -> None:
    assert example(monad.is_none, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [
        pytest.param(
            Some(1),
            is_even,
            False,
            id="When the predicate rejects a ``Some``, ``is_none_or`` reports ``False``.",
        ),
        pytest.param(
            Some(2),
            is_even,
            True,
            id="When the predicate accepts a ``Some``, ``is_none_or`` reports ``True``.",
        ),
        pytest.param(
            Null(),
            is_even,
            True,
            id="``Null`` makes ``is_none_or`` report ``True`` without calling the predicate.",
        ),
    ],
)
def test_is_none_or(request, monad: Option, fn, expected_result) -> None:
    assert example(monad.is_none_or, fn, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result"),
    [
        pytest.param(Some(2), True, id="``is_some`` reports ``True`` for a ``Some``."),
        pytest.param(Null(), False, id="For ``Null``, ``is_some`` reports ``False``."),
    ],
)
def test_is_some(request, monad: Option, expected_result) -> None:
    assert example(monad.is_some, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [
        pytest.param(
            Some(1),
            is_even,
            False,
            id="When the predicate rejects a ``Some``, ``is_some_and`` reports ``False``.",
        ),
        pytest.param(
            Some(2),
            is_even,
            True,
            id="When the predicate accepts a ``Some``, ``is_some_and`` reports ``True``.",
        ),
        pytest.param(
            Null(),
            is_even,
            False,
            id="A ``Null`` makes ``is_some_and`` report ``False`` without calling the predicate.",
        ),
    ],
)
def test_is_some_and(request, monad: Option, fn, expected_result) -> None:
    assert example(monad.is_some_and, fn, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [
        pytest.param(
            Some(1),
            add_one,
            Some(2),
            id="Mapping a ``Some`` applies the function and wraps its result in a new ``Some``.",
        ),
        pytest.param(
            Null(),
            add_one,
            Null(),
            id="Mapping ``Null`` leaves it unchanged and skips the function.",
        ),
    ],
)
def test_map(request, monad: Option, fn, expected_result) -> None:
    assert example(monad.map, fn, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "default", "fn", "expected_result"),
    [
        pytest.param(
            Some("foo"),
            42,
            len,
            3,
            id="For a ``Some``, ``map_or`` uses the function result instead of the default.",
        ),
        pytest.param(
            Null(), 42, len, 42, id="For ``Null``, ``map_or`` returns the supplied default."
        ),
    ],
)
def test_map_or(request, monad: Option, default, fn, expected_result) -> None:
    assert (
        example(monad.map_or, default, fn, description=request.node.callspec.id) == expected_result
    )


@pytest.mark.parametrize(
    ("monad", "default", "fn", "expected_result"),
    [
        pytest.param(
            Some("foo"),
            get_42,
            len,
            3,
            id="A ``Some`` makes ``map_or_else`` use the mapping function.",
        ),
        pytest.param(
            Null(), get_42, len, 42, id="A ``Null`` makes ``map_or_else`` use the default function."
        ),
    ],
)
def test_map_or_else(request, monad: Option, default, fn, expected_result) -> None:
    assert (
        example(monad.map_or_else, default, fn, description=request.node.callspec.id)
        == expected_result
    )


@pytest.mark.parametrize(
    ("monad", "err", "expected_result"),
    [
        pytest.param(
            Some("foo"), 0, Ok("foo"), id="A ``Some`` converts to ``Ok`` through ``ok_or``."
        ),
        pytest.param(Null(), 0, Err(0), id="A ``Null`` converts to ``Err`` through ``ok_or``."),
    ],
)
def test_ok_or(request, monad: Option, err, expected_result) -> None:
    assert example(monad.ok_or, err, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "err", "expected_result"),
    [
        pytest.param(
            Some("foo"),
            get_42,
            Ok("foo"),
            id="A ``Some`` converts to ``Ok`` without calling the error function.",
        ),
        pytest.param(
            Null(),
            get_42,
            Err(42),
            id="A ``Null`` converts to ``Err`` using the error function result.",
        ),
    ],
)
def test_ok_or_else(request, monad: Option, err, expected_result) -> None:
    assert example(monad.ok_or_else, err, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "opt_b", "expected_result"),
    [
        pytest.param(
            Some(2),
            Null(),
            Some(2),
            id="A ``Some`` keeps its value when ``or_`` receives ``Null``.",
        ),
        pytest.param(
            Null(), Some(100), Some(100), id="A ``Null`` gives way to a ``Some`` passed to ``or_``."
        ),
        pytest.param(
            Some(2),
            Some(100),
            Some(2),
            id="When both options contain values, ``or_`` keeps the first ``Some``.",
        ),
        pytest.param(
            Null(), Null(), Null(), id="When both options are ``Null``, ``or_`` returns ``Null``."
        ),
    ],
)
def test_or_(request, monad: Option, opt_b, expected_result) -> None:
    assert example(monad.or_, opt_b, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "opt_b", "expected_result"),
    [
        pytest.param(
            Some("barbarians"),
            get_some_vikings,
            Some("barbarians"),
            id="A ``Some`` passes through ``or_else`` without calling the function.",
        ),
        pytest.param(
            Null(),
            get_some_vikings,
            Some("vikings"),
            id="For ``Null``, ``or_else`` returns the ``Some`` produced by the function.",
        ),
        pytest.param(
            Null(),
            Null,
            Null(),
            id="If the fallback also produces ``Null``, ``or_else`` returns ``Null``.",
        ),
    ],
)
def test_or_else(request, monad: Option, opt_b, expected_result) -> None:
    assert example(monad.or_else, opt_b, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "value", "expected_result"),
    [
        pytest.param(
            Some(2),
            5,
            Some(5),
            id="Replacing a ``Some`` returns a new ``Some`` with the replacement value.",
        ),
        pytest.param(Null(), 3, Null(), id="Replacing ``Null`` leaves it as ``Null``."),
    ],
)
def test_replace(request, monad: Option, value, expected_result) -> None:
    assert example(monad.replace, value, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result", "expected_context"),
    [
        pytest.param(
            Some(Ok(2)),
            Ok(Some(2)),
            nullcontext(),
            id="Transposing ``Some(Ok(value))`` produces ``Ok(Some(value))``.",
        ),
        pytest.param(
            Some(Err(2)),
            Err(Some(2)),
            nullcontext(),
            id="Transposing ``Some(Err(error))`` produces ``Err(Some(error))``.",
        ),
        pytest.param(
            Null(), Ok(Null()), nullcontext(), id="Transposing ``Null`` produces ``Ok(Null())``."
        ),
        pytest.param(
            Some(2),
            None,
            pytest.raises(TypeError),
            id="Transposing a ``Some`` with an unsupported value raises ``TypeError``.",
        ),
    ],
)
def test_transpose(request, monad: Option, expected_result, expected_context) -> None:
    with expected_context:
        assert example(monad.transpose, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result", "expected_context"),
    [
        pytest.param(
            Some(2), 2, nullcontext(), id="``unwrap`` extracts the value from a ``Some``."
        ),
        pytest.param(
            Null(),
            None,
            pytest.raises(TypeError),
            id="``unwrap`` raises ``TypeError`` when the option is ``Null``.",
        ),
    ],
)
def test_unwrap(request, monad: Option, expected_result, expected_context) -> None:
    with expected_context:
        assert example(monad.unwrap, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "default", "expected_result"),
    [
        pytest.param(
            Some("car"),
            "bike",
            "car",
            id="With a ``Some``, ``unwrap_or`` returns the value and ignores the default.",
        ),
        pytest.param(
            Null(), "bike", "bike", id="With ``Null``, ``unwrap_or`` returns the default."
        ),
    ],
)
def test_unwrap_or(request, monad: Option, default, expected_result) -> None:
    assert (
        example(monad.unwrap_or, default, description=request.node.callspec.id) == expected_result
    )


@pytest.mark.parametrize(
    ("monad", "fn", "expected_result"),
    [
        pytest.param(
            Some(4),
            get_42,
            4,
            id="A ``Some`` makes ``unwrap_or_else`` return its value without calling the function.",
        ),
        pytest.param(
            Null(), get_42, 42, id="A ``Null`` makes ``unwrap_or_else`` return the function result."
        ),
    ],
)
def test_unwrap_or_else(request, monad: Option, fn, expected_result) -> None:
    assert (
        example(monad.unwrap_or_else, fn, description=request.node.callspec.id) == expected_result
    )


@pytest.mark.parametrize(
    ("monad", "other", "expected_result"),
    [
        pytest.param(
            Some(1),
            Some("hi"),
            Some((1, "hi")),
            id="Zipping two ``Some`` values produces a ``Some`` containing both values.",
        ),
        pytest.param(
            Some(1), Null(), Null(), id="Zipping a ``Some`` with ``Null`` produces ``Null``."
        ),
        pytest.param(
            Null(), Some(1), Null(), id="Zipping ``Null`` with a ``Some`` produces ``Null``."
        ),
    ],
)
def test_zip(request, monad: Option, other, expected_result) -> None:
    assert example(monad.zip, other, description=request.node.callspec.id) == expected_result


@pytest.mark.parametrize(
    ("monad", "expected_result"),
    [
        pytest.param(
            Some((2, 2)),
            (Some(2), Some(2)),
            id="Unzipping a ``Some`` pair produces two ``Some`` values.",
        ),
        pytest.param(
            Some(4),
            (Null(), Null()),
            id="Unzipping a ``Some`` with a non-pair value produces two ``Null`` values.",
        ),
        pytest.param(
            Null(), (Null(), Null()), id="Unzipping ``Null`` produces two ``Null`` values."
        ),
    ],
)
def test_unzip(request, monad: Option, expected_result) -> None:
    assert example(monad.unzip, description=request.node.callspec.id) == expected_result
