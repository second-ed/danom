from __future__ import annotations

import inspect
from collections.abc import Callable, Sequence
from typing import Self

import attrs


# skip return type because it makes Pylance think the returned type isn't a type
def new_type(  # noqa: ANN202
    name: str,
    base_type: type,
    validators: Callable | Sequence[Callable] | None = None,
    converters: Callable | Sequence[Callable] | None = None,
    *,
    frozen: bool = True,
):
    """Create a NewType based on another type.

    .. code-block:: python

        from danom import new_type

        def is_positive(value):
            return value >= 0

        ValidBalance = new_type("ValidBalance", float, validators=[is_positive])
        ValidBalance("20") == ValidBalance(inner=20.0)

    Unlike an inherited class, the type will not return `True` for an isinstance check.

    .. code-block:: python

        isinstance(ValidBalance(20.0), ValidBalance) == True
        isinstance(ValidBalance(20.0), float) == False

    The methods of the given `base_type` will be forwarded to the specialised type.
    Alternatively the map method can be used to return a new type instance with the transformation.

    .. code-block:: python

        from danom import new_type

        def has_len(email: str) -> bool:
        return len(email) > 0

        Email = new_type("Email", str, validators=[has_len])
        Email("some_email@domain.com").upper() == "SOME_EMAIL@DOMAIN.COM"
        Email("some_email@domain.com").map(str.upper) == Email(inner='SOME_EMAIL@DOMAIN.COM')
    """
    kwargs = _callables_to_kwargs(base_type, validators, converters)

    @attrs.define(frozen=frozen, eq=True, hash=frozen)
    class _Wrapper[T]:
        inner: T = attrs.field(**kwargs)

        def map(self, func: Callable[[T], T]) -> T:
            return type(self)(func(self.inner))

        locals().update(_create_forward_methods(base_type))

    _Wrapper.__name__ = name
    _Wrapper.__qualname__ = name
    return _Wrapper


def _create_forward_methods(base_type: type) -> dict[str, Callable]:
    methods: dict[str, Callable] = {}
    for attr_name, _ in inspect.getmembers(base_type, inspect.isroutine):
        if attr_name.startswith("_"):
            continue

        def make_forwarder(name: str) -> Callable:
            def method[T](self: Self, *args: tuple, **kwargs: dict) -> T:
                return getattr(self.inner, name)(*args, **kwargs)

            method.__name__ = name
            method.__doc__ = getattr(base_type, name).__doc__
            return method

        methods[attr_name] = make_forwarder(attr_name)
    return methods


def _callables_to_kwargs(
    base_type: type,
    validators: Callable | Sequence[Callable] | None,
    converters: Callable | Sequence[Callable] | None,
) -> dict[str, Sequence[Callable]]:
    kwargs = {"validator": [attrs.validators.instance_of(base_type)], "converter": []}
    kwargs["validator"] += [_validate_bool_func(fn) for fn in _to_list(validators)]
    kwargs["converter"] += _to_list(converters)

    return {k: v for k, v in kwargs.items() if v}


def _validate_bool_func[T](
    bool_fn: Callable[..., bool],
) -> Callable[[attrs.AttrsInstance, attrs.Attribute, T], None]:
    if not isinstance(bool_fn, Callable):
        raise TypeError("provided boolean function must be callable")

    def wrapper(_instance: attrs.AttrsInstance, attribute: attrs.Attribute, value: T) -> None:
        if not bool_fn(value):
            raise ValueError(
                f"{attribute.name} does not return True for `{bool_fn.__name__}`, received `{value}`."
            )

    return wrapper


def _to_list(value: Callable | Sequence[Callable] | None) -> list[Callable]:
    if value is None:
        return []
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return list(value)
    return [value]
