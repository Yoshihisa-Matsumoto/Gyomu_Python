from pathlib import Path
from typing import Any, Literal

from gyomu_schema.schemas.concept.base import DocumentBaseContext, Knowledge
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
from gyomu_schema.schemas.concept.llm_context.input import (
    LlmContextBuildContext,
    LlmKnowledge,
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
    DocumentContent,
    Paragraph,
    Table,
    TableRow,
)
from gyomu_schema.schemas.document.document import Document
from gyomu_schema.schemas.document.section import (
    BuiltSection,
    DocumentContentTranslationStrategy,
    LanguageCodes,
    Section,
    SectionLocation,
    SectionNoTranslation,
    SectionTranslationDefinition,
    SectionTranslationInstruction,
    SectionWithInstruction,
    TranslationRequest,
    TranslationRequestItem,
    TranslationResult,
    TranslationState,
    TranslationTarget,
)
from gyomu_schema.schemas.document.translation.code import (
    code_block_translation_strategy,
)
from gyomu_schema.schemas.document.translation.paragraph import (
    paragraph_translation_strategy,
)
from gyomu_schema.schemas.document.validation import ValidationIssue, ValidationResult
from gyomu_schema.schemas.knowledge.coding_guideline import CodingGuideline, CodingRule
from gyomu_schema.schemas.knowledge.development import (
    Development,
    DevelopmentFaq,
    DevelopmentKnownIssue,
    DevelopmentTip,
)
from gyomu_schema.schemas.knowledge.package import (
    Package,
    PackageExample,
    PackageTerminology,
    PackageUsage,
)
from gyomu_schema.schemas.knowledge.roadmap import Roadmap, RoadmapItem
from gyomu_schema.schemas.knowledge.technical import (
    Compatibility,
    Dependency,
    Installation,
    Technical,
    TechnicalConfiguration,
    TechnicalMigration,
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


def create_package_analysis__default() -> PackageAnalysis:
    return create_package_analysis(
        package=create_pyproject_analysis(),
        dependencies=(
            create_dependency_analysis(
                package_name="pydantic",
                kind="version",
                source="dependency",
                required_version="<3,>=2",
            ),
            create_dependency_analysis(
                package_name="pytest",
                kind="version",
                source="devDependency",
                required_version=">=9",
            ),
        ),
        directories=(
            create_directory_analysis(
                path=ProjectRelativePath(Path("src")),
                concept=create_directory_concept(),
                fact=create_directory_analysis_fact(),
            ),
        ),
        public_files=(
            create_file_summary(
                path=ProjectRelativePath(Path("src/test.py")),
                exports=(
                    create_public_declaration_summary(
                        symbol="test.module",
                        summary="Test symbol",
                    ),
                ),
                dependencies=(),
            ),
        ),
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
    language: str = "en", code: str = "this is code block", title: str | None = None
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
    translation_strategies: tuple[
        DocumentContentTranslationStrategy[Any], ...
    ] = tuple(),
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


def create_coding_rule(
    category: str = "category", rule: str = "rule", rationale: str | None = None
) -> CodingRule:
    return CodingRule(category=category, rule=rule, rationale=rationale)


def create_coding_guideline(
    display_name: str = "Test Guideline",
    principles: tuple[str, ...] = ("principle 1", "principle 2"),
    forbidden: tuple[str, ...] = ("forbidden practice 1", "forbidden practice 2"),
    rules: tuple[CodingRule, ...] = (create_coding_rule(),),
) -> CodingGuideline:
    return CodingGuideline(
        display_name=display_name,
        principles=principles,
        rules=rules,
        forbidden=forbidden,
    )


def create_development_faq(
    question: str = "What is this?", answer: str = "This is a test."
) -> DevelopmentFaq:
    return DevelopmentFaq(question=question, answer=answer)


def create_development_known_issue(
    issue: str = "Issue 1", workaround: str = "Workaround 1"
) -> DevelopmentKnownIssue:
    return DevelopmentKnownIssue(issue=issue, workaround=workaround)


def create_development_tip(
    title: str = "Tip 1", description: str = "This is a test tip."
) -> DevelopmentTip:
    return DevelopmentTip(title=title, description=description)


def create_development(
    faq: tuple[DevelopmentFaq, ...] = (create_development_faq(),),
    known_issues: tuple[DevelopmentKnownIssue, ...] = (
        create_development_known_issue(),
    ),
    tips: tuple[DevelopmentTip, ...] = (create_development_tip(),),
) -> Development:
    return Development(faq=faq, known_issues=known_issues, tips=tips)


def create_package_terminology(
    term: str = "Term 1", definition: str = "Definition 1"
) -> PackageTerminology:
    return PackageTerminology(term=term, definition=definition)


def create_package_example(
    title: str = "example1",
    input: str = "input1",
    output: str = "output1",
    explanation: str = "explanation1",
) -> PackageExample:
    return PackageExample(
        title=title, input=input, output=output, explanation=explanation
    )


def create_package_usage(
    situation: str = "situation1", guidance: str = "guidance1"
) -> PackageUsage:
    return PackageUsage(situation=situation, guidance=guidance)


def create_package(
    display_name: str = "Test Package",
    mission: str = "Mission 1",
    policies: tuple[str, ...] = ("Policy 1",),
    constraints: tuple[str, ...] = ("Constraint 1",),
    non_goals: tuple[str, ...] = ("Non-Goal 1",),
    terminology: tuple[PackageTerminology, ...] = (create_package_terminology(),),
    rationale: tuple[str, ...] = ("Rationale 1",),
    usage: tuple[PackageUsage, ...] = (create_package_usage(),),
    examples: tuple[PackageExample, ...] = (create_package_example(),),
) -> Package:
    return Package(
        display_name=display_name,
        mission=mission,
        policies=policies,
        constraints=constraints,
        non_goals=non_goals,
        terminology=terminology,
        rationale=rationale,
        usage=usage,
        examples=examples,
    )


def create_roadmap_item(
    title: str,
    description: str = "Description of the roadmap item",
    priority: Literal["high", "medium", "low"] = "medium",
) -> RoadmapItem:
    return RoadmapItem(title=title, description=description, priority=priority)


def create_roadmap(
    planned: tuple[RoadmapItem, ...] = (create_roadmap_item(title="Planned Item 1"),),
    in_progress: tuple[RoadmapItem, ...] = (
        create_roadmap_item(title="In Progress Item 1"),
    ),
    completed: tuple[RoadmapItem, ...] = (
        create_roadmap_item(title="Completed Item 1"),
    ),
    backlog: tuple[RoadmapItem, ...] = (create_roadmap_item(title="Backlog Item 1"),),
) -> Roadmap:
    return Roadmap(
        planned=planned, in_progress=in_progress, completed=completed, backlog=backlog
    )


def create_installation(
    command: str = "default_command", description: str = "default_description"
) -> Installation:
    return Installation(command=command, description=description)


def create_technical_configuration(
    key: str = "default_key",
    description: str = "default_description",
    default_value: str | None = None,
) -> TechnicalConfiguration:
    return TechnicalConfiguration(
        key=key, description=description, default_value=default_value
    )


def create_dependency(
    package: str = "default_package", description: str = "default_description"
) -> Dependency:
    return Dependency(package=package, description=description)


def create_compatibility(
    name: str = "default_name",
    supported: str = "default_supported",
    description: str | None = None,
) -> Compatibility:
    return Compatibility(name=name, supported=supported, description=description)


def create_technical_migration(
    version: str = "1.0.0",
    description: str = "This is a migration note.",
) -> TechnicalMigration:
    return TechnicalMigration(
        version=version,
        description=description,
    )


def create_technical(
    installation: tuple[Installation, ...] = (create_installation(),),
    configuration: tuple[TechnicalConfiguration, ...] = (
        create_technical_configuration(),
    ),
    dependencies: tuple[Dependency, ...] = (create_dependency(),),
    compatibility: tuple[Compatibility, ...] = (create_compatibility(),),
    migration: tuple[TechnicalMigration, ...] = (create_technical_migration(),),
) -> Technical:
    return Technical(
        installation=installation,
        configuration=configuration,
        dependencies=dependencies,
        compatibility=compatibility,
        migration=migration,
    )


def create_section(
    id: str = "section_id",
    title: str | None = None,
    contents: tuple[DocumentContent, ...] = (create_paragraph(),),
) -> Section:
    return Section(id=id, title=title, contents=contents)


def create_translation_state[T: DocumentContent](
    context: T, validation: ValidationResult
) -> TranslationState[T]:
    return TranslationState(context=context, validation=validation)


def create_section_no_translation() -> SectionNoTranslation:
    return SectionNoTranslation()


def create_section_translation_instruction(
    translation_instruction: str = "Translate this section.",
    translation_strategies: tuple[DocumentContentTranslationStrategy[Any], ...] = (
        paragraph_translation_strategy,
        code_block_translation_strategy,
    ),
) -> SectionTranslationInstruction:
    return SectionTranslationInstruction(
        translation_instruction=translation_instruction,
        translation_strategies=translation_strategies,
    )


def create_section_with_instruction(
    section: Section = create_section(),  # noqa: B008
    translation_instruction: str | None = None,
) -> SectionWithInstruction:
    return SectionWithInstruction(
        section=section, translation_instruction=translation_instruction
    )


def create_built_section(
    section: Section = create_section(),  # noqa: B008
    translation: SectionTranslationDefinition = create_section_no_translation(),  # noqa: B008, E501
) -> BuiltSection:
    return BuiltSection(section=section, translation=translation)


def create_section_location(
    section_id: str, path: tuple[str | int, ...] = (0,)
) -> SectionLocation:
    return SectionLocation(section_id=section_id, path=path)


def create_translation_target(
    id: str,
    source: str = "source_content",
    location: SectionLocation = create_section_location(section_id="section_id"),  # noqa: B008
) -> TranslationTarget:
    return TranslationTarget(id=id, source=source, location=location)


def create_translation_result(
    id: str, translation: str = "translated_content"
) -> TranslationResult:
    return TranslationResult(id=id, translation=translation)


def create_translation_request_item(
    id: str, source: str = "source_content"
) -> TranslationRequestItem:
    return TranslationRequestItem(id=id, source=source)


def create_translation_request(
    target_language: LanguageCodes = "en",
    translations: tuple[TranslationRequestItem, ...] = (),
) -> TranslationRequest:
    return TranslationRequest(
        target_language=target_language, translations=translations
    )


def create_document(
    title: str = "Test Document", sections: tuple[Section, ...] = (create_section(),)
) -> Document:
    return Document(title=title, sections=sections)


def create_knowledge(
    package: Package = create_package(),  # noqa: B008
    technical: Technical = create_technical(),  # noqa: B008
    development: Development = create_development(),  # noqa: B008
    roadmap: Roadmap | None = create_roadmap(),  # noqa: B008
) -> Knowledge:
    return Knowledge(
        package=package, technical=technical, development=development, roadmap=roadmap
    )


def create_document_base_context(
    analysis: PackageAnalysis = create_package_analysis__default(),  # noqa: B008
    concept: PackageConcept = create_package_concept(),  # noqa: B008
    knowledge: Knowledge = create_knowledge(),  # noqa: B008
) -> DocumentBaseContext:
    return DocumentBaseContext(analysis=analysis, concept=concept, knowledge=knowledge)


def create_llm_knowledge(
    package: Package = create_package(),  # noqa: B008
    technical: Technical = create_technical(),  # noqa: B008
    development: Development = create_development(),  # noqa: B008
    roadmap: Roadmap | None = create_roadmap(),  # noqa: B008
    coding_guideline: CodingGuideline = create_coding_guideline(),  # noqa: B008
) -> LlmKnowledge:
    return LlmKnowledge(
        package=package,
        technical=technical,
        development=development,
        roadmap=roadmap,
        coding_guideline=coding_guideline,
    )


def create_llm_context_build_context(
    analysis: PackageAnalysis = create_package_analysis__default(),  # noqa: B008
    concept: PackageConcept = create_package_concept(),  # noqa: B008
    knowledge: LlmKnowledge = create_llm_knowledge(),  # noqa: B008
) -> LlmContextBuildContext:
    return LlmContextBuildContext(
        analysis=analysis, concept=concept, knowledge=knowledge
    )
