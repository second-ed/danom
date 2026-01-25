from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from types import TracebackType
from typing import (
    Any,
    Literal,
    ParamSpec,
    Self,
    TypeVar,
)

import attrs

T_co = TypeVar("T_co", covariant=True)
U_co = TypeVar("U_co", covariant=True)
E_co = TypeVar("E_co", bound=object, covariant=True)
P = ParamSpec("P")

Mappable = Callable[P, U_co]
ResultReturnType = TypeVar("ResultReturnType", bound="Result[U_co, E_co]")
Bindable = Callable[P, ResultReturnType]


@attrs.define(frozen=True)
class Result(ABC):
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
    def map(self, func: Mappable, **kwargs: P.kwargs) -> ResultReturnType:
        """Pipe a pure function and wrap the return value with `Ok`.
        Given an `Err` will return self.

        .. code-block:: python

            from danom import Err, Ok

            Ok(1).map(add_one) == Ok(2)
            Err(error=TypeError()).map(add_one) == Err(error=TypeError())
        """
        ...

    @abstractmethod
    def and_then(self, func: Bindable, **kwargs: P.kwargs) -> ResultReturnType:
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

    @abstractmethod
    def match(self, if_ok_func: Mappable, if_err_func: Mappable) -> ResultReturnType:
        """Map `ok_func` to `Ok` and `err_func` to `Err`

        .. code-block:: python

            from danom import Err, Ok

            Ok(1).match(add_one, mock_get_error_type) == Ok(inner=2)
            Ok("ok").match(double, mock_get_error_type) == Ok(inner='okok')
            Err(error=TypeError()).match(double, mock_get_error_type) == Ok(inner='TypeError')
        """
        ...

    def __class_getitem__(cls, _params: tuple) -> Self:
        return cls  # ty: ignore[invalid-return-type]


@attrs.define(frozen=True, hash=True)
class Ok[T_co](Result):
    inner: Any = attrs.field(default=None)

    def is_ok(self) -> Literal[True]:
        return True

    def map(self, func: Mappable, **kwargs: P.kwargs) -> Ok[U_co]:
        return Ok(func(self.inner, **kwargs))

    def and_then(self, func: Bindable, **kwargs: P.kwargs) -> ResultReturnType:
        return func(self.inner, **kwargs)

    def unwrap(self) -> T_co:
        return self.inner

    def match(self, if_ok_func: Mappable, if_err_func: Mappable) -> ResultReturnType:  # noqa: ARG002
        return if_ok_func(self.inner)


SafeArgs = tuple[tuple[Any, ...], dict[str, Any]]
SafeMethodArgs = tuple[object, tuple[Any, ...], dict[str, Any]]


@attrs.define(frozen=True)
class Err[E_co](Result):
    error: E_co | Exception = attrs.field(default=None)
    input_args: tuple[()] | SafeArgs | SafeMethodArgs = attrs.field(default=(), repr=False)
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

    def map(self, func: Mappable, **kwargs: P.kwargs) -> Err[E_co]:  # noqa: ARG002
        return self

    def and_then(self, func: Bindable, **kwargs: P.kwargs) -> Err[E_co]:  # noqa: ARG002
        return self

    def unwrap(self) -> None:
        if isinstance(self.error, Exception):
            raise self.error
        raise ValueError(f"Err does not have a caught error to raise: {self.error = }")

    def match(self, if_ok_func: Mappable, if_err_func: Mappable) -> ResultReturnType:  # noqa: ARG002
        return if_err_func(self.error)

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
