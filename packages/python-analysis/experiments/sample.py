import asyncio
import pathlib

from pydantic import BaseModel
from pydantic import Field as fld
from pydantic.aliases import AliasChoices as choice
from pydantic.config import JsonDict

from .griffe_analysis import Field as fld2

VERSION = 0.1


async def add(a: int, b: int):
    await asyncio.sleep(1)
    return a + b


def add2(a: int, b: int) -> int:
    return a + b


class User(BaseModel):
    """User information."""

    id: int = fld(description="Primary identifier")

    @classmethod
    def create(cls, name: str) -> "User":
        """Create a user."""
        path: pathlib.Path = pathlib.Path("c:\\data")
        dict: JsonDict = {}
        ch: choice = {}
        fld3: fld2 = {}
        return cls(id=1)
