from dataclasses import dataclass
from enum import Enum

from gyomu_schema.schemas.config.test.model_defaults import Parameter
from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.type.type_analysis import TypeAnalysis
from gyomu_schema.schemas.python.types import DeclarationIdentity, ProjectRelativePath


@dataclass(frozen=True)
class ParameterInfo:
    name: str
    parameter_type: TypeAnalysis
    default: Parameter | None


class TargetClassKind(Enum):
    DATACLASS = "dataclass"
    PYDANTIC_MODEL = "pydantic_model"
    GYOMU_ERROR = "gyomu_error"


@dataclass(frozen=True)
class HelperInventoryItem:
    target_identity: DeclarationIdentity
    function_name: str
    parameters: tuple[ParameterInfo, ...]


@dataclass(frozen=True)
class ExpectedHelperInventoryItem(HelperInventoryItem):
    kind: TargetClassKind


@dataclass(frozen=True)
class ExistingHelperInventoryItem(HelperInventoryItem):
    location: SourceLocation


@dataclass(frozen=True)
class HelperUpdate:
    file_path: ProjectRelativePath
    expected: HelperInventoryItem
    existing: HelperInventoryItem


@dataclass(frozen=True)
class HelperFileInventory:
    file_path: ProjectRelativePath
    items: tuple[ExistingHelperInventoryItem, ...]
    source_lines: tuple[str, ...]


@dataclass(frozen=True)
class HelperReconcileResult:
    create: tuple[HelperInventoryItem, ...]
    update: tuple[HelperUpdate, ...]
    unchanged: tuple[ExistingHelperInventoryItem, ...]
    delete_candidates: tuple[ExistingHelperInventoryItem, ...]
