from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from types import TracebackType
from typing import (
    Any,
    Literal,
    Self,
)

import attrs


@attrs.define
class Result[T, U](ABC):
    """`Result` monad. Consists of `Ok` and `Err` for successful and failed operations respectively.
    Each monad is a frozen instance to prevent further mutation.
    """

    @classmethod
    def unit(cls, inner: T) -> Ok[T]:
        """Unit method. Given an item of type `T` return `Ok(T)`

        ```python
        >>> from danom import Err, Ok, Result
        >>> Result.unit(0) == Ok(inner=0)
        >>> Ok.unit(0) == Ok(inner=0)
        >>> Err.unit(0) == Ok(inner=0)
        ```
        """
        return Ok(inner)

    @abstractmethod
    def is_ok(self) -> bool:
        """Returns `True` if the result type is `Ok`.
        Returns `False` if the result type is `Err`.

        ```python
        >>> from danom import Err, Ok
        >>> Ok().is_ok() == True
        >>> Err().is_ok() == False
        ```
        """
        ...

    @abstractmethod
    def map(self, func: Callable[[T], U], **kwargs: dict) -> Result[U]:
        """Pipe a pure function and wrap the return value with `Ok`.
        Given an `Err` will return self.

        ```python
        >>> from danom import Err, Ok
        >>> Ok(1).map(add_one) == Ok(2)
        >>> Err(error=TypeError()).map(add_one) == Err(error=TypeError())
        ```
        """
        ...

    @abstractmethod
    def and_then(self, func: Callable[[T], Result[U]], **kwargs: dict) -> Result[U]:
        """Pipe another function that returns a monad. For `Err` will return original error.

        ```python
        >>> from danom import Err, Ok
        >>> Ok(1).and_then(add_one) == Ok(2)
        >>> Ok(1).and_then(raise_err) == Err(error=TypeError())
        >>> Err(error=TypeError()).and_then(add_one) == Err(error=TypeError())
        >>> Err(error=TypeError()).and_then(raise_value_err) == Err(error=TypeError())
        ```
        """
        ...

    @abstractmethod
    def unwrap(self) -> T:
        """Unwrap the `Ok` monad and get the inner value.
        Unwrap the `Err` monad will raise the inner error.
        ```python
        >>> from danom import Err, Ok
        >>> Ok().unwrap() == None
        >>> Ok(1).unwrap() == 1
        >>> Ok("ok").unwrap() == 'ok'
        >>> Err(error=TypeError()).unwrap() raise TypeError(...)
        ```
        """
        ...

    @abstractmethod
    def match(
        self, if_ok_func: Callable[[T], Result], if_err_func: Callable[[T], Result]
    ) -> Result:
        """Map `ok_func` to `Ok` and `err_func` to `Err`

        ```python
        >>> from danom import Err, Ok
        >>> Ok(1).match(add_one, mock_get_error_type) == Ok(inner=2)
        >>> Ok("ok").match(double, mock_get_error_type) == Ok(inner='okok')
        >>> Err(error=TypeError()).match(double, mock_get_error_type) == Ok(inner='TypeError')
        ```
        """
        ...

    def __class_getitem__(cls, _params: tuple) -> Self:
        return cls


@attrs.define(frozen=True, hash=True)
class Ok[T, U](Result):
    inner: Any = attrs.field(default=None)

    def is_ok(self) -> Literal[True]:
        return True

    def map(self, func: Callable[[T], U], **kwargs: dict) -> Result[U]:
        return Ok(func(self.inner, **kwargs))

    def and_then(self, func: Callable[[T], Result[U]], **kwargs: dict) -> Result[U]:
        return func(self.inner, **kwargs)

    def unwrap(self) -> T:
        return self.inner

    def match(
        self, if_ok_func: Callable[[T], Result], _if_err_func: Callable[[T], Result]
    ) -> Result:
        return if_ok_func(self.inner)


@attrs.define(frozen=True, hash=True)
class Err[T, U, E](Result):
    error: E | Exception | None = attrs.field(default=None)
    input_args: tuple[T] = attrs.field(default=None, repr=False)
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

    def map(self, _: Callable[[T], U], **_kwargs: dict) -> Result[U]:
        return self

    def and_then(self, _: Callable[[T], Result[U]], **_kwargs: dict) -> Self:
        return self

    def unwrap(self) -> None:
        if isinstance(self.error, Exception):
            raise self.error
        raise ValueError(f"Err does not have a caught error to raise: {self.error = }")

    def match(
        self, _if_ok_func: Callable[[T], Result], if_err_func: Callable[[T], Result]
    ) -> Result:
        return if_err_func(self.error)

    def __eq__(self, other: Err) -> bool:
        return all(
            (
                isinstance(other, Err),
                type(self.error) is type(other.error),
                str(self.error) == str(other.error),
                self.input_args == other.input_args,
            )
        )
