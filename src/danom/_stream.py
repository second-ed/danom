from collections.abc import Callable, Generator, Iterable

import attrs


@attrs.define(frozen=True)
class Stream:
    """A lazy iterator with functional operations."""

    seq: Callable[[], Iterable] = attrs.field(
        validator=attrs.validators.instance_of(Callable), repr=False
    )

    @classmethod
    def from_iterable(cls, it: Iterable) -> "Stream":
        """This is the recommended way of creating a Stream object.

        ```python
        >>> Stream.from_iterable([0, 1, 2, 3]).collect() == (0, 1, 2, 3)
        ```
        """
        if not isinstance(it, Iterable):
            it = [it]
        return cls(lambda: iter(it))

    def map[T, U](self, *fns: Callable[[T], U]) -> "Stream":
        """Map a function to the elements in the `Stream`. Will return a new `Stream` with the modified sequence.

        ```python
        >>> Stream.from_iterable([0, 1, 2, 3]).map(add_one).collect() == (1, 2, 3, 4)
        ```

        This can also be mixed with `safe` functions:
        ```python
        >>> Stream.from_iterable([0, 1, 2, 3]).map(add_one).collect() == (Ok(inner=1), Ok(inner=2), Ok(inner=3), Ok(inner=4))

        >>> @safe
        ... def two_div_value(x: float) -> float:
        ...     return 2 / x

        >>> Stream.from_iterable([0, 1, 2, 4]).map(two_div_value).collect() == (Err(error=ZeroDivisionError('division by zero')), Ok(inner=2.0), Ok(inner=1.0), Ok(inner=0.5))
        ```

        Simple functions can be passed in sequence to compose more complex transformations
        ```python
        >>> Stream.from_iterable(range(5)).map(mul_two, add_one).collect() == (1, 3, 5, 7, 9)
        ```
        """

        def generator() -> Generator[U, None, None]:
            for elem in self.seq():
                res = elem
                for fn in fns:
                    res = fn(res)
                yield res

        return Stream(generator)

    def filter[T](self, *fns: Callable[[T], bool]) -> "Stream":
        """Filter the stream based on a predicate. Will return a new `Stream` with the modified sequence.

        ```python
        >>> Stream.from_iterable([0, 1, 2, 3]).filter(lambda x: x % 2 == 0).collect() == (0, 2)
        ```

        Simple functions can be passed in sequence to compose more complex filters
        ```python
        >>> Stream.from_iterable(range(20)).filter(divisible_by_3, divisible_by_5).collect() == (0, 15)
        ```
        """
        return Stream(lambda: (x for x in self.seq() if all(fn(x) for fn in fns)))

    def partition[T](self, fn: Callable[[T], bool]) -> tuple["Stream", "Stream"]:
        """Similar to `filter` except splits the True and False values. Will return a two new `Stream` with the partitioned sequences.

        Each partition is independently replayable.
        ```python
        >>> part1, part2 = Stream.from_iterable([0, 1, 2, 3]).partition(lambda x: x % 2 == 0)
        >>> part1.collect() == (0, 2)
        >>> part2.collect() == (1, 3)
        ```
        """
        # have to materialise to be able to replay each side independently
        seq_tuple = self.collect()
        return (
            Stream(lambda: (x for x in seq_tuple if fn(x))),
            Stream(lambda: (x for x in seq_tuple if not fn(x))),
        )

    def collect(self) -> tuple:
        """Materialise the sequence from the `Stream`.

        ```python
        >>> stream = Stream.from_iterable([0, 1, 2, 3]).map(add_one)
        >>> stream.collect() == (1, 2, 3, 4)
        ```
        """
        return tuple(self.seq())
