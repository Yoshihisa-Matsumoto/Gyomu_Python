from pydantic import BaseModel, Field


class CapabilityConcept(BaseModel):
    name: str = Field(
        description=(
            "Short capability name. Use 2-5 words. Examples: 'Text Generation', "
            "'Schema Validation'."
        )
    )
    description: str = Field(
        description=(
            "Brief explanation of what this capability provides to "
            "consumers of the package."
        )
    )


class PackageConcept(BaseModel):
    summary: str = Field(
        description=(
            "High-level summary of the package. "
            "Write 2-4 concise sentences describing its primary purpose and "
            "overall role within the project."
        )
    )
    responsibilities: list[str] = Field(
        description=(
            "- What the package is responsible for within the system\n"
            "- Not APIs\n"
            "- Not implementation\n"
            "- Long-term architectural responsibilities\n"
            "- 3-6 items\n\n"
            "Examples:\n"
            "- Define business domain schemas.\n"
            "- Model TypeScript source code structures.\n"
            "- Provide shared validation models.\n"
        )
    )
    capabilities: list[CapabilityConcept] = Field(
        description=(
            "- What consumers can accomplish\n"
            "- Cohesive feature areas\n"
            "- Group multiple related APIs\n"
            "- Capability names should be concise nouns or noun phrases that describe "
            "a feature area, not an implementation mechanism.\n"
            "- Do not list exported symbols\n"
            "- Do not repeat responsibilities\n"
            "- 3-8 items\n\n"
            "Examples:\n"
            "- Business Entity Schemas\n"
            "- AI Conversation Models\n"
            "- Type Analysis Framework\n"
        )
    )
    design_decisions: list[str] = Field(
        description=(
            "Important architectural or design decisions that explain why the package "
            "is structured this way. Focus on stable design principles "
            "rather than temporary implementation choices."
        )
    )
    usage_guidance: list[str] = Field(
        description=(
            "Recommendations and best practices for consumers of this package. "
            "Explain how the package is intended to be used."
        )
    )
