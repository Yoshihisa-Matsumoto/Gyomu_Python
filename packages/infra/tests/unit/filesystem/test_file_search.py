from datetime import UTC, datetime
from pathlib import Path

from gyomu_schema.filesystem.file import (
    FileCompareType,
    FileFilterInfo,
    FileFilterType,
)

from gyomu_infra.filesystem.file_search import FileSearch


class TestFileSearch:
    def test_returns_empty_list_when_directory_does_not_exist(
        self,
        tmp_path: Path,
    ) -> None:
        directory = tmp_path / "not_exists"

        result = FileSearch.search(
            directory,
            [],
        )

        assert result == []

    def test_returns_files_in_direct_directory(
        self,
        tmp_path: Path,
    ) -> None:
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        subdirectory = tmp_path / "subdir"

        file1.touch()
        file2.touch()
        subdirectory.mkdir()
        (subdirectory / "file3.txt").touch()

        result = FileSearch.search(
            tmp_path,
            [],
        )

        assert {file_info.full_path for file_info in result} == {
            file1,
            file2,
        }

    def test_returns_files_recursively(
        self,
        tmp_path: Path,
    ) -> None:
        file1 = tmp_path / "file1.txt"
        subdirectory = tmp_path / "subdir"
        file2 = subdirectory / "file2.txt"

        file1.touch()
        subdirectory.mkdir()
        file2.touch()

        result = FileSearch.search(
            tmp_path,
            [],
            recursive=True,
        )

        assert {file_info.full_path for file_info in result} == {
            file1,
            file2,
        }

    def test_filters_by_file_name(
        self,
        tmp_path: Path,
    ) -> None:
        txt_file = tmp_path / "test.txt"
        csv_file = tmp_path / "test.csv"

        txt_file.touch()
        csv_file.touch()

        result = FileSearch.search(
            tmp_path,
            [
                FileFilterInfo(
                    kind=FileFilterType.FILE_NAME,
                    value=r".*\.txt",
                    operator=FileCompareType.EQUAL,
                )
            ],
        )

        assert [file_info.full_path for file_info in result] == [txt_file]

    def test_applies_multiple_filters_with_and_condition(
        self,
        tmp_path: Path,
    ) -> None:
        txt_file = tmp_path / "test.txt"
        csv_file = tmp_path / "test.csv"

        txt_file.touch()
        csv_file.touch()

        result = FileSearch.search(
            tmp_path,
            [
                FileFilterInfo(
                    kind=FileFilterType.FILE_NAME,
                    value=r"test\..*",
                    operator=FileCompareType.EQUAL,
                ),
                FileFilterInfo(
                    kind=FileFilterType.FILE_NAME,
                    value=r".*\.txt",
                    operator=FileCompareType.EQUAL,
                ),
            ],
        )

        assert [file_info.full_path for file_info in result] == [txt_file]


class TestFileSearchFileNameMatch:
    def test_equal_uses_regular_expression(self) -> None:
        assert FileSearch._is_file_name_match(
            "test.txt",
            r"test\..*",
            FileCompareType.EQUAL,
        )

    def test_larger(self) -> None:
        assert FileSearch._is_file_name_match(
            "b.txt",
            "a.txt",
            FileCompareType.LARGER,
        )

    def test_larger_or_equal(self) -> None:
        assert FileSearch._is_file_name_match(
            "b.txt",
            "b.txt",
            FileCompareType.LARGER_OR_EQUAL,
        )

    def test_less(self) -> None:
        assert FileSearch._is_file_name_match(
            "a.txt",
            "b.txt",
            FileCompareType.LESS,
        )

    def test_less_or_equal(self) -> None:
        assert FileSearch._is_file_name_match(
            "a.txt",
            "a.txt",
            FileCompareType.LESS_OR_EQUAL,
        )


class TestFileSearchFileDateMatch:
    def test_equal(self) -> None:
        target = datetime(2026, 1, 1, tzinfo=UTC)

        assert FileSearch._is_file_date_match(
            target,
            target,
            FileCompareType.EQUAL,
        )

    def test_larger(self) -> None:
        target = datetime(2026, 1, 1, tzinfo=UTC)
        file_date = datetime(2026, 1, 2, tzinfo=UTC)

        assert FileSearch._is_file_date_match(
            file_date,
            target,
            FileCompareType.LARGER,
        )

    def test_larger_or_equal(self) -> None:
        target = datetime(2026, 1, 1, tzinfo=UTC)

        assert FileSearch._is_file_date_match(
            target,
            target,
            FileCompareType.LARGER_OR_EQUAL,
        )

    def test_less(self) -> None:
        target = datetime(2026, 1, 2, tzinfo=UTC)
        file_date = datetime(2026, 1, 1, tzinfo=UTC)

        assert FileSearch._is_file_date_match(
            file_date,
            target,
            FileCompareType.LESS,
        )

    def test_less_or_equal(self) -> None:
        target = datetime(2026, 1, 1, tzinfo=UTC)

        assert FileSearch._is_file_date_match(
            target,
            target,
            FileCompareType.LESS_OR_EQUAL,
        )
