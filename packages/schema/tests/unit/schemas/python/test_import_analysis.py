import pytest
from gyomu_schema.schemas.python.import_analysis import ImportAnalysis, ImportKind
from gyomu_schema.schemas.python.types import PythonPath, SymbolId
from gyomu_schema.utility.serialization import _assert_json_round_trip

from packages.schema.test_support.helpers import create_import_analysis


class TestImportAnalysis:
    def test(self) -> None:
        _assert_json_round_trip(
            ImportAnalysis,
            create_import_analysis(
                local_name="loc1",
                imported_name="ABC",
                kind=ImportKind.SYMBOL,
            ),
        )

    @pytest.mark.parametrize(
        ("kind", "imported_name", "expected"),
        [
            (ImportKind.MODULE, "pydantic", PythonPath("pydantic")),
            (
                ImportKind.MODULE,
                "project_a.models",
                PythonPath("project_a.models"),
            ),
            (
                ImportKind.SYMBOL,
                "pydantic.BaseModel",
                PythonPath("pydantic"),
            ),
            (
                ImportKind.SYMBOL,
                "project_a.models.User",
                PythonPath("project_a.models"),
            ),
            (ImportKind.SYMBOL, "BaseModel", PythonPath("")),
        ],
    )
    def test_get_module_path(
        self,
        kind: ImportKind,
        imported_name: str,
        expected: PythonPath,
    ) -> None:
        analysis = create_import_analysis(
            local_name="local",
            imported_name=imported_name,
            kind=kind,
        )

        assert analysis.get_module_path() == expected

    @pytest.mark.parametrize(
        ("kind", "imported_name", "expected"),
        [
            (ImportKind.MODULE, "pydantic", None),
            (ImportKind.MODULE, "pydantic.BaseModel", None),
            (
                ImportKind.SYMBOL,
                "pydantic.BaseModel",
                SymbolId("pydantic::BaseModel"),
            ),
            (
                ImportKind.SYMBOL,
                "project_a.models.User",
                SymbolId("project_a.models::User"),
            ),
            (ImportKind.SYMBOL, "BaseModel", None),
        ],
    )
    def test_get_symbol_id(
        self,
        kind: ImportKind,
        imported_name: str,
        expected: SymbolId | None,
    ) -> None:
        analysis = create_import_analysis(
            local_name="local",
            imported_name=imported_name,
            kind=kind,
        )

        assert analysis.get_symbol_id() == expected
