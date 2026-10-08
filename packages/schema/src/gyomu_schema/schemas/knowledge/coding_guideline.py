from pydantic import BaseModel, ConfigDict, Field


class CodingRule(BaseModel):
    """Defines a coding guideline rule containing a category, rule description, and
    optional rationale.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "description": "A coding guideline rule.",
        },
    )

    category: str = Field(
        description="Category of the coding guideline.",
    )
    """Category of the coding guideline."""

    rule: str = Field(
        description="The coding rule to follow.",
    )
    """The coding rule to follow."""

    rationale: str | None = Field(
        default=None,
        description="Reason why the rule exists.",
    )
    """Reason why the rule exists."""


class CodingGuideline(BaseModel):
    """Defines coding guidelines and rules for AI-assisted development, including
    principles, actionable rules, and forbidden practices.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "description": ("Coding guidelines and rules for AI-assisted development."),
        },
    )

    display_name: str
    """Display name of the coding guideline."""

    principles: tuple[str, ...] = Field(
        description="Fundamental coding principles.",
    )
    """Fundamental coding principles."""

    rules: tuple[CodingRule, ...] = Field(
        description="Actionable coding rules.",
    )
    """Actionable coding rules."""

    forbidden: tuple[str, ...] = Field(
        description="Forbidden coding practices.",
    )
    """Forbidden coding practices."""


def merge_coding_guideline(
    root: CodingGuideline, project: CodingGuideline | None
) -> CodingGuideline:
    if project is None:
        return root

    return CodingGuideline(
        display_name=project.display_name,
        rules=(*root.rules, *project.rules),
        forbidden=(*root.forbidden, *project.forbidden),
        principles=(*root.principles, *project.principles),
    )
