from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from copy import deepcopy
from typing import TYPE_CHECKING, cast

import attrs

if TYPE_CHECKING:
    from ._result_v2 import Result


@attrs.define(frozen=True)
class Option[T](ABC):
    """A monad to represent optional values.

    Version changes
    ----------
    ``0.17.0``: Added ``Option``, ``Some``, ``Null``
    """

    @abstractmethod
    def and_(self, opt_b: Option[T]) -> Option[T]:
        """Papertrail examples:

        A ``Some`` combined with ``Null`` through ``and_`` produces ``Null``.

        .. code-block:: python

            >>> Some(inner=2).and_(Null()) == Null()
            True
        A ``Null`` combined with an ``Some`` through ``and_`` remains ``Null``.

        .. code-block:: python

            >>> Null().and_(Some(inner="foo")) == Null()
            True
        When both options contain values, ``and_`` keeps the second ``Some``.

        .. code-block:: python

            >>> Some(inner=2).and_(Some(inner="foo")) == Some(inner="foo")
            True
        Combining two ``Null`` values with ``and_`` produces ``Null``.

        .. code-block:: python

            >>> Null().and_(Null()) == Null()
            True
        ::
        """
        ...

    @abstractmethod
    def and_then[U](self, fn: Callable[[T], Option[U]]) -> Option[T]:
        """Papertrail examples:

        A successful function passed to ``and_then`` returns its ``Some`` result.

        .. code-block:: python

            >>> Some(inner=2).and_then(must_be_less_than_10) == Some(inner=2)
            True
        When the function returns ``Null``, ``and_then`` passes that ``Null`` through.

        .. code-block:: python

            >>> Some(inner=20).and_then(must_be_less_than_10) == Null()
            True
        An existing ``Null`` skips the function passed to ``and_then``.

        .. code-block:: python

            >>> Null().and_then(must_be_less_than_10) == Null()
            True
        ::
        """
        ...

    @abstractmethod
    def as_list(self) -> list[T]:
        """Papertrail examples:

        A ``Some`` becomes a one-item list through ``as_list``.

        .. code-block:: python

            >>> Some(inner=2).as_list() == [2]
            True
        ``as_list`` represents ``Null`` as an empty list.

        .. code-block:: python

            >>> Null().as_list() == []
            True
        ::
        """
        ...

    @abstractmethod
    def as_tuple(self) -> tuple[T, ...]:
        """Papertrail examples:

        A ``Some`` becomes a one-item tuple through ``as_tuple``.

        .. code-block:: python

            >>> Some(inner=2).as_tuple() == (2,)
            True
        ``as_tuple`` represents ``Null`` as an empty tuple.

        .. code-block:: python

            >>> Null().as_tuple() == ()
            True
        ::
        """
        ...

    def cloned(self) -> Option[T]:
        """Papertrail examples:

        Cloning a ``Some`` creates a separate option with the same value.

        .. code-block:: python

            >>> Some(inner=2).cloned() == Some(inner=2)
            True
        Cloning ``Null`` creates a separate ``Null``.

        .. code-block:: python

            >>> Null().cloned() == Null()
            True
        ::
        """
        return deepcopy(self)

    @abstractmethod
    def expect(self, msg: str) -> T:
        """Papertrail examples:

        ``expect`` extracts the value from a ``Some``.

        .. code-block:: python

            >>> Some(inner=2).expect("must be positive") == 2
            True
        ::
        """
        ...

    @abstractmethod
    def filter_(self, predicate: Callable[[T], bool]) -> Option[T]:
        """Papertrail examples:

        A ``Some`` that fails the predicate becomes ``Null`` through ``filter_``.

        .. code-block:: python

            >>> Some(inner=3).filter_(is_even) == Null()
            True
        A ``Some`` that passes the predicate remains unchanged.

        .. code-block:: python

            >>> Some(inner=4).filter_(is_even) == Some(inner=4)
            True
        ``filter_`` leaves ``Null`` unchanged without calling the predicate.

        .. code-block:: python

            >>> Null().filter_(is_even) == Null()
            True
        ::
        """
        ...

    @abstractmethod
    def flatten(self) -> Option[T]:
        """Papertrail examples:

        Flattening three nested ``Some`` values removes only the outer option.

        .. code-block:: python

            >>> Some(inner=Some(inner=Some(inner=2))).flatten() == Some(inner=Some(inner=2))
            True
        Flattening a doubly wrapped value returns the inner ``Some``.

        .. code-block:: python

            >>> Some(inner=Some(inner=2)).flatten() == Some(inner=2)
            True
        Flattening a ``Some`` with a non-option value does nothing.

        .. code-block:: python

            >>> Some(inner=2).flatten() == Some(inner=2)
            True
        A ``Null`` passes through ``flatten`` unchanged.

        .. code-block:: python

            >>> Null().flatten() == Null()
            True
        ::
        """
        ...

    @abstractmethod
    def inspect(self, fn: Callable[[T], None]) -> Option[T]:
        """Papertrail examples:

        Inspecting a ``Some`` calls the function and returns the original option.

        .. code-block:: python

            >>> Some(inner=[1]).inspect(append_to_list) == Some(inner=[1])
            True
        Inspecting ``Null`` returns ``Null`` without calling the function.

        .. code-block:: python

            >>> Null().inspect(append_to_list) == Null()
            True
        ::
        """
        ...

    @abstractmethod
    def is_none(self) -> bool:
        """Papertrail examples:

        ``is_none`` reports ``False`` for a ``Some``.

        .. code-block:: python

            >>> Some(inner=2).is_none() == False
            True
        For ``Null``, ``is_none`` reports ``True``.

        .. code-block:: python

            >>> Null().is_none() == True
            True
        ::
        """
        ...

    @abstractmethod
    def is_none_or(self, fn: Callable[[T], bool]) -> bool:
        """Papertrail examples:

        When the predicate rejects a ``Some``, ``is_none_or`` reports ``False``.

        .. code-block:: python

            >>> Some(inner=1).is_none_or(is_even) == False
            True
        When the predicate accepts a ``Some``, ``is_none_or`` reports ``True``.

        .. code-block:: python

            >>> Some(inner=2).is_none_or(is_even) == True
            True
        ``Null`` makes ``is_none_or`` report ``True`` without calling the predicate.

        .. code-block:: python

            >>> Null().is_none_or(is_even) == True
            True
        ::
        """
        ...

    @abstractmethod
    def is_some(self) -> bool:
        """Papertrail examples:

        ``is_some`` reports ``True`` for a ``Some``.

        .. code-block:: python

            >>> Some(inner=2).is_some() == True
            True
        For ``Null``, ``is_some`` reports ``False``.

        .. code-block:: python

            >>> Null().is_some() == False
            True
        ::
        """
        ...

    @abstractmethod
    def is_some_and(self, fn: Callable[[T], bool]) -> bool:
        """Papertrail examples:

        When the predicate rejects a ``Some``, ``is_some_and`` reports ``False``.

        .. code-block:: python

            >>> Some(inner=1).is_some_and(is_even) == False
            True
        When the predicate accepts a ``Some``, ``is_some_and`` reports ``True``.

        .. code-block:: python

            >>> Some(inner=2).is_some_and(is_even) == True
            True
        A ``Null`` makes ``is_some_and`` report ``False`` without calling the predicate.

        .. code-block:: python

            >>> Null().is_some_and(is_even) == False
            True
        ::
        """
        ...

    @abstractmethod
    def map[U](self, fn: Callable[[T], U]) -> Option[U]:
        """Papertrail examples:

        Mapping a ``Some`` applies the function and wraps its result in a new ``Some``.

        .. code-block:: python

            >>> Some(inner=1).map(add_one) == Some(inner=2)
            True
        Mapping ``Null`` leaves it unchanged and skips the function.

        .. code-block:: python

            >>> Null().map(add_one) == Null()
            True
        ::
        """
        ...

    @abstractmethod
    def map_or[U](self, default: U, fn: Callable[[T], U]) -> U:
        """Papertrail examples:

        For a ``Some``, ``map_or`` uses the function result instead of the default.

        .. code-block:: python

            >>> Some(inner="foo").map_or(42, len) == 3
            True
        For ``Null``, ``map_or`` returns the supplied default.

        .. code-block:: python

            >>> Null().map_or(42, len) == 42
            True
        ::
        """
        ...

    @abstractmethod
    def map_or_else[U](self, default: Callable[..., U], fn: Callable[[T], U]) -> U:
        """Papertrail examples:

        A ``Some`` makes ``map_or_else`` use the mapping function.

        .. code-block:: python

            >>> Some(inner="foo").map_or_else(get_42, len) == 3
            True
        A ``Null`` makes ``map_or_else`` use the default function.

        .. code-block:: python

            >>> Null().map_or_else(get_42, len) == 42
            True
        ::
        """
        ...

    @abstractmethod
    def ok_or[E](self, err: E) -> Result[T, E]:
        """Papertrail examples:

        A ``Some`` converts to ``Ok`` through ``ok_or``.

        .. code-block:: python

            >>> Some(inner="foo").ok_or(0) == Ok(inner="foo")
            True
        A ``Null`` converts to ``Err`` through ``ok_or``.

        .. code-block:: python

            >>> Null().ok_or(0) == Err(error=0)
            True
        ::
        """
        ...

    @abstractmethod
    def ok_or_else[E](self, err: Callable[..., E]) -> Result[T, E]:
        """Papertrail examples:

        A ``Some`` converts to ``Ok`` without calling the error function.

        .. code-block:: python

            >>> Some(inner="foo").ok_or_else(get_42) == Ok(inner="foo")
            True
        A ``Null`` converts to ``Err`` using the error function result.

        .. code-block:: python

            >>> Null().ok_or_else(get_42) == Err(error=42)
            True
        ::
        """
        ...

    @abstractmethod
    def or_(self, opt_b: Option[T]) -> Option[T]:
        """Papertrail examples:

        A ``Some`` keeps its value when ``or_`` receives ``Null``.

        .. code-block:: python

            >>> Some(inner=2).or_(Null()) == Some(inner=2)
            True
        A ``Null`` gives way to a ``Some`` passed to ``or_``.

        .. code-block:: python

            >>> Null().or_(Some(inner=100)) == Some(inner=100)
            True
        When both options contain values, ``or_`` keeps the first ``Some``.

        .. code-block:: python

            >>> Some(inner=2).or_(Some(inner=100)) == Some(inner=2)
            True
        When both options are ``Null``, ``or_`` returns ``Null``.

        .. code-block:: python

            >>> Null().or_(Null()) == Null()
            True
        ::
        """
        ...

    @abstractmethod
    def or_else(self, opt_b: Callable[..., Option[T]]) -> Option[T]:
        """Papertrail examples:

        A ``Some`` passes through ``or_else`` without calling the function.

        .. code-block:: python

            >>> Some(inner="barbarians").or_else(get_some_vikings) == Some(inner="barbarians")
            True
        For ``Null``, ``or_else`` returns the ``Some`` produced by the function.

        .. code-block:: python

            >>> Null().or_else(get_some_vikings) == Some(inner="vikings")
            True
        If the fallback also produces ``Null``, ``or_else`` returns ``Null``.

        .. code-block:: python

            >>> Null().or_else(Null) == Null()
            True
        ::
        """
        ...

    @abstractmethod
    def replace(self, value: T) -> Option[T]:
        """Papertrail examples:

        Replacing a ``Some`` returns a new ``Some`` with the replacement value.

        .. code-block:: python

            >>> Some(inner=2).replace(5) == Some(inner=5)
            True
        Replacing ``Null`` leaves it as ``Null``.

        .. code-block:: python

            >>> Null().replace(3) == Null()
            True
        ::
        """
        ...

    @abstractmethod
    def transpose[E](self) -> Result[Option[T], E]:
        """Papertrail examples:

        Transposing ``Some(Ok(value))`` produces ``Ok(Some(value))``.

        .. code-block:: python

            >>> Some(inner=Ok(inner=2)).transpose() == Ok(inner=Some(inner=2))
            True
        Transposing ``Some(Err(error))`` produces ``Err(Some(error))``.

        .. code-block:: python

            >>> Some(inner=Err(error=2)).transpose() == Err(error=Some(inner=2))
            True
        Transposing ``Null`` produces ``Ok(Null())``.

        .. code-block:: python

            >>> Null().transpose() == Ok(inner=Null())
            True
        ::
        """
        ...

    @abstractmethod
    def unwrap(self) -> T:
        """Papertrail examples:

        ``unwrap`` extracts the value from a ``Some``.

        .. code-block:: python

            >>> Some(inner=2).unwrap() == 2
            True
        ::
        """
        ...

    @abstractmethod
    def unwrap_or(self, default: T) -> T:
        """Papertrail examples:

        With a ``Some``, ``unwrap_or`` returns the value and ignores the default.

        .. code-block:: python

            >>> Some(inner="car").unwrap_or("bike") == "car"
            True
        With ``Null``, ``unwrap_or`` returns the default.

        .. code-block:: python

            >>> Null().unwrap_or("bike") == "bike"
            True
        ::
        """
        ...

    @abstractmethod
    def unwrap_or_else(self, fn: Callable[..., T]) -> T:
        """Papertrail examples:

        A ``Some`` makes ``unwrap_or_else`` return its value without calling the function.

        .. code-block:: python

            >>> Some(inner=4).unwrap_or_else(get_42) == 4
            True
        A ``Null`` makes ``unwrap_or_else`` return the function result.

        .. code-block:: python

            >>> Null().unwrap_or_else(get_42) == 42
            True
        ::
        """
        ...

    @abstractmethod
    def zip[U](self, other: Option[U]) -> Option[tuple[T, U]]:
        """Papertrail examples:

        Zipping two ``Some`` values produces a ``Some`` containing both values.

        .. code-block:: python

            >>> Some(inner=1).zip(Some(inner="hi")) == Some(inner=(1, "hi"))
            True
        Zipping a ``Some`` with ``Null`` produces ``Null``.

        .. code-block:: python

            >>> Some(inner=1).zip(Null()) == Null()
            True
        Zipping ``Null`` with a ``Some`` produces ``Null``.

        .. code-block:: python

            >>> Null().zip(Some(inner=1)) == Null()
            True
        ::
        """
        ...

    @abstractmethod
    def unzip[U](self) -> tuple[Option[T], Option[U]]:
        """Papertrail examples:

        Unzipping a ``Some`` pair produces two ``Some`` values.

        .. code-block:: python

            >>> Some(inner=(2, 2)).unzip() == (Some(inner=2), Some(inner=2))
            True
        Unzipping a ``Some`` with a non-pair value produces two ``Null`` values.

        .. code-block:: python

            >>> Some(inner=4).unzip() == (Null(), Null())
            True
        Unzipping ``Null`` produces two ``Null`` values.

        .. code-block:: python

            >>> Null().unzip() == (Null(), Null())
            True
        ::
        """
        ...


@attrs.define(frozen=True)
class Some[T](Option):
    inner: T

    def and_(self, opt_b: Option[T]) -> Option[T]:
        """Papertrail examples:

        A ``Some`` combined with ``Null`` through ``and_`` produces ``Null``.

        .. code-block:: python

            >>> Some(inner=2).and_(Null()) == Null()
            True
        A ``Null`` combined with an ``Some`` through ``and_`` remains ``Null``.

        .. code-block:: python

            >>> Null().and_(Some(inner="foo")) == Null()
            True
        When both options contain values, ``and_`` keeps the second ``Some``.

        .. code-block:: python

            >>> Some(inner=2).and_(Some(inner="foo")) == Some(inner="foo")
            True
        Combining two ``Null`` values with ``and_`` produces ``Null``.

        .. code-block:: python

            >>> Null().and_(Null()) == Null()
            True
        ::
        """
        return opt_b

    def and_then[U](self, fn: Callable[[T], Option[U]]) -> Option[U]:
        """Papertrail examples:

        A successful function passed to ``and_then`` returns its ``Some`` result.

        .. code-block:: python

            >>> Some(inner=2).and_then(must_be_less_than_10) == Some(inner=2)
            True
        When the function returns ``Null``, ``and_then`` passes that ``Null`` through.

        .. code-block:: python

            >>> Some(inner=20).and_then(must_be_less_than_10) == Null()
            True
        An existing ``Null`` skips the function passed to ``and_then``.

        .. code-block:: python

            >>> Null().and_then(must_be_less_than_10) == Null()
            True
        ::
        """
        return fn(self.inner)

    def as_list(self) -> list[T]:
        """Papertrail examples:

        A ``Some`` becomes a one-item list through ``as_list``.

        .. code-block:: python

            >>> Some(inner=2).as_list() == [2]
            True
        ``as_list`` represents ``Null`` as an empty list.

        .. code-block:: python

            >>> Null().as_list() == []
            True
        ::
        """
        return [self.inner]

    def as_tuple(self) -> tuple[T, ...]:
        """Papertrail examples:

        A ``Some`` becomes a one-item tuple through ``as_tuple``.

        .. code-block:: python

            >>> Some(inner=2).as_tuple() == (2,)
            True
        ``as_tuple`` represents ``Null`` as an empty tuple.

        .. code-block:: python

            >>> Null().as_tuple() == ()
            True
        ::
        """
        return (self.inner,)

    def expect(self, msg: str) -> T:  # noqa: ARG002
        """Papertrail examples:

        ``expect`` extracts the value from a ``Some``.

        .. code-block:: python

            >>> Some(inner=2).expect("must be positive") == 2
            True
        ::
        """
        return self.inner

    def filter_(self, predicate: Callable[[T], bool]) -> Option[T]:
        """Papertrail examples:

        A ``Some`` that fails the predicate becomes ``Null`` through ``filter_``.

        .. code-block:: python

            >>> Some(inner=3).filter_(is_even) == Null()
            True
        A ``Some`` that passes the predicate remains unchanged.

        .. code-block:: python

            >>> Some(inner=4).filter_(is_even) == Some(inner=4)
            True
        ``filter_`` leaves ``Null`` unchanged without calling the predicate.

        .. code-block:: python

            >>> Null().filter_(is_even) == Null()
            True
        ::
        """
        return self if predicate(self.inner) else Null()

    def flatten(self) -> Option[T]:
        """Papertrail examples:

        Flattening three nested ``Some`` values removes only the outer option.

        .. code-block:: python

            >>> Some(inner=Some(inner=Some(inner=2))).flatten() == Some(inner=Some(inner=2))
            True
        Flattening a doubly wrapped value returns the inner ``Some``.

        .. code-block:: python

            >>> Some(inner=Some(inner=2)).flatten() == Some(inner=2)
            True
        Flattening a ``Some`` with a non-option value does nothing.

        .. code-block:: python

            >>> Some(inner=2).flatten() == Some(inner=2)
            True
        A ``Null`` passes through ``flatten`` unchanged.

        .. code-block:: python

            >>> Null().flatten() == Null()
            True
        ::
        """
        if isinstance(self.inner, Some):
            return self.inner
        return self

    def inspect(self, fn: Callable[[T], None]) -> Option[T]:
        """Papertrail examples:

        Inspecting a ``Some`` calls the function and returns the original option.

        .. code-block:: python

            >>> Some(inner=[1]).inspect(append_to_list) == Some(inner=[1])
            True
        Inspecting ``Null`` returns ``Null`` without calling the function.

        .. code-block:: python

            >>> Null().inspect(append_to_list) == Null()
            True
        ::
        """
        fn(deepcopy(self.inner))
        return self

    def is_none(self) -> bool:
        """Papertrail examples:

        ``is_none`` reports ``False`` for a ``Some``.

        .. code-block:: python

            >>> Some(inner=2).is_none() == False
            True
        For ``Null``, ``is_none`` reports ``True``.

        .. code-block:: python

            >>> Null().is_none() == True
            True
        ::
        """
        return False

    def is_none_or(self, fn: Callable[[T], bool]) -> bool:
        """Papertrail examples:

        When the predicate rejects a ``Some``, ``is_none_or`` reports ``False``.

        .. code-block:: python

            >>> Some(inner=1).is_none_or(is_even) == False
            True
        When the predicate accepts a ``Some``, ``is_none_or`` reports ``True``.

        .. code-block:: python

            >>> Some(inner=2).is_none_or(is_even) == True
            True
        ``Null`` makes ``is_none_or`` report ``True`` without calling the predicate.

        .. code-block:: python

            >>> Null().is_none_or(is_even) == True
            True
        ::
        """
        return fn(self.inner)

    def is_some(self) -> bool:
        """Papertrail examples:

        ``is_some`` reports ``True`` for a ``Some``.

        .. code-block:: python

            >>> Some(inner=2).is_some() == True
            True
        For ``Null``, ``is_some`` reports ``False``.

        .. code-block:: python

            >>> Null().is_some() == False
            True
        ::
        """
        return True

    def is_some_and(self, fn: Callable[[T], bool]) -> bool:
        """Papertrail examples:

        When the predicate rejects a ``Some``, ``is_some_and`` reports ``False``.

        .. code-block:: python

            >>> Some(inner=1).is_some_and(is_even) == False
            True
        When the predicate accepts a ``Some``, ``is_some_and`` reports ``True``.

        .. code-block:: python

            >>> Some(inner=2).is_some_and(is_even) == True
            True
        A ``Null`` makes ``is_some_and`` report ``False`` without calling the predicate.

        .. code-block:: python

            >>> Null().is_some_and(is_even) == False
            True
        ::
        """
        return fn(self.inner)

    def map[U](self, fn: Callable[[T], U]) -> Option[U]:
        """Papertrail examples:

        Mapping a ``Some`` applies the function and wraps its result in a new ``Some``.

        .. code-block:: python

            >>> Some(inner=1).map(add_one) == Some(inner=2)
            True
        Mapping ``Null`` leaves it unchanged and skips the function.

        .. code-block:: python

            >>> Null().map(add_one) == Null()
            True
        ::
        """
        return Some(fn(self.inner))

    def map_or[U](self, default: U, fn: Callable[[T], U]) -> U:  # noqa: ARG002
        """Papertrail examples:

        For a ``Some``, ``map_or`` uses the function result instead of the default.

        .. code-block:: python

            >>> Some(inner="foo").map_or(42, len) == 3
            True
        For ``Null``, ``map_or`` returns the supplied default.

        .. code-block:: python

            >>> Null().map_or(42, len) == 42
            True
        ::
        """
        return fn(self.inner)

    def map_or_else[U](self, default: Callable[[], U], fn: Callable[[T], U]) -> U:  # noqa: ARG002
        """Papertrail examples:

        A ``Some`` makes ``map_or_else`` use the mapping function.

        .. code-block:: python

            >>> Some(inner="foo").map_or_else(get_42, len) == 3
            True
        A ``Null`` makes ``map_or_else`` use the default function.

        .. code-block:: python

            >>> Null().map_or_else(get_42, len) == 42
            True
        ::
        """
        return fn(self.inner)

    def ok_or[E](self, err: E) -> Result[T, E]:  # noqa: ARG002
        """Papertrail examples:

        A ``Some`` converts to ``Ok`` through ``ok_or``.

        .. code-block:: python

            >>> Some(inner="foo").ok_or(0) == Ok(inner="foo")
            True
        A ``Null`` converts to ``Err`` through ``ok_or``.

        .. code-block:: python

            >>> Null().ok_or(0) == Err(error=0)
            True
        ::
        """
        from ._result_v2 import Ok, Result  # noqa: PLC0415

        return cast(Result[T, E], Ok(self.inner))

    def ok_or_else[E](self, err: Callable[[], E]) -> Result[T, E]:  # noqa: ARG002
        """Papertrail examples:

        A ``Some`` converts to ``Ok`` without calling the error function.

        .. code-block:: python

            >>> Some(inner="foo").ok_or_else(get_42) == Ok(inner="foo")
            True
        A ``Null`` converts to ``Err`` using the error function result.

        .. code-block:: python

            >>> Null().ok_or_else(get_42) == Err(error=42)
            True
        ::
        """
        from ._result_v2 import Ok, Result  # noqa: PLC0415

        return cast(Result[T, E], Ok(self.inner))

    def or_(self, opt_b: Option[T]) -> Option[T]:  # noqa: ARG002
        """Papertrail examples:

        A ``Some`` keeps its value when ``or_`` receives ``Null``.

        .. code-block:: python

            >>> Some(inner=2).or_(Null()) == Some(inner=2)
            True
        A ``Null`` gives way to a ``Some`` passed to ``or_``.

        .. code-block:: python

            >>> Null().or_(Some(inner=100)) == Some(inner=100)
            True
        When both options contain values, ``or_`` keeps the first ``Some``.

        .. code-block:: python

            >>> Some(inner=2).or_(Some(inner=100)) == Some(inner=2)
            True
        When both options are ``Null``, ``or_`` returns ``Null``.

        .. code-block:: python

            >>> Null().or_(Null()) == Null()
            True
        ::
        """
        return self

    def or_else(self, opt_b: Callable[[], Option[T]]) -> Option[T]:  # noqa: ARG002
        """Papertrail examples:

        A ``Some`` passes through ``or_else`` without calling the function.

        .. code-block:: python

            >>> Some(inner="barbarians").or_else(get_some_vikings) == Some(inner="barbarians")
            True
        For ``Null``, ``or_else`` returns the ``Some`` produced by the function.

        .. code-block:: python

            >>> Null().or_else(get_some_vikings) == Some(inner="vikings")
            True
        If the fallback also produces ``Null``, ``or_else`` returns ``Null``.

        .. code-block:: python

            >>> Null().or_else(Null) == Null()
            True
        ::
        """
        return self

    def replace(self, value: T) -> Option[T]:
        """Papertrail examples:

        Replacing a ``Some`` returns a new ``Some`` with the replacement value.

        .. code-block:: python

            >>> Some(inner=2).replace(5) == Some(inner=5)
            True
        Replacing ``Null`` leaves it as ``Null``.

        .. code-block:: python

            >>> Null().replace(3) == Null()
            True
        ::
        """
        return Some(value)

    def transpose(self) -> Result[Option[T], Option[T]]:
        """Papertrail examples:

        Transposing ``Some(Ok(value))`` produces ``Ok(Some(value))``.

        .. code-block:: python

            >>> Some(inner=Ok(inner=2)).transpose() == Ok(inner=Some(inner=2))
            True
        Transposing ``Some(Err(error))`` produces ``Err(Some(error))``.

        .. code-block:: python

            >>> Some(inner=Err(error=2)).transpose() == Err(error=Some(inner=2))
            True
        Transposing ``Null`` produces ``Ok(Null())``.

        .. code-block:: python

            >>> Null().transpose() == Ok(inner=Null())
            True
        ::
        """
        from ._result_v2 import Err, Ok, Result  # noqa: PLC0415

        if isinstance(self.inner, Ok):
            return cast(Result[Option[T], Option[T]], Ok(Some(self.inner.inner)))
        if isinstance(self.inner, Err):
            return cast(Result[Option[T], Option[T]], Err[Option[T]](Some(self.inner.error)))
        raise TypeError("inner must be a `Result` type")

    def unwrap(self) -> T:
        """Papertrail examples:

        ``unwrap`` extracts the value from a ``Some``.

        .. code-block:: python

            >>> Some(inner=2).unwrap() == 2
            True
        ::
        """
        return self.inner

    def unwrap_or(self, default: T) -> T:  # noqa: ARG002
        """Papertrail examples:

        With a ``Some``, ``unwrap_or`` returns the value and ignores the default.

        .. code-block:: python

            >>> Some(inner="car").unwrap_or("bike") == "car"
            True
        With ``Null``, ``unwrap_or`` returns the default.

        .. code-block:: python

            >>> Null().unwrap_or("bike") == "bike"
            True
        ::
        """
        return self.inner

    def unwrap_or_else(self, fn: Callable[[], T]) -> T:  # noqa: ARG002
        """Papertrail examples:

        A ``Some`` makes ``unwrap_or_else`` return its value without calling the function.

        .. code-block:: python

            >>> Some(inner=4).unwrap_or_else(get_42) == 4
            True
        A ``Null`` makes ``unwrap_or_else`` return the function result.

        .. code-block:: python

            >>> Null().unwrap_or_else(get_42) == 42
            True
        ::
        """
        return self.inner

    def zip[U](self, other: Option[U]) -> Option[tuple[T, U]]:
        """Papertrail examples:

        Zipping two ``Some`` values produces a ``Some`` containing both values.

        .. code-block:: python

            >>> Some(inner=1).zip(Some(inner="hi")) == Some(inner=(1, "hi"))
            True
        Zipping a ``Some`` with ``Null`` produces ``Null``.

        .. code-block:: python

            >>> Some(inner=1).zip(Null()) == Null()
            True
        Zipping ``Null`` with a ``Some`` produces ``Null``.

        .. code-block:: python

            >>> Null().zip(Some(inner=1)) == Null()
            True
        ::
        """
        if isinstance(other, Some):
            return Some[tuple[T, U]]((self.inner, other.inner))
        return Null[tuple[T, U]]()

    def unzip[U](self) -> tuple[Option[T], Option[U]]:
        """Papertrail examples:

        Unzipping a ``Some`` pair produces two ``Some`` values.

        .. code-block:: python

            >>> Some(inner=(2, 2)).unzip() == (Some(inner=2), Some(inner=2))
            True
        Unzipping a ``Some`` with a non-pair value produces two ``Null`` values.

        .. code-block:: python

            >>> Some(inner=4).unzip() == (Null(), Null())
            True
        Unzipping ``Null`` produces two ``Null`` values.

        .. code-block:: python

            >>> Null().unzip() == (Null(), Null())
            True
        ::
        """
        if isinstance(self.inner, tuple) and len(self.inner) == 2:  # noqa: PLR2004
            return (Some(self.inner[0]), Some(self.inner[1]))
        return (Null(), Null())


@attrs.define(frozen=True)
class Null[T](Option):
    def and_(self, opt_b: Option[T]) -> Option[T]:  # noqa: ARG002
        """Papertrail examples:

        A ``Some`` combined with ``Null`` through ``and_`` produces ``Null``.

        .. code-block:: python

            >>> Some(inner=2).and_(Null()) == Null()
            True
        A ``Null`` combined with an ``Some`` through ``and_`` remains ``Null``.

        .. code-block:: python

            >>> Null().and_(Some(inner="foo")) == Null()
            True
        When both options contain values, ``and_`` keeps the second ``Some``.

        .. code-block:: python

            >>> Some(inner=2).and_(Some(inner="foo")) == Some(inner="foo")
            True
        Combining two ``Null`` values with ``and_`` produces ``Null``.

        .. code-block:: python

            >>> Null().and_(Null()) == Null()
            True
        ::
        """
        return self

    def and_then[U](self, fn: Callable[[T], Option[U]]) -> Option[U]:  # noqa: ARG002
        """Papertrail examples:

        A successful function passed to ``and_then`` returns its ``Some`` result.

        .. code-block:: python

            >>> Some(inner=2).and_then(must_be_less_than_10) == Some(inner=2)
            True
        When the function returns ``Null``, ``and_then`` passes that ``Null`` through.

        .. code-block:: python

            >>> Some(inner=20).and_then(must_be_less_than_10) == Null()
            True
        An existing ``Null`` skips the function passed to ``and_then``.

        .. code-block:: python

            >>> Null().and_then(must_be_less_than_10) == Null()
            True
        ::
        """
        return self

    def as_list(self) -> list[T]:
        """Papertrail examples:

        A ``Some`` becomes a one-item list through ``as_list``.

        .. code-block:: python

            >>> Some(inner=2).as_list() == [2]
            True
        ``as_list`` represents ``Null`` as an empty list.

        .. code-block:: python

            >>> Null().as_list() == []
            True
        ::
        """
        return []

    def as_tuple(self) -> tuple[T, ...]:
        """Papertrail examples:

        A ``Some`` becomes a one-item tuple through ``as_tuple``.

        .. code-block:: python

            >>> Some(inner=2).as_tuple() == (2,)
            True
        ``as_tuple`` represents ``Null`` as an empty tuple.

        .. code-block:: python

            >>> Null().as_tuple() == ()
            True
        ::
        """
        return ()

    def expect(self, msg: str) -> T:
        """Papertrail examples:

        ``expect`` extracts the value from a ``Some``.

        .. code-block:: python

            >>> Some(inner=2).expect("must be positive") == 2
            True
        ::
        """
        raise ValueError(msg)

    def filter_(self, predicate: Callable[[T], bool]) -> Option[T]:  # noqa: ARG002
        """Papertrail examples:

        A ``Some`` that fails the predicate becomes ``Null`` through ``filter_``.

        .. code-block:: python

            >>> Some(inner=3).filter_(is_even) == Null()
            True
        A ``Some`` that passes the predicate remains unchanged.

        .. code-block:: python

            >>> Some(inner=4).filter_(is_even) == Some(inner=4)
            True
        ``filter_`` leaves ``Null`` unchanged without calling the predicate.

        .. code-block:: python

            >>> Null().filter_(is_even) == Null()
            True
        ::
        """
        return self

    def flatten(self) -> Option[T]:
        """Papertrail examples:

        Flattening three nested ``Some`` values removes only the outer option.

        .. code-block:: python

            >>> Some(inner=Some(inner=Some(inner=2))).flatten() == Some(inner=Some(inner=2))
            True
        Flattening a doubly wrapped value returns the inner ``Some``.

        .. code-block:: python

            >>> Some(inner=Some(inner=2)).flatten() == Some(inner=2)
            True
        Flattening a ``Some`` with a non-option value does nothing.

        .. code-block:: python

            >>> Some(inner=2).flatten() == Some(inner=2)
            True
        A ``Null`` passes through ``flatten`` unchanged.

        .. code-block:: python

            >>> Null().flatten() == Null()
            True
        ::
        """
        return self

    def inspect(self, fn: Callable[[T], None]) -> Option[T]:  # noqa: ARG002
        """Papertrail examples:

        Inspecting a ``Some`` calls the function and returns the original option.

        .. code-block:: python

            >>> Some(inner=[1]).inspect(append_to_list) == Some(inner=[1])
            True
        Inspecting ``Null`` returns ``Null`` without calling the function.

        .. code-block:: python

            >>> Null().inspect(append_to_list) == Null()
            True
        ::
        """
        return self

    def is_none(self) -> bool:
        """Papertrail examples:

        ``is_none`` reports ``False`` for a ``Some``.

        .. code-block:: python

            >>> Some(inner=2).is_none() == False
            True
        For ``Null``, ``is_none`` reports ``True``.

        .. code-block:: python

            >>> Null().is_none() == True
            True
        ::
        """
        return True

    def is_none_or(self, fn: Callable[[T], bool]) -> bool:  # noqa: ARG002
        """Papertrail examples:

        When the predicate rejects a ``Some``, ``is_none_or`` reports ``False``.

        .. code-block:: python

            >>> Some(inner=1).is_none_or(is_even) == False
            True
        When the predicate accepts a ``Some``, ``is_none_or`` reports ``True``.

        .. code-block:: python

            >>> Some(inner=2).is_none_or(is_even) == True
            True
        ``Null`` makes ``is_none_or`` report ``True`` without calling the predicate.

        .. code-block:: python

            >>> Null().is_none_or(is_even) == True
            True
        ::
        """
        return True

    def is_some(self) -> bool:
        """Papertrail examples:

        ``is_some`` reports ``True`` for a ``Some``.

        .. code-block:: python

            >>> Some(inner=2).is_some() == True
            True
        For ``Null``, ``is_some`` reports ``False``.

        .. code-block:: python

            >>> Null().is_some() == False
            True
        ::
        """
        return False

    def is_some_and(self, fn: Callable[[T], bool]) -> bool:  # noqa: ARG002
        """Papertrail examples:

        When the predicate rejects a ``Some``, ``is_some_and`` reports ``False``.

        .. code-block:: python

            >>> Some(inner=1).is_some_and(is_even) == False
            True
        When the predicate accepts a ``Some``, ``is_some_and`` reports ``True``.

        .. code-block:: python

            >>> Some(inner=2).is_some_and(is_even) == True
            True
        A ``Null`` makes ``is_some_and`` report ``False`` without calling the predicate.

        .. code-block:: python

            >>> Null().is_some_and(is_even) == False
            True
        ::
        """
        return False

    def map[U](self, fn: Callable[[T], U]) -> Option[U]:  # noqa: ARG002
        """Papertrail examples:

        Mapping a ``Some`` applies the function and wraps its result in a new ``Some``.

        .. code-block:: python

            >>> Some(inner=1).map(add_one) == Some(inner=2)
            True
        Mapping ``Null`` leaves it unchanged and skips the function.

        .. code-block:: python

            >>> Null().map(add_one) == Null()
            True
        ::
        """
        return self

    def map_or[U](self, default: U, fn: Callable[[T], U]) -> U:  # noqa: ARG002
        """Papertrail examples:

        For a ``Some``, ``map_or`` uses the function result instead of the default.

        .. code-block:: python

            >>> Some(inner="foo").map_or(42, len) == 3
            True
        For ``Null``, ``map_or`` returns the supplied default.

        .. code-block:: python

            >>> Null().map_or(42, len) == 42
            True
        ::
        """
        return default

    def map_or_else[U](self, default: Callable[..., U], fn: Callable[[T], U]) -> U:  # noqa: ARG002
        """Papertrail examples:

        A ``Some`` makes ``map_or_else`` use the mapping function.

        .. code-block:: python

            >>> Some(inner="foo").map_or_else(get_42, len) == 3
            True
        A ``Null`` makes ``map_or_else`` use the default function.

        .. code-block:: python

            >>> Null().map_or_else(get_42, len) == 42
            True
        ::
        """
        return default()

    def ok_or[E](self, err: E) -> Result[T, E]:
        """Papertrail examples:

        A ``Some`` converts to ``Ok`` through ``ok_or``.

        .. code-block:: python

            >>> Some(inner="foo").ok_or(0) == Ok(inner="foo")
            True
        A ``Null`` converts to ``Err`` through ``ok_or``.

        .. code-block:: python

            >>> Null().ok_or(0) == Err(error=0)
            True
        ::
        """
        from ._result_v2 import Err, Result  # noqa: PLC0415

        return cast(Result[T, E], Err[E](err))

    def ok_or_else[E](self, err: Callable[[], E]) -> Result[T, E]:
        """Papertrail examples:

        A ``Some`` converts to ``Ok`` without calling the error function.

        .. code-block:: python

            >>> Some(inner="foo").ok_or_else(get_42) == Ok(inner="foo")
            True
        A ``Null`` converts to ``Err`` using the error function result.

        .. code-block:: python

            >>> Null().ok_or_else(get_42) == Err(error=42)
            True
        ::
        """
        from ._result_v2 import Err, Result  # noqa: PLC0415

        return cast(Result[T, E], Err[E](err()))

    def or_(self, opt_b: Option[T]) -> Option[T]:
        """Papertrail examples:

        A ``Some`` keeps its value when ``or_`` receives ``Null``.

        .. code-block:: python

            >>> Some(inner=2).or_(Null()) == Some(inner=2)
            True
        A ``Null`` gives way to a ``Some`` passed to ``or_``.

        .. code-block:: python

            >>> Null().or_(Some(inner=100)) == Some(inner=100)
            True
        When both options contain values, ``or_`` keeps the first ``Some``.

        .. code-block:: python

            >>> Some(inner=2).or_(Some(inner=100)) == Some(inner=2)
            True
        When both options are ``Null``, ``or_`` returns ``Null``.

        .. code-block:: python

            >>> Null().or_(Null()) == Null()
            True
        ::
        """
        return opt_b

    def or_else(self, opt_b: Callable[[], Option[T]]) -> Option[T]:
        """Papertrail examples:

        A ``Some`` passes through ``or_else`` without calling the function.

        .. code-block:: python

            >>> Some(inner="barbarians").or_else(get_some_vikings) == Some(inner="barbarians")
            True
        For ``Null``, ``or_else`` returns the ``Some`` produced by the function.

        .. code-block:: python

            >>> Null().or_else(get_some_vikings) == Some(inner="vikings")
            True
        If the fallback also produces ``Null``, ``or_else`` returns ``Null``.

        .. code-block:: python

            >>> Null().or_else(Null) == Null()
            True
        ::
        """
        return opt_b()

    def replace(self, value: T) -> Option[T]:  # noqa: ARG002
        """Papertrail examples:

        Replacing a ``Some`` returns a new ``Some`` with the replacement value.

        .. code-block:: python

            >>> Some(inner=2).replace(5) == Some(inner=5)
            True
        Replacing ``Null`` leaves it as ``Null``.

        .. code-block:: python

            >>> Null().replace(3) == Null()
            True
        ::
        """
        return self

    def transpose[E](self) -> Result[Option[T], E]:
        """Papertrail examples:

        Transposing ``Some(Ok(value))`` produces ``Ok(Some(value))``.

        .. code-block:: python

            >>> Some(inner=Ok(inner=2)).transpose() == Ok(inner=Some(inner=2))
            True
        Transposing ``Some(Err(error))`` produces ``Err(Some(error))``.

        .. code-block:: python

            >>> Some(inner=Err(error=2)).transpose() == Err(error=Some(inner=2))
            True
        Transposing ``Null`` produces ``Ok(Null())``.

        .. code-block:: python

            >>> Null().transpose() == Ok(inner=Null())
            True
        ::
        """
        from ._result_v2 import Ok, Result  # noqa: PLC0415

        return cast(Result[Option[T], E], Ok(self))

    def unwrap(self) -> T:
        """Papertrail examples:

        ``unwrap`` extracts the value from a ``Some``.

        .. code-block:: python

            >>> Some(inner=2).unwrap() == 2
            True
        ::
        """
        raise TypeError("Can't call `unwrap` on `Null`")

    def unwrap_or(self, default: T) -> T:
        """Papertrail examples:

        With a ``Some``, ``unwrap_or`` returns the value and ignores the default.

        .. code-block:: python

            >>> Some(inner="car").unwrap_or("bike") == "car"
            True
        With ``Null``, ``unwrap_or`` returns the default.

        .. code-block:: python

            >>> Null().unwrap_or("bike") == "bike"
            True
        ::
        """
        return default

    def unwrap_or_else(self, fn: Callable[[], T]) -> T:
        """Papertrail examples:

        A ``Some`` makes ``unwrap_or_else`` return its value without calling the function.

        .. code-block:: python

            >>> Some(inner=4).unwrap_or_else(get_42) == 4
            True
        A ``Null`` makes ``unwrap_or_else`` return the function result.

        .. code-block:: python

            >>> Null().unwrap_or_else(get_42) == 42
            True
        ::
        """
        return fn()

    def zip[U](self, other: Option[U]) -> Option[tuple[T, U]]:  # noqa: ARG002
        """Papertrail examples:

        Zipping two ``Some`` values produces a ``Some`` containing both values.

        .. code-block:: python

            >>> Some(inner=1).zip(Some(inner="hi")) == Some(inner=(1, "hi"))
            True
        Zipping a ``Some`` with ``Null`` produces ``Null``.

        .. code-block:: python

            >>> Some(inner=1).zip(Null()) == Null()
            True
        Zipping ``Null`` with a ``Some`` produces ``Null``.

        .. code-block:: python

            >>> Null().zip(Some(inner=1)) == Null()
            True
        ::
        """
        return self

    def unzip[U](self) -> tuple[Option[T], Option[U]]:
        """Papertrail examples:

        Unzipping a ``Some`` pair produces two ``Some`` values.

        .. code-block:: python

            >>> Some(inner=(2, 2)).unzip() == (Some(inner=2), Some(inner=2))
            True
        Unzipping a ``Some`` with a non-pair value produces two ``Null`` values.

        .. code-block:: python

            >>> Some(inner=4).unzip() == (Null(), Null())
            True
        Unzipping ``Null`` produces two ``Null`` values.

        .. code-block:: python

            >>> Null().unzip() == (Null(), Null())
            True
        ::
        """
        return (Null(), Null())
