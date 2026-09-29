from enum import StrEnum

from pydantic import BaseModel, Field


class DirectoryImportance(StrEnum):
    """Defines the importance level of a directory within the package."""

    CORE = "Core"
    """Represents core directory importance."""

    SUPPORTING = "Supporting"
    """Represents supporting directory importance."""

    UTILITY = "Utility"
    """Represents utility directory importance."""


class DirectoryConcept(BaseModel):
    """Defines the architectural and domain concept schema for a directory, including
    its summary, responsibilities, concepts, relationships, design decisions, and
    importance.
    """

    summary: str = Field(
        description=(
            "Describe the overall architectural purpose "
            "of this directory in 100-300 characters."
        )
    )
    """Overall architectural purpose summary of the directory."""

    responsibilities: list[str] = Field(
        description=(
            "List the primary responsibilities owned by this directory. "
            "Describe what this directory does, not how it is implemented."
        )
    )
    """Primary responsibilities owned by the directory."""

    concepts: list[str] = Field(
        description=(
            "List the important domain or architectural concepts "
            "represented by this directory. Prefer nouns or noun phrases."
        )
    )
    """Important domain or architectural concepts represented by the directory."""

    relationships: list[str] = Field(
        description=(
            "Describe important relationships between concepts in complete sentences."
        )
    )
    """Relationships between concepts within the directory."""

    design_decisions: list[str] = Field(
        description=(
            "List significant architectural decisions, design patterns, "
            "layering, dependency direction, immutability, caching, "
            "or other notable implementation strategies."
        )
    )
    """Significant architectural decisions and implementation strategies for the
    directory.
    """
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
    """Essentialness level of the directory to the package's primary purpose."""
