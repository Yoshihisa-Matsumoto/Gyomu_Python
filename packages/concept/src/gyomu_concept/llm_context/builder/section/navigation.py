from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.llm_context.input import LlmContextBuildContext
from gyomu_schema.schemas.concept.llm_context.types import LlmContextSectionId
from gyomu_schema.schemas.document.content import BulletList, BulletListItem, Paragraph
from gyomu_schema.schemas.document.section import (
    Section,
    SectionNoTranslation,
    SectionWithInstruction,
)
from returns.result import Result, Success

from gyomu_concept.document.builder.section import SectionBuilder
from gyomu_concept.error.document import DocumentBuilderError

_section_id: LlmContextSectionId = "navigation"


async def _build(
    context: LlmContextBuildContext, option: ConceptOption | None = None
) -> Result[SectionWithInstruction[LlmContextSectionId], DocumentBuilderError]:

    return Success(
        SectionWithInstruction[LlmContextSectionId](
            section=Section[LlmContextSectionId](
                id=_section_id,
                contents=(
                    Paragraph(
                        text=(
                            "This document provides a high-level overview of the "
                            "package concept, responsibilities, and design decisions."
                            "\n\nFor more detailed information, "
                            "refer to the following documents:\n\n"
                        )
                    ),
                    BulletList(
                        items=(
                            BulletListItem(
                                translation_id=1,
                                text=(
                                    "**Architecture Documentation**\n"
                                    "  Describes the internal architecture, "
                                    "major components, dependencies, "
                                    "and design decisions of this package.\n"
                                ),
                            ),
                            BulletListItem(
                                translation_id=2,
                                text=(
                                    "**API Reference**\n"
                                    "  Describes public APIs, exported modules, "
                                    "and usage patterns.\n"
                                ),
                            ),
                            BulletListItem(
                                translation_id=3,
                                text=(
                                    "**Technical Documentation**\n"
                                    "  Describes technical details, configuration, "
                                    "dependencies, and implementation-specific "
                                    "information.\n"
                                ),
                            ),
                            BulletListItem(
                                translation_id=4,
                                text=(
                                    "**Development Guide**\n"
                                    "  Describes development workflows, coding "
                                    "conventions, testing strategies, "
                                    "and contribution guidelines.\n"
                                ),
                            ),
                            BulletListItem(
                                translation_id=5,
                                text=(
                                    "**Project Knowledge**\n"
                                    "  Contains additional knowledge maintained by "
                                    "developers, including constraints, rationale, "
                                    "terminology, and operational guidelines.\n"
                                ),
                            ),
                        )
                    ),
                    Paragraph(
                        text="When modifying this package, review the relevant "
                        "documentation before making changes to preserve the intended "
                        "responsibilities and architectural boundaries.\n"
                    ),
                ),
            )
        )
    )


def _enabled(context: LlmContextBuildContext) -> bool:
    return True


build_navigation: SectionBuilder[LlmContextSectionId, LlmContextBuildContext] = (
    SectionBuilder[LlmContextSectionId, LlmContextBuildContext](
        id=_section_id,
        translation=SectionNoTranslation(),
        enabled=_enabled,
        build=_build,
    )
)
