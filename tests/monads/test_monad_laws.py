from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from danom import Either, Err, Left, Ok, Result, Right, identity


def monad_tests(
    parent: type[Result | Either], ok_monad: type[Ok | Right], err_monad: type[Err | Left]
):
    inners = st.one_of(st.integers(), st.text(), st.floats(allow_nan=False, allow_infinity=False))

    results = st.one_of(inners.map(parent.unit), st.just(err_monad(1)))
    safe_fns = st.sampled_from([lambda x: parent.unit(x * 2), err_monad])

    @given(inner=inners, f=safe_fns)
    def test_monadic_left_identity(inner, f) -> None:
        assert parent.unit(inner).and_then(f) == f(inner)

    @given(results)
    def test_monadic_right_identity(monad) -> None:
        assert monad.and_then(parent.unit) == monad

    @given(monad=results, f=safe_fns, g=safe_fns, h=safe_fns)
    def test_monadic_associativity(monad, f, g, h) -> None:
        assert monad.and_then(f).and_then(g).or_else(h) == monad.and_then(
            lambda x: f(x).and_then(g)
        ).or_else(h)

    st_results = st.integers().map(ok_monad) | st.text().map(err_monad)
    st_nested_results = st.recursive(
        st_results, lambda children: st.one_of(children.map(ok_monad)), max_leaves=5
    )
    st_nested_errs = st.recursive(
        st_results, lambda children: st.one_of(children.map(err_monad)), max_leaves=5
    )

    @given(monad=st_nested_results)
    def test_flatten_idempotent(monad) -> None:
        assert monad.flatten().flatten() == monad.flatten()

    @given(monad=st_results)
    def test_flatten_noop_for_flat_monad(monad) -> None:
        assert monad.flatten() == monad

    @given(monad=st_nested_results)
    def test_and_then_flattens(monad) -> None:
        assert monad.flatten() == monad.and_then(identity)

    @given(monad=st_nested_errs)
    def test_or_else_flattens(monad) -> None:
        if isinstance(monad, Result):
            pytest.skip("or_else flatten law not defined for Result")
        assert monad.flatten() == monad.or_else(identity)

    return (
        test_monadic_left_identity,
        test_monadic_right_identity,
        test_monadic_associativity,
        test_flatten_idempotent,
        test_flatten_noop_for_flat_monad,
        test_and_then_flattens,
        test_or_else_flattens,
    )


(
    test_result_left_identity,
    test_result_right_identity,
    test_result_associativity,
    test_result_flatten_idempotent,
    test_result_flatten_noop_for_flat_monad,
    test_result_and_then_flattens,
    test_result_or_else_flattens,
) = monad_tests(Result, Ok, Err)


(
    test_either_left_identity,
    test_either_right_identity,
    test_either_associativity,
    test_either_flatten_idempotent,
    test_either_flatten_noop_for_flat_monad,
    test_either_and_then_flattens,
    test_either_or_else_flattens,
) = monad_tests(Either, Right, Left)
