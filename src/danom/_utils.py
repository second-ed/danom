from collections.abc import Callable, Sequence
from operator import not_

import attrs

from danom._result import P


@attrs.define(frozen=True, hash=True, eq=True)
class _Composer[T, U]:
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
    return _Composer(fns)


@attrs.define(frozen=True, hash=True, eq=True)
class _AllOf[T, U]:
    fns: Sequence[Callable[[T], U]]

    def __call__(self, initial: T) -> U:
        return all(fn(initial) for fn in self.fns)


def all_of[T](*fns: Callable[[T], bool]) -> Callable[[T], bool]:
    return _AllOf(fns)


@attrs.define(frozen=True, hash=True, eq=True)
class _AnyOf[T, U]:
    fns: Sequence[Callable[[T], U]]

    def __call__(self, initial: T) -> U:
        return any(fn(initial) for fn in self.fns)


def any_of[T](*fns: Callable[[T], bool]) -> Callable[[T], bool]:
    return _AnyOf(fns)


def identity[T](x: T) -> T:
    """Basic identity function.

    ```python
    >>> identity("abc") == "abc"
    >>> identity(1) == 1
    >>> identity(ComplexDataType(a=1, b=2, c=3)) == ComplexDataType(a=1, b=2, c=3)
    ```
    """
    return x


def invert(func: Callable[[P], bool]) -> Callable[[P], bool]:
    """Invert a boolean function so it returns False where it would've returned True.

    ```python
    >>> invert(has_len)("abc") == False
    >>> invert(has_len)("") == True
    ```
    """
    return compose(func, not_)
