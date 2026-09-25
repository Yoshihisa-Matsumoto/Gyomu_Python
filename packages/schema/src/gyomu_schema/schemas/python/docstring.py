from enum import StrEnum
from typing import Literal, TypedDict

from pydantic import BaseModel

from gyomu_schema.schemas.python.location import SourceLocation


class DocstringStyle(StrEnum):
    """Defines supported docstring formatting styles.

    Defines supported docstring formatting styles.
    """

    GOOGLE = "google"
    """Google docstring style.

    Google docstring style.
    """


class DocstringSectionKind(StrEnum):
    """Defines standard kinds of docstring sections.

    Defines standard kinds of docstring sections.
    """

    ARGS = "args"
    """Arguments section.

    Arguments section.
    """
    RETURNS = "returns"
    """Returns section.

    Returns section.
    """
    RAISES = "raises"
    """Raises section.

    Raises section.
    """
    EXAMPLES = "examples"
    """Examples section.

    Examples section.
    """
    NOTES = "notes"
    """Notes section.

    Notes section.
    """
    CUSTOM = "custom"
    """Custom section.

    Custom section.
    """
    CUSTOM_LIST = "custom_list"
    """Custom list section.

    Custom list section.
    """
    GYOMU_CONTEXT = "gyomu_context"
    """Gyomu context section.

    Gyomu context section.
    """
    TEXT = "text"
    """Text section.

    Text section.
    """


class DocstringTextSection(BaseModel):
    """Represents a text section in a docstring.

    Represents a text section in a docstring.
    """

    kind: Literal[DocstringSectionKind.TEXT] = DocstringSectionKind.TEXT
    """The section kind.

    The section kind.
    """
    value: str
    """The text value.

    The text value.
    """


class DocstringParametersSectionItem(BaseModel):
    """Represents an item in a docstring parameters section.

    Represents an item in a docstring parameters section.
    """

    name: str
    """The parameter name.

    The parameter name.
    """
    type: str | None
    """The parameter type, if specified.

    The parameter type, if specified.
    """
    description: str
    """The parameter description.

    The parameter description.
    """


class DocstringParametersSection(BaseModel):
    """Represents a docstring parameters section containing multiple parameter items.

    Represents a docstring parameters section containing multiple parameter items.
    """

    kind: Literal[DocstringSectionKind.ARGS] = DocstringSectionKind.ARGS
    """The section kind.

    The section kind.
    """
    items: tuple[DocstringParametersSectionItem, ...]
    """The collection of parameter items.

    The collection of parameter items.
    """


class DocstringReturnsSectionItem(BaseModel):
    """Represents an item in a docstring returns section.

    Represents an item in a docstring returns section.
    """

    type: str | None
    """The return type, if specified.

    The return type, if specified.
    """
    description: str
    """The return description.

    The return description.
    """


class DocstringReturnsSection(BaseModel):
    """Represents a docstring returns section.

    Represents a docstring returns section.
    """

    kind: Literal[DocstringSectionKind.RETURNS] = DocstringSectionKind.RETURNS
    """The section kind.

    The section kind.
    """
    item: DocstringReturnsSectionItem
    """The return item details.

    The return item details.
    """


class DocstringRaisesSectionItem(BaseModel):
    """Represents an item in a docstring raises section.

    Represents an item in a docstring raises section.
    """

    type: str
    """The exception type.

    The exception type.
    """
    description: str
    """The exception description.

    The exception description.
    """


class DocstringRaisesSection(BaseModel):
    """Represents a docstring raises section containing multiple exception items.

    Represents a docstring raises section containing multiple exception items.
    """

    kind: Literal[DocstringSectionKind.RAISES] = DocstringSectionKind.RAISES
    """The section kind.

    The section kind.
    """
    items: tuple[DocstringRaisesSectionItem, ...]
    """The collection of exception items.

    The collection of exception items.
    """


class DocstringExamplesSectionItem(BaseModel):
    """Represents an item in a docstring examples section.

    Represents an item in a docstring examples section.
    """

    value: str
    """The example code value.

    The example code value.
    """


class DocstringExamplesSection(BaseModel):
    """Represents a docstring examples section containing code examples.

    Represents a docstring examples section containing code examples.
    """

    kind: Literal[DocstringSectionKind.EXAMPLES] = DocstringSectionKind.EXAMPLES
    """The section kind.

    The section kind.
    """
    items: tuple[DocstringExamplesSectionItem, ...]
    """The collection of example items.

    The collection of example items.
    """


class DocstringGyomuContextSection(BaseModel):
    """Represents a Gyomu context section in a docstring.

    Represents a Gyomu context section in a docstring.
    """

    kind: Literal[DocstringSectionKind.GYOMU_CONTEXT] = (
        DocstringSectionKind.GYOMU_CONTEXT
    )
    """The section kind.

    The section kind.
    """
    value: str
    """The context value.

    The context value.
    """


class DocstringCustomSection(BaseModel):
    """Represents a custom section in a docstring.

    Represents a custom section in a docstring.
    """

    kind: Literal[DocstringSectionKind.CUSTOM] = DocstringSectionKind.CUSTOM
    """The section kind.

    The section kind.
    """
    title: str
    """The custom section title.

    The custom section title.
    """
    value: str
    """The custom section value.

    The custom section value.
    """


class DocstringCustomNamedSectionItem(BaseModel):
    """Represents an item in a custom named section.

    Represents an item in a custom named section.
    """

    name: str | None
    """The item name, if specified.

    The item name, if specified.
    """
    value: str
    """The item value.

    The item value.
    """


class DocstringCustomListSection(BaseModel):
    """Represents a custom list section in a docstring.

    Represents a custom list section in a docstring.
    """

    kind: Literal[DocstringSectionKind.CUSTOM_LIST] = DocstringSectionKind.CUSTOM_LIST
    """The section kind.

    The section kind.
    """
    title: str
    """The custom section title.

    The custom section title.
    """
    items: tuple[DocstringCustomNamedSectionItem, ...]
    """The collection of custom named items.

    The collection of custom named items.
    """


class DocstringNotesSection(BaseModel):
    """Represents a notes section in a docstring.

    Represents a notes section in a docstring.
    """

    kind: Literal[DocstringSectionKind.NOTES] = DocstringSectionKind.NOTES
    """The section kind.

    The section kind.
    """
    value: str
    """The notes value.

    The notes value.
    """


type DocstringSection = (
    DocstringParametersSection
    | DocstringReturnsSection
    | DocstringRaisesSection
    | DocstringExamplesSection
    | DocstringNotesSection
    | DocstringGyomuContextSection
    | DocstringCustomSection
    | DocstringCustomListSection
)
"""Represents a union of all supported docstring section types.

Represents a union of all supported docstring section types.
"""


class DocstringAnalysis(BaseModel):
    """Represents the complete analysis of a parsed docstring.

    Represents the complete analysis of a parsed docstring.
    """

    raw: str
    """The raw docstring content.

    The raw docstring content.
    """
    summary: str | None
    """The parsed summary, if present.

    The parsed summary, if present.
    """
    description: str | None
    """The parsed description, if present.

    The parsed description, if present.
    """
    style: DocstringStyle
    """The docstring formatting style.

    The docstring formatting style.
    """
    location: SourceLocation
    """The source code location.

    The source code location.
    """
    sections: tuple[DocstringSection, ...]
    """The collection of parsed sections.

    The collection of parsed sections.
    """
    indent: int
    """The indentation level.

    The indentation level.
    """


class DocstringCommon(TypedDict):
    """Represents common docstring metadata including location and indentation.

    Represents common docstring metadata including location and indentation.
    """

    location: SourceLocation
    """The source code location.

    The source code location.
    """
    indent: int
    """The indentation level.

    The indentation level.
    """
