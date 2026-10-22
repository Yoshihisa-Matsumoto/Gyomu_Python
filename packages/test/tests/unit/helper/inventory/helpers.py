from dataclasses import dataclass

from gyomu_python_analysis.analysis.initialize import initialize_project_from_workspace
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import (
    WorkspaceContext,
)
from gyomu_schema.schemas.python.types import (
    DeclarationId,
    DeclarationIdentity,
    ProjectRelativePath,
    PythonPath,
    SymbolId,
    WorkspaceRelativePath,
)
from gyomu_schema.schemas.testing.helper import HelperInventoryItem, ParameterInfo
from gyomu_test.error.inventory import ProjectInventoryError


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


@dataclass
class ParameterSummary:
    name: str
    parameter_type: str


def equal_helper_inventory_parameter(
    parameters: tuple[ParameterInfo, ...], parameter_name: str, parameter_type: str
) -> None:
    target_parameter = next(
        (parameter for parameter in parameters if parameter.name == parameter_name),
        None,
    )
    assert target_parameter is not None
    assert target_parameter.parameter_type.text == parameter_type


def function_not_exist_in_inventory(
    inventories: tuple[HelperInventoryItem, ...], function_name: str
) -> None:
    target_inventory = next(
        (
            inventory
            for inventory in inventories
            if str(inventory.function_name) == function_name
        ),
        None,
    )
    assert target_inventory is None


def inventory_not_exist(
    inventories: tuple[HelperInventoryItem, ...], symbol_id: str
) -> None:
    target_inventory = next(
        (
            inventory
            for inventory in inventories
            if str(inventory.target_identity.symbol_id) == symbol_id
        ),
        None,
    )
    assert target_inventory is None


def equal_helper_inventory(
    inventories: tuple[HelperInventoryItem, ...],
    symbol_id: str,
    function_name: str,
    parameters: tuple[ParameterSummary, ...],
) -> None:
    target_inventory = next(
        (
            inventory
            for inventory in inventories
            if inventory.function_name == function_name
        ),
        None,
    )
    assert target_inventory is not None
    assert str(target_inventory.target_identity.symbol_id) == symbol_id

    for parameter in parameters:
        equal_helper_inventory_parameter(
            target_inventory.parameters,
            parameter_name=parameter.name,
            parameter_type=parameter.parameter_type,
        )
    actual_parameters = {
        parameter.name: parameter.parameter_type.text
        for parameter in target_inventory.parameters
    }
    expected_parameters = {
        parameter.name: parameter.parameter_type for parameter in parameters
    }

    assert actual_parameters == expected_parameters


def helper_project_relative_path_to_python_path(
    path: WorkspaceRelativePath,
) -> PythonPath:
    """Converts a source-relative path to a Python dotted module path."""

    if path.name == "__init__.py":
        path = WorkspaceRelativePath(path.parent)
    else:
        path = WorkspaceRelativePath(path.with_suffix(""))

    return PythonPath(".".join(path.parts))


def _to_workspace_relative_path(
    path: ProjectRelativePath, project: ProjectContext, workspace: WorkspaceContext
) -> WorkspaceRelativePath:
    full_path = project.project_root / path
    return WorkspaceRelativePath(full_path.relative_to(workspace.path))


def error_contains_missing_parameter_type_annotation(
    failure: ProjectInventoryError,
    file_path: ProjectRelativePath,
    project: ProjectContext,
    workspace: WorkspaceContext,
    function_name: str,
    parameter: str,
) -> None:
    workspace_relative_path = _to_workspace_relative_path(file_path, project, workspace)
    python_path = helper_project_relative_path_to_python_path(workspace_relative_path)
    identity = DeclarationIdentity(
        symbol_id=SymbolId(f"{python_path}::{function_name}"),
        declaration_id=DeclarationId(f".::{parameter}"),
    )
    error_contains_missing_type_annotation(
        failure=failure,
        file_path=ProjectRelativePath(workspace_relative_path),
        identity=identity,
    )


def error_contains_missing_return_type_annotation(
    failure: ProjectInventoryError,
    file_path: ProjectRelativePath,
    project: ProjectContext,
    workspace: WorkspaceContext,
    function_name: str,
) -> None:
    workspace_relative_path = _to_workspace_relative_path(file_path, project, workspace)
    print(workspace_relative_path)
    python_path = helper_project_relative_path_to_python_path(workspace_relative_path)
    print(python_path)
    identity = DeclarationIdentity(
        symbol_id=SymbolId(f"{python_path}::{function_name}"),
        declaration_id=DeclarationId("."),
    )
    error_contains_missing_type_annotation(
        failure=failure,
        file_path=ProjectRelativePath(workspace_relative_path),
        identity=identity,
    )


def error_contains_missing_type_annotation(
    failure: ProjectInventoryError,
    file_path: ProjectRelativePath,
    identity: DeclarationIdentity,
) -> None:
    target_file = next(
        file for file in failure.error_files if file.project_relative_path == file_path
    )
    assert target_file.missing_annotations
    target_error = next(
        error for error in target_file.missing_annotations if error.identity == identity
    )
    assert target_error


def error_contains_function_reference_error(
    failure: ProjectInventoryError,
    file_path: ProjectRelativePath,
    project: ProjectContext,
    workspace: WorkspaceContext,
    function_name: str,
    return_type_name: str,
) -> None:
    workspace_relative_path = _to_workspace_relative_path(file_path, project, workspace)
    print(workspace_relative_path)
    python_path = helper_project_relative_path_to_python_path(workspace_relative_path)
    print(python_path)
    identity = DeclarationIdentity(
        symbol_id=SymbolId(f"{python_path}::{function_name}"),
        declaration_id=DeclarationId("."),
    )
    error_contains_reference_error(
        failure=failure,
        file_path=ProjectRelativePath(workspace_relative_path),
        identity=identity,
        reference=return_type_name,
    )


def error_contains_reference_error(
    failure: ProjectInventoryError,
    file_path: ProjectRelativePath,
    identity: DeclarationIdentity,
    reference: str,
) -> None:
    target_file = next(
        file for file in failure.error_files if file.project_relative_path == file_path
    )
    assert target_file.missing_annotations
    target_error = next(
        error
        for error in target_file.reference_errors
        if error.identity == identity and error.reference == reference
    )
    assert target_error


def error_contains_duplicate(
    failure: ProjectInventoryError,
    file_path: ProjectRelativePath,
    function_name: str,
    identity: DeclarationIdentity,
) -> None:
    target_duplicate = next(
        duplicate
        for duplicate in failure.duplicates
        if duplicate.target_identity == identity
    )
    target_function = next(
        func
        for func in target_duplicate.functions
        if func.function_name == function_name and func.file_path == file_path
    )
    assert target_function
