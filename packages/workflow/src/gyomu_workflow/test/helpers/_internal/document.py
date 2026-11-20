from pathlib import Path

from gyomu_python_analysis.resolve.models import PackageType, SymbolType
from gyomu_schema.error.gyomu import GyomuError
from gyomu_schema.error.validation import ValidationError
from gyomu_schema.protocols.interaction import InteractionExecutor
from gyomu_schema.schemas.config.test.model_defaults import (
    Parameter,
)
from gyomu_schema.schemas.interaction.request import (
    InputMode,
    InteractionDocumentRequest,
    InteractionRequest,
)
from gyomu_schema.schemas.interaction.result import (
    InteractionCancelled,
)
from gyomu_schema.schemas.python.types import DeclarationIdentity
from gyomu_test.helper.defaults.requirements import (
    ResolvedParameterDefault,
)
from gyomu_test.helper.defaults.validate import (
    prepare_directory,
    validate_file_parameter,
)
from returns.result import Failure, Result, Success

from gyomu_workflow.test.helpers._internal.error import wrap_gyomu_error
from gyomu_workflow.test.helpers.models import (
    DefaultTypeParameterContext,
)


def _build_necessary_import_lines(
    context: DefaultTypeParameterContext,
) -> tuple[str, ...]:
    imports: list[str] = []
    for resolved_type in context.parameter.missing_types:
        if isinstance(resolved_type, SymbolType):
            imports.append(
                f"from {resolved_type.symbol.identity.get_module_name()} "
                f"import {resolved_type.symbol.identity.get_symbol_name()}"
            )
        elif isinstance(resolved_type, PackageType):
            identity = DeclarationIdentity.create_from_symbol_id(
                symbol_id=resolved_type.symbol_id
            )
            imports.append(
                f"from {identity.get_module_name()} import {identity.get_symbol_name()}"
            )
    return tuple(imports)


def _build_variable_line(context: DefaultTypeParameterContext) -> str:
    return (
        f"{context.parameter.parameter.name}: "
        f"{context.parameter.parameter.parameter_type.text} = "
    )


class ComplexValueProvider:
    def create_initial_text(
        self,
        context: DefaultTypeParameterContext,
    ) -> Result[str, GyomuError]:
        lines: list[str] = []
        lines.extend(_build_necessary_import_lines(context=context))
        lines.append(_build_variable_line(context=context))
        return Success("\n".join(lines))

    def parse(
        self,
        document: Path,
        context: DefaultTypeParameterContext,
    ) -> Result[Parameter, ValidationError]:

        return validate_file_parameter(
            file_path=document,
            root_project_context=context.workspace_root_project_context,
            project_context=context.project_context,
            workspace_context=context.workspace_context,
            parameter_name=context.parameter.parameter.name,
        ).alt(
            lambda error: ValidationError(
                message="fail to compute parameter", location=(str(document),)
            ).chain(error)
        )


def _build_document_interaction_request(
    parameter_context: DefaultTypeParameterContext,
) -> Result[
    InteractionRequest[str, Path, DefaultTypeParameterContext, Parameter], GyomuError
]:

    complex_provider = ComplexValueProvider()
    prepare_result = prepare_directory(
        project_context=parameter_context.project_context
    )
    if isinstance(prepare_result, Failure):
        return prepare_result.alt(
            lambda error: wrap_gyomu_error(
                error, "fail to prepare validation directory"
            )
        )
    temporary_directory = prepare_result.unwrap()
    return Success(
        InteractionDocumentRequest[Path, DefaultTypeParameterContext, Parameter](
            instruction="Please define your type parameter for ",
            context=parameter_context,
            input_mode=InputMode.DOCUMENT,
            codec=complex_provider,
            text_provider=complex_provider,
            temporary_directory=temporary_directory,
        )
    )


def define_document_parameter(
    parameter_context: DefaultTypeParameterContext,
    interaction: InteractionExecutor[str, Path],
) -> Result[ResolvedParameterDefault, GyomuError]:
    request_result = _build_document_interaction_request(
        parameter_context=parameter_context
    )
    if isinstance(request_result, Failure):
        return request_result
    request = request_result.unwrap()
    interaction_result = interaction.execute(request=request)
    if isinstance(interaction_result, Failure):
        return interaction_result
    result = interaction_result.unwrap()
    if isinstance(result, InteractionCancelled):
        return Failure(
            GyomuError(
                "parameter was not defined by user",
                operation="test",
                domain="test",
                reason="external_failure",
            )
        )
    return Success(
        ResolvedParameterDefault(
            parameter=parameter_context.parameter.parameter, default=result.value
        )
    )
