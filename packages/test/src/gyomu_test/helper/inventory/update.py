from gyomu_infra.filesystem.file_io import write_text
from gyomu_python_analysis.analysis.load_file_context import load_file_analysis_context
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_python_analysis.resolve.models import ReferencedType
from gyomu_python_analysis.source_code import get_import_insertion_line
from gyomu_schema.schemas.config.test.model_defaults import (
    ModelDefault,
)
from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.types import (
    DeclarationIdentity,
    ProjectRelativePath,
    SymbolId,
    WorkspaceRelativePath,
)
from gyomu_schema.schemas.testing.helper import (
    HelperInventoryItem,
)
from returns.result import Failure, Result, Success

from gyomu_test.error.test import GyomuTestError
from gyomu_test.helper.inventory.config import get_helper_file_path
from gyomu_test.helper.inventory.expected import reflect_updated_inventory
from gyomu_test.helper.inventory.function import (
    generate_function_code_lines,
    generate_import_code_lines,
)


def update_helper_file(
    expected_item: HelperInventoryItem,
    workspace_context: WorkspaceContext,
    project_context: ProjectContext,
    model_default: ModelDefault,
    referenced_types: tuple[ReferencedType, ...],
    existing_item: HelperInventoryItem | None,
) -> Result[WorkspaceRelativePath, GyomuTestError]:
    # decide which helpers file to be updated/created
    helper_file_result = get_helper_file_path(
        model_identity=expected_item.target_identity, project_context=project_context
    )
    if isinstance(helper_file_result, Failure):
        return helper_file_result
    helper_file_path = ProjectRelativePath(
        helper_file_result.unwrap().relative_to(
            workspace_context.root_project_context.project_root
        )
    )

    update_file_lines: list[str] = []
    last_line = 0
    existing_function_location: SourceLocation | None = None
    if (
        workspace_context.root_project_context.project_root / helper_file_path
    ).exists():
        file_result = load_file_analysis_context(
            workspace_context.root_project_context, helper_file_path
        )
        if isinstance(file_result, Failure):
            return file_result.alt(
                lambda error: GyomuTestError(message="fail to load helper file").chain(
                    error
                )
            )
        helper_file_analysis = file_result.unwrap()

        existing_function_symbol = (
            helper_file_analysis.metadata.symbols.get(
                DeclarationIdentity.create_from_symbol_id(
                    symbol_id=SymbolId(
                        f"{helper_file_analysis.analysis.module_name}::{existing_item.function_name}"
                    )
                )
            )
            if existing_item is not None
            else None
        )
        existing_function_location = (
            existing_function_symbol.location
            if existing_function_symbol is not None
            else None
        )

        if existing_item is not None and existing_function_location is None:
            return Failure(GyomuTestError(message="existing helper function not found"))

        update_file_lines.extend(helper_file_analysis.source_lines)
        last_line = get_import_insertion_line(helper_file_analysis)

    if existing_item is not None and existing_function_location is None:
        return Failure(GyomuTestError(message="existing helper function not found"))
    # insert helper function
    reflected_item = reflect_updated_inventory(
        inventory=expected_item, model_default=model_default
    )
    function_lines = generate_function_code_lines(reflected_item)
    if existing_item is None:
        update_file_lines.append("")
        update_file_lines.extend(function_lines)
    else:
        assert existing_function_location is not None
        update_file_lines[
            existing_function_location.start_line
            - 1 : existing_function_location.end_line
        ] = function_lines

    # insert import statement

    # print(format_object(unique_ref_types))
    import_lines = generate_import_code_lines(expected_item, referenced_types)
    update_file_lines[last_line : last_line + 1] = import_lines

    # save helper file
    # print(helper_file_path)
    # breakpoint()
    write_result = write_text(
        workspace_context.root_project_context.project_root / helper_file_path,
        "".join(update_file_lines),
    )
    if isinstance(write_result, Failure):
        return write_result.alt(
            lambda error: GyomuTestError(message="fail to write file").chain(error)
        )
    return Success(WorkspaceRelativePath(helper_file_path))
