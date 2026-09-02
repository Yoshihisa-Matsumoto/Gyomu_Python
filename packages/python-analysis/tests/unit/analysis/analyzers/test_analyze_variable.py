from griffe import Attribute
from gyomu_python_analysis.analysis.analyzers.variables import analyze_variable
from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.symbol_base import SymbolKind
from gyomu_schema.schemas.python.types import PythonPath
from gyomu_schema.schemas.python.variable import VariableAnalysis
from gyomu_schema.schemas.python.visibility import Visibility

from tests.helpers import AnalysisTestBase


class TestAnalyzeVariable(AnalysisTestBase):
    def _analyze_variable(self, name: str) -> VariableAnalysis:
        context = self._read_module_fixture(PythonPath("analysis.symbol.variable"))
        module = context.source.module
        variable = module[name]

        assert isinstance(variable, Attribute)

        source_full_path = (
            context.project.project_root
            / context.project.source_root
            / context.source.path
        )
        source_lines = source_full_path.read_text(
            encoding="utf-8",
        ).splitlines()
        result = analyze_variable(
            variable=variable,
            name=name,
            source_lines=source_lines,
        )
        return result

    # def _create_variable(
    #     self,
    #     name: str,
    # ) -> tuple[ProjectContext, SourceFileContext, Attribute]:
    #     context = self._read_module_fixture(
    #         PythonPath("analysis.symbol.variable"),
    #     )
    #     module = context.source.module
    #     variable = module.members[name]

    #     assert isinstance(variable, Attribute)

    #     return (
    #         context.project,
    #         context.source,
    #         variable,
    #     )

    def test_analyzes_public_variable(self) -> None:
        result = self._analyze_variable(
            "VERSION",
        )

        assert result == VariableAnalysis(
            kind=SymbolKind.VARIABLE,
            name="VERSION",
            docstring=None,
            decorators=tuple(),
            dependencies=[],
            type=None,
            value_source="5",
            location=SourceLocation(
                start_line=1,
                start_column=0,
                end_line=1,
                end_column=11,
            ),
            visibility=Visibility.PUBLIC,
            indent=0,
        )

        result = self._analyze_variable(
            "VERSION_STR",
        )

    def test_analyzes_private_variable(self) -> None:
        result = self._analyze_variable(
            "_internal_value",
        )

        assert result.visibility == Visibility.PRIVATE
        assert result.kind == SymbolKind.VARIABLE
        assert result.name == "_internal_value"
        assert result.value_source == "10"

    def test_analyzes_variable_without_value(self) -> None:
        result = self._analyze_variable(
            "ANNOTATED",
        )

        assert result.kind == SymbolKind.VARIABLE
        assert result.name == "ANNOTATED"
        assert result.visibility == Visibility.PUBLIC
        assert result.type is None
        assert result.value_source is None

    def test_analyzes_variable_expression(self) -> None:
        result = self._analyze_variable(
            "Calculated",
        )

        assert result.kind == SymbolKind.VARIABLE
        assert result.name == "Calculated"
        assert result.visibility == Visibility.PUBLIC
        assert result.type is None
        assert result.value_source == "2 + 3"
