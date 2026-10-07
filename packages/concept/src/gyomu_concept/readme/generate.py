from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.option.concept import ConceptOption
from returns.result import Result

from gyomu_concept.document.generate import generate_document
from gyomu_concept.error.document import DocumentBuilderError
from gyomu_concept.readme.definition import README_DOCUMENT_DEFINITION


async def generate_readme_files(
    project: ProjectContext,
    option: ConceptOption | None = None,
) -> Result[None, DocumentBuilderError]:
    """Generates README files for a project.

    Generates README files for the project based on the provided concept options.

    Args:
        project (ProjectContext): The project context containing project metadata and
            structure.
        option (ConceptOption | None): Optional configuration options for the concept
            generation.

    Returns:
        Result[None, DocumentBuilderError]: A Result containing None on success, or a
            DocumentBuilderError on failure.
    """
    return await generate_document(README_DOCUMENT_DEFINITION, project, option)
