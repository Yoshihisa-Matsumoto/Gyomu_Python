
from typing import Annotated

from pydantic import Field

VERSION = 5
VERSION_STR = "5"

_internal_value = 10

ANNOTATED: int

Calculated = 2 + 3


Confidence = Annotated[
    float,
    Field(
        ge=0.0,
        le=1.0,
        description="AI decision confidence used for merge strategy routing",
    ),
]

Confidence2 = Annotated[
    float,
    SomeMetadata(),
    Field(
        ge=0.0,
        le=1.0,
        description="AI decision confidence used for merge strategy routing",
    ),
]
