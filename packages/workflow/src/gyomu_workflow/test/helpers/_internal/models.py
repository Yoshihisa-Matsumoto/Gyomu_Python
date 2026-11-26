from dataclasses import dataclass

from gyomu_config.manager import ConfigManager
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_python_analysis.resolve.models import (
    LiteralValueType,
    PackageType,
    PrimitiveType,
    SymbolType,
)
from gyomu_schema.schemas.python.types import DeclarationIdentity
from gyomu_schema.schemas.testing.helper import ParameterInfo
from gyomu_test.helper.defaults.requirements import (
    MissingParameterDefault,
)


@dataclass(frozen=True)
class DefaultTypeParameterContext:
    model_identity: DeclarationIdentity
    parameter: MissingParameterDefault
    workspace_context: WorkspaceContext
    project_context: ProjectContext
    config_manager: ConfigManager


@dataclass(frozen=True)
class DefaultPrimitiveLiteralTypeParameterContext(DefaultTypeParameterContext):
    resolved_type: PrimitiveType | LiteralValueType

    def parameter_type_name(self) -> str:

        if isinstance(self.resolved_type, PrimitiveType):
            return self.resolved_type.primitive_type

        value = self.resolved_type.value
        return type(value).__name__


@dataclass(frozen=True)
class DefaultBaseTypeConfigPlaceContext:
    parameter: ParameterInfo
    workspace_context: WorkspaceContext
    test_project_context: ProjectContext


@dataclass(frozen=True)
class DefaultPrimitiveLiteralTypeConfigPlaceContext(DefaultBaseTypeConfigPlaceContext):
    resolved_type: PrimitiveType | LiteralValueType


@dataclass(frozen=True)
class DefaultSymbolTypeConfigPlaceContext(DefaultBaseTypeConfigPlaceContext):
    resolved_type: SymbolType
    model_project_context: ProjectContext | None


@dataclass(frozen=True)
class DefaultPackageTypeConfigPlaceContext(DefaultBaseTypeConfigPlaceContext):
    resolved_type: PackageType
    model_project_context: ProjectContext | None


type DefaultTypeConfigPlaceContext = (
    DefaultPrimitiveLiteralTypeConfigPlaceContext
    | DefaultSymbolTypeConfigPlaceContext
    | DefaultPackageTypeConfigPlaceContext
)
