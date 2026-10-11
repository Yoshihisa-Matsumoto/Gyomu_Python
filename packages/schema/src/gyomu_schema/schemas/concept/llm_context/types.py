from typing import Literal

from gyomu_schema.schemas.document.section import LanguageCodes

LlmContextSectionId = Literal[
    "overview",
    "architecture",
    "repository-structure",
    "package-responsibilities",
    "design-principles",
    "coding-guidelines",
    "public-api",
    "common-workflows",
    "important-constraints",
    "editing-rules",
    "navigation",
]
"""Literal type representing the section IDs available in an LLM context."""


LLM_CONTEXT_SECTION_TITLES: dict[LanguageCodes, dict[LlmContextSectionId, str]] = {
    "en": {
        "overview": "Repository Overview",
        "architecture": "Architecture",
        "repository-structure": "Repository Structure",
        "package-responsibilities": "Package Responsibilities",
        "design-principles": "Design Principles",
        "coding-guidelines": "Coding Guidelines",
        "public-api": "Public API",
        "common-workflows": "Common Workflows",
        "important-constraints": "Important Constraints",
        "editing-rules": "Editing Rules",
        "navigation": "Navigation",
    },
}
"""Dictionary mapping language codes and LLM context section IDs to their localized
section titles.
"""
