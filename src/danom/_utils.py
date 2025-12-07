from collections.abc import Callable

from danom._result import P


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

    def wrapper(*args: P.args, **kwargs: P.kwargs) -> bool:
        return not func(*args, **kwargs)

    return wrapper
