from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import (
    ParamSpec,
    Self,
    TypeVar,
)

import attrs

T = TypeVar("T")
P = ParamSpec("P")


@attrs.define
class Result(ABC):
    @abstractmethod
    def is_ok(self) -> bool: ...

    @abstractmethod
    def and_then(self, func: Callable[[T], Result], **kwargs: dict) -> Result: ...

    @abstractmethod
    def unwrap(self) -> T: ...

    def __class_getitem__(cls, _params: tuple) -> Self:
        return cls
