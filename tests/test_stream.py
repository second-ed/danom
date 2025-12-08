import pytest

from src.danom import Stream
from tests.conftest import add_one, divisible_by_3, divisible_by_5


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


def test_stream_with_multiple_fns():
    assert (
        Stream.from_iterable(range(10))
        .map(lambda x: x * 2, lambda x: x + 1)
        .filter(lambda x: x % 5 == 0, lambda x: x < 10)
        .collect()
    ) == (5,)


@pytest.mark.parametrize(
    ("it", "n_workers", "expected_result"),
    [
        pytest.param(range(15), 4, (15,)),
        pytest.param(13, -1, (15,)),
    ],
)
def test_par_collect(it, n_workers, expected_result):
    assert (
        Stream.from_iterable(it)
        .map(add_one, add_one)
        .filter(divisible_by_3, divisible_by_5)
        .par_collect(workers=n_workers)
        == expected_result
    )


def test_stream_to_par_stream():
    part1, part2 = (
        Stream.from_iterable(range(10)).map(add_one, add_one).partition(divisible_by_3, workers=4)
    )
    assert part1.map(add_one).collect() == (4, 7, 10)
    assert part2.collect() == (2, 4, 5, 7, 8, 10, 11)
