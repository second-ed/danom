from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from copy import deepcopy

import attrs

from ._result import Result


@attrs.define(frozen=True)
class Option[T](ABC):
    @abstractmethod
    def and_(self, opt_b: Option[T]) -> Option[T]: ...

    @abstractmethod
    def and_then[U](self, fn: Callable[[T], Option[U]]) -> Option[T]: ...

    @abstractmethod
    def as_list(self) -> list[T]: ...

    @abstractmethod
    def as_tuple(self) -> tuple[T]: ...

    def cloned(self) -> Option[T]:
        return deepcopy(self)

    @abstractmethod
    def expect(self, msg: str) -> T: ...

    @abstractmethod
    def filter_(self, predicate: Callable[[T], bool]) -> Option[T]: ...

    @abstractmethod
    def flatten(self) -> Option[T]: ...

    @abstractmethod
    def inspect(self, fn: Callable[[T], None]) -> Option[T]: ...

    @abstractmethod
    def is_none(self) -> bool: ...

    @abstractmethod
    def is_none_or(self, fn: Callable[[T], bool]) -> bool: ...

    @abstractmethod
    def is_some(self) -> bool: ...

    @abstractmethod
    def is_some_and(self, fn: Callable[[T], bool]) -> bool: ...

    @abstractmethod
    def map[U](self, fn: Callable[[T], U]) -> Option[U]: ...

    @abstractmethod
    def map_or[U](self, default: U, fn: Callable[[T], U]) -> U: ...

    @abstractmethod
    def map_or_else[U](self, default: Callable[..., U], fn: Callable[[T], U]) -> U: ...

    @abstractmethod
    def ok_or[E](self, err: E) -> Result[T, E]: ...

    @abstractmethod
    def ok_or_else[E](self, err: Callable[..., E]) -> Result[T, E]: ...

    @abstractmethod
    def or_(self, opt_b: Option[T]) -> Option[T]: ...

    @abstractmethod
    def or_else(self, opt_b: Callable[..., Option[T]]) -> Option[T]: ...

    @abstractmethod
    def replace(self, value: T) -> Option[T]: ...

    @abstractmethod
    def transpose[E](self) -> Result[Option[T], E]: ...

    @abstractmethod
    def unwrap(self) -> T: ...

    @abstractmethod
    def unwrap_or(self, default: T) -> T: ...

    @abstractmethod
    def unwrap_or_else(self, fn: Callable[..., T]) -> T: ...

    @abstractmethod
    def zip[U](self, other: Option[U]) -> Option[tuple[T, U]]: ...

    @abstractmethod
    def unzip[U](self) -> tuple[Option[T], Option[U]]: ...
