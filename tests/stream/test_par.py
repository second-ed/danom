from contextlib import nullcontext
from multiprocessing import Manager

import pytest
from hypothesis import given
from hypothesis import strategies as st

from danom import ParStream
from danom._either import Right
from danom._result import Err, Ok
from danom._stream._sync import _FILTER, _MAP, _TAP
from tests.conftest import ValueLogger, add, add_one, divisible_by_3
from tests.stream._common import basic_partition, basic_pipeline


@pytest.mark.parametrize(
    ("stream_cls", "kwargs"),
    [
        pytest.param(ParStream, {}, id="simple `collect`"),
        pytest.param(ParStream, {"workers": 4}, id="`collect` with workers passed in"),
        pytest.param(ParStream, {"workers": -1}, id="`collect` with n-1 workers"),
        pytest.param(
            ParStream, {"workers": 0}, id="`collect` with 0 workers falls back to 1 worker"
        ),
        pytest.param(ParStream, {"use_threads": True}, id="`collect` with threads True"),
    ],
)
@pytest.mark.parametrize(
    ("fn", "it", "expected_result"),
    [
        pytest.param(basic_partition, range(10), ((6, 12), (1, 3, 5, 7, 9))),
        pytest.param(basic_partition, 0, ((), (1,))),
        pytest.param(basic_pipeline, range(30), (15, 30), id="works with iterator"),
        pytest.param(basic_pipeline, 28, (30,), id="works with single value"),
    ],
)
def test_stream_pipeline(stream_cls, kwargs, fn, it, expected_result) -> None:
    assert fn(stream_cls, it, kwargs) == expected_result


@pytest.mark.parametrize(
    ("starting", "initial", "fn", "workers", "expected_result"),
    [
        pytest.param(range(10), 0, add, 1, 45),
        pytest.param(range(10), 0, add, 4, 45),
        pytest.param(range(10), 5, add, 4, 50),
    ],
)
def test_fold(starting, initial, fn, workers, expected_result):
    assert ParStream.from_iterable(starting).fold(initial, fn, workers=workers) == expected_result


@pytest.mark.parametrize(
    "kwargs",
    [
        pytest.param({}, id="simple `collect`"),
        pytest.param({"workers": 4}, id="`collect` with workers passed in"),
        pytest.param({"workers": -1}, id="`collect` with n-1 workers"),
        pytest.param({"use_threads": True}, id="`collect` with threads True"),
    ],
)
def test_tap(kwargs):
    with Manager() as manager:
        values = manager.list()
        val_logger = ValueLogger(values)

        assert (
            ParStream.from_iterable(range(4))
            .map(add, b=1)
            .tap(val_logger)
            .tap(val_logger)
            .map(add_one)
            .collect(**kwargs)
        ) == (2, 3, 4, 5)
        assert sorted(values) == [1, 1, 2, 2, 3, 3, 4, 4]


@pytest.mark.parametrize(
    ("kwargs"),
    [
        pytest.param({}, id="simple `collect`"),
        pytest.param({"workers": 4}, id="`collect` with workers passed in"),
        pytest.param({"workers": -1}, id="`collect` with n-1 workers"),
        pytest.param({"use_threads": True}, id="`collect` with threads True"),
    ],
)
@pytest.mark.parametrize(
    ("seq", "expected_result", "expected_context"),
    [
        pytest.param(
            (Ok(0), Ok(1), Ok(2)),
            Ok(ParStream.from_iterable((0, 1, 2))),
            nullcontext(),
            id="sequence of Oks returns Ok[tuple[T]]",
        ),
        pytest.param(
            (Right(0), Right(1), Right(2)),
            Right(ParStream.from_iterable((0, 1, 2))),
            nullcontext(),
            id="sequence of Rights returns Right[tuple[T]]",
        ),
        pytest.param(
            (Ok(0), Err(1), Ok(2)), Err(1), nullcontext(), id="returns first Err in the seq"
        ),
        pytest.param(
            (Ok(0), 1, Ok(2)),
            Ok(ParStream.from_iterable((0, 1, 2))),
            pytest.raises(TypeError),
            id="raises error if not all elements are Result",
        ),
        pytest.param(
            [],
            Ok(ParStream.from_iterable(())),
            nullcontext(),
            id="empty sequence of either Rights or Ok returns Ok[tuple[T]]",
        ),
    ],
)
def test_sequence(kwargs, seq, expected_result, expected_context):
    with expected_context:
        assert ParStream.from_iterable(seq).sequence(**kwargs) == expected_result


@given(
    st.one_of(
        st.tuples(st.lists(st.integers(), min_size=1), st.just(True)),
        st.tuples(st.lists(st.integers(), max_size=0), st.just(False)),
        st.tuples(st.dictionaries(st.characters(), st.integers(), min_size=1), st.just(True)),
        st.tuples(st.dictionaries(st.characters(), st.integers(), max_size=0), st.just(False)),
    )
)
def test_stream_bool(args):
    seq, expected_result = args
    assert bool(ParStream.from_iterable(seq)) == expected_result


@pytest.mark.parametrize(
    ("elements", "ops", "expected_result", "expected_context"),
    [
        pytest.param(
            range(4),
            ((_MAP, add_one), (_FILTER, divisible_by_3), (_TAP, add_one)),
            [3],
            nullcontext(),
            id="valid operations don't raise any errors",
        ),
        pytest.param(
            range(4),
            (("INVALID", add_one),),
            None,
            pytest.raises(RuntimeError),
            id="raises if given invalid operation",
        ),
    ],
)
def test_apply_fns(elements, ops, expected_result, expected_context):
    with expected_context:
        assert list(ParStream(tuple(elements), ops).collect()) == expected_result
