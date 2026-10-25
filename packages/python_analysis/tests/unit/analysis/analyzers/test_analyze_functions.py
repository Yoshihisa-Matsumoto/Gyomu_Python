from gyomu_schema.schemas.python.function_analysis import FunctionAnalysis
from gyomu_schema.schemas.python.parameter import ParameterAnalysis, ParameterKind
from gyomu_schema.schemas.python.symbol_base import DeclarationKind
from gyomu_schema.schemas.python.type.expression import (
    CallExpressionAnalysis,
    NameExpressionAnalysis,
)
from gyomu_schema.schemas.python.type.structure import LiteralValue
from gyomu_schema.schemas.python.types import PythonPath
from gyomu_schema.schemas.python.visibility import Visibility
from gyomu_schema.utility.fromatting import format_object
from test_support.helpers import AnalysisTestBase


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
            (
                p.name,
                p.kind,
                p.default
                if p.default is None
                else p.default.value
                if isinstance(p.default, LiteralValue)
                else "Unsupported",
                p.type.text if p.type else None,
            )
            for p in result.parameters
        ] == [
            ("name", ParameterKind.POSITIONAL_OR_KEYWORD, None, "str"),
            ("count", ParameterKind.POSITIONAL_OR_KEYWORD, 1, "int"),
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

    def test_analyzes_function_ellipse(self) -> None:
        result = self._analyze_function(
            name="abstract",
        )
        assert result.kind == DeclarationKind.FUNCTION
        assert result.name == "abstract"
        assert result.visibility == Visibility.PUBLIC
        assert result.is_ellipsis_only

    def test_default(self) -> None:
        result = self._analyze_function(name="build_default_user")
        assert result.kind == DeclarationKind.FUNCTION
        assert result.name == "build_default_user"
        assert len(result.parameters) == 1
        parameter = result.parameters[0]
        assert parameter.default is not None
        print(format_object(parameter.default, depth=6))
        func = parameter.default
        assert isinstance(func, CallExpressionAnalysis)
        assert isinstance(func.func, NameExpressionAnalysis)
        assert func.func.name == "create_user"
        assert len(func.keywords) == 1
        arg = func.keywords[0]
        assert arg.arg == "id"
        assert isinstance(arg.value, LiteralValue)
        assert arg.value.value == "345D"

    def test_default_parameter(self) -> None:
        result = self._analyze_function(name="build_default_parameter")
        assert result.kind == DeclarationKind.FUNCTION
        assert result.name == "build_default_parameter"
        assert len(result.parameters) == 2
        print(format_object(result.parameters, depth=6))
