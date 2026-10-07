from pydantic import BaseModel, ConfigDict, Field

from gyomu_schema.schemas.document.section import Section


class Document[TSectionId: str](BaseModel):
    """Represents a structured document containing a title and sections.

    A structured document independent of any output format such as Markdown or HTML.
    """

    title: str = Field(
        description=("Top-level document title."), examples=["gyomu-schema"]
    )
    """Top-level document title."""

    sections: tuple[Section[TSectionId], ...] = Field(
        description=("Sections contained in the document."),
    )
    """Sections contained in the document."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": (
                "A structured document independent of any output format "
                "such as Markdown or HTML."
            ),
        },
    )
