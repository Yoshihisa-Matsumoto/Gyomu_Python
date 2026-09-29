from dataclasses import dataclass

from gyomu_concept.directory.internal.file_summary import build_file_summary_record
from gyomu_concept.directory.internal.load import load_directory_concept
from gyomu_concept.error.concept import ConceptError
from gyomu_concept.package.internal.dependency import collect_dependencies
from gyomu_infra.logger import logger
from gyomu_python_analysis.analysis.load_file_context import load_file_analysis_context
from gyomu_python_analysis.analysis.workspace import (
    find_root,
    initialize_workspace_context,
)
from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.file_summary import FileSummary
from gyomu_schema.schemas.concept.package.analysis import (
    DirectoryAnalysis,
    DirectoryAnalysisFact,
    PackageAnalysis,
    PyProjectAnalysis,
)
from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.python.visibility import Visibility
from gyomu_schema.utility.context import caller_context
from returns.result import Failure, Result, Success


def build_package_analysis(
    context: ProjectContext, option: ConceptOption | None = None
) -> Result[PackageAnalysis, ConceptError]:
    caller = caller_context()
    root_result = find_root(context.project_root)
    if isinstance(root_result, Failure):
        logger.error_object(root_result.failure())
        return root_result.alt(
            lambda error: ConceptError(
                message="fail to build package analysis",
                file_path=context.project_root,
                package_name=context.config.name,
                phase="package-concept",
                identity=None,
                context=caller,
            ).chain(error)
        )
    workspace = root_result.unwrap()
    workspace_result = initialize_workspace_context(workspace)
    if isinstance(workspace_result, Failure):
        logger.error_object(workspace_result.failure())
        return workspace_result.alt(
            lambda error: ConceptError(
                message="fail to build package analysis",
                file_path=context.project_root,
                package_name=context.config.name,
                phase="package-concept",
                identity=None,
                context=caller,
            ).chain(error)
        )
    workspace_context = workspace_result.unwrap()

    aggregate_result = _aggregate_file_and_load_directory(context, option)
    if isinstance(aggregate_result, Failure):
        logger.error_object(aggregate_result.failure())
        return aggregate_result.alt(
            lambda error: (
                error
                if isinstance(error, ConceptError)
                else ConceptError(
                    "fail to build package analysis",
                    file_path=context.project_root,
                    package_name=context.config.name,
                    phase="package-concept",
                    identity=None,
                    context=caller,
                ).chain(error)
            )
        )
    aggregation = aggregate_result.unwrap()
    license = context.config.get_attribute("project.license", str)

    return Success(
        PackageAnalysis(
            package=PyProjectAnalysis(
                name=context.config.name,
                description=context.config.description,
                version=context.config.version,
                license=license or "",
            ),
            dependencies=collect_dependencies(context, workspace_context),
            directories=tuple(aggregation.dirs.values()),
            public_files=tuple(aggregation.files.values()),
        )
    )


@dataclass(frozen=True)
class AggregateFileAndDirectories:
    files: dict[ProjectRelativePath, FileSummary]
    dirs: dict[ProjectRelativePath, DirectoryAnalysis]


def _aggregate_file_and_load_directory(
    context: ProjectContext, option: ConceptOption | None
) -> Result[AggregateFileAndDirectories, ConceptError | AnalysisError]:
    files: dict[ProjectRelativePath, FileSummary] = {}
    dirs: dict[ProjectRelativePath, DirectoryAnalysis] = {}

    for file_path in context.included_files:
        directory_path = file_path.parent
        if directory_path not in dirs:
            directory_result = load_directory_concept(
                context=context, target_directory=directory_path, option=option
            )
            if isinstance(directory_result, Failure):
                return directory_result
            directory_concept = directory_result.unwrap()
            if directory_concept:
                dirs[directory_path] = DirectoryAnalysis(
                    path=directory_path,
                    concept=directory_concept,
                    fact=DirectoryAnalysisFact(
                        public_symbol_count=0, file_count=0, total_symbol_count=0
                    ),
                )

        file_result = load_file_analysis_context(
            context=context,
            file_path=file_path,
        )

        if isinstance(file_result, Failure):
            return file_result

        file_context = file_result.unwrap()
        files[file_path] = build_file_summary_record(
            project_context=context,
            file_context=file_context,
        )
        file_fact = _get_file_analysis_fact(file_context)

        directory_entry = dirs.get(directory_path)
        if directory_entry:
            directory_entry.fact.add(file_fact)

    return Success(AggregateFileAndDirectories(files=files, dirs=dirs))


def _get_file_analysis_fact(file_context: FileAnalysisContext) -> DirectoryAnalysisFact:
    total_symbols = len(file_context.analysis.symbols)
    public_symbols = len(
        [
            item
            for item in file_context.analysis.symbols
            if item.visibility == Visibility.PUBLIC
        ]
    )
    return DirectoryAnalysisFact(
        file_count=1,
        public_symbol_count=public_symbols,
        total_symbol_count=total_symbols,
    )
