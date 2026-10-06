from pydantic import BaseModel, ConfigDict, Field


class DevelopmentFaq(BaseModel):
    """Defines a frequently asked question containing the question and its
    recommended answer.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "description": "A frequently asked question.",
        },
    )

    question: str = Field(
        description="A frequently asked question.",
    )
    """A frequently asked question."""

    answer: str = Field(
        description="The recommended answer.",
    )
    """The recommended answer."""


class DevelopmentKnownIssue(BaseModel):
    """Defines a known limitation or unresolved issue containing the issue
    description and an optional workaround.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "description": "A known limitation or unresolved issue.",
        },
    )

    issue: str = Field(
        description="Describe the known issue.",
    )
    """Describe the known issue."""

    workaround: str | None = Field(
        default=None,
        description="Temporary workaround if available.",
    )
    """Temporary workaround if available."""


class DevelopmentTip(BaseModel):
    """Defines a helpful development recommendation or best practice containing a
    title and description.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "description": "A helpful development recommendation.",
        },
    )

    title: str = Field(
        description="Short title of the development tip.",
    )
    """Short title of the development tip."""

    description: str = Field(
        description="Explain the recommendation or best practice.",
    )
    """Explain the recommendation or best practice."""


class Development(BaseModel):
    """Defines developer-oriented operational knowledge including FAQs, known issues,
    and practical tips.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "title": "Development",
            "description": (
                "Developer-oriented operational knowledge including FAQ, "
                "known issues, and practical tips."
            ),
        },
    )

    faq: tuple[DevelopmentFaq, ...] = Field(
        description="Frequently asked questions for developers.",
    )
    """Frequently asked questions for developers."""

    known_issues: tuple[DevelopmentKnownIssue, ...] = Field(
        description="Known limitations or unresolved issues.",
    )
    """Known limitations or unresolved issues."""

    tips: tuple[DevelopmentTip, ...] = Field(
        description="Helpful recommendations that improve development experience.",
    )
    """Helpful recommendations that improve development experience."""
