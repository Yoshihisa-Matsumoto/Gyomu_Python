from gyomu_schema.schemas.document.section import RetryContextArg, SectionNoTranslation
from gyomu_schema.schemas.document.translation.bullet_list import (
    _find_bullet_list_item,
    _find_bullet_list_item_from_item,
    _merge_validation_result,
    _retrieve_valid_id_list,
    _retrieve_valid_id_list_item,
    _update_bullet_list_retry_context,
)
from returns.result import Success

from packages.schema.schema_test_support.concept_helpers import (
    create_bullet_list,
    create_bullet_list_item,
    create_validation_issue,
    create_validation_result,
)


class TestFindBulletListItemFromItem:
    def test_from_item_returns_matching_item(self) -> None:
        item = create_bullet_list_item(translation_id=1)

        result = _find_bullet_list_item_from_item(item, 1)

        assert result is item

    def test_from_item_returns_none_when_not_found(self) -> None:
        item = create_bullet_list_item(translation_id=1)

        result = _find_bullet_list_item_from_item(item, 2)

        assert result is None

    def test_from_item_finds_nested_item(self) -> None:
        child = create_bullet_list_item(translation_id=2)
        parent = create_bullet_list_item(
            translation_id=1,
            children=(child,),
        )

        result = _find_bullet_list_item_from_item(parent, 2)

        assert result is child

    def test_from_item_finds_deeply_nested_item(self) -> None:
        grandchild = create_bullet_list_item(translation_id=3)
        child = create_bullet_list_item(
            translation_id=2,
            children=(grandchild,),
        )
        parent = create_bullet_list_item(
            translation_id=1,
            children=(child,),
        )

        result = _find_bullet_list_item_from_item(parent, 3)

        assert result is grandchild


class TestFindBulletListItem:
    def test_returns_matching_top_level_item(self) -> None:
        item = create_bullet_list_item(translation_id=1)
        bullet_list = create_bullet_list((item,))

        result = _find_bullet_list_item(bullet_list, 1)

        assert result is item

    def test_finds_nested_item(self) -> None:
        child = create_bullet_list_item(translation_id=2)
        parent = create_bullet_list_item(
            translation_id=1,
            children=(child,),
        )
        bullet_list = create_bullet_list((parent,))

        result = _find_bullet_list_item(bullet_list, 2)

        assert result is child

    def test_returns_none_when_not_found(self) -> None:
        bullet_list = create_bullet_list((create_bullet_list_item(translation_id=1),))

        result = _find_bullet_list_item(bullet_list, 999)

        assert result is None


class TestRetrieveValidIdListItem:
    def test_returns_item_id_when_valid(self) -> None:
        item = create_bullet_list_item(translation_id=1)

        result = _retrieve_valid_id_list_item([], item)

        assert result == [1]

    def test_excludes_invalid_item(self) -> None:
        item = create_bullet_list_item(translation_id=1)

        result = _retrieve_valid_id_list_item([1], item)

        assert result == []

    def test_retrieves_nested_valid_ids(self) -> None:
        child = create_bullet_list_item(translation_id=2)
        parent = create_bullet_list_item(
            translation_id=1,
            children=(child,),
        )

        result = _retrieve_valid_id_list_item([], parent)

        assert result == [1, 2]

    def test_retrieves_valid_child_when_parent_is_invalid(self) -> None:
        child = create_bullet_list_item(translation_id=2)
        parent = create_bullet_list_item(
            translation_id=1,
            children=(child,),
        )

        result = _retrieve_valid_id_list_item([1], parent)

        assert result == [2]


class TestRetrieveValidIdList:
    def test_retrieve_valid_id_list_returns_all_valid_ids(self) -> None:
        bullet_list = create_bullet_list(
            (
                create_bullet_list_item(translation_id=1),
                create_bullet_list_item(translation_id=2),
            )
        )
        validation = create_validation_result()

        result = _retrieve_valid_id_list(validation, bullet_list)

        assert result == (1, 2)

    def test_retrieve_valid_id_list_excludes_invalid_ids(self) -> None:
        bullet_list = create_bullet_list(
            (
                create_bullet_list_item(translation_id=1),
                create_bullet_list_item(translation_id=2),
            )
        )
        validation = create_validation_result(
            issues=(create_validation_issue(translation_id=2),)
        )

        result = _retrieve_valid_id_list(validation, bullet_list)

        assert result == (1,)

    def test_retrieve_valid_id_list_includes_nested_valid_ids(self) -> None:
        child = create_bullet_list_item(translation_id=2)
        parent = create_bullet_list_item(
            translation_id=1,
            children=(child,),
        )
        bullet_list = create_bullet_list((parent,))
        validation = create_validation_result()

        result = _retrieve_valid_id_list(validation, bullet_list)

        assert result == (1, 2)


class TestMergeValidationResult:
    def test_returns_current_when_previous_is_none(
        self,
    ) -> None:
        current_validation = create_validation_result(
            issues=(create_validation_issue(translation_id=1),)
        )
        context = create_bullet_list((create_bullet_list_item(translation_id=1),))

        result = _merge_validation_result(
            current_validation,
            None,
            context,
        )

        assert result is current_validation

    def test_keeps_current_issues_for_previous_invalid_ids(self) -> None:
        context = create_bullet_list(
            (
                create_bullet_list_item(translation_id=1),
                create_bullet_list_item(translation_id=2),
            )
        )
        previous_validation = create_validation_result(
            issues=(create_validation_issue(translation_id=1),)
        )
        current_validation = create_validation_result(
            issues=(
                create_validation_issue(translation_id=1),
                create_validation_issue(translation_id=2),
            )
        )

        result = _merge_validation_result(
            current_validation,
            previous_validation,
            context,
        )

        assert result.is_valid is False
        assert len(result.issues) == 1
        assert result.issues[0].translation_id == 2


class TestUpdateBulletListRetryContext:
    def test_returns_success_when_validation_is_valid(
        self,
    ) -> None:
        original_context = create_bullet_list(
            (create_bullet_list_item(translation_id=1, text="Hello"),)
        )
        translated_context = create_bullet_list(
            (create_bullet_list_item(translation_id=1, text="こんにちは"),)
        )
        validation = create_validation_result()

        result = _update_bullet_list_retry_context(
            RetryContextArg(
                section_id="section-1",
                section_definition=SectionNoTranslation(),
                original_context=original_context,
                translated_context=translated_context,
                current_validation=validation,
                previous_validation=None,
            )
        )

        assert isinstance(result, Success)

        state = result.unwrap()
        assert state.context is original_context
        assert state.validation is validation

    def test_updates_valid_item_text(
        self,
    ) -> None:
        original_context = create_bullet_list(
            (
                create_bullet_list_item(translation_id=1, text="Hello"),
                create_bullet_list_item(translation_id=2, text="World"),
            )
        )
        translated_context = create_bullet_list(
            (
                create_bullet_list_item(translation_id=1, text="こんにちは"),
                create_bullet_list_item(translation_id=2, text="世界"),
            )
        )

        validation = create_validation_result(
            issues=(create_validation_issue(translation_id=2),)
        )

        result = _update_bullet_list_retry_context(
            RetryContextArg(
                section_id="section-1",
                section_definition=SectionNoTranslation(),
                original_context=original_context,
                translated_context=translated_context,
                current_validation=validation,
                previous_validation=None,
            )
        )

        assert isinstance(result, Success)

        state = result.unwrap()

        assert state.context is original_context
        assert state.context.items[0].text == "こんにちは"
        assert state.context.items[1].text == "World"

    def test_does_not_reprocess_item_valid_in_previous_attempt(
        self,
    ) -> None:
        original_context = create_bullet_list(
            (
                create_bullet_list_item(translation_id=1, text="Hello"),
                create_bullet_list_item(translation_id=2, text="World"),
            )
        )
        translated_context = create_bullet_list(
            (
                create_bullet_list_item(translation_id=1, text="こんにちは"),
                create_bullet_list_item(translation_id=2, text="世界"),
            )
        )

        previous_validation = create_validation_result(
            issues=(create_validation_issue(translation_id=2),)
        )
        current_validation = create_validation_result(
            issues=(create_validation_issue(translation_id=1),)
        )

        result = _update_bullet_list_retry_context(
            RetryContextArg(
                section_id="section-1",
                section_definition=SectionNoTranslation(),
                original_context=original_context,
                translated_context=translated_context,
                current_validation=current_validation,
                previous_validation=previous_validation,
            )
        )

        assert isinstance(result, Success)

        state = result.unwrap()

        # item 1 は今回invalidなので元のまま
        assert state.context.items[0].text == "Hello"

        # item 2 は前回invalid → 今回validなので反映される
        assert state.context.items[1].text == "世界"
