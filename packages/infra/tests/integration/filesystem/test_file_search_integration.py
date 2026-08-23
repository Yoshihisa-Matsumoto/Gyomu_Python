from datetime import timedelta
from pathlib import Path

from gyomu_schema.filesystem.file import (
    FileCompareType,
    FileFilterInfo,
    FileFilterType,
    FileInfo,
)

from gyomu_infra.filesystem.file_search import FileSearch

RESOURCE_DIR = Path(__file__).parent.parent.parent / "resources" / "source"


def _file_names(result: list[FileInfo]) -> set[str]:
    return {info.file_name for info in result}


def _relative_paths(result: list[FileInfo], parent: Path) -> set[str]:
    return {info.full_path.relative_to(parent.resolve()).as_posix() for info in result}


class TestFileSearch:
    def test_search_non_recursive(self) -> None:
        result = FileSearch.search(RESOURCE_DIR, [])

        assert _file_names(result) == {
            "README.md",
            "setup.cfg",
            "ユーザー噂.py",
        }

    def test_search_recursive(self) -> None:
        result = FileSearch.search(
            RESOURCE_DIR,
            [],
            recursive=True,
        )

        assert _relative_paths(result, RESOURCE_DIR) == {
            "README.md",
            "setup.cfg",
            "ユーザー噂.py",
            "folder1/email_sender.py",
            "folder1/gyomu_db_model.py",
            "folder1/folder 2/aes_encryption.py",
            "folder1/folder 2/ユーザー噂～.py",
            "folder1/folder 2/フォルダ噂～３/parameter_access.py",
            "folder1/folder 2/フォルダ噂～３/コンフィグ.py",
        }

    def test_search_nonexistent_directory(self) -> None:
        result = FileSearch.search(
            RESOURCE_DIR / "not_exists",
            [],
        )

        assert result == []

    def test_search_file_name_equal(self) -> None:
        result = FileSearch.search(
            RESOURCE_DIR,
            [
                FileFilterInfo(
                    FileFilterType.FILE_NAME,
                    FileCompareType.EQUAL,
                    r"README\.md",
                )
            ],
        )

        assert _file_names(result) == {"README.md"}

    def test_search_file_name_regex(self) -> None:
        result = FileSearch.search(
            RESOURCE_DIR,
            [
                FileFilterInfo(
                    FileFilterType.FILE_NAME,
                    FileCompareType.EQUAL,
                    r".*\.py",
                )
            ],
            recursive=True,
        )

        assert _relative_paths(result, RESOURCE_DIR) == {
            "ユーザー噂.py",
            "folder1/email_sender.py",
            "folder1/gyomu_db_model.py",
            "folder1/folder 2/aes_encryption.py",
            "folder1/folder 2/ユーザー噂～.py",
            "folder1/folder 2/フォルダ噂～３/parameter_access.py",
            "folder1/folder 2/フォルダ噂～３/コンフィグ.py",
        }

    def test_search_file_name_larger(self) -> None:
        result = FileSearch.search(
            RESOURCE_DIR,
            [
                FileFilterInfo(
                    FileFilterType.FILE_NAME,
                    FileCompareType.LARGER,
                    "README.md",
                )
            ],
        )

        assert _file_names(result) == {
            "setup.cfg",
            "ユーザー噂.py",
        }

    def test_search_file_name_larger_or_equal(self) -> None:
        result = FileSearch.search(
            RESOURCE_DIR,
            [
                FileFilterInfo(
                    FileFilterType.FILE_NAME,
                    FileCompareType.LARGER_OR_EQUAL,
                    "README.md",
                )
            ],
        )

        assert _file_names(result) == {
            "README.md",
            "setup.cfg",
            "ユーザー噂.py",
        }

    def test_search_file_name_less(self) -> None:
        result = FileSearch.search(
            RESOURCE_DIR,
            [
                FileFilterInfo(
                    FileFilterType.FILE_NAME,
                    FileCompareType.LESS,
                    "setup.cfg",
                )
            ],
        )

        assert _file_names(result) == {"README.md"}

    def test_search_file_name_less_or_equal(self) -> None:
        result = FileSearch.search(
            RESOURCE_DIR,
            [
                FileFilterInfo(
                    FileFilterType.FILE_NAME,
                    FileCompareType.LESS_OR_EQUAL,
                    "setup.cfg",
                )
            ],
        )

        assert _file_names(result) == {
            "README.md",
            "setup.cfg",
        }

    def test_search_japanese_file_name(self) -> None:
        result = FileSearch.search(
            RESOURCE_DIR,
            [
                FileFilterInfo(
                    FileFilterType.FILE_NAME,
                    FileCompareType.EQUAL,
                    r"ユーザー噂\.py",
                )
            ],
        )

        assert _file_names(result) == {"ユーザー噂.py"}

    def test_search_multiple_conditions(self) -> None:
        result = FileSearch.search(
            RESOURCE_DIR,
            [
                FileFilterInfo(
                    FileFilterType.FILE_NAME,
                    FileCompareType.EQUAL,
                    r".*\.py",
                ),
                FileFilterInfo(
                    FileFilterType.FILE_NAME,
                    FileCompareType.LARGER,
                    "email_sender.py",
                ),
            ],
            recursive=True,
        )

        assert _relative_paths(result, RESOURCE_DIR) == {
            "ユーザー噂.py",
            "folder1/gyomu_db_model.py",
            "folder1/folder 2/ユーザー噂～.py",
            "folder1/folder 2/フォルダ噂～３/parameter_access.py",
            "folder1/folder 2/フォルダ噂～３/コンフィグ.py",
        }

    def test_search_create_time_equal(self) -> None:
        target = FileInfo(RESOURCE_DIR / "README.md").create_time_utc

        result = FileSearch.search(
            RESOURCE_DIR,
            [
                FileFilterInfo(
                    FileFilterType.CREATE_TIME_UTC,
                    FileCompareType.EQUAL,
                    target,
                )
            ],
        )

        assert "README.md" in _file_names(result)

    def test_search_create_time_larger(self) -> None:
        target = FileInfo(RESOURCE_DIR / "README.md").create_time_utc

        result = FileSearch.search(
            RESOURCE_DIR,
            [
                FileFilterInfo(
                    FileFilterType.CREATE_TIME_UTC,
                    FileCompareType.LARGER,
                    target - timedelta(microseconds=1),
                )
            ],
        )

        assert "README.md" in _file_names(result)

    def test_search_create_time_larger_or_equal(self) -> None:
        target = FileInfo(RESOURCE_DIR / "README.md").create_time_utc

        result = FileSearch.search(
            RESOURCE_DIR,
            [
                FileFilterInfo(
                    FileFilterType.CREATE_TIME_UTC,
                    FileCompareType.LARGER_OR_EQUAL,
                    target,
                )
            ],
        )

        assert "README.md" in _file_names(result)

    def test_search_last_access_time(self) -> None:
        target = FileInfo(RESOURCE_DIR / "README.md").last_access_time_utc

        result = FileSearch.search(
            RESOURCE_DIR,
            [
                FileFilterInfo(
                    FileFilterType.LAST_ACCESS_TIME_UTC,
                    FileCompareType.LARGER_OR_EQUAL,
                    target,
                )
            ],
        )

        assert "README.md" in _file_names(result)

    def test_search_last_write_time(self) -> None:
        target = FileInfo(RESOURCE_DIR / "README.md").update_time_utc

        result = FileSearch.search(
            RESOURCE_DIR,
            [
                FileFilterInfo(
                    FileFilterType.LAST_WRITE_TIME_UTC,
                    FileCompareType.EQUAL,
                    target,
                )
            ],
        )

        assert "README.md" in _file_names(result)

    def test_search_file_name_no_match(self) -> None:
        result = FileSearch.search(
            RESOURCE_DIR,
            [
                FileFilterInfo(
                    FileFilterType.FILE_NAME,
                    FileCompareType.EQUAL,
                    r"does_not_exist\.txt",
                )
            ],
        )

        assert result == []
