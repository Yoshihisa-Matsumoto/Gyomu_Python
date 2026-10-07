from gyomu_schema.schemas.document.section import (
    Section,
    SectionLocation,
    SectionWithInstruction,
    TranslationRequest,
    TranslationResult,
    TranslationState,
    TranslationTarget,
)
from gyomu_schema.utility.serialization import _assert_json_round_trip

from packages.schema.schema_test_support.concept_helpers import (
    create_paragraph,
    create_section,
    create_section_location,
    create_section_with_instruction,
    create_translation_request,
    create_translation_request_item,
    create_translation_result,
    create_translation_state,
    create_translation_target,
    create_validation_issue,
    create_validation_result,
)


class TestSection:
    def test(self) -> None:
        _assert_json_round_trip(Section, create_section())


class TestTranslationState:
    def test(self) -> None:
        _assert_json_round_trip(
            TranslationState,
            create_translation_state(
                context=create_paragraph(),
                validation=create_validation_result(
                    issues=(create_validation_issue(),)
                ),
            ),
        )


class TestSectionWithInstruction:
    def test(self) -> None:
        _assert_json_round_trip(
            SectionWithInstruction, create_section_with_instruction()
        )


class TestSectionLocation:
    def test(self) -> None:
        _assert_json_round_trip(
            SectionLocation, create_section_location(section_id="section-id")
        )


class TestTranslationTarget:
    def test(self) -> None:
        _assert_json_round_trip(
            TranslationTarget, create_translation_target(id="section-id")
        )


class TestTranslationResult:
    def test(self) -> None:
        _assert_json_round_trip(
            TranslationResult, create_translation_result(id="section-id")
        )


class TestTranslationRequest:
    def test(self) -> None:
        _assert_json_round_trip(
            TranslationRequest,
            create_translation_request(
                translations=(create_translation_request_item(id="item-id"),)
            ),
        )
