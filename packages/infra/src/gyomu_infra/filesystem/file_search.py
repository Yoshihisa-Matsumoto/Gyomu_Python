import re
from datetime import datetime
from pathlib import Path

from gyomu_schema.filesystem.file import (
    FileCompareType,
    FileFilterInfo,
    FileFilterType,
    FileInfo,
)


class FileSearch:
    @staticmethod
    def search(
        parent_directory: Path,
        filter_conditions: list[FileFilterInfo],
        recursive: bool = False,
    ) -> list[FileInfo]:
        file_info_list: list[FileInfo] = []
        if not parent_directory.exists():
            return file_info_list

        for path in (
            parent_directory.rglob("*") if recursive else parent_directory.iterdir()
        ):
            if path.is_file() and FileSearch._is_file_valid(path, filter_conditions):
                file_info_list.append(FileInfo(path))

        return file_info_list

    @staticmethod
    def _is_file_valid(filename: Path, filter_conditions: list[FileFilterInfo]) -> bool:
        file_information = FileInfo(filename)

        return all(
            FileSearch._is_file_valid_for_filter(file_information, filter_info)
            for filter_info in filter_conditions
        )

    @staticmethod
    def _is_file_valid_for_filter(
        file_information: FileInfo, filter_condition: FileFilterInfo
    ) -> bool:

        if filter_condition.kind == FileFilterType.FILE_NAME:
            return FileSearch._is_file_name_match(
                file_information.file_name,
                filter_condition.name_filter,
                filter_condition.operator,
            )
        elif filter_condition.kind == FileFilterType.CREATE_TIME_UTC:
            return FileSearch._is_file_date_match(
                file_information.create_time_utc,
                filter_condition.target_date,
                filter_condition.operator,
            )
        elif filter_condition.kind == FileFilterType.LAST_ACCESS_TIME_UTC:
            return FileSearch._is_file_date_match(
                file_information.last_access_time_utc,
                filter_condition.target_date,
                filter_condition.operator,
            )
        elif filter_condition.kind == FileFilterType.LAST_WRITE_TIME_UTC:
            return FileSearch._is_file_date_match(
                file_information.update_time_utc,
                filter_condition.target_date,
                filter_condition.operator,
            )
        return True

    @staticmethod
    def _is_file_name_match(
        filename: str, target_filter: str, compare_type: FileCompareType
    ) -> bool:
        if compare_type == FileCompareType.EQUAL:
            return re.fullmatch(target_filter, filename) is not None
        elif compare_type == FileCompareType.LARGER:
            return filename > target_filter
        elif compare_type == FileCompareType.LARGER_OR_EQUAL:
            return filename >= target_filter
        elif compare_type == FileCompareType.LESS:
            return filename < target_filter
        elif compare_type == FileCompareType.LESS_OR_EQUAL:
            return filename <= target_filter
        return False

    @staticmethod
    def _is_file_date_match(
        file_date: datetime, target_filter: datetime, compare_type: FileCompareType
    ) -> bool:
        if compare_type == FileCompareType.EQUAL:
            return file_date == target_filter
        elif compare_type == FileCompareType.LARGER:
            return file_date > target_filter
        elif compare_type == FileCompareType.LARGER_OR_EQUAL:
            return file_date >= target_filter
        elif compare_type == FileCompareType.LESS:
            return file_date < target_filter
        elif compare_type == FileCompareType.LESS_OR_EQUAL:
            return file_date <= target_filter
        return False
