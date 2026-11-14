from gyomu_config.file.retrieve import retrieve_config
from gyomu_config.file.save import save_config
from gyomu_python_analysis.analysis.load_file_context import load_file_analysis_context
from gyomu_python_analysis.path.conversion import get_project_relative_path
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.schemas.config.test.model_defaults import ModelDefault, ModelDefaults
from gyomu_schema.schemas.python.types import DeclarationIdentity
from returns.result import Failure, Result

from gyomu_test.error.test import GyomuTestError
from gyomu_test.helper.inventory.config import build_config_request


def update_model_default(
    project_context: ProjectContext,
    target_identity: DeclarationIdentity,
    model_default: ModelDefault,
) -> Result[None, GyomuTestError]:

    file_result = load_file_analysis_context(
        context=project_context,
        file_path=get_project_relative_path(
            project_context=project_context, identity=target_identity
        ),
    )
    if isinstance(file_result, Failure):
        return file_result.alt(
            lambda error: GyomuTestError(message="fail to load source").chain(error)
        )
    file_analysis = file_result.unwrap()

    config_request = build_config_request(
        file_analysis=file_analysis, project_context=project_context
    )
    default_config_result = retrieve_config(request=config_request)
    if isinstance(default_config_result, Failure):
        return default_config_result.alt(
            lambda error: GyomuTestError(message="fail to retrieve ").chain(error)
        )
    default_config = default_config_result.unwrap()
    models: list[ModelDefault] = []
    if default_config is not None:
        models.extend(default_config.models)
    models.append(model_default)

    model_defaults: ModelDefaults = ModelDefaults(models=tuple(models))
    return save_config(request=config_request, value=model_defaults).alt(
        lambda error: GyomuTestError("fail to save config").chain(error)
    )
