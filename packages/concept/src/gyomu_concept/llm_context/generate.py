from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.option.concept import ConceptOption
from returns.result import Result

from gyomu_concept.document.generate import generate_document
from gyomu_concept.error.document import DocumentBuilderError
from gyomu_concept.llm_context.definition import LLMCONTEXT_DOCUMENT_DEFINITION


async def generate_llm_context_files(
    project: ProjectContext,
    option: ConceptOption | None = None,
) -> Result[None, DocumentBuilderError]:
    return await generate_document(LLMCONTEXT_DOCUMENT_DEFINITION, project, option)
