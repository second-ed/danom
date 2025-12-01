from collections.abc import Callable, Iterable

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

    def map(self, fn: Callable) -> "Stream":
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
        """
        return Stream(lambda: (fn(x) for x in self.seq()))

    def filter(self, fn: Callable) -> "Stream":
        """Filter the stream based on a predicate. Will return a new `Stream` with the modified sequence.

        ```python
        >>> Stream.from_iterable([0, 1, 2, 3]).filter(lambda x: x % 2 == 0).collect() == (0, 2)
        ```
        """
        return Stream(lambda: (x for x in self.seq() if fn(x)))

    def partition(self, fn: Callable) -> tuple["Stream", "Stream"]:
        """Similar to `filter` except splits the True and False values. Will return a two new `Stream` with the partitioned sequences.

        Each partition is independently replayable.
        ```python
        >>> part1, part2 = Stream.from_iterable([0, 1, 2, 3]).partition(lambda x: x % 2 == 0)
        >>> part1.collect() == (0, 2)
        >>> part2.collect() == (1, 3)
        ```
        """
        # have to materialise to be able to replay each side independently
        seq_tuple = tuple(self.seq())
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
