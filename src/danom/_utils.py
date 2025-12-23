from collections.abc import Callable, Sequence
from operator import not_

import attrs


@attrs.define(frozen=True, hash=True, eq=True)
class _Compose[T, U]:
    fns: Sequence[Callable[[T], U]]

    def __call__(self, initial: T) -> U:
        value = initial
        for fn in self.fns:
            value = fn(value)
        return value


def compose[T, U](*fns: Callable[[T], U]) -> Callable[[T], U]:
    """Compose multiple functions into one.

    The functions will be called in sequence with the result of one being used as the input for the next.

    ```python
    >>> add_two = compose(add_one, add_one)
    >>> add_two(0) == 2
    ```

    ```python
    >>> add_two = compose(add_one, add_one, is_even)
    >>> add_two(0) == True
    ```
    """
    return _Compose(fns)


@attrs.define(frozen=True, hash=True, eq=True)
class _AllOf[T]:
    fns: Sequence[Callable[[T], bool]]

    def __call__(self, initial: T) -> bool:
        return all(fn(initial) for fn in self.fns)


def all_of[T](*fns: Callable[[T], bool]) -> Callable[[T], bool]:
    """True if all of the given functions return True.

    ```python
    >>> is_valid_user = all_of(is_subscribed, is_active, has_2fa)
    >>> is_valid_user(user) == True
    ```
    """
    return _AllOf(fns)


@attrs.define(frozen=True, hash=True, eq=True)
class _AnyOf[T]:
    fns: Sequence[Callable[[T], bool]]

    def __call__(self, initial: T) -> bool:
        return any(fn(initial) for fn in self.fns)


def any_of[T](*fns: Callable[[T], bool]) -> Callable[[T], bool]:
    """True if any of the given functions return True.

    ```python
    >>> is_eligible = any_of(has_coupon, is_vip, is_staff)
    >>> is_eligible(user) == True
    ```
    """
    return _AnyOf(fns)


def none_of[T](*fns: Callable[[T], bool]) -> Callable[[T], bool]:
    """True if none of the given functions return True.

    ```python
    >>> is_valid = none_of(is_empty, exceeds_size_limit, contains_unsupported_format)
    >>> is_valid(submission) == True
    ```
    """
    return compose(_AnyOf(fns), not_)


def identity[T](x: T) -> T:
    """Basic identity function.

    ```python
    >>> identity("abc") == "abc"
    >>> identity(1) == 1
    >>> identity(ComplexDataType(a=1, b=2, c=3)) == ComplexDataType(a=1, b=2, c=3)
    ```
    """
    return x


def invert[T](func: Callable[[T], bool]) -> Callable[[T], bool]:
    """Invert a boolean function so it returns False where it would've returned True.

    ```python
    >>> invert(has_len)("abc") == False
    >>> invert(has_len)("") == True
    ```
    """
    return compose(func, not_)
