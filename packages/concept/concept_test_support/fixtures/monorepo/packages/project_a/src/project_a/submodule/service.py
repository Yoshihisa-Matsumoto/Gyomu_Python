"""Service layer for project A."""

from enum import Enum
from typing import TypeAlias


PUBLIC_CONSTANT = "public"
_PRIVATE_CONSTANT = "private"
__SECRET_CONSTANT = "secret"


def public_function(value: str) -> str:
    """Return a formatted public value."""
    return value.strip()


def _private_function(value: str) -> str:
    """Return a formatted private value."""
    return value.strip()


def __secret_function(value: str) -> str:
    """Return a formatted secret value."""
    return value.strip()


async def public_async_function(value: str) -> str:
    """Return a formatted value asynchronously."""
    return value.strip()


async def _private_async_function(value: str) -> str:
    """Return a formatted private value asynchronously."""
    return value.strip()


class PublicService:
    """A public service."""

    class NestedPublic:
        """A nested public class."""

    class _NestedPrivate:
        """A nested private class."""


class _PrivateService:
    """A private service."""


class __SecretService:
    """A secret service."""


class PublicEnum(Enum):
    """A public enumeration."""

    VALUE = "value"


class _PrivateEnum(Enum):
    """A private enumeration."""

    VALUE = "value"


PublicAlias: TypeAlias = str
_PrivateAlias: TypeAlias = str
__SecretAlias: TypeAlias = str
