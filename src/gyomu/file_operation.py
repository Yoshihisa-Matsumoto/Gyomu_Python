""" FileOperation class
FileOperation support
* Access check
* File Lock ( logical lock )
* Search
* Archive / Unarchive
"""

import os
import multiprocessing
from datetime import datetime
from sys import platform
import re
from gyomu.file_model import FileFilterInfo, FileInfo, FilterType, FileCompareType, FileTransportInfo, FileArchiveType
from gyomu.configurator import Configurator, SharedObjectType
from gyomu.status_code import StatusCode
import gyomu.archive.zip


class FileOperation:
    """ FileOperation class
    FileOperation support
    * Access check
    * File Lock ( logical lock )
    * Search
    * Archive / Unarchive
    """
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

        if platform == 'win32':
            try:
                os.rename(filename,filename)
                return True
            except OSError:
                return False
        else:
            # TODO Not proper way to consider when we access file on different server
            return False

    lock_filename: str = None
    lock_event: multiprocessing.Condition = None

    lock_dictionary: dict = None
    _lock: multiprocessing.Lock = None

    __config: Configurator

    @staticmethod
    def lock_process(filename: str, config: Configurator) :
        """
        Probably better to enhance for inter-process locking because of python threading limitation
        :param filename:
        :return:
        """
        file_access: FileOperation = FileOperation(config)
        file_access.lock_filename = filename.upper()
        is_first = False

        if FileOperation._lock is None:
            FileOperation._lock = config.retrieve_shared_item_and_register_if_not_exist(
                FileOperation.__name__ + ":lock", SharedObjectType.Lock)
        if FileOperation.lock_dictionary is None:
            FileOperation.lock_dictionary = config.retrieve_shared_item_and_register_if_not_exist(
                FileOperation.__name__, SharedObjectType.Dictionary)

        with FileOperation._lock:
            if file_access.lock_filename in FileOperation.lock_dictionary:
                #print('retrieve existing lock event for ' + file_access.lock_filename)
                file_access.lock_event = FileOperation.lock_dictionary[file_access.lock_filename]
            else:
                #print('create lock event for ' + file_access.lock_filename)
                file_access.lock_event = config.get_proxy_object().create_condition()
                FileOperation.lock_dictionary[file_access.lock_filename] = file_access.lock_event
                is_first= True
        #print('PID:' + str(config.unique_instance_id_per_machine) + '  ' + str(FileOperation.lock_dictionary))
        #StatusCode.debug(config.dump_shared_dictionary(), config)
        #print('file operation lock unlock')

        # if not is_first:
        #     file_access.lock_event.wait()

        return file_access

    def __init__(self, config: Configurator):
        self.__config=config

    def __enter__(self):
        if self.lock_event is not None:
            self.lock_event.__enter__()
            #StatusCode.debug('FileOperation Lock, dump:' + self.__config.dump_shared_dictionary(),self.__config)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.lock_event is not None:
            self.lock_event.notify()
            self.lock_event.__exit__(exc_type, exc_val, exc_tb)
            #StatusCode.debug('FileOperation UnLock', self.__config)

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
                gyomu.archive.zip.ZipArchive.create(zip_filename=archive_name,
                                                    transfer_information_list=source_file_list,
                                                    password=password, config=config)

            return StatusCode.SUCCEED_STATUS
