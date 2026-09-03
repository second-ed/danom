"""BaseStream

repo-map-desc: the base class for Stream
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable
from copy import deepcopy
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
    def map[**P](self, fn: Callable, *args: P.args, **kwargs: P.kwargs) -> object: ...

    @abstractmethod
    def filter[**P](self, fn: Callable, *args: P.args, **kwargs: P.kwargs) -> object: ...

    @abstractmethod
    def tap[**P](self, fn: Callable, *args: P.args, **kwargs: P.kwargs) -> object: ...

    @abstractmethod
    def partition[U](
        self, fn: Callable, *, workers: int = 1, use_threads: bool = False
    ) -> object: ...

    @abstractmethod
    def fold(
        self, initial: T, fn: Callable[[T, U], T], *, workers: int = 1, use_threads: bool = False
    ) -> T: ...

    @abstractmethod
    def sequence(
        self, *, workers: int = 1, use_threads: bool = False
    ) -> Result[S, E] | Either[S, E]: ...

    @abstractmethod
    def collect(self, *, workers: int = 4, use_threads: bool = False) -> object: ...

    def __bool__(self) -> bool:
        return bool(self.seq)


@attrs.define(frozen=True, hash=True, eq=True)
class _Tap:
    fn: Callable

    def __call__(self, value: T) -> T:
        self.fn(deepcopy(value))
        return value
