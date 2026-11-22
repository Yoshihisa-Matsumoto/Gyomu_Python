from gyomu_python_analysis.error.resolve import ResolveError
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_python_analysis.resolve.models import (
    PackageType,
    ReferencedType,
    SymbolType,
)
from gyomu_python_analysis.resolve.type_reference import (
    resolve_identity,
)
from gyomu_schema.schemas.config.test.model_defaults import (
    AttributeParameter,
    CallParameter,
    DictParameter,
    LambdaParameter,
    ListParameter,
    Parameter,
    TupleParameter,
)
from gyomu_schema.schemas.python.types import SymbolId
from returns.result import Failure, Result, Success

from gyomu_test.error.test import GyomuTestError


def deduplicate_referenced_types(
    referenced_types: list[ReferencedType],
) -> tuple[ReferencedType, ...]:
    unique_types: dict[SymbolId, ReferencedType] = {}

    for referenced_type in referenced_types:
        symbol_id = (
            referenced_type.symbol.identity.symbol_id
            if isinstance(referenced_type, SymbolType)
            else referenced_type.symbol_id
        )
        unique_types.setdefault(symbol_id, referenced_type)

    return tuple(unique_types.values())


def _compute_referenced_types(
    parameter: Parameter,
    referenced_types: list[ReferencedType],
    workspace_context: WorkspaceContext,
) -> Result[None, ResolveError]:

    if isinstance(parameter, AttributeParameter):
        return _compute_referenced_types(
            parameter=parameter.value,
            referenced_types=referenced_types,
            workspace_context=workspace_context,
        )
    if isinstance(parameter, CallParameter):
        resolve_result = resolve_identity(
            identity=parameter.callable_identity, workspace_context=workspace_context
        )
        if isinstance(resolve_result, Failure):
            return resolve_result
        for resolved_type in resolve_result.unwrap():
            if isinstance(resolved_type, SymbolType | PackageType):
                referenced_types.append(resolved_type)
        for arg in parameter.args:
            result = _compute_referenced_types(
                parameter=arg,
                referenced_types=referenced_types,
                workspace_context=workspace_context,
            )
            if isinstance(result, Failure):
                return result
        for kwarg in parameter.kwargs:
            result = _compute_referenced_types(
                parameter=kwarg.value,
                referenced_types=referenced_types,
                workspace_context=workspace_context,
            )
            if isinstance(result, Failure):
                return result

    if isinstance(parameter, DictParameter):
        for entry in parameter.entries:
            result = _compute_referenced_types(
                parameter=entry.key,
                referenced_types=referenced_types,
                workspace_context=workspace_context,
            )
            if isinstance(result, Failure):
                return result
            result = _compute_referenced_types(
                parameter=entry.value,
                referenced_types=referenced_types,
                workspace_context=workspace_context,
            )
            if isinstance(result, Failure):
                return result
    if isinstance(parameter, TupleParameter | ListParameter):
        for element in parameter.elements:
            result = _compute_referenced_types(
                parameter=element,
                referenced_types=referenced_types,
                workspace_context=workspace_context,
            )
            if isinstance(result, Failure):
                return result
    if isinstance(parameter, LambdaParameter):
        result = _compute_lambda_referenced_types(
            parameter=parameter,
            referenced_types=referenced_types,
            workspace_context=workspace_context,
        )
        if isinstance(result, Failure):
            return result
    return Success(None)


def _compute_lambda_referenced_types(
    parameter: LambdaParameter,
    referenced_types: list[ReferencedType],
    workspace_context: WorkspaceContext,
) -> Result[None, ResolveError]:
    result = _compute_referenced_types(
        parameter=parameter.body,
        referenced_types=referenced_types,
        workspace_context=workspace_context,
    )
    if isinstance(result, Failure):
        return result
    for arg in parameter.args.posonlyargs:
        result = _compute_referenced_types(
            parameter=arg.annotation,
            referenced_types=referenced_types,
            workspace_context=workspace_context,
        )
        if isinstance(result, Failure):
            return result
    for arg in parameter.args.args:
        result = _compute_referenced_types(
            parameter=arg.annotation,
            referenced_types=referenced_types,
            workspace_context=workspace_context,
        )
        if isinstance(result, Failure):
            return result
    if parameter.args.vararg is not None:
        result = _compute_referenced_types(
            parameter=parameter.args.vararg.annotation,
            referenced_types=referenced_types,
            workspace_context=workspace_context,
        )
        if isinstance(result, Failure):
            return result
    for arg in parameter.args.kwonlyargs:
        result = _compute_referenced_types(
            parameter=arg.annotation,
            referenced_types=referenced_types,
            workspace_context=workspace_context,
        )
        if isinstance(result, Failure):
            return result
    for kw_default in parameter.args.kw_defaults:
        result = _compute_referenced_types(
            parameter=kw_default,
            referenced_types=referenced_types,
            workspace_context=workspace_context,
        )
        if isinstance(result, Failure):
            return result
    if parameter.args.kwarg is not None:
        result = _compute_referenced_types(
            parameter=parameter.args.kwarg.annotation,
            referenced_types=referenced_types,
            workspace_context=workspace_context,
        )
        if isinstance(result, Failure):
            return result
    for default in parameter.args.defaults:
        result = _compute_referenced_types(
            parameter=default,
            referenced_types=referenced_types,
            workspace_context=workspace_context,
        )
        if isinstance(result, Failure):
            return result
    return Success(None)


def aggregate_referenced_types(
    parameter: Parameter,
    referenced_types: list[ReferencedType],
    workspace_context: WorkspaceContext,
) -> Result[tuple[ReferencedType, ...], GyomuTestError]:
    computed_references: list[ReferencedType] = []
    compute_result = _compute_referenced_types(
        parameter=parameter,
        referenced_types=computed_references,
        workspace_context=workspace_context,
    )
    if isinstance(compute_result, Failure):
        return compute_result.alt(
            lambda error: GyomuTestError(
                "Failed to resolve referenced types for parameter default",
                details={"parameter": parameter},
            ).chain(error)
        )
    referenced_types.extend(computed_references)
    return Success(deduplicate_referenced_types(referenced_types))
