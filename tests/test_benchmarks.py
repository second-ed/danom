from __future__ import annotations

from danom import Err, Ok, Result, Stream, all_of, any_of, compose, identity, invert, new_type

# ---------------------------------------------------------------------------
# Helper functions used by benchmarks
# ---------------------------------------------------------------------------


def add_one(x: float) -> float:
    return x + 1


def double(x: float) -> float:
    return x * 2


def is_even(x: float) -> bool:
    return x % 2 == 0


def is_positive(x: float) -> bool:
    return x > 0


def lt_100(x: float) -> bool:
    return x < 100


def has_len(value: str) -> bool:
    return len(value) > 0


# ---------------------------------------------------------------------------
# Type definitions used by benchmarks
# ---------------------------------------------------------------------------

positive_float_type = new_type("PositiveFloat", float, validators=[is_positive])
str_type = new_type("StrType", str, validators=[has_len], converters=[str])


# ---------------------------------------------------------------------------
# Stream benchmarks
# ---------------------------------------------------------------------------


class TestStreamBenchmarks:
    def test_stream_map_small(self, benchmark) -> None:
        @benchmark
        def _() -> None:
            Stream.from_iterable(range(100)).map(add_one).collect()

    def test_stream_map_medium(self, benchmark) -> None:
        @benchmark
        def _() -> None:
            Stream.from_iterable(range(10_000)).map(add_one).collect()

    def test_stream_filter_small(self, benchmark) -> None:
        @benchmark
        def _() -> None:
            Stream.from_iterable(range(100)).filter(is_even).collect()

    def test_stream_filter_medium(self, benchmark) -> None:
        @benchmark
        def _() -> None:
            Stream.from_iterable(range(10_000)).filter(is_even).collect()

    def test_stream_map_filter_chain(self, benchmark) -> None:
        @benchmark
        def _() -> None:
            (
                Stream.from_iterable(range(1_000))
                .map(add_one, double)
                .filter(is_even, lt_100)
                .collect()
            )

    def test_stream_fold(self, benchmark) -> None:
        @benchmark
        def _() -> None:
            Stream.from_iterable(range(1_000)).fold(0, lambda a, b: a + b)

    def test_stream_partition(self, benchmark) -> None:
        @benchmark
        def _() -> None:
            Stream.from_iterable(range(1_000)).partition(is_even)


# ---------------------------------------------------------------------------
# Result benchmarks
# ---------------------------------------------------------------------------


class TestResultBenchmarks:
    def test_ok_creation(self, benchmark) -> None:
        @benchmark
        def _() -> None:
            for i in range(1_000):
                Ok(i)

    def test_err_creation(self, benchmark) -> None:
        @benchmark
        def _() -> None:
            for i in range(1_000):
                Err(error=i)

    def test_ok_map_chain(self, benchmark) -> None:
        @benchmark
        def _() -> None:
            Ok(1).map(add_one).map(double).map(add_one)

    def test_ok_and_then_chain(self, benchmark) -> None:
        def safe_add_one(x: float) -> Result:
            return Ok(x + 1)

        @benchmark
        def _() -> None:
            Ok(1).and_then(safe_add_one).and_then(safe_add_one).and_then(safe_add_one)

    def test_err_map_short_circuit(self, benchmark) -> None:
        @benchmark
        def _() -> None:
            Err(error=TypeError()).map(add_one).map(double).map(add_one)

    def test_result_unwrap(self, benchmark) -> None:
        ok = Ok(42)

        @benchmark
        def _() -> None:
            ok.unwrap()

    def test_stream_of_results(self, benchmark) -> None:
        @benchmark
        def _() -> None:
            (
                Stream.from_iterable([Ok(i) for i in range(100)])
                .filter(Result.result_is_ok)
                .map(Result.result_unwrap)
                .collect()
            )


# ---------------------------------------------------------------------------
# Utility function benchmarks
# ---------------------------------------------------------------------------


class TestUtilsBenchmarks:
    def test_compose(self, benchmark) -> None:
        fn = compose(add_one, double, add_one)

        @benchmark
        def _() -> None:
            fn(5)

    def test_all_of(self, benchmark) -> None:
        fn = all_of(is_even, is_positive, lt_100)

        @benchmark
        def _() -> None:
            fn(42)

    def test_any_of(self, benchmark) -> None:
        fn = any_of(is_even, is_positive, lt_100)

        @benchmark
        def _() -> None:
            fn(42)

    def test_identity(self, benchmark) -> None:
        @benchmark
        def _() -> None:
            identity(42)

    def test_invert(self, benchmark) -> None:
        fn = invert(is_even)

        @benchmark
        def _() -> None:
            fn(3)


# ---------------------------------------------------------------------------
# NewType benchmarks
# ---------------------------------------------------------------------------


class TestNewTypeBenchmarks:
    def test_new_type_creation(self, benchmark) -> None:
        @benchmark
        def _() -> None:
            positive_float_type(42.0)

    def test_new_type_map(self, benchmark) -> None:
        val = positive_float_type(10.0)

        @benchmark
        def _() -> None:
            val.map(double)

    def test_new_type_with_converter(self, benchmark) -> None:
        @benchmark
        def _() -> None:
            str_type(12345)
