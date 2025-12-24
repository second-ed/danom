import pytest

from src.danom import Err, Ok, Result


@pytest.mark.parametrize(
    ("sub_cls", "base_cls"),
    [
        pytest.param(Ok(), Result),
        pytest.param(Err(), Result),
    ],
)
def test_subclass(sub_cls, base_cls):
    assert isinstance(sub_cls, base_cls)
