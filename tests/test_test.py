import pytest

from py_cashier._builders import DefaultKeyBuilder


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
def test_key_builder(args: list[int], kwargs: dict[str, int]):  # FIXME: rewrite
    def func(a: int, b: int, c: int = 3) -> None:
        pass

    assert (
        DefaultKeyBuilder(
            prefix="",
            func=func,
        ).build_key(*args, **kwargs)
        == "//Users/alex/dev/private/py-cashier/tests/test_test.py/a=1\tb=2\tc=3"
    )
