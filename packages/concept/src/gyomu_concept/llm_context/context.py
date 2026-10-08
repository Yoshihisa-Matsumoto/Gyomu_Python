from gyomu_infra.filesystem.file_io import read_yaml
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.error.base import BaseError
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.llm_context.input import (
    LlmContextBuildContext,
    LlmKnowledge,
)
from gyomu_schema.schemas.knowledge.coding_guideline import (
    CodingGuideline,
    merge_coding_guideline,
)
from gyomu_schema.utility.context import caller_context
from returns.result import Failure, Result, Success

from gyomu_concept.document.context import initialize_document_base_context
from gyomu_concept.document.path.knowledge import (
    get_knowledge_path,
    get_root_knowledge_path,
)
from gyomu_concept.error.document import DocumentBuilderError


def _wrap_error(
    error: BaseError, caller: str, context: ProjectContext
) -> DocumentBuilderError:
    return DocumentBuilderError(
        message="fail to initialize llm context base context",
        phase="context-build",
        package_name=context.config.name,
        context=caller,
    ).chain(error)


def initialize_llm_context_build_context(
    context: ProjectContext, option: ConceptOption | None = None
) -> Result[LlmContextBuildContext, DocumentBuilderError]:
    caller = caller_context()
    base_result = initialize_document_base_context(context, option)
    if isinstance(base_result, Failure):
        return base_result
    base_context = base_result.unwrap().context

    root_knowledge_path_result = get_root_knowledge_path(context, option)
    if isinstance(root_knowledge_path_result, Failure):
        return root_knowledge_path_result
    root_knowledge_path = root_knowledge_path_result.unwrap()

    root_coding_guideline_result = read_yaml(
        path=root_knowledge_path / "Coding.yaml", model_type=CodingGuideline
    )
    if isinstance(root_coding_guideline_result, Failure):
        return root_coding_guideline_result.alt(
            lambda error: _wrap_error(error, caller, context)
        )
    root_coding_guideline = root_coding_guideline_result.unwrap()
    knowledge_path = get_knowledge_path(context, option)

    local_coding_guideline_path = knowledge_path / "Coding.yaml"
    coding_guideline = None
    if local_coding_guideline_path.exists():
        coding_guideline_result = read_yaml(
            path=local_coding_guideline_path, model_type=CodingGuideline
        )

        if isinstance(coding_guideline_result, Failure):
            return coding_guideline_result.alt(
                lambda error: _wrap_error(error, caller, context)
            )
        coding_guideline = coding_guideline_result.unwrap()

    merged_coding_guideline = merge_coding_guideline(
        root_coding_guideline, coding_guideline
    )

    return Success(
        LlmContextBuildContext(
            analysis=base_context.analysis,
            concept=base_context.concept,
            knowledge=LlmKnowledge(
                package=base_context.knowledge.package,
                technical=base_context.knowledge.technical,
                development=base_context.knowledge.development,
                roadmap=base_context.knowledge.roadmap,
                coding_guideline=merged_coding_guideline,
            ),
        )
    )
