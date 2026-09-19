from enum import StrEnum
from typing import Literal

from gyomu_ai_compiler.pipelines.docstring_update.schema.ai_plan import (
    ParamActionValue,
    RaiseActionValue,
    ReturnActionValue,
)
from gyomu_schema.schemas.python.types import DeclarationIdentity
from pydantic import BaseModel


class MergeReplaceAction[T](BaseModel):
    value: T
    type: Literal["replace"] = "replace"


class MergeDeleteAction(BaseModel):
    type: Literal["delete"] = "delete"


class MergePreserveAction(BaseModel):
    """
    Gyomu Context:
    Preserve the semantic content of the existing docstring section.

    The existing docstring text may be normalized or enriched with
    information derived from source code analysis.
    """

    type: Literal["preserve"] = "preserve"


type MergeAction[T] = MergeReplaceAction[T] | MergeDeleteAction | MergePreserveAction


class ConflictType(StrEnum):
    HUMAN_EDITED = "human-edited"
    MISSING_IN_NEW = "missing-in-new"
    STRUCTURAL_MISMATCH = "structural-mismatch"


class RaiseMergePlan(BaseModel):
    exception_type: str
    action: MergeAction[RaiseActionValue]


class ParamMergePlan(BaseModel):
    name: str
    sort_order: int
    action: MergeAction[ParamActionValue]


class MergeConflict(BaseModel):
    symbol: str
    type: ConflictType
    message: str


class MergePlan(BaseModel):
    identity: DeclarationIdentity

    summary: MergeAction[str]

    description: MergeAction[str] | None

    params: tuple[ParamMergePlan, ...]

    returns: MergeAction[ReturnActionValue] | None

    raises: tuple[RaiseMergePlan, ...]


class MergePlans(BaseModel):
    plans: tuple[MergePlan, ...]
