from __future__ import annotations

from collections.abc import Iterable

from danom import AsyncStream, ParStream, Stream
from tests.conftest import add, add_one, divisible_by_3, divisible_by_5, is_even, make_async


def basic_pipeline(
    stream_cls: type[Stream | ParStream], it: Iterable, kwargs: dict | None = None
) -> tuple:
    kwargs = kwargs or {}
    return (
        stream_cls.from_iterable(it)
        .to_par()
        .to_par()
        .map(add_one)
        .map(add_one)
        .filter(divisible_by_3)
        .filter(divisible_by_5)
        .to_stream()
        .to_stream()
        .collect(**kwargs)
    )


def basic_partition(
    stream_cls: type[Stream | ParStream], it: Iterable, kwargs: dict | None = None
) -> tuple:
    kwargs = kwargs or {}
    part1, part2 = stream_cls.from_iterable(it).map(add_one).partition(is_even)

    return (
        part1.map(add, 1).map(add_one).filter(divisible_by_3).collect(**kwargs),
        part2.collect(**kwargs),
    )


async def async_basic_pipeline(
    stream_cls: type[AsyncStream], it: Iterable, kwargs: dict | None = None
) -> tuple:
    kwargs = kwargs or {}
    return await (
        stream_cls.from_iterable(it)
        .map(make_async(add_one))
        .map(make_async(add_one))
        .filter(make_async(divisible_by_3))
        .filter(make_async(divisible_by_5))
    ).collect(**kwargs)


async def async_basic_partition(
    stream_cls: type[AsyncStream], it: Iterable, kwargs: dict | None = None
) -> tuple:
    kwargs = kwargs or {}
    part1, part2 = (
        await stream_cls.from_iterable(it).map(make_async(add_one)).partition(make_async(is_even))
    )

    return (
        await part1.map(make_async(add), 1)
        .map(make_async(add_one))
        .filter(make_async(divisible_by_3))
        .collect(**kwargs),
        await part2.collect(**kwargs),
    )
