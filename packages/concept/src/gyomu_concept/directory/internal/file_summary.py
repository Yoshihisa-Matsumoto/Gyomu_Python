from gyomu_python_analysis.path.conversion import (
    source_relative_path_to_project_relative_path,
)
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.schemas.concept.file_summary import (
    DependencySummary,
    FileSummary,
    PublicDeclarationSummary,
)
from gyomu_schema.schemas.python.dependency import ImportedSymbolDependency
from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from gyomu_schema.schemas.python.symbol import SymbolAnalysis
from gyomu_schema.schemas.python.symbol_base import DeclarationKind
from gyomu_schema.schemas.python.visibility import Visibility


def build_file_summary_record(
    project_context: ProjectContext, file_context: FileAnalysisContext
) -> FileSummary:
    """Builds a file summary record for a given file context within a project.

    Returns:
        FileSummary: The constructed file summary record.
    """
    package_name = file_context.analysis.module_name.split(".")[0]
    return FileSummary(
        path=source_relative_path_to_project_relative_path(
            path=file_context.analysis.path, context=project_context
        ),
        exports=tuple(
            [
                _build_export_summary(item)
                for item in file_context.analysis.symbols
                if item.visibility == Visibility.PUBLIC
            ]
        ),
        dependencies=_aggregate_dependencies(
            file_context=file_context, package_name=package_name
        ),
    )


def _build_export_summary(item: SymbolAnalysis) -> PublicDeclarationSummary:
    """Builds a public declaration summary for a symbol analysis item.

    Returns:
        PublicDeclarationSummary: The public declaration summary.
    """
    summary = ""
    if (
        item.docstring is not None
        and item.docstring.summary is not None
        and item.docstring.summary != ""
    ):
        summary = item.docstring.summary
    elif (
        item.kind == DeclarationKind.VARIABLE
        and item.pydantic is not None
        and item.pydantic.description is not None
    ):
        summary = item.pydantic.description
    return PublicDeclarationSummary(
        symbol=item.identity.symbol_id, kind=item.kind, summary=summary
    )


def _aggregate_dependencies(
    file_context: FileAnalysisContext, package_name: str
) -> tuple[DependencySummary, ...]:
    """Aggregates unique dependencies from a file analysis context.

    Returns:
        tuple[DependencySummary, ...]: A tuple of aggregated dependency summaries.
    """
    dependencies = [
        dependency.target
        for symbol in file_context.analysis.symbols
        for dependency in symbol.dependencies
        if isinstance(dependency.target, ImportedSymbolDependency)
    ]

    summaries = {
        (
            summary.target,
            summary.external,
        ): summary
        for dependency in dependencies
        for summary in [
            _build_dependency_summary(
                import_item=dependency,
                package_name=package_name,
            )
        ]
    }

    return tuple(summaries.values())


def _build_dependency_summary(
    import_item: ImportedSymbolDependency, package_name: str
) -> DependencySummary:
    """Builds a dependency summary for an imported symbol.

    Returns:
        DependencySummary: The constructed dependency summary.
    """
    return DependencySummary(
        target=import_item.symbol_id,
        external=not import_item.symbol_id.startswith(package_name),
    )
