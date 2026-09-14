from typing import Annotated

from pydantic import Field

Confidence = Annotated[
    float,
    Field(
        ge=0.0,
        le=1.0,
        description="AI decision confidence used for merge strategy routing",
    ),
]
