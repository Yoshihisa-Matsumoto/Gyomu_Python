from gyomu_ai_compiler.pipelines.document.executor.item import build_section_item
from gyomu_ai_compiler.pipelines.readme.prompt import readme_prompt_provider
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.base import DocumentBaseContext, Knowledge
from gyomu_schema.schemas.concept.readme.types import ReadmeSectionId
from gyomu_schema.schemas.document.content import Paragraph
from gyomu_schema.schemas.document.section import (
    Section,
    SectionTranslationInstruction,
    SectionWithInstruction,
)
from gyomu_schema.utility.context import caller_context
from returns.result import Failure, Result, Success

from gyomu_concept.document.builder.section import SectionBuilder
from gyomu_concept.error.document import DocumentBuilderError

_section_id: ReadmeSectionId = "dependencies"
"""Identifier for the dependencies section in the README.

None
"""


async def _build(
    context: DocumentBaseContext[Knowledge], option: ConceptOption | None = None
) -> Result[SectionWithInstruction[ReadmeSectionId], DocumentBuilderError]:
    """Builds the dependencies section for the README document.

    None

    Args:
        context (DocumentBaseContext): The document base context.
        option (ConceptOption | None): Optional concept options.

    Returns:
        Result[SectionWithInstruction[ReadmeSectionId], DocumentBuilderError]: A result
            containing the built dependencies section with instruction or a builder
            error.
    """

    dependencies_result = await build_section_item(
        _section_id, context, readme_prompt_provider
    )
    if isinstance(dependencies_result, Failure):
        return dependencies_result.alt(
            lambda error: DocumentBuilderError(
                "fail to build dependencies",
                package_name=context.analysis.package.name,
                phase="section-build",
                section_id=_section_id,
                context=caller_context(),
            ).chain(error)
        )
    return Success(
        SectionWithInstruction[ReadmeSectionId](
            section=Section[ReadmeSectionId](
                id=_section_id,
                contents=(Paragraph(text=dependencies_result.unwrap()),),
            )
        )
    )


def _enabled(_: DocumentBaseContext[Knowledge]) -> bool:
    """Determines whether the dependencies section is enabled.

    None

    Args:
        _ (DocumentBaseContext): The document base context.

    Returns:
        bool: True as the dependencies section is always enabled.
    """
    return True


build_dependencies: SectionBuilder[ReadmeSectionId, DocumentBaseContext[Knowledge]] = (
    SectionBuilder[ReadmeSectionId, DocumentBaseContext[Knowledge]](
        id=_section_id,
        translation=SectionTranslationInstruction(translation_strategies=()),
        enabled=_enabled,
        build=_build,
    )
)
"""Section builder for generating the dependencies section of the README.

None
"""
