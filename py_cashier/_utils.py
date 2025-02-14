from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Callable, NamedTuple, TypeVar, final, get_args, get_type_hints

from typing_extensions import ParamSpec

if TYPE_CHECKING:
    from collections.abc import Mapping

    from py_cashier._serializers import KeySerializer

P = ParamSpec("P")
T = TypeVar("T")


@final
class NotSet: ...


NOT_SET = NotSet()


def get_arg_default_value(argspec: inspect.FullArgSpec, arg_position: int) -> Any | NotSet:  # noqa: ANN401
    if argspec.defaults is None:
        return NOT_SET
    if arg_position >= len(argspec.args):
        return NOT_SET
    offset = len(argspec.args) - len(argspec.defaults)
    if arg_position < offset:
        return NOT_SET
    return argspec.defaults[arg_position - offset]


def get_kwarg_default_value(argspec: inspect.FullArgSpec, kwarg_name: str) -> Any | NotSet:  # noqa: ANN401
    if argspec.kwonlydefaults is None:
        return NOT_SET
    return argspec.kwonlydefaults.get(kwarg_name, NOT_SET)


def build_cache_key_template(by_name: Mapping[str, Any], *, delimiter: str = "\t") -> str:
    return delimiter.join(f"{x}={{{x}}}" for x, _ in sorted(by_name.items(), key=lambda x: x[1].position))


def _cached(type_alias: Any) -> bool:  # noqa: ANN401
    if type_alias is None:
        return False
    return any(isinstance(type_arg, CacheWith) for type_arg in get_args(type_alias))


class ArgsInfo(NamedTuple):
    by_name: Mapping[str, ArgInfo]
    by_position: list[str]
    args_name: str | None
    kwargs_name: str | None


def _collect_args_info(f: Callable[P, T]) -> ArgsInfo:
    argspec = inspect.getfullargspec(f)
    typing_info = get_type_hints(f, include_extras=True)
    by_name = {}
    by_position: list[str] = []
    for j, arg in enumerate(argspec.args):
        by_name[arg] = ArgInfo(
            position=j,
            name=arg,
            default=get_arg_default_value(argspec, j),
            cached=_cached(typing_info.get(arg)),
        )
        by_position.append(arg)

    for j, arg in enumerate(argspec.kwonlyargs, start=len(argspec.args)):
        by_name[arg] = ArgInfo(
            position=j,
            name=arg,
            default=get_kwarg_default_value(argspec, arg),
            cached=_cached(typing_info.get(arg)),
        )
    return ArgsInfo(by_name=by_name, by_position=by_position, args_name=argspec.varargs, kwargs_name=argspec.varkw)


class CacheWith:
    def __init__(self, serializer: KeySerializer | None = None) -> None:
        pass


class ArgInfo(NamedTuple):
    position: int
    name: str
    cached: bool
    default: Any | NotSet
