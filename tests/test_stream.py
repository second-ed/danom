import pytest

from src.danom import Stream


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
