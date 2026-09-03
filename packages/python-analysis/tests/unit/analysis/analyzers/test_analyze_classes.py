from griffe import Class
from gyomu_python_analysis.analysis.analyzers.cls import analyze_class
from gyomu_schema.schemas.python.class_analysis import ClassAnalysis
from gyomu_schema.schemas.python.member_analysis import MemberKind
from gyomu_schema.schemas.python.parameter import ParameterKind
from gyomu_schema.schemas.python.symbol_base import SymbolKind
from gyomu_schema.schemas.python.type.structure import (
    NameStructureAnalysis,
    TypeStructureKind,
)
from gyomu_schema.schemas.python.types import PythonPath

from tests.helpers import AnalysisTestBase


class TestAnalyzeClass(AnalysisTestBase):
    def _analyze_class(self, class_name: str) -> ClassAnalysis:
        context = self._read_module_fixture(PythonPath("analysis.symbol.classes"))
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

    def test_analyzes_class_simple(self) -> None:
        result = self._analyze_class("Simple")

        assert result.name == "Simple"
        assert result.kind == SymbolKind.CLASS
        assert result.visibility.value == "public"

        # class Simple starts at column 0
        assert result.location.start_line == 6
        assert result.location.start_column == 0

        assert result.bases == ()
        assert result.pydantic is None

        assert [method.name for method in result.methods] == [
            "__init__",
            "get_name",
        ]

        assert [variable.name for variable in result.variables] == [
            "name",
            "age",
            "position",
        ]

        assert result.inner_classes == ()

    def test_analyzes_class_simple_variables(self) -> None:
        result = self._analyze_class("Simple")

        assert len(result.variables) == 3

        variables = {variable.name: variable for variable in result.variables}

        name = variables["name"]
        assert name.kind == MemberKind.VARIABLE
        assert name.type is None
        assert name.value_source == "name"
        assert name.location is None

        age = variables["age"]
        assert age.kind == MemberKind.VARIABLE
        assert age.type is None
        assert age.value_source == "age"
        assert age.location is None

        position = variables["position"]
        assert position.kind == MemberKind.VARIABLE
        assert position.type
        assert position.type.text == "int"
        assert position.type.structure
        assert isinstance(position.type.structure, NameStructureAnalysis)
        assert position.type.structure.kind == TypeStructureKind.NAME
        assert position.type.structure.name == "int"
        assert position.value_source is None
        assert position.location is not None
        assert position.location.start_line == 16
        assert position.location.start_column == 4

    def test_analyzes_class_simple_methods(self) -> None:
        result = self._analyze_class("Simple")

        init_method = result.methods[0]

        assert init_method.name == "__init__"
        assert init_method.kind == MemberKind.METHOD
        assert init_method.is_async is False
        assert init_method.return_type is None

        assert [param.name for param in init_method.parameters] == [
            "self",
            "name",
            "age",
        ]

        assert [param.kind for param in init_method.parameters] == [
            ParameterKind.POSITIONAL_OR_KEYWORD,
            ParameterKind.POSITIONAL_OR_KEYWORD,
            ParameterKind.POSITIONAL_OR_KEYWORD,
        ]

        get_name = result.methods[1]

        assert get_name.name == "get_name"
        assert get_name.is_async is False
        assert get_name.return_type is None

        assert [param.name for param in get_name.parameters] == ["self"]

    def test_analyzes_class_noinit(self) -> None:
        result = self._analyze_class("NoInit")

        assert result.name == "NoInit"
        assert result.location.start_line == 22
        assert result.location.start_column == 0

        assert result.methods == ()
        assert result.inner_classes == ()

        assert len(result.variables) == 1

        variable = result.variables[0]

        assert variable.name == "value"
        assert variable.kind == MemberKind.VARIABLE
        assert variable.type
        assert variable.type.text == "int"
        assert variable.value_source == "10"

        assert variable.location is not None
        assert variable.location.start_line == 23
        assert variable.location.start_column == 4

    def test_analyzes_class_inherited(self) -> None:
        result = self._analyze_class("Inherited")

        assert result.name == "Inherited"
        assert result.methods == ()
        assert result.variables == ()
        assert result.inner_classes == ()

        # TypeAnalysis is not implemented yet.
        assert len(result.bases) == 1
        assert result.bases[0].text == "Base"

    def test_analyzes_class_complex(self) -> None:
        result = self._analyze_class("Complex")

        assert result.name == "Complex"

        assert [variable.name for variable in result.variables] == [
            "positional_only",
            "positional_or_keyword",
            "args",
            "keyword_only",
            "kwargs",
        ]

        assert all(variable.location is None for variable in result.variables)

        assert all(variable.type is None for variable in result.variables)

        assert result.inner_classes == ()

        assert [method.name for method in result.methods] == [
            "__init__",
            "from_value",
            "create",
        ]

        init_method = result.methods[0]

        assert [param.name for param in init_method.parameters] == [
            "self",
            "positional_only",
            "positional_or_keyword",
            "args",
            "keyword_only",
            "kwargs",
        ]

        assert [param.kind for param in init_method.parameters] == [
            ParameterKind.POSITIONAL_ONLY,
            ParameterKind.POSITIONAL_ONLY,
            ParameterKind.POSITIONAL_OR_KEYWORD,
            ParameterKind.VAR_POSITIONAL,
            ParameterKind.KEYWORD_ONLY,
            ParameterKind.VAR_KEYWORD,
        ]

        assert init_method.is_async is False

        from_value = result.methods[1]

        assert from_value.name == "from_value"
        assert [param.name for param in from_value.parameters] == [
            "cls",
            "value",
        ]
        assert from_value.is_async is False

        create = result.methods[2]

        assert create.name == "create"
        assert [param.name for param in create.parameters] == [
            "name",
        ]
        assert create.is_async is False

    def test_analyzes_class_nested(self) -> None:
        result = self._analyze_class("Nested")

        assert result.name == "Nested"

        assert [variable.name for variable in result.variables] == [
            "parent_value",
        ]
        assert result.variables[0].location is None

        assert [method.name for method in result.methods] == [
            "__init__",
        ]

        init_method = result.methods[0]

        assert [param.name for param in init_method.parameters] == [
            "self",
            "value",
        ]

        assert [param.kind for param in init_method.parameters] == [
            ParameterKind.POSITIONAL_OR_KEYWORD,
            ParameterKind.POSITIONAL_OR_KEYWORD,
        ]

        assert init_method.is_async is False

        assert [inner.name for inner in result.inner_classes] == [
            "Inner",
        ]

        inner = result.inner_classes[0]

        assert [variable.name for variable in inner.variables] == [
            "child_value",
        ]
        assert inner.variables[0].location is None

        assert [method.name for method in inner.methods] == [
            "__init__",
        ]

        inner_init = inner.methods[0]

        assert [param.name for param in inner_init.parameters] == [
            "self",
            "value",
        ]

        assert [param.kind for param in inner_init.parameters] == [
            ParameterKind.POSITIONAL_OR_KEYWORD,
            ParameterKind.POSITIONAL_OR_KEYWORD,
        ]

        assert inner_init.is_async is False

        assert [inner.name for inner in inner.inner_classes] == [
            "InnerMost",
        ]

        inner_most = inner.inner_classes[0]

        assert [variable.name for variable in inner_most.variables] == [
            "grandchild_value",
        ]
        assert inner_most.variables[0].location is None

        assert [method.name for method in inner_most.methods] == [
            "__init__",
        ]
