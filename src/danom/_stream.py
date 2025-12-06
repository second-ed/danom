from __future__ import annotations

import os
from abc import ABC, abstractmethod
from collections.abc import Callable, Generator, Iterable
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from enum import Enum, auto, unique
from typing import Self

import attrs


@attrs.define(frozen=True)
class _BaseStream(ABC):
    @abstractmethod
    def map[T, U](self, *fns: Callable[[T], U]) -> Self: ...

    @abstractmethod
    def filter[T](self, *fns: Callable[[T], bool]) -> Self: ...

    @abstractmethod
    def partition[T](self, fn: Callable[[T], bool]) -> tuple[Self, Self]: ...


@attrs.define(frozen=True)
class Stream(_BaseStream):
    """A lazy iterator with functional operations."""

    seq: Callable[[], Iterable] = attrs.field(
        validator=attrs.validators.instance_of(Callable), repr=False
    )

    @classmethod
    def from_iterable(cls, it: Iterable) -> Self:
        """This is the recommended way of creating a `Stream` object.

        ```python
        >>> Stream.from_iterable([0, 1, 2, 3]).collect() == (0, 1, 2, 3)
        ```
        """
        if not isinstance(it, Iterable):
            it = [it]
        return cls(lambda: iter(it))

    def to_par_stream(self) -> ParStream:
        """Convert `Stream` to `ParStream`. This will incur a `collect`.

        ```python
        >>> Stream.from_iterable([0, 1, 2, 3]).to_par_stream().map(some_expensive_cpu_task).collect() == (1, 2, 3, 4)

        ```
        """
        return ParStream.from_iterable(self.collect())

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

        def generator() -> Generator[U, None, None]:
            for elem in self.seq():
                yield compose(*fns)(elem)

        return Stream(generator)

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
        return Stream(lambda: (x for x in self.seq() if all(fn(x) for fn in fns)))

    def partition[T](self, fn: Callable[[T], bool]) -> tuple[Self, Self]:
        """Similar to `filter` except splits the True and False values. Will return a two new `Stream` with the partitioned sequences.

        Each partition is independently replayable.
        ```python
        >>> part1, part2 = Stream.from_iterable([0, 1, 2, 3]).partition(lambda x: x % 2 == 0)
        >>> part1.collect() == (0, 2)
        >>> part2.collect() == (1, 3)
        ```
        """
        # have to materialise to be able to replay each side independently
        seq_tuple = self.collect()
        return (
            Stream(lambda: (x for x in seq_tuple if fn(x))),
            Stream(lambda: (x for x in seq_tuple if not fn(x))),
        )

    def collect(self) -> tuple:
        """Materialise the sequence from the `Stream`.

        ```python
        >>> stream = Stream.from_iterable([0, 1, 2, 3]).map(add_one)
        >>> stream.collect() == (1, 2, 3, 4)
        ```
        """
        return tuple(self.seq())


@attrs.define(frozen=True)
class ParStream(_BaseStream):
    """A parallel iterator with functional operations."""

    seq: Iterable = attrs.field(validator=attrs.validators.instance_of(Iterable), repr=False)
    ops: tuple = attrs.field(default=(), validator=attrs.validators.instance_of(tuple), repr=False)

    @classmethod
    def from_iterable(cls, it: Iterable) -> Self:
        """This is the recommended way of creating a `ParStream` object.

        ```python
        >>> ParStream.from_iterable([0, 1, 2, 3]).collect() == (0, 1, 2, 3)
        ```
        """
        if not isinstance(it, Iterable):
            it = [it]
        return cls(it)

    def to_stream(self) -> Stream:
        """Convert `ParStream` to `Stream`. This will incur a `collect`.

        ```python
        >>> ParStream.from_iterable([0, 1, 2, 3]).to_stream().map(some_memory_hungry_task).collect() == (1, 2, 3, 4)
        ```
        """
        return Stream.from_iterable(self.collect())

    def map[T, U](self, *fns: Callable[[T], U]) -> Self:
        """Map functions to the elements in the `ParStream` in parallel. Will return a new `ParStream` with the modified sequence.

        ```python
        >>> ParStream.from_iterable([0, 1, 2, 3]).map(add_one, add_one).collect() == (2, 3, 4, 5)
        ```
        """
        plan = (*self.ops, *tuple((OpType.MAP, fn) for fn in fns))
        return ParStream(self.seq, ops=plan)

    def filter[T](self, *fns: Callable[[T], bool]) -> Self:
        """Filter the par stream based on a predicate. Will return a new `ParStream` with the modified sequence.

        ```python
        >>> ParStream.from_iterable([0, 1, 2, 3]).filter(lambda x: x % 2 == 0).collect() == (0, 2)
        ```

        Simple functions can be passed in sequence to compose more complex filters
        ```python
        >>> ParStream.from_iterable(range(20)).filter(divisible_by_3, divisible_by_5).collect() == (0, 15)
        ```
        """
        plan = (*self.ops, *tuple((OpType.FILTER, fn) for fn in fns))
        return ParStream(self.seq, ops=plan)

    def partition[T](self, _fn: Callable[[T], bool]) -> tuple[Self, Self]:
        """Partition isn't implemented for `ParStream`. Convert to `Stream` with the `to_stream()` method and then call partition."""
        raise NotImplementedError(
            "`partition` is not implemented for `ParStream`. Convert to `Stream` with the `to_stream()` method."
        )

    def collect(self, workers: int = 4, *, use_threads: bool = False) -> tuple:
        """Materialise the sequence from the `ParStream`.

        ```python
        >>> stream = ParStream.from_iterable([0, 1, 2, 3]).map(add_one)
        >>> stream.collect() == (1, 2, 3, 4)
        ```

        Use the `workers` arg to select the number of workers to use. Use `-1` to use all available processors (except 1).
        Defaults to `4`.
        ```python
        >>> stream = ParStream.from_iterable([0, 1, 2, 3]).map(add_one)
        >>> stream.collect(workers=-1) == (1, 2, 3, 4)
        ```

        For smaller I/O bound tasks use the `use_threads` flag as True
        ```python
        >>> stream = ParStream.from_iterable([0, 1, 2, 3]).map(add_one)
        >>> stream.collect(use_threads=True) == (1, 2, 3, 4)
        ```
        """
        if workers == -1:
            workers = (os.cpu_count() - 1) or 4

        executor_cls = ThreadPoolExecutor if use_threads else ProcessPoolExecutor

        with executor_cls(max_workers=workers) as ex:
            res = tuple(ex.map(_apply_fns_worker, ((x, self.ops) for x in self.seq)))

        return tuple(elem for elem in res if elem != _Nothing.NOTHING)


def compose[T, U](*fns: Callable[[T], U]) -> Callable[[T], U]:
    """Compose multiple functions into one.

    The functions will be called in sequence with the result of one being used as the input for the next.

    ```python
    >>> add_two = compose(add_one, add_one)
    >>> add_two(0) == 2
    ```

    ```python
    >>> add_two = compose(add_one, add_one, is_even)
    >>> add_two(0) == True
    ```
    """

    def wrapper(value: T) -> U:
        for fn in fns:
            value = fn(value)
        return value

    return wrapper


@unique
class OpType(Enum):
    MAP = auto()
    FILTER = auto()


class _Nothing(Enum):
    NOTHING = auto()


def _apply_fns_worker[T, U](args: tuple[T, tuple[tuple[OpType, Callable], ...]]) -> U | None:
    elem, ops = args
    return _apply_fns(elem, ops)


def _apply_fns[T, U](elem: T, ops: tuple[tuple[OpType, Callable], ...]) -> U | None:
    res = elem
    for op, op_fn in ops:
        if op == OpType.MAP:
            res = op_fn(res)
        elif op == OpType.FILTER and not op_fn(res):
            return _Nothing.NOTHING
    return res
