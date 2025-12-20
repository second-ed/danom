from pathlib import Path

import pytest

from src.danom import Stream
from tests.conftest import (
    REPO_ROOT,
    add,
    add_one,
    async_is_file,
    async_read_text,
    divisible_by_3,
    divisible_by_5,
)


@pytest.mark.parametrize(
    ("it", "expected_part1", "expected_part2"),
    [
        pytest.param(range(10), (6, 12), (1, 3, 5, 7, 9)),
        pytest.param(0, (), (1,)),
    ],
)
def test_stream_pipeline(it, expected_part1, expected_part2):
    part1, part2 = Stream.from_iterable(it).map(lambda x: x + 1).partition(lambda x: x % 2 == 0)

    assert part1.map(lambda x: x + 2).filter(lambda x: x % 3 == 0).collect() == expected_part1
    assert part2.collect() == expected_part2


@pytest.mark.parametrize(
    ("it", "expected_result"),
    [
        pytest.param(range(30), (15, 30), id="works with iterator"),
        pytest.param(28, (30,), id="works with single value"),
    ],
)
@pytest.mark.parametrize(
    ("collect_fn", "kwargs"),
    [
        pytest.param("collect", {}, id="simple `collect`"),
        pytest.param("par_collect", {"workers": 4}, id="`par_collect` with workers passed in"),
        pytest.param("par_collect", {"workers": -1}, id="`par_collect` with n-1 workers"),
        pytest.param("par_collect", {"use_threads": True}, id="`par_collect` with threads True"),
    ],
)
def test_collect_methods(it, collect_fn, kwargs, expected_result):
    assert (
        getattr(
            Stream.from_iterable(it).map(add_one, add_one).filter(divisible_by_3, divisible_by_5),
            collect_fn,
        )(**kwargs)
        == expected_result
    )


def test_stream_to_par_stream():
    part1, part2 = (
        Stream.from_iterable(range(10)).map(add_one, add_one).partition(divisible_by_3, workers=4)
    )
    assert part1.map(add_one).collect() == (4, 7, 10)
    assert part2.collect() == (2, 4, 5, 7, 8, 10, 11)


@pytest.mark.parametrize(
    ("starting", "initial", "fn", "workers", "expected_result"),
    [
        pytest.param(range(10), 0, add, 1, 45),
        pytest.param(range(10), 0, add, 4, 45),
        pytest.param(range(10), 5, add, 4, 50),
    ],
)
def test_fold(starting, initial, fn, workers, expected_result):
    assert Stream.from_iterable(starting).fold(initial, fn, workers=workers) == expected_result


@pytest.mark.asyncio
async def test_async_collect():
    assert await Stream.from_iterable(
        sorted(Path(f"{REPO_ROOT}/tests/mock_data").glob("*"))
    ).filter(async_is_file).map(async_read_text).async_collect() == (
        "",
        "x = 1\n",
        "y = 2\n",
        "z = 3\n",
    )


@pytest.mark.asyncio
async def test_async_collect_no_fns():
    assert await Stream.from_iterable(
        sorted(Path(f"{REPO_ROOT}/tests/mock_data").glob("*"))
    ).async_collect() == (
        Path(f"{REPO_ROOT}/tests/mock_data/__init__.py"),
        Path(f"{REPO_ROOT}/tests/mock_data/dir_should_skip"),
        Path(f"{REPO_ROOT}/tests/mock_data/file_a.py"),
        Path(f"{REPO_ROOT}/tests/mock_data/file_b.py"),
        Path(f"{REPO_ROOT}/tests/mock_data/file_c.py"),
    )
