from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class DocumentContentType(StrEnum):
    PARAGRAPH = "paragraph"
    BULLET_LIST = "bullet-list"
    CODE = "code"
    TABLE = "table"


class Paragraph(BaseModel):
    kind: Literal[DocumentContentType.PARAGRAPH] = DocumentContentType.PARAGRAPH
    text: str = Field(description="Paragraph text.")

    model_config = ConfigDict(
        json_schema_extra={
            "description": ("A paragraph of text."),
        },
    )


class BulletListItem(BaseModel):
    translation_id: int = Field(
        description=(
            "A temporary identifier used to track this item during "
            "translation retries. This value must never be translated or modified."
        )
    )
    text: str = Field(description=("The text content of the bullet list item."))
    children: tuple[BulletListItem, ...] | None = Field(
        default=None, description=("Nested bullet list items.")
    )

    model_config = ConfigDict(
        json_schema_extra={
            "description": ("A single bullet list item."),
        },
    )


class BulletList(BaseModel):
    kind: Literal[DocumentContentType.BULLET_LIST] = DocumentContentType.BULLET_LIST
    items: tuple[BulletListItem, ...] = Field(description=("Bullet list items."))

    model_config = ConfigDict(
        json_schema_extra={
            "description": ("An unordered list."),
        },
    )


class CodeBlock(BaseModel):
    kind: Literal[DocumentContentType.CODE] = DocumentContentType.CODE
    language: str = Field(
        description=("Programming or markup language."), examples=["ts", "bash", "yaml"]
    )
    code: str = Field(description=("Source code."))
    title: str | None = Field(
        description=(
            "Optional code block title. Omit this field entirely "
            "when no title is needed. Never use null."
        ),
        default=None,
    )

    model_config = ConfigDict(
        json_schema_extra={
            "description": ("A source code block."),
        },
    )


class TableRow(BaseModel):
    cells: tuple[str, ...] = Field(description=("Cells in a table row."))

    model_config = ConfigDict(
        json_schema_extra={
            "description": ("A table row."),
        },
    )


class Table(BaseModel):
    kind: Literal[DocumentContentType.TABLE] = DocumentContentType.TABLE
    header: TableRow
    rows: tuple[TableRow, ...]

    model_config = ConfigDict(
        json_schema_extra={
            "description": ("A table with a header row and data rows."),
        },
    )


type DocumentContent = Annotated[
    Paragraph | BulletList | CodeBlock | Table, Field(discriminator="kind")
]
