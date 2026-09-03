"""BaseStream

repo-map-desc: the base class for Stream
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable
from copy import deepcopy
from functools import partial, reduce
from typing import ParamSpec, Self, TypeVar

import attrs

from danom import Either, Result

T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E")
P = ParamSpec("P")
S = TypeVar("S", bound="_BaseStream")

MapFn = Callable[P, U]
FilterFn = Callable[P, bool]
TapFn = Callable[P, None]
StreamFn = MapFn | FilterFn | TapFn


_MAP = 0
_FILTER = 1
_TAP = 2


PlannedOps = tuple[str, StreamFn]


@attrs.define(frozen=True)
class _BaseStream[T](ABC):
    seq: tuple = attrs.field(validator=attrs.validators.instance_of(tuple))
    ops: tuple = attrs.field(default=(), validator=attrs.validators.instance_of(tuple), repr=False)

    @classmethod
    @abstractmethod
    def from_iterable(cls, it: Iterable) -> Self: ...

    @abstractmethod
    def map[**P](self, fn: Callable, *args: P.args, **kwargs: P.kwargs) -> Self: ...

    @abstractmethod
    def filter[**P](self, fn: Callable, *args: P.args, **kwargs: P.kwargs) -> Self: ...

    @abstractmethod
    def tap[**P](self, fn: Callable, *args: P.args, **kwargs: P.kwargs) -> Self: ...

    @abstractmethod
    def partition[U](
        self, fn: Callable, *, workers: int = 1, use_threads: bool = False
    ) -> tuple[Self, Self]: ...

    @abstractmethod
    def fold(
        self, initial: T, fn: Callable[[T, U], T], *, workers: int = 1, use_threads: bool = False
    ) -> T: ...

    @abstractmethod
    def sequence(
        self, *, workers: int = 1, use_threads: bool = False
    ) -> Result[Self, E] | Either[Self, E]: ...

    @abstractmethod
    def collect(self, *, workers: int = 4, use_threads: bool = False) -> tuple[U, ...]: ...

    def __bool__(self) -> bool:
        return bool(self.seq)


@attrs.define(frozen=True)
class _BaseSyncStream[T](_BaseStream):
    @classmethod
    def from_iterable(cls, it: Iterable) -> Self:
        """This is the recommended way of creating a `Stream` object.

        .. doctest::

            >>> from danom import Stream

            >>> Stream.from_iterable([0, 1, 2, 3]).collect() == (0, 1, 2, 3)
            True
        """
        if not isinstance(it, Iterable):
            it = [it]
        return cls(seq=tuple(it))

    def map[**P](self, fn: MapFn, *args: P.args, **kwargs: P.kwargs) -> Self:
        """Map a function to the elements in the ``Stream``. Will return a new ``Stream`` with the modified sequence.

        .. code-block:: python

            from danom import Stream

            Stream.from_iterable([0, 1, 2, 3]).map(add_one).collect() == (1, 2, 3, 4)

        This can also be mixed with ``safe`` functions:

        .. code-block:: python

            from danom import Stream

            Stream.from_iterable([0, 1, 2, 3]).map(add_one).collect() == (Ok(1), Ok(2), Ok(3), Ok(4))

            @safe
            def two_div_value(x: float) -> float:
                return 2 / x

            Stream.from_iterable([0, 1, 2, 4]).map(two_div_value).collect() == (Err(error=ZeroDivisionError('division by zero')), Ok(2.0), Ok(1.0), Ok(0.5))


        Keyword arguments can be passed into the functions:

        .. code-block:: python

            from danom import Stream

            Stream.from_iterable(range(5)).map(mul, b=2).map(add, b=1).collect() == (1, 3, 5, 7, 9)

        """
        plan = (*self.ops, (_MAP, partial(fn, *args, **kwargs)))
        return type(self)(seq=self.seq, ops=plan)

    def filter[**P](self, fn: FilterFn, *args: P.args, **kwargs: P.kwargs) -> Self:
        """Filter the stream based on a predicate. Will return a new ``Stream`` with the modified sequence.

        .. doctest::

            >>> from danom import Stream

            >>> Stream.from_iterable([0, 1, 2, 3]).filter(lambda x: x % 2 == 0).collect() == (0, 2)
            True

        Keyword arguments can be passed into the functions:

        .. code-block:: python

            from danom import Stream

            Stream.from_iterable(range(20)).filter(divisible_by, x=3).filter(divisible_by, x=5).collect() == (0, 15)

        """
        plan = (*self.ops, (_FILTER, partial(fn, *args, **kwargs)))
        return type(self)(seq=self.seq, ops=plan)

    def tap[**P](self, fn: TapFn, *args: P.args, **kwargs: P.kwargs) -> Self:
        """Tap the values to another process that returns None. Will return a new ``Stream`` with the modified sequence.

        The value passed to the tap function will be deep-copied to avoid any modification to the ``Stream`` item for downstream consumers.

        .. code-block:: python

            from danom import Stream

            Stream.from_iterable([0, 1, 2, 3]).tap(log_value).collect() == (0, 1, 2, 3)


        Simple functions can be passed in sequence for multiple ``tap`` operations

        .. code-block:: python

            from danom import Stream

            Stream.from_iterable([0, 1, 2, 3]).tap(log_value).tap(print_value).collect() == (0, 1, 2, 3)


        ``tap`` is useful for logging and similar actions without effecting the individual items, in this example eligible and dormant users are logged using ``tap``:

        .. code-block:: python

            from danom import Stream

            active_users, inactive_users = (
                Stream.from_iterable(users).map(parse_user_objects).partition(inactive_users)
            )

            active_users.filter(eligible_for_promotion).tap(log_eligible_users).map(construct_promo_email).map(send_with_confirmation).collect()

            inactive_users.tap(log_inactive_users).map(create_dormant_user_entry).map(add_to_dormant_table).collect()

        """
        plan = (*self.ops, (_TAP, partial(fn, *args, **kwargs)))
        return type(self)(seq=self.seq, ops=plan)

    def partition(
        self, fn: FilterFn, *, workers: int = 1, use_threads: bool = False
    ) -> tuple[Self, Self]:
        """Similar to ``filter`` except splits the ``True`` and ``False`` values. Will return a two new ``Stream`` with the partitioned sequences.

        Each partition is independently replayable.

        .. doctest::

            from danom import Stream

            >>> part1, part2 = Stream.from_iterable([0, 1, 2, 3]).partition(lambda x: x % 2 == 0)
            >>> part1.collect() == (0, 2)
            True
            >>> part2.collect() == (1, 3)
            True

        As ``partition`` triggers an action, the parameters will be forwarded to the ``collect`` call if the ``workers`` are greater than 1.

        .. code-block:: python

            from danom import Stream

            Stream.from_iterable(range(10)).map(add_one).map(add_one).partition(divisible_by_3, workers=4)
            part1.map(add_one).par_collect() == (4, 7, 10)
            part2.collect() == (2, 4, 5, 7, 8, 10, 11)

        """
        # have to materialise to be able to replay each side independently
        seq_tuple = self.collect(workers=workers, use_threads=use_threads)

        pos, neg = [], []

        for x in seq_tuple:
            if not fn(x):
                neg.append(x)
                continue
            pos.append(x)
        return (type(self).from_iterable(pos), type(self).from_iterable(neg))

    def sequence(  # ty: ignore[invalid-method-override]
        self, *, workers: int = 1, use_threads: bool = False
    ) -> Result[Self, E] | Either[Self, E]:
        """Convert a ``Stream`` of ``Result`` or ``Either`` monads to a monad of Stream

        .. doctest::

            >>> from danom import Ok, Stream

            >>> Stream.from_iterable((Ok(0), Ok(1), Ok(2))).sequence() == Ok(Stream.from_iterable((0, 1, 2)))
            True

            >>> Stream.from_iterable((Right(0), Right(1), Right(2))).sequence() == Right(Stream.from_iterable((0, 1, 2)))
            True

            >>> Stream.from_iterable((Ok(0), Err(1), Ok(2))).sequence() == Err(1)
            True

            >>> Stream.from_iterable((Right(0), Left(1), Right(2))).sequence() == Left(1)
            True

        If the ``Stream`` is of mixed monads, the final wrapped result will be ok the last seen monad type

        .. doctest::

            >>> from danom import Ok, Stream

            >>> Stream.from_iterable((Right(0), Right(1), Ok(2))).sequence() == Ok(Stream.from_iterable((0, 1, 2)))
            True

        """
        if not self:
            return Result.unit(self)

        seq_tuple = self.collect(workers=workers, use_threads=use_threads)

        if not all(isinstance(res, (Result, Either)) for res in seq_tuple):
            raise TypeError("All elements in the `Stream` must be of `Result` or `Either` type")

        results = []

        for res in seq_tuple:
            if not res.is_ok():
                return res
            results.append(res.unwrap())

        return type(res)(type(self).from_iterable(results))

    def fold(
        self, initial: T, fn: Callable[[T, U], T], *, workers: int = 1, use_threads: bool = False
    ) -> T:
        """Fold the results into a single value. ``fold`` triggers an action so will incur a ``collect``.

        .. doctest::

            >>> from danom import Stream

            >>> Stream.from_iterable([1, 2, 3, 4]).fold(0, lambda a, b: a + b) == 10
            True
            >>> Stream.from_iterable([[1], [2], [3], [4]]).fold([0], lambda a, b: a + b) == [0, 1, 2, 3, 4]
            True
            >>> Stream.from_iterable([1, 2, 3, 4]).fold(1, lambda a, b: a * b) == 24
            True


        As ``fold`` triggers an action, the parameters will be forwarded to the ``par_collect`` call if the ``workers`` are greater than 1.
        This will only effect the ``collect`` that is used to create the iterable to reduce, not the ``fold`` operation itself.

        .. code-block:: python

            from danom import Stream

            Stream.from_iterable([1, 2, 3, 4]).map(some_expensive_fn).fold(0, add, workers=4, use_threads=False)

        """
        return reduce(fn, self.collect(workers=workers, use_threads=use_threads), initial)


@attrs.define(frozen=True, hash=True, eq=True)
class _Tap:
    fn: Callable

    def __call__(self, value: T) -> T:
        self.fn(deepcopy(value))
        return value
