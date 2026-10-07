from gyomu_concept.readme.builder.section.license import (
    _build,
    _enabled,
    build_license,
)
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.readme.types import ReadmeSectionId
from gyomu_schema.schemas.document.content import Paragraph
from gyomu_schema.schemas.document.section import (
    Section,
    SectionNoTranslation,
    SectionWithInstruction,
)
from pytest_mock import MockerFixture
from returns.result import Success

from packages.schema.schema_test_support.concept_helpers import (
    create_document_base_context,
)


class TestBuildLicense:
    async def test_builds_section(self, mocker: MockerFixture) -> None:
        context = create_document_base_context()
        option = ConceptOption()

        result = await _build(context, option)

        assert result == Success(
            SectionWithInstruction[ReadmeSectionId](
                section=Section[ReadmeSectionId](
                    id="license",
                    contents=(Paragraph(text=context.analysis.package.license),),
                )
            )
        )

    def test_enabled(self) -> None:
        context = create_document_base_context()

        assert _enabled(context) is True


class TestBuildLicenseDefinition:
    def test_definition(self) -> None:
        assert build_license.id == "license"
        assert build_license.enabled is _enabled
        assert build_license.build is _build
        assert build_license.translation == SectionNoTranslation()
