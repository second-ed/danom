from collections.abc import Callable, Iterable

import attrs


@attrs.define(frozen=True)
class Stream:
    seq: Callable[[], Iterable] = attrs.field(
        validator=attrs.validators.instance_of(Callable), repr=False
    )

    @classmethod
    def from_iterable(cls, it: Iterable) -> "Stream":
        if not isinstance(it, Iterable):
            it = [it]
        return cls(lambda: iter(it))

    def map(self, fn: Callable) -> "Stream":
        return Stream(lambda: (fn(x) for x in self.seq()))

    def filter(self, fn: Callable) -> "Stream":
        return Stream(lambda: (x for x in self.seq() if fn(x)))

    def partition(self, fn: Callable) -> tuple["Stream", "Stream"]:
        # have to materialise to be able to replay each side independently
        seq_tuple = tuple(self.seq())
        return (
            Stream(lambda: (x for x in seq_tuple if fn(x))),
            Stream(lambda: (x for x in seq_tuple if not fn(x))),
        )

    def collect(self) -> tuple:
        return tuple(self.seq())
