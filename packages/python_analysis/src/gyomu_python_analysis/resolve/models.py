from dataclasses import dataclass
from typing import Literal

from gyomu_schema.schemas.python.class_analysis import ClassAnalysis
from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from gyomu_schema.schemas.python.import_analysis import ImportAnalysis
from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.symbol import SymbolAnalysis
from gyomu_schema.schemas.python.types import PythonPath, SymbolId


@dataclass(frozen=True)
class ResolvedReference:
    import_analysis: ImportAnalysis | None
    module_path: PythonPath
    symbol_id: SymbolId | None


@dataclass(frozen=True)
class ResolvedClass:
    symbol: ClassAnalysis
    module: ModuleAnalysis


type UnresolvedClassReason = Literal[
    "symbol-is-not-class",
    "symbol-not-found-in-module",
    "reference-not-resolved",
]


@dataclass(frozen=True)
class ExternalClass:
    reference: ResolvedReference


@dataclass(frozen=True)
class UnresolvedClass:
    reference_name: str
    reason: UnresolvedClassReason


type ClassResolution = ResolvedClass | UnresolvedClass | ExternalClass


@dataclass(frozen=True)
class ClassResolutionCollection:
    _collection: tuple[ClassResolution, ...]

    def all(self) -> tuple[ClassResolution, ...]:
        return self._collection

    def resolved(self) -> tuple[ResolvedClass, ...]:
        return tuple(
            item for item in self._collection if isinstance(item, ResolvedClass)
        )

    def unresolved(self) -> tuple[UnresolvedClass, ...]:
        return tuple(
            item for item in self._collection if isinstance(item, UnresolvedClass)
        )

    def external(self) -> tuple[ExternalClass, ...]:
        return tuple(
            item for item in self._collection if isinstance(item, ExternalClass)
        )


@dataclass(frozen=True)
class PrimitiveType:
    primitive_type: str
    parameter_name: str


@dataclass(frozen=True)
class SymbolType:
    symbol: SymbolAnalysis
    context: FileAnalysisContext


@dataclass(frozen=True)
class LiteralValueType:
    value: str | bytes | bool | int | float | complex | None
    parameter_name: str


type ResolvedType = PrimitiveType | SymbolType | LiteralValueType
