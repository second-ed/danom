"""BaseStream

repo-map-desc: the base class for Stream
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable, Iterable
from typing import ParamSpec, TypeVar

import attrs

from danom._either import Either
from danom._result import Result

T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E")
P = ParamSpec("P")
S = TypeVar("S", bound="_BaseStream")

MapFn = Callable[P, U]
FilterFn = Callable[P, bool]
TapFn = Callable[P, None]

AsyncMapFn = Callable[P, Awaitable[U]]
AsyncFilterFn = Callable[P, Awaitable[bool]]
AsyncTapFn = Callable[P, Awaitable[None]]

StreamFn = MapFn | FilterFn | TapFn
AsyncStreamFn = AsyncMapFn | AsyncFilterFn | AsyncTapFn


@attrs.define(frozen=True)
class _BaseStream[T](ABC):
    seq: tuple = attrs.field(validator=attrs.validators.instance_of(tuple))
    ops: tuple = attrs.field(default=(), validator=attrs.validators.instance_of(tuple), repr=False)

    @classmethod
    @abstractmethod
    def from_iterable(cls, it: Iterable) -> _BaseStream[T]: ...

    @abstractmethod
    def map[**P](self, fn: Callable, *args: P.args, **kwargs: P.kwargs) -> _BaseStream[T]: ...

    @abstractmethod
    def filter[**P](self, fn: Callable, *args: P.args, **kwargs: P.kwargs) -> _BaseStream[T]: ...

    @abstractmethod
    def tap[**P](self, fn: Callable, *args: P.args, **kwargs: P.kwargs) -> _BaseStream[T]: ...

    @abstractmethod
    def partition[U](
        self, fn: Callable, *, workers: int = 1, use_threads: bool = False
    ) -> tuple[_BaseStream[T], _BaseStream[U]]: ...

    @abstractmethod
    def fold(
        self, initial: T, fn: Callable[[T, U], T], *, workers: int = 1, use_threads: bool = False
    ) -> T: ...

    @abstractmethod
    def sequence(
        self, *, workers: int = 1, use_threads: bool = False
    ) -> Result[S, E] | Either[S, E]: ...

    @abstractmethod
    def collect(
        self, *, workers: int = 4, use_threads: bool = False
    ) -> tuple[U, ...] | Awaitable[tuple[U, ...]]: ...

    def __bool__(self) -> bool:
        return bool(self.seq)
