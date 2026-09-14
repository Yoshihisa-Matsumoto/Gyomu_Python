from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.symbol_base import DeclarationKind
from gyomu_schema.schemas.python.type.structure import (
    LiteralValue,
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
from python_analysis_test_support.helpers import AnalysisTestBase


class TestAnalyzeVariable(AnalysisTestBase):
    def _analyze_variable(self, name: str) -> VariableAnalysis:
        return self._analyze_variable_base(PythonPath("analysis.symbol.variable"), name)

    def test_analyzes_public_variable(self) -> None:
        result = self._analyze_variable(
            "VERSION",
        )

        assert result == VariableAnalysis(
            kind=DeclarationKind.VARIABLE,
            name="VERSION",
            docstring=None,
            decorators=tuple(),
            dependencies=tuple(),
            type=None,
            value_source="5",
            location=SourceLocation(
                start_line=6,
                start_column=0,
                end_line=6,
                end_column=11,
                start_offset=59,
                end_offset=70,
            ),
            visibility=Visibility.PUBLIC,
            indent=0,
            identity=DeclarationIdentity(
                symbol_id=SymbolId("analysis.symbol.variable::VERSION"),
                declaration_id=DeclarationId("."),
            ),
            value_expression=LiteralValue(value=5),
            pydantic=None,
        )

        result = self._analyze_variable(
            "VERSION_STR",
        )

    def test_analyzes_private_variable(self) -> None:
        result = self._analyze_variable(
            "_internal_value",
        )

        assert result.visibility == Visibility.PRIVATE
        assert result.kind == DeclarationKind.VARIABLE
        assert result.name == "_internal_value"
        assert result.value_source == "10"

    def test_analyzes_variable_without_value(self) -> None:
        result = self._analyze_variable(
            "ANNOTATED",
        )

        assert result.kind == DeclarationKind.VARIABLE
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

        assert result.kind == DeclarationKind.VARIABLE
        assert result.name == "Calculated"
        assert result.visibility == Visibility.PUBLIC
        assert result.type is None
        assert result.value_source == "2 + 3"

    def test_analyzes_variable_pydantic(self) -> None:
        result = self._analyze_variable(
            "Confidence",
        )

        assert result.kind == DeclarationKind.VARIABLE
        assert result.name == "Confidence"
        assert result.visibility == Visibility.PUBLIC
        assert result.value_expression is not None
        assert result.pydantic is not None
        assert result.pydantic.description
        assert "AI decision" in result.pydantic.description
        assert result.pydantic.required

    def test_analyzes_variable_pydantic2(self) -> None:
        result = self._analyze_variable(
            "Confidence2",
        )

        assert result.kind == DeclarationKind.VARIABLE
        assert result.name == "Confidence2"
        assert result.visibility == Visibility.PUBLIC
        assert result.value_expression is not None
        assert result.pydantic is not None
        assert result.pydantic.description
        assert "AI decision" in result.pydantic.description
        assert result.pydantic.required
