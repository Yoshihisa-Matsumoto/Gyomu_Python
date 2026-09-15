from gyomu_ai_compiler.pipelines.docstring_update.context.declaration_context import (
    ContextEntry,
    DeclarationInfo,
    DocstringDeclarationContext,
    DocstringParameter,
    DocstringRaise,
    DocstringReturn,
    DocumentableContext,
    ExistingDocstring,
    NonDocumentableContext,
)
from gyomu_ai_compiler.pipelines.docstring_update.context.file_context import (
    DocstringFileContext,
)
from gyomu_schema.schemas.python.class_analysis import (
    ClassAnalysis,
    ClassBase,
    InnerClassAnalysis,
)
from gyomu_schema.schemas.python.dependency import DependencyAnalysis, DependencySummary
from gyomu_schema.schemas.python.docstring import (
    DocstringAnalysis,
    DocstringParametersSection,
    DocstringRaisesSection,
    DocstringReturnsSection,
    DocstringSection,
)
from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.symbol import MemberAnalysis, SymbolAnalysis


def build_docstring_file_context(
    project_name: str,
    file_result: FileAnalysisContext,
    source: str,
) -> DocstringFileContext:
    return DocstringFileContext(
        project_name=project_name,
        source_relative_path=file_result.analysis.path,
        symbols=tuple(
            build_docstring_declaration_context(
                analysis=symbol,
                source=source,
            )
            for symbol in file_result.analysis.symbols
        ),
        retry=None,
    )


def build_docstring_declaration_context(
    analysis: SymbolAnalysis, source: str
) -> DocstringDeclarationContext:
    return DocstringDeclarationContext(
        target=analysis.identity,
        symbol=_build_declaration_info(analysis),
        code=_build_code(source, analysis.location),
        existing_docstring=build_existing_docstring(analysis.docstring)
        if analysis.docstring is not None
        else None,
        dependencies=build_dependencies(analysis.dependencies),
        children=build_context_entries(analysis)
        if isinstance(analysis, ClassAnalysis)
        else tuple(),
    )


def build_context_entries(cls: ClassBase) -> tuple[ContextEntry, ...]:
    entries: list[ContextEntry] = []

    for variable in cls.variables:
        entries.append(build_context_entry(variable))
    for typealias in cls.type_aliases:
        entries.append(build_context_entry(typealias))

    for method in cls.methods:
        entries.append(build_context_entry(method))
    for inner in cls.inner_classes:
        entries.append(build_context_entry(inner))

    return tuple(entries)


def build_context_entry(member: MemberAnalysis) -> ContextEntry:

    return ContextEntry(
        target=member.identity,
        member=_build_declaration_info(member),
        existing_docstring=build_existing_docstring(member.docstring)
        if member.docstring is not None
        else None,
        documentable=DocumentableContext()
        if member.location is not None
        else NonDocumentableContext(reason="non-documentable-member"),
        children=build_context_entries(member)
        if isinstance(member, InnerClassAnalysis)
        else tuple(),
    )


def build_dependencies(
    dependencies: tuple[DependencyAnalysis, ...],
) -> tuple[DependencySummary, ...]:
    return tuple(DependencySummary(target=item.target) for item in dependencies)


def _build_declaration_info(target: SymbolAnalysis | MemberAnalysis) -> DeclarationInfo:
    return DeclarationInfo(name=target.name, kind=target.kind.value)


def _build_code(source: str, location: SourceLocation) -> str:
    return source[location.start_offset : location.end_offset]


def build_existing_docstring(docstring: DocstringAnalysis) -> ExistingDocstring:
    parameter_section = _find_section(docstring, DocstringParametersSection)
    parameters = (
        tuple()
        if parameter_section is None
        else tuple(
            DocstringParameter(
                name=parameter.name,
                type=parameter.type,
                description=parameter.description,
                sort_order=index,
            )
            for index, parameter in enumerate(parameter_section.items)
        )
    )
    raise_section = _find_section(docstring, DocstringRaisesSection)
    raises = (
        tuple()
        if raise_section is None
        else tuple(
            DocstringRaise(type=item.type, description=item.description)
            for item in raise_section.items
        )
    )
    return_section = _find_section(docstring, DocstringReturnsSection)
    returns = (
        None
        if return_section is None
        else DocstringReturn(
            type=return_section.item.type, description=return_section.item.description
        )
    )

    return ExistingDocstring(
        summary=docstring.summary,
        description=docstring.description,
        parameters=parameters,
        raises=raises,
        returns=returns,
    )


def _find_section[T: DocstringSection](
    existing_docstring: DocstringAnalysis, section_type: type[T]
) -> T | None:

    return next(
        (
            section
            for section in existing_docstring.sections
            if isinstance(section, section_type)
        ),
        None,
    )
