import pytest

from py_cashier._utils import ArgInfo, NOT_SET, build_cache_key_template


@pytest.mark.parametrize(
    "delimiter",
    [
        "\t",
        "\n",
        " ",
        ",",
    ],
)
@pytest.mark.parametrize(
    "args_by_name",
    [
        {"a": ArgInfo(position=0, name="a", cached=False, default=NOT_SET)},
        {
            "b": ArgInfo(position=0, name="b", cached=False, default=NOT_SET),
            "a": ArgInfo(position=1, name="a", cached=False, default=NOT_SET),
        },
        {
            "c": ArgInfo(position=2, name="c", cached=False, default=NOT_SET),
            "b": ArgInfo(position=0, name="b", cached=False, default=NOT_SET),
            "a": ArgInfo(position=1, name="a", cached=False, default=NOT_SET),
        },
    ],
)
def test_build_cache_key_template(delimiter: str, args_by_name: dict[str, ArgInfo]) -> None:
    key_info_pairs = list(args_by_name.items())
    key_info_pairs.sort(key=lambda pair: pair[1].position)
    res = []
    for key, _ in key_info_pairs:
        res.append(key + "={" + key + "}")
    expected_template = delimiter.join(res)
    assert build_cache_key_template(args_by_name, delimiter=delimiter) == expected_template
