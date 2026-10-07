from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RoadmapItem(BaseModel):
    """Represents an individual roadmap item.

    One roadmap item describing a planned improvement or feature.
    """

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
    )
    """A short title summarizing the planned work.

    A short title summarizing the planned work.
    """

    description: str = Field(
        description=(
            "Explain the purpose, expected outcome, or motivation for this work."
        ),
    )
    """Explain the purpose, expected outcome, or motivation for this work.

    Explain the purpose, expected outcome, or motivation for this work.
    """

    priority: Literal["high", "medium", "low"] = Field(
        description=(
            "Relative implementation priority. High-priority items are expected "
            "to be addressed before lower-priority items."
        ),
    )
    """Relative implementation priority.

    Relative implementation priority. High-priority items are expected to be addressed
    before lower-priority items.
    """


class Roadmap(BaseModel):
    """Defines a package roadmap containing planned, in-progress, completed, and backlog
    items.

    Tracks the implementation status of planned work for this package. It is intended to
    communicate current priorities and future direction rather than detailed task
    management.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "title": "Roadmap",
            "description": (
                "Tracks the implementation status of planned work for this package. "
                "It is intended to communicate current priorities and future direction "
                "rather than detailed task management."
            ),
        },
    )

    planned: tuple[RoadmapItem, ...] = Field(
        description=("Work that has been approved or planned but has not yet started."),
    )
    """Work that has been approved or planned but has not yet started.

    Work that has been approved or planned but has not yet started.
    """

    in_progress: tuple[RoadmapItem, ...] = Field(
        description="Work that is currently being implemented.",
    )
    """Work that is currently being implemented.

    Work that is currently being implemented.
    """

    completed: tuple[RoadmapItem, ...] = Field(
        description=(
            "Completed work that is worth documenting because it influences "
            "future development."
        ),
    )
    """Completed work that influences future development.

    Completed work that is worth documenting because it influences future development.
    """

    backlog: tuple[RoadmapItem, ...] = Field(
        description=(
            "Ideas or requests that may be implemented in the future but are "
            "not currently planned."
        ),
    )
    """Ideas or requests that are not currently planned.

    Ideas or requests that may be implemented in the future but are not currently
    planned.
    """
