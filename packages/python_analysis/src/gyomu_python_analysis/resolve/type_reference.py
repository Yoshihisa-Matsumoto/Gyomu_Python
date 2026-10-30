from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.type.structure import (
    EllipsisStructureAnalysis,
    LiteralValue,
    NameStructureAnalysis,
    NoneStructureAnalysis,
)
from gyomu_schema.schemas.python.type.type_analysis import (
    ArrayStructureAnalysis,
    AttributeStructureAnalysis,
    CallableStructureAnalysis,
    CallStructureAnalysis,
    DictionaryStructureAnalysis,
    GenericsStructureAnalysis,
    KeywordStructureAnalysis,
    LiteralStructureAnalysis,
    SetStructureAnalysis,
    StructureAnalysis,
    TupleStructureAnalysis,
    TypeAnalysis,
    TypeExpression,
    UnionStructureAnalysis,
)
from gyomu_schema.schemas.python.types import DeclarationIdentity
from returns.result import Failure, Result, Success

from gyomu_python_analysis.error.resolve import ResolveError
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.resolve.file_analysis_cache import FileAnalysisCache
from gyomu_python_analysis.resolve.models import (
    LiteralValueType,
    PrimitiveType,
    ResolvedType,
    SymbolType,
)
from gyomu_python_analysis.resolve.path import normalize_reference_name
from gyomu_python_analysis.resolve.reference import resolve_reference
from gyomu_python_analysis.resolve.symbol import resolve_symbol_analysis


def _resolve_self_from_name(
    structure: NameStructureAnalysis, class_name: str | None
) -> str:
    if structure.name == "Self":
        return class_name if class_name is not None else structure.name
    return structure.name


def _resolve_name(
    structure: NameStructureAnalysis,
    parameter_name: str,
    type_text: str,
    module: ModuleAnalysis,
    project_context: ProjectContext,
    file_analysis_cache: FileAnalysisCache,
    class_name: str | None,
) -> Result[tuple[ResolvedType, ...], ResolveError]:
    resolved_name = _resolve_self_from_name(structure, class_name)
    normalized_name = normalize_reference_name(
        imported=module.imports, reference_name=resolved_name
    )
    resolved_reference = resolve_reference(
        reference_name=normalized_name, module=module
    )
    if resolved_reference is None or resolved_reference.symbol_id is None:
        return Success(
            (
                PrimitiveType(
                    primitive_type=normalized_name, parameter_name=parameter_name
                ),
            )
        )
    else:
        symbol_result = resolve_symbol_analysis(
            declaration_identity=DeclarationIdentity.create_from_symbol_id(
                resolved_reference.symbol_id
            ),
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
        )
        if isinstance(symbol_result, Failure):
            return symbol_result
        file_analysis_context, symbol = symbol_result.unwrap()
        return Success((SymbolType(symbol=symbol, context=file_analysis_context),))


def _resolve_none(
    structure: NoneStructureAnalysis,
    parameter_name: str,
    type_text: str,
    module: ModuleAnalysis,
    project_context: ProjectContext,
    file_analysis_cache: FileAnalysisCache,
    class_name: str | None,
) -> Result[tuple[ResolvedType, ...], ResolveError]:
    return Success(())


def _resolve_union(
    structure: UnionStructureAnalysis,
    parameter_name: str,
    type_text: str,
    module: ModuleAnalysis,
    project_context: ProjectContext,
    file_analysis_cache: FileAnalysisCache,
    class_name: str | None,
) -> Result[tuple[ResolvedType, ...], ResolveError]:
    result: list[ResolvedType] = []
    for expression in structure.types:
        expression_result = _resolve_type_expression(
            parameter_name=parameter_name,
            expression=expression,
            type_text=type_text,
            module=module,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
            class_name=class_name,
        )
        if isinstance(expression_result, Failure):
            return expression_result
        result.extend(expression_result.unwrap())
    return Success(tuple(result))


def _resolve_attribute(
    structure: AttributeStructureAnalysis,
    parameter_name: str,
    type_text: str,
    module: ModuleAnalysis,
    project_context: ProjectContext,
    file_analysis_cache: FileAnalysisCache,
    class_name: str | None,
) -> Result[tuple[ResolvedType, ...], ResolveError]:
    # TODO: Validate whether attribute references need resolution
    # using real-project cases such as Literal[Color.RED].
    return Success(tuple())
    # result: list[ResolvedType] = []
    # for expression in structure.values:
    #     expression_result = _resolve_type_expression(
    #         parameter_name=parameter_name,
    #         expression=expression,
    #         type_text=type_text,
    #         module=module,
    #         project_context=project_context,
    #         file_analysis_cache=file_analysis_cache,
    #         class_name=class_name,
    #     )
    #     if isinstance(expression_result, Failure):
    #         return expression_result
    #     result.extend(expression_result.unwrap())
    # return Success(tuple(result))


def _resolve_tuple(
    structure: TupleStructureAnalysis,
    parameter_name: str,
    type_text: str,
    module: ModuleAnalysis,
    project_context: ProjectContext,
    file_analysis_cache: FileAnalysisCache,
    class_name: str | None,
) -> Result[tuple[ResolvedType, ...], ResolveError]:
    result: list[ResolvedType] = []
    for expression in structure.elements:
        expression_result = _resolve_type_expression(
            parameter_name=parameter_name,
            expression=expression,
            type_text=type_text,
            module=module,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
            class_name=class_name,
        )
        if isinstance(expression_result, Failure):
            return expression_result
        result.extend(expression_result.unwrap())
    return Success(tuple(result))


def _resolve_generics(
    structure: GenericsStructureAnalysis,
    parameter_name: str,
    type_text: str,
    module: ModuleAnalysis,
    project_context: ProjectContext,
    file_analysis_cache: FileAnalysisCache,
    class_name: str | None,
) -> Result[tuple[ResolvedType, ...], ResolveError]:
    result: list[ResolvedType] = []
    expression_result = _resolve_type_expression(
        parameter_name=parameter_name,
        expression=structure.base,
        type_text=type_text,
        module=module,
        project_context=project_context,
        file_analysis_cache=file_analysis_cache,
        class_name=class_name,
    )
    if isinstance(expression_result, Failure):
        return expression_result
    result.extend(expression_result.unwrap())

    for expression in structure.parameters:
        expression_result = _resolve_type_expression(
            parameter_name=parameter_name,
            expression=expression,
            type_text=type_text,
            module=module,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
            class_name=class_name,
        )
        if isinstance(expression_result, Failure):
            return expression_result
        result.extend(expression_result.unwrap())
    return Success(tuple(result))


def _resolve_literal(
    structure: LiteralStructureAnalysis,
    parameter_name: str,
    type_text: str,
    module: ModuleAnalysis,
    project_context: ProjectContext,
    file_analysis_cache: FileAnalysisCache,
    class_name: str | None,
) -> Result[tuple[ResolvedType, ...], ResolveError]:
    return _resolve_type_expression(
        parameter_name=parameter_name,
        expression=structure.value,
        type_text=type_text,
        module=module,
        project_context=project_context,
        file_analysis_cache=file_analysis_cache,
        class_name=class_name,
    )


def _resolve_array(
    structure: ArrayStructureAnalysis,
    parameter_name: str,
    type_text: str,
    module: ModuleAnalysis,
    project_context: ProjectContext,
    file_analysis_cache: FileAnalysisCache,
    class_name: str | None,
) -> Result[tuple[ResolvedType, ...], ResolveError]:
    return _resolve_type_expression(
        parameter_name=parameter_name,
        expression=structure.element,
        type_text=type_text,
        module=module,
        project_context=project_context,
        file_analysis_cache=file_analysis_cache,
        class_name=class_name,
    )


def _resolve_dictionary(
    structure: DictionaryStructureAnalysis,
    parameter_name: str,
    type_text: str,
    module: ModuleAnalysis,
    project_context: ProjectContext,
    file_analysis_cache: FileAnalysisCache,
    class_name: str | None,
) -> Result[tuple[ResolvedType, ...], ResolveError]:
    result: list[ResolvedType] = []
    if structure.keys is not None:
        expression_result = _resolve_type_expression(
            parameter_name=parameter_name,
            expression=structure.keys,
            type_text=type_text,
            module=module,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
            class_name=class_name,
        )
        if isinstance(expression_result, Failure):
            return expression_result
        result.extend(expression_result.unwrap())
    if structure.values is not None:
        expression_result = _resolve_type_expression(
            parameter_name=parameter_name,
            expression=structure.values,
            type_text=type_text,
            module=module,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
            class_name=class_name,
        )
        if isinstance(expression_result, Failure):
            return expression_result
        result.extend(expression_result.unwrap())
    return Success(tuple(result))


def _resolve_callable(
    structure: CallableStructureAnalysis,
    parameter_name: str,
    type_text: str,
    module: ModuleAnalysis,
    project_context: ProjectContext,
    file_analysis_cache: FileAnalysisCache,
    class_name: str | None,
) -> Result[tuple[ResolvedType, ...], ResolveError]:
    result: list[ResolvedType] = []
    expression_result = _resolve_type_expression(
        parameter_name=parameter_name,
        expression=structure.return_type,
        type_text=type_text,
        module=module,
        project_context=project_context,
        file_analysis_cache=file_analysis_cache,
        class_name=class_name,
    )
    if isinstance(expression_result, Failure):
        return expression_result
    result.extend(expression_result.unwrap())
    if structure.parameters is not None:
        for expression in structure.parameters:
            expression_result = _resolve_type_expression(
                parameter_name=parameter_name,
                expression=expression,
                type_text=type_text,
                module=module,
                project_context=project_context,
                file_analysis_cache=file_analysis_cache,
                class_name=class_name,
            )
            if isinstance(expression_result, Failure):
                return expression_result
            result.extend(expression_result.unwrap())
    return Success(tuple(result))


# def _resolve_unknown(
#     structure: UnknownStructureAnalysis,
#     parameter_name: str,
#     type_text: str,
#     module: ModuleAnalysis,
#     project_context: ProjectContext,
#     file_analysis_cache: FileAnalysisCache,
#     class_name: str | None,
# ) -> Result[tuple[ResolvedType, ...], ResolveError]:
#     return Failure(
#         ResolveError(message="Unsupported structure type", reference=type_text)
#     )


def _resolve_set(
    structure: SetStructureAnalysis,
    parameter_name: str,
    type_text: str,
    module: ModuleAnalysis,
    project_context: ProjectContext,
    file_analysis_cache: FileAnalysisCache,
    class_name: str | None,
) -> Result[tuple[ResolvedType, ...], ResolveError]:
    return _resolve_type_expression(
        expression=structure.element_type,
        parameter_name=parameter_name,
        type_text=type_text,
        module=module,
        project_context=project_context,
        file_analysis_cache=file_analysis_cache,
        class_name=class_name,
    )


def _resolve_keyword(
    structure: KeywordStructureAnalysis,
    parameter_name: str,
    type_text: str,
    module: ModuleAnalysis,
    project_context: ProjectContext,
    file_analysis_cache: FileAnalysisCache,
    class_name: str | None,
) -> Result[tuple[ResolvedType, ...], ResolveError]:

    return _resolve_type_expression(
        expression=structure.value,
        parameter_name=parameter_name,
        type_text=type_text,
        module=module,
        project_context=project_context,
        file_analysis_cache=file_analysis_cache,
        class_name=class_name,
    )
    # Maybe need to set parameter_name to structure.name??


def _resolve_call(
    structure: CallStructureAnalysis,
    parameter_name: str,
    type_text: str,
    module: ModuleAnalysis,
    project_context: ProjectContext,
    file_analysis_cache: FileAnalysisCache,
    class_name: str | None,
) -> Result[tuple[ResolvedType, ...], ResolveError]:
    result: list[ResolvedType] = []
    expression_result = _resolve_structure(
        parameter_name=parameter_name,
        structure=structure.function,
        type_text=type_text,
        module=module,
        project_context=project_context,
        file_analysis_cache=file_analysis_cache,
        class_name=class_name,
    )
    if isinstance(expression_result, Failure):
        return expression_result
    result.extend(expression_result.unwrap())
    for expression in structure.arguments:
        expression_result = _resolve_type_expression(
            parameter_name=parameter_name,
            expression=expression,
            type_text=type_text,
            module=module,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
            class_name=class_name,
        )
        if isinstance(expression_result, Failure):
            return expression_result
        result.extend(expression_result.unwrap())
    return Success(tuple(result))


def _resolve_ellipsis(
    structure: EllipsisStructureAnalysis,
    parameter_name: str,
    type_text: str,
    module: ModuleAnalysis,
    project_context: ProjectContext,
    file_analysis_cache: FileAnalysisCache,
    class_name: str | None,
) -> Result[tuple[ResolvedType, ...], ResolveError]:
    return Success(())


def _resolve_structure(
    structure: StructureAnalysis,
    parameter_name: str,
    type_text: str,
    module: ModuleAnalysis,
    project_context: ProjectContext,
    file_analysis_cache: FileAnalysisCache,
    class_name: str | None = None,
) -> Result[tuple[ResolvedType, ...], ResolveError]:

    if isinstance(structure, NameStructureAnalysis):
        return _resolve_name(
            structure=structure,
            parameter_name=parameter_name,
            type_text=type_text,
            module=module,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
            class_name=class_name,
        )
    if isinstance(structure, NoneStructureAnalysis):
        return _resolve_none(
            structure=structure,
            parameter_name=parameter_name,
            type_text=type_text,
            module=module,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
            class_name=class_name,
        )
    if isinstance(structure, LiteralStructureAnalysis):
        return _resolve_literal(
            structure=structure,
            parameter_name=parameter_name,
            type_text=type_text,
            module=module,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
            class_name=class_name,
        )
    if isinstance(structure, EllipsisStructureAnalysis):
        return _resolve_ellipsis(
            structure=structure,
            parameter_name=parameter_name,
            type_text=type_text,
            module=module,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
            class_name=class_name,
        )
    if isinstance(structure, UnionStructureAnalysis):
        return _resolve_union(
            structure=structure,
            parameter_name=parameter_name,
            type_text=type_text,
            module=module,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
            class_name=class_name,
        )

    if isinstance(structure, AttributeStructureAnalysis):
        return _resolve_attribute(
            structure=structure,
            parameter_name=parameter_name,
            type_text=type_text,
            module=module,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
            class_name=class_name,
        )
    if isinstance(structure, TupleStructureAnalysis):
        return _resolve_tuple(
            structure=structure,
            parameter_name=parameter_name,
            type_text=type_text,
            module=module,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
            class_name=class_name,
        )
    if isinstance(structure, ArrayStructureAnalysis):
        return _resolve_array(
            structure=structure,
            parameter_name=parameter_name,
            type_text=type_text,
            module=module,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
            class_name=class_name,
        )
    if isinstance(structure, DictionaryStructureAnalysis):
        return _resolve_dictionary(
            structure=structure,
            parameter_name=parameter_name,
            type_text=type_text,
            module=module,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
            class_name=class_name,
        )
    if isinstance(structure, GenericsStructureAnalysis):
        return _resolve_generics(
            structure=structure,
            parameter_name=parameter_name,
            type_text=type_text,
            module=module,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
            class_name=class_name,
        )
    if isinstance(structure, SetStructureAnalysis):
        return _resolve_set(
            structure=structure,
            parameter_name=parameter_name,
            type_text=type_text,
            module=module,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
            class_name=class_name,
        )
    if isinstance(structure, KeywordStructureAnalysis):
        return _resolve_keyword(
            structure=structure,
            parameter_name=parameter_name,
            type_text=type_text,
            module=module,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
            class_name=class_name,
        )
    if isinstance(structure, CallableStructureAnalysis):
        return _resolve_callable(
            structure=structure,
            parameter_name=parameter_name,
            type_text=type_text,
            module=module,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
            class_name=class_name,
        )
    if isinstance(structure, CallStructureAnalysis):
        return _resolve_call(
            structure=structure,
            parameter_name=parameter_name,
            type_text=type_text,
            module=module,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
            class_name=class_name,
        )
    else:
        raise ValueError(f"Unsupported Type: {type(structure).__name__}")


def _resolve_type_expression(
    expression: TypeExpression,
    parameter_name: str,
    type_text: str,
    module: ModuleAnalysis,
    project_context: ProjectContext,
    file_analysis_cache: FileAnalysisCache,
    class_name: str | None = None,
) -> Result[tuple[ResolvedType, ...], ResolveError]:
    if isinstance(expression, LiteralValue):
        return Success(
            (LiteralValueType(value=expression.value, parameter_name=parameter_name),)
        )
    return _resolve_structure(
        structure=expression,
        parameter_name=parameter_name,
        type_text=type_text,
        module=module,
        project_context=project_context,
        file_analysis_cache=file_analysis_cache,
        class_name=class_name,
    )


def resolve_type_analysis(
    type_analysis: TypeAnalysis,
    parameter_name: str,
    module: ModuleAnalysis,
    project_context: ProjectContext,
    file_analysis_cache: FileAnalysisCache,
    class_name: str | None = None,
) -> Result[tuple[ResolvedType, ...], ResolveError]:
    if type_analysis.structure is None:
        return Success(
            (LiteralValueType(value=type_analysis.text, parameter_name=parameter_name),)
        )
    return _resolve_structure(
        structure=type_analysis.structure,
        parameter_name=parameter_name,
        type_text=type_analysis.text,
        module=module,
        project_context=project_context,
        file_analysis_cache=file_analysis_cache,
        class_name=class_name,
    )
