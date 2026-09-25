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
    @abstractmethod
    def and_(self, opt_b: Option[T]) -> Option[T]:
        """.. code-block:: python

            >>> Some(inner=2).and_(Null()) == Null()
            True

            >>> Null().and_(Some(inner="foo")) == Null()
            True

            >>> Some(inner=2).and_(Some(inner="foo")) == Some(inner="foo")
            True

            >>> Null().and_(Null()) == Null()
            True
        ::
        """
        ...

    @abstractmethod
    def and_then[U](self, fn: Callable[[T], Option[U]]) -> Option[T]:
        """.. code-block:: python

            >>> Some(inner=2).and_then(must_be_less_than_10) == Some(inner=2)
            True

            >>> Some(inner=20).and_then(must_be_less_than_10) == Null()
            True

            >>> Null().and_then(must_be_less_than_10) == Null()
            True
        ::
        """
        ...

    @abstractmethod
    def as_list(self) -> list[T]:
        """.. code-block:: python

            >>> Some(inner=2).as_list() == [2]
            True

            >>> Null().as_list() == []
            True
        ::
        """
        ...

    @abstractmethod
    def as_tuple(self) -> tuple[T, ...]:
        """.. code-block:: python

            >>> Some(inner=2).as_tuple() == (2,)
            True

            >>> Null().as_tuple() == ()
            True
        ::
        """
        ...

    def cloned(self) -> Option[T]:
        """.. code-block:: python

            >>> Some(inner=2).cloned() == Some(inner=2)
            True

            >>> Null().cloned() == Null()
            True
        ::
        """
        return deepcopy(self)

    @abstractmethod
    def expect(self, msg: str) -> T:
        """.. code-block:: python

            >>> Some(inner=2).expect("must be positive") == 2
            True
        ::
        """
        ...

    @abstractmethod
    def filter_(self, predicate: Callable[[T], bool]) -> Option[T]:
        """.. code-block:: python

            >>> Some(inner=3).filter_(is_even) == Null()
            True

            >>> Some(inner=4).filter_(is_even) == Some(inner=4)
            True

            >>> Null().filter_(is_even) == Null()
            True
        ::
        """
        ...

    @abstractmethod
    def flatten(self) -> Option[T]:
        """.. code-block:: python

            >>> Some(inner=Some(inner=Some(inner=2))).flatten() == Some(inner=Some(inner=2))
            True

            >>> Some(inner=Some(inner=2)).flatten() == Some(inner=2)
            True

            >>> Some(inner=2).flatten() == Some(inner=2)
            True

            >>> Null().flatten() == Null()
            True
        ::
        """
        ...

    @abstractmethod
    def inspect(self, fn: Callable[[T], None]) -> Option[T]:
        """.. code-block:: python

            >>> Some(inner=[1]).inspect(append_to_list) == Some(inner=[1])
            True

            >>> Null().inspect(append_to_list) == Null()
            True
        ::
        """
        ...

    @abstractmethod
    def is_none(self) -> bool:
        """.. code-block:: python

            >>> Some(inner=2).is_none() == False
            True

            >>> Null().is_none() == True
            True
        ::
        """
        ...

    @abstractmethod
    def is_none_or(self, fn: Callable[[T], bool]) -> bool:
        """.. code-block:: python

            >>> Some(inner=1).is_none_or(is_even) == False
            True

            >>> Some(inner=2).is_none_or(is_even) == True
            True

            >>> Null().is_none_or(is_even) == True
            True
        ::
        """
        ...

    @abstractmethod
    def is_some(self) -> bool:
        """.. code-block:: python

            >>> Some(inner=2).is_some() == True
            True

            >>> Null().is_some() == False
            True
        ::
        """
        ...

    @abstractmethod
    def is_some_and(self, fn: Callable[[T], bool]) -> bool:
        """.. code-block:: python

            >>> Some(inner=1).is_some_and(is_even) == False
            True

            >>> Some(inner=2).is_some_and(is_even) == True
            True

            >>> Null().is_some_and(is_even) == False
            True
        ::
        """
        ...

    @abstractmethod
    def map[U](self, fn: Callable[[T], U]) -> Option[U]:
        """.. code-block:: python

            >>> Some(inner=1).map(add_one) == Some(inner=2)
            True

            >>> Null().map(add_one) == Null()
            True
        ::
        """
        ...

    @abstractmethod
    def map_or[U](self, default: U, fn: Callable[[T], U]) -> U: ...

    @abstractmethod
    def map_or_else[U](self, default: Callable[..., U], fn: Callable[[T], U]) -> U: ...

    @abstractmethod
    def ok_or[E](self, err: E) -> Result[T, E]:
        """.. code-block:: python

            >>> Some(inner="foo").ok_or(0) == Ok(inner="foo")
            True

            >>> Null().ok_or(0) == Err(error=0, traceback="")
            True
        ::
        """
        ...

    @abstractmethod
    def ok_or_else[E](self, err: Callable[..., E]) -> Result[T, E]:
        """.. code-block:: python

            >>> Some(inner="foo").ok_or_else(get_42) == Ok(inner="foo")
            True

            >>> Null().ok_or_else(get_42) == Err(error=42, traceback="")
            True
        ::
        """
        ...

    @abstractmethod
    def or_(self, opt_b: Option[T]) -> Option[T]:
        """.. code-block:: python

            >>> Some(inner=2).or_(Null()) == Some(inner=2)
            True

            >>> Null().or_(Some(inner=100)) == Some(inner=100)
            True

            >>> Some(inner=2).or_(Some(inner=100)) == Some(inner=2)
            True

            >>> Null().or_(Null()) == Null()
            True
        ::
        """
        ...

    @abstractmethod
    def or_else(self, opt_b: Callable[..., Option[T]]) -> Option[T]:
        """.. code-block:: python

            >>> Some(inner="barbarians").or_else(get_some_vikings) == Some(inner="barbarians")
            True

            >>> Null().or_else(get_some_vikings) == Some(inner="vikings")
            True

            >>> Null().or_else(Null) == Null()
            True
        ::
        """
        ...

    @abstractmethod
    def replace(self, value: T) -> Option[T]:
        """.. code-block:: python

            >>> Some(inner=2).replace(5) == Some(inner=5)
            True

            >>> Null().replace(3) == Null()
            True
        ::
        """
        ...

    @abstractmethod
    def transpose[E](self) -> Result[Option[T], E]:
        """.. code-block:: python

            >>> Some(inner=Ok(inner=2)).transpose() == Ok(inner=Some(inner=2))
            True

            >>> Some(inner=Err(error=2, traceback="")).transpose() == Err(
            ...     error=Some(inner=2), traceback=""
            ... )
            True

            >>> Null().transpose() == Ok(inner=Null())
            True
        ::
        """
        ...

    @abstractmethod
    def unwrap(self) -> T:
        """.. code-block:: python

            >>> Some(inner=2).unwrap() == 2
            True
        ::
        """
        ...

    @abstractmethod
    def unwrap_or(self, default: T) -> T:
        """.. code-block:: python

            >>> Some(inner="car").unwrap_or("bike") == "car"
            True

            >>> Null().unwrap_or("bike") == "bike"
            True
        ::
        """
        ...

    @abstractmethod
    def unwrap_or_else(self, fn: Callable[..., T]) -> T:
        """.. code-block:: python

            >>> Some(inner=4).unwrap_or_else(get_42) == 4
            True

            >>> Null().unwrap_or_else(get_42) == 42
            True
        ::
        """
        ...

    @abstractmethod
    def zip[U](self, other: Option[U]) -> Option[tuple[T, U]]:
        """.. code-block:: python

            >>> Some(inner=1).zip(Some(inner="hi")) == Some(inner=(1, "hi"))
            True

            >>> Some(inner=1).zip(Null()) == Null()
            True

            >>> Null().zip(Some(inner=1)) == Null()
            True
        ::
        """
        ...

    @abstractmethod
    def unzip[U](self) -> tuple[Option[T], Option[U]]:
        """.. code-block:: python

            >>> Some(inner=(2, 2)).unzip() == (Some(inner=2), Some(inner=2))
            True

            >>> Some(inner=4).unzip() == (Null(), Null())
            True

            >>> Null().unzip() == (Null(), Null())
            True
        ::
        """
        ...


@attrs.define(frozen=True)
class Some[T](Option):
    inner: T

    def and_(self, opt_b: Option[T]) -> Option[T]:
        """.. code-block:: python

            >>> Some(inner=2).and_(Null()) == Null()
            True

            >>> Null().and_(Some(inner="foo")) == Null()
            True

            >>> Some(inner=2).and_(Some(inner="foo")) == Some(inner="foo")
            True

            >>> Null().and_(Null()) == Null()
            True
        ::
        """
        return opt_b

    def and_then[U](self, fn: Callable[[T], Option[U]]) -> Option[U]:
        """.. code-block:: python

            >>> Some(inner=2).and_then(must_be_less_than_10) == Some(inner=2)
            True

            >>> Some(inner=20).and_then(must_be_less_than_10) == Null()
            True

            >>> Null().and_then(must_be_less_than_10) == Null()
            True
        ::
        """
        return fn(self.inner)

    def as_list(self) -> list[T]:
        """.. code-block:: python

            >>> Some(inner=2).as_list() == [2]
            True

            >>> Null().as_list() == []
            True
        ::
        """
        return [self.inner]

    def as_tuple(self) -> tuple[T, ...]:
        """.. code-block:: python

            >>> Some(inner=2).as_tuple() == (2,)
            True

            >>> Null().as_tuple() == ()
            True
        ::
        """
        return (self.inner,)

    def expect(self, msg: str) -> T:  # noqa: ARG002
        """.. code-block:: python

            >>> Some(inner=2).expect("must be positive") == 2
            True
        ::
        """
        return self.inner

    def filter_(self, predicate: Callable[[T], bool]) -> Option[T]:
        """.. code-block:: python

            >>> Some(inner=3).filter_(is_even) == Null()
            True

            >>> Some(inner=4).filter_(is_even) == Some(inner=4)
            True

            >>> Null().filter_(is_even) == Null()
            True
        ::
        """
        return self if predicate(self.inner) else Null()

    def flatten(self) -> Option[T]:
        """.. code-block:: python

            >>> Some(inner=Some(inner=Some(inner=2))).flatten() == Some(inner=Some(inner=2))
            True

            >>> Some(inner=Some(inner=2)).flatten() == Some(inner=2)
            True

            >>> Some(inner=2).flatten() == Some(inner=2)
            True

            >>> Null().flatten() == Null()
            True
        ::
        """
        if isinstance(self.inner, Some):
            return self.inner
        return self

    def inspect(self, fn: Callable[[T], None]) -> Option[T]:
        """.. code-block:: python

            >>> Some(inner=[1]).inspect(append_to_list) == Some(inner=[1])
            True

            >>> Null().inspect(append_to_list) == Null()
            True
        ::
        """
        fn(deepcopy(self.inner))
        return self

    def is_none(self) -> bool:
        """.. code-block:: python

            >>> Some(inner=2).is_none() == False
            True

            >>> Null().is_none() == True
            True
        ::
        """
        return False

    def is_none_or(self, fn: Callable[[T], bool]) -> bool:
        """.. code-block:: python

            >>> Some(inner=1).is_none_or(is_even) == False
            True

            >>> Some(inner=2).is_none_or(is_even) == True
            True

            >>> Null().is_none_or(is_even) == True
            True
        ::
        """
        return fn(self.inner)

    def is_some(self) -> bool:
        """.. code-block:: python

            >>> Some(inner=2).is_some() == True
            True

            >>> Null().is_some() == False
            True
        ::
        """
        return True

    def is_some_and(self, fn: Callable[[T], bool]) -> bool:
        """.. code-block:: python

            >>> Some(inner=1).is_some_and(is_even) == False
            True

            >>> Some(inner=2).is_some_and(is_even) == True
            True

            >>> Null().is_some_and(is_even) == False
            True
        ::
        """
        return fn(self.inner)

    def map[U](self, fn: Callable[[T], U]) -> Option[U]:
        """.. code-block:: python

            >>> Some(inner=1).map(add_one) == Some(inner=2)
            True

            >>> Null().map(add_one) == Null()
            True
        ::
        """
        return Some(fn(self.inner))

    def map_or[U](self, default: U, fn: Callable[[T], U]) -> U:  # noqa: ARG002
        return fn(self.inner)

    def map_or_else[U](self, default: Callable[[], U], fn: Callable[[T], U]) -> U:  # noqa: ARG002
        return fn(self.inner)

    def ok_or[E](self, err: E) -> Result[T, E]:  # noqa: ARG002
        """.. code-block:: python

            >>> Some(inner="foo").ok_or(0) == Ok(inner="foo")
            True

            >>> Null().ok_or(0) == Err(error=0, traceback="")
            True
        ::
        """
        from ._result_v2 import Ok, Result  # noqa: PLC0415

        return cast(Result[T, E], Ok(self.inner))

    def ok_or_else[E](self, err: Callable[[], E]) -> Result[T, E]:  # noqa: ARG002
        """.. code-block:: python

            >>> Some(inner="foo").ok_or_else(get_42) == Ok(inner="foo")
            True

            >>> Null().ok_or_else(get_42) == Err(error=42, traceback="")
            True
        ::
        """
        from ._result_v2 import Ok, Result  # noqa: PLC0415

        return cast(Result[T, E], Ok(self.inner))

    def or_(self, opt_b: Option[T]) -> Option[T]:  # noqa: ARG002
        """.. code-block:: python

            >>> Some(inner=2).or_(Null()) == Some(inner=2)
            True

            >>> Null().or_(Some(inner=100)) == Some(inner=100)
            True

            >>> Some(inner=2).or_(Some(inner=100)) == Some(inner=2)
            True

            >>> Null().or_(Null()) == Null()
            True
        ::
        """
        return self

    def or_else(self, opt_b: Callable[[], Option[T]]) -> Option[T]:  # noqa: ARG002
        """.. code-block:: python

            >>> Some(inner="barbarians").or_else(get_some_vikings) == Some(inner="barbarians")
            True

            >>> Null().or_else(get_some_vikings) == Some(inner="vikings")
            True

            >>> Null().or_else(Null) == Null()
            True
        ::
        """
        return self

    def replace(self, value: T) -> Option[T]:
        """.. code-block:: python

            >>> Some(inner=2).replace(5) == Some(inner=5)
            True

            >>> Null().replace(3) == Null()
            True
        ::
        """
        return Some(value)

    def transpose(self) -> Result[Option[T], Option[T]]:
        """.. code-block:: python

            >>> Some(inner=Ok(inner=2)).transpose() == Ok(inner=Some(inner=2))
            True

            >>> Some(inner=Err(error=2, traceback="")).transpose() == Err(
            ...     error=Some(inner=2), traceback=""
            ... )
            True

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
        """.. code-block:: python

            >>> Some(inner=2).unwrap() == 2
            True
        ::
        """
        return self.inner

    def unwrap_or(self, default: T) -> T:  # noqa: ARG002
        """.. code-block:: python

            >>> Some(inner="car").unwrap_or("bike") == "car"
            True

            >>> Null().unwrap_or("bike") == "bike"
            True
        ::
        """
        return self.inner

    def unwrap_or_else(self, fn: Callable[[], T]) -> T:  # noqa: ARG002
        """.. code-block:: python

            >>> Some(inner=4).unwrap_or_else(get_42) == 4
            True

            >>> Null().unwrap_or_else(get_42) == 42
            True
        ::
        """
        return self.inner

    def zip[U](self, other: Option[U]) -> Option[tuple[T, U]]:
        """.. code-block:: python

            >>> Some(inner=1).zip(Some(inner="hi")) == Some(inner=(1, "hi"))
            True

            >>> Some(inner=1).zip(Null()) == Null()
            True

            >>> Null().zip(Some(inner=1)) == Null()
            True
        ::
        """
        if isinstance(other, Some):
            return Some[tuple[T, U]]((self.inner, other.inner))
        return Null[tuple[T, U]]()

    def unzip[U](self) -> tuple[Option[T], Option[U]]:
        """.. code-block:: python

            >>> Some(inner=(2, 2)).unzip() == (Some(inner=2), Some(inner=2))
            True

            >>> Some(inner=4).unzip() == (Null(), Null())
            True

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
        """.. code-block:: python

            >>> Some(inner=2).and_(Null()) == Null()
            True

            >>> Null().and_(Some(inner="foo")) == Null()
            True

            >>> Some(inner=2).and_(Some(inner="foo")) == Some(inner="foo")
            True

            >>> Null().and_(Null()) == Null()
            True
        ::
        """
        return self

    def and_then[U](self, fn: Callable[[T], Option[U]]) -> Option[U]:  # noqa: ARG002
        """.. code-block:: python

            >>> Some(inner=2).and_then(must_be_less_than_10) == Some(inner=2)
            True

            >>> Some(inner=20).and_then(must_be_less_than_10) == Null()
            True

            >>> Null().and_then(must_be_less_than_10) == Null()
            True
        ::
        """
        return self

    def as_list(self) -> list[T]:
        """.. code-block:: python

            >>> Some(inner=2).as_list() == [2]
            True

            >>> Null().as_list() == []
            True
        ::
        """
        return []

    def as_tuple(self) -> tuple[T, ...]:
        """.. code-block:: python

            >>> Some(inner=2).as_tuple() == (2,)
            True

            >>> Null().as_tuple() == ()
            True
        ::
        """
        return ()

    def expect(self, msg: str) -> T:
        """.. code-block:: python

            >>> Some(inner=2).expect("must be positive") == 2
            True
        ::
        """
        raise ValueError(msg)

    def filter_(self, predicate: Callable[[T], bool]) -> Option[T]:  # noqa: ARG002
        """.. code-block:: python

            >>> Some(inner=3).filter_(is_even) == Null()
            True

            >>> Some(inner=4).filter_(is_even) == Some(inner=4)
            True

            >>> Null().filter_(is_even) == Null()
            True
        ::
        """
        return self

    def flatten(self) -> Option[T]:
        """.. code-block:: python

            >>> Some(inner=Some(inner=Some(inner=2))).flatten() == Some(inner=Some(inner=2))
            True

            >>> Some(inner=Some(inner=2)).flatten() == Some(inner=2)
            True

            >>> Some(inner=2).flatten() == Some(inner=2)
            True

            >>> Null().flatten() == Null()
            True
        ::
        """
        return self

    def inspect(self, fn: Callable[[T], None]) -> Option[T]:  # noqa: ARG002
        """.. code-block:: python

            >>> Some(inner=[1]).inspect(append_to_list) == Some(inner=[1])
            True

            >>> Null().inspect(append_to_list) == Null()
            True
        ::
        """
        return self

    def is_none(self) -> bool:
        """.. code-block:: python

            >>> Some(inner=2).is_none() == False
            True

            >>> Null().is_none() == True
            True
        ::
        """
        return True

    def is_none_or(self, fn: Callable[[T], bool]) -> bool:  # noqa: ARG002
        """.. code-block:: python

            >>> Some(inner=1).is_none_or(is_even) == False
            True

            >>> Some(inner=2).is_none_or(is_even) == True
            True

            >>> Null().is_none_or(is_even) == True
            True
        ::
        """
        return True

    def is_some(self) -> bool:
        """.. code-block:: python

            >>> Some(inner=2).is_some() == True
            True

            >>> Null().is_some() == False
            True
        ::
        """
        return False

    def is_some_and(self, fn: Callable[[T], bool]) -> bool:  # noqa: ARG002
        """.. code-block:: python

            >>> Some(inner=1).is_some_and(is_even) == False
            True

            >>> Some(inner=2).is_some_and(is_even) == True
            True

            >>> Null().is_some_and(is_even) == False
            True
        ::
        """
        return False

    def map[U](self, fn: Callable[[T], U]) -> Option[U]:  # noqa: ARG002
        """.. code-block:: python

            >>> Some(inner=1).map(add_one) == Some(inner=2)
            True

            >>> Null().map(add_one) == Null()
            True
        ::
        """
        return self

    def map_or[U](self, default: U, fn: Callable[[T], U]) -> U:  # noqa: ARG002
        return default

    def map_or_else[U](self, default: Callable[..., U], fn: Callable[[T], U]) -> U:  # noqa: ARG002
        return default()

    def ok_or[E](self, err: E) -> Result[T, E]:
        """.. code-block:: python

            >>> Some(inner="foo").ok_or(0) == Ok(inner="foo")
            True

            >>> Null().ok_or(0) == Err(error=0, traceback="")
            True
        ::
        """
        from ._result_v2 import Err, Result  # noqa: PLC0415

        return cast(Result[T, E], Err[E](err))

    def ok_or_else[E](self, err: Callable[[], E]) -> Result[T, E]:
        """.. code-block:: python

            >>> Some(inner="foo").ok_or_else(get_42) == Ok(inner="foo")
            True

            >>> Null().ok_or_else(get_42) == Err(error=42, traceback="")
            True
        ::
        """
        from ._result_v2 import Err, Result  # noqa: PLC0415

        return cast(Result[T, E], Err[E](err()))

    def or_(self, opt_b: Option[T]) -> Option[T]:
        """.. code-block:: python

            >>> Some(inner=2).or_(Null()) == Some(inner=2)
            True

            >>> Null().or_(Some(inner=100)) == Some(inner=100)
            True

            >>> Some(inner=2).or_(Some(inner=100)) == Some(inner=2)
            True

            >>> Null().or_(Null()) == Null()
            True
        ::
        """
        return opt_b

    def or_else(self, opt_b: Callable[[], Option[T]]) -> Option[T]:
        """.. code-block:: python

            >>> Some(inner="barbarians").or_else(get_some_vikings) == Some(inner="barbarians")
            True

            >>> Null().or_else(get_some_vikings) == Some(inner="vikings")
            True

            >>> Null().or_else(Null) == Null()
            True
        ::
        """
        return opt_b()

    def replace(self, value: T) -> Option[T]:  # noqa: ARG002
        """.. code-block:: python

            >>> Some(inner=2).replace(5) == Some(inner=5)
            True

            >>> Null().replace(3) == Null()
            True
        ::
        """
        return self

    def transpose[E](self) -> Result[Option[T], E]:
        """.. code-block:: python

            >>> Some(inner=Ok(inner=2)).transpose() == Ok(inner=Some(inner=2))
            True

            >>> Some(inner=Err(error=2, traceback="")).transpose() == Err(
            ...     error=Some(inner=2), traceback=""
            ... )
            True

            >>> Null().transpose() == Ok(inner=Null())
            True
        ::
        """
        from ._result_v2 import Ok, Result  # noqa: PLC0415

        return cast(Result[Option[T], E], Ok(self))

    def unwrap(self) -> T:
        """.. code-block:: python

            >>> Some(inner=2).unwrap() == 2
            True
        ::
        """
        raise TypeError("Can't call `unwrap` on `Null`")

    def unwrap_or(self, default: T) -> T:
        """.. code-block:: python

            >>> Some(inner="car").unwrap_or("bike") == "car"
            True

            >>> Null().unwrap_or("bike") == "bike"
            True
        ::
        """
        return default

    def unwrap_or_else(self, fn: Callable[[], T]) -> T:
        """.. code-block:: python

            >>> Some(inner=4).unwrap_or_else(get_42) == 4
            True

            >>> Null().unwrap_or_else(get_42) == 42
            True
        ::
        """
        return fn()

    def zip[U](self, other: Option[U]) -> Option[tuple[T, U]]:  # noqa: ARG002
        """.. code-block:: python

            >>> Some(inner=1).zip(Some(inner="hi")) == Some(inner=(1, "hi"))
            True

            >>> Some(inner=1).zip(Null()) == Null()
            True

            >>> Null().zip(Some(inner=1)) == Null()
            True
        ::
        """
        return self

    def unzip[U](self) -> tuple[Option[T], Option[U]]:
        """.. code-block:: python

            >>> Some(inner=(2, 2)).unzip() == (Some(inner=2), Some(inner=2))
            True

            >>> Some(inner=4).unzip() == (Null(), Null())
            True

            >>> Null().unzip() == (Null(), Null())
            True
        ::
        """
        return (Null(), Null())
