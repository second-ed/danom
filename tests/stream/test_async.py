from contextlib import nullcontext
from pathlib import Path

import pytest

from danom import AsyncStream
from danom._either import Right
from danom._result import Err, Ok
from tests.conftest import REPO_ROOT, AsyncValueLogger, async_is_file, async_read_text
from tests.stream._common import async_basic_partition, async_basic_pipeline


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("stream_cls", "kwargs"),
    [
        pytest.param(AsyncStream, {}, id="simple `collect`"),
        pytest.param(AsyncStream, {"workers": 4}, id="`collect` with workers passed in"),
        pytest.param(AsyncStream, {"workers": -1}, id="`collect` with n-1 workers"),
        pytest.param(
            AsyncStream, {"workers": 0}, id="`collect` with 0 workers falls back to 1 worker"
        ),
        pytest.param(AsyncStream, {"use_threads": True}, id="`collect` with threads True"),
    ],
)
@pytest.mark.parametrize(
    ("fn", "it", "expected_result"),
    [
        pytest.param(async_basic_partition, range(10), ((6, 12), (1, 3, 5, 7, 9))),
        pytest.param(async_basic_partition, 0, ((), (1,))),
        pytest.param(async_basic_pipeline, range(30), (15, 30), id="works with iterator"),
        pytest.param(async_basic_pipeline, 28, (30,), id="works with single value"),
    ],
)
async def test_async_stream_pipeline(stream_cls, kwargs, fn, it, expected_result) -> None:
    assert await fn(stream_cls, it, kwargs) == expected_result


@pytest.mark.asyncio
async def test_async_collect() -> None:
    assert await AsyncStream.from_iterable(
        sorted(Path(f"{REPO_ROOT}/tests/mock_data").glob("*"))
    ).filter(async_is_file).map(async_read_text).collect() == ("", "x = 1\n", "y = 2\n", "z = 3\n")


@pytest.mark.asyncio
async def test_async_collect_no_fns() -> None:
    assert await AsyncStream.from_iterable(
        sorted(Path(f"{REPO_ROOT}/tests/mock_data").glob("*"))
    ).collect() == (
        Path(f"{REPO_ROOT}/tests/mock_data/__init__.py"),
        Path(f"{REPO_ROOT}/tests/mock_data/dir_should_skip"),
        Path(f"{REPO_ROOT}/tests/mock_data/file_a.py"),
        Path(f"{REPO_ROOT}/tests/mock_data/file_b.py"),
        Path(f"{REPO_ROOT}/tests/mock_data/file_c.py"),
    )


@pytest.mark.asyncio
async def test_async_tap() -> None:
    val_logger = AsyncValueLogger()
    val_logger_2 = AsyncValueLogger()

    assert await AsyncStream.from_iterable(range(4)).tap(val_logger).tap(
        val_logger_2
    ).collect() == (0, 1, 2, 3)
    assert sorted(val_logger.values) == [0, 1, 2, 3]
    assert sorted(val_logger_2.values) == [0, 1, 2, 3]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("seq", "expected_result", "expected_context"),
    [
        pytest.param(
            (Ok(0), Ok(1), Ok(2)),
            Ok(AsyncStream.from_iterable((0, 1, 2))),
            nullcontext(),
            id="sequence of Oks returns Ok[tuple[T]]",
        ),
        pytest.param(
            (Right(0), Right(1), Right(2)),
            Right(AsyncStream.from_iterable((0, 1, 2))),
            nullcontext(),
            id="sequence of Rights returns Right[tuple[T]]",
        ),
        pytest.param(
            (Ok(0), Err(1), Ok(2)), Err(1), nullcontext(), id="returns first Err in the seq"
        ),
        pytest.param(
            (Ok(0), 1, Ok(2)),
            Ok(AsyncStream.from_iterable((0, 1, 2))),
            pytest.raises(TypeError),
            id="raises error if not all elements are Result",
        ),
        pytest.param(
            [],
            Ok(AsyncStream.from_iterable(())),
            nullcontext(),
            id="empty sequence of either Rights or Ok returns Ok[tuple[T]]",
        ),
    ],
)
async def test_sequence(seq, expected_result, expected_context) -> None:
    with expected_context:
        assert await AsyncStream.from_iterable(seq).sequence() == expected_result
