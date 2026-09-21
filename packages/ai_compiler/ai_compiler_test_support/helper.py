from pathlib import Path
from typing import Literal

from gyomu_ai_compiler.pipelines.docstring_update.context.declaration_context import (
    ContextEntry,
    DeclarationInfo,
    DocstringDeclarationContext,
    DocstringParameter,
    DocstringRaise,
    DocstringReturn,
    DocumentableContext,
    ExistingDocstring,
    NonDocumentableContext,
)
from gyomu_ai_compiler.pipelines.docstring_update.context.file_context import (
    DocstringFileContext,
    DocstringRetryOption,
)
from gyomu_ai_compiler.pipelines.docstring_update.schema.ai_plan import (
    DescriptionPlan,
    DocstringUpdateEntry,
    DocstringUpdatePlan,
    ParamUpdateAction,
    ParamUpdatePlan,
    RaiseUpdateAction,
    RaiseUpdatePlan,
    Reasoning,
    ReturnUpdateAction,
    ReturnUpdatePlan,
    Risk,
    SummaryPlan,
    UpdateAction,
    UpdatePreserveAction,
    UpdateReplaceAction,
)
from gyomu_schema.schemas.confidence import Confidence
from gyomu_schema.schemas.python.dependency import DependencySummary
from gyomu_schema.schemas.python.types import DeclarationIdentity, SourceRelativePath


def create_docstring_file_context(
    symbols: tuple[DocstringDeclarationContext, ...],
    retry: DocstringRetryOption | None = None,
    project_name: str = "test_project",
    source_relative_path: str = "test.py",
) -> DocstringFileContext:
    return DocstringFileContext(
        project_name=project_name,
        source_relative_path=SourceRelativePath(Path(source_relative_path)),
        symbols=symbols,
        retry=retry,
    )


def create_declaration_info(name: str, kind: str = "class") -> DeclarationInfo:
    return DeclarationInfo(name=name, kind=kind)


def create_declaration_info_from_declaration_identity(
    identity: DeclarationIdentity, kind: str = "class"
) -> DeclarationInfo:
    return DeclarationInfo(name=identity.symbol_id, kind=kind)


def create_docstring_parameter(
    name: str, sort_order: int, type: str | None, description: str | None
) -> DocstringParameter:
    return DocstringParameter(
        name=name, sort_order=sort_order, type=type, description=description
    )


def create_docstring_return(type: str | None, description: str) -> DocstringReturn:
    return DocstringReturn(type=type, description=description)


def create_docstring_raise(type: str, description: str) -> DocstringRaise:
    return DocstringRaise(type=type, description=description)


def create_existing_docstring(
    summary: str | None = None,
    description: str | None = None,
    parameters: tuple[DocstringParameter, ...] = tuple(),
    returns: DocstringReturn | None = None,
    raises: tuple[DocstringRaise, ...] = tuple(),
) -> ExistingDocstring:
    return ExistingDocstring(
        summary=summary,
        description=description,
        parameters=parameters,
        returns=returns,
        raises=raises,
    )


_default_documentable = DocumentableContext()


def create_nondocumentable_context(
    reason: Literal["generated", "external", "non-documentable-member"] = "external",
) -> NonDocumentableContext:
    return NonDocumentableContext(reason=reason)


def create_context_entry(
    target: DeclarationIdentity,
    member: DeclarationInfo,
    existing_docstring: ExistingDocstring | None = None,
    children: tuple[ContextEntry, ...] = tuple(),
    documentable: DocumentableContext | NonDocumentableContext = _default_documentable,
) -> ContextEntry:
    return ContextEntry(
        target=target,
        member=member,
        existing_docstring=existing_docstring,
        children=children,
        documentable=documentable,
    )


def create_docstring_declaration_context(
    symbol: DeclarationInfo,
    target: DeclarationIdentity,
    children: tuple[ContextEntry, ...] = tuple(),
    existing_docstring: ExistingDocstring | None = None,
    code: str = "int",
    dependencies: tuple[DependencySummary, ...] | None = None,
) -> DocstringDeclarationContext:
    return DocstringDeclarationContext(
        symbol=symbol,
        code=code,
        existing_docstring=existing_docstring,
        dependencies=dependencies,
        children=children,
        target=target,
    )


def create_update_replace_action(value: str) -> UpdateReplaceAction:
    return UpdateReplaceAction(value=value)


_preserve_action = UpdatePreserveAction()


def create_return_update_plan(
    action: ReturnUpdateAction = _preserve_action,
    confidence: Confidence = 1,
) -> ReturnUpdatePlan:
    return ReturnUpdatePlan(action=action, confidence=confidence)


def create_raise_update_plan(
    error_type: str,
    action: RaiseUpdateAction = _preserve_action,
    confidence: Confidence = 1,
) -> RaiseUpdatePlan:
    return RaiseUpdatePlan(action=action, confidence=confidence, error_type=error_type)


def create_param_update_plan(
    name: str = "param1",
    sort_order: int = 1,
    action: ParamUpdateAction = _preserve_action,
    confidence: Confidence = 1,
) -> ParamUpdatePlan:
    return ParamUpdatePlan(
        name=name, sort_order=sort_order, action=action, confidence=confidence
    )


def create_description_plan(
    action: UpdateAction = _preserve_action, confidence: Confidence = 1
) -> DescriptionPlan:
    return DescriptionPlan(action=action, confidence=confidence)


def create_summary_plan(
    action: UpdateAction = _preserve_action, confidence: Confidence = 1
) -> SummaryPlan:
    return SummaryPlan(action=action, confidence=confidence)


def create_reasoning(
    summary: str = "summary",
    param_mapping: str = "parameter_mapping",
    return_mapping: str = "return_mapping",
) -> Reasoning:
    return Reasoning(
        summary=summary, param_mapping=param_mapping, return_mapping=return_mapping
    )


def create_risk(
    has_human_conflict: bool = False,
    risk_level: Literal["low", "medium", "high"] = "low",
) -> Risk:
    return Risk(has_human_conflict=has_human_conflict, risk_level=risk_level)


_default_reasoning = create_reasoning()
_default_risk = create_risk()
_default_return = create_return_update_plan()
_default_description = create_description_plan()
_default_summary = create_summary_plan()


def create_docstring_update_entry(
    identity: DeclarationIdentity,
    summary: SummaryPlan = _default_summary,
    description: DescriptionPlan = _default_description,
    returns: ReturnUpdatePlan = _default_return,
    params: tuple[ParamUpdatePlan, ...] = tuple(),
    raises: tuple[RaiseUpdatePlan, ...] = tuple(),
    reasoning: Reasoning = _default_reasoning,
    risk: Risk = _default_risk,
) -> DocstringUpdateEntry:
    return DocstringUpdateEntry(
        identity=identity,
        summary=summary,
        description=description,
        params=params,
        raises=raises,
        returns=returns,
        reasoning=reasoning,
        risk=risk,
    )


def create_docstring_update_plan(
    entries: tuple[DocstringUpdateEntry, ...],
) -> DocstringUpdatePlan:
    return DocstringUpdatePlan(entries=entries)
