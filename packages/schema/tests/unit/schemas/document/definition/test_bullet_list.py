from gyomu_schema.schemas.document.definition.bullent_list import _validate_bullet_list

from packages.schema.schema_test_support.concept_helpers import (
    create_bullet_list,
    create_bullet_list_item,
)


def test_returns_valid_when_bullet_list_is_unchanged() -> None:
    source = create_bullet_list(
        (
            create_bullet_list_item(translation_id=1, text="one"),
            create_bullet_list_item(translation_id=2, text="two"),
        )
    )
    destination = create_bullet_list(
        (
            create_bullet_list_item(translation_id=1, text="一"),
            create_bullet_list_item(translation_id=2, text="二"),
        )
    )

    result = _validate_bullet_list(source, destination)

    assert result.is_valid
    assert result.issues == ()


def test_returns_issue_when_top_level_item_count_changes() -> None:
    source = create_bullet_list(
        (
            create_bullet_list_item(translation_id=1, text="one"),
            create_bullet_list_item(translation_id=2, text="two"),
        )
    )
    destination = create_bullet_list(
        (create_bullet_list_item(translation_id=1, text="一"),)
    )

    result = _validate_bullet_list(source, destination)

    assert not result.is_valid
    assert len(result.issues) == 1

    issue = result.issues[0]
    assert issue.code == "BULLET_LIST_ITEM_COUNT_CHANGED"
    assert issue.translation_id is None
    assert issue.details == {
        "source_count": "2",
        "translated_count": "1",
    }


def test_returns_issue_when_top_level_translation_id_changes() -> None:
    source = create_bullet_list(
        (
            create_bullet_list_item(translation_id=1, text="one"),
            create_bullet_list_item(translation_id=2, text="two"),
        )
    )
    destination = create_bullet_list(
        (
            create_bullet_list_item(translation_id=1, text="一"),
            create_bullet_list_item(translation_id=3, text="二"),
        )
    )

    result = _validate_bullet_list(source, destination)

    assert not result.is_valid
    assert len(result.issues) == 1

    issue = result.issues[0]
    assert issue.code == "BULLET_LIST_ITEM_TRANSLATIONID_MISMATCH"
    assert issue.translation_id is None


def test_returns_valid_when_children_are_unchanged() -> None:
    source = create_bullet_list(
        (
            create_bullet_list_item(
                translation_id=1,
                text="parent",
                children=(
                    create_bullet_list_item(translation_id=2, text="child"),
                    create_bullet_list_item(translation_id=3, text="child 2"),
                ),
            ),
        )
    )
    destination = create_bullet_list(
        (
            create_bullet_list_item(
                translation_id=1,
                text="親",
                children=(
                    create_bullet_list_item(translation_id=2, text="子"),
                    create_bullet_list_item(translation_id=3, text="子2"),
                ),
            ),
        )
    )

    result = _validate_bullet_list(source, destination)

    assert result.is_valid
    assert result.issues == ()


def test_returns_issue_when_child_item_count_changes() -> None:
    source = create_bullet_list(
        (
            create_bullet_list_item(
                translation_id=1,
                text="parent",
                children=(
                    create_bullet_list_item(translation_id=2, text="child"),
                    create_bullet_list_item(translation_id=3, text="child 2"),
                ),
            ),
        )
    )
    destination = create_bullet_list(
        (
            create_bullet_list_item(
                translation_id=1,
                text="親",
                children=(create_bullet_list_item(translation_id=2, text="子"),),
            ),
        )
    )

    result = _validate_bullet_list(source, destination)

    assert not result.is_valid
    assert len(result.issues) == 1

    issue = result.issues[0]
    assert issue.code == "BULLET_LIST_ITEM_COUNT_CHANGED"
    assert issue.translation_id == 1
    assert issue.details == {
        "source_count": "2",
        "translated_count": "1",
    }


def test_returns_issue_when_child_translation_id_changes() -> None:
    source = create_bullet_list(
        (
            create_bullet_list_item(
                translation_id=1,
                text="parent",
                children=(create_bullet_list_item(translation_id=2, text="child"),),
            ),
        )
    )
    destination = create_bullet_list(
        (
            create_bullet_list_item(
                translation_id=1,
                text="親",
                children=(create_bullet_list_item(translation_id=3, text="子"),),
            ),
        )
    )

    result = _validate_bullet_list(source, destination)

    assert not result.is_valid
    assert len(result.issues) == 1

    issue = result.issues[0]
    assert issue.code == "BULLET_LIST_ITEM_TRANSLATIONID_MISMATCH"
    assert issue.translation_id == 1


def test_returns_issue_when_nested_child_translation_id_changes() -> None:
    source = create_bullet_list(
        (
            create_bullet_list_item(
                translation_id=1,
                text="parent",
                children=(
                    create_bullet_list_item(
                        translation_id=2,
                        text="child",
                        children=(
                            create_bullet_list_item(
                                translation_id=3,
                                text="nested child",
                            ),
                        ),
                    ),
                ),
            ),
        )
    )
    destination = create_bullet_list(
        (
            create_bullet_list_item(
                translation_id=1,
                text="親",
                children=(
                    create_bullet_list_item(
                        translation_id=2,
                        text="子",
                        children=(
                            create_bullet_list_item(
                                translation_id=4,
                                text="孫",
                            ),
                        ),
                    ),
                ),
            ),
        )
    )

    result = _validate_bullet_list(source, destination)

    assert not result.is_valid
    assert len(result.issues) == 1

    issue = result.issues[0]
    assert issue.code == "BULLET_LIST_ITEM_TRANSLATIONID_MISMATCH"
    assert issue.translation_id == 2
