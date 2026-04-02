from __future__ import annotations

from danom import Err, Ok, Result, Stream, all_of, any_of, compose, identity, invert, new_type
from tests.conftest import (
    add_one,
    double,
    has_len,
    is_even,
    is_even_num,
    is_gt_ten,
    is_lt_400,
    is_positive,
    lt_100,
    min_two,
    square,
    triple,
)


def test_stream_map(benchmark) -> None:
    @benchmark
    def _() -> None:
        Stream.from_iterable(range(10_000)).map(add_one).collect()


def test_stream_filter(benchmark) -> None:
    @benchmark
    def _() -> None:
        Stream.from_iterable(range(10_000)).filter(is_even).collect()


def test_stream_map_filter_chain(benchmark) -> None:
    @benchmark
    def _() -> None:
        (
            Stream.from_iterable(range(10_000))
            .map(triple)
            .filter(is_gt_ten)  # ty: ignore[invalid-argument-type]
            .map(min_two)
            .filter(is_even_num)
            .map(square)
            .filter(is_lt_400)  # ty: ignore[invalid-argument-type]
            .collect()
        )


def test_stream_fold(benchmark) -> None:
    @benchmark
    def _() -> None:
        Stream.from_iterable(range(1_000)).fold(0, lambda a, b: a + b)


def test_stream_partition(benchmark) -> None:
    @benchmark
    def _() -> None:
        Stream.from_iterable(range(1_000)).partition(is_even)


def test_ok_creation(benchmark) -> None:
    @benchmark
    def _() -> None:
        for i in range(1_000):
            Ok(i)


def test_err_creation(benchmark) -> None:
    @benchmark
    def _() -> None:
        for i in range(1_000):
            Err(error=i)


def test_ok_map_chain(benchmark) -> None:
    @benchmark
    def _() -> None:
        Ok(1).map(add_one).map(double).map(add_one)


def test_ok_and_then_chain(benchmark) -> None:
    def safe_add_one(x: float) -> Result:
        return Ok(x + 1)

    @benchmark
    def _() -> None:
        Ok(1).and_then(safe_add_one).and_then(safe_add_one).and_then(safe_add_one)


def test_err_map_short_circuit(benchmark) -> None:
    @benchmark
    def _() -> None:
        Err(error=TypeError()).map(add_one).map(double).map(add_one)


def test_result_unwrap(benchmark) -> None:
    ok = Ok(42)

    @benchmark
    def _() -> None:
        ok.unwrap()


def test_stream_of_results(benchmark) -> None:
    @benchmark
    def _() -> None:
        (
            Stream.from_iterable([Ok(i) for i in range(100)])
            .filter(Result.result_is_ok)
            .map(Result.result_unwrap)
            .collect()
        )


def test_stream_of_results_sequence(benchmark) -> None:
    @benchmark
    def _() -> None:
        (Stream.from_iterable([Ok(i) for i in range(100)]).sequence())


def test_compose(benchmark) -> None:
    fn = compose(add_one, double, add_one)

    @benchmark
    def _() -> None:
        fn(5)


def test_all_of(benchmark) -> None:
    fn = all_of(is_even, is_positive, lt_100)

    @benchmark
    def _() -> None:
        fn(42)


def test_any_of(benchmark) -> None:
    fn = any_of(is_even, is_positive, lt_100)

    @benchmark
    def _() -> None:
        fn(42)


def test_identity(benchmark) -> None:
    @benchmark
    def _() -> None:
        identity(42)


def test_invert(benchmark) -> None:
    fn = invert(is_even)

    @benchmark
    def _() -> None:
        fn(3)


PositiveFloat = new_type("PositiveFloat", float, validators=[is_positive])


def test_new_type_creation(benchmark) -> None:
    @benchmark
    def _() -> None:
        PositiveFloat(42.0)


def test_new_type_map(benchmark) -> None:
    val = PositiveFloat(10.0)

    @benchmark
    def _() -> None:
        val.map(double)


StrType = new_type("StrType", str, validators=[has_len], converters=[str])


def test_new_type_with_converter(benchmark) -> None:
    @benchmark
    def _() -> None:
        StrType(12345)
