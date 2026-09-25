from __future__ import annotations

from collections.abc import Callable
from typing import Any

import attrs

from .record import ExampleRecord
from .recorder import _RECORDER, Recorder


@attrs.define(frozen=True)
class Example[T]:
    fn: Callable
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    actual_result: T
    recorder: Recorder

    def __eq__(self, expected: T) -> bool:
        self.recorder.record_example(
            ExampleRecord.new(self.fn, self.args, self.kwargs, self.actual_result, expected)
        )
        return self.actual_result == expected

    def __hash__(self) -> int:
        hash_value = "".join(
            [
                self.fn.__qualname__,
                self.fn.__module__,
                str(self.args),
                str(self.kwargs),
                str(self.actual_result),
            ]
        )
        return hash(hash_value)


def example(fn: Callable, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> Example:
    value = fn(*args, **kwargs)
    return Example(fn, args, kwargs, value, recorder=_RECORDER)
