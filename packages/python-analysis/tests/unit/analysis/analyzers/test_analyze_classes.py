from gyomu_schema.schemas.python.class_analysis import ClassAnalysis
from gyomu_schema.schemas.python.member_analysis import MemberKind
from gyomu_schema.schemas.python.parameter import ParameterKind
from gyomu_schema.schemas.python.symbol_base import SymbolKind
from gyomu_schema.schemas.python.type.structure import (
    NameStructureAnalysis,
    NoneStructureAnalysis,
    TypeStructureKind,
)
from gyomu_schema.schemas.python.types import PythonPath

from tests.helpers import AnalysisTestBase


class TestAnalyzeClass(AnalysisTestBase):
    def _analyze_file(self, file_name: str, class_name: str) -> ClassAnalysis:
        return self._analyze_class_base(
            PythonPath(f"analysis.symbol.{file_name}"), class_name
        )

    def _analyze_class(self, class_name: str) -> ClassAnalysis:
        return self._analyze_class_base(
            PythonPath("analysis.symbol.classes"), class_name
        )

    def test_analyzes_class_simple(self) -> None:
        result = self._analyze_class("Simple")

        assert result.name == "Simple"
        assert result.kind == SymbolKind.CLASS
        assert result.visibility.value == "public"

        # class Simple starts at column 0
        assert result.location.start_line == 6
        assert result.location.start_column == 0

        assert result.bases == ()

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
        print(init_method)
        assert init_method.name == "__init__"
        assert init_method.kind == MemberKind.METHOD
        assert init_method.is_async is False
        assert init_method.return_type
        assert isinstance(init_method.return_type.structure, NoneStructureAnalysis)
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
        print(get_name)
        assert get_name.name == "get_name"
        assert get_name.is_async is False
        assert get_name.return_type
        assert get_name.return_type.text == "str"

        assert [param.name for param in get_name.parameters] == ["self"]

    def test_analyzes_class_noinit(self) -> None:
        result = self._analyze_class("NoInit")

        assert result.name == "NoInit"
        assert result.location.start_line == 22
        assert result.location.start_column == 0

        # Identity
        assert result.identity.symbol_id.endswith("::NoInit")
        assert result.identity.declaration_id == "."

        assert result.methods == ()
        assert result.inner_classes == ()

        assert len(result.variables) == 1

        variable = result.variables[0]

        assert variable.name == "value"
        assert variable.kind == MemberKind.VARIABLE

        # Identity
        assert variable.identity.symbol_id == result.identity.symbol_id
        assert variable.identity.declaration_id == ".::value"

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

        # Identity
        assert result.identity.symbol_id.endswith("::Complex")
        assert result.identity.declaration_id == "."

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

        assert [method.identity.declaration_id for method in result.methods] == [
            ".::__init__",
            ".::from_value",
            ".::create",
        ]
        assert all(
            method.identity.symbol_id == result.identity.symbol_id
            for method in result.methods
        )

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
        assert result.identity.symbol_id.endswith("::Nested")
        assert result.identity.declaration_id == "."

        assert [variable.name for variable in result.variables] == [
            "parent_value",
        ]
        assert result.variables[0].location is None
        assert result.variables[0].identity.symbol_id == result.identity.symbol_id
        assert result.variables[0].identity.declaration_id == ".::parent_value"

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

        # Inner class
        assert inner.identity.symbol_id == result.identity.symbol_id
        assert inner.identity.declaration_id == ".::Inner"

        assert [variable.name for variable in inner.variables] == [
            "child_value",
        ]
        assert inner.variables[0].location is None

        assert inner.variables[0].identity.symbol_id == result.identity.symbol_id
        assert inner.variables[0].identity.declaration_id == ".::Inner::child_value"

        assert [method.name for method in inner.methods] == [
            "__init__",
        ]

        inner_init = inner.methods[0]

        assert inner_init.identity.symbol_id == result.identity.symbol_id
        assert inner_init.identity.declaration_id == ".::Inner::__init__"

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

        # InnerMost class
        assert inner_most.identity.symbol_id == result.identity.symbol_id
        assert inner_most.identity.declaration_id == ".::Inner::InnerMost"

        assert [variable.name for variable in inner_most.variables] == [
            "grandchild_value",
        ]
        assert inner_most.variables[0].location is None

        assert inner_most.variables[0].identity.symbol_id == result.identity.symbol_id
        assert inner_most.variables[0].identity.declaration_id == (
            ".::Inner::InnerMost::grandchild_value"
        )

        assert [method.name for method in inner_most.methods] == [
            "__init__",
        ]

        inner_most_init = inner_most.methods[0]
        assert inner_most_init.identity.symbol_id == result.identity.symbol_id
        assert (
            inner_most_init.identity.declaration_id == ".::Inner::InnerMost::__init__"
        )

        assert [param.name for param in inner_most_init.parameters] == [
            "self",
            "value",
        ]

    def test_analyzes_class_typealias(self) -> None:
        result = self._analyze_class("TypeAlias")

        assert result.name == "TypeAlias"

        assert len(result.type_aliases) == 2

        user_id = result.type_aliases[0]
        assert user_id.name == "UserId"
        assert user_id.alias_type
        assert user_id.alias_type.text == "int"

        user_list = result.type_aliases[1]
        assert user_list.name == "UserList"
        assert user_list.alias_type
        assert user_list.alias_type.text == "list[UserId]"
        assert user_list.alias_type.structure

    def test_analyzes_class_pydantic(self) -> None:
        result = self._analyze_file("pydantic", "User")
        assert result.name == "User"
        print(repr(result.bases))
        field = result.variables[0]
        assert field
        assert field.name == "id"
        print(repr(field))


class TypeAlias:
    type UserId = int
    type UserList = list[UserId]
