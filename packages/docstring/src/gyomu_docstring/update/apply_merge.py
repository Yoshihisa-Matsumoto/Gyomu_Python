from gyomu_python_analysis.error.update import UpdateError
from gyomu_schema.schemas.python.docstring import (
    DocstringAnalysis,
    DocstringParametersSection,
    DocstringParametersSectionItem,
    DocstringRaisesSection,
    DocstringRaisesSectionItem,
    DocstringReturnsSection,
    DocstringReturnsSectionItem,
    DocstringSection,
    DocstringStyle,
)
from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.symbol_base import DeclarationKind
from gyomu_schema.schemas.python.types import DeclarationIdentity, PythonPath
from returns.result import Failure, Result, Success

from gyomu_docstring.update.docstring.merge_plan import (
    DeleteAction,
    MergeAction,
    MergePlan,
    ParamMergePlan,
    PreserveAction,
    RaiseMergePlan,
    ReplaceAction,
    ReturnActionValue,
)
from gyomu_docstring.update.docstring.updated_docstring import UpdatedDocstring


def apply_merge_plans(
    context: FileAnalysisContext, plans: tuple[MergePlan, ...]
) -> Result[tuple[UpdatedDocstring, ...], UpdateError]:
    results: list[UpdatedDocstring] = []

    for plan in plans:
        result = apply_merge_plan(context, plan)

        if isinstance(result, Failure):
            return result

        results.append(result.unwrap())

    return Success(tuple(results))


def apply_merge_plan(
    context: FileAnalysisContext, plan: MergePlan
) -> Result[UpdatedDocstring, UpdateError]:
    existing_docstring = context.metadata.parsed_docstring.get(plan.identity)
    existing_symbol_or_method = context.metadata.symbols.get(plan.identity)

    if existing_symbol_or_method is None:
        return Failure(
            UpdateError(
                "Symbol/Method not found",
                file_path=context.analysis.module_name,
                phase="apply-merge",
                identity=plan.identity,
            )
        )
    if (
        existing_symbol_or_method.location is None
        or existing_symbol_or_method.indent is None
    ):
        return Failure(
            UpdateError(
                "Constructor private variable should not be here",
                file_path=context.analysis.module_name,
                phase="apply-merge",
                identity=plan.identity,
            )
        )

    summary = _merge_summary(plan.summary, existing_docstring)
    description = _merge_description(plan.description, existing_docstring)

    arguments_result = _merge_arguments(
        file_path=context.analysis.module_name,
        identity=plan.identity,
        plans=plan.params,
        existing_docstring=existing_docstring,
    )
    if isinstance(arguments_result, Failure):
        return arguments_result

    returns = _merge_returns(
        plan.returns,
        existing_docstring,
    )

    raises_result = _merge_raises(
        file_path=context.analysis.module_name,
        identity=plan.identity,
        plans=plan.raises,
        existing_docstring=existing_docstring,
    )
    if isinstance(raises_result, Failure):
        return raises_result

    sections = _merge_sections(
        existing_docstring=existing_docstring,
        arguments=arguments_result.unwrap(),
        returns=returns,
        raises=raises_result.unwrap(),
    )
    new_location = (
        existing_docstring.location if existing_docstring is not None else None
    )
    if new_location is None:
        new_location = SourceLocation(
            start_line=existing_symbol_or_method.location.start_line,
            end_line=existing_symbol_or_method.location.end_line,
            start_offset=existing_symbol_or_method.location.end_offset,
            end_offset=existing_symbol_or_method.location.end_offset,
            start_column=existing_symbol_or_method.location.start_column,
            end_column=existing_symbol_or_method.location.start_column,
        )

    new_indent = existing_docstring.indent if existing_docstring is not None else None

    if new_indent is None:
        if existing_symbol_or_method.kind in (
            DeclarationKind.CLASS,
            DeclarationKind.FUNCTION,
            DeclarationKind.METHOD,
        ):
            new_indent = existing_symbol_or_method.indent + 4
        else:
            new_indent = existing_symbol_or_method.indent

    updated_docstring = DocstringAnalysis(
        raw=existing_docstring.raw if existing_docstring is not None else "",
        summary=summary,
        description=description,
        style=(
            existing_docstring.style
            if existing_docstring is not None
            else DocstringStyle.GOOGLE
        ),
        location=new_location,
        sections=sections,
        indent=new_indent,
    )

    return Success(
        UpdatedDocstring(
            identity=plan.identity,
            docstring=updated_docstring,
        )
    )


def _merge_sections(
    existing_docstring: DocstringAnalysis | None,
    arguments: tuple[DocstringParametersSectionItem, ...],
    returns: DocstringReturnsSectionItem | None,
    raises: tuple[DocstringRaisesSectionItem, ...],
) -> tuple[DocstringSection, ...]:
    existing_sections = (
        existing_docstring.sections if existing_docstring is not None else ()
    )

    sections: list[DocstringSection] = []

    arguments_added = False
    returns_added = False
    raises_added = False

    for section in existing_sections:
        match section:
            case DocstringParametersSection():
                if arguments:
                    sections.append(DocstringParametersSection(items=arguments))
                arguments_added = True

            case DocstringReturnsSection():
                if returns is not None:
                    sections.append(DocstringReturnsSection(item=returns))
                returns_added = True

            case DocstringRaisesSection():
                if raises:
                    sections.append(DocstringRaisesSection(items=raises))
                raises_added = True

            case _:
                sections.append(section)

    if arguments and not arguments_added:
        sections.append(DocstringParametersSection(items=arguments))

    if returns is not None and not returns_added:
        sections.append(DocstringReturnsSection(item=returns))

    if raises and not raises_added:
        sections.append(DocstringRaisesSection(items=raises))

    return tuple(sections)


def _merge_summary(
    plan: MergeAction[str], existing_docstring: DocstringAnalysis | None
) -> str | None:
    match plan.type:
        case "preserve":
            if existing_docstring is None:
                return None
            return existing_docstring.summary
        case "delete":
            return None
        case "replace":
            return plan.value


def _merge_description(
    plan: MergeAction[str], existing_docstring: DocstringAnalysis | None
) -> str | None:
    match plan.type:
        case "preserve":
            if existing_docstring is None:
                return None
            return existing_docstring.description
        case "delete":
            return None
        case "replace":
            return plan.value


def _find_section[T: DocstringSection](
    existing_docstring: DocstringAnalysis | None, section_type: type[T]
) -> T | None:
    if existing_docstring is None:
        return None
    existing_parameters = next(
        (
            section
            for section in existing_docstring.sections
            if isinstance(section, section_type)
        ),
        None,
    )
    return existing_parameters


def _merge_arguments(
    file_path: PythonPath,
    identity: DeclarationIdentity,
    plans: tuple[ParamMergePlan, ...],
    existing_docstring: DocstringAnalysis | None,
) -> Result[
    tuple[DocstringParametersSectionItem, ...],
    UpdateError,
]:
    parameters_section = _find_section(existing_docstring, DocstringParametersSection)
    existing_parameters_by_name = (
        {item.name: item for item in parameters_section.items}
        if parameters_section is not None
        else {}
    )

    merged: list[tuple[int, DocstringParametersSectionItem]] = []

    for plan in plans:
        existing_param = existing_parameters_by_name.get(plan.name)

        match plan.action:
            case PreserveAction():
                if existing_param is not None:
                    merged.append((plan.sort_order, existing_param))

            case DeleteAction():
                pass

            case ReplaceAction(value=value):
                if (
                    existing_param is None
                    and value.parameter_type is None
                    and value.description is None
                ):
                    return Failure(
                        UpdateError(
                            file_path=file_path,
                            message="Planned Argument doesn not have valid Argument",
                            phase="update-plan",
                            details={"plannedParameter": plan},
                            identity=identity,
                        )
                    )

                merged.append(
                    (
                        plan.sort_order,
                        DocstringParametersSectionItem(
                            name=plan.name,
                            type=(
                                value.parameter_type
                                if value.parameter_type is not None
                                else existing_param.type
                                if existing_param is not None
                                else None
                            ),
                            description=(
                                value.description
                                if value.description is not None
                                else existing_param.description
                                if existing_param is not None
                                else ""
                            ),
                        ),
                    )
                )

    merged.sort(key=lambda item: item[0])

    return Success(tuple(item for _, item in merged))


def _merge_returns(
    plan: MergeAction[ReturnActionValue], existing_docstring: DocstringAnalysis | None
) -> DocstringReturnsSectionItem | None:
    returns_section = _find_section(existing_docstring, DocstringReturnsSection)
    existing_item = returns_section.item if returns_section is not None else None
    match plan.type:
        case "preserve":
            if existing_item is None:
                return None
            return existing_item
        case "delete":
            return None
        case "replace":
            new_value = plan.value
            return (
                DocstringReturnsSectionItem(
                    description=new_value.description,
                    type=new_value.return_type
                    if new_value.return_type is not None
                    else existing_item.type
                    if existing_item is not None
                    else None,
                )
                if new_value.description is not None
                else existing_item
            )


def _merge_raises(
    file_path: PythonPath,
    identity: DeclarationIdentity,
    plans: tuple[RaiseMergePlan, ...],
    existing_docstring: DocstringAnalysis | None,
) -> Result[
    tuple[DocstringRaisesSectionItem, ...],
    UpdateError,
]:
    raises_section = _find_section(existing_docstring, DocstringRaisesSection)
    existing_raises_by_type = (
        {item.type: item for item in raises_section.items}
        if raises_section is not None
        else {}
    )

    merged: list[tuple[int, DocstringRaisesSectionItem]] = []

    for plan in plans:
        existing_raise = existing_raises_by_type.get(plan.exception_type)

        match plan.action:
            case PreserveAction():
                if existing_raise is not None:
                    merged.append((plan.sort_order, existing_raise))

            case DeleteAction():
                pass

            case ReplaceAction(value=value):
                if existing_raise is None and value.description is None:
                    return Failure(
                        UpdateError(
                            file_path=file_path,
                            message="Planned Raises doesn not have valid Raise Item",
                            phase="update-plan",
                            details={"plannedParameter": plan},
                            identity=identity,
                        )
                    )

                merged.append(
                    (
                        plan.sort_order,
                        DocstringRaisesSectionItem(
                            type=(value.exception_type),
                            description=(
                                value.description
                                if value.description is not None
                                else existing_raise.description
                                if existing_raise is not None
                                else ""
                            ),
                        ),
                    )
                )

    merged.sort(key=lambda item: item[0])

    return Success(tuple(item for _, item in merged))
