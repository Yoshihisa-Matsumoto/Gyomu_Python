from pydantic import BaseModel, ConfigDict, Field


class CodingRule(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "description": "A coding guideline rule.",
        },
    )

    category: str = Field(
        description="Category of the coding guideline.",
    )

    rule: str = Field(
        description="The coding rule to follow.",
    )

    rationale: str | None = Field(
        default=None,
        description="Reason why the rule exists.",
    )


class CodingGuideline(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "description": ("Coding guidelines and rules for AI-assisted development."),
        },
    )

    display_name: str

    principles: tuple[str, ...] = Field(
        description="Fundamental coding principles.",
    )

    rules: tuple[CodingRule, ...] = Field(
        description="Actionable coding rules.",
    )

    forbidden: tuple[str, ...] = Field(
        description="Forbidden coding practices.",
    )
