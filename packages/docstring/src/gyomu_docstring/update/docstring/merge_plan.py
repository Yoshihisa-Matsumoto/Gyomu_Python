from dataclasses import dataclass
from enum import StrEnum
from typing import Literal

from gyomu_schema.schemas.python.types import DeclarationIdentity
from pydantic import BaseModel, Field


@dataclass(frozen=True)
class ReplaceAction[T]:
    value: T
    type: Literal["replace"] = "replace"


@dataclass(frozen=True)
class DeleteAction:
    type: Literal["delete"] = "delete"


@dataclass(frozen=True)
class PreserveAction:
    type: Literal["preserve"] = "preserve"


type MergeAction[T] = ReplaceAction[T] | DeleteAction | PreserveAction


class ConflictType(StrEnum):
    HUMAN_EDITED = "human-edited"
    MISSING_IN_NEW = "missing-in-new"
    STRUCTURAL_MISMATCH = "structural-mismatch"


# 一時的な定義（後でLLM側に）
class ParamActionValue(BaseModel):
    parameter_type: str | None = Field(description="Type hint of parameter")
    description: str | None = Field(
        description=(
            "Complete replacement parameter metadata. "
            "When using replace, provide the final parameter "
            "documentation to be written."
        )
    )


# 一時的な定義（後でLLM側に）
class ReturnActionValue(BaseModel):
    return_type: str | None = Field(description="Type hint of return")
    description: str | None = Field(
        description=(
            "Complete replacement parameter metadata. "
            "When using replace, provide the final return "
            "documentation to be written."
        )
    )


# 一時的な定義（後でLLM側に）
class RaiseActionValue(BaseModel):
    exception_type: str = Field(description="Type hint of exception")
    description: str | None = Field(
        description=(
            "Complete replacement parameter metadata. "
            "When using replace, provide the final raise "
            "documentation to be written."
        )
    )


@dataclass(frozen=True)
class RaiseMergePlan:
    exception_type: str
    sort_order: int
    action: MergeAction[RaiseActionValue]


@dataclass(frozen=True)
class ParamMergePlan:
    name: str
    sort_order: int
    action: MergeAction[ParamActionValue]


@dataclass(frozen=True)
class MergeConflict:
    symbol: str
    type: ConflictType
    message: str


@dataclass(frozen=True)
class MergePlan:
    identity: DeclarationIdentity

    summary: MergeAction[str]

    description: MergeAction[str]

    params: tuple[ParamMergePlan, ...]

    returns: MergeAction[ReturnActionValue]

    raises: tuple[RaiseMergePlan, ...]

    conflicts: tuple[MergeConflict, ...]

    confidence: float

    average_confidence: float
