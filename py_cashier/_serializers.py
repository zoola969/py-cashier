from abc import ABC, abstractmethod
from typing import Any

from typing_extensions import TypeAlias


class KeySerializer(ABC):
    """Key serializer interface."""

    @classmethod
    @abstractmethod
    def to_str(cls, value: Any) -> str:  # noqa: ANN401
        """Convert value to string."""


class StrKeySerializer(KeySerializer):
    """Hash key serializer."""

    @classmethod
    def to_str(cls, value: Any) -> str:  # noqa: ANN401
        """Convert value to string."""
        return str(value)


class ReprKeySerializer(KeySerializer):
    """Hash key serializer."""

    @classmethod
    def to_str(cls, value: Any) -> str:  # noqa: ANN401
        """Convert value to string."""
        return repr(value)


class HashKeySerializer(KeySerializer):
    """Hash key serializer."""

    @classmethod
    def to_str(cls, value: Any) -> str:  # noqa: ANN401
        """Convert value to string."""
        return str(hash(value))


CacheKey: TypeAlias = str
