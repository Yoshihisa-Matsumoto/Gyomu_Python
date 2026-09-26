from typing import Literal

from pydantic import BaseModel


class DocstringText(BaseModel):
    """Represents a standard text line within a docstring."""

    text: str
    """The text content of the line."""

    type: Literal["text"] = "text"
    """The line type discriminator, fixed to 'text'."""


class DocstringBlank(BaseModel):
    """Represents a blank line within a docstring."""

    type: Literal["blank"] = "blank"
    """The line type discriminator, fixed to 'blank'."""


class DocstringSectionItem(BaseModel):
    """Represents a section header line within a docstring."""

    text: str
    """The section header text."""

    type: Literal["section"] = "section"
    """The line type discriminator, fixed to 'section'."""


type DocstringLine = DocstringText | DocstringSectionItem | DocstringBlank
"""Represents any line type within a docstring, which can be text, a section header,
or blank.
"""
