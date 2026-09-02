from griffe import Attribute, Class
from gyomu_python_analysis.analysis.analyzers.cls import analyze_class
from gyomu_python_analysis.analysis.analyzers.variables import analyze_variable
from gyomu_schema.schemas.python.class_analysis import ClassAnalysis
from gyomu_schema.schemas.python.type.structure import NameStructureAnalysis
from gyomu_schema.schemas.python.types import PythonPath
from gyomu_schema.schemas.python.variable import VariableAnalysis

from tests.helpers import AnalysisTestBase


class TestAnalyzeType(AnalysisTestBase):
    def _analyze_class(self, class_name: str) -> ClassAnalysis:
        context = self._read_module_fixture(PythonPath("analysis.types.name"))
        module = context.source.module
        cls = module[class_name]

        assert isinstance(cls, Class)

        source_full_path = (
            context.project.project_root
            / context.project.source_root
            / context.source.path
        )
        source_lines = source_full_path.read_text(
            encoding="utf-8",
        ).splitlines()
        result = analyze_class(
            cls=cls,
            name=class_name,
            source_lines=source_lines,
        )
        return result

    def _analyze_variable(self, name: str) -> VariableAnalysis:
        context = self._read_module_fixture(PythonPath("analysis.types.name"))
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
