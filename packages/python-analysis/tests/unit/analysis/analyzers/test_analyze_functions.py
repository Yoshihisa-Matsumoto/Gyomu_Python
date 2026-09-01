from griffe import Function
from gyomu_python_analysis.analysis.analyzers.functions import analyze_function
from gyomu_schema.schemas.python.function_analysis import FunctionAnalysis
from gyomu_schema.schemas.python.parameter import ParameterAnalysis, ParameterKind
from gyomu_schema.schemas.python.symbol_base import SymbolKind
from gyomu_schema.schemas.python.types import PythonPath
from gyomu_schema.schemas.python.visibility import Visibility

from tests.helpers import AnalysisTestBase


class TestAnalyzeFunctions(AnalysisTestBase):
    def _analyze_function(self, name: str) -> FunctionAnalysis:
        context = self._read_module_fixture(PythonPath("analysis.symbol.functions"))
        module = context.source.module
        func = module[name]

        assert isinstance(func, Function)

        source_full_path = (
            context.project.project_root
            / context.project.source_root
            / context.source.path
        )
        source_lines = source_full_path.read_text(
            encoding="utf-8",
        ).splitlines()
        result = analyze_function(
            func=func,
            name=name,
            source_lines=source_lines,
        )
        return result

    def test_analyzes_function(self) -> None:

        result = self._analyze_function(
            name="greet",
        )

        assert result.kind == SymbolKind.FUNCTION
        assert result.name == "greet"
        assert result.visibility == Visibility.PUBLIC

        assert result.docstring is None
        assert result.decorators == ()
        assert result.dependencies == []

        assert result.parameters == (
            ParameterAnalysis(
                name="name",
                kind=ParameterKind.POSITIONAL_OR_KEYWORD,
                type=None,
                default=None,
            ),
            ParameterAnalysis(
                name="count",
                kind=ParameterKind.POSITIONAL_OR_KEYWORD,
                type=None,
                default=None,
            ),
        )

        assert result.is_async is False
        assert result.return_type == "str"

        function2 = self._analyze_function("test_async")
        assert function2.is_async is True

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
