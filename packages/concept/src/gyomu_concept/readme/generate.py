from gyomu_concept.document.generate import generate_document
from gyomu_concept.error.document import DocumentBuilderError
from gyomu_concept.readme.definition import README_DOCUMENT_DEFINITION
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.option.concept import ConceptOption
from returns.result import Result


async def generate_readme_files(
    project: ProjectContext,
    option: ConceptOption | None = None,
) -> Result[None, DocumentBuilderError]:
    return await generate_document(README_DOCUMENT_DEFINITION, project, option)
