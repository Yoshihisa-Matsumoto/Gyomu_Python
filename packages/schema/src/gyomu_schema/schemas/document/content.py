from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class DocumentContentType(StrEnum):
    """Defines the types of document content elements available, including
    paragraphs, bullet lists, code blocks, and tables.
    """

    PARAGRAPH = "paragraph"
    """Paragraph content type."""

    BULLET_LIST = "bullet-list"
    """Bullet list content type."""

    CODE = "code"
    """Code block content type."""

    TABLE = "table"
    """Table content type."""


class Paragraph(BaseModel):
    """Represents a paragraph of text within document content."""

    kind: Literal[DocumentContentType.PARAGRAPH] = DocumentContentType.PARAGRAPH
    """The content type discriminator."""

    text: str = Field(description="Paragraph text.")
    """Paragraph text."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": ("A paragraph of text."),
        },
    )


class BulletListItem(BaseModel):
    """Represents a single bullet list item with an optional nested list."""

    translation_id: int = Field(
        description=(
            "A temporary identifier used to track this item during "
            "translation retries. This value must never be translated or modified."
        )
    )
    """A temporary identifier used to track this item during translation retries."""

    text: str = Field(description=("The text content of the bullet list item."))
    """The text content of the bullet list item."""

    children: tuple[BulletListItem, ...] | None = Field(
        default=None, description=("Nested bullet list items.")
    )
    """Nested bullet list items."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": ("A single bullet list item."),
        },
    )


class BulletList(BaseModel):
    """Represents an unordered bullet list containing multiple list items."""

    kind: Literal[DocumentContentType.BULLET_LIST] = DocumentContentType.BULLET_LIST
    """The content type discriminator."""

    items: tuple[BulletListItem, ...] = Field(description=("Bullet list items."))
    """Bullet list items."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": ("An unordered list."),
        },
    )


class CodeBlock(BaseModel):
    """Represents a source code block with language specification and optional title."""

    kind: Literal[DocumentContentType.CODE] = DocumentContentType.CODE
    """The content type discriminator."""

    language: str = Field(
        description=("Programming or markup language."), examples=["ts", "bash", "yaml"]
    )
    """Programming or markup language."""

    code: str = Field(description=("Source code."))
    """Source code."""

    title: str | None = Field(
        description=(
            "Optional code block title. Omit this field entirely "
            "when no title is needed. Never use null."
        ),
        default=None,
    )
    """Optional code block title."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": ("A source code block."),
        },
    )


class TableRow(BaseModel):
    """Represents a single table row containing a sequence of text cells."""

    cells: tuple[str, ...] = Field(description=("Cells in a table row."))
    """Cells in a table row."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": ("A table row."),
        },
    )


class Table(BaseModel):
    """Represents a table with a header row and data rows."""

    kind: Literal[DocumentContentType.TABLE] = DocumentContentType.TABLE
    """The content type discriminator."""

    header: TableRow
    """The table header row."""

    rows: tuple[TableRow, ...]
    """The data rows of the table."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": ("A table with a header row and data rows."),
        },
    )


type DocumentContent = Annotated[
    Paragraph | BulletList | CodeBlock | Table, Field(discriminator="kind")
]
"""Type alias representing a discriminated union of document content elements
including paragraphs, bullet lists, code blocks, and tables.
"""
