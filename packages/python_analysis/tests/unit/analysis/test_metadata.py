from pathlib import Path

from gyomu_python_analysis.analysis.metadata import create_file_analysis_metadata
from gyomu_schema.schemas.python.class_analysis import (
    ClassAnalysis,
    ClassTypeAliasAnalysis,
    ClassVariableAnalysis,
    InnerClassAnalysis,
)
from gyomu_schema.schemas.python.docstring import DocstringAnalysis, DocstringStyle
from gyomu_schema.schemas.python.method_analysis import MethodAnalysis
from gyomu_schema.schemas.python.module import ModuleAnalysis
from gyomu_schema.schemas.python.type_alias import TypeAliasAnalysis
from gyomu_schema.schemas.python.types import PythonPath, SourceRelativePath
from gyomu_schema.schemas.python.visibility import Visibility

from packages.schema.schema_test_support.helpers import (
    create_declaration_identity,
    create_location,
)


class TestCreateFileAnalysisMetadata:
    def test_creates_empty_metadata_for_module_without_symbols(self) -> None:
        module_analysis = ModuleAnalysis(
            path=SourceRelativePath(Path("foo.py")),
            module_name=PythonPath("test.foo"),
            imports=tuple(),
            symbols=tuple(),
            name="foo",
            docstring=None,
        )

        result = create_file_analysis_metadata(module_analysis)

        assert result.symbols == {}
        assert result.parsed_docstring == {}

    def test_registers_module_level_symbols_with_docstring(
        self,
    ) -> None:
        symbol = TypeAliasAnalysis(
            name="test",
            identity=create_declaration_identity("test"),
            visibility=Visibility.PUBLIC,
            decorators=tuple(),
            location=create_location(),
            dependencies=tuple(),
            indent=0,
            alias_type=None,
            docstring=DocstringAnalysis(
                raw="",
                summary="test",
                description=None,
                style=DocstringStyle.GOOGLE,
                location=create_location(),
                sections=tuple(),
                indent=0,
            ),
        )
        module_analysis = ModuleAnalysis(
            path=SourceRelativePath(Path("foo.py")),
            module_name=PythonPath("test.foo"),
            imports=tuple(),
            symbols=(symbol,),
            name="foo",
            docstring=None,
        )

        result = create_file_analysis_metadata(module_analysis)

        assert result.symbols == {
            symbol.identity: symbol,
        }

        # if symbol.docstring is not None:
        assert result.parsed_docstring == {
            symbol.identity: symbol.docstring,
        }
        # else:
        #     assert result.parsed_docstring == {}

    def test_registers_module_level_symbols_without_docstring(
        self,
    ) -> None:
        symbol = TypeAliasAnalysis(
            name="test",
            identity=create_declaration_identity("test"),
            visibility=Visibility.PUBLIC,
            decorators=tuple(),
            location=create_location(),
            dependencies=tuple(),
            indent=0,
            alias_type=None,
            docstring=None,
        )
        module_analysis = ModuleAnalysis(
            path=SourceRelativePath(Path("foo.py")),
            module_name=PythonPath("test.foo"),
            imports=tuple(),
            symbols=(symbol,),
            name="foo",
            docstring=None,
        )

        result = create_file_analysis_metadata(module_analysis)

        assert result.symbols == {
            symbol.identity: symbol,
        }

        assert result.parsed_docstring == {}

    def test_registers_class_metadata_recursively(self) -> None:
        nested_inner_class = create_class_inner_class(
            "NestedInner",
            doc=True,
        )
        inner_class = create_class_inner_class(
            "Inner",
            doc=False,
            methods=(create_method("inner_method", doc=True),),
            variables=(create_class_variable("inner_variable", doc=False),),
            type_aliases=(create_class_typealias("InnerAlias", doc=True),),
            inner_classes=(nested_inner_class,),
        )
        cls = create_class(
            "TestClass",
            doc=True,
            methods=(create_method("method", doc=True),),
            variables=(create_class_variable("variable", doc=False),),
            type_aliases=(create_class_typealias("Alias", doc=True),),
            inner_classes=(inner_class,),
        )

        module_analysis = ModuleAnalysis(
            path=SourceRelativePath(Path("foo.py")),
            module_name=PythonPath("test.foo"),
            imports=tuple(),
            symbols=(cls,),
            name="foo",
            docstring=None,
        )

        result = create_file_analysis_metadata(module_analysis)

        assert result.symbols == {
            cls.identity: cls,
            inner_class.identity: inner_class,
            nested_inner_class.identity: nested_inner_class,
            cls.methods[0].identity: cls.methods[0],
            cls.variables[0].identity: cls.variables[0],
            cls.type_aliases[0].identity: cls.type_aliases[0],
            inner_class.methods[0].identity: inner_class.methods[0],
            inner_class.variables[0].identity: inner_class.variables[0],
            inner_class.type_aliases[0].identity: inner_class.type_aliases[0],
        }

        assert result.parsed_docstring == {
            cls.identity: cls.docstring,
            nested_inner_class.identity: nested_inner_class.docstring,
            cls.methods[0].identity: cls.methods[0].docstring,
            cls.type_aliases[0].identity: cls.type_aliases[0].docstring,
            inner_class.methods[0].identity: inner_class.methods[0].docstring,
            inner_class.type_aliases[0].identity: inner_class.type_aliases[0].docstring,
        }


def create_class(
    id: str,
    doc: bool,
    methods: tuple[MethodAnalysis, ...] = tuple(),
    variables: tuple[ClassVariableAnalysis, ...] = tuple(),
    type_aliases: tuple[ClassTypeAliasAnalysis, ...] = tuple(),
    inner_classes: tuple[InnerClassAnalysis, ...] = tuple(),
) -> ClassAnalysis:
    docstring = None
    if doc:
        docstring = DocstringAnalysis(
            raw="",
            summary="test",
            description=None,
            style=DocstringStyle.GOOGLE,
            location=create_location(),
            sections=tuple(),
            indent=4,
        )
    return ClassAnalysis(
        bases=tuple(),
        name=id,
        visibility=Visibility.PUBLIC,
        decorators=tuple(),
        identity=create_declaration_identity(id),
        indent=0,
        dependencies=tuple(),
        location=create_location(),
        methods=methods,
        docstring=docstring,
        variables=variables,
        type_aliases=type_aliases,
        inner_classes=inner_classes,
    )


def create_method(id: str, doc: bool) -> MethodAnalysis:
    docstring = None
    indent = 4
    if doc:
        docstring = DocstringAnalysis(
            raw="",
            summary="test",
            description=None,
            style=DocstringStyle.GOOGLE,
            location=create_location(),
            sections=tuple(),
            indent=indent,
        )
    return MethodAnalysis(
        return_type=None,
        is_async=False,
        name=id,
        visibility=Visibility.PUBLIC,
        decorators=tuple(),
        identity=create_declaration_identity(id),
        location=create_location(),
        indent=indent,
        docstring=docstring,
        parameters=tuple(),
    )


def create_class_variable(id: str, doc: bool) -> ClassVariableAnalysis:
    docstring = None
    indent = 4
    if doc:
        docstring = DocstringAnalysis(
            raw="",
            summary="test",
            description=None,
            style=DocstringStyle.GOOGLE,
            location=create_location(),
            sections=tuple(),
            indent=indent,
        )
    return ClassVariableAnalysis(
        name=id,
        visibility=Visibility.PUBLIC,
        docstring=docstring,
        decorators=tuple(),
        identity=create_declaration_identity(id),
        location=create_location(),
        pydantic=None,
        indent=4,
        type=None,
        value_source=None,
        value_expression=None,
    )


def create_class_typealias(id: str, doc: bool) -> ClassTypeAliasAnalysis:
    docstring = None
    indent = 4
    if doc:
        docstring = DocstringAnalysis(
            raw="",
            summary="test",
            description=None,
            style=DocstringStyle.GOOGLE,
            location=create_location(),
            sections=tuple(),
            indent=indent,
        )
    return ClassTypeAliasAnalysis(
        name=id,
        visibility=Visibility.PUBLIC,
        docstring=docstring,
        decorators=tuple(),
        identity=create_declaration_identity(id),
        location=create_location(),
        indent=4,
        alias_type=None,
    )


def create_class_inner_class(
    id: str,
    doc: bool,
    methods: tuple[MethodAnalysis, ...] = tuple(),
    variables: tuple[ClassVariableAnalysis, ...] = tuple(),
    type_aliases: tuple[ClassTypeAliasAnalysis, ...] = tuple(),
    inner_classes: tuple[InnerClassAnalysis, ...] = tuple(),
) -> InnerClassAnalysis:
    docstring = None
    indent = 4
    if doc:
        docstring = DocstringAnalysis(
            raw="",
            summary="test",
            description=None,
            style=DocstringStyle.GOOGLE,
            location=create_location(),
            sections=tuple(),
            indent=indent,
        )
    return InnerClassAnalysis(
        name=id,
        visibility=Visibility.PUBLIC,
        docstring=docstring,
        decorators=tuple(),
        identity=create_declaration_identity(id),
        location=create_location(),
        indent=4,
        bases=tuple(),
        methods=methods,
        variables=variables,
        type_aliases=type_aliases,
        inner_classes=inner_classes,
    )
