from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, Concatenate, Literal, Never, ParamSpec, Self, TypeVar

import attrs

T_co = TypeVar("T_co", covariant=True)
U_co = TypeVar("U_co", covariant=True)
E_co = TypeVar("E_co", bound=object, covariant=True)
F_co = TypeVar("F_co", bound=object, covariant=True)
P = ParamSpec("P")

Mappable = Callable[Concatenate[T_co, P], U_co]
Bindable = Callable[Concatenate[T_co, P], "Either[U_co, E_co]"]


@attrs.define(frozen=True)
class Either[T_co, E_co: object](ABC):
    """``Either`` monad. Consists of ``Right`` and ``Left`` for successful and failed operations respectively.
    Each monad is a frozen instance to prevent further mutation.
    """

    @classmethod
    def unit(cls, inner: T_co) -> Right[T_co]:
        """Unit method. Given an item of type ``T`` return ``Right(T)``

        .. doctest::

            >>> from danom import Left, Right, Either

            >>> Either.unit(0) == Right(inner=0)
            True

            >>> Right.unit(0) == Right(inner=0)
            True

            >>> Left.unit(0) == Right(inner=0)
            True
        """
        return Right(inner)

    @abstractmethod
    def is_ok(self) -> bool:
        """Returns ``True`` if the result type is ``Right``.
        Returns ``False`` if the result type is ``Left``.

        .. doctest::

            >>> from danom import Left, Right

            >>> Right().is_ok() == True
            True

            >>> Left().is_ok() == False
            True
        """
        ...

    @abstractmethod
    def map(self, func: Mappable, *args: P.args, **kwargs: P.kwargs) -> Either[U_co, E_co]:
        """Pipe a pure function and wrap the return value with ``Right``.
        Given an ``Left`` will return ``self``.

        .. code-block:: python

            from danom import Left, Right

            Right(1).map(add_one) == Right(2)
            Left(1).map(add_one) == Left(1)
        """
        ...

    @abstractmethod
    def map_err(self, func: Mappable, *args: P.args, **kwargs: P.kwargs) -> Either[U_co, E_co]:
        """Pipe a pure function and wrap the return value with ``Left``.
        Given an ``Right`` will return ``self``.

        .. code-block:: python

            from danom import Left, Right

            Left(TypeError()).map_err(type_err_to_value_err) == Left(ValueError())
            Right(1).map(type_err_to_value_err) == Right(1)
        """
        ...

    @abstractmethod
    def and_then(self, func: Bindable, *args: P.args, **kwargs: P.kwargs) -> Either[U_co, E_co]:
        """Pipe another function that returns a monad. For ``Left`` will return original inner.

        .. code-block:: python

            from danom import Left, Right

            Right(1).and_then(add_one) == Right(2)
            Right(1).and_then(raise_err) == Left(TypeError())
            Left(TypeError()).and_then(add_one) == Left(TypeError())
            Left(TypeError()).and_then(raise_value_err) == Left(TypeError())
        """
        ...

    @abstractmethod
    def or_else(self, func: Bindable, *args: P.args, **kwargs: P.kwargs) -> Either[U_co, E_co]:
        """Pipe a function that returns a monad to recover from an ``Left``. For ``Right`` will return original ``Either``.

        .. code-block:: python

            from danom import Left, Right

            Right(1).or_else(replace_err_with_zero) == Right(1)
            Left(TypeError()).or_else(replace_err_with_zero) == Right(0)
        """
        ...

    @abstractmethod
    def unwrap(self) -> T_co:
        """Unwrap the `Right` or ``Left`` monad to get the inner value.

        .. doctest::

            >>> from danom import Left, Right

            >>> Right().unwrap() == None
            True

            >>> Right(1).unwrap() == 1
            True

            >>> Right("ok").unwrap() == 'ok'
            True

            >>> Left(-1).unwrap() == -1
            True

        """
        ...

    @staticmethod
    def either_is_ok(result: Either[T_co, E_co]) -> bool:
        """Check whether the monad is ok. Allows for ``filter`` or ``partition`` in a ``Stream`` without needing a lambda or custom function.

        .. code-block:: python

            from danom import Stream, Either

            Stream.from_iterable([Right(), Right(), Left()]).filter(Either.either_is_ok).collect() == (Right(), Right())

        """
        return result.is_ok()

    @staticmethod
    def either_unwrap(result: Either[T_co, E_co]) -> T_co:
        """Unwrap the `Right` or ``Left`` monad to get the inner value.

        .. code-block:: python

            from danom import Stream, Either

            oks, errs = Stream.from_iterable([Right(1), Right(2), Left()]).partition(Either.either_is_ok)
            oks.map(Either.either_unwrap).collect == (1, 2)

        """
        return result.unwrap()


@attrs.define(frozen=True, hash=True)
class Right(Either[T_co, Never]):
    inner: Any = attrs.field(default=None)

    def is_ok(self) -> Literal[True]:
        return True

    def map(self, func: Mappable, *args: P.args, **kwargs: P.kwargs) -> Right[U_co]:
        return Right(func(self.inner, *args, **kwargs))

    def map_err(self, func: Mappable, *args: P.args, **kwargs: P.kwargs) -> Self:  # noqa: ARG002
        return self

    def and_then(self, func: Bindable, *args: P.args, **kwargs: P.kwargs) -> Either[U_co, E_co]:
        return func(self.inner, *args, **kwargs)

    def or_else(self, func: Bindable, *args: P.args, **kwargs: P.kwargs) -> Self:  # noqa: ARG002
        return self

    def unwrap(self) -> T_co:
        return self.inner


@attrs.define(frozen=True, hash=True)
class Left(Either[Never, E_co]):
    inner: Any = attrs.field(default=None)

    def is_ok(self) -> Literal[False]:
        return False

    def map(self, func: Mappable, *args: P.args, **kwargs: P.kwargs) -> Self:  # noqa: ARG002
        return self

    def map_err(self, func: Mappable, *args: P.args, **kwargs: P.kwargs) -> Left[F_co]:
        return Left(func(self.inner, *args, **kwargs))

    def and_then(self, func: Bindable, *args: P.args, **kwargs: P.kwargs) -> Self:  # noqa: ARG002
        return self

    def or_else(self, func: Bindable, *args: P.args, **kwargs: P.kwargs) -> Either[U_co, E_co]:
        return func(self.inner, *args, **kwargs)

    def unwrap(self) -> T_co:
        return self.inner
