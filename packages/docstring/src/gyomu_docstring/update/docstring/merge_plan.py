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
    """Represents an action to replace a docstring element with a new value.

    Defines a replacement action specifying a new value to apply.
    """

    value: T
    """Replacement value.

    The replacement value to be applied.
    """
    type: Literal["replace"] = "replace"
    """Action type.

    Action type specifier, fixed to 'replace'.
    """


class MergeDeleteAction(BaseModel):
    """Represents an action to delete a docstring section or element.

    Defines a deletion action to remove a docstring section or element.
    """

    type: Literal["delete"] = "delete"
    """Action type.

    Action type specifier, fixed to 'delete'.
    """


class MergePreserveAction(BaseModel):
    """Gyomu Context:
    Preserve the semantic content of the existing docstring section.

    The existing docstring text may be normalized or enriched with
    information derived from source code analysis.
    """

    type: Literal["preserve"] = "preserve"
    """Action type.

    Action type specifier, fixed to 'preserve'.
    """


type MergeAction[T] = MergeReplaceAction[T] | MergeDeleteAction | MergePreserveAction
"""Type alias representing any supported merge action type.

Defines a union of possible merge actions including replacement, deletion, and
preservation.
"""


class ConflictType(StrEnum):
    """Enumeration of conflict types that can occur during docstring merging.

    Defines the category or reason for a merge conflict encountered during docstring
    merging.
    """

    HUMAN_EDITED = "human-edited"
    """Human-edited conflict.

    Indicates a conflict caused by human editing.
    """
    MISSING_IN_NEW = "missing-in-new"
    """Missing in new version conflict.

    Indicates a conflict where content is missing in the new version.
    """
    STRUCTURAL_MISMATCH = "structural-mismatch"
    """Structural mismatch conflict.

    Indicates a conflict caused by a structural mismatch.
    """


class RaiseMergePlan(BaseModel):
    """Represents a merge plan for an exception raise documentation entry.

    Defines the merge plan for an exception raise documentation section.
    """

    exception_type: str
    """Exception type name.

    The type of exception being raised.
    """
    action: MergeAction[RaiseActionValue]
    """Merge action for the exception.

    The merge action to apply to the exception documentation.
    """


class ParamMergePlan(BaseModel):
    """Represents a merge plan for a function parameter documentation entry.

    Defines the merge plan for a function parameter documentation entry.
    """

    name: str
    """Parameter name.

    The name of the parameter.
    """
    sort_order: int
    """Parameter sort order.

    The sort order or position of the parameter.
    """
    action: MergeAction[ParamActionValue]
    """Merge action for the parameter.

    The merge action to apply to the parameter documentation.
    """


class MergeConflict(BaseModel):
    """Represents a conflict encountered during docstring merging.

    Defines details about a conflict encountered during docstring merging.
    """

    symbol: str
    """Affected symbol name.

    The symbol where the conflict occurred.
    """
    type: ConflictType
    """Conflict category.

    The category of the conflict.
    """
    message: str
    """Conflict detail message.

    A descriptive message explaining the conflict.
    """


class MergePlan(BaseModel):
    """Represents a comprehensive merge plan for updating a target symbol docstring.

    Defines a complete merge plan for a docstring target symbol, including actions for
    summary, description, parameters, return value, and exceptions.
    """

    identity: DeclarationIdentity
    """Target declaration identity.

    The identity of the target declaration.
    """

    summary: MergeAction[str]
    """Summary merge action.

    The merge action for the summary.
    """

    description: MergeAction[str] | None
    """Description merge action.

    The merge action for the description, if any.
    """

    params: tuple[ParamMergePlan, ...]
    """Parameter merge plans.

    A tuple of parameter merge plans.
    """

    returns: MergeAction[ReturnActionValue] | None
    """Return merge action.

    The merge action for the return value, if any.
    """

    raises: tuple[RaiseMergePlan, ...]
    """Raise merge plans.

    A tuple of exception raise merge plans.
    """


class MergePlans(BaseModel):
    """Represents a collection of docstring merge plans.

    Container holding a collection of docstring merge plans.
    """

    plans: tuple[MergePlan, ...]
    """Merge plans list.

    Tuple of individual merge plans.
    """
