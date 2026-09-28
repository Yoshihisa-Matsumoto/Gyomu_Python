from enum import StrEnum

from pydantic import BaseModel, Field


class DirectoryImportance(StrEnum):
    CORE = "Core"
    SUPPORTING = "Supporting"
    UTILITY = "Utility"


class DirectoryConcept(BaseModel):
    summary: str = Field(
        description=(
            "Describe the overall architectural purpose "
            "of this directory in 100-300 characters."
        )
    )
    responsibilities: list[str] = Field(
        description=(
            "List the primary responsibilities owned by this directory. "
            "Describe what this directory does, not how it is implemented."
        )
    )
    concepts: list[str] = Field(
        description=(
            "List the important domain or architectural concepts "
            "represented by this directory. Prefer nouns or noun phrases."
        )
    )
    relationships: list[str] = Field(
        description=(
            "Describe important relationships between concepts in complete sentences."
        )
    )
    design_decisions: list[str] = Field(
        description=(
            "List significant architectural decisions, design patterns, "
            "layering, dependency direction, immutability, caching, "
            "or other notable implementation strategies."
        )
    )
    importance: DirectoryImportance = Field(
        description=(
            "Indicates how essential this directory is to "
            "the package's primary purpose.\n\n"
            "Choose:\n"
            "- Core: This directory represents one of the primary reasons the "
            "package exists. Without it, the package would lose its core identity.\n"
            "- Supporting: This directory mainly supports or extends the core "
            "functionality but is not itself the primary purpose of the package.\n"
            "- Utility: This directory provides auxiliary or "
            "reusable helper functionality. It is useful but not essential "
            "for understanding the package's main responsibility.\n\n"
            "Classify based on the package's overall purpose, "
            "not on implementation size, number of files, or complexity."
        )
    )
