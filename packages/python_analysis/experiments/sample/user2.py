
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field



Confidence = Annotated[
    float,
    Field(
        ge=0.0,
        le=1.0,
        description="AI decision confidence used for merge strategy routing",
    ),
]

Version = 1.2

class RoadmapItem(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "title": "RoadmapItem",
            "description": (
                "One roadmap item describing a planned improvement or feature."
            ),
        },
    )

    title: str = Field(
        description="A short title summarizing the planned work.",
        default="ABC"
    )

    description: str = Field(
        description=(
            "Explain the purpose, expected outcome, or motivation for this work."
        ),
    )

    priority: Literal["high", "medium", "low"] = Field(
        description=(
            "Relative implementation priority. High-priority items are expected "
            "to be addressed before lower-priority items."
        ),
    )

ReadmeSectionId = Literal[
    "overview",
    "features",
    "installation",
    "requirements",
    "quick-start",
    "architecture",
    "public-api",
    "development",
    "dependencies",
    "license",
]

README_SECTION_TITLES: dict[str, dict[ReadmeSectionId, str]] = {
    "en": {
        "overview": "Overview",
        "features": "Features",
        "installation": "Installation",
        "public-api": "Public API",
        "quick-start": "Quick Start",
        "architecture": "Architecture",
        "dependencies": "Dependencies",
        "development": "Development",
        "license": "License",
        "requirements": "Requirements",
    },
    "ja": {
        "overview": "概要",
        "features": "機能",
        "installation": "インストール",
        "public-api": "Public API",
        "quick-start": "クイックスタート",
        "architecture": "アーキテクチャ",
        "dependencies": "依存関係",
        "development": "開発",
        "license": "ライセンス",
        "requirements": "要件",
    },
}
