from gyomu_concept.document.path.knowledge import get_knowledge_path
from gyomu_concept.error.document import DocumentBuilderError
from gyomu_concept.package.analysis import build_package_analysis
from gyomu_concept.package.internal.load import load_package_concept
from gyomu_concept.package.internal.path import get_package_concept_path
from gyomu_infra.filesystem.file_io import read_yaml
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.error.base import BaseError
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.base import DocumentBaseContext, Knowledge
from gyomu_schema.schemas.knowledge.development import Development
from gyomu_schema.schemas.knowledge.package import Package
from gyomu_schema.schemas.knowledge.roadmap import Roadmap
from gyomu_schema.schemas.knowledge.technical import Technical
from gyomu_schema.schemas.types import FullPath
from gyomu_schema.utility.context import caller_context
from pydantic import BaseModel
from returns.result import Failure, Result, Success


class DocumentBaseContextResult(BaseModel):
    context: DocumentBaseContext
    knowledge_path: FullPath


def _wrap_error(
    error: BaseError, caller: str, context: ProjectContext
) -> DocumentBuilderError:
    return DocumentBuilderError(
        message="fail to initialize document base context",
        phase="context-build",
        package_name=context.config.name,
        context=caller,
    ).chain(error)


def initialize_document_base_context(
    context: ProjectContext, option: ConceptOption | None = None
) -> Result[DocumentBaseContextResult, DocumentBuilderError]:
    caller = caller_context()
    package_analysis_result = build_package_analysis(context, option)
    if isinstance(package_analysis_result, Failure):
        return package_analysis_result.alt(
            lambda error: _wrap_error(error, caller, context)
        )
    analysis = package_analysis_result.unwrap()

    concept_result = load_package_concept(context, option)
    if isinstance(concept_result, Failure):
        return concept_result.alt(lambda error: _wrap_error(error, caller, context))
    concept = concept_result.unwrap()
    if concept is None:
        return Failure(
            DocumentBuilderError(
                message="Package Concept not found",
                file_path=get_package_concept_path(context, option),
                package_name=context.config.name,
                phase="context-build",
                context=caller,
            )
        )

    knowledge_path = get_knowledge_path(context, option)

    package_knowledge_result = read_yaml(
        path=knowledge_path / "Package.yaml", model_type=Package
    )
    if isinstance(package_knowledge_result, Failure):
        return package_knowledge_result.alt(
            lambda error: _wrap_error(error, caller, context)
        )
    package_knowledge = package_knowledge_result.unwrap()

    development_result = read_yaml(
        path=knowledge_path / "Development.yaml", model_type=Development
    )
    if isinstance(development_result, Failure):
        return development_result.alt(lambda error: _wrap_error(error, caller, context))
    development = development_result.unwrap()

    technical_result = read_yaml(
        path=knowledge_path / "Technical.yaml", model_type=Technical
    )
    if isinstance(technical_result, Failure):
        return technical_result.alt(lambda error: _wrap_error(error, caller, context))
    technical = technical_result.unwrap()

    roadmap_result = read_yaml(path=knowledge_path / "Roadmap.yaml", model_type=Roadmap)
    if isinstance(roadmap_result, Failure):
        return roadmap_result.alt(lambda error: _wrap_error(error, caller, context))
    roadmap = roadmap_result.unwrap()

    return Success(
        DocumentBaseContextResult(
            context=DocumentBaseContext(
                analysis=analysis,
                concept=concept,
                knowledge=Knowledge(
                    package=package_knowledge,
                    development=development,
                    technical=technical,
                    roadmap=roadmap,
                ),
            ),
            knowledge_path=knowledge_path,
        )
    )
