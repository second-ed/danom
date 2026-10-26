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
    description: str | None = None

    @classmethod
    def new(  # noqa: PLR0913
        cls,
        fn: Callable,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        returned: Any,  # noqa: ANN401
        expected: Any,  # noqa: ANN401
        description: str | None = None,
    ) -> Self:
        cls_self = _try_self(fn)

        return cls(
            cls_name=cls_self.__class__.__name__ if cls_self else "",
            fn_name=fn.__name__,
            module=fn.__module__,
            src_file=str(Path(inspect.getsourcefile(fn))),
            ent_repr=f"{cls_self!r}.{fn.__name__}"
            if cls_self
            # else fn.__name__
            # if fn.__class__.__name__ == "method"
            else fn.__name__,
            args=tuple(_get_repr(arg) for arg in args),
            kwargs={k: _get_repr(v) for k, v in kwargs.items()},
            returned=_get_repr(returned),
            expected=_get_repr(expected),
            description=description,
        )

    def to_dict(self) -> dict[str, str]:
        return attrs.asdict(self)


def _try_self(fn: Callable) -> str:
    try:
        return fn.__self__
    except AttributeError:
        return ""


def _get_repr(arg: Any) -> str:  # noqa: ANN401
    return _clean_repr(repr(arg))


def _clean_repr(raw: str) -> str:
    if raw.startswith("<function "):
        return raw.removeprefix("<function ").split(" at ")[0]
    if raw.startswith("<class "):
        return raw.removeprefix("<class ").strip("'>").split(".")[-1]
    if raw.startswith("<built-in function "):
        return raw.removeprefix("<built-in function ").strip(" >")
    return raw
