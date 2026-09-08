from gyomu_schema.schemas.python.function_analysis import FunctionAnalysis
from gyomu_schema.schemas.python.parameter import ParameterAnalysis, ParameterKind
from gyomu_schema.schemas.python.symbol_base import DeclarationKind
from gyomu_schema.schemas.python.types import PythonPath
from gyomu_schema.schemas.python.visibility import Visibility

from tests.helpers import AnalysisTestBase


class TestAnalyzeFunctions(AnalysisTestBase):
    def _analyze_function(self, name: str) -> FunctionAnalysis:
        return self._analyze_function_base(
            PythonPath("analysis.symbol.functions"), name
        )

    def test_analyzes_function(self) -> None:

        result = self._analyze_function(
            name="greet",
        )

        assert result.kind == DeclarationKind.FUNCTION
        assert result.name == "greet"
        assert result.visibility == Visibility.PUBLIC

        # Identity
        assert result.identity.symbol_id == "analysis.symbol.functions::greet"
        assert result.identity.declaration_id == "."

        assert result.docstring is None
        assert result.decorators == ()
        assert result.dependencies == ()

        assert [
            (p.name, p.kind, p.default, p.type.text if p.type else None)
            for p in result.parameters
        ] == [
            ("name", ParameterKind.POSITIONAL_OR_KEYWORD, None, "str"),
            ("count", ParameterKind.POSITIONAL_OR_KEYWORD, None, "int"),
        ]

        assert result.is_async is False
        assert result.return_type.text if result.return_type else None == "str"

        function2 = self._analyze_function("test_async")
        assert function2.is_async is True

        # Identity
        assert function2.identity.symbol_id == "analysis.symbol.functions::test_async"
        assert function2.identity.declaration_id == "."

    def test_analyzes_function_parameter_kinds(self) -> None:

        result = self._analyze_function(
            name="parameters",
        )

        assert result.parameters == (
            ParameterAnalysis(
                name="positional_only",
                kind=ParameterKind.POSITIONAL_ONLY,
                type=None,
                default=None,
            ),
            ParameterAnalysis(
                name="positional_or_keyword",
                kind=ParameterKind.POSITIONAL_OR_KEYWORD,
                type=None,
                default=None,
            ),
            ParameterAnalysis(
                name="var_positional",
                kind=ParameterKind.VAR_POSITIONAL,
                type=None,
                default=None,
            ),
            ParameterAnalysis(
                name="keyword_only",
                kind=ParameterKind.KEYWORD_ONLY,
                type=None,
                default=None,
            ),
            ParameterAnalysis(
                name="var_keyword",
                kind=ParameterKind.VAR_KEYWORD,
                type=None,
                default=None,
            ),
        )
