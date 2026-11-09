from gyomu_workflow.snapshot.normalize import normalize_filter

from packages.workflow.test_support.helpers import (
    create_file_filter,
    create_snapshot_target_option,
)


def test_normalize_filter_without_file_filter() -> None:
    option = create_snapshot_target_option(file_filter=None)

    normalize_filter(option)

    assert option.file_filter is None


def test_normalize_filter_with_trailing_wildcard() -> None:
    option = create_snapshot_target_option(
        file_filter=create_file_filter(pattern="src/*"),
    )

    normalize_filter(option)

    assert option.file_filter is not None
    assert option.file_filter.pattern == "**/src/**"


def test_normalize_filter_without_trailing_wildcard() -> None:
    option = create_snapshot_target_option(
        file_filter=create_file_filter(pattern="src/**/*.py"),
    )

    normalize_filter(option)

    assert option.file_filter is not None
    assert option.file_filter.pattern == "src/**/*.py"
