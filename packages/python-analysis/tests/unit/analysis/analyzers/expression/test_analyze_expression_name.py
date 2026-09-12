from gyomu_schema.schemas.python.class_analysis import ClassAnalysis
from gyomu_schema.schemas.python.type.structure import NameStructureAnalysis
from gyomu_schema.schemas.python.types import PythonPath
from gyomu_schema.schemas.python.variable import VariableAnalysis
from python_analysis_test_support.helpers import AnalysisTestBase


class TestAnalyzeType(AnalysisTestBase):
    def _analyze_class(self, class_name: str) -> ClassAnalysis:
        return self._analyze_class_base(
            file_name=PythonPath("analysis.types.name"), symbol_name=class_name
        )

    def _analyze_variable(self, name: str) -> VariableAnalysis:
        return self._analyze_variable_base(PythonPath("analysis.types.name"), name)

    def _check_name_analysis(self, variable: VariableAnalysis, expected_name: str):
        assert variable.type
        assert variable.type.structure
        assert isinstance(variable.type.structure, NameStructureAnalysis)
        assert variable.type.structure.name == expected_name

    def test_analyzes_variable_with_type_annotation(self) -> None:
        result = self._analyze_variable(
            "UserId",
        )
        self._check_name_analysis(result, "TypeAlias")

        result = self._analyze_variable(
            "value_builtin",
        )
        self._check_name_analysis(result, "int")

        result = self._analyze_variable(
            "value_custom",
        )
        self._check_name_analysis(result, "User")

        result = self._analyze_variable(
            "value_alias",
        )
        self._check_name_analysis(result, "T")

        result = self._analyze_variable(
            "value_type_alias",
        )
        self._check_name_analysis(result, "UserId")

        result = self._analyze_variable(
            "value_module",
        )
        self._check_name_analysis(result, "str")

        result = self._analyze_variable(
            "value_enum_class",
        )
        self._check_name_analysis(result, "Color")

        result = self._analyze_variable(
            "value_union",
        )

        result = self._analyze_class(
            "Box",
        )
        assert result.variables[0].name == "value"
        val = result.variables[0]
        assert val.type
        assert val.type.structure
        assert isinstance(val.type.structure, NameStructureAnalysis)
        assert val.type.structure.name == "U"
