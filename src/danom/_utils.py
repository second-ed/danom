def identity[T](x: T) -> T:
    """Basic identity function.

    ```python
    >>> identity("abc") == "abc"
    >>> identity(1) == 1
    >>> identity(ComplexDataType(a=1, b=2, c=3)) == ComplexDataType(a=1, b=2, c=3)
    ```
    """
    return x
