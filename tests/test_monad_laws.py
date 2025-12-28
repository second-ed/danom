from hypothesis import given
from hypothesis import strategies as st

from src.danom import Err, Result
from tests.conftest import safe_add_one, safe_double

inners = st.one_of(
    st.integers().map(Result.unit),
    st.text().map(Result.unit),
    st.floats(allow_nan=False, allow_infinity=False).map(Result.unit),
)

results = st.one_of(
    st.integers().map(Result.unit),
    st.text().map(Result.unit),
    st.floats(allow_nan=False, allow_infinity=False).map(Result.unit),
    st.just(Err()),
)


safe_fns = st.sampled_from([safe_double, safe_add_one])


@given(inner=inners, f=safe_fns)
def test_monadic_left_identity(inner, f):
    assert Result.unit(inner).and_then(f) == f(inner)


@given(results)
def test_monadic_right_identity(monad):
    assert monad.and_then(Result.unit) == monad


@given(monad=results, f=safe_fns, g=safe_fns)
def test_monadic_associativity(monad, f, g):
    assert monad.and_then(f).and_then(g) == monad.and_then(lambda x: f(x).and_then(g))
