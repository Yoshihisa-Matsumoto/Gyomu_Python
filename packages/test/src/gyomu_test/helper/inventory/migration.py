from os import getcwd
from pathlib import Path

from gyomu_infra.filesystem.file_io import write_json
from gyomu_infra.logger import logger
from gyomu_python_analysis.analysis.initialize import (
    initialize_project_context,
)
from gyomu_python_analysis.analysis.resolve.cls import resolve_class_analysis
from gyomu_python_analysis.analysis.resolve.file_analysis_cache import FileAnalysisCache
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_schema.schemas.config.test.model_defaults import (
    ModelDefault,
    ModelDefaults,
    ParameterDefault,
)
from gyomu_schema.schemas.python.types import ProjectRelativePath, PythonPath
from gyomu_schema.schemas.testing.helper import HelperFileInventory
from gyomu_schema.schemas.types import FullPath
from gyomu_schema.utility.fromatting import format_object
from gyomu_workflow.snapshot.workspace import get_workspace_context
from returns.result import Failure, Success

from gyomu_test.helper.inventory.existing import collect_existing_helper_inventory
from gyomu_test.helper.inventory.expected import _is_model_candidate
from gyomu_test.helper.inventory.path import get_default_config_path
from packages.test.tests.unit.helper.inventory.helpers import get_project_context


def assemble_model_defaults(
    file_inventory: HelperFileInventory,
    model_defaults_by_module: dict[PythonPath, list[ModelDefault]],
    project_context: ProjectContext,
    workspace: WorkspaceContext,
) -> None:
    file_analysis_cache = FileAnalysisCache(workspace_context=workspace)
    for inventory in file_inventory.items:
        model_class_name = inventory.target_identity.get_symbol_name()
        model_path = inventory.target_identity.get_module_name()
        model_default_list = model_defaults_by_module.setdefault(model_path, [])

        class_result = resolve_class_analysis(
            declaration_identity=inventory.target_identity,
            project_context=project_context,
            file_analysis_cache=file_analysis_cache,
        )
        assert isinstance(class_result, Success)
        file_analysis, symbol = class_result.unwrap()
        candidate_result = _is_model_candidate(
            symbol=symbol, module=file_analysis.analysis, workspace=workspace
        )
        assert isinstance(candidate_result, Success)
        if candidate_result.unwrap():
            invalid_parameters: list[str] = []
            parameters: list[ParameterDefault] = []
            for parameter in inventory.parameters:
                if parameter.default is None:
                    invalid_parameters.append(parameter.name)

                parameters.append(
                    ParameterDefault(name=parameter.name, value=parameter.default)
                )

            if invalid_parameters:
                logger.info(
                    message=(
                        f"helper for {inventory.target_identity.symbol_id} "
                        "has parameters without default values: "
                        f"{format_object(invalid_parameters)}"
                    )
                )
            class_default = ModelDefault(
                class_name=model_class_name, parameters=tuple(parameters)
            )
            model_default_list.append(class_default)


def migrate(
    package_name: str,
    target_path: Path | None = None,
    helper_files: tuple[ProjectRelativePath, ...] = (
        ProjectRelativePath(Path("test_support/helpers.py")),
    ),
) -> None:
    if target_path is None:
        target_path = FullPath(Path(getcwd()))
    else:
        target_path = FullPath(target_path)
    workspace_result = get_workspace_context(target_path)
    if isinstance(workspace_result, Failure):
        logger.error_object(workspace_result.failure())
        return
    workspace_context = workspace_result.unwrap()

    project_context = get_project_context(workspace_context, package_name)

    root_context_result = initialize_project_context(
        project_root=workspace_context.path,
        source_root=ProjectRelativePath(Path(".")),
    )
    assert isinstance(root_context_result, Success)

    existing_result = collect_existing_helper_inventory(
        root=root_context_result.unwrap(),
        target_project=project_context,
        files=helper_files,
    )
    assert isinstance(existing_result, Success)
    existings = existing_result.unwrap()
    model_defaults_by_module: dict[PythonPath, list[ModelDefault]] = {}
    for existing in existings:
        assemble_model_defaults(
            existing,
            model_defaults_by_module=model_defaults_by_module,
            project_context=project_context,
            workspace=workspace_context,
        )
        for python_path in model_defaults_by_module:
            module_defaults = ModelDefaults(
                models=tuple(model_defaults_by_module[python_path])
            )
            file_path = get_default_config_path(
                python_path=python_path, project_context=project_context
            )
            write_result = write_json(
                path=file_path, value=module_defaults, value_type=ModelDefaults
            )
            assert isinstance(write_result, Success)
