from collections.abc import Callable
from typing import (
    Any,
    Literal,
)

import attrs

from danom._result import Result, T


@attrs.define
class Ok(Result):
    inner: Any = attrs.field(default=None)

    def is_ok(self) -> Literal[True]:
        return True

    def and_then(self, func: Callable[[T], Result], **kwargs: dict) -> Result:
        return func(self.inner, **kwargs)

    def unwrap(self) -> T:
        return self.inner

    def match(
        self, if_ok_func: Callable[[T], Result], _if_err_func: Callable[[T], Result]
    ) -> Result:
        return if_ok_func(self.inner)

    def __getattr__(self, name: str) -> Callable:
        return getattr(self.inner, name)
