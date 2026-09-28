from pathlib import Path

from gyomu_schema.schemas.concept.directory.concept import (
    DirectoryConcept,
    DirectoryImportance,
)
from gyomu_schema.schemas.concept.directory.input import (
    DirectoryConceptInput,
    SubDirectoryInput,
)
from gyomu_schema.schemas.concept.file_summary import (
    DependencySummary,
    FileSummary,
    PublicDeclarationSummary,
)
from gyomu_schema.schemas.python.symbol_base import DeclarationKind
from gyomu_schema.schemas.python.types import DirectoryRelativePath, ProjectRelativePath


def create_directory_concept_input(
    files: tuple[FileSummary, ...], sub_directories: tuple[SubDirectoryInput, ...]
) -> DirectoryConceptInput:
    return DirectoryConceptInput(files=files, sub_directories=sub_directories)


def create_sub_directory_input(
    path: Path, concept: DirectoryConcept
) -> SubDirectoryInput:
    return SubDirectoryInput(path=DirectoryRelativePath(path), concept=concept)


def create_directory_concept(
    summary: str,
    responsibilities: list[str],
    concepts: list[str],
    relationships: list[str],
    design_decisions: list[str],
    importance: DirectoryImportance,
) -> DirectoryConcept:
    return DirectoryConcept(
        summary=summary,
        responsibilities=responsibilities,
        concepts=concepts,
        relationships=relationships,
        design_decisions=design_decisions,
        importance=importance,
    )


def create_file_summary(
    path: ProjectRelativePath,
    exports: tuple[PublicDeclarationSummary, ...],
    # re_exports: tuple[ReExportSummary, ...],
    dependencies: tuple[DependencySummary, ...],
) -> FileSummary:
    return FileSummary(
        path=path,
        exports=exports,
        #   re_exports=re_exports,
        dependencies=dependencies,
    )


def create_public_declaration_summary(
    symbol: str, kind: DeclarationKind, summary: str
) -> PublicDeclarationSummary:
    return PublicDeclarationSummary(symbol=symbol, kind=kind, summary=summary)


# def create_re_exports_summary(
#     export_all: bool, module: str, symbol: str = ""
# ) -> ReExportSummary:
#     if export_all:
#         return ReExportSummaryAll(module=module)
#     return ReExportSummarySingle(module=module, symbol=symbol)


def create_dependency_summary(target: str, external: bool) -> DependencySummary:
    return DependencySummary(target=target, external=external)
