import pytest

from src.danom import Ok, identity


@pytest.mark.parametrize(
    "x",
    [
        pytest.param(1, id="identity on a primative datatype (int)"),
        pytest.param("abc", id="identity on a primative datatype (str)"),
        pytest.param([0, 1, 2], id="identity on a primative datatype (list)"),
        pytest.param(Ok(1), id="identity on a more complex datatype"),
    ],
)
def test_identity(x):
    assert identity(x) == x
