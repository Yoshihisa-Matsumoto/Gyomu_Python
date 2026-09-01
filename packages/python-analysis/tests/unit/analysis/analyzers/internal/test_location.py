from griffe import Alias
from gyomu_python_analysis.analysis.analyzers.internal.location import (
    calculate_symbol_location,
)
from gyomu_python_analysis.analysis.load import load_module
from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.types import PythonPath
from returns.result import Success

from tests.helpers import AnalysisTestBase


class TestCalculateSymbolLocation(AnalysisTestBase):
    def _calculate_symbol_location(self, symbol_name: str) -> SourceLocation:
        context = self._read_module_fixture(
            PythonPath("analysis.symbol.location"),
        )
        module = context.source.module

        result = load_module(
            context.project,
            PythonPath("analysis.symbol.location"),
        )
        assert isinstance(result, Success)
        source_full_path = (
            context.project.project_root
            / context.project.source_root
            / context.source.path
        )
        source_lines = source_full_path.read_text(
            encoding="utf-8",
        ).splitlines()

        symbol = module.members[symbol_name]
        assert not isinstance(symbol, Alias)

        location = calculate_symbol_location(
            symbol,
            source_lines,
        )

        return location

    def test_calculates_variable_location(self) -> None:

        location = self._calculate_symbol_location("VERSION")

        assert location == SourceLocation(
            start_line=1,
            start_column=0,
            end_line=1,
            end_column=11,
        )

    def test_calculates_private_variable_location(self) -> None:

        location = self._calculate_symbol_location("_internal_value")

        assert location == SourceLocation(
            start_line=3,
            start_column=0,
            end_line=3,
            end_column=20,
        )

    def test_calculates_function_location(self) -> None:

        location = self._calculate_symbol_location("public_function")

        assert location == SourceLocation(
            start_line=6,
            start_column=0,
            end_line=7,
            end_column=8,
        )

    def test_calculates_class_location(self) -> None:

        location = self._calculate_symbol_location("User")
        assert location == SourceLocation(
            start_line=10,
            start_column=0,
            end_line=13,
            end_column=11,
        )
