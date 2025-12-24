from hypothesis import given
from hypothesis import strategies as st

from src.danom import Err, Result
from tests.conftest import safe_add, safe_add_one, safe_double


def test_monadic_left_identity():
    assert Result.unit(0).and_then(safe_add, b=1) == safe_add(0, 1)


results = st.one_of(
    st.integers().map(Result.unit),
    st.text().map(Result.unit),
    st.floats(allow_nan=False, allow_infinity=False).map(Result.unit),
    st.just(Err()),
)


@given(results)
def test_monadic_right_identity(monad):
    assert monad.and_then(Result.unit) == monad


safe_fns = st.sampled_from([safe_double, safe_add_one])


@given(monad=results, f=safe_fns, g=safe_fns)
def test_monadic_associativity(monad, f, g):
    assert monad.and_then(f).and_then(g) == monad.and_then(lambda x: f(x).and_then(g))
