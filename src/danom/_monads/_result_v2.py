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
    def and_[U, F](self, res: Result[U, F]) -> Result[U, F]: ...

    @abstractmethod
    def and_then[U, F, **P](
        self, fn: Callable[Concatenate[T, P], Result[U, F]], *args: P.args, **kwargs: P.kwargs
    ) -> Result[U, F]: ...

    def cloned(self) -> Result[T, E]:
        return deepcopy(self)

    @abstractmethod
    def err(self) -> Option[E]: ...

    @abstractmethod
    def expect(self, msg: str) -> T: ...

    @abstractmethod
    def expect_err(self, msg: str) -> E: ...

    @abstractmethod
    def flatten(self) -> Result[T, E]: ...

    @abstractmethod
    def inspect(self, fn: Callable[[T], None]) -> Result[T, E]: ...

    @abstractmethod
    def inspect_err(self, fn: Callable[[E], None]) -> Result[T, E]: ...

    @abstractmethod
    def is_err(self) -> bool: ...

    @abstractmethod
    def is_err_and(self, fn: Callable[[E], bool]) -> bool: ...

    @abstractmethod
    def is_ok(self) -> bool: ...

    @abstractmethod
    def is_ok_and(self, fn: Callable[[T], bool]) -> bool: ...

    @abstractmethod
    def map[U, **P](
        self, fn: Callable[Concatenate[T, P], U], *args: P.args, **kwargs: P.kwargs
    ) -> Result[U, E]: ...

    @abstractmethod
    def map_err[F, **P](
        self, fn: Callable[Concatenate[E, P], F], *args: P.args, **kwargs: P.kwargs
    ) -> Result[T, F]: ...

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
    def ok(self) -> Option[T]: ...

    @abstractmethod
    def or_[F](self, res: Result[T, F]) -> Result[T, F]: ...

    @abstractmethod
    def or_else[F, **P](
        self, fn: Callable[Concatenate[E, P], F], *args: P.args, **kwargs: P.kwargs
    ) -> Result[T, F]: ...

    @abstractmethod
    def transpose(self) -> Option[Result[T, E]]: ...

    @abstractmethod
    def unwrap(self) -> T: ...

    @abstractmethod
    def unwrap_err(self) -> E: ...

    @abstractmethod
    def unwrap_or(self, default: T) -> T: ...

    @abstractmethod
    def unwrap_or_else(self, fn: Callable[[E], T]) -> T: ...


@attrs.define(frozen=True)
class Ok[T](Result[T, Never]):
    inner: T = attrs.field(default=None)

    def and_[U, E](self, res: Result[U, E]) -> Result[U, E]:
        return res

    def and_then[U, E, **P](
        self, fn: Callable[Concatenate[T, P], Result[U, E]], *args: P.args, **kwargs: P.kwargs
    ) -> Result[U, E]:
        return fn(self.inner, *args, **kwargs)

    def err[E](self) -> Option[E]:
        from ._option import Null  # noqa: PLC0415

        return Null()

    def expect(self, msg: str) -> T:  # noqa: ARG002
        return self.inner

    def expect_err(self, msg: str) -> Never:
        raise ValueError(msg)

    def flatten(self) -> Result[T, Never]:
        if isinstance(self.inner, Result):
            return cast(Result[T, Never], self.inner)
        return cast(Result[T, Never], self)

    def inspect(self, fn: Callable[[T], None]) -> Result[T, Never]:
        fn(deepcopy(self.inner))
        return self

    def inspect_err(self, fn: Callable[[Never], None]) -> Result[T, Never]:  # noqa: ARG002
        return self

    def is_err(self) -> bool:
        return False

    def is_err_and(self, fn: Callable[[Never], bool]) -> bool:  # noqa: ARG002
        return False

    def is_ok(self) -> bool:
        return True

    def is_ok_and(self, fn: Callable[[T], bool]) -> bool:
        return fn(self.inner)

    def map[U, **P](
        self, fn: Callable[Concatenate[T, P], U], *args: P.args, **kwargs: P.kwargs
    ) -> Result[U, Never]:
        return Ok(fn(self.inner, *args, **kwargs))

    def map_err[F, **P](
        self,
        fn: Callable[Concatenate[Never, P], F],  # noqa: ARG002
        *args: P.args,  # noqa: ARG002
        **kwargs: P.kwargs,  # noqa: ARG002
    ) -> Result[T, F]:
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
        from ._option import Some  # noqa: PLC0415

        return Some(self.inner)

    def or_[F](self, res: Result[T, F]) -> Result[T, F]:  # noqa: ARG002
        return cast(Result[T, F], self)

    def or_else[F, **P](
        self,
        fn: Callable[Concatenate[Never, P], F],  # noqa: ARG002
        *args: P.args,  # noqa: ARG002
        **kwargs: P.kwargs,  # noqa: ARG002
    ) -> Result[T, F]:
        return cast(Result[T, F], self)

    def transpose(self) -> Option[Result[T, Never]]:
        from ._option import Null, Some  # noqa: PLC0415

        if isinstance(self.inner, Some):
            return Some(Ok(self.inner.inner))
        if isinstance(self.inner, Null):
            return Null()
        raise TypeError("inner must be an `Option` type")

    def unwrap(self) -> T:
        return self.inner

    def unwrap_err(self) -> Never:
        raise TypeError("Can't call `unwrap_err` on `Ok`")

    def unwrap_or(self, default: T) -> T:  # noqa: ARG002
        return self.inner

    def unwrap_or_else(self, fn: Callable[[Never], T]) -> T:  # noqa: ARG002
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
        return cast(Result[U, F], self)

    def and_then[U, F, **P](
        self,
        fn: Callable[Concatenate[Never, P], Result[U, F]],  # noqa: ARG002
        *args: P.args,  # noqa: ARG002
        **kwargs: P.kwargs,  # noqa: ARG002
    ) -> Result[U, F]:
        return cast(Result[U, F], self)

    def err(self) -> Option[E]:
        from ._option import Some  # noqa: PLC0415

        return Some(self.error)

    def expect(self, msg: str) -> Never:
        raise ValueError(msg)

    def expect_err(self, msg: str) -> E:  # noqa: ARG002
        return self.error

    def flatten(self) -> Result[Never, E]:
        return self

    def inspect(self, fn: Callable[[Never], None]) -> Result[Never, E]:  # noqa: ARG002
        return self

    def inspect_err(self, fn: Callable[[E], None]) -> Result[Never, E]:
        fn(deepcopy(self.error))
        return self

    def is_err(self) -> bool:
        return True

    def is_err_and(self, fn: Callable[[E], bool]) -> bool:
        return fn(self.error)

    def is_ok(self) -> bool:
        return False

    def is_ok_and(self, fn: Callable[[Never], bool]) -> bool:  # noqa: ARG002
        return False

    def map[U, **P](
        self,
        fn: Callable[Concatenate[Never, P], U],  # noqa: ARG002
        *args: P.args,  # noqa: ARG002
        **kwargs: P.kwargs,  # noqa: ARG002
    ) -> Result[U, E]:
        return cast(Result[U, E], self)

    def map_err[F, **P](
        self, fn: Callable[Concatenate[E, P], F], *args: P.args, **kwargs: P.kwargs
    ) -> Result[Never, F]:
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
        from ._option import Null  # noqa: PLC0415

        return Null()

    def or_[F](self, res: Result[Never, F]) -> Result[Never, F]:
        return res

    def or_else[F, **P](
        self, fn: Callable[Concatenate[E, P], F], *args: P.args, **kwargs: P.kwargs
    ) -> Result[Never, F]:
        return cast(Result[Never, F], fn(self.error, *args, **kwargs))

    def transpose(self) -> Option[Result[Never, E]]:
        from ._option import Some  # noqa: PLC0415

        return Some(self)

    def unwrap(self) -> Never:
        if isinstance(self.error, Exception):
            raise self.error
        raise TypeError("Can't call `unwrap` on `Err`")

    def unwrap_err(self) -> E:
        return self.error

    def unwrap_or[U](self, default: U) -> U:
        return default

    def unwrap_or_else[U](self, fn: Callable[[E], U]) -> U:
        return fn(self.error)
