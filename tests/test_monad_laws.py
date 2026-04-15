from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from danom import Either, Err, Left, Result


def monad_tests(parent: type[Result | Either], err_monad: type[Err | Left]):
    inners = st.one_of(st.integers(), st.text(), st.floats(allow_nan=False, allow_infinity=False))

    results = st.one_of(inners.map(parent.unit), st.just(err_monad(1)))
    safe_fns = st.sampled_from([lambda x: parent.unit(x * 2), err_monad])

    @given(inner=inners, f=safe_fns)
    def test_monadic_left_identity(inner, f):
        assert parent.unit(inner).and_then(f) == f(inner)

    @given(results)
    def test_monadic_right_identity(monad):
        assert monad.and_then(parent.unit) == monad

    @given(monad=results, f=safe_fns, g=safe_fns, h=safe_fns)
    def test_monadic_associativity(monad, f, g, h):
        assert monad.and_then(f).and_then(g).or_else(h) == monad.and_then(
            lambda x: f(x).and_then(g)
        ).or_else(h)

    return test_monadic_left_identity, test_monadic_right_identity, test_monadic_associativity


test_result_left_identity, test_result_right_identity, test_result_associativity = monad_tests(
    Result, Err
)


test_either_left_identity, test_either_right_identity, test_either_associativity = monad_tests(
    Either, Left
)
