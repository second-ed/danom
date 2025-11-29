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
        """Returns True if the result type is Ok.

        ```python
        >>> Ok().is_ok() == True
        ```
        """
        return True

    def and_then(self, func: Callable[[T], Result], **kwargs: dict) -> Result:
        """Pipe another function that returns a monad.

        ```python
        >>> Ok(1).and_then(add_one) == Ok(2)
        >>> Ok(1).and_then(raise_err) == Err(error=TypeError())
        ```
        """
        return func(self.inner, **kwargs)

    def unwrap(self) -> T:
        """Unwrap the Ok monad and get the inner value.

        ```python
        >>> Ok().unwrap() == None
        >>> Ok(1).unwrap() == 1
        >>> Ok("ok").unwrap() == 'ok'
        ```
        """
        return self.inner

    def match(
        self, if_ok_func: Callable[[T], Result], _if_err_func: Callable[[T], Result]
    ) -> Result:
        """Map Ok func to Ok and Err func to Err

        ```python
        >>> Ok(1).match(add_one, mock_get_error_type) == Ok(inner=2)
        >>> Ok("ok").match(double, mock_get_error_type) == Ok(inner='okok')
        >>> Err(error=TypeError()).match(double, mock_get_error_type) == Ok(inner='TypeError')
        ```
        """
        return if_ok_func(self.inner)

    def __getattr__(self, name: str) -> Callable:
        return getattr(self.inner, name)
