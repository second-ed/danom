from __future__ import annotations

from collections.abc import Callable
from types import TracebackType
from typing import (
    Any,
    Literal,
    Self,
)

import attrs

from danom._result import Result, T


@attrs.define
class Err(Result):
    input_args: tuple[T] = attrs.field(default=None, repr=False)
    error: Exception | None = attrs.field(default=None)
    err_type: BaseException = attrs.field(init=False, repr=False)
    err_msg: str = attrs.field(init=False, repr=False)
    details: list[dict[str, Any]] = attrs.field(factory=list, init=False, repr=False)

    def __attrs_post_init__(self) -> None:
        self.err_type = type(self.error)
        self.err_msg = str(self.error)
        if isinstance(self.error, Exception):
            self.details = self._extract_details(self.error.__traceback__)

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
        """Returns False if the result type is Err.

        ```python
        Err().is_ok() == False
        ```
        """
        return False

    def and_then(self, _: Callable[[T], Result], **_kwargs: dict) -> Self:
        """Pipe another function that returns a monad. For Err will return original error.

        ```python
        >>> Err(error=TypeError()).and_then(add_one) == Err(error=TypeError())
        >>> Err(error=TypeError()).and_then(raise_value_err) == Err(error=TypeError())
        ```
        """
        return self

    def unwrap(self) -> None:
        """Unwrap the Err monad will raise the inner error.

        ```python
        >>> Err(error=TypeError()).unwrap() raise TypeError(...)
        ```
        """
        raise self.error

    def match(
        self, _if_ok_func: Callable[[T], Result], if_err_func: Callable[[T], Result]
    ) -> Result:
        """Map Ok func to Ok and Err func to Err

        ```python
        >>> Ok(1).match(add_one, mock_get_error_type) == Ok(inner=2)
        >>> Ok("ok").match(double, mock_get_error_type) == Ok(inner='okok')
        >>> Err(error=TypeError()).match(double, mock_get_error_type) == Ok(inner='TypeError')
        ```
        """
        return if_err_func(self.error)

    def __getattr__(self, _name: str) -> Self:
        def _(*_args: tuple, **_kwargs: dict) -> Self:
            return self

        return _
