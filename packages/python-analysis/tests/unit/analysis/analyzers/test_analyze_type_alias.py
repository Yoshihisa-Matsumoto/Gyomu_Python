from gyomu_schema.schemas.python.symbol_base import DeclarationKind
from gyomu_schema.schemas.python.type.structure import (
    NameStructureAnalysis,
)
from gyomu_schema.schemas.python.type.type_analysis import (
    ArrayStructureAnalysis,
    LiteralStructureAnalysis,
    UnionStructureAnalysis,
)
from gyomu_schema.schemas.python.type_alias import TypeAliasAnalysis
from gyomu_schema.schemas.python.types import (
    DeclarationId,
    PythonPath,
    SymbolId,
)
from python_analysis_test_support.helpers import AnalysisTestBase


class TestAnalyzeTypeAlias(AnalysisTestBase):
    def _analyze_typealias(self, name: str) -> TypeAliasAnalysis:
        return self._analyze_typealias_bases(
            PythonPath("analysis.symbol.type_alias"), name
        )

    def test_analyzes_userid(self) -> None:
        result = self._analyze_typealias(
            "UserId",
        )

        assert result.kind == DeclarationKind.TYPEALIAS
        assert result.name == "UserId"

        assert result.docstring is None
        assert result.decorators == ()
        assert result.dependencies == ()

        assert result.alias_type is not None
        assert result.alias_type.structure
        assert isinstance(result.alias_type.structure, NameStructureAnalysis)
        assert result.alias_type.structure.name == "int"

        assert result.identity.symbol_id == SymbolId(
            "analysis.symbol.type_alias::UserId"
        )
        assert result.identity.declaration_id == DeclarationId(".")

    def test_analyzes_userlist(self) -> None:
        result = self._analyze_typealias(
            "UserList",
        )

        assert result.kind == DeclarationKind.TYPEALIAS
        assert result.name == "UserList"

        assert result.docstring is None
        assert result.decorators == ()
        assert result.dependencies == ()

        assert result.alias_type is not None
        assert result.alias_type.structure
        assert isinstance(result.alias_type.structure, ArrayStructureAnalysis)
        assert isinstance(result.alias_type.structure.element, NameStructureAnalysis)
        assert result.alias_type.structure.element.name == "UserId"

    def test_analyzes_uservalue(self) -> None:
        result = self._analyze_typealias(
            "UserValue",
        )

        assert result.kind == DeclarationKind.TYPEALIAS
        assert result.name == "UserValue"

        assert result.docstring is None
        assert result.decorators == ()
        assert result.dependencies == ()

        assert result.alias_type is not None
        assert result.alias_type.structure
        assert isinstance(result.alias_type.structure, UnionStructureAnalysis)

    def test_analyzes_status(self) -> None:
        result = self._analyze_typealias(
            "Status",
        )

        assert result.kind == DeclarationKind.TYPEALIAS
        assert result.name == "Status"

        assert result.docstring is None
        assert result.decorators == ()
        assert result.dependencies == ()

        assert result.alias_type is not None
        assert result.alias_type.structure
        assert isinstance(result.alias_type.structure, LiteralStructureAnalysis)
