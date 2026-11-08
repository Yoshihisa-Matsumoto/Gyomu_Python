from pathlib import Path

from gyomu_schema.schemas.config.test.model_defaults import Parameter
from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.type.type_analysis import TypeAnalysis
from gyomu_schema.schemas.python.types import (
    DeclarationIdentity,
    ProjectRelativePath,
    PythonPath,
)
from gyomu_schema.schemas.testing.helper import (
    ExistingHelperInventoryItem,
    HelperConfig,
    HelperFileAllocation,
    HelperFileInventory,
    HelperInventoryItem,
    HelperReconcileResult,
    HelperUpdate,
    ParameterInfo,
)

from packages.schema.test_support.helpers import (
    create_source_location,
    create_type_analysis,
    simple_create_declaration_identity,
)


def create_parameter_info(
    name: str = "arg",
    parameter_type: TypeAnalysis = create_type_analysis("str"),  # noqa: B008
    default: Parameter | None = None,
) -> ParameterInfo:
    return ParameterInfo(name=name, parameter_type=parameter_type, default=default)


def create_helper_inventory_item(
    target_identity: DeclarationIdentity = simple_create_declaration_identity(
        id="Test"
    ),  # noqa: B008
    function_name: str = "create_test",
    parameters: tuple[ParameterInfo, ...] = tuple(),
) -> HelperInventoryItem:
    return HelperInventoryItem(
        target_identity=target_identity,
        function_name=function_name,
        parameters=parameters,
    )


def create_existing_helper_inventory_item(
    target_identity: DeclarationIdentity = simple_create_declaration_identity(
        id="Test"
    ),  # noqa: B008
    function_name: str = "create_test",
    parameters: tuple[ParameterInfo, ...] = tuple(),
    location: SourceLocation = create_source_location(),  # noqa: B008
) -> ExistingHelperInventoryItem:
    return ExistingHelperInventoryItem(
        target_identity=target_identity,
        function_name=function_name,
        parameters=parameters,
        location=location,
    )


def create_helper_update(
    file_path: ProjectRelativePath = ProjectRelativePath(Path("tmp")),
    expected: HelperInventoryItem = create_helper_inventory_item(),
    existing: HelperInventoryItem = create_helper_inventory_item(),
) -> HelperUpdate:
    return HelperUpdate(file_path=file_path, expected=expected, existing=existing)


def create_helper_file_inventory(
    file_path: ProjectRelativePath = ProjectRelativePath(Path("tmp")),
    items: tuple[ExistingHelperInventoryItem, ...] = (
        create_existing_helper_inventory_item(),
    ),
    source_lines: tuple[str, ...] = ("",),
) -> HelperFileInventory:
    return HelperFileInventory(
        file_path=file_path, items=items, source_lines=source_lines
    )


def create_helper_reconcile_result(
    create: tuple[HelperInventoryItem, ...] = tuple(),
    update: tuple[HelperUpdate, ...] = tuple(),
    unchanged: tuple[ExistingHelperInventoryItem, ...] = tuple(),
    delete_candidates: tuple[ExistingHelperInventoryItem, ...] = tuple(),
) -> HelperReconcileResult:
    return HelperReconcileResult(
        create=create,
        update=update,
        unchanged=unchanged,
        delete_candidates=delete_candidates,
    )


def create_helper_file_allocation(
    path: PythonPath = PythonPath("test"), helper_filename: str = "helpers.py"
) -> HelperFileAllocation:
    return HelperFileAllocation(path=path, helper_filename=helper_filename)


def create_helper_config(
    helper_directory: str = "test_support",
    file_allocation: tuple[HelperFileAllocation, ...] = (),
) -> HelperConfig:
    return HelperConfig(
        helper_directory=helper_directory, file_allocation=file_allocation
    )
