from gyomu_schema.schemas.python.dependency import (
    DependencyAnalysis,
    DependencySummary,
    ImportedSymbolDependency,
    LocalFileDependency,
)
from gyomu_schema.schemas.python.types import SymbolId
from gyomu_schema.utility.serialization import _assert_json_round_trip

from packages.schema.schema_test_support.helpers import create_declaration_identity


class TestLocalFileDependency:
    def test(self) -> None:
        _assert_json_round_trip(
            LocalFileDependency,
            LocalFileDependency(symbol_id=SymbolId("A1")),
        )


class TestImportedSymbolDependency:
    def test(self) -> None:
        _assert_json_round_trip(
            ImportedSymbolDependency,
            ImportedSymbolDependency(symbol_id=SymbolId("A1")),
        )


class TestDependencyAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            DependencyAnalysis,
            DependencyAnalysis(
                source=create_declaration_identity("id1"),
                target=ImportedSymbolDependency(symbol_id=SymbolId("A1")),
            ),
        )


class TestDependencySummary:
    def test(self) -> None:
        _assert_json_round_trip(
            DependencySummary,
            DependencySummary(
                target=ImportedSymbolDependency(symbol_id=SymbolId("A1")),
            ),
        )
