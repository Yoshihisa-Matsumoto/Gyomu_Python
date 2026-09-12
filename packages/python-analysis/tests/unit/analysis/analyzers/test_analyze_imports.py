from pathlib import Path

from gyomu_python_analysis.analysis.extract.symbols import _extract_imports
from gyomu_schema.schemas.python.import_analysis import ImportAnalysis, ImportKind
from gyomu_schema.schemas.python.types import PythonPath
from python_analysis_test_support.helpers import AnalysisTestBase


class TestAnalizeImport(AnalysisTestBase):
    def test_analyzes_imports(self) -> None:
        context = self._read_module_fixture(PythonPath("analysis.import.imports"))
        source = context.source.module
        print("name:", source.name)
        print("path:", source.path)
        print("parent:", source.parent)
        print("package:", source.package)
        assert isinstance(source.filepath, Path)
        source_lines = source.filepath.read_text(encoding="utf-8").splitlines()
        result = _extract_imports(source, source_lines)
        print(result)
        assert result == [
            ImportAnalysis(
                local_name="pathlib", imported_name="pathlib", kind=ImportKind.MODULE
            ),
            ImportAnalysis(
                local_name="path", imported_name="pathlib", kind=ImportKind.MODULE
            ),
            ImportAnalysis(
                local_name="BaseModel",
                imported_name="pydantic.BaseModel",
                kind=ImportKind.SYMBOL,
            ),
            ImportAnalysis(
                local_name="fld", imported_name="pydantic.Field", kind=ImportKind.SYMBOL
            ),
            ImportAnalysis(
                local_name="fld2",
                imported_name="pydantic.Field",
                kind=ImportKind.SYMBOL,
            ),
            ImportAnalysis(
                local_name="rel1",
                imported_name="analysis.import.relative.Field",
                kind=ImportKind.SYMBOL,
            ),
            ImportAnalysis(
                local_name="Value",
                imported_name="analysis.shared.Value",
                kind=ImportKind.SYMBOL,
            ),
            ImportAnalysis(
                local_name="VAR1",
                imported_name="analysis.import.all.VAR1",
                kind=ImportKind.SYMBOL,
            ),
            ImportAnalysis(
                local_name="VAR11",
                imported_name="analysis.import.all2.VAR11",
                kind=ImportKind.SYMBOL,
            ),
            ImportAnalysis(
                local_name="VAR21",
                imported_name="analysis.import.all2.VAR21",
                kind=ImportKind.SYMBOL,
            ),
        ]
