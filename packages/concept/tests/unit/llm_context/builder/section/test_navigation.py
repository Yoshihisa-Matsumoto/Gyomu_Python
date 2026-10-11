from gyomu_concept.llm_context.builder.section.navigation import (
    _build,
    _enabled,
    build_navigation,
)
from gyomu_schema.schemas.concept.llm_context.types import LlmContextSectionId
from gyomu_schema.schemas.document.content import (
    BulletList,
    BulletListItem,
    Paragraph,
)
from gyomu_schema.schemas.document.section import (
    Section,
    SectionNoTranslation,
    SectionWithInstruction,
)
from returns.result import Success

from packages.schema.schema_test_support.concept_helpers import (
    create_llm_context_build_context,
)


class TestBuildNavigation:
    async def test_builds_section(self) -> None:
        context = create_llm_context_build_context()

        result = await _build(context)

        assert result == Success(
            SectionWithInstruction[LlmContextSectionId](
                section=Section[LlmContextSectionId](
                    id="navigation",
                    contents=(
                        Paragraph(
                            text=(
                                "This document provides a high-level overview of the "
                                "package concept, responsibilities, and design decisions."  # noqa: E501
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
                            text=(
                                "When modifying this package, review the relevant "
                                "documentation before making changes to preserve the "
                                "intended responsibilities and architectural boundaries.\n"  # noqa: E501
                            )
                        ),
                    ),
                ),
            )
        )

    def test_enabled(self) -> None:
        context = create_llm_context_build_context()

        assert _enabled(context) is True


class TestBuildNavigationDefinition:
    def test_definition(self) -> None:
        assert build_navigation.id == "navigation"
        assert build_navigation.enabled is _enabled
        assert build_navigation.build is _build
        assert build_navigation.translation == SectionNoTranslation()
