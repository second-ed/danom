from __future__ import annotations

import os
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from enum import Enum, auto, unique
from typing import Self

import attrs


@attrs.define(frozen=True)
class _BaseStream(ABC):
    seq: Iterable = attrs.field(validator=attrs.validators.instance_of(Iterable), repr=False)
    ops: tuple = attrs.field(default=(), validator=attrs.validators.instance_of(tuple), repr=False)

    @abstractmethod
    def map[T, U](self, *fns: Callable[[T], U]) -> Self: ...

    @abstractmethod
    def filter[T](self, *fns: Callable[[T], bool]) -> Self: ...

    @abstractmethod
    def partition[T](self, fn: Callable[[T], bool]) -> tuple[Self, Self]: ...

    @abstractmethod
    def collect(self) -> tuple: ...


@attrs.define(frozen=True)
class Stream(_BaseStream):
    """A lazy iterator with functional operations."""

    @classmethod
    def from_iterable(cls, it: Iterable) -> Self:
        """This is the recommended way of creating a `Stream` object.

        ```python
        >>> Stream.from_iterable([0, 1, 2, 3]).collect() == (0, 1, 2, 3)
        ```
        """
        if not isinstance(it, Iterable):
            it = [it]
        return cls(seq=iter(it))

    def map[T, U](self, *fns: Callable[[T], U]) -> Self:
        """Map a function to the elements in the `Stream`. Will return a new `Stream` with the modified sequence.

        ```python
        >>> Stream.from_iterable([0, 1, 2, 3]).map(add_one).collect() == (1, 2, 3, 4)
        ```

        This can also be mixed with `safe` functions:
        ```python
        >>> Stream.from_iterable([0, 1, 2, 3]).map(add_one).collect() == (Ok(inner=1), Ok(inner=2), Ok(inner=3), Ok(inner=4))

        >>> @safe
        ... def two_div_value(x: float) -> float:
        ...     return 2 / x

        >>> Stream.from_iterable([0, 1, 2, 4]).map(two_div_value).collect() == (Err(error=ZeroDivisionError('division by zero')), Ok(inner=2.0), Ok(inner=1.0), Ok(inner=0.5))
        ```

        Simple functions can be passed in sequence to compose more complex transformations
        ```python
        >>> Stream.from_iterable(range(5)).map(mul_two, add_one).collect() == (1, 3, 5, 7, 9)
        ```
        """
        plan = (*self.ops, *tuple((_OpType.MAP, fn) for fn in fns))
        return Stream(seq=self.seq, ops=plan)

    def filter[T](self, *fns: Callable[[T], bool]) -> Self:
        """Filter the stream based on a predicate. Will return a new `Stream` with the modified sequence.

        ```python
        >>> Stream.from_iterable([0, 1, 2, 3]).filter(lambda x: x % 2 == 0).collect() == (0, 2)
        ```

        Simple functions can be passed in sequence to compose more complex filters
        ```python
        >>> Stream.from_iterable(range(20)).filter(divisible_by_3, divisible_by_5).collect() == (0, 15)
        ```
        """
        plan = (*self.ops, *tuple((_OpType.FILTER, fn) for fn in fns))
        return Stream(seq=self.seq, ops=plan)

    def partition[T](
        self, fn: Callable[[T], bool], *, workers: int = 1, use_threads: bool = False
    ) -> tuple[Self, Self]:
        """Similar to `filter` except splits the True and False values. Will return a two new `Stream` with the partitioned sequences.

        Each partition is independently replayable.
        ```python
        >>> part1, part2 = Stream.from_iterable([0, 1, 2, 3]).partition(lambda x: x % 2 == 0)
        >>> part1.collect() == (0, 2)
        >>> part2.collect() == (1, 3)
        ```

        As `partition` triggers an action, the parameters will be forwarded to the `collect` call if the `workers` are greater than 1.
        ```python
        >>> Stream.from_iterable(range(10)).map(add_one, add_one).partition(divisible_by_3, workers=4)
        >>> part1.map(add_one).par_collect() == (4, 7, 10)
        >>> part2.collect() == (2, 4, 5, 7, 8, 10, 11)
        ```
        """
        # have to materialise to be able to replay each side independently
        if workers > 1:
            seq_tuple = self.par_collect(workers=workers, use_threads=use_threads)
        else:
            seq_tuple = self.collect()
        return (
            Stream(seq=(x for x in seq_tuple if fn(x))),
            Stream(seq=(x for x in seq_tuple if not fn(x))),
        )

    def collect(self) -> tuple:
        """Materialise the sequence from the `Stream`.

        ```python
        >>> stream = Stream.from_iterable([0, 1, 2, 3]).map(add_one)
        >>> stream.collect() == (1, 2, 3, 4)
        ```
        """
        return tuple(
            elem for x in self.seq if (elem := _apply_fns(x, self.ops)) != _Nothing.NOTHING
        )

    def par_collect(self, workers: int = 4, *, use_threads: bool = False) -> tuple:
        """Materialise the sequence from the `Stream` in parallel.

        ```python
        >>> stream = Stream.from_iterable([0, 1, 2, 3]).map(add_one)
        >>> stream.par_collect() == (1, 2, 3, 4)
        ```

        Use the `workers` arg to select the number of workers to use. Use `-1` to use all available processors (except 1).
        Defaults to `4`.
        ```python
        >>> stream = Stream.from_iterable([0, 1, 2, 3]).map(add_one)
        >>> stream.par_collect(workers=-1) == (1, 2, 3, 4)
        ```

        For smaller I/O bound tasks use the `use_threads` flag as True.
        If False the processing will use `ProcessPoolExecutor` else it will use `ThreadPoolExecutor`.
        ```python
        >>> stream = Stream.from_iterable([0, 1, 2, 3]).map(add_one)
        >>> stream.par_collect(use_threads=True) == (1, 2, 3, 4)
        ```
        """
        if workers == -1:
            workers = (os.cpu_count() - 1) or 4

        executor_cls = ThreadPoolExecutor if use_threads else ProcessPoolExecutor

        with executor_cls(max_workers=workers) as ex:
            res = tuple(ex.map(_apply_fns_worker, ((x, self.ops) for x in self.seq)))

        return tuple(elem for elem in res if elem != _Nothing.NOTHING)


@unique
class _OpType(Enum):
    MAP = auto()
    FILTER = auto()


class _Nothing(Enum):
    NOTHING = auto()


def _apply_fns_worker[T, U](args: tuple[T, tuple[tuple[_OpType, Callable], ...]]) -> U | None:
    elem, ops = args
    return _apply_fns(elem, ops)


def _apply_fns[T, U](elem: T, ops: tuple[tuple[_OpType, Callable], ...]) -> U | None:
    res = elem
    for op, op_fn in ops:
        if op == _OpType.MAP:
            res = op_fn(res)
        elif op == _OpType.FILTER and not op_fn(res):
            return _Nothing.NOTHING
    return res
