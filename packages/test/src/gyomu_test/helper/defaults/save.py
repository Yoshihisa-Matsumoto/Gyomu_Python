from pathlib import Path

from gyomu_config.file.retrieve import retrieve_config
from gyomu_config.file.save import save_config
from gyomu_config.request import ConfigRequest
from gyomu_python_analysis.project.context import ProjectContext, WorkspaceProject
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_schema.error.config import ConfigError
from gyomu_schema.schemas.config.test.model_defaults import (
    ModelDefault,
    ModelDefaults,
    PackageModelDefaults,
    PrimitiveDefault,
    PrimitiveDefaults,
)
from gyomu_schema.schemas.python.types import PythonPath
from gyomu_schema.schemas.types import FullPath
from returns.result import Failure, Result, Success

from gyomu_test.error.test import GyomuTestError
from gyomu_test.helper.defaults.resolution import (
    _get_project_config_path,
    _get_project_config_path_from_workspace,
    _get_workspace_config_path,
)


class DefaultConfigPathResolver:
    def get_path(self, context: FullPath) -> Result[Path, ConfigError]:
        return Success(context)


def build_config_request(
    config_path: FullPath,
) -> ConfigRequest[PackageModelDefaults, FullPath]:
    return ConfigRequest(
        config_type=PackageModelDefaults,
        context=config_path,
        path_resolver=DefaultConfigPathResolver(),
    )


def _retrieve_existing_config(
    config_path: FullPath,
) -> Result[PackageModelDefaults, GyomuTestError]:
    request = build_config_request(config_path=config_path)
    config_retrieve_result = retrieve_config(request=request)
    if isinstance(config_retrieve_result, Failure):
        return config_retrieve_result.alt(
            lambda error: GyomuTestError("fail to retrieve default config").chain(error)
        )
    retrieved_config = config_retrieve_result.unwrap()
    if retrieved_config is None:
        retrieved_config = PackageModelDefaults(
            models_per_module_path={}, primitives_per_type={}
        )
    return Success(retrieved_config)


def _update_primitive(
    existing_config: PackageModelDefaults,
    primitive_default: PrimitiveDefault,
) -> PackageModelDefaults:
    primitives_per_type = dict(existing_config.primitives_per_type)

    type_defaults = primitives_per_type.get(primitive_default.type_name)
    defaults_per_variable_name = (
        dict(type_defaults.defaults_per_variable_name)
        if type_defaults is not None
        else {}
    )

    defaults_per_variable_name[primitive_default.variable_name] = (
        primitive_default.parameters
    )

    primitives_per_type[primitive_default.type_name] = PrimitiveDefaults(
        defaults_per_variable_name=defaults_per_variable_name
    )

    return PackageModelDefaults(
        models_per_module_path=existing_config.models_per_module_path,
        primitives_per_type=primitives_per_type,
    )


def _update_symbol(
    existing_config: PackageModelDefaults,
    module_path: PythonPath,
    model_default: ModelDefault,
) -> PackageModelDefaults:
    models_per_module_path = dict(existing_config.models_per_module_path)

    module_defaults = models_per_module_path.get(module_path)
    existing_models = module_defaults.models if module_defaults is not None else ()

    updated_models: list[ModelDefault] = []
    model_found = False

    for existing_model in existing_models:
        if existing_model.symbol_name == model_default.symbol_name:
            if not model_found:
                updated_models.append(model_default)
                model_found = True
        else:
            updated_models.append(existing_model)

    if not model_found:
        updated_models.append(model_default)

    models_per_module_path[module_path] = ModelDefaults(models=tuple(updated_models))

    return PackageModelDefaults(
        models_per_module_path=models_per_module_path,
        primitives_per_type=existing_config.primitives_per_type,
    )


def _save_config(
    config_path: FullPath, updated_config: PackageModelDefaults
) -> Result[None, GyomuTestError]:
    request = build_config_request(config_path=config_path)
    return save_config(request=request, value=updated_config).alt(
        lambda error: GyomuTestError("fail to save default config").chain(error)
    )


def save_primitive_parameter_default_config(
    workspace_context: WorkspaceContext,
    project_context: ProjectContext | None,
    primitive_default: PrimitiveDefault,
) -> Result[None, GyomuTestError]:
    config_path = (
        _get_project_config_path(project_context=project_context)
        if project_context is not None
        else _get_workspace_config_path(workspace_context=workspace_context)
    )
    config_result = _retrieve_existing_config(config_path=config_path)
    if isinstance(config_result, Failure):
        return config_result
    existing_config = config_result.unwrap()
    updated_config = _update_primitive(
        existing_config=existing_config, primitive_default=primitive_default
    )
    return _save_config(config_path=config_path, updated_config=updated_config)


def save_symbol_parameter_default_config(
    workspace_context: WorkspaceContext,
    workspace_project: WorkspaceProject | None,
    module_path: PythonPath,
    model_default: ModelDefault,
) -> Result[None, GyomuTestError]:
    config_path = (
        _get_project_config_path_from_workspace(
            workspace_context=workspace_context, workspace_project=workspace_project
        )
        if workspace_project is not None
        else _get_workspace_config_path(workspace_context=workspace_context)
    )
    config_result = _retrieve_existing_config(config_path=config_path)
    if isinstance(config_result, Failure):
        return config_result
    existing_config = config_result.unwrap()
    updated_config = _update_symbol(
        existing_config=existing_config,
        module_path=module_path,
        model_default=model_default,
    )
    return _save_config(config_path=config_path, updated_config=updated_config)
