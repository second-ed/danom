from collections.abc import Callable
from operator import not_

from danom._result import P


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

    def wrapper(value: T) -> U:
        for fn in fns:
            value = fn(value)
        return value

    return wrapper


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
