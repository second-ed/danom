from __future__ import annotations

from typing import TYPE_CHECKING

import attrs

from ._base import _FILTER, _MAP, _TAP, U, _BaseSyncStream, _Tap

if TYPE_CHECKING:
    from ._par import ParStream


@attrs.define(frozen=True)
class Stream[T](_BaseSyncStream):
    """A lazy iterator with functional operations.

    Why bother?
    -----------

    Readability counts, abstracting common operations helps reduce cognitive complexity when reading code.

    Comparison
    ----------

    Take this imperative pipeline of operations, it iterates once over the data, skipping the value if it fails one of the filter checks:

    .. code-block:: python

        res = []

        for x in range(1_000_000):
            item = triple(x)

            if not is_gt_ten(item):
                continue

            item = min_two(item)

            if not is_even_num(item):
                continue

            item = square(item)

            if not is_lt_400(item):
                continue

            res.append(item)
        [100, 256]

    number of tokens: `90`

    number of keywords: `11`

    keyword breakdown: `{'for': 1, 'in': 1, 'if': 3, 'not': 3, 'continue': 3}`

    After a bit of experience with python you might use list comprehensions, however this is arguably _less_ clear and iterates multiple times over the same data

    .. code-block:: python

        mul_three = [triple(x) for x in range(1_000_000)]
        gt_ten = [x for x in mul_three if is_gt_ten(x)]
        sub_two = [min_two(x) for x in gt_ten]
        is_even = [x for x in sub_two if is_even_num(x)]
        squared = [square(x) for x in is_even]
        lt_400 = [x for x in squared if is_lt_400(x)]
        [100, 256]

    number of tokens: `92`

    number of keywords: `15`

    keyword breakdown: `{'for': 6, 'in': 6, 'if': 3}`

    This still has a lot of tokens that the developer has to read to understand the code. The extra keywords add noise that cloud the actual transformations.

    Using a ``Stream`` results in this:

    .. code-block:: python

        from danom import Stream

        (
            Stream.from_iterable(range(1_000_000))
            .map(triple)
            .filter(is_gt_ten)
            .map(min_two)
            .filter(is_even_num)
            .map(square)
            .filter(is_lt_400)
            .collect()
        )
        (100, 256)

    number of tokens: `60`

    number of keywords: `0`

    keyword breakdown: `{}`

    The business logic is arguably much clearer like this.

    Version changes
    ----------
    ``0.13.0``: ``Stream.map``, ``Stream.filter`` and ``Stream.tap`` now take kwargs and ``partial`` them into the passed in function.

    """

    def collect(self, *, workers: int = 4, use_threads: bool = False) -> tuple[U, ...]:  # noqa: ARG002
        """Materialise the sequence from the ``Stream``.

        .. code-block:: python

            from danom import Stream

            stream = Stream.from_iterable([0, 1, 2, 3]).map(add_one)
            stream.collect() == (1, 2, 3, 4)

        """
        pipeline = self.seq
        for op, fn in self.ops:
            if op == _MAP:
                pipeline = map(fn, pipeline)
            elif op == _FILTER:
                pipeline = filter(fn, pipeline)
            elif op == _TAP:
                pipeline = map(_Tap(fn), pipeline)
            else:
                raise RuntimeError("Invalid operation selected. Valid options [map, filter, tap]")

        return tuple(pipeline)

    def to_par(self) -> ParStream[T]:
        from ._par import ParStream

        return ParStream(self.seq, self.ops)

    def to_stream(self) -> Stream[T]:
        return self
