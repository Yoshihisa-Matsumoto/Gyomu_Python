from pydantic import BaseModel, ConfigDict, Field


class PackageTerminology(BaseModel):
    """Defines a glossary entry containing a technical term and its definition."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "A glossary entry.",
        },
    )

    term: str = Field(
        description="The technical term or concept.",
    )
    """The technical term or concept."""

    definition: str = Field(
        description=(
            "A concise explanation of the meaning of the term within this project."
        ),
    )
    """A concise explanation of the meaning of the term within this project."""


class PackageUsage(BaseModel):
    """Defines a recommended usage pattern consisting of a situation and
    corresponding guidance.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "description": (
                "One recommended usage pattern consisting of a situation and "
                "the corresponding guidance."
            ),
        },
    )

    situation: str = Field(
        description=(
            "Describe the context or situation in which this guidance should be "
            "applied."
        ),
    )
    """The context or situation in which this guidance should be applied."""

    guidance: str = Field(
        description=(
            "Explain the recommended action, behavior, or workflow that should "
            "be followed in this situation."
        ),
    )
    """The recommended action, behavior, or workflow that should be followed in this
    situation.
    """


class PackageExample(BaseModel):
    """Defines a complete worked example with title, input, output, and explanation
    demonstrating knowledge application.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "description": (
                "A complete worked example demonstrating how this knowledge "
                "should be applied."
            ),
        },
    )

    title: str = Field(
        description="A short descriptive title that summarizes the example.",
    )
    """A short descriptive title that summarizes the example."""

    input: str = Field(
        description=(
            "The input, request, or initial situation presented to the system. "
            "Use Markdown when formatting improves readability."
        ),
    )
    """The input, request, or initial situation presented to the system."""

    output: str = Field(
        description=(
            "The expected or recommended output produced from the input. "
            "Use Markdown when appropriate."
        ),
    )
    """The expected or recommended output produced from the input."""

    explanation: str = Field(
        description=(
            "Explain why this output is considered correct and what principle "
            "or policy it demonstrates."
        ),
    )
    """Explanation of why the output is considered correct and what principle or
    policy it demonstrates.
    """


class Package(BaseModel):
    """Defines a structured knowledge package containing a mission, policies,
    constraints, terminology, usage patterns, and examples.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "title": "Knowledge",
            "description": (
                "Structured knowledge provided to an LLM. It defines the mission, "
                "expected behaviors, limitations, terminology, rationale, "
                "recommended usage, and practical examples for a specific topic."
            ),
        },
    )

    display_name: str = Field(
        description="Package display name",
    )
    """Package display name."""

    mission: str = Field(
        description=(
            "The primary mission or purpose of this knowledge. Explain what "
            "this knowledge exists to achieve in one concise paragraph."
        ),
    )
    """The primary mission or purpose of this knowledge."""

    policies: tuple[str, ...] = Field(
        description=(
            "General principles or recommended behaviors. These describe what "
            "should usually be done, but are not absolute requirements."
        ),
    )
    """General principles or recommended behaviors."""

    constraints: tuple[str, ...] = Field(
        description=(
            "Hard requirements that must always be satisfied. Violating these "
            "constraints makes the output incorrect."
        ),
    )
    """Hard requirements that must always be satisfied."""

    non_goals: tuple[str, ...] = Field(
        description=(
            "Explicitly state what this knowledge is not intended to solve or "
            "cover. This helps avoid scope creep and incorrect assumptions."
        ),
    )
    """Explicitly states what this knowledge is not intended to solve or cover."""

    terminology: tuple[PackageTerminology, ...] = Field(
        description=(
            "Definitions of project-specific terminology. Include only terms "
            "that may be ambiguous or unfamiliar."
        ),
    )
    """Definitions of project-specific terminology."""

    rationale: tuple[str, ...] = Field(
        description=(
            "Important reasoning behind decisions, trade-offs, or architectural "
            'choices. Focus on "why" rather than "what".'
        ),
    )
    """Important reasoning behind decisions, trade-offs, or architectural choices."""

    usage: tuple[PackageUsage, ...] = Field(
        description=(
            "Recommended ways to apply this knowledge in practice. Each entry "
            "describes when the guidance applies and what should be done."
        ),
    )
    """Recommended ways to apply this knowledge in practice."""

    examples: tuple[PackageExample, ...] = Field(
        description=(
            "Concrete examples showing correct application of this knowledge. "
            "Examples should be realistic, representative, and suitable for "
            "few-shot prompting."
        ),
    )
    """Concrete examples showing correct application of this knowledge."""
