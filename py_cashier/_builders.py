from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar

from typing_extensions import Annotated, Doc, ParamSpec

from py_cashier._serializers import ReprKeySerializer
from py_cashier._utils import NOT_SET, _collect_args_info, build_cache_key_template

if TYPE_CHECKING:
    from py_cashier._serializers import CacheKey, KeySerializer

P = ParamSpec("P")
T = TypeVar("T")
F = Callable[P, T]


class KeyBuilder(Generic[P, T], ABC):
    """
    A generic abstract base class for building cache keys.

    This class serves as a blueprint for creating cache keys based on
    custom logic defined in subclasses. It provides an interface that
    enforces implementation of the 'build_key' method, which must be
    overridden to define specific key-building behavior. This helps in
    ensuring consistent and reusable caching mechanisms.
    """

    @abstractmethod
    def build_key(
        self,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> CacheKey:
        """
        Abstract method for building a cache key.

            This method must be implemented by subclasses to define the mechanism
            for constructing a unique key for caching purposes, using the provided
            arguments and keyword arguments. The implementation of this method must
            return a value of type `CacheKey`, which serves as the identifier for
            cached data.
        """


class DefaultKeyBuilder(KeyBuilder[P, T]):
    """Default key builder."""

    def __init__(
        self,
        *,
        prefix: str = "",
        func: Callable[P, T],
        cache_by_args: tuple[str, ...] | None = None,  # noqa: ARG002
        key_serializer: type[KeySerializer] = ReprKeySerializer,
        _max_key_size: int = 250,
    ) -> None:
        self._key_serializer = key_serializer
        self._prefix = f"{prefix}/{inspect.getfile(func)}"
        self._by_name, self._by_position, self._args_name, self._kwargs_name = _collect_args_info(func)
        self._cache_key_template = build_cache_key_template(self._by_name)

    def _get_call_args(self, *args: P.args, **kwargs: P.kwargs) -> dict[str, Any]:
        """Return mapping of argument names to their given values."""
        max_arg_number = len(self._by_position)
        for kw in kwargs:
            if (data := self._by_name.get(kw)) and (pos := data.position) is not None:
                max_arg_number = min(max_arg_number, pos)
        res = {}
        i = 0
        while i < max_arg_number and i < len(args):
            res[self._by_position[i]] = args[i]
            i += 1
        _args = args[i:]
        _kwargs = {}
        for kw, value in kwargs.items():
            if kw in self._by_name:
                res[kw] = value
            else:
                _kwargs[kw] = value
        for name, d in self._by_name.items():
            if name in res:
                continue
            if d.default is NOT_SET:
                msg = f"Default value for argument '{name}' is not set"
                raise RuntimeError(msg)
            res[name] = d.default
        return res

    def build_key(
        self,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> CacheKey:
        """Build a cache key."""
        call_args = self._get_call_args(*args, **kwargs)
        return f"{self._prefix}/{self._cache_key_template.format(**call_args)}"
