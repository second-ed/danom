from __future__ import annotations

import asyncio
import itertools
import os
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable, Generator, Iterable
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from copy import deepcopy
from enum import Enum, auto
from functools import reduce
from itertools import batched
from typing import ParamSpec, TypeVar, cast

import attrs

T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E")
P = ParamSpec("P")

MapFn = Callable[[T], U]
FilterFn = Callable[[T], bool]
TapFn = Callable[[T], None]

AsyncMapFn = Callable[[T], Awaitable[U]]
AsyncFilterFn = Callable[[T], Awaitable[bool]]
AsyncTapFn = Callable[[T], Awaitable[None]]

StreamFn = MapFn | FilterFn | TapFn
AsyncStreamFn = AsyncMapFn | AsyncFilterFn | AsyncTapFn


@attrs.define(frozen=True)
class _BaseStream(ABC):
    seq: tuple = attrs.field(validator=attrs.validators.instance_of(tuple))
    ops: tuple = attrs.field(default=(), validator=attrs.validators.instance_of(tuple), repr=False)

    @classmethod
    @abstractmethod
    def from_iterable(cls, it: Iterable) -> _BaseStream[T]: ...

    @abstractmethod
    def map(self, *fns: MapFn | AsyncMapFn) -> _BaseStream[T]: ...

    @abstractmethod
    def filter(self, *fns: FilterFn | AsyncFilterFn) -> _BaseStream[T]: ...

    @abstractmethod
    def tap(self, *fns: TapFn | AsyncTapFn) -> _BaseStream[T]: ...

    @abstractmethod
    def partition(self, fn: FilterFn) -> tuple[_BaseStream[T], _BaseStream[U]]: ...

    @abstractmethod
    def fold(
        self, initial: T, fn: Callable[[T, U], T], *, workers: int = 1, use_threads: bool = False
    ) -> T: ...

    @abstractmethod
    def collect(self) -> tuple[U, ...]: ...

    @abstractmethod
    def par_collect(self, workers: int = 4, *, use_threads: bool = False) -> tuple[U, ...]: ...

    @abstractmethod
    async def async_collect(self) -> Awaitable[tuple[U, ...]]: ...


@attrs.define(frozen=True)
class Stream(_BaseStream):
    """An immutable lazy iterator with functional operations.

    Why bother?
    -----------

    Readability counts, abstracting common operations helps reduce cognitive complexity when reading code.

    Comparison
    ----------

    Take this imperative pipeline of operations, it iterates once over the data, skipping the value if it fails one of the filter checks:

    .. code-block:: python

        res = []

        for x in range(1_000_000):
            item = triple(x)

            if not is_gt_ten(item):
                continue

            item = min_two(item)

            if not is_even_num(item):
                continue

            item = square(item)

            if not is_lt_400(item):
                continue

            res.append(item)
        [100, 256]

    number of tokens: `90`

    number of keywords: `11`

    keyword breakdown: `{'for': 1, 'in': 1, 'if': 3, 'not': 3, 'continue': 3}`

    After a bit of experience with python you might use list comprehensions, however this is arguably _less_ clear and iterates multiple times over the same data

    .. code-block:: python

        mul_three = [triple(x) for x in range(1_000_000)]
        gt_ten = [x for x in mul_three if is_gt_ten(x)]
        sub_two = [min_two(x) for x in gt_ten]
        is_even = [x for x in sub_two if is_even_num(x)]
        squared = [square(x) for x in is_even]
        lt_400 = [x for x in squared if is_lt_400(x)]
        [100, 256]

    number of tokens: `92`

    number of keywords: `15`

    keyword breakdown: `{'for': 6, 'in': 6, 'if': 3}`

    This still has a lot of tokens that the developer has to read to understand the code. The extra keywords add noise that cloud the actual transformations.

    Using a `Stream` results in this:

    .. code-block:: python

        from danom import Stream

        (
            Stream.from_iterable(range(1_000_000))
            .map(triple)
            .filter(is_gt_ten)
            .map(min_two)
            .filter(is_even_num)
            .map(square)
            .filter(is_lt_400)
            .collect()
        )
        (100, 256)

    number of tokens: `60`

    number of keywords: `0`

    keyword breakdown: `{}`

    The business logic is arguably much clearer like this.
    """

    @classmethod
    def from_iterable(cls, it: Iterable) -> Stream[T]:
        """This is the recommended way of creating a `Stream` object.

        .. code-block:: python

            from danom import Stream

            Stream.from_iterable([0, 1, 2, 3]).collect() == (0, 1, 2, 3)

        """
        if not isinstance(it, Iterable):
            it = [it]
        return cls(seq=tuple(it))

    def map(self, *fns: MapFn | AsyncMapFn) -> Stream[U]:
        """Map a function to the elements in the `Stream`. Will return a new `Stream` with the modified sequence.

        .. code-block:: python

            from danom import Stream

            Stream.from_iterable([0, 1, 2, 3]).map(add_one).collect() == (1, 2, 3, 4)

        This can also be mixed with `safe` functions:

        .. code-block:: python

            from danom import Stream

            Stream.from_iterable([0, 1, 2, 3]).map(add_one).collect() == (Ok(inner=1), Ok(inner=2), Ok(inner=3), Ok(inner=4))

            @safe
            def two_div_value(x: float) -> float:
                return 2 / x

            Stream.from_iterable([0, 1, 2, 4]).map(two_div_value).collect() == (Err(error=ZeroDivisionError('division by zero')), Ok(inner=2.0), Ok(inner=1.0), Ok(inner=0.5))


        Simple functions can be passed in sequence to compose more complex transformations

        .. code-block:: python

            from danom import Stream

            Stream.from_iterable(range(5)).map(mul_two, add_one).collect() == (1, 3, 5, 7, 9)

        """
        plan = (*self.ops, *tuple((_MAP, fn) for fn in fns))
        object.__setattr__(self, "ops", plan)
        return self

    def filter(self, *fns: FilterFn | AsyncFilterFn) -> Stream[T]:
        """Filter the stream based on a predicate. Will return a new `Stream` with the modified sequence.

        .. doctest::

            >>> from danom import Stream

            >>> Stream.from_iterable([0, 1, 2, 3]).filter(lambda x: x % 2 == 0).collect() == (0, 2)
            True

        Simple functions can be passed in sequence to compose more complex filters

        .. code-block:: python

            from danom import Stream

            Stream.from_iterable(range(20)).filter(divisible_by_3, divisible_by_5).collect() == (0, 15)

        """
        plan = (*self.ops, *tuple((_FILTER, fn) for fn in fns))
        object.__setattr__(self, "ops", plan)
        return self

    def tap(self, *fns: TapFn | AsyncTapFn) -> Stream[T]:
        """Tap the values to another process that returns None. Will return a new `Stream` with the modified sequence.

        The value passed to the tap function will be deep-copied to avoid any modification to the `Stream` item for downstream consumers.

        .. code-block:: python

            from danom import Stream

            Stream.from_iterable([0, 1, 2, 3]).tap(log_value).collect() == (0, 1, 2, 3)


        Simple functions can be passed in sequence for multiple `tap` operations

        .. code-block:: python

            from danom import Stream

            Stream.from_iterable([0, 1, 2, 3]).tap(log_value, print_value).collect() == (0, 1, 2, 3)


        `tap` is useful for logging and similar actions without effecting the individual items, in this example eligible and dormant users are logged using `tap`:

        .. code-block:: python

            from danom import Stream

            active_users, inactive_users = (
                Stream.from_iterable(users).map(parse_user_objects).partition(inactive_users)
            )

            active_users.filter(eligible_for_promotion).tap(log_eligible_users).map(
                construct_promo_email, send_with_confirmation
            ).collect()

            inactive_users.tap(log_inactive_users).map(
                create_dormant_user_entry, add_to_dormant_table
            ).collect()

        """
        plan = (*self.ops, *tuple((_TAP, fn) for fn in fns))
        object.__setattr__(self, "ops", plan)
        return self

    def partition(
        self, fn: FilterFn, *, workers: int = 1, use_threads: bool = False
    ) -> tuple[Stream[T], Stream[U]]:
        """Similar to `filter` except splits the True and False values. Will return a two new `Stream` with the partitioned sequences.

        Each partition is independently replayable.

        .. doctest::

            from danom import Stream

            >>> part1, part2 = Stream.from_iterable([0, 1, 2, 3]).partition(lambda x: x % 2 == 0)
            >>> part1.collect() == (0, 2)
            True
            >>> part2.collect() == (1, 3)
            True

        As `partition` triggers an action, the parameters will be forwarded to the `par_collect` call if the `workers` are greater than 1.

        .. code-block:: python

            from danom import Stream

            Stream.from_iterable(range(10)).map(add_one, add_one).partition(divisible_by_3, workers=4)
            part1.map(add_one).par_collect() == (4, 7, 10)
            part2.collect() == (2, 4, 5, 7, 8, 10, 11)

        """
        # have to materialise to be able to replay each side independently
        if workers > 1:
            seq_tuple = self.par_collect(workers=workers, use_threads=use_threads)
        else:
            seq_tuple = self.collect()
        return (
            Stream(seq=tuple(x for x in seq_tuple if fn(x))),
            Stream(seq=tuple(x for x in seq_tuple if not fn(x))),
        )

    def fold(
        self, initial: T, fn: Callable[[T, U], T], *, workers: int = 1, use_threads: bool = False
    ) -> T:
        """Fold the results into a single value. `fold` triggers an action so will incur a `collect`.

        .. code-block:: python

            from danom import Stream

            Stream.from_iterable([1, 2, 3, 4]).fold(0, lambda a, b: a + b) == 10
            Stream.from_iterable([[1], [2], [3], [4]]).fold([0], lambda a, b: a + b) == [0, 1, 2, 3, 4]
            Stream.from_iterable([1, 2, 3, 4]).fold(1, lambda a, b: a * b) == 24


        As `fold` triggers an action, the parameters will be forwarded to the `par_collect` call if the `workers` are greater than 1.
        This will only effect the `collect` that is used to create the iterable to reduce, not the `fold` operation itself.

        .. code-block:: python

            from danom import Stream

            Stream.from_iterable([1, 2, 3, 4]).map(some_expensive_fn).fold(0, add, workers=4, use_threads=False)

        """
        if workers > 1:
            return reduce(fn, self.par_collect(workers=workers, use_threads=use_threads), initial)
        return reduce(fn, self.collect(), initial)

    def collect(self) -> tuple[U, ...]:
        """Materialise the sequence from the `Stream`.

        .. code-block:: python

            from danom import Stream

            stream = Stream.from_iterable([0, 1, 2, 3]).map(add_one)
            stream.collect() == (1, 2, 3, 4)

        """
        return tuple(_apply_fns(self.seq, self.ops))

    def par_collect(self, workers: int = 4, *, use_threads: bool = False) -> tuple[U, ...]:
        """Materialise the sequence from the `Stream` in parallel.

        .. code-block:: python

            from danom import Stream

            stream = Stream.from_iterable([0, 1, 2, 3]).map(add_one)
            stream.par_collect() == (1, 2, 3, 4)

        Use the `workers` arg to select the number of workers to use. Use `-1` to use all available processors (except 1).
        Defaults to `4`.

        .. code-block:: python

            from danom import Stream

            stream = Stream.from_iterable([0, 1, 2, 3]).map(add_one)
            stream.par_collect(workers=-1) == (1, 2, 3, 4)

        For smaller I/O bound tasks use the `use_threads` flag as True.
        If False the processing will use `ProcessPoolExecutor` else it will use `ThreadPoolExecutor`.

        .. code-block:: python

            from danom import Stream

            stream = Stream.from_iterable([0, 1, 2, 3]).map(add_one)
            stream.par_collect(use_threads=True) == (1, 2, 3, 4)

        Note that all operations should be pickle-able, for that reason `Stream` does not support lambdas or closures.
        """
        if workers == -1:
            workers = (os.cpu_count() or 5) - 1

        executor_cls = ThreadPoolExecutor if use_threads else ProcessPoolExecutor

        batches = [
            (list(chunk), self.ops)
            for chunk in batched(self.seq, n=max(10, len(self.seq) // workers))
        ]

        with executor_cls(max_workers=workers) as ex:
            return cast(
                tuple[U, ...],
                tuple(itertools.chain.from_iterable(ex.map(_apply_fns_worker, batches))),
            )

    async def async_collect(self) -> Awaitable[tuple[U, ...]]:
        """Async version of collect. Note that all functions in the stream should be `Awaitable`.

        .. code-block:: python

            from danom import Stream

            Stream.from_iterable(file_paths).map(async_read_files).async_collect()

        If there are no operations in the `Stream` then this will act as a normal collect.

        .. code-block:: python

            from danom import Stream

            Stream.from_iterable(file_paths).async_collect()

        """
        if not self.ops:
            return cast(Awaitable[tuple[U, ...]], self.collect())

        res = await asyncio.gather(*(_async_apply_fns(x, self.ops) for x in self.seq))
        return cast(
            Awaitable[tuple[U, ...]], tuple(elem for elem in res if elem != _Nothing.NOTHING)
        )


_MAP = 0
_FILTER = 1
_TAP = 2


class _Nothing(Enum):
    NOTHING = auto()


PlannedOps = tuple[str, StreamFn]
AsyncPlannedOps = tuple[str, AsyncStreamFn]


def _apply_fns_worker[T](
    args: tuple[tuple[T], tuple[PlannedOps, ...]],
) -> tuple[T]:
    seq, ops = args
    return _par_apply_fns(seq, ops)


def _apply_fns[T](elements: tuple[T], ops: tuple[PlannedOps, ...]) -> Generator[T, None, None]:
    for elem in elements:
        valid = True
        res = elem
        for op, op_fn in ops:
            if op == _MAP:
                res = op_fn(res)
            elif op == _FILTER and not op_fn(res):
                valid = False
                break
            elif op == _TAP:
                op_fn(deepcopy(res))
        if valid:
            yield res


def _par_apply_fns[T](elements: tuple[T], ops: tuple[PlannedOps, ...]) -> tuple[T]:
    results = []
    for elem in elements:
        valid = True
        res = elem
        for op, op_fn in ops:
            if op == _MAP:
                res = op_fn(res)
            elif op == _FILTER and not op_fn(res):
                valid = False
                break
            elif op == _TAP:
                op_fn(deepcopy(res))
        if valid:
            results.append(res)
    return tuple(results)


async def _async_apply_fns[T](elem: T, ops: tuple[AsyncPlannedOps, ...]) -> T | _Nothing:
    res = elem
    for op, op_fn in ops:
        if op == _MAP:
            res = await op_fn(res)
        elif op == _FILTER and not await op_fn(res):
            return _Nothing.NOTHING
        elif op == _TAP:
            await op_fn(deepcopy(res))
    return res
