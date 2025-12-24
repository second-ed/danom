import pytest

from src.danom import Err, Ok, Result
from tests.conftest import safe_add, safe_add_one


@pytest.mark.parametrize(
    ("sub_cls", "base_cls"),
    [
        pytest.param(Ok(), Result),
        pytest.param(Err(), Result),
    ],
)
def test_subclass(sub_cls, base_cls):
    assert isinstance(sub_cls, base_cls)


def test_monadic_left_identity():
    assert Result.unit(0).and_then(safe_add, b=1) == safe_add(0, 1)


@pytest.mark.parametrize(("monad"), [pytest.param(Ok(1)), pytest.param(Err())])
def test_monadic_right_identity(monad):
    assert monad.and_then(Result.unit) == monad


@pytest.mark.parametrize(
    ("monad", "f", "g"),
    [
        pytest.param(Ok(0), safe_add_one, safe_add_one),
        pytest.param(Err(), safe_add_one, safe_add_one),
    ],
)
def test_monadic_associativity(monad, f, g):
    assert monad.and_then(f).and_then(g) == monad.and_then(lambda x: f(x).and_then(g))
