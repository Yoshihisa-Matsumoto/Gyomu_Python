import os
import threading
from datetime import datetime

import re
from gyomu.file_model import FileFilterInfo, FileInfo, FilterType, FileCompareType, FileTransportInfo, FileArchiveType
from gyomu.configurator import Configurator
from gyomu.status_code import StatusCode
import gyomu.archive.zip_archive


class FileOperation:
    @staticmethod
    def can_access(filename: str, readonly: bool = False) -> bool:
        if not os.path.exists(filename):
            return False

        special_extensions = ["xls", "xlsm", "xlsx", "zip"]
        _, file_extension = os.path.splitext(filename)
        file_extension = file_extension.lower()
        if file_extension in special_extensions and os.path.getsize(filename) == 0:
            return False

        if readonly:
            return True

        try:
            with open(filename, 'w'):
                pass
            return True
        except OSError:
            return False

    lock_filename: str = None
    lock_event: threading.Condition = None

    lock_dictionary = dict()
    _lock: threading.Lock = threading.Lock()

    @staticmethod
    def lock_process(filename: str) -> gyomu.file_operation.FileOperation:
        file_access: FileOperation = FileOperation()
        file_access.lock_filename = filename.upper()
        with FileOperation._lock:
            if file_access.lock_filename in FileOperation.lock_dictionary:
                file_access.lock_event = FileOperation.lock_dictionary[file_access.lock_filename]
                file_access.lock_event.wait()
            else:
                file_access.lock_event = threading.Condition()
                FileOperation.lock_dictionary[file_access.lock_filename] = file_access.lock_event

        return file_access

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.lock_event is not None:
            self.lock_event.notify()

    @staticmethod
    def search(parent_directory: str, filter_conditions: list[FileFilterInfo],
               recursive: bool = False) -> list[FileInfo]:
        file_infos: list[FileInfo] = []
        if not os.path.exists(parent_directory):
            return file_infos

        for root, _, files in os.walk(parent_directory):
            for filename in files:
                fullpath = os.path.join(root, filename)
                if FileOperation._is_file_valid(fullpath, filter_conditions):
                    file_infos.append(FileInfo(fullpath))
            if not recursive:
                break

        return file_infos

    @staticmethod
    def _is_file_valid(filename: str, filter_conditions: list[FileFilterInfo]) -> bool:
        is_match = True
        file_information: FileInfo = FileInfo(filename)
        for filter_info in filter_conditions:
            is_match = FileOperation._is_file_valid_for_filter(file_information, filter_info)
            if not is_match:
                break
        return is_match

    @staticmethod
    def _is_file_valid_for_filter(file_information: FileInfo, filter_condition: FileFilterInfo) -> bool:

        if filter_condition.kind == FilterType.FILE_NAME:
            return FileOperation._is_file_name_match(file_information.file_name, filter_condition.name_filter,
                                                     filter_condition.operator)
        elif filter_condition.kind == FilterType.CREATE_TIME_UTC:
            return FileOperation._is_file_date_match(file_information.create_time_utc, filter_condition.target_date,
                                                     filter_condition.operator)
        elif filter_condition.kind == FilterType.LAST_ACCESS_TIME_UTC:
            return FileOperation._is_file_date_match(file_information.last_access_time_utc,
                                                     filter_condition.target_date, filter_condition.operator)
        elif filter_condition.kind == FilterType.LAST_WRITE_TIME_UTC:
            return FileOperation._is_file_date_match(file_information.update_time_utc, filter_condition.target_date,
                                                     filter_condition.operator)
        return True

    @staticmethod
    def _is_file_name_match(filename: str, target_filter: str, compare_type: FileCompareType) -> bool:
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
    def _is_file_date_match(file_date: datetime, target_filter: datetime, compare_type: FileCompareType) -> bool:
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

    @staticmethod
    def archive(archive_filename: str, archive_type: FileArchiveType,
                source_file_list: list[FileTransportInfo],
                config: Configurator, application_id: int,
                password: str = None) -> StatusCode:
        if source_file_list is None or len(source_file_list) == 0:
            return StatusCode.invalid_argument_status("Source File Not Specified to archive", config, application_id)

        archive_info = FileInfo(archive_filename)
        if archive_type == FileArchiveType.GuessFromFileName:
            extension = archive_info.extension.lower()
            if extension == "zip":
                archive_type = FileArchiveType.ZIP
            elif extension == "tgz":
                archive_type = FileArchiveType.TGZ
            elif extension == "bz2":
                archive_type = FileArchiveType.BZIP2
            elif extension == "gz":
                archive_type = FileArchiveType.GZIP
            elif extension == "tar":
                archive_type = FileArchiveType.TAR
            else:
                return StatusCode.invalid_argument_status("File Extension Not supported for archiving",
                                                          config, application_id)

            if archive_type == FileArchiveType.BZIP2 or archive_type == FileArchiveType.GZIP:
                if len(source_file_list) > 1 or len([f for f in source_file_list if f.is_source_directory]) > 0:
                    return StatusCode.invalid_argument_status(
                        "Multiple files are not supported in this compression type",
                        config, application_id)

            if archive_type != FileArchiveType.ZIP and password != "":
                return StatusCode.invalid_argument_status("password is not supported on other than zip format",
                                                          config, application_id)

            source_file = source_file_list[0]
            archive_file_directory = archive_info.dir_path
            archive_name = archive_info.file_name

            if archive_type == FileArchiveType.ZIP:
                gyomu.archive.zip_archive.ZipArchive.create(zip_filename=archive_name,
                                                            transfer_information_list=source_file_list,
                                                            password=password)

            return StatusCode.SUCCEED_STATUS
