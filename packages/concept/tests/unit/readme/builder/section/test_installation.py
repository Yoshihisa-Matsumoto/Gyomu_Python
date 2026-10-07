from gyomu_concept.readme.builder.section.installation import (
    _build,
    _enabled,
    build_installation,
)
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.readme.types import ReadmeSectionId
from gyomu_schema.schemas.document.content import CodeBlock, Paragraph
from gyomu_schema.schemas.document.section import (
    Section,
    SectionTranslationInstruction,
    SectionWithInstruction,
)
from pytest_mock import MockerFixture
from returns.result import Success

from packages.schema.schema_test_support.concept_helpers import (
    create_document_base_context,
)


class TestBuildInstallation:
    async def test_builds_section(self, mocker: MockerFixture) -> None:
        context = create_document_base_context()
        option = ConceptOption()

        result = await _build(context, option)

        assert result == Success(
            SectionWithInstruction[ReadmeSectionId](
                section=Section[ReadmeSectionId](
                    id="installation",
                    contents=(
                        Paragraph(text="Install using uv."),
                        CodeBlock(
                            language="bash",
                            code=f"uv add {context.analysis.package.name}",
                        ),
                    ),
                )
            )
        )

    async def test_uses_package_name_from_context(self, mocker: MockerFixture) -> None:
        context = create_document_base_context()

        result = await _build(context)

        assert result.unwrap().section.contents[1] == CodeBlock(
            language="bash",
            code=f"uv add {context.analysis.package.name}",
        )

    def test_enabled(self) -> None:
        context = create_document_base_context()

        assert _enabled(context) is True


class TestBuildInstallationDefinition:
    def test_definition(self) -> None:
        assert build_installation.id == "installation"
        assert build_installation.enabled is _enabled
        assert build_installation.build is _build
        assert build_installation.translation == SectionTranslationInstruction(
            translation_strategies=()
        )
