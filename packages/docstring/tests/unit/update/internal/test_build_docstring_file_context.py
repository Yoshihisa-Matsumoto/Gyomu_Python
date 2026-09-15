from gyomu_ai_compiler.pipelines.docstring_update.context.declaration_context import (
    ContextEntry,
    DeclarationInfo,
    DocstringParameter,
    DocstringRaise,
    DocstringReturn,
    DocumentableContext,
    ExistingDocstring,
    NonDocumentableContext,
)
from gyomu_docstring.update.internal.build_docstring_file_context import (
    _build_code,
    _build_declaration_info,
    build_context_entries,
    build_context_entry,
    build_dependencies,
    build_docstring_declaration_context,
    build_docstring_file_context,
    build_existing_docstring,
)
from gyomu_schema.schemas.python.dependency import (
    DependencyAnalysis,
    DependencySummary,
    ImportedSymbolDependency,
    LocalFileDependency,
)
from gyomu_schema.schemas.python.docstring import (
    DocstringAnalysis,
    DocstringParametersSection,
    DocstringParametersSectionItem,
    DocstringRaisesSection,
    DocstringRaisesSectionItem,
    DocstringReturnsSection,
    DocstringReturnsSectionItem,
    DocstringSection,
    DocstringStyle,
)
from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.types import SymbolId

from packages.schema.schema_test_support.helpers import (
    create_class_analysis,
    create_class_type_alias_analysis,
    create_class_variable_analysis,
    create_declaration_identity,
    create_docstring,
    create_file_analysis_context,
    create_function_analysis,
    create_inner_class_analysis,
    create_location,
    create_method_analysis,
)


def _docstring(sections: tuple[DocstringSection, ...]) -> DocstringAnalysis:
    return DocstringAnalysis(
        raw="""Summary.

    Description.

    Args:
        name: Name.
        age: Age.

    Returns:
        User.

    Raises:
        ValueError: Invalid value.
    """,
        summary="Summary.",
        description="Description.",
        style=DocstringStyle.GOOGLE,
        location=create_location(),
        indent=4,
        sections=sections,
    )


class TestBuildExistingDocstring:
    def test_build_existing_docstring(self) -> None:
        docstring = DocstringAnalysis(
            raw="""Summary.

    Description.

    Args:
        name: Name.
        age: Age.

    Returns:
        User.

    Raises:
        ValueError: Invalid value.
    """,
            summary="Summary.",
            description="Description.",
            style=DocstringStyle.GOOGLE,
            location=create_location(),
            indent=4,
            sections=(
                DocstringParametersSection(
                    items=(
                        DocstringParametersSectionItem(
                            name="name",
                            type="str",
                            description="Name.",
                        ),
                        DocstringParametersSectionItem(
                            name="age",
                            type="int",
                            description="Age.",
                        ),
                    ),
                ),
                DocstringReturnsSection(
                    item=DocstringReturnsSectionItem(
                        type="User",
                        description="User.",
                    ),
                ),
                DocstringRaisesSection(
                    items=(
                        DocstringRaisesSectionItem(
                            type="ValueError",
                            description="Invalid value.",
                        ),
                    ),
                ),
            ),
        )

        result = build_existing_docstring(docstring)

        assert result == ExistingDocstring(
            summary="Summary.",
            description="Description.",
            parameters=(
                DocstringParameter(
                    name="name",
                    type="str",
                    description="Name.",
                    sort_order=0,
                ),
                DocstringParameter(
                    name="age",
                    type="int",
                    description="Age.",
                    sort_order=1,
                ),
            ),
            returns=DocstringReturn(
                type="User",
                description="User.",
            ),
            raises=(
                DocstringRaise(
                    type="ValueError",
                    description="Invalid value.",
                ),
            ),
        )

    def test_build_existing_docstring_without_parameters(self) -> None:
        docstring = _docstring(
            sections=(
                DocstringReturnsSection(
                    item=DocstringReturnsSectionItem(
                        type="str",
                        description="The result.",
                    ),
                ),
            ),
        )

        result = build_existing_docstring(docstring)

        assert result.parameters == ()

    def test_build_existing_docstring_without_returns(self) -> None:
        docstring = _docstring(
            sections=(
                DocstringParametersSection(
                    items=(
                        DocstringParametersSectionItem(
                            name="value",
                            type="int",
                            description="The value.",
                        ),
                    ),
                ),
            ),
        )

        result = build_existing_docstring(docstring)

        assert result.returns is None

    def test_build_existing_docstring_without_raises(self) -> None:
        docstring = _docstring(
            sections=(
                DocstringParametersSection(
                    items=(
                        DocstringParametersSectionItem(
                            name="value",
                            type="int",
                            description="The value.",
                        ),
                    ),
                ),
            ),
        )

        result = build_existing_docstring(docstring)

        assert result.raises == ()

    def test_build_existing_docstring_without_sections(self) -> None:
        docstring = _docstring(sections=())

        result = build_existing_docstring(docstring)

        assert result == ExistingDocstring(
            summary=docstring.summary,
            description=docstring.description,
            parameters=(),
            returns=None,
            raises=(),
        )

    def test_build_existing_docstring_parameter_sort_order(self) -> None:
        docstring = _docstring(
            sections=(
                DocstringParametersSection(
                    items=(
                        DocstringParametersSectionItem(
                            name="first",
                            type=None,
                            description="First.",
                        ),
                        DocstringParametersSectionItem(
                            name="second",
                            type=None,
                            description="Second.",
                        ),
                        DocstringParametersSectionItem(
                            name="third",
                            type=None,
                            description="Third.",
                        ),
                    ),
                ),
            ),
        )

        result = build_existing_docstring(docstring)

        assert tuple(parameter.sort_order for parameter in result.parameters) == (
            0,
            1,
            2,
        )


class TestBuildCode:
    def test_build_code(self) -> None:
        source = "class Foo:\n    def bar(self) -> None:\n        pass\n"

        start = source.index("def bar")
        end = source.index("\n", source.index("pass")) + 1

        location = SourceLocation(
            start_line=2,
            start_column=4,
            start_offset=start,
            end_line=3,
            end_column=12,
            end_offset=end,
        )

        assert _build_code(source, location) == (
            "def bar(self) -> None:\n        pass\n"
        )

    def test_build_code_uses_half_open_offset_range(self) -> None:
        source = "0123456789"

        location = SourceLocation(
            start_line=1,
            start_column=2,
            start_offset=2,
            end_line=1,
            end_column=7,
            end_offset=7,
        )

        assert _build_code(source, location) == "23456"


class TestBuildDeclarationInfo:
    def test_build_declaration_info(self) -> None:
        analysis = create_function_analysis(indent=0, location=create_location())

        result = _build_declaration_info(analysis)

        assert result == DeclarationInfo(
            name=analysis.name,
            kind="function",
        )


class TestBuildDependencies:
    def test_build_dependencies(self) -> None:
        dependencies = (
            DependencyAnalysis(
                source=create_declaration_identity("id1"),
                target=LocalFileDependency(
                    symbol_id=SymbolId("symbol1"),
                ),
            ),
            DependencyAnalysis(
                source=create_declaration_identity("id2"),
                target=ImportedSymbolDependency(
                    symbol_id=SymbolId("symbol2"),
                ),
            ),
        )

        result = build_dependencies(dependencies)

        assert result == (
            DependencySummary(
                target=dependencies[0].target,
            ),
            DependencySummary(
                target=dependencies[1].target,
            ),
        )


class TestBuildContextEntry:
    def test_build_context_entry(self) -> None:
        member = create_method_analysis(
            indent=4,
            name="foo",
            location=create_location(),
        )

        result = build_context_entry(member)

        assert result == ContextEntry(
            target=member.identity,
            member=DeclarationInfo(
                name="foo",
                kind="method",
            ),
            existing_docstring=None,
            children=(),
            documentable=DocumentableContext(),
        )

    def test_build_context_entry_with_docstring(self) -> None:
        docstring = create_docstring(
            summary="Do something.",
        )
        member = create_method_analysis(
            indent=4,
            name="foo",
            location=create_location(),
            docstring=docstring,
        )

        result = build_context_entry(member)

        assert result.existing_docstring == build_existing_docstring(docstring)

        assert result.existing_docstring == ExistingDocstring(
            summary="Do something.",
            description=None,
            parameters=(),
            returns=None,
            raises=(),
        )

    def test_build_context_entry_without_location(self) -> None:
        member = create_method_analysis(
            indent=4,
            name="foo",
            location=None,
        )

        result = build_context_entry(member)

        assert result.documentable == NonDocumentableContext(
            reason="non-documentable-member",
        )

    def test_build_context_entry_builds_inner_class_children(self) -> None:
        method = create_method_analysis(
            indent=8,
            name="foo",
            location=create_location(),
        )

        inner_class = create_inner_class_analysis(
            indent=4,
            name="Inner",
            location=create_location(),
            methods=(method,),
        )

        result = build_context_entry(inner_class)

        assert result.children == (
            ContextEntry(
                target=method.identity,
                member=DeclarationInfo(
                    name="foo",
                    kind="method",
                ),
                existing_docstring=None,
                documentable=DocumentableContext(),
                children=(),
            ),
        )

    def test_build_context_entries(self) -> None:
        variable = create_class_variable_analysis(indent=4, location=create_location())
        typealias = create_class_type_alias_analysis(
            indent=4, location=create_location()
        )
        method = create_method_analysis(indent=4, location=create_location())
        inner_class = create_inner_class_analysis(indent=4, location=create_location())

        cls = create_class_analysis(
            indent=0,
            location=create_location(),
            variables=(variable,),
            type_aliases=(typealias,),
            methods=(method,),
            inner_classes=(inner_class,),
        )

        result = build_context_entries(cls)

        assert tuple(entry.target for entry in result) == (
            variable.identity,
            typealias.identity,
            method.identity,
            inner_class.identity,
        )


class TestBuildDocstringDeclarationContext:
    def test_build_docstring_declaration_context(self) -> None:
        source = (
            "def foo(value: int) -> str:\n"
            '    """Do something."""\n'
            "    return str(value)\n"
        )

        analysis = create_function_analysis(
            indent=0,
            location=create_location(start_offset=0, end_offset=len(source)),
            name="foo",
            docstring=create_docstring(
                summary="Do something.",
            ),
            dependencies=(
                DependencyAnalysis(
                    source=create_declaration_identity("id1"),
                    target=LocalFileDependency(
                        symbol_id=SymbolId("symbol1"),
                    ),
                ),
            ),
        )

        result = build_docstring_declaration_context(
            analysis=analysis,
            source=source,
        )

        assert result.target == analysis.identity
        assert result.symbol == DeclarationInfo(
            name="foo",
            kind="function",
        )
        expected_code = source[
            analysis.location.start_offset : analysis.location.end_offset
        ]
        assert result.code == expected_code
        assert result.existing_docstring == ExistingDocstring(
            summary="Do something.",
            description=None,
            parameters=(),
            returns=None,
            raises=(),
        )
        assert result.dependencies == (
            DependencySummary(
                target=analysis.dependencies[0].target,
            ),
        )
        assert result.children == ()

    def test_build_docstring_declaration_context_for_class(self) -> None:
        method = create_method_analysis(
            indent=4,
            name="run",
            location=create_location(),
        )

        source = "class Service:\n    def run(self) -> None:\n        pass\n"
        analysis = create_class_analysis(
            indent=0,
            location=create_location(start_offset=0, end_offset=len(source)),
            name="Service",
            methods=(method,),
        )

        result = build_docstring_declaration_context(
            analysis=analysis,
            source=source,
        )

        assert len(result.children) == 1
        assert result.children[0].target == method.identity
        assert result.children[0].member == DeclarationInfo(
            name="run",
            kind="method",
        )


class TestBuildDocstringFileContext:
    def test_build_docstring_file_context(self) -> None:

        source = "def foo() -> None:\n    pass\n\nclass Foo:\n    pass\n"
        function = create_function_analysis(
            indent=0,
            location=create_location(start_offset=0, end_offset=len(source)),
            name="foo",
        )
        cls = create_class_analysis(
            indent=0,
            name="Foo",
            location=create_location(start_offset=0, end_offset=len(source)),
        )

        file_result = create_file_analysis_context(
            symbol=function,
            symbol2=cls,
        )

        result = build_docstring_file_context(
            project_name="example",
            file_result=file_result,
            source=source,
        )

        assert result.project_name == "example"
        assert result.source_relative_path == file_result.analysis.path
        assert result.retry is None

        assert tuple(symbol.target for symbol in result.symbols) == (
            function.identity,
            cls.identity,
        )
