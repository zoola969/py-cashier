import pytest

from py_cashier.main import DefaultKeyBuilder


@pytest.mark.parametrize(
    ("args", "kwargs"),
    [
        ([1, 2], {}),
        ([1, 2, 3], {}),
        ([1, 2], {"c": 3}),
        ([1], {"b": 2}),
        ([1], {"b": 2, "c": 3}),
        ([], {"a": 1, "b": 2}),
        ([], {"a": 1, "b": 2, "c": 3}),
    ],
)
def test_key_builder(args: list[int], kwargs: dict[str, int]):
    def func(a: int, b: int, c: int = 1) -> None:  # noqa: ARG001
        pass

    assert (
        DefaultKeyBuilder(
            prefix="",
            func=func,
        ).build_key(*args, **kwargs)
        == "//home/alexandr_mysky/develop/py-cashier/py_cashier/main.py/a=1/b=2/c=3"
    )
