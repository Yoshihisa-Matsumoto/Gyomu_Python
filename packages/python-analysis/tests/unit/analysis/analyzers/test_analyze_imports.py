from gyomu_python_analysis.analysis.extract.symbols import _extract_imports
from gyomu_schema.schemas.python.import_analysis import ImportAnalysis
from gyomu_schema.schemas.python.types import PythonPath

from tests.helpers import AnalysisTestBase


class TestAnalizeImport(AnalysisTestBase):
    def test_analyzes_imports(self) -> None:
        context = self._read_module_fixture(PythonPath("analysis.import.imports"))
        source = context.source.module
        print("name:", source.name)
        print("path:", source.path)
        print("parent:", source.parent)
        print("package:", source.package)
        result = _extract_imports(source)
        print(result)
        assert result == [
            ImportAnalysis(
                local_name="pathlib",
                imported_name="pathlib",
            ),
            ImportAnalysis(
                local_name="path",
                imported_name="pathlib",
            ),
            ImportAnalysis(
                local_name="BaseModel",
                imported_name="pydantic.BaseModel",
            ),
            ImportAnalysis(
                local_name="fld",
                imported_name="pydantic.Field",
            ),
            ImportAnalysis(
                local_name="fld2",
                imported_name="pydantic.Field",
            ),
            ImportAnalysis(
                local_name="rel1",
                imported_name="analysis.import.relative.Field",
            ),
            ImportAnalysis(
                local_name="Value",
                imported_name="analysis.shared.Value",
            ),
            ImportAnalysis(
                local_name="VAR1",
                imported_name="analysis.import.all.VAR1",
            ),
        ]
