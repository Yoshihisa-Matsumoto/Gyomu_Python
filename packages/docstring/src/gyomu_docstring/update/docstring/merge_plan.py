from dataclasses import dataclass
from enum import StrEnum
from typing import Literal

from gyomu_ai_compiler.pipelines.docstring_update.schema.ai_plan import (
    ParamActionValue,
    RaiseActionValue,
    ReturnActionValue,
)
from gyomu_schema.schemas.python.types import DeclarationIdentity


@dataclass(frozen=True)
class MergeReplaceAction[T]:
    value: T
    type: Literal["replace"] = "replace"


@dataclass(frozen=True)
class MergeDeleteAction:
    type: Literal["delete"] = "delete"


@dataclass(frozen=True)
class MergePreserveAction:
    type: Literal["preserve"] = "preserve"


type MergeAction[T] = MergeReplaceAction[T] | MergeDeleteAction | MergePreserveAction


class ConflictType(StrEnum):
    HUMAN_EDITED = "human-edited"
    MISSING_IN_NEW = "missing-in-new"
    STRUCTURAL_MISMATCH = "structural-mismatch"


@dataclass(frozen=True)
class RaiseMergePlan:
    exception_type: str
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
