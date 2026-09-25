from __future__ import annotations

import inspect
from collections.abc import Callable
from pathlib import Path
from typing import Any, Self

import attrs


@attrs.define(frozen=True, eq=True)
class ExampleRecord:
    cls_name: str
    fn_name: str
    module: str
    src_file: str
    ent_repr: str
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    returned: Any
    expected: Any

    @classmethod
    def new(
        cls,
        fn: Callable,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        returned: Any,  # noqa: ANN401
        expected: Any,  # noqa: ANN401
    ) -> Self:
        return cls(
            cls_name=fn.__self__.__class__.__name__,
            fn_name=fn.__name__,
            module=fn.__module__,
            src_file=str(Path(inspect.getsourcefile(fn))),
            ent_repr=f"{fn.__self__!r}.{fn.__name__}"
            if fn.__class__.__name__ == "method"
            else fn.__name__,
            args=tuple(_get_repr(arg) for arg in args),
            kwargs={k: _get_repr(v) for k, v in kwargs.items()},
            returned=_get_repr(returned),
            expected=_get_repr(expected),
        )

    def to_dict(self) -> dict[str, str]:
        return attrs.asdict(self)


def _get_repr(arg: Any) -> str:  # noqa: ANN401
    value = repr(arg)
    return (
        value.removeprefix("<function ").split(" at ")[0]
        if value.startswith("<function ")
        else value
    )
