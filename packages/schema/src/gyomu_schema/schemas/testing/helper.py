from dataclasses import dataclass

from gyomu_schema.schemas.python.type.type_analysis import TypeAnalysis
from gyomu_schema.schemas.python.types import DeclarationIdentity, ProjectRelativePath


@dataclass(frozen=True)
class ParameterInfo:
    name: str
    parameter_type: TypeAnalysis


@dataclass(frozen=True)
class HelperInventoryItem:
    target_identity: DeclarationIdentity
    function_name: str
    parameters: tuple[ParameterInfo, ...]


@dataclass(frozen=True)
class HelperUpdate:
    expected: HelperInventoryItem
    existing: HelperInventoryItem


@dataclass(frozen=True)
class HelperFileInventory:
    file_path: ProjectRelativePath
    items: tuple[HelperInventoryItem, ...]


@dataclass(frozen=True)
class HelperReconcileResult:
    create: tuple[HelperInventoryItem, ...]
    update: tuple[HelperUpdate, ...]
    unchanged: tuple[HelperInventoryItem, ...]
    delete_candidates: tuple[HelperInventoryItem, ...]
