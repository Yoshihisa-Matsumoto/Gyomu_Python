from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Literal

from gyomu_schema.error.config import ConfigError, ConfigPhase, ConfigSource
from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from gyomu_schema.schemas.config.test.model_defaults import (
    AttributeParameter,
    CallParameter,
    DictEntry,
    DictParameter,
    KeywordArgument,
    ListParameter,
    LiteralParameter,
    ModelDefault,
    ModelDefaults,
    NameParameter,
    NoneParameter,
    PackageModelDefaults,
    Parameter,
    ParameterDefault,
    ParameterExpressionType,
    PrimitiveDefault,
    PrimitiveDefaults,
    TupleParameter,
)
from gyomu_schema.schemas.python.class_analysis import (
    ClassAnalysis,
    ClassTypeAliasAnalysis,
    ClassVariableAnalysis,
    InnerClassAnalysis,
)
from gyomu_schema.schemas.python.decorator import DecoratorAnalysis
from gyomu_schema.schemas.python.dependency import (
    DependencyAnalysis,
    ImportedSymbolDependency,
    LocalFileDependency,
)
from gyomu_schema.schemas.python.docstring import (
    DocstringAnalysis,
    DocstringCustomListSection,
    DocstringCustomNamedSectionItem,
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
from gyomu_schema.schemas.python.import_analysis import ImportAnalysis, ImportKind
from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.method_analysis import MethodAnalysis
from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.parameter import ParameterAnalysis
from gyomu_schema.schemas.python.pydantic import PydanticFieldAnalysis
from gyomu_schema.schemas.python.symbol import MemberAnalysis, SymbolAnalysis
from gyomu_schema.schemas.python.symbol_base import DeclarationKind
from gyomu_schema.schemas.python.type.expression import StatementAnalysis
from gyomu_schema.schemas.python.type.structure import (
    EllipsisStructureAnalysis,
    LiteralValue,
    NameStructureAnalysis,
    NoneStructureAnalysis,
    UnknownStructureAnalysis,
)
from gyomu_schema.schemas.python.type.type_analysis import (
    ArrayStructureAnalysis,
    AttributeStructureAnalysis,
    CallableStructureAnalysis,
    CallStructureAnalysis,
    DictionaryStructureAnalysis,
    GenericsStructureAnalysis,
    KeywordStructureAnalysis,
    LiteralStructureAnalysis,
    SetStructureAnalysis,
    StructureAnalysis,
    TupleStructureAnalysis,
    TypeAnalysis,
    TypeExpression,
    UnionStructureAnalysis,
)
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


def build_declaration_identity(
    module_path: PythonPath, symbol_name: str
) -> DeclarationIdentity:
    return DeclarationIdentity(
        symbol_id=SymbolId(f"{module_path}::{symbol_name}"),
        declaration_id=DeclarationId("."),
    )


def simple_create_declaration_identity(id: str = "test") -> DeclarationIdentity:
    return DeclarationIdentity(
        symbol_id=SymbolId(id),
        declaration_id=DeclarationId("."),
    )


def create_source_location(
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
    name: str = "test_alias",
    visibility: Visibility = Visibility.PUBLIC,
    docstring: DocstringAnalysis | None = None,
    decorators: tuple[DecoratorAnalysis, ...] = (),
    identity: DeclarationIdentity = simple_create_declaration_identity("test_alias"),
    location: SourceLocation = create_source_location(),
    dependencies: tuple[DependencyAnalysis, ...] = (),
    indent: int = 0,
    kind: Literal[DeclarationKind.TYPEALIAS] = DeclarationKind.TYPEALIAS,
    alias_type: TypeAnalysis | None = None,
) -> TypeAliasAnalysis:
    return TypeAliasAnalysis(
        name=name,
        visibility=visibility,
        docstring=docstring,
        decorators=decorators,
        identity=identity,
        location=location,
        dependencies=dependencies,
        indent=indent,
        kind=kind,
        alias_type=alias_type,
    )


def create_class_type_alias_analysis(
    indent: int,
    location: SourceLocation,
    name: str = "test_func",
    identity: DeclarationIdentity | None = None,
) -> ClassTypeAliasAnalysis:
    if identity is None:
        identity = simple_create_declaration_identity(name)
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
    indent: int = 0,
    location: SourceLocation = create_source_location(),  # noqa: B008
    name: str = "test_func",
    identity: DeclarationIdentity = simple_create_declaration_identity("test_func"),
    type: TypeAnalysis | None = None,
    value_source: str | None = None,
    pydantic: PydanticFieldAnalysis | None = None,
    docstring: DocstringAnalysis | None = None,
) -> VariableAnalysis:

    return VariableAnalysis(
        name=name,
        docstring=docstring,
        identity=identity,
        decorators=tuple(),
        dependencies=tuple(),
        indent=indent,
        kind=DeclarationKind.VARIABLE,
        visibility=Visibility.PUBLIC,
        location=location,
        type=type,
        value_source=value_source,
        pydantic=pydantic,
    )


def create_class_variable_analysis(
    name: str = "test_variable",
    visibility: Visibility = Visibility.PUBLIC,
    docstring: DocstringAnalysis | None = None,
    decorators: tuple[DecoratorAnalysis, ...] = (),
    identity: DeclarationIdentity = simple_create_declaration_identity("test_variable"),
    location: SourceLocation | None = None,
    indent: int | None = None,
    kind: Literal[DeclarationKind.VARIABLE] = DeclarationKind.VARIABLE,
    type: TypeAnalysis | None = None,
    value_source: str | None = None,
    pydantic: PydanticFieldAnalysis | None = None,
) -> ClassVariableAnalysis:

    return ClassVariableAnalysis(
        name=name,
        visibility=visibility,
        docstring=docstring,
        identity=identity,
        decorators=decorators,
        indent=indent,
        kind=kind,
        location=location,
        type=type,
        value_source=value_source,
        pydantic=pydantic,
    )


def create_function_analysis(
    parameters: tuple[ParameterAnalysis, ...] = (),
    return_type: TypeAnalysis | None = None,
    is_async: bool = False,
    is_ellipsis_only: bool = False,
    name: str = "test_func",
    visibility: Visibility = Visibility.PUBLIC,
    docstring: DocstringAnalysis | None = None,
    decorators: tuple[DecoratorAnalysis, ...] = (),
    identity: DeclarationIdentity = simple_create_declaration_identity("test_func"),
    location: SourceLocation = create_source_location(),
    dependencies: tuple[DependencyAnalysis, ...] = (),
    indent: int = 0,
    kind: Literal[DeclarationKind.FUNCTION] = DeclarationKind.FUNCTION,
) -> FunctionAnalysis:
    return FunctionAnalysis(
        parameters=parameters,
        return_type=return_type,
        is_async=is_async,
        is_ellipsis_only=is_ellipsis_only,
        name=name,
        visibility=visibility,
        docstring=docstring,
        decorators=decorators,
        identity=identity,
        location=location,
        dependencies=dependencies,
        indent=indent,
        kind=kind,
    )


def create_method_analysis(
    indent: int | None,
    location: SourceLocation | None,
    name: str = "test_func",
    identity: DeclarationIdentity | None = None,
    docstring: DocstringAnalysis | None = None,
    is_ellipsis_only: bool = False,
    statements: tuple[StatementAnalysis, ...] = tuple(),
) -> MethodAnalysis:
    if identity is None:
        identity = simple_create_declaration_identity(name)
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
        is_ellipsis_only=is_ellipsis_only,
    )


def create_class_analysis(
    indent: int = 0,
    location: SourceLocation = create_source_location(),  # noqa: B008
    name: str = "test_class",
    identity: DeclarationIdentity | None = None,
    methods: tuple[MethodAnalysis, ...] = tuple(),
    variables: tuple[ClassVariableAnalysis, ...] = tuple(),
    type_aliases: tuple[ClassTypeAliasAnalysis, ...] = tuple(),
    inner_classes: tuple[InnerClassAnalysis, ...] = tuple(),
    bases: tuple[TypeAnalysis, ...] = tuple(),
) -> ClassAnalysis:
    if identity is None:
        identity = simple_create_declaration_identity(name)
    return ClassAnalysis(
        name=name,
        docstring=None,
        identity=identity,
        decorators=tuple(),
        dependencies=tuple(),
        indent=indent,
        kind=DeclarationKind.CLASS,
        bases=bases,
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
        identity = simple_create_declaration_identity(name)
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


def create_name_structure_analysis(name: str = "name") -> NameStructureAnalysis:
    return NameStructureAnalysis(name=name)


def create_none_structure_analysis() -> NoneStructureAnalysis:
    return NoneStructureAnalysis()


def create_type_analysis(
    text: str, structure: StructureAnalysis | None = None
) -> TypeAnalysis:
    return TypeAnalysis(text=text, structure=structure)


def create_union_structure_analysis(
    types: tuple[TypeExpression, ...] = (create_name_structure_analysis(),),
) -> UnionStructureAnalysis:
    return UnionStructureAnalysis(types=types)


def create_attribute_structure_analysis(
    values: tuple[TypeExpression, ...] = (create_name_structure_analysis(),),
) -> AttributeStructureAnalysis:
    return AttributeStructureAnalysis(values=values)


def create_tuple_structure_analysis(
    elements: Sequence[TypeExpression] = (create_name_structure_analysis(),),
    variable_length: bool = False,
) -> TupleStructureAnalysis:
    return TupleStructureAnalysis(elements=elements, variable_length=variable_length)


def create_set_structure_analysis(
    element_type: TypeExpression = create_name_structure_analysis(),
) -> SetStructureAnalysis:
    return SetStructureAnalysis(element_type=element_type)


def create_literal_structure_analysis(
    value: TypeExpression = create_name_structure_analysis(),
) -> LiteralStructureAnalysis:
    return LiteralStructureAnalysis(value=value)


def create_unknown_structure_analysis() -> UnknownStructureAnalysis:
    return UnknownStructureAnalysis()


def create_array_structure_analysis(
    element: TypeExpression = create_name_structure_analysis(),
) -> ArrayStructureAnalysis:
    return ArrayStructureAnalysis(element=element)


def create_dictionary_structure_analysis(
    keys: TypeExpression = create_name_structure_analysis(),
    values: TypeExpression = create_name_structure_analysis(),
) -> DictionaryStructureAnalysis:
    return DictionaryStructureAnalysis(keys=keys, values=values)


def create_callable_structure_analysis(
    return_type: TypeExpression = create_name_structure_analysis(),
    parameters: tuple[TypeExpression, ...] | None = None,
) -> CallableStructureAnalysis:
    return CallableStructureAnalysis(return_type=return_type, parameters=parameters)


def create_ellipsis_structure_analysis() -> EllipsisStructureAnalysis:
    return EllipsisStructureAnalysis()


def create_call_structure_analysis(
    function: StructureAnalysis = create_name_structure_analysis(),
    arguments: tuple[TypeExpression, ...] = (create_name_structure_analysis(),),
) -> CallStructureAnalysis:
    return CallStructureAnalysis(function=function, arguments=arguments)


def create_generics_structure_analysis(
    base: TypeExpression = create_name_structure_analysis(),
    parameters: tuple[TypeExpression, ...] = (create_name_structure_analysis(),),
) -> GenericsStructureAnalysis:
    return GenericsStructureAnalysis(base=base, parameters=parameters)


def create_keyword_structure_analysis(
    name: str = "param", value: TypeExpression = create_name_structure_analysis()
) -> KeywordStructureAnalysis:
    return KeywordStructureAnalysis(name=name, value=value)


def create_module_analysis(
    path: SourceRelativePath = SourceRelativePath(Path(".")),
    name: str = "test",
    module_name=PythonPath(""),
    docstring: DocstringAnalysis | None = None,
    imports: tuple[ImportAnalysis, ...] = tuple(),
    symbols: tuple[SymbolAnalysis, ...] = (),
) -> ModuleAnalysis:
    return ModuleAnalysis(
        path=path,
        name=name,
        module_name=module_name,
        docstring=docstring,
        imports=imports,
        symbols=symbols,
    )


def create_file_analysis_metadata(
    parsed_docstring: dict[DeclarationIdentity, DocstringAnalysis] = {},
    symbols: dict[DeclarationIdentity, SymbolAnalysis | MemberAnalysis] = {},
) -> FileAnalysisMetadata:
    return FileAnalysisMetadata(parsed_docstring=parsed_docstring, symbols=symbols)


def create_file_analysis_context(
    metadata: FileAnalysisMetadata = create_file_analysis_metadata(),
    analysis: ModuleAnalysis = create_module_analysis(),
) -> FileAnalysisContext:
    return FileAnalysisContext(metadata=metadata, analysis=analysis)


def build_file_analysis_context(
    symbol: SymbolAnalysis | MemberAnalysis | None = None,
    symbol2: SymbolAnalysis | MemberAnalysis | None = None,
    symbol3: SymbolAnalysis | MemberAnalysis | None = None,
    module_path: SourceRelativePath | None = None,
    module_name: str = "test",
    python_path: PythonPath | None = None,
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
            path=SourceRelativePath(Path("test.py"))
            if module_path is None
            else module_path,
            name=module_name,
            module_name=PythonPath("test") if python_path is None else python_path,
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
        location=location if location is not None else create_source_location(),
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


def create_custom_named_section_item(
    value: str,
    name: str | None = None,
) -> DocstringCustomNamedSectionItem:
    return DocstringCustomNamedSectionItem(name=name, value=value)


def create_custom_list_section(
    title: str, items: tuple[DocstringCustomNamedSectionItem, ...]
) -> DocstringCustomListSection:
    return DocstringCustomListSection(title=title, items=items)


def create_import_dependency_analysis(id: str) -> DependencyAnalysis:
    return DependencyAnalysis(
        source=simple_create_declaration_identity(id),
        target=ImportedSymbolDependency(symbol_id=SymbolId(id)),
    )


def create_local_dependency_analysis(id: str) -> DependencyAnalysis:
    return DependencyAnalysis(
        source=simple_create_declaration_identity(id),
        target=LocalFileDependency(symbol_id=SymbolId(id)),
    )


def create_gyomu_io_error(
    message: str = "test",
    layer: IOLayer = IOLayer.FILESYSTEM,
    operation: IOOperation = IOOperation.WRITE,
    target: str | None = None,
    retryable: bool = False,
    reason: str | None = None,
) -> GyomuIOError:
    return GyomuIOError(
        message=message,
        layer=layer,
        operation=operation,
        target=target,
        retryable=retryable,
        reason=reason,
    )


def create_config_error(
    message: str = "config error",
    phase: ConfigPhase = "load",
    source: ConfigSource = "json",
    schema: object | None = None,
    context: str | None = None,
    details: Mapping[str, object] | None = None,
) -> ConfigError:
    return ConfigError(
        message=message,
        phase=phase,
        source=source,
        schema=schema,
        context=context,
        details=details,
    )


def create_import_analysis(
    local_name: str = "BaseModel",
    imported_name: str = "pydantic.BaseModel",
    kind: ImportKind = ImportKind.SYMBOL,
) -> ImportAnalysis:
    return ImportAnalysis(local_name=local_name, imported_name=imported_name, kind=kind)


def create_literal_parameter(
    kind: Literal[ParameterExpressionType.LITERAL] = ParameterExpressionType.LITERAL,
    value: int | bool | str | float = "test",
) -> LiteralParameter:
    return LiteralParameter(kind=kind, value=value)


def create_none_parameter(
    kind: Literal[ParameterExpressionType.NONE] = ParameterExpressionType.NONE,
) -> NoneParameter:
    return NoneParameter(kind=kind)


def create_name_parameter(name: str = "parameter1") -> NameParameter:
    return NameParameter(name=name)


def create_attribute_parameter(
    kind: Literal[ParameterExpressionType.ATTR] = ParameterExpressionType.ATTR,
    value: Parameter = create_name_parameter(),  # noqa: B008
    attribute: str = "member",
) -> AttributeParameter:
    return AttributeParameter(kind=kind, value=value, attribute=attribute)


def create_tuple_parameter(
    kind: Literal[ParameterExpressionType.TUPLE] = ParameterExpressionType.TUPLE,
    elements: tuple[Parameter, ...] = (create_literal_parameter(),),
) -> TupleParameter:
    return TupleParameter(kind=kind, elements=elements)


def create_list_parameter(
    kind: Literal[ParameterExpressionType.LIST] = ParameterExpressionType.LIST,
    elements: tuple[Parameter, ...] = (create_literal_parameter(),),
) -> ListParameter:
    return ListParameter(kind=kind, elements=elements)


def create_dict_entry(
    key: Parameter = create_literal_parameter(),  # noqa: B008
    value: Parameter = create_literal_parameter(),  # noqa: B008
) -> DictEntry:
    return DictEntry(key=key, value=value)


def create_dict_parameter(
    kind: Literal[ParameterExpressionType.DICT] = ParameterExpressionType.DICT,
    entries: tuple[DictEntry, ...] = (create_dict_entry(),),
) -> DictParameter:
    return DictParameter(kind=kind, entries=entries)


def create_keyword_argument(
    name: str = "arg1",
    value: Parameter = create_literal_parameter(),  # noqa: B008
) -> KeywordArgument:
    return KeywordArgument(name=name, value=value)


def create_call_parameter(
    kind: Literal[ParameterExpressionType.CALL] = ParameterExpressionType.CALL,
    callable_identity: DeclarationIdentity = simple_create_declaration_identity(),  # noqa: B008
    args: tuple[Parameter, ...] = (),
    kwargs: tuple[KeywordArgument, ...] = (),
) -> CallParameter:
    return CallParameter(
        kind=kind, callable_identity=callable_identity, args=args, kwargs=kwargs
    )


def create_parameter_default(
    name: str = "parameter",
    value: Parameter = create_literal_parameter(),  # noqa: B008
) -> ParameterDefault:
    return ParameterDefault(name=name, value=value)


def create_model_default(
    class_name: str = "Test",
    parameters: tuple[ParameterDefault, ...] = (create_parameter_default(),),
) -> ModelDefault:
    return ModelDefault(symbol_name=class_name, parameters=parameters)


def create_model_defaults(
    models: tuple[ModelDefault, ...] = (create_model_default(),),
) -> ModelDefaults:
    return ModelDefaults(models=models)


def create_primitive_default(
    type_name: str = "str",
    variable_name: str = "parameter",
    parameters: tuple[ParameterDefault, ...] = (create_parameter_default(),),
) -> PrimitiveDefault:
    return PrimitiveDefault(
        type_name=type_name, variable_name=variable_name, parameters=parameters
    )


def create_primitive_defaults(
    defaults_per_variable_name: dict[str, tuple[ParameterDefault, ...]] = {
        "var": (create_parameter_default(),),
    },
) -> PrimitiveDefaults:
    return PrimitiveDefaults(defaults_per_variable_name=defaults_per_variable_name)


def create_package_model_defaults(
    models_per_module_path: dict[PythonPath, ModelDefaults] = {
        PythonPath("test"): create_model_defaults()
    },
    primitives_per_type: dict[str, PrimitiveDefaults] = {
        "str": create_primitive_defaults()
    },
) -> PackageModelDefaults:
    return PackageModelDefaults(
        models_per_module_path=models_per_module_path,
        primitives_per_type=primitives_per_type,
    )


STRUCTURE_FACTORIES: dict[type, StructureAnalysis] = {
    NameStructureAnalysis: create_name_structure_analysis(),
    NoneStructureAnalysis: create_none_structure_analysis(),
    UnionStructureAnalysis: create_union_structure_analysis(),
    AttributeStructureAnalysis: create_attribute_structure_analysis(),
    TupleStructureAnalysis: create_tuple_structure_analysis(),
    GenericsStructureAnalysis: create_generics_structure_analysis(),
    LiteralStructureAnalysis: create_literal_structure_analysis(),
    ArrayStructureAnalysis: create_array_structure_analysis(),
    DictionaryStructureAnalysis: create_dictionary_structure_analysis(),
    CallableStructureAnalysis: create_callable_structure_analysis(),
    UnknownStructureAnalysis: create_unknown_structure_analysis(),
    SetStructureAnalysis: create_set_structure_analysis(),
    KeywordStructureAnalysis: create_keyword_structure_analysis(),
    CallStructureAnalysis: create_call_structure_analysis(),
    EllipsisStructureAnalysis: create_ellipsis_structure_analysis(),
}
