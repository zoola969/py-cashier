from __future__ import annotations

import inspect
import logging
from abc import ABC, abstractmethod
from asyncio import iscoroutinefunction
from datetime import timedelta
from functools import wraps
from itertools import chain
from typing import TYPE_CHECKING, Any, Callable, TypeVar, cast, overload

from ttlru_map import TTLMap

from py_cashier.key import ReprKeySerializer

if TYPE_CHECKING:
    from py_cashier.key import CacheKey, KeySerializer

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("py-cashier")


class KeyBuilder(ABC):
    """Key builder interface."""

    @abstractmethod
    def build_key(
        self,
        *args: Any,  # noqa: ANN401
        **kwargs: Any,  # noqa: ANN401
    ) -> CacheKey:
        """Build cache key."""


class DefaultKeyBuilder(KeyBuilder):
    """Default key builder."""

    def __init__(
        self,
        *,
        prefix: str = "",
        func: Callable[..., Any],
        cache_by_args: tuple[str, ...] | None = None,
        key_serializer: type[KeySerializer] = ReprKeySerializer,
        _max_key_size: int = 250,
    ) -> None:
        self._key_serializer = key_serializer
        self._prefix = f"{prefix}/{inspect.getfile(func)}"
        self._included_args, self._included_kwargs = self.get_args(cache_by_args, func)

    def get_args(
        self,
        include_args: tuple[str, ...] | None,
        func: Callable[..., Any],
    ) -> tuple[tuple[tuple[str, bool], ...], frozenset[str]]:
        """Get args and kwargs to include in cache key."""
        if include_args is not None and len(include_args) == 0:
            msg = "include_args cannot be an empty set"
            raise ValueError(msg)
        argspec = inspect.getfullargspec(func)
        arg_names = set(argspec.args + argspec.kwonlyargs)
        include_args_set = frozenset(include_args or arg_names)
        if not include_args_set.issubset(arg_names):
            raise ValueError("include_args contains unknown arguments: %s" % (include_args_set - arg_names))

        return tuple((arg, arg in include_args_set) for arg in argspec.args), include_args_set

    def build_key(
        self,
        *args: Any,  # noqa: ANN401
        **kwargs: Any,  # noqa: ANN401
    ) -> CacheKey:
        """Build cache key."""
        # TODO: limit by max size
        key = "/".join(
            chain(
                (self._key_serializer.to_str(arg) for i, arg in enumerate(args) if self._included_args[i][1]),
                (
                    self._key_serializer.to_str(kwarg)
                    for kwarg, value in kwargs.items()
                    if kwarg in self._included_kwargs
                ),
            ),
        )
        return f"{self._prefix}/{key}"


F = TypeVar("F", bound=Callable[..., Any])


@overload
def cache(*, key_builder: KeyBuilder | None = None) -> Callable[[F], F]: ...


@overload
def cache(func: F, /) -> F: ...


def cache(func: F | None = None, /, *, key_builder: KeyBuilder | None = None) -> Callable[[F], F]:
    """Cache decorator."""

    def _decorator(func_: F) -> F:
        if iscoroutinefunction(func_):
            return _async_wrapper(func_)
        return _wrapper(func_, key_builder)

    if func is None:
        return _decorator
    return _decorator(func)


def _wrapper(func: F, key_builder: KeyBuilder | None) -> F:
    if key_builder is None:
        key_builder = DefaultKeyBuilder(func=func)

    mapa = TTLMap(ttl=timedelta(minutes=1))

    @wraps(func)
    def wrapper(*args, **kwargs):  # noqa: ANN002,ANN003,ANN202
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

    return cast(F, wrapper)


def _async_wrapper(func: F) -> F:
    @wraps(func)
    async def wrapper(*args, **kwargs):  # noqa: ANN002,ANN003,ANN202
        return await func(*args, **kwargs)

    return cast(F, wrapper)


if __name__ == "__main__":
    pass
