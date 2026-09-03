import pytest
from griffe import Attribute
from gyomu_python_analysis.analysis.analyzers.variables import analyze_variable
from gyomu_schema.schemas.python.types import PythonPath
from gyomu_schema.schemas.python.variable import VariableAnalysis

from tests.helpers import AnalysisTestBase


class TestAnalyzeType(AnalysisTestBase):
    def _analyze_variable(self, name: str) -> VariableAnalysis:
        context = self._read_module_fixture(PythonPath("analysis.symbol.types"))
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

    def _analyze_callable(self, name: str) -> VariableAnalysis:
        context = self._read_module_fixture(PythonPath("analysis.symbol.callable"))
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

    def test_analyzes_variable_with_type_annotation(self) -> None:
        result = self._analyze_variable(
            "value_int",
        )

        # assert result.type is not None
        # assert result.type.text == "int"

        result = self._analyze_variable(
            "value_str",
        )

        result = self._analyze_variable(
            "value_none",
        )
        result = self._analyze_variable(
            "value_custom",
        )
        result = self._analyze_variable(
            "value_list",
        )
        result = self._analyze_variable(
            "value_union",
        )
        result = self._analyze_variable(
            "value_dict",
        )
        result = self._analyze_variable(
            "value_tuple",
        )
        result = self._analyze_variable(
            "value_literal_int",
        )
        result = self._analyze_variable(
            "value_literal_int2",
        )
        result = self._analyze_variable(
            "value_literal_str",
        )
        result = self._analyze_variable(
            "value_literal_str2",
        )
        result = self._analyze_variable(
            "value_literal_bool",
        )
        result = self._analyze_variable(
            "value_literal_bool2",
        )
        result = self._analyze_variable(
            "value_callable",
        )
        result = self._analyze_variable(
            "value_callable2",
        )

    @pytest.mark.parametrize(
        ("name"),
        [
            ("value_callable_1"),
            ("value_callable_2"),
            ("value_callable_3"),
            ("value_callable_4"),
            ("value_callable_5"),
            ("value_callable_6"),
            ("value_callable_7"),
            ("value_callable_8"),
            ("value_callable_9"),
            ("value_callable_10"),
            ("value_callable_11"),
            ("value_callable_12"),
            ("value_callable_13"),
            ("value_callable_14"),
            ("value_callable_15"),
        ],
    )
    def test_analyzes_variable_with_callable(
        self,
        name: str,
    ) -> None:
        self._analyze_callable(name)
