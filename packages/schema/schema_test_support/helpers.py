from pathlib import Path

from gyomu_schema.schemas.python.class_analysis import (
    ClassAnalysis,
    ClassTypeAliasAnalysis,
    ClassVariableAnalysis,
    InnerClassAnalysis,
)
from gyomu_schema.schemas.python.dependency import (
    DependencyAnalysis,
    ImportedSymbolDependency,
    LocalFileDependency,
)
from gyomu_schema.schemas.python.docstring import (
    DocstringAnalysis,
    DocstringCustomSection,
    DocstringExamplesSection,
    DocstringExamplesSectionItem,
    DocstringGyomuContextSection,
    DocstringNotesSection,
    DocstringParametersSection,
    DocstringParametersSectionItem,
    DocstringRaisesSection,
    DocstringRaisesSectionItem,
    DocstringReturnsSection,
    DocstringReturnsSectionItem,
    DocstringSection,
    DocstringStyle,
)
from gyomu_schema.schemas.python.file_analysis import (
    FileAnalysisContext,
    FileAnalysisMetadata,
)
from gyomu_schema.schemas.python.function_analysis import FunctionAnalysis
from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.method_analysis import MethodAnalysis
from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.pydantic import PydanticFieldAnalysis
from gyomu_schema.schemas.python.symbol import MemberAnalysis, SymbolAnalysis
from gyomu_schema.schemas.python.symbol_base import DeclarationKind
from gyomu_schema.schemas.python.type.structure import (
    LiteralValue,
    NameStructureAnalysis,
)
from gyomu_schema.schemas.python.type.type_analysis import TypeAnalysis, TypeExpression
from gyomu_schema.schemas.python.type_alias import TypeAliasAnalysis
from gyomu_schema.schemas.python.types import (
    DeclarationId,
    DeclarationIdentity,
    PythonPath,
    SourceRelativePath,
    SymbolId,
)
from gyomu_schema.schemas.python.variable import VariableAnalysis
from gyomu_schema.schemas.python.visibility import Visibility
from gyomu_schema.schemas.types import FullPath

FIXTURES_ROOT = FullPath(Path(__file__).parent / "fixtures")

print("LOADED DOCSTRING TESTS.HELPERS")


def create_declaration_identity(id: str) -> DeclarationIdentity:
    return DeclarationIdentity(
        symbol_id=SymbolId(id),
        declaration_id=DeclarationId("."),
    )


def create_location(
    start_offset: int = 0,
    end_offset: int = 0,
    start_line: int = 1,
    start_column: int = 0,
    end_line: int = 1,
    end_column: int = 0,
) -> SourceLocation:
    return SourceLocation(
        start_line=start_line,
        start_offset=start_offset,
        end_line=end_line,
        end_offset=end_offset,
        start_column=start_column,
        end_column=end_column,
    )


_default_identity = DeclarationIdentity(
    symbol_id=SymbolId("test.User"),
    declaration_id=DeclarationId("."),
)


def create_type_alias_analysis(
    indent: int,
    location: SourceLocation,
    name: str = "test_func",
    identity: DeclarationIdentity | None = None,
) -> TypeAliasAnalysis:
    if identity is None:
        identity = create_declaration_identity(name)
    return TypeAliasAnalysis(
        name=name,
        docstring=None,
        identity=identity,
        decorators=tuple(),
        dependencies=tuple(),
        indent=indent,
        kind=DeclarationKind.TYPEALIAS,
        visibility=Visibility.PUBLIC,
        location=location,
        alias_type=None,
    )


def create_class_type_alias_analysis(
    indent: int,
    location: SourceLocation,
    name: str = "test_func",
    identity: DeclarationIdentity | None = None,
) -> ClassTypeAliasAnalysis:
    if identity is None:
        identity = create_declaration_identity(name)
    return ClassTypeAliasAnalysis(
        name=name,
        docstring=None,
        identity=identity,
        decorators=tuple(),
        indent=indent,
        kind=DeclarationKind.TYPEALIAS,
        visibility=Visibility.PUBLIC,
        location=location,
        alias_type=None,
    )


def create_variable_analysis(
    indent: int,
    location: SourceLocation,
    name: str = "test_func",
    identity: DeclarationIdentity | None = None,
    type: TypeAnalysis | None = None,
    value_source: str | None = None,
    value_expression: TypeExpression | None = None,
    pydantic: PydanticFieldAnalysis | None = None,
) -> VariableAnalysis:
    if identity is None:
        identity = create_declaration_identity(name)
    return VariableAnalysis(
        name=name,
        docstring=None,
        identity=identity,
        decorators=tuple(),
        dependencies=tuple(),
        indent=indent,
        kind=DeclarationKind.VARIABLE,
        visibility=Visibility.PUBLIC,
        location=location,
        type=None,
        value_source=value_source,
        value_expression=value_expression,
        pydantic=pydantic,
    )


def create_class_variable_analysis(
    indent: int,
    location: SourceLocation,
    name: str = "test_func",
    identity: DeclarationIdentity | None = None,
) -> ClassVariableAnalysis:
    if identity is None:
        identity = create_declaration_identity(name)
    return ClassVariableAnalysis(
        name=name,
        docstring=None,
        identity=identity,
        decorators=tuple(),
        indent=indent,
        kind=DeclarationKind.VARIABLE,
        visibility=Visibility.PUBLIC,
        location=location,
        type=None,
        value_source=None,
        value_expression=None,
        pydantic=None,
    )


def create_function_analysis(
    indent: int,
    location: SourceLocation,
    name: str = "test_func",
    identity: DeclarationIdentity | None = None,
    docstring: DocstringAnalysis | None = None,
    dependencies: tuple[DependencyAnalysis, ...] = tuple(),
) -> FunctionAnalysis:
    if identity is None:
        identity = create_declaration_identity(name)
    return FunctionAnalysis(
        name=name,
        docstring=docstring,
        identity=identity,
        decorators=tuple(),
        dependencies=dependencies,
        indent=indent,
        is_async=False,
        kind=DeclarationKind.FUNCTION,
        parameters=tuple(),
        return_type=None,
        visibility=Visibility.PUBLIC,
        location=location,
    )


def create_method_analysis(
    indent: int | None,
    location: SourceLocation | None,
    name: str = "test_func",
    identity: DeclarationIdentity | None = None,
    docstring: DocstringAnalysis | None = None,
) -> MethodAnalysis:
    if identity is None:
        identity = create_declaration_identity(name)
    return MethodAnalysis(
        name=name,
        docstring=docstring,
        identity=identity,
        decorators=tuple(),
        indent=indent,
        is_async=False,
        kind=DeclarationKind.METHOD,
        parameters=tuple(),
        return_type=None,
        visibility=Visibility.PUBLIC,
        location=location,
    )


def create_class_analysis(
    indent: int,
    location: SourceLocation,
    name: str = "test_class",
    identity: DeclarationIdentity | None = None,
    methods: tuple[MethodAnalysis, ...] = tuple(),
    variables: tuple[ClassVariableAnalysis, ...] = tuple(),
    type_aliases: tuple[ClassTypeAliasAnalysis, ...] = tuple(),
    inner_classes: tuple[InnerClassAnalysis, ...] = tuple(),
) -> ClassAnalysis:
    if identity is None:
        identity = create_declaration_identity(name)
    return ClassAnalysis(
        name=name,
        docstring=None,
        identity=identity,
        decorators=tuple(),
        dependencies=tuple(),
        indent=indent,
        kind=DeclarationKind.CLASS,
        bases=tuple(),
        visibility=Visibility.PUBLIC,
        location=location,
        methods=methods,
        variables=variables,
        type_aliases=type_aliases,
        inner_classes=inner_classes,
    )


def create_inner_class_analysis(
    indent: int,
    location: SourceLocation,
    name: str = "test_class",
    identity: DeclarationIdentity | None = None,
    methods: tuple[MethodAnalysis, ...] = tuple(),
) -> InnerClassAnalysis:
    if identity is None:
        identity = create_declaration_identity(name)
    return InnerClassAnalysis(
        name=name,
        docstring=None,
        identity=identity,
        decorators=tuple(),
        indent=indent,
        kind=DeclarationKind.CLASS,
        bases=tuple(),
        visibility=Visibility.PUBLIC,
        location=location,
        methods=methods,
        variables=tuple(),
        type_aliases=tuple(),
        inner_classes=tuple(),
    )


def create_pydantic_field_analysis(
    default_source: str | None = None,
    description: str | None = None,
    alias: str | None = None,
    required: bool = True,
) -> PydanticFieldAnalysis:
    return PydanticFieldAnalysis(
        default_source=default_source,
        description=description,
        alias=alias,
        required=required,
    )


def create_literal_value(value: str | int | bool | float) -> LiteralValue:
    return LiteralValue(value=value)


def create_name_structure(name: str) -> NameStructureAnalysis:
    return NameStructureAnalysis(name=name)


def create_module_analysis(
    symbols: tuple[SymbolAnalysis, ...],
    name: str = "test",
    docstring: DocstringAnalysis | None = None,
) -> ModuleAnalysis:
    return ModuleAnalysis(
        path=SourceRelativePath(Path(".")),
        name=name,
        module_name=PythonPath(""),
        docstring=docstring,
        imports=tuple(),
        symbols=symbols,
    )


def create_file_analysis_context(
    symbol: SymbolAnalysis | MemberAnalysis | None = None,
    symbol2: SymbolAnalysis | MemberAnalysis | None = None,
    symbol3: SymbolAnalysis | MemberAnalysis | None = None,
) -> FileAnalysisContext:
    symbols: dict[DeclarationIdentity, SymbolAnalysis | MemberAnalysis]
    symbols = dict([(symbol.identity, symbol)]) if symbol else dict()
    analysis_symbols: list[SymbolAnalysis] = []
    if isinstance(
        symbol, VariableAnalysis | ClassAnalysis | FunctionAnalysis | TypeAliasAnalysis
    ):
        analysis_symbols.append(symbol)
    if symbol2:
        symbols[symbol2.identity] = symbol2
        if isinstance(
            symbol2,
            VariableAnalysis | ClassAnalysis | FunctionAnalysis | TypeAliasAnalysis,
        ):
            analysis_symbols.append(symbol2)
    if symbol3:
        symbols[symbol3.identity] = symbol3
        if isinstance(
            symbol3,
            VariableAnalysis | ClassAnalysis | FunctionAnalysis | TypeAliasAnalysis,
        ):
            analysis_symbols.append(symbol3)
    return FileAnalysisContext(
        metadata=FileAnalysisMetadata(parsed_docstring=dict(), symbols=symbols),
        analysis=ModuleAnalysis(
            path=SourceRelativePath(Path(".")),
            name="test",
            module_name=PythonPath(""),
            docstring=None,
            imports=tuple(),
            symbols=tuple(analysis_symbols),
        ),
    )


def create_docstring(
    summary: str | None = None,
    description: str | None = None,
    location: SourceLocation | None = None,
    sections: tuple[DocstringSection, ...] = tuple(),
) -> DocstringAnalysis:
    return DocstringAnalysis(
        raw="",
        summary=summary,
        description=description,
        location=location if location is not None else create_location(),
        style=DocstringStyle.GOOGLE,
        indent=0,
        sections=sections,
    )


def create_parameter_section(
    items: tuple[DocstringParametersSectionItem, ...],
) -> DocstringParametersSection:
    return DocstringParametersSection(items=items)


def create_parameter_section_item(
    name: str,
    description: str,
    type: str | None = None,
) -> DocstringParametersSectionItem:
    return DocstringParametersSectionItem(name=name, description=description, type=type)


def create_return_section(
    type: str | None, description: str
) -> DocstringReturnsSection:
    return DocstringReturnsSection(
        item=DocstringReturnsSectionItem(type=type, description=description)
    )


def create_raise_section(
    items: tuple[DocstringRaisesSectionItem, ...],
) -> DocstringRaisesSection:
    return DocstringRaisesSection(items=items)


def create_raise_section_item(
    type: str, description: str
) -> DocstringRaisesSectionItem:
    return DocstringRaisesSectionItem(type=type, description=description)


def create_example_section(values: tuple[str, ...]) -> DocstringExamplesSection:
    return DocstringExamplesSection(
        items=tuple([DocstringExamplesSectionItem(value=val) for val in values])
    )


def create_note_section(value: str) -> DocstringNotesSection:
    return DocstringNotesSection(value=value)


def create_gyomu_context_section(value: str) -> DocstringGyomuContextSection:
    return DocstringGyomuContextSection(value=value)


def create_custom_section(title: str, value: str) -> DocstringCustomSection:
    return DocstringCustomSection(title=title, value=value)


def create_import_dependency_analysis(id: str) -> DependencyAnalysis:
    return DependencyAnalysis(
        source=create_declaration_identity(id),
        target=ImportedSymbolDependency(symbol_id=SymbolId(id)),
    )


def create_local_dependency_analysis(id: str) -> DependencyAnalysis:
    return DependencyAnalysis(
        source=create_declaration_identity(id),
        target=LocalFileDependency(symbol_id=SymbolId(id)),
    )
