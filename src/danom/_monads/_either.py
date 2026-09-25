"""Either monad probably the better implementation out of this and Result

repo-map-desc: A simple Either monad, includes the base Either, Right and Left.
"""

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

    inner: Any = attrs.field(default=None)

    @classmethod
    def unit(cls, inner: T_co) -> Right[T_co]:
        """Unit method. Given an item of type ``T`` return ``Right(T)``"""
        return Right(inner)

    @abstractmethod
    def is_ok(self) -> bool:
        """Returns ``True`` if the result type is ``Right``.
        Returns ``False`` if the result type is ``Left``.


        .. code-block:: python

            >>> Right(inner=None).is_ok() == True
            True

            >>> Left(inner=None).is_ok() == False
            True
        ::
        """
        ...

    @abstractmethod
    def map(self, func: Mappable, *args: P.args, **kwargs: P.kwargs) -> Either[U_co, E_co]:
        """Pipe a pure function and wrap the return value with ``Right``.
        Given an ``Left`` will return ``self``.


        .. code-block:: python

            >>> Right(inner=0).map(add_one) == Right(inner=1)
            True

            >>> Left(inner=None).map(add_one) == Left(inner=None)
            True
        ::
        """
        ...

    @abstractmethod
    def map_err(self, func: Mappable, *args: P.args, **kwargs: P.kwargs) -> Either[U_co, E_co]:
        """Pipe a pure function and wrap the return value with ``Left``.
        Given an ``Right`` will return ``self``.


        .. code-block:: python

            >>> Right(inner=0).map_err(add_one) == Right(inner=0)
            True

            >>> Left(inner=0).map_err(add_one) == Left(inner=1)
            True
        ::
        """
        ...

    @abstractmethod
    def and_then(self, func: Bindable, *args: P.args, **kwargs: P.kwargs) -> Either[U_co, E_co]:
        """Pipe another function that returns a monad. For ``Left`` will return original inner."""
        ...

    @abstractmethod
    def or_else(self, func: Bindable, *args: P.args, **kwargs: P.kwargs) -> Either[U_co, E_co]:
        """Pipe a function that returns a monad to recover from an ``Left``. For ``Right`` will return original ``Either``."""
        ...

    @abstractmethod
    def unwrap(self) -> T_co:
        """Unwrap the `Right` or ``Left`` monad to get the inner value."""
        ...

    @staticmethod
    def either_is_ok(result: Either[T_co, E_co]) -> bool:
        """Check whether the monad is ok. Allows for ``filter`` or ``partition`` in a ``Stream`` without needing a lambda or custom function."""
        return result.is_ok()

    @staticmethod
    def either_unwrap(result: Either[T_co, E_co]) -> T_co:
        """Unwrap the `Right` or ``Left`` monad to get the inner value."""
        return result.unwrap()

    def flatten(self) -> Either[T_co, E_co]:
        """Flatten the monad. Will return the first ``Left`` or the lowest ``Right`` instance.



        .. code-block:: python

            >>> Right(inner=Right(inner=None)).flatten() == Right(inner=None)
            True

            >>> Right(inner=Left(inner=None)).flatten() == Left(inner=None)
            True

            >>> Left(inner=Right(inner=None)).flatten() == Right(inner=None)
            True

            >>> Left(inner=Left(inner=None)).flatten() == Left(inner=None)
            True
        ::
        """
        current = self

        while isinstance(current, Either) and isinstance(current.inner, Either):
            current = current.inner

        return current


@attrs.define(frozen=True, hash=True)
class Right(Either[T_co, Never]):
    def is_ok(self) -> Literal[True]:
        """.. code-block:: python

            >>> Right(inner=None).is_ok() == True
            True

            >>> Left(inner=None).is_ok() == False
            True
        ::
        """
        return True

    def map(self, func: Mappable, *args: P.args, **kwargs: P.kwargs) -> Right[U_co]:
        """.. code-block:: python

            >>> Right(inner=0).map(add_one) == Right(inner=1)
            True

            >>> Left(inner=None).map(add_one) == Left(inner=None)
            True
        ::
        """
        return Right(func(self.inner, *args, **kwargs))

    def map_err(self, func: Mappable, *args: P.args, **kwargs: P.kwargs) -> Self:  # noqa: ARG002
        """.. code-block:: python

            >>> Right(inner=0).map_err(add_one) == Right(inner=0)
            True

            >>> Left(inner=0).map_err(add_one) == Left(inner=1)
            True
        ::
        """
        return self

    def and_then(self, func: Bindable, *args: P.args, **kwargs: P.kwargs) -> Either[U_co, E_co]:
        return Right(func(self.inner, *args, **kwargs)).flatten()

    def or_else(self, func: Bindable, *args: P.args, **kwargs: P.kwargs) -> Self:  # noqa: ARG002
        return self

    def unwrap(self) -> T_co:
        return self.inner


@attrs.define(frozen=True, hash=True)
class Left(Either[Never, E_co]):
    def is_ok(self) -> Literal[False]:
        """.. code-block:: python

            >>> Right(inner=None).is_ok() == True
            True

            >>> Left(inner=None).is_ok() == False
            True
        ::
        """
        return False

    def map(self, func: Mappable, *args: P.args, **kwargs: P.kwargs) -> Self:  # noqa: ARG002
        """.. code-block:: python

            >>> Right(inner=0).map(add_one) == Right(inner=1)
            True

            >>> Left(inner=None).map(add_one) == Left(inner=None)
            True
        ::
        """
        return self

    def map_err(self, func: Mappable, *args: P.args, **kwargs: P.kwargs) -> Left[F_co]:
        """.. code-block:: python

            >>> Right(inner=0).map_err(add_one) == Right(inner=0)
            True

            >>> Left(inner=0).map_err(add_one) == Left(inner=1)
            True
        ::
        """
        return Left(func(self.inner, *args, **kwargs))

    def and_then(self, func: Bindable, *args: P.args, **kwargs: P.kwargs) -> Self:  # noqa: ARG002
        return self

    def or_else(self, func: Bindable, *args: P.args, **kwargs: P.kwargs) -> Either[U_co, E_co]:
        return Left(func(self.inner, *args, **kwargs)).flatten()  # ty: ignore[invalid-return-type]

    def unwrap(self) -> T_co:
        return self.inner
