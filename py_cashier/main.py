from __future__ import annotations

import logging
from typing import Annotated, Any

from py_cashier._decorators import cache
from py_cashier._utils import CacheWith

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("py-cashier")


@cache
def func2(
    a: Annotated[int, CacheWith()],
    b: str,
    /,
    a1: int = 3,
    b1: str = "4",
    *args: Any,  # noqa: ANN401
    c: int,
    d: str = "6",
    **kwargs: Any,  # noqa: ANN401
) -> None:
    """Func2."""


if __name__ == "__main__":
    func2(1, "1", 2, "3", {}, [], (), c=6, e=1588)
