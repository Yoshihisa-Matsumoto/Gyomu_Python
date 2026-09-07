from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.symbol_base import SymbolKind
from gyomu_schema.schemas.python.type.structure import (
    NameStructureAnalysis,
)
from gyomu_schema.schemas.python.type.type_analysis import (
    TypeAnalysis,
)
from gyomu_schema.schemas.python.types import (
    DeclarationId,
    DeclarationIdentity,
    PythonPath,
    SymbolId,
)
from gyomu_schema.schemas.python.variable import VariableAnalysis
from gyomu_schema.schemas.python.visibility import Visibility

from tests.helpers import AnalysisTestBase


class TestAnalyzeVariable(AnalysisTestBase):
    def _analyze_variable(self, name: str) -> VariableAnalysis:
        return self._analyze_variable_base(PythonPath("analysis.symbol.variable"), name)

    def test_analyzes_public_variable(self) -> None:
        result = self._analyze_variable(
            "VERSION",
        )

        assert result == VariableAnalysis(
            kind=SymbolKind.VARIABLE,
            name="VERSION",
            docstring=None,
            decorators=tuple(),
            dependencies=tuple(),
            type=None,
            value_source="5",
            location=SourceLocation(
                start_line=1,
                start_column=0,
                end_line=1,
                end_column=11,
                start_offset=0,
                end_offset=11,
            ),
            visibility=Visibility.PUBLIC,
            indent=0,
            identity=DeclarationIdentity(
                symbol_id=SymbolId("analysis.symbol.variable::VERSION"),
                declaration_id=DeclarationId("."),
            ),
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
        assert result.type == TypeAnalysis(
            text="int", structure=NameStructureAnalysis(name="int")
        )
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
