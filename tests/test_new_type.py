from contextlib import nullcontext

import pytest

from src.danom import new_type
from tests.conftest import has_len


@pytest.mark.parametrize(
    (
        "initial_value",
        "base_type",
        "validators",
        "converters",
        "expected_inner",
        "expected_context",
    ),
    [
        pytest.param(
            "Some_Email@Domain.Com ",
            str,
            has_len,
            [str.strip, str.lower],
            "some_email@domain.com",
            nullcontext(),
            id="Create specified str type with converters",
        ),
        pytest.param(
            "",
            str,
            [0],
            None,
            None,
            pytest.raises(TypeError),
            id="Ensure it raises TypeError if given an invalid validator",
        ),
        pytest.param(
            "",
            str,
            has_len,
            None,
            "",
            pytest.raises(ValueError),
            id="Ensure it raises ValueError if given a value that fails the validator",
        ),
    ],
)
def test_new_type(  # noqa: PLR0913
    initial_value, base_type, validators, converters, expected_inner, expected_context
):
    with expected_context:
        TestType = new_type("TestType", base_type, validators, converters)  # noqa: N806
        assert TestType(initial_value).inner == expected_inner


@pytest.mark.parametrize(
    ("initial_value", "base_type", "map_fn", "get_attr", "expected_inner", "expected_context"),
    [
        pytest.param(
            "Some_Email@Domain.Com",
            str,
            str.upper,
            "upper",
            "SOME_EMAIL@DOMAIN.COM",
            nullcontext(),
            id="Create specified str type with converters",
        ),
    ],
)
def test_new_type_map(initial_value, base_type, map_fn, get_attr, expected_inner, expected_context):  # noqa: PLR0913
    with expected_context:
        TestType = new_type("TestType", base_type)  # noqa: N806
        assert TestType(initial_value).map(map_fn) == TestType(expected_inner)
        assert getattr(TestType(initial_value), get_attr)() == expected_inner
