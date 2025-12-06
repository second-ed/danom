import pytest

from src.danom import ParStream, Stream, compose


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


def add_one(x: int) -> int:
    return x + 1


def divisible_by_3(x: int) -> bool:
    return x % 3 == 0


def divisible_by_5(x: int) -> bool:
    return x % 5 == 0


@pytest.mark.parametrize(
    ("it", "n_workers", "expected_result"),
    [
        pytest.param(range(15), 4, (15,)),
        pytest.param(13, -1, (15,)),
    ],
)
def test_par_stream(it, n_workers, expected_result):
    assert (
        ParStream.from_iterable(it)
        .map(add_one, add_one)
        .filter(divisible_by_3, divisible_by_5)
        .collect(workers=n_workers)
        == expected_result
    )


def test_stream_to_par_stream():
    part1, part2 = (
        Stream.from_iterable(range(10))
        .map(add_one)
        .to_par_stream()
        .map(add_one)
        .to_stream()
        .partition(divisible_by_3)
    )
    assert part1.to_par_stream().map(add_one).collect() == (4, 7, 10)
    assert part2.collect() == (2, 4, 5, 7, 8, 10, 11)


def test_par_stream_partition():
    with pytest.raises(NotImplementedError):
        ParStream.from_iterable(range(10)).partition(divisible_by_3)


@pytest.mark.parametrize(
    ("inp_args", "fns", "expected_result"),
    [
        pytest.param(0, (add_one, add_one), 2),
        pytest.param(0, (add_one, divisible_by_3), False),
    ],
)
def test_compose(inp_args, fns, expected_result):
    assert compose(*fns)(inp_args) == expected_result
