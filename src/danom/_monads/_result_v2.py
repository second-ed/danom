from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from copy import deepcopy
from typing import TYPE_CHECKING, Any, Concatenate, Never, cast

import attrs
from attrs.validators import instance_of

if TYPE_CHECKING:
    from ._option import Option


@attrs.define(frozen=True)
class Result[T, E](ABC):
    @classmethod
    def unit(cls, inner: T) -> Result[T, E]:
        """Unit method. Given an item of type ``T`` return ``Ok(T)``

        .. doctest::

            >>> from danom import Err, Ok, Result

            >>> Result.unit(0) == Ok(0)
            True

            >>> Ok.unit(0) == Ok(0)
            True

            >>> Err.unit(0) == Ok(0)
            True
        """
        return cast(Result[T, E], Ok(inner))

    @staticmethod
    def result_is_ok(result: Result[T, E]) -> bool:
        """Check whether the monad is ok. Allows for ``filter`` or ``partition`` in a ``Stream`` without needing a lambda or custom function.

        .. code-block:: python

            from danom import Stream, Result

            Stream.from_iterable([Ok(), Ok(), Err()]).filter(Result.result_is_ok).collect() == (Ok(), Ok())

        """
        return result.is_ok()

    @staticmethod
    def result_unwrap(result: Result[T, E]) -> T:
        """Unwrap the ``Ok`` monad and get the inner value.
        Unwrap the ``Err`` monad will raise the inner error.

        .. code-block:: python

            from danom import Err, Ok, Stream, Result

            oks, errs = Stream.from_iterable([Ok(1), Ok(2), Err()]).partition(Result.result_is_ok)
            oks.map(Result.result_unwrap).collect == (1, 2)

        """
        return result.unwrap()

    @abstractmethod
    def and_[U, F](self, res: Result[U, F]) -> Result[U, F]:
        """.. code-block:: python

            >>> Ok(inner=2).and_(Err(error="late error", traceback="")) == Err(
            ...     error="late error", traceback=""
            ... )
            True

            >>> Err(error="early error", traceback="").and_(Ok(inner="foo")) == Err(
            ...     error="early error", traceback=""
            ... )
            True

            >>> Err(error="not a 2", traceback="").and_(Err(error="late error", traceback="")) == Err(
            ...     error="not a 2", traceback=""
            ... )
            True

            >>> Ok(inner=2).and_(Ok(inner="different result type")) == Ok(inner="different result type")
            True
        ::
        """
        ...

    @abstractmethod
    def and_then[U, F, **P](
        self, fn: Callable[Concatenate[T, P], Result[U, F]], *args: P.args, **kwargs: P.kwargs
    ) -> Result[U, F]:
        """.. code-block:: python

            >>> Ok(inner=2).and_then(must_be_less_than_10) == Ok(inner=2)
            True

            >>> Ok(inner=20).and_then(must_be_less_than_10) == Err(error="too high", traceback="")
            True

            >>> Err(error="not a number", traceback="").and_then(must_be_less_than_10) == Err(
            ...     error="not a number", traceback=""
            ... )
            True
        ::
        """
        ...

    def cloned(self) -> Result[T, E]:
        """.. code-block:: python

            >>> Ok(inner=2).cloned() == Ok(inner=2)
            True

            >>> Err(error=2, traceback="").cloned() == Err(error=2, traceback="")
            True
        ::
        """
        return deepcopy(self)

    @abstractmethod
    def err(self) -> Option[E]:
        """.. code-block:: python

            >>> Ok(inner=2).err() == Null()
            True

            >>> Err(error="Nothing here", traceback="").err() == Some(inner="Nothing here")
            True
        ::
        """
        ...

    @abstractmethod
    def expect(self, msg: str) -> T:
        """.. code-block:: python

            >>> Ok(inner=2).expect("must be positive") == 2
            True
        ::
        """
        ...

    @abstractmethod
    def expect_err(self, msg: str) -> E:
        """.. code-block:: python

            >>> Err(error=2, traceback="").expect_err("must be err") == 2
            True
        ::
        """
        ...

    @abstractmethod
    def flatten(self) -> Result[T, E]:
        """.. code-block:: python

            >>> Ok(inner=Ok(inner=Ok(inner=2))).flatten() == Ok(inner=Ok(inner=2))
            True

            >>> Ok(inner=Ok(inner=2)).flatten() == Ok(inner=2)
            True

            >>> Ok(inner=2).flatten() == Ok(inner=2)
            True

            >>> Err(error=None, traceback="").flatten() == Err(error=None, traceback="")
            True
        ::
        """
        ...

    @abstractmethod
    def inspect(self, fn: Callable[[T], None]) -> Result[T, E]:
        """.. code-block:: python

            >>> Ok(inner=[1]).inspect(append_to_list) == Ok(inner=[1])
            True

            >>> Err(error="un-appendable", traceback="").inspect(append_to_list) == Err(
            ...     error="un-appendable", traceback=""
            ... )
            True
        ::
        """
        ...

    @abstractmethod
    def inspect_err(self, fn: Callable[[E], None]) -> Result[T, E]:
        """.. code-block:: python

            >>> Err(error=[1], traceback="").inspect_err(append_to_list) == Err(error=[1], traceback="")
            True

            >>> Ok(inner="un-appendable").inspect_err(append_to_list) == Ok(inner="un-appendable")
            True
        ::
        """
        ...

    @abstractmethod
    def is_err(self) -> bool:
        """.. code-block:: python

            >>> Ok(inner=2).is_err() == False
            True

            >>> Err(error=2, traceback="").is_err() == True
            True
        ::
        """
        ...

    @abstractmethod
    def is_err_and(self, fn: Callable[[E], bool]) -> bool:
        """.. code-block:: python

            >>> Err(error=1, traceback="").is_err_and(is_even) == False
            True

            >>> Err(error=2, traceback="").is_err_and(is_even) == True
            True

            >>> Ok(inner=2).is_err_and(is_even) == False
            True
        ::
        """
        ...

    @abstractmethod
    def is_ok(self) -> bool:
        """.. code-block:: python

            >>> Ok(inner=2).is_ok() == True
            True

            >>> Err(error=2, traceback="").is_ok() == False
            True
        ::
        """
        ...

    @abstractmethod
    def is_ok_and(self, fn: Callable[[T], bool]) -> bool:
        """.. code-block:: python

            >>> Ok(inner=1).is_ok_and(is_even) == False
            True

            >>> Ok(inner=2).is_ok_and(is_even) == True
            True

            >>> Err(error=2, traceback="").is_ok_and(is_even) == False
            True
        ::
        """
        ...

    @abstractmethod
    def map[U, **P](
        self, fn: Callable[Concatenate[T, P], U], *args: P.args, **kwargs: P.kwargs
    ) -> Result[U, E]:
        """.. code-block:: python

            >>> Ok(inner=1).map(add_one) == Ok(inner=2)
            True

            >>> Err(error=1, traceback="").map(add_one) == Err(error=1, traceback="")
            True
        ::
        """
        ...

    @abstractmethod
    def map_err[F, **P](
        self, fn: Callable[Concatenate[E, P], F], *args: P.args, **kwargs: P.kwargs
    ) -> Result[T, F]:
        """.. code-block:: python

            >>> Err(error=1, traceback="").map_err(add_one) == Err(error=2, traceback="")
            True

            >>> Ok(inner=1).map_err(add_one) == Ok(inner=1)
            True
        ::
        """
        ...

    @abstractmethod
    def map_or[U, **P](
        self, default: U, fn: Callable[Concatenate[T, P], U], *args: P.args, **kwargs: P.kwargs
    ) -> U: ...

    @abstractmethod
    def map_or_else[U, **P](
        self,
        default: Callable[P, U],
        fn: Callable[Concatenate[T, P], U],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> U: ...

    @abstractmethod
    def ok(self) -> Option[T]:
        """.. code-block:: python

            >>> Ok(inner=2).ok() == Some(inner=2)
            True

            >>> Err(error=2, traceback="").ok() == Null()
            True
        ::
        """
        ...

    @abstractmethod
    def or_[F](self, res: Result[T, F]) -> Result[T, F]:
        """.. code-block:: python

            >>> Ok(inner=2).or_(Err(error="foo", traceback="")) == Ok(inner=2)
            True

            >>> Err(error="foo", traceback="").or_(Ok(inner=100)) == Ok(inner=100)
            True

            >>> Ok(inner=2).or_(Ok(inner=100)) == Ok(inner=2)
            True

            >>> Err(error="foo", traceback="").or_(Err(error="foo", traceback="")) == Err(
            ...     error="foo", traceback=""
            ... )
            True
        ::
        """
        ...

    @abstractmethod
    def or_else[F, **P](
        self, fn: Callable[Concatenate[E, P], F], *args: P.args, **kwargs: P.kwargs
    ) -> Result[T, F]:
        """.. code-block:: python

            >>> Ok(inner="barbarians").or_else(get_ok_vikings) == Ok(inner="barbarians")
            True

            >>> Err(error="foo", traceback="").or_else(get_ok_vikings) == Ok(inner="vikings")
            True

            >>> Err(error="foo", traceback="").or_else(Err) == Err(error="foo", traceback="")
            True
        ::
        """
        ...

    @abstractmethod
    def transpose(self) -> Option[Result[T, E]]:
        """.. code-block:: python

            >>> Ok(inner=Some(inner=5)).transpose() == Some(inner=Ok(inner=5))
            True

            >>> Ok(inner=Null()).transpose() == Null()
            True

            >>> Err(error=None, traceback="").transpose() == Some(inner=Err(error=None, traceback=""))
            True
        ::
        """
        ...

    @abstractmethod
    def unwrap(self) -> T:
        """.. code-block:: python

            >>> Ok(inner=2).unwrap() == 2
            True
        ::
        """
        ...

    @abstractmethod
    def unwrap_err(self) -> E:
        """.. code-block:: python

            >>> Err(error="failed", traceback="").unwrap_err() == "failed"
            True
        ::
        """
        ...

    @abstractmethod
    def unwrap_or(self, default: T) -> T:
        """.. code-block:: python

            >>> Ok(inner="car").unwrap_or("bike") == "car"
            True

            >>> Err(error=None, traceback="").unwrap_or("bike") == "bike"
            True
        ::
        """
        ...

    @abstractmethod
    def unwrap_or_else(self, fn: Callable[[E], T]) -> T:
        """.. code-block:: python

            >>> Ok(inner=4).unwrap_or_else(get_42) == 4
            True

            >>> Err(error=None, traceback="").unwrap_or_else(get_42) == 42
            True
        ::
        """
        ...


@attrs.define(frozen=True)
class Ok[T](Result[T, Never]):
    inner: T = attrs.field(default=None)

    def and_[U, E](self, res: Result[U, E]) -> Result[U, E]:
        """.. code-block:: python

            >>> Ok(inner=2).and_(Err(error="late error", traceback="")) == Err(
            ...     error="late error", traceback=""
            ... )
            True

            >>> Err(error="early error", traceback="").and_(Ok(inner="foo")) == Err(
            ...     error="early error", traceback=""
            ... )
            True

            >>> Err(error="not a 2", traceback="").and_(Err(error="late error", traceback="")) == Err(
            ...     error="not a 2", traceback=""
            ... )
            True

            >>> Ok(inner=2).and_(Ok(inner="different result type")) == Ok(inner="different result type")
            True
        ::
        """
        return res

    def and_then[U, E, **P](
        self, fn: Callable[Concatenate[T, P], Result[U, E]], *args: P.args, **kwargs: P.kwargs
    ) -> Result[U, E]:
        """.. code-block:: python

            >>> Ok(inner=2).and_then(must_be_less_than_10) == Ok(inner=2)
            True

            >>> Ok(inner=20).and_then(must_be_less_than_10) == Err(error="too high", traceback="")
            True

            >>> Err(error="not a number", traceback="").and_then(must_be_less_than_10) == Err(
            ...     error="not a number", traceback=""
            ... )
            True
        ::
        """
        return fn(self.inner, *args, **kwargs)

    def err[E](self) -> Option[E]:
        """.. code-block:: python

            >>> Ok(inner=2).err() == Null()
            True

            >>> Err(error="Nothing here", traceback="").err() == Some(inner="Nothing here")
            True
        ::
        """
        from ._option import Null  # noqa: PLC0415

        return Null()

    def expect(self, msg: str) -> T:  # noqa: ARG002
        """.. code-block:: python

            >>> Ok(inner=2).expect("must be positive") == 2
            True
        ::
        """
        return self.inner

    def expect_err(self, msg: str) -> Never:
        """.. code-block:: python

            >>> Err(error=2, traceback="").expect_err("must be err") == 2
            True
        ::
        """
        raise ValueError(msg)

    def flatten(self) -> Result[T, Never]:
        """.. code-block:: python

            >>> Ok(inner=Ok(inner=Ok(inner=2))).flatten() == Ok(inner=Ok(inner=2))
            True

            >>> Ok(inner=Ok(inner=2)).flatten() == Ok(inner=2)
            True

            >>> Ok(inner=2).flatten() == Ok(inner=2)
            True

            >>> Err(error=None, traceback="").flatten() == Err(error=None, traceback="")
            True
        ::
        """
        if isinstance(self.inner, Result):
            return cast(Result[T, Never], self.inner)
        return cast(Result[T, Never], self)

    def inspect(self, fn: Callable[[T], None]) -> Result[T, Never]:
        """.. code-block:: python

            >>> Ok(inner=[1]).inspect(append_to_list) == Ok(inner=[1])
            True

            >>> Err(error="un-appendable", traceback="").inspect(append_to_list) == Err(
            ...     error="un-appendable", traceback=""
            ... )
            True
        ::
        """
        fn(deepcopy(self.inner))
        return self

    def inspect_err(self, fn: Callable[[Never], None]) -> Result[T, Never]:  # noqa: ARG002
        """.. code-block:: python

            >>> Err(error=[1], traceback="").inspect_err(append_to_list) == Err(error=[1], traceback="")
            True

            >>> Ok(inner="un-appendable").inspect_err(append_to_list) == Ok(inner="un-appendable")
            True
        ::
        """
        return self

    def is_err(self) -> bool:
        """.. code-block:: python

            >>> Ok(inner=2).is_err() == False
            True

            >>> Err(error=2, traceback="").is_err() == True
            True
        ::
        """
        return False

    def is_err_and(self, fn: Callable[[Never], bool]) -> bool:  # noqa: ARG002
        """.. code-block:: python

            >>> Err(error=1, traceback="").is_err_and(is_even) == False
            True

            >>> Err(error=2, traceback="").is_err_and(is_even) == True
            True

            >>> Ok(inner=2).is_err_and(is_even) == False
            True
        ::
        """
        return False

    def is_ok(self) -> bool:
        """.. code-block:: python

            >>> Ok(inner=2).is_ok() == True
            True

            >>> Err(error=2, traceback="").is_ok() == False
            True
        ::
        """
        return True

    def is_ok_and(self, fn: Callable[[T], bool]) -> bool:
        """.. code-block:: python

            >>> Ok(inner=1).is_ok_and(is_even) == False
            True

            >>> Ok(inner=2).is_ok_and(is_even) == True
            True

            >>> Err(error=2, traceback="").is_ok_and(is_even) == False
            True
        ::
        """
        return fn(self.inner)

    def map[U, **P](
        self, fn: Callable[Concatenate[T, P], U], *args: P.args, **kwargs: P.kwargs
    ) -> Result[U, Never]:
        """.. code-block:: python

            >>> Ok(inner=1).map(add_one) == Ok(inner=2)
            True

            >>> Err(error=1, traceback="").map(add_one) == Err(error=1, traceback="")
            True
        ::
        """
        return Ok(fn(self.inner, *args, **kwargs))

    def map_err[F, **P](
        self,
        fn: Callable[Concatenate[Never, P], F],  # noqa: ARG002
        *args: P.args,  # noqa: ARG002
        **kwargs: P.kwargs,  # noqa: ARG002
    ) -> Result[T, F]:
        """.. code-block:: python

            >>> Err(error=1, traceback="").map_err(add_one) == Err(error=2, traceback="")
            True

            >>> Ok(inner=1).map_err(add_one) == Ok(inner=1)
            True
        ::
        """
        return cast(Result[T, F], self)

    def map_or[U, **P](
        self,
        default: U,  # noqa: ARG002
        fn: Callable[Concatenate[T, P], U],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> U:
        return fn(self.inner, *args, **kwargs)

    def map_or_else[U, **P](
        self,
        default: Callable[P, U],  # noqa: ARG002
        fn: Callable[Concatenate[T, P], U],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> U:
        return fn(self.inner, *args, **kwargs)

    def ok(self) -> Option[T]:
        """.. code-block:: python

            >>> Ok(inner=2).ok() == Some(inner=2)
            True

            >>> Err(error=2, traceback="").ok() == Null()
            True
        ::
        """
        from ._option import Some  # noqa: PLC0415

        return Some(self.inner)

    def or_[F](self, res: Result[T, F]) -> Result[T, F]:  # noqa: ARG002
        """.. code-block:: python

            >>> Ok(inner=2).or_(Err(error="foo", traceback="")) == Ok(inner=2)
            True

            >>> Err(error="foo", traceback="").or_(Ok(inner=100)) == Ok(inner=100)
            True

            >>> Ok(inner=2).or_(Ok(inner=100)) == Ok(inner=2)
            True

            >>> Err(error="foo", traceback="").or_(Err(error="foo", traceback="")) == Err(
            ...     error="foo", traceback=""
            ... )
            True
        ::
        """
        return cast(Result[T, F], self)

    def or_else[F, **P](
        self,
        fn: Callable[Concatenate[Never, P], F],  # noqa: ARG002
        *args: P.args,  # noqa: ARG002
        **kwargs: P.kwargs,  # noqa: ARG002
    ) -> Result[T, F]:
        """.. code-block:: python

            >>> Ok(inner="barbarians").or_else(get_ok_vikings) == Ok(inner="barbarians")
            True

            >>> Err(error="foo", traceback="").or_else(get_ok_vikings) == Ok(inner="vikings")
            True

            >>> Err(error="foo", traceback="").or_else(Err) == Err(error="foo", traceback="")
            True
        ::
        """
        return cast(Result[T, F], self)

    def transpose(self) -> Option[Result[T, Never]]:
        """.. code-block:: python

            >>> Ok(inner=Some(inner=5)).transpose() == Some(inner=Ok(inner=5))
            True

            >>> Ok(inner=Null()).transpose() == Null()
            True

            >>> Err(error=None, traceback="").transpose() == Some(inner=Err(error=None, traceback=""))
            True
        ::
        """
        from ._option import Null, Some  # noqa: PLC0415

        if isinstance(self.inner, Some):
            return Some(Ok(self.inner.inner))
        if isinstance(self.inner, Null):
            return Null()
        raise TypeError("inner must be an `Option` type")

    def unwrap(self) -> T:
        """.. code-block:: python

            >>> Ok(inner=2).unwrap() == 2
            True
        ::
        """
        return self.inner

    def unwrap_err(self) -> Never:
        """.. code-block:: python

            >>> Err(error="failed", traceback="").unwrap_err() == "failed"
            True
        ::
        """
        raise TypeError("Can't call `unwrap_err` on `Ok`")

    def unwrap_or(self, default: T) -> T:  # noqa: ARG002
        """.. code-block:: python

            >>> Ok(inner="car").unwrap_or("bike") == "car"
            True

            >>> Err(error=None, traceback="").unwrap_or("bike") == "bike"
            True
        ::
        """
        return self.inner

    def unwrap_or_else(self, fn: Callable[[Never], T]) -> T:  # noqa: ARG002
        """.. code-block:: python

            >>> Ok(inner=4).unwrap_or_else(get_42) == 4
            True

            >>> Err(error=None, traceback="").unwrap_or_else(get_42) == 42
            True
        ::
        """
        return self.inner


SafeArgs = tuple[tuple[Any, ...], dict[str, Any]]
SafeMethodArgs = tuple[object, tuple[Any, ...], dict[str, Any]]


@attrs.define(frozen=True)
class Err[E](Result[Never, E]):
    error: E = attrs.field(default=None)
    input_args: tuple[()] | SafeArgs | SafeMethodArgs = attrs.field(
        default=(), validator=instance_of(tuple), repr=False
    )
    traceback: str = attrs.field(default="", validator=instance_of(str))

    def and_[U, F](self, res: Result[U, F]) -> Result[U, F]:  # noqa: ARG002
        """.. code-block:: python

            >>> Ok(inner=2).and_(Err(error="late error", traceback="")) == Err(
            ...     error="late error", traceback=""
            ... )
            True

            >>> Err(error="early error", traceback="").and_(Ok(inner="foo")) == Err(
            ...     error="early error", traceback=""
            ... )
            True

            >>> Err(error="not a 2", traceback="").and_(Err(error="late error", traceback="")) == Err(
            ...     error="not a 2", traceback=""
            ... )
            True

            >>> Ok(inner=2).and_(Ok(inner="different result type")) == Ok(inner="different result type")
            True
        ::
        """
        return cast(Result[U, F], self)

    def and_then[U, F, **P](
        self,
        fn: Callable[Concatenate[Never, P], Result[U, F]],  # noqa: ARG002
        *args: P.args,  # noqa: ARG002
        **kwargs: P.kwargs,  # noqa: ARG002
    ) -> Result[U, F]:
        """.. code-block:: python

            >>> Ok(inner=2).and_then(must_be_less_than_10) == Ok(inner=2)
            True

            >>> Ok(inner=20).and_then(must_be_less_than_10) == Err(error="too high", traceback="")
            True

            >>> Err(error="not a number", traceback="").and_then(must_be_less_than_10) == Err(
            ...     error="not a number", traceback=""
            ... )
            True
        ::
        """
        return cast(Result[U, F], self)

    def err(self) -> Option[E]:
        """.. code-block:: python

            >>> Ok(inner=2).err() == Null()
            True

            >>> Err(error="Nothing here", traceback="").err() == Some(inner="Nothing here")
            True
        ::
        """
        from ._option import Some  # noqa: PLC0415

        return Some(self.error)

    def expect(self, msg: str) -> Never:
        """.. code-block:: python

            >>> Ok(inner=2).expect("must be positive") == 2
            True
        ::
        """
        raise ValueError(msg)

    def expect_err(self, msg: str) -> E:  # noqa: ARG002
        """.. code-block:: python

            >>> Err(error=2, traceback="").expect_err("must be err") == 2
            True
        ::
        """
        return self.error

    def flatten(self) -> Result[Never, E]:
        """.. code-block:: python

            >>> Ok(inner=Ok(inner=Ok(inner=2))).flatten() == Ok(inner=Ok(inner=2))
            True

            >>> Ok(inner=Ok(inner=2)).flatten() == Ok(inner=2)
            True

            >>> Ok(inner=2).flatten() == Ok(inner=2)
            True

            >>> Err(error=None, traceback="").flatten() == Err(error=None, traceback="")
            True
        ::
        """
        return self

    def inspect(self, fn: Callable[[Never], None]) -> Result[Never, E]:  # noqa: ARG002
        """.. code-block:: python

            >>> Ok(inner=[1]).inspect(append_to_list) == Ok(inner=[1])
            True

            >>> Err(error="un-appendable", traceback="").inspect(append_to_list) == Err(
            ...     error="un-appendable", traceback=""
            ... )
            True
        ::
        """
        return self

    def inspect_err(self, fn: Callable[[E], None]) -> Result[Never, E]:
        """.. code-block:: python

            >>> Err(error=[1], traceback="").inspect_err(append_to_list) == Err(error=[1], traceback="")
            True

            >>> Ok(inner="un-appendable").inspect_err(append_to_list) == Ok(inner="un-appendable")
            True
        ::
        """
        fn(deepcopy(self.error))
        return self

    def is_err(self) -> bool:
        """.. code-block:: python

            >>> Ok(inner=2).is_err() == False
            True

            >>> Err(error=2, traceback="").is_err() == True
            True
        ::
        """
        return True

    def is_err_and(self, fn: Callable[[E], bool]) -> bool:
        """.. code-block:: python

            >>> Err(error=1, traceback="").is_err_and(is_even) == False
            True

            >>> Err(error=2, traceback="").is_err_and(is_even) == True
            True

            >>> Ok(inner=2).is_err_and(is_even) == False
            True
        ::
        """
        return fn(self.error)

    def is_ok(self) -> bool:
        """.. code-block:: python

            >>> Ok(inner=2).is_ok() == True
            True

            >>> Err(error=2, traceback="").is_ok() == False
            True
        ::
        """
        return False

    def is_ok_and(self, fn: Callable[[Never], bool]) -> bool:  # noqa: ARG002
        """.. code-block:: python

            >>> Ok(inner=1).is_ok_and(is_even) == False
            True

            >>> Ok(inner=2).is_ok_and(is_even) == True
            True

            >>> Err(error=2, traceback="").is_ok_and(is_even) == False
            True
        ::
        """
        return False

    def map[U, **P](
        self,
        fn: Callable[Concatenate[Never, P], U],  # noqa: ARG002
        *args: P.args,  # noqa: ARG002
        **kwargs: P.kwargs,  # noqa: ARG002
    ) -> Result[U, E]:
        """.. code-block:: python

            >>> Ok(inner=1).map(add_one) == Ok(inner=2)
            True

            >>> Err(error=1, traceback="").map(add_one) == Err(error=1, traceback="")
            True
        ::
        """
        return cast(Result[U, E], self)

    def map_err[F, **P](
        self, fn: Callable[Concatenate[E, P], F], *args: P.args, **kwargs: P.kwargs
    ) -> Result[Never, F]:
        """.. code-block:: python

            >>> Err(error=1, traceback="").map_err(add_one) == Err(error=2, traceback="")
            True

            >>> Ok(inner=1).map_err(add_one) == Ok(inner=1)
            True
        ::
        """
        return Err(
            fn(self.error, *args, **kwargs), input_args=self.input_args, traceback=self.traceback
        )

    def map_or[U, **P](
        self,
        default: U,
        fn: Callable[Concatenate[Never, P], U],  # noqa: ARG002
        *args: P.args,  # noqa: ARG002
        **kwargs: P.kwargs,  # noqa: ARG002
    ) -> U:
        return default

    def map_or_else[U, **P](
        self,
        default: Callable[P, U],
        fn: Callable[Concatenate[Never, P], U],  # noqa: ARG002
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> U:
        return default(*args, **kwargs)

    def ok(self) -> Option[Never]:
        """.. code-block:: python

            >>> Ok(inner=2).ok() == Some(inner=2)
            True

            >>> Err(error=2, traceback="").ok() == Null()
            True
        ::
        """
        from ._option import Null  # noqa: PLC0415

        return Null()

    def or_[F](self, res: Result[Never, F]) -> Result[Never, F]:
        """.. code-block:: python

            >>> Ok(inner=2).or_(Err(error="foo", traceback="")) == Ok(inner=2)
            True

            >>> Err(error="foo", traceback="").or_(Ok(inner=100)) == Ok(inner=100)
            True

            >>> Ok(inner=2).or_(Ok(inner=100)) == Ok(inner=2)
            True

            >>> Err(error="foo", traceback="").or_(Err(error="foo", traceback="")) == Err(
            ...     error="foo", traceback=""
            ... )
            True
        ::
        """
        return res

    def or_else[F, **P](
        self, fn: Callable[Concatenate[E, P], F], *args: P.args, **kwargs: P.kwargs
    ) -> Result[Never, F]:
        """.. code-block:: python

            >>> Ok(inner="barbarians").or_else(get_ok_vikings) == Ok(inner="barbarians")
            True

            >>> Err(error="foo", traceback="").or_else(get_ok_vikings) == Ok(inner="vikings")
            True

            >>> Err(error="foo", traceback="").or_else(Err) == Err(error="foo", traceback="")
            True
        ::
        """
        return cast(Result[Never, F], fn(self.error, *args, **kwargs))

    def transpose(self) -> Option[Result[Never, E]]:
        """.. code-block:: python

            >>> Ok(inner=Some(inner=5)).transpose() == Some(inner=Ok(inner=5))
            True

            >>> Ok(inner=Null()).transpose() == Null()
            True

            >>> Err(error=None, traceback="").transpose() == Some(inner=Err(error=None, traceback=""))
            True
        ::
        """
        from ._option import Some  # noqa: PLC0415

        return Some(self)

    def unwrap(self) -> Never:
        """.. code-block:: python

            >>> Ok(inner=2).unwrap() == 2
            True
        ::
        """
        if isinstance(self.error, Exception):
            raise self.error
        raise TypeError("Can't call `unwrap` on `Err`")

    def unwrap_err(self) -> E:
        """.. code-block:: python

            >>> Err(error="failed", traceback="").unwrap_err() == "failed"
            True
        ::
        """
        return self.error

    def unwrap_or[U](self, default: U) -> U:
        """.. code-block:: python

            >>> Ok(inner="car").unwrap_or("bike") == "car"
            True

            >>> Err(error=None, traceback="").unwrap_or("bike") == "bike"
            True
        ::
        """
        return default

    def unwrap_or_else[U](self, fn: Callable[[E], U]) -> U:
        """.. code-block:: python

            >>> Ok(inner=4).unwrap_or_else(get_42) == 4
            True

            >>> Err(error=None, traceback="").unwrap_or_else(get_42) == 42
            True
        ::
        """
        return fn(self.error)
