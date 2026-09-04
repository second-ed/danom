from __future__ import annotations

import itertools
import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from copy import deepcopy
from itertools import batched
from typing import TYPE_CHECKING, Self, cast

import attrs

from ._base import _FILTER, _MAP, _TAP, PlannedOps, T, U, _BaseSyncStream

if TYPE_CHECKING:
    from ._sync import Stream


@attrs.define(frozen=True)
class ParStream[T](_BaseSyncStream):
    def collect(self, *, workers: int = 4, use_threads: bool = False) -> tuple[U, ...]:
        if workers == -1:
            workers = (os.cpu_count() or 5) - 1

        workers = max(workers, 1)

        executor_cls = ThreadPoolExecutor if use_threads else ProcessPoolExecutor

        batches = [
            (list(chunk), self.ops)
            for chunk in batched(self.seq, n=max(4, len(self.seq) // workers))
        ]

        with executor_cls(max_workers=workers) as ex:
            return cast(
                tuple[U, ...],
                tuple(itertools.chain.from_iterable(ex.map(_apply_fns_worker, batches))),
            )

    def to_stream(self) -> Stream[T]:
        from ._sync import Stream

        return Stream(self.seq, self.ops)

    def to_par(self) -> Self:
        return self


def _apply_fns_worker[T](args: tuple[tuple[T], tuple[PlannedOps, ...]]) -> tuple[T, ...]:
    seq, ops = args

    results = []

    for elem in seq:
        valid = True
        res = elem
        for op, op_fn in ops:
            if op == _MAP:
                res = op_fn(res)
            elif op == _FILTER:
                if not op_fn(res):
                    valid = False
                    break
            elif op == _TAP:
                op_fn(deepcopy(res))
            else:
                raise RuntimeError("Invalid operation selected. Valid options [map, filter, tap]")

        if valid:
            results.append(res)
    return tuple(results)
