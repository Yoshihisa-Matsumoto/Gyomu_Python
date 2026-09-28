from gyomu_ai_compiler.pipelines.directory_concept.executor.generate import (
    generate_directory_concept,
)
from gyomu_concept.error.concept import ConceptError
from gyomu_schema.schemas.concept.directory.input import DirectoryConceptInput
from gyomu_schema.schemas.python.types import ProjectRelativePath


async def process_directory_concept(
    package_name: str,
    target_directory: ProjectRelativePath,
    concept: DirectoryConceptInput,
):
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
