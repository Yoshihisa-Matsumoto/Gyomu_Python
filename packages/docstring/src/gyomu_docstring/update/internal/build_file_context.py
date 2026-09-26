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
from gyomu_python_analysis.analysis.analyzers.cls import is_base_class_pydantic
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
from gyomu_schema.schemas.python.function_analysis import FunctionAnalysis
from gyomu_schema.schemas.python.location import SourceLocation
from gyomu_schema.schemas.python.symbol import MemberAnalysis, SymbolAnalysis
from gyomu_schema.schemas.python.symbol_base import DeclarationKind


def build_docstring_file_context(
    project_name: str,
    file_context: FileAnalysisContext,
    source: str,
) -> DocstringFileContext:
    """Builds a docstring file context from file analysis data."""

    return DocstringFileContext(
        project_name=project_name,
        source_relative_path=file_context.analysis.path,
        symbols=tuple(
            build_docstring_declaration_context(
                analysis=symbol,
                source=source,
            )
            for symbol in file_context.analysis.symbols
            if is_docstring_target(symbol)
        ),
        retry=None,
    )


def is_docstring_target(symbol: SymbolAnalysis) -> bool:
    """Determines whether a symbol is a valid target for docstring processing."""

    if isinstance(symbol, FunctionAnalysis):
        return not symbol.is_ellipsis_only
    return True


def build_docstring_declaration_context(
    analysis: SymbolAnalysis, source: str
) -> DocstringDeclarationContext:
    """Builds a docstring declaration context from symbol analysis and source code."""

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


def is_documentable_child_entry(cls: ClassBase, member: MemberAnalysis) -> bool:
    """Determines whether a class member is eligible for documentation."""

    if member.location is None:
        return False

    if member.kind == DeclarationKind.METHOD and member.is_ellipsis_only:
        return False
    is_pydantic = is_base_class_pydantic(list(cls.bases))
    if not is_pydantic:
        return True
    return not (
        member.kind == DeclarationKind.VARIABLE and member.name == "model_config"
    )


def build_context_entries(cls: ClassBase) -> tuple[ContextEntry, ...]:
    """Builds context entries for documentable members of a class."""

    entries: list[ContextEntry] = []

    for variable in cls.variables:
        if is_documentable_child_entry(cls, variable):
            entries.append(build_context_entry(cls, variable))
    for typealias in cls.type_aliases:
        if is_documentable_child_entry(cls, typealias):
            entries.append(build_context_entry(cls, typealias))

    for method in cls.methods:
        if is_documentable_child_entry(cls, method):
            entries.append(build_context_entry(cls, method))
    for inner in cls.inner_classes:
        if is_documentable_child_entry(cls, inner):
            entries.append(build_context_entry(cls, inner))

    return tuple(entries)


def build_context_entry(cls: ClassBase, member: MemberAnalysis) -> ContextEntry:
    """Builds a context entry for a class member analysis."""

    is_documentable = is_documentable_child_entry(cls, member)
    return ContextEntry(
        target=member.identity,
        member=_build_declaration_info(member),
        existing_docstring=build_existing_docstring(member.docstring)
        if member.docstring is not None
        else None,
        documentable=DocumentableContext()
        if is_documentable
        else NonDocumentableContext(reason="non-documentable-member"),
        children=build_context_entries(member)
        if isinstance(member, InnerClassAnalysis)
        else tuple(),
    )


def build_dependencies(
    dependencies: tuple[DependencyAnalysis, ...],
) -> tuple[DependencySummary, ...]:
    """Builds a tuple of dependency summaries from dependency analyses."""

    return tuple(DependencySummary(target=item.target) for item in dependencies)


def _build_declaration_info(target: SymbolAnalysis | MemberAnalysis) -> DeclarationInfo:
    """Builds declaration info from a symbol or member analysis."""

    return DeclarationInfo(name=target.name, kind=target.kind.value)


def _build_code(source: str, location: SourceLocation) -> str:
    """Extracts source code snippet based on a source location."""

    return source[location.start_offset : location.end_offset]


def build_existing_docstring(docstring: DocstringAnalysis) -> ExistingDocstring:
    """Builds an existing docstring structure from docstring analysis."""

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
    """Finds a specific section within an existing docstring analysis."""

    return next(
        (
            section
            for section in existing_docstring.sections
            if isinstance(section, section_type)
        ),
        None,
    )
