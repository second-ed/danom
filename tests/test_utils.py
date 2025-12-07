import pytest

from src.danom import Ok, compose, identity, invert
from tests.conftest import add_one, divisible_by_3, has_len


@pytest.mark.parametrize(
    ("inp_args", "fns", "expected_result"),
    [
        pytest.param(0, (add_one, add_one), 2),
        pytest.param(0, (add_one, divisible_by_3), False),
    ],
)
def test_compose(inp_args, fns, expected_result):
    assert compose(*fns)(inp_args) == expected_result


@pytest.mark.parametrize(
    "x",
    [
        pytest.param(1, id="identity on a primitive datatype (int)"),
        pytest.param("abc", id="identity on a primitive datatype (str)"),
        pytest.param([0, 1, 2], id="identity on a primitive datatype (list)"),
        pytest.param(Ok(1), id="identity on a more complex datatype"),
    ],
)
def test_identity(x):
    assert identity(x) == x


@pytest.mark.parametrize(
    ("input_args", "fn", "expected_result"),
    [
        pytest.param("", has_len, True),
        pytest.param("abc", has_len, False),
    ],
)
def test_invert(input_args, fn, expected_result):
    assert invert(fn)(input_args) == expected_result


@pytest.mark.parametrize(
    ("input_args", "fn", "expected_result"),
    [
        pytest.param("abc", has_len, True),
        pytest.param("", has_len, False),
    ],
)
def test_two_inverts_returns_same_as_original_fn(input_args, fn, expected_result):
    assert invert(invert(fn))(input_args) == expected_result
