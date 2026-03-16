from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from types import TracebackType
from typing import (
    Any,
    Concatenate,
    Literal,
    Never,
    ParamSpec,
    Self,
    TypeVar,
)

import attrs
from attrs.validators import instance_of

T_co = TypeVar("T_co", covariant=True)
U_co = TypeVar("U_co", covariant=True)
E_co = TypeVar("E_co", bound=object, covariant=True)
F_co = TypeVar("F_co", bound=object, covariant=True)
P = ParamSpec("P")

Mappable = Callable[Concatenate[T_co, P], U_co]
Bindable = Callable[Concatenate[T_co, P], "Result[U_co, E_co]"]


@attrs.define(frozen=True)
class Result[T_co, E_co: object](ABC):
    """`Result` monad. Consists of `Ok` and `Err` for successful and failed operations respectively.
    Each monad is a frozen instance to prevent further mutation.
    """

    @classmethod
    def unit(cls, inner: T_co) -> Ok[T_co]:
        """Unit method. Given an item of type `T_co` return `Ok(T_co)`

        .. doctest::

            >>> from danom import Err, Ok, Result

            >>> Result.unit(0) == Ok(inner=0)
            True

            >>> Ok.unit(0) == Ok(inner=0)
            True

            >>> Err.unit(0) == Ok(inner=0)
            True
        """
        return Ok(inner)

    @abstractmethod
    def is_ok(self) -> bool:
        """Returns `True` if the result type is `Ok`.
        Returns `False` if the result type is `Err`.

        .. doctest::

            >>> from danom import Err, Ok

            >>> Ok().is_ok() == True
            True

            >>> Err().is_ok() == False
            True
        """
        ...

    @abstractmethod
    def map(self, func: Mappable, *args: P.args, **kwargs: P.kwargs) -> Result[U_co, E_co]:
        """Pipe a pure function and wrap the return value with `Ok`.
        Given an `Err` will return self.

        .. code-block:: python

            from danom import Err, Ok

            Ok(1).map(add_one) == Ok(2)
            Err(error=TypeError()).map(add_one) == Err(error=TypeError())
        """
        ...

    @abstractmethod
    def map_err(self, func: Mappable, *args: P.args, **kwargs: P.kwargs) -> Result[U_co, E_co]:
        """Pipe a pure function and wrap the return value with `Err`.
        Given an `Ok` will return self.

        .. code-block:: python

            from danom import Err, Ok

            Err(error=TypeError()).map_err(type_err_to_value_err) == Err(error=ValueError())
            Ok(1).map(type_err_to_value_err) == Ok(1)
        """
        ...

    @abstractmethod
    def and_then(self, func: Bindable, *args: P.args, **kwargs: P.kwargs) -> Result[U_co, E_co]:
        """Pipe another function that returns a monad. For `Err` will return original error.

        .. code-block:: python

            from danom import Err, Ok

            Ok(1).and_then(add_one) == Ok(2)
            Ok(1).and_then(raise_err) == Err(error=TypeError())
            Err(error=TypeError()).and_then(add_one) == Err(error=TypeError())
            Err(error=TypeError()).and_then(raise_value_err) == Err(error=TypeError())
        """
        ...

    @abstractmethod
    def or_else(self, func: Bindable, *args: P.args, **kwargs: P.kwargs) -> Result[U_co, E_co]:
        """Pipe a function that returns a monad to recover from an `Err`. For `Ok` will return original `Result`.

        .. code-block:: python

            from danom import Err, Ok

            Ok(1).or_else(replace_err_with_zero) == Ok(1)
            Err(error=TypeError()).or_else(replace_err_with_zero) == Ok(0)
        """
        ...

    @abstractmethod
    def unwrap(self) -> T_co:
        """Unwrap the `Ok` monad and get the inner value.
        Unwrap the `Err` monad will raise the inner error.

        .. doctest::

            >>> from danom import Err, Ok

            >>> Ok().unwrap() == None
            True

            >>> Ok(1).unwrap() == 1
            True

            >>> Ok("ok").unwrap() == 'ok'
            True

            >>> Err(error=TypeError()).unwrap()
            Traceback (most recent call last):
            ...
            TypeError:
        """
        ...

    @staticmethod
    def result_is_ok(result: Result[T_co, E_co]) -> bool:
        """Check whether the monad is ok. Allows for ``filter`` or ``partition`` in a ``Stream`` without needing a lambda or custom function.

        .. code-block:: python

            from danom import Stream, Result

            Stream.from_iterable([Ok(), Ok(), Err()]).filter(Result.result_is_ok).collect() == (Ok(), Ok())

        """
        return result.is_ok()

    @staticmethod
    def result_unwrap(result: Result[T_co, E_co]) -> T_co:
        """Unwrap the `Ok` monad and get the inner value.
        Unwrap the `Err` monad will raise the inner error.

        .. code-block:: python

            from danom import Stream, Result

            oks, errs = Stream.from_iterable([Ok(1), Ok(2), Err()]).partition(Result.result_is_ok)
            oks.map(Result.result_unwrap).collect == (1, 2)

        """
        return result.unwrap()


@attrs.define(frozen=True, hash=True)
class Ok(Result[T_co, Never]):
    inner: Any = attrs.field(default=None)

    def is_ok(self) -> Literal[True]:
        return True

    def map(self, func: Mappable, *args: P.args, **kwargs: P.kwargs) -> Ok[U_co]:
        return Ok(func(self.inner, *args, **kwargs))

    def map_err(self, func: Mappable, *args: P.args, **kwargs: P.kwargs) -> Self:  # noqa: ARG002
        return self

    def and_then(self, func: Bindable, *args: P.args, **kwargs: P.kwargs) -> Result[U_co, E_co]:
        return func(self.inner, *args, **kwargs)

    def or_else(self, func: Bindable, *args: P.args, **kwargs: P.kwargs) -> Self:  # noqa: ARG002
        return self

    def unwrap(self) -> T_co:
        return self.inner


SafeArgs = tuple[tuple[Any, ...], dict[str, Any]]
SafeMethodArgs = tuple[object, tuple[Any, ...], dict[str, Any]]


@attrs.define(frozen=True)
class Err(Result[Never, E_co]):
    error: Any = attrs.field(default=None)
    input_args: tuple[()] | SafeArgs | SafeMethodArgs = attrs.field(
        default=(), validator=instance_of(tuple), repr=False
    )
    traceback: str = attrs.field(default="", validator=instance_of(str))
    details: list[dict[str, Any]] = attrs.field(factory=list, init=False, repr=False)

    def __attrs_post_init__(self) -> None:
        if isinstance(self.error, Exception):
            # little hack explained here: https://www.attrs.org/en/stable/init.html#post-init
            object.__setattr__(self, "details", self._extract_details(self.error.__traceback__))

    def _extract_details(self, tb: TracebackType | None) -> list[dict[str, Any]]:
        trace_info = []
        while tb:
            frame = tb.tb_frame
            trace_info.append(
                {
                    "file": frame.f_code.co_filename,
                    "func": frame.f_code.co_name,
                    "line_no": tb.tb_lineno,
                    "locals": frame.f_locals,
                },
            )
            tb = tb.tb_next
        return trace_info

    def is_ok(self) -> Literal[False]:
        return False

    def map(self, func: Mappable, *args: P.args, **kwargs: P.kwargs) -> Self:  # noqa: ARG002
        return self

    def map_err(self, func: Mappable, *args: P.args, **kwargs: P.kwargs) -> Err[F_co]:
        return Err(func(self.error, *args, **kwargs))

    def and_then(self, func: Bindable, *args: P.args, **kwargs: P.kwargs) -> Self:  # noqa: ARG002
        return self

    def or_else(self, func: Bindable, *args: P.args, **kwargs: P.kwargs) -> Result[U_co, E_co]:
        return func(self.error, *args, **kwargs)

    def unwrap(self) -> T_co:
        if isinstance(self.error, Exception):
            raise self.error
        raise ValueError(f"Err does not have a caught error to raise: {self.error = }")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Err):
            return False

        return all(
            (
                type(self.error) is type(other.error),
                str(self.error) == str(other.error),
                self.input_args == other.input_args,
            )
        )

    def __hash__(self) -> int:
        return hash(f"{type(self.error)}{self.error}{self.input_args}")
