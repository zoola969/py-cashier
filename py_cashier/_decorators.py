from __future__ import annotations

from asyncio import iscoroutinefunction
from datetime import timedelta
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, TypeVar, cast, overload

from ttlru_map import TTLMap
from typing_extensions import ParamSpec

from py_cashier._builders import DefaultKeyBuilder
from py_cashier.main import logger

if TYPE_CHECKING:
    from py_cashier._builders import KeyBuilder

P = ParamSpec("P")
T = TypeVar("T")
# F = TypeVar("F", bound=Callable[..., Any])  # noqa: ERA001
F = TypeVar("F", bound=Callable[..., Any])


@overload
def cache(
    *,
    key_builder: KeyBuilder[P, T] | None = None,
    max_size: int | None = 1024,
    ttl: timedelta | None = timedelta(minutes=1),
) -> Callable[[F], F]: ...


@overload
def cache(func: F, /) -> F: ...


def cache(
    func: F | None = None,
    /,
    *,
    key_builder: KeyBuilder[P, T] | None = None,
    max_size: int | None = 1024,  # noqa: ARG001
    ttl: timedelta | None = timedelta(minutes=1),  # noqa: ARG001
) -> Callable[[F], F]:
    """Cache decorator."""

    def _decorator(func_: F) -> F:
        if iscoroutinefunction(func_):
            return _async_wrapper(func_)
        return cast(F, _wrapper(func_, key_builder))

    if func is None:
        return _decorator
    return _decorator(func)


def _wrapper(
    func: Callable[P, T],
    key_builder: KeyBuilder[P, T] | None,
    max_size: int | None = 1024,
    ttl: timedelta | None = timedelta(minutes=1),
) -> Callable[P, T]:
    if key_builder is None:
        key_builder = DefaultKeyBuilder(func=func)

    mapa = TTLMap[str, T](ttl=ttl, max_size=max_size)

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        key = key_builder.build_key(*args, **kwargs)
        # Todo multithreading dog piling
        try:
            res = mapa[key]
            logger.debug("Value for key '%s' has been retrieved from cache map", key)
        except KeyError:
            logger.debug("No entry for key '%s' in cache map", key)
        else:
            return res
        res = func(*args, **kwargs)
        mapa[key] = res
        logger.debug("Value for key '%s' has been set to cache map", key)
        return res

    return wrapper


def _async_wrapper(func: F) -> F:
    @wraps(func)
    async def wrapper(*args, **kwargs):  # noqa: ANN002,ANN003,ANN202
        return await func(*args, **kwargs)

    return cast(F, wrapper)
