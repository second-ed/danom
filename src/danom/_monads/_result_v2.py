from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from copy import deepcopy
from typing import TYPE_CHECKING, Any, Concatenate, Never, cast

import attrs
from attrs.validators import instance_of

if TYPE_CHECKING:
    from ._option import Option


@attrs.define(frozen=True)
class Result[T, E](ABC):
    @classmethod
    def unit(cls, inner: T) -> Result[T, E]:
        """Unit method. Given an item of type ``T`` return ``Ok(T)``

        .. doctest::

            >>> from danom import Err, Ok, Result

            >>> Result.unit(0) == Ok(0)
            True

            >>> Ok.unit(0) == Ok(0)
            True

            >>> Err.unit(0) == Ok(0)
            True
        """
        return cast(Result[T, E], Ok(inner))

    @staticmethod
    def result_is_ok(result: Result[T, E]) -> bool:
        """Check whether the monad is ok. Allows for ``filter`` or ``partition`` in a ``Stream`` without needing a lambda or custom function.

        .. code-block:: python

            from danom import Stream, Result

            Stream.from_iterable([Ok(), Ok(), Err()]).filter(Result.result_is_ok).collect() == (Ok(), Ok())

        """
        return result.is_ok()

    @staticmethod
    def result_unwrap(result: Result[T, E]) -> T:
        """Unwrap the ``Ok`` monad and get the inner value.
        Unwrap the ``Err`` monad will raise the inner error.

        .. code-block:: python

            from danom import Err, Ok, Stream, Result

            oks, errs = Stream.from_iterable([Ok(1), Ok(2), Err()]).partition(Result.result_is_ok)
            oks.map(Result.result_unwrap).collect == (1, 2)

        """
        return result.unwrap()

    @abstractmethod
    def and_[U, F](self, res: Result[U, F]) -> Result[U, F]:
        """Papertrail examples:

        If you call ``and_`` on an ``Ok`` with an ``Err`` as the arg then the ``Err`` takes precedence over the ``Ok``.

        .. code-block:: python

            >>> Ok(inner=2).and_(Err(error="late error")) == Err(error="late error")
            True
        If you call ``and_`` on an ``Err`` with an ``Ok`` as the arg then the ``Err`` still takes precedence over the ``Ok``.

        .. code-block:: python

            >>> Err(error="early error").and_(Ok(inner="foo")) == Err(error="early error")
            True
        If you call ``and_`` on an ``Err`` with an ``Err`` as the arg then the first ``Err`` is returned and the second is discarded.

        .. code-block:: python

            >>> Err(error="not a 2").and_(Err(error="late error")) == Err(error="not a 2")
            True
        Whereas, calling ``and_`` on an ``Ok`` with another ``Ok`` as the arg then the first ``Ok`` is discarded and the second is returned.

        .. code-block:: python

            >>> Ok(inner=2).and_(Ok(inner="different result type")) == Ok(inner="different result type")
            True
        ::
        """
        ...

    @abstractmethod
    def and_then[U, F, **P](
        self, fn: Callable[Concatenate[T, P], Result[U, F]], *args: P.args, **kwargs: P.kwargs
    ) -> Result[U, F]:
        """Papertrail examples:

        An ``Ok`` passed to ``and_then`` returns the ``Ok`` produced by the function.

        .. code-block:: python

            >>> Ok(inner=2).and_then(must_be_less_than_10) == Ok(inner=2)
            True
        When the function passed to ``and_then`` produces an ``Err``, that ``Err`` becomes the result.

        .. code-block:: python

            >>> Ok(inner=20).and_then(must_be_less_than_10) == Err(error="too high")
            True
        An existing ``Err`` passes through ``and_then`` unchanged, without calling the function.

        .. code-block:: python

            >>> Err(error="not a number").and_then(must_be_less_than_10) == Err(error="not a number")
            True
        ::
        """
        ...

    def cloned(self) -> Result[T, E]:
        """Papertrail examples:

        Cloning an ``Ok`` creates a separate ``Ok`` with the same value.

        .. code-block:: python

            >>> Ok(inner=2).cloned() == Ok(inner=2)
            True
        Cloning an ``Err`` creates a separate ``Err`` with the same value.

        .. code-block:: python

            >>> Err(error=2).cloned() == Err(error=2)
            True
        ::
        """
        return deepcopy(self)

    @abstractmethod
    def err(self) -> Option[E]:
        """Papertrail examples:

        An ``Ok`` has no error, so ``err`` returns ``Null``.

        .. code-block:: python

            >>> Ok(inner=2).err() == Null()
            True
        If you call ``err`` on an ``Err`` then ``Some`` with the wrapped error is returned.

        .. code-block:: python

            >>> Err(error="Nothing here").err() == Some(inner="Nothing here")
            True
        ::
        """
        ...

    @abstractmethod
    def expect(self, msg: str) -> T:
        """Papertrail examples:

        ``expect`` extracts the value from an ``Ok``.

        .. code-block:: python

            >>> Ok(inner=2).expect("must be positive") == 2
            True
        ::
        """
        ...

    @abstractmethod
    def expect_err(self, msg: str) -> E:
        """Papertrail examples:

        ``expect_err`` extracts the error from an ``Err``.

        .. code-block:: python

            >>> Err(error=2).expect_err("must be err") == 2
            True
        ::
        """
        ...

    @abstractmethod
    def flatten(self) -> Result[T, E]:
        """Papertrail examples:

        If you call ``flatten`` on three nested ``Ok`` values then two nested ``Ok`` values are returned. Only the outer monad is removed

        .. code-block:: python

            >>> Ok(inner=Ok(inner=Ok(inner=2))).flatten() == Ok(inner=Ok(inner=2))
            True
        This is made obvious calling ``flatten`` on a doubly wrapped value returning just the inner monad.

        .. code-block:: python

            >>> Ok(inner=Ok(inner=2)).flatten() == Ok(inner=2)
            True
        Calling ``flatten`` if the inner is not a monad of the same type is a no-op.

        .. code-block:: python

            >>> Ok(inner=2).flatten() == Ok(inner=2)
            True
        An ``Err`` passes through ``flatten`` unchanged.

        .. code-block:: python

            >>> Err(error=None).flatten() == Err(error=None)
            True
        ::
        """
        ...

    @abstractmethod
    def inspect(self, fn: Callable[[T], None]) -> Result[T, E]:
        """Papertrail examples:

        If you call ``inspect`` on an ``Ok`` then the original ``Ok`` is returned after the function is called, this is used for logging or side outputs that shouldn't disrupt the existing flow.

        .. code-block:: python

            >>> Ok(inner=[1]).inspect(append_to_list) == Ok(inner=[1])
            True
        If you call ``inspect`` on an ``Err`` then the ``Err`` is returned and the function is not called.

        .. code-block:: python

            >>> Err(error="un-appendable").inspect(append_to_list) == Err(error="un-appendable")
            True
        ::
        """
        ...

    @abstractmethod
    def inspect_err(self, fn: Callable[[E], None]) -> Result[T, E]:
        """Papertrail examples:

        If you call ``inspect_err`` on an ``Err`` then the original ``Err`` is returned after the function is called, it's essentially the inverse of ``inspect``.

        .. code-block:: python

            >>> Err(error=[1]).inspect_err(append_to_list) == Err(error=[1])
            True
        Similarly to calling ``inspect`` on an ``Err``, if you call ``inspect_err`` on an ``Ok`` then the ``Ok`` is returned and the function is not called.

        .. code-block:: python

            >>> Ok(inner="un-appendable").inspect_err(append_to_list) == Ok(inner="un-appendable")
            True
        ::
        """
        ...

    @abstractmethod
    def is_err(self) -> bool:
        """Papertrail examples:

        ``is_err`` reports ``False`` for an ``Ok``.

        .. code-block:: python

            >>> Ok(inner=2).is_err() == False
            True
        For an ``Err``, ``is_err`` reports ``True``.

        .. code-block:: python

            >>> Err(error=2).is_err() == True
            True
        ::
        """
        ...

    @abstractmethod
    def is_err_and(self, fn: Callable[[E], bool]) -> bool:
        """Papertrail examples:

        ``is_err_and`` requires both the monad to be an ``Err`` and the returned value of the passed in callable to be ``True``, for example, if you called ``is_err_and`` with a function that checks for evenness on an ``Err(1)`` then the result is ``False``.

        .. code-block:: python

            >>> Err(error=1).is_err_and(is_even) == False
            True
        Therefore, if you call ``is_err_and`` on an ``Err`` with a function that returns ``True`` then ``True`` is returned.

        .. code-block:: python

            >>> Err(error=2).is_err_and(is_even) == True
            True
        Whereas, if you call ``is_err_and`` on an ``Ok`` with a function then ``False`` is returned and the function is not called.

        .. code-block:: python

            >>> Ok(inner=2).is_err_and(is_even) == False
            True
        ::
        """
        ...

    @abstractmethod
    def is_ok(self) -> bool:
        """Papertrail examples:

        ``is_ok`` reports ``True`` for an ``Ok``.

        .. code-block:: python

            >>> Ok(inner=2).is_ok() == True
            True
        For an ``Err``, ``is_ok`` reports ``False``.

        .. code-block:: python

            >>> Err(error=2).is_ok() == False
            True
        ::
        """
        ...

    @abstractmethod
    def is_ok_and(self, fn: Callable[[T], bool]) -> bool:
        """Papertrail examples:

        When the predicate rejects an ``Ok``, ``is_ok_and`` reports ``False``.

        .. code-block:: python

            >>> Ok(inner=1).is_ok_and(is_even) == False
            True
        When the predicate accepts an ``Ok``, ``is_ok_and`` reports ``True``.

        .. code-block:: python

            >>> Ok(inner=2).is_ok_and(is_even) == True
            True
        An ``Err`` makes ``is_ok_and`` report ``False`` without calling the predicate.

        .. code-block:: python

            >>> Err(error=2).is_ok_and(is_even) == False
            True
        ::
        """
        ...

    @abstractmethod
    def map[U, **P](
        self, fn: Callable[Concatenate[T, P], U], *args: P.args, **kwargs: P.kwargs
    ) -> Result[U, E]:
        """Papertrail examples:

        Mapping an ``Ok`` applies the function and wraps its result in a new ``Ok``.

        .. code-block:: python

            >>> Ok(inner=1).map(add_one) == Ok(inner=2)
            True
        Mapping an ``Err`` leaves it unchanged and skips the function.

        .. code-block:: python

            >>> Err(error=1).map(add_one) == Err(error=1)
            True
        ::
        """
        ...

    @abstractmethod
    def map_err[F, **P](
        self, fn: Callable[Concatenate[E, P], F], *args: P.args, **kwargs: P.kwargs
    ) -> Result[T, F]:
        """Papertrail examples:

        Mapping an ``Err`` applies the function and wraps its result in a new ``Err``.

        .. code-block:: python

            >>> Err(error=1).map_err(add_one) == Err(error=2)
            True
        Mapping an ``Ok`` leaves it unchanged and skips the function.

        .. code-block:: python

            >>> Ok(inner=1).map_err(add_one) == Ok(inner=1)
            True
        ::
        """
        ...

    @abstractmethod
    def map_or[U, **P](
        self, default: U, fn: Callable[Concatenate[T, P], U], *args: P.args, **kwargs: P.kwargs
    ) -> U:
        """Papertrail examples:

        For an ``Ok``, ``map_or`` uses the function result instead of the default.

        .. code-block:: python

            >>> Ok(inner="foo").map_or(42, len) == 3
            True
        For an ``Err``, ``map_or`` returns the supplied default.

        .. code-block:: python

            >>> Err(error=None).map_or(42, len) == 42
            True
        ::
        """
        ...

    @abstractmethod
    def map_or_else[U, **P](
        self,
        default: Callable[P, U],
        fn: Callable[Concatenate[T, P], U],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> U:
        """Papertrail examples:

        An ``Ok`` makes ``map_or_else`` use the mapping function.

        .. code-block:: python

            >>> Ok(inner="foo").map_or_else(get_42, len) == 3
            True
        An ``Err`` makes ``map_or_else`` use the default function.

        .. code-block:: python

            >>> Err(error=None).map_or_else(get_42, len) == 42
            True
        ::
        """
        ...

    @abstractmethod
    def ok(self) -> Option[T]:
        """Papertrail examples:

        An ``Ok`` converts to ``Some`` through ``ok``.

        .. code-block:: python

            >>> Ok(inner=2).ok() == Some(inner=2)
            True
        An ``Err`` converts to ``Null`` through ``ok``.

        .. code-block:: python

            >>> Err(error=2).ok() == Null()
            True
        ::
        """
        ...

    @abstractmethod
    def or_[F](self, res: Result[T, F]) -> Result[T, F]:
        """Papertrail examples:

        An ``Ok`` keeps its value when ``or_`` receives an ``Err``.

        .. code-block:: python

            >>> Ok(inner=2).or_(Err(error="foo")) == Ok(inner=2)
            True
        An ``Err`` gives way to an ``Ok`` passed to ``or_``.

        .. code-block:: python

            >>> Err(error="foo").or_(Ok(inner=100)) == Ok(inner=100)
            True
        When both values are ``Ok``, ``or_`` keeps the first one.

        .. code-block:: python

            >>> Ok(inner=2).or_(Ok(inner=100)) == Ok(inner=2)
            True
        When both values are ``Err``, ``or_`` keeps the first error.

        .. code-block:: python

            >>> Err(error="foo").or_(Err(error="foo")) == Err(error="foo")
            True
        ::
        """
        ...

    @abstractmethod
    def or_else[F, **P](
        self, fn: Callable[Concatenate[E, P], F], *args: P.args, **kwargs: P.kwargs
    ) -> Result[T, F]:
        """Papertrail examples:

        An ``Ok`` passes through ``or_else`` without calling the function.

        .. code-block:: python

            >>> Ok(inner="barbarians").or_else(get_ok_vikings) == Ok(inner="barbarians")
            True
        For an ``Err``, ``or_else`` returns the ``Ok`` produced by the function.

        .. code-block:: python

            >>> Err(error="foo").or_else(get_ok_vikings) == Ok(inner="vikings")
            True
        If the fallback also produces an ``Err``, ``or_else`` keeps the original error.

        .. code-block:: python

            >>> Err(error="foo").or_else(Err) == Err(error="foo")
            True
        ::
        """
        ...

    @abstractmethod
    def transpose(self) -> Option[Result[T, E]]:
        """Papertrail examples:

        Transposing ``Ok(Some(value))`` produces ``Some(Ok(value))``.

        .. code-block:: python

            >>> Ok(inner=Some(inner=5)).transpose() == Some(inner=Ok(inner=5))
            True
        Transposing ``Ok(Null())`` produces ``Null``.

        .. code-block:: python

            >>> Ok(inner=Null()).transpose() == Null()
            True
        Transposing an ``Err`` wraps it in ``Some``.

        .. code-block:: python

            >>> Err(error=None).transpose() == Some(inner=Err(error=None))
            True
        ::
        """
        ...

    @abstractmethod
    def unwrap(self) -> T:
        """Papertrail examples:

        ``unwrap`` extracts the value from an ``Ok``.

        .. code-block:: python

            >>> Ok(inner=2).unwrap() == 2
            True
        ::
        """
        ...

    @abstractmethod
    def unwrap_err(self) -> E:
        """Papertrail examples:

        ``unwrap_err`` extracts the error from an ``Err``.

        .. code-block:: python

            >>> Err(error="failed").unwrap_err() == "failed"
            True
        ::
        """
        ...

    @abstractmethod
    def unwrap_or(self, default: T) -> T:
        """Papertrail examples:

        With an ``Ok``, ``unwrap_or`` returns the value and ignores the default.

        .. code-block:: python

            >>> Ok(inner="car").unwrap_or("bike") == "car"
            True
        With an ``Err``, ``unwrap_or`` returns the default.

        .. code-block:: python

            >>> Err(error=None).unwrap_or("bike") == "bike"
            True
        ::
        """
        ...

    @abstractmethod
    def unwrap_or_else(self, fn: Callable[[E], T]) -> T:
        """Papertrail examples:

        An ``Ok`` makes ``unwrap_or_else`` return its value without calling the function.

        .. code-block:: python

            >>> Ok(inner=4).unwrap_or_else(get_42) == 4
            True
        An ``Err`` makes ``unwrap_or_else`` return the function result.

        .. code-block:: python

            >>> Err(error=None).unwrap_or_else(get_42) == 42
            True
        ::
        """
        ...


@attrs.define(frozen=True)
class Ok[T](Result[T, Never]):
    inner: T = attrs.field(default=None)

    def and_[U, E](self, res: Result[U, E]) -> Result[U, E]:
        """Papertrail examples:

        If you call ``and_`` on an ``Ok`` with an ``Err`` as the arg then the ``Err`` takes precedence over the ``Ok``.

        .. code-block:: python

            >>> Ok(inner=2).and_(Err(error="late error")) == Err(error="late error")
            True
        If you call ``and_`` on an ``Err`` with an ``Ok`` as the arg then the ``Err`` still takes precedence over the ``Ok``.

        .. code-block:: python

            >>> Err(error="early error").and_(Ok(inner="foo")) == Err(error="early error")
            True
        If you call ``and_`` on an ``Err`` with an ``Err`` as the arg then the first ``Err`` is returned and the second is discarded.

        .. code-block:: python

            >>> Err(error="not a 2").and_(Err(error="late error")) == Err(error="not a 2")
            True
        Whereas, calling ``and_`` on an ``Ok`` with another ``Ok`` as the arg then the first ``Ok`` is discarded and the second is returned.

        .. code-block:: python

            >>> Ok(inner=2).and_(Ok(inner="different result type")) == Ok(inner="different result type")
            True
        ::
        """
        return res

    def and_then[U, E, **P](
        self, fn: Callable[Concatenate[T, P], Result[U, E]], *args: P.args, **kwargs: P.kwargs
    ) -> Result[U, E]:
        """Papertrail examples:

        An ``Ok`` passed to ``and_then`` returns the ``Ok`` produced by the function.

        .. code-block:: python

            >>> Ok(inner=2).and_then(must_be_less_than_10) == Ok(inner=2)
            True
        When the function passed to ``and_then`` produces an ``Err``, that ``Err`` becomes the result.

        .. code-block:: python

            >>> Ok(inner=20).and_then(must_be_less_than_10) == Err(error="too high")
            True
        An existing ``Err`` passes through ``and_then`` unchanged, without calling the function.

        .. code-block:: python

            >>> Err(error="not a number").and_then(must_be_less_than_10) == Err(error="not a number")
            True
        ::
        """
        return fn(self.inner, *args, **kwargs)

    def err[E](self) -> Option[E]:
        """Papertrail examples:

        An ``Ok`` has no error, so ``err`` returns ``Null``.

        .. code-block:: python

            >>> Ok(inner=2).err() == Null()
            True
        If you call ``err`` on an ``Err`` then ``Some`` with the wrapped error is returned.

        .. code-block:: python

            >>> Err(error="Nothing here").err() == Some(inner="Nothing here")
            True
        ::
        """
        from ._option import Null  # noqa: PLC0415

        return Null()

    def expect(self, msg: str) -> T:  # noqa: ARG002
        """Papertrail examples:

        ``expect`` extracts the value from an ``Ok``.

        .. code-block:: python

            >>> Ok(inner=2).expect("must be positive") == 2
            True
        ::
        """
        return self.inner

    def expect_err(self, msg: str) -> Never:
        """Papertrail examples:

        ``expect_err`` extracts the error from an ``Err``.

        .. code-block:: python

            >>> Err(error=2).expect_err("must be err") == 2
            True
        ::
        """
        raise ValueError(msg)

    def flatten(self) -> Result[T, Never]:
        """Papertrail examples:

        If you call ``flatten`` on three nested ``Ok`` values then two nested ``Ok`` values are returned. Only the outer monad is removed

        .. code-block:: python

            >>> Ok(inner=Ok(inner=Ok(inner=2))).flatten() == Ok(inner=Ok(inner=2))
            True
        This is made obvious calling ``flatten`` on a doubly wrapped value returning just the inner monad.

        .. code-block:: python

            >>> Ok(inner=Ok(inner=2)).flatten() == Ok(inner=2)
            True
        Calling ``flatten`` if the inner is not a monad of the same type is a no-op.

        .. code-block:: python

            >>> Ok(inner=2).flatten() == Ok(inner=2)
            True
        An ``Err`` passes through ``flatten`` unchanged.

        .. code-block:: python

            >>> Err(error=None).flatten() == Err(error=None)
            True
        ::
        """
        if isinstance(self.inner, Result):
            return cast(Result[T, Never], self.inner)
        return cast(Result[T, Never], self)

    def inspect(self, fn: Callable[[T], None]) -> Result[T, Never]:
        """Papertrail examples:

        If you call ``inspect`` on an ``Ok`` then the original ``Ok`` is returned after the function is called, this is used for logging or side outputs that shouldn't disrupt the existing flow.

        .. code-block:: python

            >>> Ok(inner=[1]).inspect(append_to_list) == Ok(inner=[1])
            True
        If you call ``inspect`` on an ``Err`` then the ``Err`` is returned and the function is not called.

        .. code-block:: python

            >>> Err(error="un-appendable").inspect(append_to_list) == Err(error="un-appendable")
            True
        ::
        """
        fn(deepcopy(self.inner))
        return self

    def inspect_err(self, fn: Callable[[Never], None]) -> Result[T, Never]:  # noqa: ARG002
        """Papertrail examples:

        If you call ``inspect_err`` on an ``Err`` then the original ``Err`` is returned after the function is called, it's essentially the inverse of ``inspect``.

        .. code-block:: python

            >>> Err(error=[1]).inspect_err(append_to_list) == Err(error=[1])
            True
        Similarly to calling ``inspect`` on an ``Err``, if you call ``inspect_err`` on an ``Ok`` then the ``Ok`` is returned and the function is not called.

        .. code-block:: python

            >>> Ok(inner="un-appendable").inspect_err(append_to_list) == Ok(inner="un-appendable")
            True
        ::
        """
        return self

    def is_err(self) -> bool:
        """Papertrail examples:

        ``is_err`` reports ``False`` for an ``Ok``.

        .. code-block:: python

            >>> Ok(inner=2).is_err() == False
            True
        For an ``Err``, ``is_err`` reports ``True``.

        .. code-block:: python

            >>> Err(error=2).is_err() == True
            True
        ::
        """
        return False

    def is_err_and(self, fn: Callable[[Never], bool]) -> bool:  # noqa: ARG002
        """Papertrail examples:

        ``is_err_and`` requires both the monad to be an ``Err`` and the returned value of the passed in callable to be ``True``, for example, if you called ``is_err_and`` with a function that checks for evenness on an ``Err(1)`` then the result is ``False``.

        .. code-block:: python

            >>> Err(error=1).is_err_and(is_even) == False
            True
        Therefore, if you call ``is_err_and`` on an ``Err`` with a function that returns ``True`` then ``True`` is returned.

        .. code-block:: python

            >>> Err(error=2).is_err_and(is_even) == True
            True
        Whereas, if you call ``is_err_and`` on an ``Ok`` with a function then ``False`` is returned and the function is not called.

        .. code-block:: python

            >>> Ok(inner=2).is_err_and(is_even) == False
            True
        ::
        """
        return False

    def is_ok(self) -> bool:
        """Papertrail examples:

        ``is_ok`` reports ``True`` for an ``Ok``.

        .. code-block:: python

            >>> Ok(inner=2).is_ok() == True
            True
        For an ``Err``, ``is_ok`` reports ``False``.

        .. code-block:: python

            >>> Err(error=2).is_ok() == False
            True
        ::
        """
        return True

    def is_ok_and(self, fn: Callable[[T], bool]) -> bool:
        """Papertrail examples:

        When the predicate rejects an ``Ok``, ``is_ok_and`` reports ``False``.

        .. code-block:: python

            >>> Ok(inner=1).is_ok_and(is_even) == False
            True
        When the predicate accepts an ``Ok``, ``is_ok_and`` reports ``True``.

        .. code-block:: python

            >>> Ok(inner=2).is_ok_and(is_even) == True
            True
        An ``Err`` makes ``is_ok_and`` report ``False`` without calling the predicate.

        .. code-block:: python

            >>> Err(error=2).is_ok_and(is_even) == False
            True
        ::
        """
        return fn(self.inner)

    def map[U, **P](
        self, fn: Callable[Concatenate[T, P], U], *args: P.args, **kwargs: P.kwargs
    ) -> Result[U, Never]:
        """Papertrail examples:

        Mapping an ``Ok`` applies the function and wraps its result in a new ``Ok``.

        .. code-block:: python

            >>> Ok(inner=1).map(add_one) == Ok(inner=2)
            True
        Mapping an ``Err`` leaves it unchanged and skips the function.

        .. code-block:: python

            >>> Err(error=1).map(add_one) == Err(error=1)
            True
        ::
        """
        return Ok(fn(self.inner, *args, **kwargs))

    def map_err[F, **P](
        self,
        fn: Callable[Concatenate[Never, P], F],  # noqa: ARG002
        *args: P.args,  # noqa: ARG002
        **kwargs: P.kwargs,  # noqa: ARG002
    ) -> Result[T, F]:
        """Papertrail examples:

        Mapping an ``Err`` applies the function and wraps its result in a new ``Err``.

        .. code-block:: python

            >>> Err(error=1).map_err(add_one) == Err(error=2)
            True
        Mapping an ``Ok`` leaves it unchanged and skips the function.

        .. code-block:: python

            >>> Ok(inner=1).map_err(add_one) == Ok(inner=1)
            True
        ::
        """
        return cast(Result[T, F], self)

    def map_or[U, **P](
        self,
        default: U,  # noqa: ARG002
        fn: Callable[Concatenate[T, P], U],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> U:
        """Papertrail examples:

        For an ``Ok``, ``map_or`` uses the function result instead of the default.

        .. code-block:: python

            >>> Ok(inner="foo").map_or(42, len) == 3
            True
        For an ``Err``, ``map_or`` returns the supplied default.

        .. code-block:: python

            >>> Err(error=None).map_or(42, len) == 42
            True
        ::
        """
        return fn(self.inner, *args, **kwargs)

    def map_or_else[U, **P](
        self,
        default: Callable[P, U],  # noqa: ARG002
        fn: Callable[Concatenate[T, P], U],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> U:
        """Papertrail examples:

        An ``Ok`` makes ``map_or_else`` use the mapping function.

        .. code-block:: python

            >>> Ok(inner="foo").map_or_else(get_42, len) == 3
            True
        An ``Err`` makes ``map_or_else`` use the default function.

        .. code-block:: python

            >>> Err(error=None).map_or_else(get_42, len) == 42
            True
        ::
        """
        return fn(self.inner, *args, **kwargs)

    def ok(self) -> Option[T]:
        """Papertrail examples:

        An ``Ok`` converts to ``Some`` through ``ok``.

        .. code-block:: python

            >>> Ok(inner=2).ok() == Some(inner=2)
            True
        An ``Err`` converts to ``Null`` through ``ok``.

        .. code-block:: python

            >>> Err(error=2).ok() == Null()
            True
        ::
        """
        from ._option import Some  # noqa: PLC0415

        return Some(self.inner)

    def or_[F](self, res: Result[T, F]) -> Result[T, F]:  # noqa: ARG002
        """Papertrail examples:

        An ``Ok`` keeps its value when ``or_`` receives an ``Err``.

        .. code-block:: python

            >>> Ok(inner=2).or_(Err(error="foo")) == Ok(inner=2)
            True
        An ``Err`` gives way to an ``Ok`` passed to ``or_``.

        .. code-block:: python

            >>> Err(error="foo").or_(Ok(inner=100)) == Ok(inner=100)
            True
        When both values are ``Ok``, ``or_`` keeps the first one.

        .. code-block:: python

            >>> Ok(inner=2).or_(Ok(inner=100)) == Ok(inner=2)
            True
        When both values are ``Err``, ``or_`` keeps the first error.

        .. code-block:: python

            >>> Err(error="foo").or_(Err(error="foo")) == Err(error="foo")
            True
        ::
        """
        return cast(Result[T, F], self)

    def or_else[F, **P](
        self,
        fn: Callable[Concatenate[Never, P], F],  # noqa: ARG002
        *args: P.args,  # noqa: ARG002
        **kwargs: P.kwargs,  # noqa: ARG002
    ) -> Result[T, F]:
        """Papertrail examples:

        An ``Ok`` passes through ``or_else`` without calling the function.

        .. code-block:: python

            >>> Ok(inner="barbarians").or_else(get_ok_vikings) == Ok(inner="barbarians")
            True
        For an ``Err``, ``or_else`` returns the ``Ok`` produced by the function.

        .. code-block:: python

            >>> Err(error="foo").or_else(get_ok_vikings) == Ok(inner="vikings")
            True
        If the fallback also produces an ``Err``, ``or_else`` keeps the original error.

        .. code-block:: python

            >>> Err(error="foo").or_else(Err) == Err(error="foo")
            True
        ::
        """
        return cast(Result[T, F], self)

    def transpose(self) -> Option[Result[T, Never]]:
        """Papertrail examples:

        Transposing ``Ok(Some(value))`` produces ``Some(Ok(value))``.

        .. code-block:: python

            >>> Ok(inner=Some(inner=5)).transpose() == Some(inner=Ok(inner=5))
            True
        Transposing ``Ok(Null())`` produces ``Null``.

        .. code-block:: python

            >>> Ok(inner=Null()).transpose() == Null()
            True
        Transposing an ``Err`` wraps it in ``Some``.

        .. code-block:: python

            >>> Err(error=None).transpose() == Some(inner=Err(error=None))
            True
        ::
        """
        from ._option import Null, Some  # noqa: PLC0415

        if isinstance(self.inner, Some):
            return Some(Ok(self.inner.inner))
        if isinstance(self.inner, Null):
            return Null()
        raise TypeError("inner must be an `Option` type")

    def unwrap(self) -> T:
        """Papertrail examples:

        ``unwrap`` extracts the value from an ``Ok``.

        .. code-block:: python

            >>> Ok(inner=2).unwrap() == 2
            True
        ::
        """
        return self.inner

    def unwrap_err(self) -> Never:
        """Papertrail examples:

        ``unwrap_err`` extracts the error from an ``Err``.

        .. code-block:: python

            >>> Err(error="failed").unwrap_err() == "failed"
            True
        ::
        """
        raise TypeError("Can't call `unwrap_err` on `Ok`")

    def unwrap_or(self, default: T) -> T:  # noqa: ARG002
        """Papertrail examples:

        With an ``Ok``, ``unwrap_or`` returns the value and ignores the default.

        .. code-block:: python

            >>> Ok(inner="car").unwrap_or("bike") == "car"
            True
        With an ``Err``, ``unwrap_or`` returns the default.

        .. code-block:: python

            >>> Err(error=None).unwrap_or("bike") == "bike"
            True
        ::
        """
        return self.inner

    def unwrap_or_else(self, fn: Callable[[Never], T]) -> T:  # noqa: ARG002
        """Papertrail examples:

        An ``Ok`` makes ``unwrap_or_else`` return its value without calling the function.

        .. code-block:: python

            >>> Ok(inner=4).unwrap_or_else(get_42) == 4
            True
        An ``Err`` makes ``unwrap_or_else`` return the function result.

        .. code-block:: python

            >>> Err(error=None).unwrap_or_else(get_42) == 42
            True
        ::
        """
        return self.inner


SafeArgs = tuple[tuple[Any, ...], dict[str, Any]]
SafeMethodArgs = tuple[object, tuple[Any, ...], dict[str, Any]]


@attrs.define(frozen=True)
class Err[E](Result[Never, E]):
    error: E = attrs.field(default=None)
    input_args: tuple[()] | SafeArgs | SafeMethodArgs = attrs.field(
        default=(), validator=instance_of(tuple), repr=False
    )
    traceback: str = attrs.field(default="", validator=instance_of(str), repr=False)

    def and_[U, F](self, res: Result[U, F]) -> Result[U, F]:  # noqa: ARG002
        """Papertrail examples:

        If you call ``and_`` on an ``Ok`` with an ``Err`` as the arg then the ``Err`` takes precedence over the ``Ok``.

        .. code-block:: python

            >>> Ok(inner=2).and_(Err(error="late error")) == Err(error="late error")
            True
        If you call ``and_`` on an ``Err`` with an ``Ok`` as the arg then the ``Err`` still takes precedence over the ``Ok``.

        .. code-block:: python

            >>> Err(error="early error").and_(Ok(inner="foo")) == Err(error="early error")
            True
        If you call ``and_`` on an ``Err`` with an ``Err`` as the arg then the first ``Err`` is returned and the second is discarded.

        .. code-block:: python

            >>> Err(error="not a 2").and_(Err(error="late error")) == Err(error="not a 2")
            True
        Whereas, calling ``and_`` on an ``Ok`` with another ``Ok`` as the arg then the first ``Ok`` is discarded and the second is returned.

        .. code-block:: python

            >>> Ok(inner=2).and_(Ok(inner="different result type")) == Ok(inner="different result type")
            True
        ::
        """
        return cast(Result[U, F], self)

    def and_then[U, F, **P](
        self,
        fn: Callable[Concatenate[Never, P], Result[U, F]],  # noqa: ARG002
        *args: P.args,  # noqa: ARG002
        **kwargs: P.kwargs,  # noqa: ARG002
    ) -> Result[U, F]:
        """Papertrail examples:

        An ``Ok`` passed to ``and_then`` returns the ``Ok`` produced by the function.

        .. code-block:: python

            >>> Ok(inner=2).and_then(must_be_less_than_10) == Ok(inner=2)
            True
        When the function passed to ``and_then`` produces an ``Err``, that ``Err`` becomes the result.

        .. code-block:: python

            >>> Ok(inner=20).and_then(must_be_less_than_10) == Err(error="too high")
            True
        An existing ``Err`` passes through ``and_then`` unchanged, without calling the function.

        .. code-block:: python

            >>> Err(error="not a number").and_then(must_be_less_than_10) == Err(error="not a number")
            True
        ::
        """
        return cast(Result[U, F], self)

    def err(self) -> Option[E]:
        """Papertrail examples:

        An ``Ok`` has no error, so ``err`` returns ``Null``.

        .. code-block:: python

            >>> Ok(inner=2).err() == Null()
            True
        If you call ``err`` on an ``Err`` then ``Some`` with the wrapped error is returned.

        .. code-block:: python

            >>> Err(error="Nothing here").err() == Some(inner="Nothing here")
            True
        ::
        """
        from ._option import Some  # noqa: PLC0415

        return Some(self.error)

    def expect(self, msg: str) -> Never:
        """Papertrail examples:

        ``expect`` extracts the value from an ``Ok``.

        .. code-block:: python

            >>> Ok(inner=2).expect("must be positive") == 2
            True
        ::
        """
        raise ValueError(msg)

    def expect_err(self, msg: str) -> E:  # noqa: ARG002
        """Papertrail examples:

        ``expect_err`` extracts the error from an ``Err``.

        .. code-block:: python

            >>> Err(error=2).expect_err("must be err") == 2
            True
        ::
        """
        return self.error

    def flatten(self) -> Result[Never, E]:
        """Papertrail examples:

        If you call ``flatten`` on three nested ``Ok`` values then two nested ``Ok`` values are returned. Only the outer monad is removed

        .. code-block:: python

            >>> Ok(inner=Ok(inner=Ok(inner=2))).flatten() == Ok(inner=Ok(inner=2))
            True
        This is made obvious calling ``flatten`` on a doubly wrapped value returning just the inner monad.

        .. code-block:: python

            >>> Ok(inner=Ok(inner=2)).flatten() == Ok(inner=2)
            True
        Calling ``flatten`` if the inner is not a monad of the same type is a no-op.

        .. code-block:: python

            >>> Ok(inner=2).flatten() == Ok(inner=2)
            True
        An ``Err`` passes through ``flatten`` unchanged.

        .. code-block:: python

            >>> Err(error=None).flatten() == Err(error=None)
            True
        ::
        """
        return self

    def inspect(self, fn: Callable[[Never], None]) -> Result[Never, E]:  # noqa: ARG002
        """Papertrail examples:

        If you call ``inspect`` on an ``Ok`` then the original ``Ok`` is returned after the function is called, this is used for logging or side outputs that shouldn't disrupt the existing flow.

        .. code-block:: python

            >>> Ok(inner=[1]).inspect(append_to_list) == Ok(inner=[1])
            True
        If you call ``inspect`` on an ``Err`` then the ``Err`` is returned and the function is not called.

        .. code-block:: python

            >>> Err(error="un-appendable").inspect(append_to_list) == Err(error="un-appendable")
            True
        ::
        """
        return self

    def inspect_err(self, fn: Callable[[E], None]) -> Result[Never, E]:
        """Papertrail examples:

        If you call ``inspect_err`` on an ``Err`` then the original ``Err`` is returned after the function is called, it's essentially the inverse of ``inspect``.

        .. code-block:: python

            >>> Err(error=[1]).inspect_err(append_to_list) == Err(error=[1])
            True
        Similarly to calling ``inspect`` on an ``Err``, if you call ``inspect_err`` on an ``Ok`` then the ``Ok`` is returned and the function is not called.

        .. code-block:: python

            >>> Ok(inner="un-appendable").inspect_err(append_to_list) == Ok(inner="un-appendable")
            True
        ::
        """
        fn(deepcopy(self.error))
        return self

    def is_err(self) -> bool:
        """Papertrail examples:

        ``is_err`` reports ``False`` for an ``Ok``.

        .. code-block:: python

            >>> Ok(inner=2).is_err() == False
            True
        For an ``Err``, ``is_err`` reports ``True``.

        .. code-block:: python

            >>> Err(error=2).is_err() == True
            True
        ::
        """
        return True

    def is_err_and(self, fn: Callable[[E], bool]) -> bool:
        """Papertrail examples:

        ``is_err_and`` requires both the monad to be an ``Err`` and the returned value of the passed in callable to be ``True``, for example, if you called ``is_err_and`` with a function that checks for evenness on an ``Err(1)`` then the result is ``False``.

        .. code-block:: python

            >>> Err(error=1).is_err_and(is_even) == False
            True
        Therefore, if you call ``is_err_and`` on an ``Err`` with a function that returns ``True`` then ``True`` is returned.

        .. code-block:: python

            >>> Err(error=2).is_err_and(is_even) == True
            True
        Whereas, if you call ``is_err_and`` on an ``Ok`` with a function then ``False`` is returned and the function is not called.

        .. code-block:: python

            >>> Ok(inner=2).is_err_and(is_even) == False
            True
        ::
        """
        return fn(self.error)

    def is_ok(self) -> bool:
        """Papertrail examples:

        ``is_ok`` reports ``True`` for an ``Ok``.

        .. code-block:: python

            >>> Ok(inner=2).is_ok() == True
            True
        For an ``Err``, ``is_ok`` reports ``False``.

        .. code-block:: python

            >>> Err(error=2).is_ok() == False
            True
        ::
        """
        return False

    def is_ok_and(self, fn: Callable[[Never], bool]) -> bool:  # noqa: ARG002
        """Papertrail examples:

        When the predicate rejects an ``Ok``, ``is_ok_and`` reports ``False``.

        .. code-block:: python

            >>> Ok(inner=1).is_ok_and(is_even) == False
            True
        When the predicate accepts an ``Ok``, ``is_ok_and`` reports ``True``.

        .. code-block:: python

            >>> Ok(inner=2).is_ok_and(is_even) == True
            True
        An ``Err`` makes ``is_ok_and`` report ``False`` without calling the predicate.

        .. code-block:: python

            >>> Err(error=2).is_ok_and(is_even) == False
            True
        ::
        """
        return False

    def map[U, **P](
        self,
        fn: Callable[Concatenate[Never, P], U],  # noqa: ARG002
        *args: P.args,  # noqa: ARG002
        **kwargs: P.kwargs,  # noqa: ARG002
    ) -> Result[U, E]:
        """Papertrail examples:

        Mapping an ``Ok`` applies the function and wraps its result in a new ``Ok``.

        .. code-block:: python

            >>> Ok(inner=1).map(add_one) == Ok(inner=2)
            True
        Mapping an ``Err`` leaves it unchanged and skips the function.

        .. code-block:: python

            >>> Err(error=1).map(add_one) == Err(error=1)
            True
        ::
        """
        return cast(Result[U, E], self)

    def map_err[F, **P](
        self, fn: Callable[Concatenate[E, P], F], *args: P.args, **kwargs: P.kwargs
    ) -> Result[Never, F]:
        """Papertrail examples:

        Mapping an ``Err`` applies the function and wraps its result in a new ``Err``.

        .. code-block:: python

            >>> Err(error=1).map_err(add_one) == Err(error=2)
            True
        Mapping an ``Ok`` leaves it unchanged and skips the function.

        .. code-block:: python

            >>> Ok(inner=1).map_err(add_one) == Ok(inner=1)
            True
        ::
        """
        return Err(
            fn(self.error, *args, **kwargs), input_args=self.input_args, traceback=self.traceback
        )

    def map_or[U, **P](
        self,
        default: U,
        fn: Callable[Concatenate[Never, P], U],  # noqa: ARG002
        *args: P.args,  # noqa: ARG002
        **kwargs: P.kwargs,  # noqa: ARG002
    ) -> U:
        """Papertrail examples:

        For an ``Ok``, ``map_or`` uses the function result instead of the default.

        .. code-block:: python

            >>> Ok(inner="foo").map_or(42, len) == 3
            True
        For an ``Err``, ``map_or`` returns the supplied default.

        .. code-block:: python

            >>> Err(error=None).map_or(42, len) == 42
            True
        ::
        """
        return default

    def map_or_else[U, **P](
        self,
        default: Callable[P, U],
        fn: Callable[Concatenate[Never, P], U],  # noqa: ARG002
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> U:
        """Papertrail examples:

        An ``Ok`` makes ``map_or_else`` use the mapping function.

        .. code-block:: python

            >>> Ok(inner="foo").map_or_else(get_42, len) == 3
            True
        An ``Err`` makes ``map_or_else`` use the default function.

        .. code-block:: python

            >>> Err(error=None).map_or_else(get_42, len) == 42
            True
        ::
        """
        return default(*args, **kwargs)

    def ok(self) -> Option[Never]:
        """Papertrail examples:

        An ``Ok`` converts to ``Some`` through ``ok``.

        .. code-block:: python

            >>> Ok(inner=2).ok() == Some(inner=2)
            True
        An ``Err`` converts to ``Null`` through ``ok``.

        .. code-block:: python

            >>> Err(error=2).ok() == Null()
            True
        ::
        """
        from ._option import Null  # noqa: PLC0415

        return Null()

    def or_[F](self, res: Result[Never, F]) -> Result[Never, F]:
        """Papertrail examples:

        An ``Ok`` keeps its value when ``or_`` receives an ``Err``.

        .. code-block:: python

            >>> Ok(inner=2).or_(Err(error="foo")) == Ok(inner=2)
            True
        An ``Err`` gives way to an ``Ok`` passed to ``or_``.

        .. code-block:: python

            >>> Err(error="foo").or_(Ok(inner=100)) == Ok(inner=100)
            True
        When both values are ``Ok``, ``or_`` keeps the first one.

        .. code-block:: python

            >>> Ok(inner=2).or_(Ok(inner=100)) == Ok(inner=2)
            True
        When both values are ``Err``, ``or_`` keeps the first error.

        .. code-block:: python

            >>> Err(error="foo").or_(Err(error="foo")) == Err(error="foo")
            True
        ::
        """
        return res

    def or_else[F, **P](
        self, fn: Callable[Concatenate[E, P], F], *args: P.args, **kwargs: P.kwargs
    ) -> Result[Never, F]:
        """Papertrail examples:

        An ``Ok`` passes through ``or_else`` without calling the function.

        .. code-block:: python

            >>> Ok(inner="barbarians").or_else(get_ok_vikings) == Ok(inner="barbarians")
            True
        For an ``Err``, ``or_else`` returns the ``Ok`` produced by the function.

        .. code-block:: python

            >>> Err(error="foo").or_else(get_ok_vikings) == Ok(inner="vikings")
            True
        If the fallback also produces an ``Err``, ``or_else`` keeps the original error.

        .. code-block:: python

            >>> Err(error="foo").or_else(Err) == Err(error="foo")
            True
        ::
        """
        return cast(Result[Never, F], fn(self.error, *args, **kwargs))

    def transpose(self) -> Option[Result[Never, E]]:
        """Papertrail examples:

        Transposing ``Ok(Some(value))`` produces ``Some(Ok(value))``.

        .. code-block:: python

            >>> Ok(inner=Some(inner=5)).transpose() == Some(inner=Ok(inner=5))
            True
        Transposing ``Ok(Null())`` produces ``Null``.

        .. code-block:: python

            >>> Ok(inner=Null()).transpose() == Null()
            True
        Transposing an ``Err`` wraps it in ``Some``.

        .. code-block:: python

            >>> Err(error=None).transpose() == Some(inner=Err(error=None))
            True
        ::
        """
        from ._option import Some  # noqa: PLC0415

        return Some(self)

    def unwrap(self) -> Never:
        """Papertrail examples:

        ``unwrap`` extracts the value from an ``Ok``.

        .. code-block:: python

            >>> Ok(inner=2).unwrap() == 2
            True
        ::
        """
        if isinstance(self.error, Exception):
            raise self.error
        raise TypeError("Can't call `unwrap` on `Err`")

    def unwrap_err(self) -> E:
        """Papertrail examples:

        ``unwrap_err`` extracts the error from an ``Err``.

        .. code-block:: python

            >>> Err(error="failed").unwrap_err() == "failed"
            True
        ::
        """
        return self.error

    def unwrap_or[U](self, default: U) -> U:
        """Papertrail examples:

        With an ``Ok``, ``unwrap_or`` returns the value and ignores the default.

        .. code-block:: python

            >>> Ok(inner="car").unwrap_or("bike") == "car"
            True
        With an ``Err``, ``unwrap_or`` returns the default.

        .. code-block:: python

            >>> Err(error=None).unwrap_or("bike") == "bike"
            True
        ::
        """
        return default

    def unwrap_or_else[U](self, fn: Callable[[E], U]) -> U:
        """Papertrail examples:

        An ``Ok`` makes ``unwrap_or_else`` return its value without calling the function.

        .. code-block:: python

            >>> Ok(inner=4).unwrap_or_else(get_42) == 4
            True
        An ``Err`` makes ``unwrap_or_else`` return the function result.

        .. code-block:: python

            >>> Err(error=None).unwrap_or_else(get_42) == 42
            True
        ::
        """
        return fn(self.error)
