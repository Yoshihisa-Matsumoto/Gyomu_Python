from gyomu_ai_compiler.pipelines.directory_concept.executor.generate import (
    generate_directory_concept,
)
from gyomu_schema.schemas.concept.directory.concept import DirectoryConcept
from gyomu_schema.schemas.concept.directory.input import DirectoryConceptInput
from gyomu_schema.schemas.python.types import ProjectRelativePath
from returns.result import Result

from gyomu_concept.error.concept import ConceptError


async def process_directory_concept(
    package_name: str,
    target_directory: ProjectRelativePath,
    concept: DirectoryConceptInput,
) -> Result[DirectoryConcept, ConceptError]:
    """Processes a directory concept by generating it from input and handling any
    errors.

    Args:
        package_name (str): Name of the package being processed
        target_directory (ProjectRelativePath): Target project-relative path for the
            directory
        concept (DirectoryConceptInput): Input configuration for the directory concept

    Returns:
        Result[DirectoryConcept, ConceptError]: A Result containing the generated
            DirectoryConcept on success or a ConceptError on failure.
    """
    result = await generate_directory_concept(context=concept)
    return result.alt(
        lambda error: ConceptError(
            message="fail to generate Directory Concept",
            file_path=target_directory,
            package_name=package_name,
            phase="directory-summary",
            identity=None,
            details=vars(concept),
        ).chain(error)
    )
