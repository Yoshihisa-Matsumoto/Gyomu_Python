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
from gyomu_schema.schemas.concept.package.analysis import (
    DirectoryAnalysis,
    DirectoryAnalysisFact,
    PackageAnalysis,
    PackageDependencyAnalysis,
    PackageDependencyKind,
    PackageDependencySource,
    PyProjectAnalysis,
)
from gyomu_schema.schemas.concept.package.concept import (
    CapabilityConcept,
    PackageConcept,
)
from gyomu_schema.schemas.document.content import (
    BulletList,
    BulletListItem,
    CodeBlock,
    Paragraph,
    Table,
    TableRow,
)
from gyomu_schema.schemas.document.section import (
    DocumentContentTranslationStrategy,
    SectionNoTranslation,
    SectionTranslationDefinition,
    SectionTranslationInstruction,
)
from gyomu_schema.schemas.document.validation import ValidationIssue, ValidationResult
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
    symbol: str = "test",
    kind: DeclarationKind = DeclarationKind.VARIABLE,
    summary: str = "summary",
) -> PublicDeclarationSummary:
    return PublicDeclarationSummary(symbol=symbol, kind=kind, summary=summary)


# def create_re_exports_summary(
#     export_all: bool, module: str, symbol: str = ""
# ) -> ReExportSummary:
#     if export_all:
#         return ReExportSummaryAll(module=module)
#     return ReExportSummarySingle(module=module, symbol=symbol)


def create_dependency_summary(
    target: str = "target", external: bool = True
) -> DependencySummary:
    return DependencySummary(target=target, external=external)


def create_package_analysis(
    package: PyProjectAnalysis,
    dependencies: tuple[PackageDependencyAnalysis, ...],
    directories: tuple[DirectoryAnalysis, ...],
    public_files: tuple[FileSummary, ...],
) -> PackageAnalysis:
    return PackageAnalysis(
        package=package,
        dependencies=dependencies,
        directories=directories,
        public_files=public_files,
    )


def create_pyproject_analysis(
    name: str = "test",
    description: str | None = None,
    version: str = "1.0.0",
    license: str = "MIT",
) -> PyProjectAnalysis:
    return PyProjectAnalysis(
        name=name, description=description, version=version, license=license
    )


def create_dependency_analysis(
    package_name: str = "test",
    kind: PackageDependencyKind = "version",
    source: PackageDependencySource = "dependency",
    required_version: str | None = None,
) -> PackageDependencyAnalysis:
    return PackageDependencyAnalysis(
        package_name=package_name,
        kind=kind,
        source=source,
        required_version=required_version,
    )


def create_directory_analysis(
    path: ProjectRelativePath, concept: DirectoryConcept, fact: DirectoryAnalysisFact
) -> DirectoryAnalysis:
    return DirectoryAnalysis(path=path, concept=concept, fact=fact)


def create_directory_concept(
    summary: str = "summary",
    responsibilities: list[str] = ["responsibility"],  # noqa: B006
    concepts: list[str] = ["concept"],  # noqa: B006
    relationships: list[str] = ["relationship"],  # noqa: B006
    design_decisions: list[str] = ["design"],  # noqa: B006
    importance: DirectoryImportance = DirectoryImportance.CORE,
) -> DirectoryConcept:
    return DirectoryConcept(
        summary=summary,
        responsibilities=responsibilities,
        concepts=concepts,
        relationships=relationships,
        design_decisions=design_decisions,
        importance=importance,
    )


def create_directory_analysis_fact(
    public_symbol_count: int = 3, file_count: int = 3, total_symbol_count: int = 5
) -> DirectoryAnalysisFact:
    return DirectoryAnalysisFact(
        public_symbol_count=public_symbol_count,
        file_count=file_count,
        total_symbol_count=total_symbol_count,
    )


def create_capability_concept(
    name: str = "test", description: str = "description"
) -> CapabilityConcept:
    return CapabilityConcept(name=name, description=description)


def create_package_concept(
    summary: str = "summary",
    responsibilities: list[str] = [],  # noqa: B006
    capabilities: list[CapabilityConcept] = [],  # noqa: B006
    design_decisions: list[str] = [],  # noqa: B006
    usage_guidance: list[str] = [],  # noqa: B006
) -> PackageConcept:
    return PackageConcept(
        summary=summary,
        responsibilities=responsibilities,
        capabilities=capabilities,
        design_decisions=design_decisions,
        usage_guidance=usage_guidance,
    )


def create_paragraph(text: str = "this is a pen") -> Paragraph:
    return Paragraph(text=text)


def create_codeblock(
    language: str = "en", code="this is code block", title: str | None = None
) -> CodeBlock:
    return CodeBlock(language=language, code=code, title=title)


def create_table(header: TableRow, rows: tuple[TableRow, ...]) -> Table:
    return Table(header=header, rows=rows)


def create_table_row(cells: tuple[str, ...]) -> TableRow:
    return TableRow(cells=cells)


def create_bullet_list_item(
    translation_id: int = 1,
    text: str = "this is list item",
    children: tuple[BulletListItem, ...] | None = None,
) -> BulletListItem:
    return BulletListItem(translation_id=translation_id, text=text, children=children)


def create_bullet_list(items: tuple[BulletListItem, ...]) -> BulletList:
    return BulletList(items=items)


def create_section_translation(
    no_translation: bool = True,
    translation_instruction: str | None = None,
    translation_strategies: tuple[DocumentContentTranslationStrategy, ...] = tuple(),
) -> SectionTranslationDefinition:
    if no_translation:
        return SectionNoTranslation()
    else:
        return SectionTranslationInstruction(
            translation_instruction=translation_instruction,
            translation_strategies=translation_strategies,
        )


def create_validation_result(
    issues: tuple[ValidationIssue, ...] = tuple(),
) -> ValidationResult:
    return ValidationResult(issues=issues, is_valid=len(issues) == 0)


def create_validation_issue(
    code: str = "test",
    message: str = "invalid test",
    repair_instruction: str = "sample instruction",
    translation_id: int | None = None,
    details: dict[str, str] | None = None,
) -> ValidationIssue:
    return ValidationIssue(
        code=code,
        message=message,
        repair_instruction=repair_instruction,
        translation_id=translation_id,
        details=details,
    )
