from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from copy import deepcopy
from typing import cast

import attrs

from ._result import Err, Ok, Result


@attrs.define(frozen=True)
class Option[T](ABC):
    @abstractmethod
    def and_(self, opt_b: Option[T]) -> Option[T]: ...

    @abstractmethod
    def and_then[U](self, fn: Callable[[T], Option[U]]) -> Option[T]: ...

    @abstractmethod
    def as_list(self) -> list[T]: ...

    @abstractmethod
    def as_tuple(self) -> tuple[T, ...]: ...

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


@attrs.define(frozen=True)
class Some[T](Option):
    inner: T

    def and_(self, opt_b: Option[T]) -> Option[T]:
        return opt_b

    def and_then[U](self, fn: Callable[[T], Option[U]]) -> Option[U]:
        return fn(self.inner)

    def as_list(self) -> list[T]:
        return [self.inner]

    def as_tuple(self) -> tuple[T, ...]:
        return (self.inner,)

    def expect(self, msg: str) -> T:  # noqa: ARG002
        return self.inner

    def filter_(self, predicate: Callable[[T], bool]) -> Option[T]:
        return self if predicate(self.inner) else Null()

    def flatten(self) -> Option[T]:
        if isinstance(self.inner, Some):
            return self.inner
        return self

    def inspect(self, fn: Callable[[T], None]) -> Option[T]:
        fn(deepcopy(self.inner))
        return self

    def is_none(self) -> bool:
        return False

    def is_none_or(self, fn: Callable[[T], bool]) -> bool:
        return fn(self.inner)

    def is_some(self) -> bool:
        return True

    def is_some_and(self, fn: Callable[[T], bool]) -> bool:
        return fn(self.inner)

    def map[U](self, fn: Callable[[T], U]) -> Option[U]:
        return Some(fn(self.inner))

    def map_or[U](self, default: U, fn: Callable[[T], U]) -> U:  # noqa: ARG002
        return fn(self.inner)

    def map_or_else[U](self, default: Callable[[], U], fn: Callable[[T], U]) -> U:  # noqa: ARG002
        return fn(self.inner)

    def ok_or[E](self, err: E) -> Result[T, E]:  # noqa: ARG002
        return Ok(self.inner)

    def ok_or_else[E](self, err: Callable[[], E]) -> Result[T, E]:  # noqa: ARG002
        return Ok(self.inner)

    def or_(self, opt_b: Option[T]) -> Option[T]:  # noqa: ARG002
        return self

    def or_else(self, opt_b: Callable[[], Option[T]]) -> Option[T]:  # noqa: ARG002
        return self

    def replace(self, value: T) -> Option[T]:
        return Some(value)

    def transpose(self) -> Result[Option[T], Option[T]]:
        if isinstance(self.inner, Ok):
            return Ok(Some(self.inner.inner))
        if isinstance(self.inner, Err):
            return cast(Result[Option[T], Option[T]], Err[Option[T]](Some(self.inner.error)))
        raise TypeError("inner must be a `Result` type")

    def unwrap(self) -> T:
        return self.inner

    def unwrap_or(self, default: T) -> T:  # noqa: ARG002
        return self.inner

    def unwrap_or_else(self, fn: Callable[[], T]) -> T:  # noqa: ARG002
        return self.inner

    def zip[U](self, other: Option[U]) -> Option[tuple[T, U]]:
        if isinstance(other, Some):
            return Some[tuple[T, U]]((self.inner, other.inner))
        return Null[tuple[T, U]]()

    def unzip[U](self) -> tuple[Option[T], Option[U]]:
        if isinstance(self.inner, tuple) and len(self.inner) == 2:  # noqa: PLR2004
            return (Some(self.inner[0]), Some(self.inner[1]))
        return (Null(), Null())


@attrs.define(frozen=True)
class Null[T](Option):
    def and_(self, opt_b: Option[T]) -> Option[T]:  # noqa: ARG002
        return self

    def and_then[U](self, fn: Callable[[T], Option[U]]) -> Option[U]:  # noqa: ARG002
        return self

    def as_list(self) -> list[T]:
        return []

    def as_tuple(self) -> tuple[T, ...]:
        return ()

    def expect(self, msg: str) -> T:
        raise ValueError(msg)

    def filter_(self, predicate: Callable[[T], bool]) -> Option[T]:  # noqa: ARG002
        return self

    def flatten(self) -> Option[T]:
        return self

    def inspect(self, fn: Callable[[T], None]) -> Option[T]:  # noqa: ARG002
        return self

    def is_none(self) -> bool:
        return True

    def is_none_or(self, fn: Callable[[T], bool]) -> bool:  # noqa: ARG002
        return True

    def is_some(self) -> bool:
        return False

    def is_some_and(self, fn: Callable[[T], bool]) -> bool:  # noqa: ARG002
        return False

    def map[U](self, fn: Callable[[T], U]) -> Option[U]:  # noqa: ARG002
        return self

    def map_or[U](self, default: U, fn: Callable[[T], U]) -> U:  # noqa: ARG002
        return default

    def map_or_else[U](self, default: Callable[..., U], fn: Callable[[T], U]) -> U:  # noqa: ARG002
        return default()

    def ok_or[E](self, err: E) -> Result[T, E]:
        return cast(Result[T, E], Err[E](err))

    def ok_or_else[E](self, err: Callable[[], E]) -> Result[T, E]:
        return cast(Result[T, E], Err[E](err()))

    def or_(self, opt_b: Option[T]) -> Option[T]:
        return opt_b

    def or_else(self, opt_b: Callable[[], Option[T]]) -> Option[T]:
        return opt_b()

    def replace(self, value: T) -> Option[T]:  # noqa: ARG002
        return self

    def transpose[E](self) -> Result[Option[T], E]:
        return Ok(self)

    def unwrap(self) -> T:
        raise TypeError("Can't call `unwrap` on `Null`")

    def unwrap_or(self, default: T) -> T:
        return default

    def unwrap_or_else(self, fn: Callable[[], T]) -> T:
        return fn()

    def zip[U](self, other: Option[U]) -> Option[tuple[T, U]]:  # noqa: ARG002
        return self

    def unzip[U](self) -> tuple[Option[T], Option[U]]:
        return (Null(), Null())
