from datetime import UTC, datetime
from enum import Enum
from os import path
from pathlib import Path, PurePosixPath


class FileInfo:
    """Represents file metadata and attributes including path, size, extension, and
    timestamps.
    """

    @staticmethod
    def epoch_to_datetimeutc(epoch: float) -> datetime:
        """Converts an epoch timestamp to a UTC datetime object."""

        return datetime.fromtimestamp(epoch, tz=UTC)

    file_name: str
    full_path: Path
    dir_name: str
    dir_path: Path
    size: int
    extension: str
    create_time_utc: datetime
    update_time_utc: datetime
    last_access_time_utc: datetime

    def __init__(self, file_path: Path):
        p = file_path
        self.file_name = p.name
        self.full_path = p.resolve()
        self.dir_name = p.parent.name
        self.dir_path = p.parent
        self.size = path.getsize(file_path)
        self.extension = "".join(p.suffix)
        self.create_time_utc = FileInfo.epoch_to_datetimeutc(path.getctime(p))
        self.update_time_utc = FileInfo.epoch_to_datetimeutc(path.getmtime(p))
        self.last_access_time_utc = FileInfo.epoch_to_datetimeutc(path.getatime(p))


class FileFilterType(Enum):
    """Defines file filtering criteria types such as file name and timestamps."""

    FILE_NAME = "file_name"
    """Filter by file name."""

    CREATE_TIME_UTC = "create_time_utc"
    """Filter by create time in UTC."""

    LAST_ACCESS_TIME_UTC = "last_access_time_utc"
    """Filter by last access time in UTC."""

    LAST_WRITE_TIME_UTC = "last_write_time_utc"
    """Filter by last write time in UTC."""


class FileCompareType(Enum):
    """Defines comparison operators for file filtering."""

    EQUAL = "equal"
    """Equal comparison operator."""

    LARGER = "larger"
    """Larger comparison operator."""

    LESS = "less"
    """Less comparison operator."""

    LARGER_OR_EQUAL = "larger_or_equal"
    """Larger than or equal comparison operator."""

    LESS_OR_EQUAL = "less_or_equal"
    """Less than or equal comparison operator."""


class FileFilterInfo:
    """Holds filter configuration details including filter type, comparison operator,
    and target values or dates.
    """

    name_filter: str
    """Filter string for file name matching."""

    target_date: datetime

    def __init__(
        self,
        kind: FileFilterType,
        operator: FileCompareType,
        value: object,
    ):
        self.kind = kind
        self.operator = operator

        if self.kind == FileFilterType.FILE_NAME:
            self.name_filter = str(value)
        elif isinstance(value, datetime):
            self.target_date = value
        elif isinstance(value, str):
            try:
                self.target_date = datetime.strptime(value, "%Y%m%d")
            except ValueError as e:
                raise ValueError(f"Date Parameter is invalid: {value}") from e
        else:
            raise ValueError(f"Date Parameter is invalid: {value}")


class FileTransportInfo:
    """Holds information for file transport operations including source, destination,
    and filter conditions.
    """

    __source_filename: str
    __source_folder_name: str
    __base_path: str
    __destination_filename: str
    __destination_folder_name: str
    delete_sourcefile_after_completion: bool = False
    overwrite_destination: bool = False
    filter_conditions: list[FileFilterInfo] | None = None

    @property
    def is_source_directory(self) -> bool:
        return not self.source_filename

    """Gets a value indicating whether the source is a directory."""

    """Gets a value indicating whether the source is a directory."""

    @property
    def is_destination_directory(self) -> bool:
        return not self.destination_filename

    """Gets a value indicating whether the destination is a directory."""

    """Gets a value indicating whether the destination is a directory."""

    @property
    def is_destination_root(self) -> bool:
        return bool(
            not self.__source_folder_name and not self.__destination_folder_name
        )

    """Gets a value indicating whether the destination is at the root."""

    """Gets a value indicating whether the destination is at the root."""

    @property
    def source_fullname(self) -> str:
        if not self.__source_folder_name:
            return self.__source_filename
        if not self.__source_filename:
            return self.__source_folder_name
        return str(PurePosixPath(self.__source_folder_name) / self.__source_filename)

    """Gets the full source path."""

    """Gets the full source path."""

    @property
    def source_fullname_with_basepath(self) -> str:
        if not self.source_fullname:
            return self.__base_path
        return (
            self.source_fullname
            if not self.__base_path
            else str(PurePosixPath(self.__base_path) / self.source_fullname)
        )

    """Gets the full source path including the base path."""

    """Gets the full source path including the base path."""

    @property
    def source_path(self) -> str:
        return self.__source_folder_name

    """Gets the source folder path."""

    """Gets the source folder path."""

    @property
    def source_filename(self) -> str:
        return self.__source_filename

    """Gets the source filename."""

    """Gets the source filename."""

    @property
    def destination_filename(self) -> str:
        return (
            self.__source_filename
            if not self.__destination_filename
            else self.__destination_filename
        )

    """Gets the destination filename."""

    """Gets the destination filename."""

    @property
    def destination_path(self) -> str:
        return (
            self.__source_folder_name
            if not self.__destination_folder_name
            else self.__destination_folder_name
        )

    """Gets the destination folder path."""

    """Gets the destination folder path."""

    @property
    def destination_fullname(self) -> str:
        if not self.destination_path:
            return self.destination_filename
        if not self.destination_filename:
            return self.destination_path
        return str(PurePosixPath(self.destination_path) / self.destination_filename)

    """Gets the full destination path."""

    """Gets the full destination path."""

    def __init__(
        self,
        base_path: str = "",
        source_filename: str = "",
        source_folder_name: str = "",
        destination_filename: str = "",
        destination_foldername: str = "",
        delete_sourcefile_after_completion: bool = False,
        overwrite_destination: bool = False,
        filter_conditions: list[FileFilterInfo] | None = None,
    ):
        self.__base_path = base_path
        self.__source_filename = source_filename
        self.__source_folder_name = source_folder_name
        self.__destination_filename = destination_filename
        self.__destination_folder_name = destination_foldername
        self.delete_sourcefile_after_completion = delete_sourcefile_after_completion
        self.overwrite_destination = overwrite_destination
        self.filter_conditions = filter_conditions

        if not self.__source_filename and self.__destination_filename:
            raise ValueError("Invalid Parameter")

        if (
            not self.__base_path
            and not self.__source_folder_name
            and not self.__source_filename
        ):
            raise ValueError("Invalid Parameter")


class FileArchiveType(Enum):
    """Defines supported archive formats and auto-detection options."""

    ZIP = ("zip",)
    """ZIP archive format."""

    TGZ = ("tgz",)
    """TGZ archive format."""

    BZIP2 = ("bz2",)
    """BZIP2 archive format."""

    GZIP = ("gz",)
    """GZIP archive format."""

    TAR = ("tar",)
    """TAR archive format."""

    GuessFromFileName = "unknown"
    """Guess archive type from the file name."""
