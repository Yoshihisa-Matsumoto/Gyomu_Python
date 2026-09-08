import pytest
from gyomu_python_analysis.analysis.analyzers.context import (
    DependencyInformation,
    initialize_symbol_context,
)
from gyomu_python_analysis.analysis.analyzers.dependency import (
    PYTHON_RESERVED_TYPE_NAMES,
    _find_imported,
    _find_symbol,
    _retrieve_imported_symbol_id,
    analyze_dependency,
    register_dependency,
    resolve_dependencies,
)
from gyomu_schema.schemas.python.dependency import (
    DependencyAnalysis,
    ImportedSymbolDependency,
    LocalFileDependency,
)
from gyomu_schema.schemas.python.import_analysis import ImportAnalysis, ImportKind
from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.symbol import SymbolAnalysis
from gyomu_schema.schemas.python.symbol_base import DeclarationKind
from gyomu_schema.schemas.python.types import (
    DeclarationId,
    DeclarationIdentity,
    PythonPath,
    SymbolId,
)
from gyomu_schema.schemas.python.variable import VariableAnalysis
from gyomu_schema.schemas.python.visibility import Visibility


def create_symbol(name: str, symbol_id: SymbolId | None = None) -> SymbolAnalysis:
    return VariableAnalysis(
        name=name,
        visibility=Visibility.PUBLIC,
        location=SourceLocation(
            start_line=1,
            end_line=1,
            start_column=1,
            end_column=1,
            start_offset=1,
            end_offset=1,
        ),
        identity=DeclarationIdentity(
            symbol_id=symbol_id if symbol_id else SymbolId("##test"),
            declaration_id=DeclarationId("**ABC##"),
        ),
        docstring=None,
        decorators=tuple(),
        dependencies=(),
        indent=0,
        kind=DeclarationKind.VARIABLE,
        type=None,
        value_source="",
    )


def test_registers_dependency() -> None:
    identity = DeclarationIdentity(
        symbol_id=SymbolId("test::User"),
        declaration_id=DeclarationId("test::User"),
    )
    context = initialize_symbol_context(PythonPath("test"), "User", [""])

    register_dependency(identity, "UserId", context)

    assert context.dependencies == [
        DependencyInformation(
            source=identity,
            target_name="UserId",
        )
    ]


@pytest.mark.parametrize(
    "name",
    sorted(PYTHON_RESERVED_TYPE_NAMES),
)
def test_does_not_register_reserved_type_name(name: str) -> None:
    identity = DeclarationIdentity(
        symbol_id=SymbolId("test::User"),
        declaration_id=DeclarationId("test::User"),
    )
    context = initialize_symbol_context(PythonPath("test"), "User", [""])

    register_dependency(identity, name, context)

    assert context.dependencies == []


def test_finds_imported_name() -> None:
    imported = [
        ImportAnalysis(
            local_name="UserId",
            imported_name="gyomu_schema.schemas.user.UserId",
            kind=ImportKind.SYMBOL,
        )
    ]

    result = _find_imported("UserId", imported)
    assert result
    assert result.imported_name == "gyomu_schema.schemas.user.UserId"


def test_returns_none_when_imported_name_not_found() -> None:
    imported = [
        ImportAnalysis(
            local_name="UserId",
            imported_name="gyomu_schema.schemas.user.UserId",
            kind=ImportKind.SYMBOL,
        )
    ]

    result = _find_imported("UserName", imported)

    assert result is None


@pytest.mark.parametrize(
    ("name", "kind", "expected"),
    [
        (
            "analysis.import.imports.VAR1",
            ImportKind.SYMBOL,
            "analysis.import.imports::VAR1",
        ),
        (
            "gyomu_schema.schemas.user.UserId",
            ImportKind.SYMBOL,
            "gyomu_schema.schemas.user::UserId",
        ),
        ("User", ImportKind.MODULE, "User"),
        ("pydantic.abc", ImportKind.MODULE, "pydantic.abc"),
    ],
)
def test_retrieves_imported_symbol_id(
    name: str,
    kind: ImportKind,
    expected: str | None,
) -> None:
    result = _retrieve_imported_symbol_id(
        ImportAnalysis(local_name="A BC", imported_name=name, kind=kind)
    )

    if expected is not None:
        assert result == SymbolId(expected)


def test_finds_symbol() -> None:
    user = create_symbol(name="User")
    user_id = create_symbol(name="UserId")

    result = _find_symbol("UserId", [user, user_id])

    assert result is user_id


def test_returns_none_when_symbol_not_found() -> None:
    user = create_symbol(name="User")

    result = _find_symbol("UserId", [user])

    assert result is None


def test_analyzes_imported_symbol_dependency() -> None:
    source = DeclarationIdentity(
        symbol_id=SymbolId("test::User"),
        declaration_id=DeclarationId("test::User"),
    )

    record = DependencyInformation(
        source=source,
        target_name="UserId",
    )

    imported = [
        ImportAnalysis(
            local_name="UserId",
            imported_name="gyomu_schema.schemas.user.UserId",
            kind=ImportKind.SYMBOL,
        )
    ]

    symbols = [
        create_symbol(name="UserId"),
    ]

    result = analyze_dependency(record, imported, symbols)

    assert result == DependencyAnalysis(
        source=source,
        target=ImportedSymbolDependency(
            symbol_id=SymbolId("gyomu_schema.schemas.user::UserId"),
        ),
    )


def test_analyzes_local_file_dependency() -> None:
    source = DeclarationIdentity(
        symbol_id=SymbolId("test::User"),
        declaration_id=DeclarationId("test::User"),
    )

    user_id = create_symbol(
        name="UserId",
        symbol_id=SymbolId("test::UserId"),
    )

    record = DependencyInformation(
        source=source,
        target_name="UserId",
    )

    result = analyze_dependency(
        record,
        imported=[],
        symbols=[user_id],
    )

    assert result == DependencyAnalysis(
        source=source,
        target=LocalFileDependency(
            symbol_id=SymbolId("test::UserId"),
        ),
    )


def test_returns_none_when_dependency_cannot_be_resolved() -> None:
    source = DeclarationIdentity(
        symbol_id=SymbolId("test::User"),
        declaration_id=DeclarationId("test::User"),
    )

    record = DependencyInformation(
        source=source,
        target_name="unknown",
    )

    result = analyze_dependency(
        record,
        imported=[],
        symbols=[],
    )

    assert result is None


def test_imported_symbol_id_uses_last_dot_as_symbol_separator() -> None:
    result = _retrieve_imported_symbol_id(
        ImportAnalysis(
            local_name="User", kind=ImportKind.SYMBOL, imported_name="foo.bar.baz.User"
        ),
    )

    assert result == SymbolId("foo.bar.baz::User")


def test_resolves_dependencies() -> None:
    user_id = DeclarationIdentity(
        symbol_id=SymbolId("test.user::User"),
        declaration_id=DeclarationId(".::User::id"),
    )
    get_name = DeclarationIdentity(
        symbol_id=SymbolId("test.user::User"),
        declaration_id=DeclarationId(".::User::get_name"),
    )

    user_id_type = create_symbol("user_id")
    user_name_type = create_symbol("user_name")
    dependencies = [
        DependencyInformation(
            source=user_id,
            target_name="UserId",
        ),
        DependencyInformation(
            source=get_name,
            target_name="UserId",
        ),
        DependencyInformation(
            source=get_name,
            target_name="UserName",
        ),
        DependencyInformation(
            source=get_name,
            target_name="Unknown",
        ),
    ]

    imported = [
        ImportAnalysis(
            local_name="UserId",
            imported_name="test.types.UserId",
            kind=ImportKind.SYMBOL,
        ),
        ImportAnalysis(
            local_name="UserName",
            imported_name="test.types.UserName",
            kind=ImportKind.SYMBOL,
        ),
    ]

    symbols = [
        user_id_type,
        user_name_type,
    ]

    result = resolve_dependencies(
        dependencies=dependencies,
        imported=imported,
        symbols=symbols,
    )

    assert result == {
        user_id: (
            DependencyAnalysis(
                source=user_id,
                target=ImportedSymbolDependency(
                    symbol_id=SymbolId("test.types::UserId"),
                ),
            ),
        ),
        get_name: (
            DependencyAnalysis(
                source=get_name,
                target=ImportedSymbolDependency(
                    symbol_id=SymbolId("test.types::UserId"),
                ),
            ),
            DependencyAnalysis(
                source=get_name,
                target=ImportedSymbolDependency(
                    symbol_id=SymbolId("test.types::UserName"),
                ),
            ),
        ),
    }
