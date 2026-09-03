from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Iterable
from copy import deepcopy
from functools import partial, reduce
from typing import cast

import attrs

from danom import Either, Result

from ._base import _FILTER, _MAP, _TAP, E, FilterFn, MapFn, P, S, T, TapFn, U, _BaseStream

AsyncMapFn = Callable[P, Awaitable[U]]
AsyncFilterFn = Callable[P, Awaitable[bool]]
AsyncTapFn = Callable[P, Awaitable[None]]
AsyncStreamFn = AsyncMapFn | AsyncFilterFn | AsyncTapFn


@attrs.define(frozen=True)
class AsyncStream[T](_BaseStream):
    @classmethod
    def from_iterable(cls, it: Iterable) -> AsyncStream[T]:
        if not isinstance(it, Iterable):
            it = [it]
        return cls(seq=tuple(it))

    def map[**P](self, fn: MapFn | AsyncMapFn, *args: P.args, **kwargs: P.kwargs) -> AsyncStream[T]:
        plan = (*self.ops, (_MAP, partial(fn, *args, **kwargs)))
        return AsyncStream(seq=self.seq, ops=plan)

    def filter[**P](
        self, fn: FilterFn | AsyncFilterFn, *args: P.args, **kwargs: P.kwargs
    ) -> AsyncStream[T]:
        plan = (*self.ops, (_FILTER, partial(fn, *args, **kwargs)))
        return AsyncStream(seq=self.seq, ops=plan)

    def tap[**P](self, fn: TapFn | AsyncTapFn, *args: P.args, **kwargs: P.kwargs) -> AsyncStream[T]:
        plan = (*self.ops, (_TAP, partial(fn, *args, **kwargs)))
        return AsyncStream(seq=self.seq, ops=plan)

    async def partition(
        self, fn: FilterFn, *, workers: int = 1, use_threads: bool = False
    ) -> tuple[AsyncStream[T], AsyncStream[U]]:
        # have to materialise to be able to replay each side independently
        seq_tuple = await self.collect(workers=workers, use_threads=use_threads)

        pos, neg = [], []

        for x in seq_tuple:
            if not fn(x):
                neg.append(x)
                continue
            pos.append(x)
        return (AsyncStream.from_iterable(pos), AsyncStream.from_iterable(neg))

    async def sequence(  # ty: ignore[invalid-method-override]
        self: AsyncStream[T], *, workers: int = 1, use_threads: bool = False
    ) -> Result[S, E] | Either[S, E]:
        if not self:
            return Result.unit(self)

        seq_tuple = await self.collect(workers=workers, use_threads=use_threads)

        if not all(isinstance(res, (Result, Either)) for res in seq_tuple):
            raise TypeError(
                "All elements in the `AsyncStream` must be of `Result` or `Either` type"
            )

        results = []

        for res in seq_tuple:
            if not res.is_ok():
                return res
            results.append(res.unwrap())

        return type(res)(AsyncStream.from_iterable(results))

    async def fold(
        self, initial: T, fn: Callable[[T, U], T], *, workers: int = 1, use_threads: bool = False
    ) -> T:
        return reduce(fn, await self.collect(workers=workers, use_threads=use_threads), initial)

    async def collect(
        self,
        *,
        workers: int = 4,  # noqa: ARG002
        use_threads: bool = False,  # noqa: ARG002
    ) -> tuple[U, ...]:
        if not self.ops:
            return self.seq

        res = await asyncio.gather(*(_async_apply_fns(x, self.ops) for x in self.seq))
        return cast(tuple[U, ...], tuple(elem for elem in res if elem != NOTHING))


NOTHING = object()
AsyncPlannedOps = tuple[str, AsyncStreamFn]


async def _async_apply_fns[T](elem: T, ops: tuple[AsyncPlannedOps, ...]) -> T | object:
    res = elem
    for op, op_fn in ops:
        if op == _MAP:
            res = await op_fn(res)
        elif op == _FILTER and not await op_fn(res):
            return NOTHING
        elif op == _TAP:
            await op_fn(deepcopy(res))
    return res
