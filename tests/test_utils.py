import pytest

from src.danom import Ok, identity, invert


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


def has_len(inp_str: str) -> bool:
    return len(inp_str) > 0


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
