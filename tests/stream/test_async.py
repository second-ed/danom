from pathlib import Path

import pytest

from danom import AsyncStream
from tests.conftest import REPO_ROOT, AsyncValueLogger, async_is_file, async_read_text


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
