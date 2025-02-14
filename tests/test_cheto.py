import inspect
from typing import Any, Callable

import pytest

from py_cashier._utils import ArgInfo, build_cache_key_template, get_arg_default_value


def test_():
    def func(a: int, b: str, /, a1: int = 2, b1: str = "1", *args: Any, c: int, d: str = "4", **kwargs: Any) -> None:
        pass

    i = inspect.getfullargspec(func)

    by_name = {}
    by_position = {}
    _varargs = i.varargs
    _varkw = i.varkw
    for j, arg in enumerate(i.args):
        by_name[arg] = ArgInfo(
            position=j,
            name=arg,
            default=get_arg_default_value(i, j),
        )
        by_position[j] = by_name[arg]

    for j, arg in enumerate(i.kwonlyargs, start=len(i.args)):
        by_name[arg] = ArgInfo(
            position=j,
            name=arg,
            default=i.kwonlydefaults[arg] if arg in i.kwonlydefaults else None,  # noqa: SIM401
        )
        by_position[j] = by_name[arg]

    cache_key_template = build_cache_key_template(by_name)  # noqa: F841
    # TODO: check that calls return the same cache key

    func(1, c=3)
    func(1, b=1, c=3)
    func(1, 1, c=3)
    func(1, c=3, d=4)
    func(1, 1, c=3, d=4)
    func(1, b=1, c=3, d=4)
    func(1, 1, c=3, d=4)


def test_build_cache_key_template():
    by_name = {
        "a": ArgInfo(position=0, name="a", default=None),
        "b": ArgInfo(position=1, name="b", default=1),
    }
    assert build_cache_key_template(by_name) == "a={a}\nb={b}"


@pytest.mark.parametrize(
    ("func", "arg_num", "expected"),
    [
        (lambda a: None, 0, None),  # noqa: ARG005
        (lambda a=1: None, 0, 1),  # noqa: ARG005
        (lambda a, b=2: None, 0, None),  # noqa: ARG005
        (lambda a=1, b=2: None, 0, 1),  # noqa: ARG005
        (lambda a=1, b=2: None, 1, 2),  # noqa: ARG005
        (lambda a=1, *, b: None, 1, None),  # noqa: ARG005
        (lambda a=1, *, b=2: None, 1, None),  # noqa: ARG005
    ],
)
def test_get_default_value(func: Callable[..., Any], arg_num: int, expected: Any):
    i = inspect.getfullargspec(func)
    assert get_arg_default_value(i, arg_num) == expected


if __name__ == "__main__":
    test_()
