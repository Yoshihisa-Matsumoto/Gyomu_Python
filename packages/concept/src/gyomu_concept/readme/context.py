from gyomu_concept.document.context import initialize_document_base_context
from gyomu_concept.error.document import DocumentBuilderError
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.base import DocumentBaseContext
from returns.result import Failure, Result


def initialize_readme_build_context(
    context: ProjectContext, option: ConceptOption | None = None
) -> Result[DocumentBaseContext, DocumentBuilderError]:
    result = initialize_document_base_context(context, option)
    if isinstance(result, Failure):
        return result
    return result.map(lambda r: r.context)
