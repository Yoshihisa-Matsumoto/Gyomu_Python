from gyomu_docstring.update.internal.validate import (
    InvalidResult,
    ValidResult,
    get_docstring_identities_from_context,
    validate_docstring_update_plan,
)

from packages.ai_compiler.ai_compiler_test_support.helper import (
    create_context_entry,
    create_declaration_info,
    create_declaration_info_from_declaration_identity,
    create_docstring_declaration_context,
    create_docstring_file_context,
    create_docstring_update_entry,
    create_docstring_update_plan,
    create_nondocumentable_context,
)
from packages.schema.schema_test_support.helpers import create_declaration_identity


def test_validate_docstring_update_plan_returns_valid_when_identities_match() -> None:
    context = create_docstring_file_context(
        symbols=(
            create_docstring_declaration_context(
                create_declaration_info("foo", "str"),
                existing_docstring=None,
                children=(),
                target=create_declaration_identity("foo"),
            ),
            create_docstring_declaration_context(
                create_declaration_info("bar", "str"),
                existing_docstring=None,
                children=(),
                target=create_declaration_identity("bar"),
            ),
        )
    )
    plan = create_docstring_update_plan(
        entries=(
            create_docstring_update_entry(
                identity=create_declaration_identity("foo"),
            ),
            create_docstring_update_entry(
                identity=create_declaration_identity("bar"),
            ),
        )
    )

    result = validate_docstring_update_plan(context, plan)

    assert isinstance(result, ValidResult)


def test_validate_docstring_update_plan_returns_invalid_when_identity_is_missing() -> (
    None
):
    foo = create_declaration_identity("foo")
    bar = create_declaration_identity("bar")

    context = create_docstring_file_context(
        symbols=(
            create_docstring_declaration_context(
                create_declaration_info("foo", "str"),
                existing_docstring=None,
                children=(),
                target=foo,
            ),
            create_docstring_declaration_context(
                create_declaration_info("bar", "str"),
                existing_docstring=None,
                children=(),
                target=bar,
            ),
        )
    )
    plan = create_docstring_update_plan(
        entries=(
            create_docstring_update_entry(
                identity=create_declaration_identity("foo"),
            ),
        )
    )

    result = validate_docstring_update_plan(context, plan)

    assert isinstance(result, InvalidResult)
    assert set(result.diff) == {bar}


def test_validate_docstring_update_plan_ignores_plan_only_identity() -> None:
    foo = create_declaration_identity("foo")
    extra = create_declaration_identity("extra")

    context = create_docstring_file_context(
        symbols=(
            create_docstring_declaration_context(
                create_declaration_info("foo", "str"),
                target=foo,
            ),
        )
    )
    plan = create_docstring_update_plan(
        entries=(
            create_docstring_update_entry(
                identity=foo,
            ),
            create_docstring_update_entry(
                identity=extra,
            ),
        )
    )

    result = validate_docstring_update_plan(context, plan)

    assert isinstance(result, ValidResult)


def test_get_docstring_identities_from_context_excludes_non_documentable_children() -> (
    None
):
    root = create_declaration_identity("root")
    documentable = create_declaration_identity("documentable")
    non_documentable = create_declaration_identity("non_documentable")

    context = create_docstring_file_context(
        symbols=(
            create_docstring_declaration_context(
                create_declaration_info("root", "int"),
                target=create_declaration_identity("root"),
                children=(
                    create_context_entry(
                        target=documentable,
                        member=create_declaration_info_from_declaration_identity(
                            documentable
                        ),
                    ),
                    create_context_entry(
                        target=non_documentable,
                        member=create_declaration_info_from_declaration_identity(
                            non_documentable
                        ),
                        documentable=create_nondocumentable_context(),
                    ),
                ),
            ),
        )
    )

    result = get_docstring_identities_from_context(context)

    assert result == {root, documentable}


def test_get_docstring_identities_from_context_stops_recursion_at_depth_two() -> None:
    root = create_declaration_identity("root")
    child = create_declaration_identity("child")
    grandchild = create_declaration_identity("grandchild")
    great_grandchild = create_declaration_identity("great_grandchild")

    # root
    # └── child          depth 0
    #     └── grandchild depth 1
    #         └── great_grandchild depth 2
    #             └── ... ← ここは探索されない

    context = create_docstring_file_context(
        symbols=(
            create_docstring_declaration_context(
                create_declaration_info("root", "int"),
                target=create_declaration_identity("root"),
                children=(
                    create_context_entry(
                        target=child,
                        member=create_declaration_info_from_declaration_identity(child),
                        children=(
                            create_context_entry(
                                target=grandchild,
                                member=create_declaration_info_from_declaration_identity(
                                    grandchild
                                ),
                                children=(
                                    create_context_entry(
                                        target=great_grandchild,
                                        member=create_declaration_info_from_declaration_identity(
                                            great_grandchild
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        )
    )

    result = get_docstring_identities_from_context(context)

    assert result == {root, child, grandchild}
