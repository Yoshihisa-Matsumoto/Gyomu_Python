from gyomu_concept.llm_context.builder.section.package_responsibilities import (
    _build,
    _enabled,
    build_package_responsibilities,
)
from gyomu_schema.schemas.concept.llm_context.types import LlmContextSectionId
from gyomu_schema.schemas.document.content import BulletList, BulletListItem
from gyomu_schema.schemas.document.section import (
    Section,
    SectionNoTranslation,
    SectionWithInstruction,
)
from returns.result import Success

from packages.schema.schema_test_support.concept_helpers import (
    create_llm_context_build_context,
    create_package_concept,
)


class TestBuildPackageResponsibilities:
    async def test_builds_section(self) -> None:
        responsibilities = [
            "Manage package configuration",
            "Provide document generation",
            "Coordinate AI execution",
        ]
        context = create_llm_context_build_context(
            concept=create_package_concept(
                responsibilities=responsibilities,
            ),
        )

        result = await _build(context)

        assert result == Success(
            SectionWithInstruction[LlmContextSectionId](
                section=Section[LlmContextSectionId](
                    id="package-responsibilities",
                    contents=(
                        BulletList(
                            items=(
                                BulletListItem(
                                    translation_id=0,
                                    text="Manage package configuration",
                                ),
                                BulletListItem(
                                    translation_id=1,
                                    text="Provide document generation",
                                ),
                                BulletListItem(
                                    translation_id=2,
                                    text="Coordinate AI execution",
                                ),
                            ),
                        ),
                    ),
                ),
            )
        )

    async def test_builds_empty_list_when_no_responsibilities(self) -> None:
        context = create_llm_context_build_context(
            concept=create_package_concept(responsibilities=[]),
        )

        result = await _build(context)

        assert result == Success(
            SectionWithInstruction[LlmContextSectionId](
                section=Section[LlmContextSectionId](
                    id="package-responsibilities",
                    contents=(BulletList(items=()),),
                ),
            )
        )

    def test_enabled(self) -> None:
        context = create_llm_context_build_context()

        assert _enabled(context) is True


class TestBuildPackageResponsibilitiesDefinition:
    def test_definition(self) -> None:
        assert build_package_responsibilities.id == "package-responsibilities"
        assert build_package_responsibilities.enabled is _enabled
        assert build_package_responsibilities.build is _build
        assert build_package_responsibilities.translation == SectionNoTranslation()
