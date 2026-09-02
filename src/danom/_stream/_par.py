from __future__ import annotations

import itertools
import os
from collections.abc import Callable, Iterable
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from copy import deepcopy
from functools import partial, reduce
from itertools import batched
from typing import cast

import attrs

from danom._either import Either
from danom._result import Result

from ._base import _FILTER, _MAP, _TAP, E, FilterFn, MapFn, PlannedOps, T, TapFn, U, _BaseStream


@attrs.define(frozen=True)
class ParStream[T](_BaseStream):
    @classmethod
    def from_iterable(cls, it: Iterable) -> ParStream[T]:
        if not isinstance(it, Iterable):
            it = [it]
        return cls(seq=tuple(it))

    def map[**P](self, fn: MapFn, *args: P.args, **kwargs: P.kwargs) -> ParStream[T]:
        plan = (*self.ops, (_MAP, partial(fn, *args, **kwargs)))
        return ParStream(seq=self.seq, ops=plan)

    def filter[**P](self, fn: FilterFn, *args: P.args, **kwargs: P.kwargs) -> ParStream[T]:
        plan = (*self.ops, (_FILTER, partial(fn, *args, **kwargs)))
        return ParStream(seq=self.seq, ops=plan)

    def tap[**P](self, fn: TapFn, *args: P.args, **kwargs: P.kwargs) -> ParStream[T]:
        plan = (*self.ops, (_TAP, partial(fn, *args, **kwargs)))
        return ParStream(seq=self.seq, ops=plan)

    def partition(
        self, fn: FilterFn, *, workers: int = 1, use_threads: bool = False
    ) -> tuple[ParStream, ParStream]:
        # have to materialise to be able to replay each side independently
        seq_tuple = self.collect(workers=workers, use_threads=use_threads)

        pos, neg = [], []

        for x in seq_tuple:
            if not fn(x):
                neg.append(x)
                continue
            pos.append(x)
        return (ParStream.from_iterable(pos), ParStream.from_iterable(neg))

    def sequence(
        self: ParStream[T], *, workers: int = 1, use_threads: bool = False
    ) -> Result[ParStream[T], E] | Either[ParStream[T], E]:
        if not self:
            return Result.unit(self)

        seq_tuple = self.collect(workers=workers, use_threads=use_threads)

        if not all(isinstance(res, (Result, Either)) for res in seq_tuple):
            raise TypeError("All elements in the `ParStream` must be of `Result` or `Either` type")

        results = []

        for res in seq_tuple:
            if not res.is_ok():
                return res
            results.append(res.unwrap())

        return type(res)(ParStream.from_iterable(results))

    def fold(
        self, initial: T, fn: Callable[[T, U], T], *, workers: int = 1, use_threads: bool = False
    ) -> T:
        return reduce(fn, self.collect(workers=workers, use_threads=use_threads), initial)

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
