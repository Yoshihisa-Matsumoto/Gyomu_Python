
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
