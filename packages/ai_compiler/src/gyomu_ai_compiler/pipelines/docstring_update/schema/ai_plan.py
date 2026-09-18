from typing import Annotated, Literal

from gyomu_schema.schemas.confidence import Confidence
from gyomu_schema.schemas.python.types import DeclarationIdentity
from pydantic import BaseModel, ConfigDict, Field


class UpdateReplaceAction(BaseModel):
    type: Literal["replace"] = "replace"
    value: str

    model_config = ConfigDict(
        json_schema_extra={
            "description": (
                "Replace the existing content with the provided value. "
                "The value must contain the final content to apply."
            ),
        },
    )


class UpdatePreserveAction(BaseModel):
    type: Literal["preserve"] = "preserve"

    model_config = ConfigDict(
        json_schema_extra={
            "description": (
                "Keep the existing content unchanged. Use when the current "
                "documentation is already adequate or uncertainty is high."
            ),
        },
    )


class UpdateDeleteAction(BaseModel):
    type: Literal["delete"] = "delete"

    model_config = ConfigDict(
        json_schema_extra={
            "description": (
                "Delete the existing content. Use only when the documented "
                "element no longer exists or the documentation is clearly invalid."
            ),
        },
    )


UpdateAction = Annotated[
    UpdateReplaceAction | UpdatePreserveAction | UpdateDeleteAction,
    Field(
        discriminator="type",
        description=(
            "Deterministic Docstring update action. All replacement content "
            "must be embedded directly in the action so that application "
            "does not require additional context."
        ),
    ),
]


class SummaryPlan(BaseModel):
    action: UpdateAction
    confidence: Confidence

    model_config = ConfigDict(
        json_schema_extra={
            "description": (
                "Update plan for the summary section. "
                "Prefer preserve. "
                "Use replace only when the summary is missing or clearly incorrect."
            ),
        },
    )


class DescriptionPlan(BaseModel):
    action: UpdateAction
    confidence: Confidence

    model_config = ConfigDict(
        json_schema_extra={
            "description": (
                "Update plan for the description section. "
                "Prefer preserve. "
                "Use replace only when the description is missing or clearly incorrect."
            ),
        },
    )


class ParamActionValue(BaseModel):
    type: str | None = Field(description="Type hint of parameter")
    description: str | None = Field(
        description=(
            "Complete replacement parameter metadata."
            " When using replace,"
            " provide the final parameter documentation to be written."
        )
    )


class ParamUpdateReplaceAction(BaseModel):
    type: Literal["replace"] = "replace"
    value: ParamActionValue

    model_config = ConfigDict(
        json_schema_extra={
            "description": (
                "Replace the existing content with the provided value."
                " The value must contain the final content to apply."
            ),
        },
    )


type ParamUpdateAction = Annotated[
    ParamUpdateReplaceAction | UpdatePreserveAction | UpdateDeleteAction,
    Field(
        discriminator="type",
        description=(
            "Deterministic Docstring update action."
            " All replacement content must be embedded directly in the action"
            " so that application does not require additional context."
        ),
    ),
]


class ParamUpdatePlan(BaseModel):
    name: str = Field(description="Parameter name from function signature")
    sort_order: int = Field(
        description=(
            "Parameter position in the function signature."
            " The first parameter should have the lowest sort_order."
            " Preserve signature order when generating update plans."
        )
    )
    action: ParamUpdateAction
    confidence: Confidence

    model_config = ConfigDict(
        json_schema_extra={
            "description": (
                "Parameter update plan."
                " Delete only when the parameter no longer exists"
                " in the function signature. Preserve when unsure."
            ),
        },
    )


class RaiseActionValue(BaseModel):
    error_type: str = Field(description="Type of error/exception")
    description: str | None = Field(
        description=(
            "Complete replacement exception documentation. "
            "When using replace, provide the final exception documentation "
            "to be written."
        )
    )


class RaiseUpdateReplaceAction(BaseModel):
    type: Literal["replace"] = "replace"
    value: RaiseActionValue

    model_config = ConfigDict(
        json_schema_extra={
            "description": (
                "Replace the existing content with the provided value."
                " The value must contain the final content to apply."
            ),
        },
    )


type RaiseUpdateAction = Annotated[
    RaiseUpdateReplaceAction | UpdatePreserveAction | UpdateDeleteAction,
    Field(
        discriminator="type",
        description=(
            "Deterministic Docstring update action."
            " All replacement content must be embedded directly in the action"
            " so that application does not require additional context."
        ),
    ),
]


class RaiseUpdatePlan(BaseModel):
    action: RaiseUpdateAction
    confidence: Confidence
    error_type: str = Field(description="Type of error/exception")
    model_config = ConfigDict(
        json_schema_extra={
            "description": (
                "Raise update plan."
                " Delete only when the raised error/exception no longer exists."
                " Preserve when unsure."
            ),
        },
    )


class ReturnActionValue(BaseModel):
    return_type: str | None = Field(description="Return type")
    description: str | None = Field(
        description=(
            "Complete replacement return documentation. "
            "When using replace, provide the final return documentation "
            "to be written."
        )
    )


class ReturnUpdateReplaceAction(BaseModel):
    type: Literal["replace"] = "replace"
    value: ReturnActionValue

    model_config = ConfigDict(
        json_schema_extra={
            "description": (
                "Replace the existing content with the provided value. "
                "The value must contain the final content to apply."
            ),
        },
    )


type ReturnUpdateAction = Annotated[
    ReturnUpdateReplaceAction | UpdatePreserveAction | UpdateDeleteAction,
    Field(
        discriminator="type",
        description=(
            "Deterministic Docstring update action. "
            "All replacement content must be embedded directly in the action "
            "so that application does not require additional context."
        ),
    ),
]


class ReturnUpdatePlan(BaseModel):
    action: ReturnUpdateAction
    confidence: Confidence
    model_config = ConfigDict(
        json_schema_extra={
            "description": (
                "Return documentation update plan."
                " Delete only when the function no longer returns a meaningful value."
            ),
        },
    )


class Reasoning(BaseModel):
    summary: str = Field(description="Why this update strategy was chosen")
    param_mapping: str = Field(description="How parameters were interpreted and mapped")
    return_mapping: str = Field(description="How return type was interpreted")

    model_config = ConfigDict(
        json_schema_extra={
            "description": ("AI reasoning trace for debugging and validation"),
        },
    )


class Risk(BaseModel):
    has_human_conflict: bool = Field(
        description="Whether AI detected conflict with human-edited content"
    )
    risk_level: Literal["low", "medium", "high"] = Field(
        description="Risk level of applying this update plan"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "description": ("Safety risk assessment for merge operation"),
        },
    )


class DocstringUpdateEntry(BaseModel):
    identity: DeclarationIdentity
    summary: SummaryPlan
    description: DescriptionPlan
    params: tuple[ParamUpdatePlan, ...]
    raises: tuple[RaiseUpdatePlan, ...]
    returns: ReturnUpdatePlan | None
    reasoning: Reasoning
    risk: Risk

    model_config = ConfigDict(
        json_schema_extra={
            "description": (
                "AI-generated structured plan for safely updating Docstring.\n\n"
                "Prefer preserve over replace.\n"
                "Prefer replace over delete.\n\n"
                "Delete actions should be rare and only used when the documented "
                "target no longer exists or the documentation is clearly invalid.\n\n"
                "All replacement content must be included directly in the plan so "
                "that application can be performed without access to the original "
                "update context."
            ),
        },
    )


class DocstringUpdatePlan(BaseModel):
    entries: tuple[DocstringUpdateEntry, ...]

    model_config = ConfigDict(
        json_schema_extra={
            "description": (
                "Collection of Docstring update plans.\n\n"
                "The first entry typically represents the requested target symbol.\n"
                "Additional entries may represent documentable child members "
                "or nested symbols.\n\n"
                "Each entry is applied independently using its identity."
            ),
        },
    )
