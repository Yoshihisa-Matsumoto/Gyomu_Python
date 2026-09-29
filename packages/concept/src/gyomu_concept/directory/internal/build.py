from gyomu_concept.directory.internal.file_summary import build_file_summary_record
from gyomu_concept.directory.internal.load import load_directory_concept
from gyomu_concept.directory.internal.process import process_directory_concept
from gyomu_concept.directory.internal.save import save_directory_concept
from gyomu_concept.directory.types import BuildResult
from gyomu_concept.error.concept import ConceptError
from gyomu_infra.logger import logger
from gyomu_python_analysis.analysis.load_file_context import load_file_analysis_context
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.directory.input import (
    DirectoryConceptInput,
    SubDirectoryInput,
)
from gyomu_schema.schemas.python.types import (
    DirectoryRelativePath,
    ProjectRelativePath,
)
from gyomu_schema.schemas.types import FullPath
from returns.result import Failure, Result, Success


async def build_directory_concept_from_path(
    context: ProjectContext,
    target_directory: FullPath,
    option: ConceptOption | None = None,
) -> Result[BuildResult, ConceptError]:
    target_directory_relative_path = ProjectRelativePath(
        target_directory.relative_to(context.project_root)
    )

    entries = sorted(
        target_directory.iterdir(),
        key=lambda path: path.name,
    )

    folders = [path for path in entries if path.is_dir() and path.name != "__pycache__"]

    files = [
        path
        for path in entries
        if path.is_file()
        and ProjectRelativePath(path.relative_to(context.project_root))
        in context.included_files
    ]

    is_changed = _is_directory_changed(
        target_directory_relative_path=target_directory_relative_path,
        option=option,
    )

    if not is_changed:
        loaded = load_directory_concept(
            context=context,
            target_directory=target_directory_relative_path,
            option=option,
        )

        if isinstance(loaded, Success):
            concept = loaded.unwrap()

            if concept is not None:
                return Success(
                    BuildResult(
                        concept=concept,
                        changed=False,
                    )
                )

    directory_concepts: list[SubDirectoryInput] = []

    for folder in folders:
        directory_result = await build_directory_concept_from_path(
            context=context,
            target_directory=folder,
            option=option,
        )

        if isinstance(directory_result, Failure):
            return directory_result

        build_result = directory_result.unwrap()

        if build_result.changed:
            is_changed = True

        directory_concepts.append(
            SubDirectoryInput(
                path=DirectoryRelativePath(folder.relative_to(target_directory)),
                concept=build_result.concept,
            )
        )

    file_summaries = []

    for file in files:
        file_relative_path = ProjectRelativePath(file.relative_to(context.project_root))

        file_result = load_file_analysis_context(
            context=context,
            file_path=file_relative_path,
        )

        if isinstance(file_result, Failure):
            return Failure(
                ConceptError(
                    message="fail to load file analysis context",
                    file_path=file_relative_path,
                    package_name=context.config.name,
                    phase="directory-summary",
                    identity=None,
                ).chain(file_result.failure())
            )
        file_summaries.append(
            build_file_summary_record(
                project_context=context,
                file_context=file_result.unwrap(),
            )
        )

    input_context = DirectoryConceptInput(
        files=tuple(file_summaries),
        sub_directories=tuple(directory_concepts),
    )
    logger.info(f"create directory concept: {target_directory_relative_path}")
    generated = await process_directory_concept(
        package_name=context.config.name,
        target_directory=target_directory_relative_path,
        concept=input_context,
    )

    if isinstance(generated, Failure):
        return generated

    concept = generated.unwrap()

    saved = save_directory_concept(
        context=context,
        target_directory=target_directory_relative_path,
        concept=concept,
        option=option,
    )

    if isinstance(saved, Failure):
        return saved

    return Success(
        BuildResult(
            concept=concept,
            changed=is_changed,
        )
    )


def _is_directory_changed(
    target_directory_relative_path: ProjectRelativePath,
    option: ConceptOption | None,
) -> bool:
    if option is None or option.changed_files is None:
        return False

    return any(
        changed_file.project_relative_path == target_directory_relative_path
        or changed_file.project_relative_path.is_relative_to(
            target_directory_relative_path
        )
        for changed_file in option.changed_files
    )
