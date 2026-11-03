from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import (
    WorkspaceContext,
    WorkspaceRoot,
    WorkspaceRootKind,
)
from gyomu_python_analysis.resolve.models import (
    LiteralValueType,
    PrimitiveType,
    SymbolType,
)
from gyomu_python_analysis.resolve.project_membership import (
    find_workspace_project,
    is_file_in_project,
)
from gyomu_schema.error.config import ConfigError
from gyomu_schema.schemas.config.test.model_defaults import (
    ModelDefault,
    PackageModelDefaults,
    PrimitiveDefault,
)
from gyomu_schema.schemas.testing.helper import HelperInventoryItem
from gyomu_schema.schemas.types import FullPath
from returns.result import Failure, Result, Success

from gyomu_test.error.parameter import (
    MissingFunctionParameterDefault,
)
from gyomu_test.helper.inventory.expected import _get_model_kind


def find_missing_function_parameter_defaults(
    inventory: HelperInventoryItem,
) -> tuple[MissingFunctionParameterDefault, ...] | None:
    missing_function_default_parameters: list[MissingFunctionParameterDefault] = []
    for parameter in inventory.parameters:
        if parameter.default is None:
            missing_function_default_parameters.append(
                MissingFunctionParameterDefault(
                    identity=inventory.target_identity, parameter=parameter
                )
            )

    if len(missing_function_default_parameters) > 0:
        return tuple(missing_function_default_parameters)
    return None


def _get_config_path(root_path: FullPath) -> FullPath:
    return root_path / ".gyomu" / "config"


class PrimitiveDefaultConfigContext:
    type_default: PrimitiveType | LiteralValueType
    workspace_root: WorkspaceRoot
    workspace_context: WorkspaceContext
    project_context: ProjectContext

    def __init__(
        self,
        type_default: PrimitiveType | LiteralValueType,
        workspace_root: WorkspaceRoot,
        workspace_context: WorkspaceContext,
        project_context: ProjectContext,
    ):
        self.type_default = type_default
        self.workspace_root = workspace_root
        self.workspace_context = workspace_context
        self.project_context = project_context


class SymbolDefaultConfigContext:
    type_default: SymbolType
    workspace_root: WorkspaceRoot
    workspace_context: WorkspaceContext
    project_context: ProjectContext

    def __init__(
        self,
        type_default: SymbolType,
        workspace_root: WorkspaceRoot,
        workspace_context: WorkspaceContext,
        project_context: ProjectContext,
    ):
        self.type_default = type_default
        self.workspace_root = workspace_root
        self.workspace_context = workspace_context
        self.project_context = project_context


class SymbolDefaultResolver:
    def get_paths(
        self,
        context: SymbolDefaultConfigContext,
    ) -> Result[tuple[FullPath, ...], ConfigError]:
        paths: list[FullPath] = []
        type_default = context.type_default
        workspace_context = context.workspace_context
        project_context = context.project_context
        workspace_root = context.workspace_root
        paths.append(
            _get_config_path(context.project_context.project_root)
            / "$Package.default.json"
        )

        if isinstance(type_default, SymbolType):
            model_kind_result = _get_model_kind(
                type_default.symbol, type_default.context.analysis, workspace_context
            )
            if isinstance(model_kind_result, Failure):
                return model_kind_result.alt(
                    lambda e: ConfigError(
                        "Failed to determine model kind",
                        source="json",
                        phase="path-resolve",
                        details={"symbol": type_default.symbol.identity},
                    ).chain(e)
                )

            model_kind = model_kind_result.unwrap()
            if model_kind is not None:
                return Success(tuple())
            if not is_file_in_project(
                file_context=type_default.context, project_context=project_context
            ):
                workspace_project_result = find_workspace_project(
                    file_context=type_default.context,
                    workspace_root=workspace_root,
                    workspace_context=workspace_context,
                )
                if isinstance(workspace_project_result, Failure):
                    return workspace_project_result.alt(
                        lambda e: ConfigError(
                            "Failed to find workspace project for type default",
                            source="json",
                            phase="path-resolve",
                            details={"symbol": type_default.symbol.identity},
                        ).chain(e)
                    )

                paths.append(
                    _get_config_path(
                        workspace_root.path / workspace_project_result.unwrap().path
                    )
                    / "$Package.default.json"
                )

        if workspace_root.kind == WorkspaceRootKind.UV_WORKSPACE:
            paths.append(
                _get_config_path(workspace_root.path) / "$Workspace.default.json"
            )

        return Success(tuple(paths))

    def extract(
        self, config: PackageModelDefaults, context: SymbolDefaultConfigContext
    ) -> Result[ModelDefault | None, ConfigError]:
        type_default = context.type_default
        symbol = type_default.symbol
        model_defaults = config.models_per_module_path.get(
            type_default.context.analysis.module_name
        )
        if model_defaults is None:
            return Success(None)

        return Success(
            next(
                (
                    model
                    for model in model_defaults.models
                    if model.symbol_name == symbol.name
                ),
                None,
            )
        )


class PrimitiveDefaultResolver:
    def get_paths(
        self,
        context: PrimitiveDefaultConfigContext,
    ) -> Result[tuple[FullPath, ...], ConfigError]:
        paths: list[FullPath] = []
        workspace_root = context.workspace_root
        paths.append(
            _get_config_path(context.project_context.project_root)
            / "$Package.default.json"
        )

        if workspace_root.kind == WorkspaceRootKind.UV_WORKSPACE:
            paths.append(
                _get_config_path(workspace_root.path) / "$Workspace.default.json"
            )

        return Success(tuple(paths))

    def extract(
        self, config: PackageModelDefaults, context: PrimitiveDefaultConfigContext
    ) -> Result[PrimitiveDefault | None, ConfigError]:
        type_default = context.type_default

        if isinstance(type_default, PrimitiveType):
            return Success(
                next(
                    (
                        primitive
                        for primitive in config.primitives
                        if primitive.variable_name == type_default.parameter_name
                        and primitive.type_name == type_default.primitive_type
                    ),
                    None,
                )
            )
        else:
            return Success(
                next(
                    (
                        primitive
                        for primitive in config.primitives
                        if primitive.variable_name == type_default.parameter_name
                        and primitive.type_name == type(type_default.value).__name__
                    ),
                    None,
                )
            )
