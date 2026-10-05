from gyomu_concept.readme.builder.section.public_api import (
    _build,
    _enabled,
    build_public_api,
)
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.document.content import (
    BulletList,
    BulletListItem,
)
from gyomu_schema.schemas.document.section import (
    Section,
    SectionTranslationInstruction,
    SectionWithInstruction,
)
from returns.result import Success

from packages.schema.schema_test_support.concept_helpers import (
    create_capability_concept,
    create_document_base_context,
    create_package_concept,
)


class TestBuildPublicApi:
    async def test_builds_section(self) -> None:
        context = create_document_base_context(
            concept=create_package_concept(
                capabilities=[
                    create_capability_concept(
                        name="Search",
                        description="Searches documents.",
                    ),
                    create_capability_concept(
                        name="Export",
                        description="Exports documents.",
                    ),
                ]
            )
        )
        option = ConceptOption()

        result = await _build(context, option)

        assert result == Success(
            SectionWithInstruction(
                section=Section(
                    id="public-api",
                    contents=(
                        BulletList(
                            items=(
                                BulletListItem(
                                    translation_id=0,
                                    text="Search - Searches documents.",
                                ),
                                BulletListItem(
                                    translation_id=1,
                                    text="Export - Exports documents.",
                                ),
                            )
                        ),
                    ),
                )
            )
        )

    async def test_builds_empty_list_when_no_capabilities(self) -> None:
        context = create_document_base_context(
            concept=create_package_concept(capabilities=[])
        )

        result = await _build(context)

        assert result == Success(
            SectionWithInstruction(
                section=Section(
                    id="public-api",
                    contents=(BulletList(items=()),),
                )
            )
        )

    def test_enabled(self) -> None:
        context = create_document_base_context()

        assert _enabled(context) is True


class TestBuildPublicApiDefinition:
    def test_definition(self) -> None:
        assert build_public_api.id == "public-api"
        assert build_public_api.enabled is _enabled
        assert build_public_api.build is _build
        assert build_public_api.translation == SectionTranslationInstruction(
            translation_strategies=()
        )
