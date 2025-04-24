import inspect
from typing import Callable, Any

import pytest

from py_cashier._utils import NOT_SET, get_kwarg_default_value, NoKwargsError


@pytest.mark.parametrize(
    ("func", "kwarg_name", "expected"),
    [
        (lambda *, a: None, "a", NOT_SET),
        (lambda *, a=1: None, "a", 1),
        (lambda *, a, b: None, "b", NOT_SET),
        (lambda *, a, b=2: None, "b", 2),
        (lambda **kwargs: None, "b", NOT_SET),
    ],
    ids=[
        "no default for kwarg",
        "default for kwarg",
        "no default for second kwarg",
        "default for second kwarg",
        "no default for kwargs",
    ],
)
def test__get_kwarg_default_value(func: Callable[..., Any], kwarg_name: str, expected: Any):
    i = inspect.getfullargspec(func)
    assert get_kwarg_default_value(i, kwarg_name) == expected


@pytest.mark.parametrize(
    ("func", "kwarg_name"),
    [
        (lambda a: None, "a"),
        (lambda a=1: None, "a"),
        (lambda a, *, b: None, "a"),
        (lambda *, b=2: None, "c"),
    ],
)
def test__get_kwarg_default_value__error(func: Callable[..., Any], kwarg_name: str):
    i = inspect.getfullargspec(func)
    with pytest.raises(NoKwargsError):
        get_kwarg_default_value(i, kwarg_name)
