from collections.abc import Callable
from typing import (
    Any,
    Literal,
)

import attrs

from danom.result import Result, T


@attrs.define
class Ok(Result):
    inner: Any = attrs.field(default=None)

    def is_ok(self) -> Literal[True]:
        return True

    def and_then(self, func: Callable[[T], Result], **kwargs: dict) -> Result:
        return func(self.inner, **kwargs)

    def unwrap(self) -> T:
        return self.inner

    def __getattr__(self, name: str) -> Callable:
        return getattr(self.inner, name)
