from __future__ import annotations

from collections.abc import Callable
from types import TracebackType
from typing import (
    Any,
    Literal,
    Self,
)

import attrs

from danom.result import Result, T


@attrs.define
class Err(Result):
    input_args: Any = attrs.field(default=None, repr=False)
    error: Exception | None = attrs.field(
        default=None,
        validator=attrs.validators.optional(attrs.validators.instance_of(Exception)),
    )
    err_type: BaseException = attrs.field(init=False, repr=False)
    err_msg: str = attrs.field(init=False, repr=False)
    details: list[dict[str, Any]] = attrs.field(init=False, repr=False)

    def __attrs_post_init__(self) -> None:
        self.err_type = type(self.error)
        self.err_msg = str(self.error)
        if self.error:
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
        return False

    def and_then(self, _: Callable[[T], Result], **_kwargs: dict) -> Self:
        return self

    def unwrap(self) -> None:
        raise self.error

    def __getattr__(self, _name: str) -> Self:
        def _(*_args: tuple, **_kwargs: dict) -> Self:
            return self

        return _
