from collections.abc import Mapping

from gyomu_python_analysis.analysis.initialize import initialize_project_from_workspace
from gyomu_python_analysis.analysis.workspace import (
    find_root,
    initialize_workspace_context,
)
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import (
    WorkspaceContext,
    WorkspaceRoot,
)
from gyomu_python_analysis.resolve.models import (
    LiteralValueType,
    PrimitiveType,
    ResolvedType,
    SymbolType,
)
from gyomu_schema.schemas.config.test.model_defaults import (
    Argument,
    Arguments,
    AttributeParameter,
    CallParameter,
    DictEntry,
    DictParameter,
    KeywordArgument,
    LambdaParameter,
    ListParameter,
    LiteralParameter,
    NameParameter,
    NoneParameter,
    Parameter,
    TupleParameter,
)
from gyomu_schema.schemas.types import FullPath
from gyomu_test.error.test import GyomuTestError
from gyomu_test.helper.defaults.requirements import (
    ConfiguredParameterDefault,
    MissingParameterDefault,
    ResolvedParameterDefault,
)
from returns.result import Success


def create_gyomu_test_error(
    message: str = "test", details: Mapping[str, object] | None = None
) -> GyomuTestError:
    return GyomuTestError(message=message, details=details)


def get_project_context(
    workspace_context: WorkspaceContext, project_name: str
) -> ProjectContext:
    project = next(
        (
            project
            for project in workspace_context.projects
            if project.config.name == project_name
        ),
        None,
    )
    assert project is not None
    return initialize_project_from_workspace(
        workspace_path=workspace_context.path, project=project
    )


def get_workspace_context(
    current_path: FullPath,
) -> tuple[WorkspaceRoot, WorkspaceContext]:

    root_result = find_root(current_path)
    assert isinstance(root_result, Success)
    workspace = root_result.unwrap()
    workspace_context_result = initialize_workspace_context(workspace)
    assert isinstance(workspace_context_result, Success)

    return workspace, workspace_context_result.unwrap()


def validate_keyword_argument(
    result: KeywordArgument, expected: KeywordArgument
) -> None:
    assert result.name == expected.name
    assert validate_parameter(result.value, expected.value)


def validate_call_parameter(result: CallParameter, expected: CallParameter) -> None:
    assert result.callable_identity == expected.callable_identity
    assert len(result.args) == len(expected.args)
    for index, result_arg in enumerate(result.args):
        expected_arg = expected.args[index]
        validate_parameter(result_arg, expected_arg)
    assert len(result.kwargs) == len(expected.kwargs)
    for index, result_keyword in enumerate(result.kwargs):
        expected_keyword = result.kwargs[index]
        validate_keyword_argument(result_keyword, expected_keyword)


def validate_tuple_parameter(result: TupleParameter, expected: TupleParameter) -> None:
    assert len(result.elements) == len(expected.elements)
    for index, result_element in enumerate(result.elements):
        expected_element = expected.elements[index]
        validate_parameter(result=result_element, expected=expected_element)


def validate_list_parameter(result: ListParameter, expected: ListParameter) -> None:
    assert len(result.elements) == len(expected.elements)
    for index, result_element in enumerate(result.elements):
        expected_element = expected.elements[index]
        validate_parameter(result=result_element, expected=expected_element)


def validate_dict_entry(result: DictEntry, expected: DictEntry) -> None:
    validate_parameter(result=result.key, expected=expected.key)
    validate_parameter(result=result.value, expected=expected.value)


def validate_dict_parameter(result: DictParameter, expected: DictParameter) -> None:
    assert len(result.entries) == len(expected.entries)
    for index, result_entry in enumerate(result.entries):
        expected_entry = expected.entries[index]
        validate_dict_entry(result=result_entry, expected=expected_entry)


def validate_attribute_parameter(
    result: AttributeParameter, expected: AttributeParameter
) -> None:
    assert result.attribute == expected.attribute
    validate_parameter(result=result.value, expected=expected.value)


def validate_argument(result: Argument, expected: Argument) -> None:
    assert result.arg == expected.arg
    validate_parameter(result=result.annotation, expected=expected.annotation)


def validate_arguments(result: Arguments, expected: Arguments) -> None:
    assert len(result.posonlyargs) == len(expected.posonlyargs)
    for index, result_posonlyarg in enumerate(result.posonlyargs):
        expected_posonlyarg = expected.posonlyargs[index]
        validate_argument(result=result_posonlyarg, expected=expected_posonlyarg)

    assert len(result.args) == len(expected.args)
    for index, result_arg in enumerate(result.args):
        expected_arg = expected.args[index]
        validate_argument(result=result_arg, expected=expected_arg)

    assert len(result.defaults) == len(expected.defaults)
    for index, result_default in enumerate(result.defaults):
        expected_default = expected.defaults[index]
        validate_parameter(result=result_default, expected=expected_default)

    if result.vararg is not None:
        assert expected.vararg is not None
        validate_argument(result=result.vararg, expected=expected.vararg)
    else:
        assert expected.vararg is None

    assert len(result.kwonlyargs) == len(expected.kwonlyargs)
    for index, result_kwonlyarg in enumerate(result.kwonlyargs):
        expected_kwonlyarg = expected.kwonlyargs[index]
        validate_argument(result=result_kwonlyarg, expected=expected_kwonlyarg)

    assert len(result.kw_defaults) == len(expected.kw_defaults)
    for index, result_kw_default in enumerate(result.kw_defaults):
        expected_kw_default = expected.kw_defaults[index]
        validate_parameter(result=result_kw_default, expected=expected_kw_default)

    if result.kwarg is not None:
        assert expected.kwarg is not None
        validate_argument(result=result.kwarg, expected=expected.kwarg)
    else:
        assert expected.kwarg is None


def validate_lambda_parameter(
    result: LambdaParameter, expected: LambdaParameter
) -> None:
    validate_arguments(result=result.args, expected=expected.args)
    validate_parameter(result=result.body, expected=expected.body)


def validate_parameter(result: Parameter, expected: Parameter) -> None:
    if isinstance(result, LiteralParameter):
        assert isinstance(expected, LiteralParameter)
        assert result.value == expected.value
    elif isinstance(result, NoneParameter):
        assert isinstance(expected, NoneParameter)
    elif isinstance(result, NameParameter):
        assert isinstance(expected, NameParameter)
        assert result.name == expected.name
    elif isinstance(result, CallParameter):
        assert isinstance(expected, CallParameter)
        validate_call_parameter(result, expected)
    elif isinstance(result, TupleParameter):
        assert isinstance(expected, TupleParameter)
        validate_tuple_parameter(result, expected)
    elif isinstance(result, ListParameter):
        assert isinstance(expected, ListParameter)
        validate_list_parameter(result, expected)
    elif isinstance(result, DictParameter):
        assert isinstance(expected, DictParameter)
        validate_dict_parameter(result, expected)
    elif isinstance(result, AttributeParameter):
        assert isinstance(expected, AttributeParameter)
        validate_attribute_parameter(result, expected)
    elif isinstance(result, LambdaParameter):
        assert isinstance(expected, LambdaParameter)
        validate_lambda_parameter(result, expected)
    else:
        assert "Not Supported" == ""


def validate_resolved_parameter_default(
    result: ResolvedParameterDefault, expected: ResolvedParameterDefault
) -> None:
    assert result.parameter.name == expected.parameter.name

    result_default = result.default
    expected_default = result.default
    assert result_default is not None
    assert expected_default is not None
    validate_parameter(result=result_default, expected=expected_default)


def validate_resolved_type(result: ResolvedType, expected: ResolvedType) -> None:
    if isinstance(result, PrimitiveType):
        assert isinstance(expected, PrimitiveType)
        assert result.primitive_type == expected.primitive_type
        assert result.parameter_name == expected.parameter_name

    elif isinstance(result, LiteralValueType):
        assert isinstance(expected, LiteralValueType)
        assert result.parameter_name == expected.parameter_name
        assert result.value == expected.value
    else:
        assert isinstance(expected, SymbolType)
        assert result.symbol.name == expected.symbol.name
        assert (
            result.context.analysis.module_name == expected.context.analysis.module_name
        )


def validate_missing_parameter_default(
    result: MissingParameterDefault, expected: MissingParameterDefault
) -> None:
    assert result.parameter.name == expected.parameter.name

    result_missing_types = result.missing_types
    expected_missing_types = result.missing_types

    for index, result_missing_type in enumerate(result_missing_types):
        expected_missing_type = expected_missing_types[index]
        validate_resolved_type(
            result=result_missing_type, expected=expected_missing_type
        )


def validate_parameters(
    result: tuple[
        ConfiguredParameterDefault | ResolvedParameterDefault | MissingParameterDefault,
        ...,
    ],
    expected: tuple[ResolvedParameterDefault | MissingParameterDefault, ...],
) -> None:
    assert len(result) == len(expected)
    for index, result_parameter in enumerate(result):
        expected_parameter = result[index]

        assert not isinstance(result_parameter, ConfiguredParameterDefault)

        if isinstance(result_parameter, ResolvedParameterDefault):
            assert isinstance(expected_parameter, ResolvedParameterDefault)
            validate_resolved_parameter_default(
                result=result_parameter, expected=expected_parameter
            )
        else:
            assert isinstance(expected_parameter, MissingParameterDefault)
            validate_missing_parameter_default(
                result=result_parameter, expected=expected_parameter
            )
