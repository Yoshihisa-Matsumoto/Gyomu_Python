import pyzipper
import os
from gyomu.file_model import FileTransportInfo
import io
from gyomu.status_code import StatusCode
from gyomu.configurator import Configurator


class ZipArchive:

    @classmethod
    def create(cls, zip_filename: str, transfer_information_list: list[FileTransportInfo],
               config: Configurator, application_id: int =-1,
               password: str = "", encoding: str = 'ascii', is_aes_encrypted: bool = True) -> StatusCode:
        if password != "" and not is_aes_encrypted:
            raise ValueError("Other than AES Encryption is supported")

        if application_id==-1:
            application_id= config.application_id

        pwd: bytes = bytes(password, encoding) if password != "" and ascii != "" else bytes()

        with cls.__create_zip_object(zip_filename, mode='w', password=pwd,
                                     is_aes_encrypted=is_aes_encrypted) as zip_object:
            for transfer_information in transfer_information_list:
                source_path = transfer_information.source_fullname_with_basepath
                if not os.path.exists(source_path):
                    return StatusCode(StatusCode.FILE_NOT_FOUND, config,
                                      arguments=[source_path], target_application_id=application_id)

                if not transfer_information.is_source_directory:
                    destination_entry_name = transfer_information.destination_fullname
                    destination_entry_name = destination_entry_name.replace(os.sep, "/")
                    zip_object.write(filename=source_path, arcname=destination_entry_name)
                else:
                    for root, _, files in os.walk(source_path):
                        for filename in files:
                            source_file_full_path = os.path.join(root, filename)
                            # destination_entry_name = filename if not transfer_information.source_path \
                            #     else os.path.join(transfer_information.source_path, filename)
                            destination_entry_name = source_file_full_path[len(source_path) + 1:]
                            destination_entry_name = destination_entry_name.replace(os.sep, "/")
                            zip_object.write(filename=source_file_full_path, arcname=destination_entry_name)

        return StatusCode.SUCCEED_STATUS

    @classmethod
    def unzip(cls, transfer_information: FileTransportInfo,
              config: Configurator, application_id: int = -1,
              password: str = "", encoding: str = 'ascii',
              is_aes_encrypted: bool = False):
        pwd: bytes = bytes(password, encoding) if password != "" and ascii != "" else bytes()
        if application_id == -1:
            application_id = config.application_id

        zip_filename = transfer_information.source_fullname_with_basepath
        if not os.path.exists(zip_filename):
            return StatusCode(StatusCode.FILE_NOT_FOUND, config,
                              arguments=[zip_filename], target_application_id=application_id)

        with cls.__create_zip_object(zip_filename, 'r', password=pwd,
                                     is_aes_encrypted=is_aes_encrypted) as zip_object:
            for info in zip_object.infolist():
                if info.filename.endswith("/"):
                    continue
                cls.__zip_info_adjust(info, encoding)
                zip_object.extract(info, transfer_information.destination_path)

    @staticmethod
    def __create_zip_object(zip_filepath: str, mode: str, password: bytes = None,
                            is_aes_encrypted: bool = False) -> pyzipper.ZipFile:
        if password is None or len(password) == 0:
            return pyzipper.ZipFile(zip_filepath, mode)
        else:
            if is_aes_encrypted:
                zip_object = pyzipper.AESZipFile(zip_filepath, mode=mode)

                zip_object.setpassword(password)
                zip_object.setencryption(pyzipper.WZ_AES)
                return zip_object
            else:
                zip_object = pyzipper.ZipFile(zip_filepath, mode=mode)
                zip_object.setpassword(password)
                return zip_object

    @staticmethod
    def __zip_info_adjust(info: pyzipper.ZipInfo, encoding: str = "ascii"):
        if encoding != "":
            info.filename = info.orig_filename.encode(encoding).decode('cp932')
        if os.sep != "/" and os.sep in info.filename:
            info.filename = info.filename.replace(os.sep, "/")

    def __init__(self, zip_filepath: str, password: str = "", encoding: str = "ascii", is_aes_encrypted: bool = True):
        self.zip_filepath = zip_filepath
        pwd: bytes = bytes(password, encoding) if password != "" and ascii != "" else bytes()
        self.password = pwd
        self.encoding = encoding
        self.is_aes_encrypted = is_aes_encrypted

    _zip_object: pyzipper.ZipFile = None

    def __enter__(self):
        if self._zip_object is None:
            self._zip_object = ZipArchive.__create_zip_object(self.zip_filepath, 'r', password=self.password,
                                                              is_aes_encrypted=self.is_aes_encrypted)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._zip_object is not None:
            with self._zip_object:
                pass

    def get_entry_from_name(self, entry_name: str) -> io.BufferedIOBase:
        if os.sep != "/" and os.sep in entry_name:
            entry_name = entry_name.replace(os.sep, "/")

        for info in self._zip_object.infolist():
            ZipArchive.__zip_info_adjust(info, self.encoding)
            if entry_name == info.filename:
                return self._zip_object.open(info, 'r', pwd=self.password)
        raise ValueError(entry_name + " Not Found")

    def get_entry_from_transfer_information(self, transfer_information: FileTransportInfo) -> io.BufferedIOBase:
        if transfer_information is None:
            raise ValueError("No transfer information set")
        if transfer_information.is_source_directory:
            raise ValueError("Source File not specified")

        entry_name = transfer_information.source_fullname
        return self.get_entry_from_name(entry_name)

    def get_entry_file_list_from_directory(self, source_folder_name: str) -> list[str]:
        result_file_list = []

        for info in self._zip_object.infolist():
            ZipArchive.__zip_info_adjust(info, self.encoding)
            if source_folder_name == "" or (
                    not info.filename.endswith("/") and info.filename.startswith(source_folder_name)):
                result_file_list.append(info.filename)
        return result_file_list

    def file_exists(self, filename: str) -> bool:

        for info in self._zip_object.infolist():
            ZipArchive.__zip_info_adjust(info, self.encoding)
            if "/" in filename:
                if info.filename == filename:
                    return True
            else:
                if info.filename.split('/')[-1] == filename:
                    return True
        return False

    def directory_exists(self, directory_name: str) -> bool:
        if not directory_name.endswith("/"):
            directory_name += "/"

        for info in self._zip_object.infolist():
            if not info.filename.endswith("/"):
                continue
            ZipArchive.__zip_info_adjust(info, self.encoding)
            if info.filename == directory_name:
                return True
        return False
