from datetime import UTC, datetime
from enum import Enum
from os import path
from pathlib import Path, PurePosixPath


class FileInfo:
    @staticmethod
    def epoch_to_datetimeutc(epoch: float) -> datetime:
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
    FILE_NAME = "file_name"
    CREATE_TIME_UTC = "create_time_utc"
    LAST_ACCESS_TIME_UTC = "last_access_time_utc"
    LAST_WRITE_TIME_UTC = "last_write_time_utc"


class FileCompareType(Enum):
    EQUAL = "equal"
    LARGER = "larger"
    LESS = "less"
    LARGER_OR_EQUAL = "larger_or_equal"
    LESS_OR_EQUAL = "less_or_equal"


class FileFilterInfo:
    name_filter: str
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
    """
    Base	Sdir	Sname	Ddir	Dname		(S)full+base	    (S)Full	    (S)path (S)name (D)full	    (D)path (D)name
    x   	x	    x	    x	    x		    base/SDir/Sname	    SDir/Sname	SDir    Sname   Ddir/Dname	Ddir    Dname
    x   	x   	x	    x	    	    	base/SDir/Sname	    SDir/Sname	SDir    Sname   Ddir/Sname	Ddir    Sname
    x   	x	    x   	    	x	    	base/SDir/Sname	    SDir/Sname	SDir    Sname   SDir/Dname	Sdir    Dname
    x   	x	    x	    	    	    	base/SDir/Sname	    SDir/Sname	SDir    Sname   SDir/Sname	SDir    Sname
    x   	x   	    	x   	    		base/SDir	          SDir	      SDir		        Ddir	      Ddir
    x   	x	                				base/SDir	          SDir	      SDir		        SDir	      SDir
    x                   						base
    x	            		x	        		base				                                    Ddir	      Ddir
    x   	    	x   	x   	x	    	base/Sname	        Sname		            Sname	  Ddir/Dname	Ddir	  Dname
    x   	    	x	    x	        		base/Sname	        Sname		            Sname	  Ddir/Sname	Ddir	  Sname
    x       		x	        	x	    	base/Sname	        Sname		            Sname	  Dname		            Dname
    x	        	x	            			base/Sname	        Sname		            Sname	  Sname		            Sname
          x   	x   	x	    x	                          SDir/Sname	SDir	  Sname	  Ddir/Dname	Ddir	  Dname
          x	    x	    x				                          SDir/Sname	SDir	  Sname	  Ddir/Sname	Ddir	  Sname
          x	    x		        x			                      SDir/Sname	SDir	  Sname	  SDir/Dname	SDir	  Dname
          x	    x					                              SDir/Sname	SDir	  Sname	  SDir/Sname	SDir	  Sname
          x	        	x				                          SDir	      SDir	    	    Ddir	      Ddir
          x						                                  SDir	      SDir		        SDir	      SDir
                x	    x	    x			                      Sname		            Sname	  Ddir/Dname	Ddir	  Dname
                x	    x				                          Sname		            Sname	  Ddir/Sname	Ddir	  Sname
                x		        x			                      Sname		            Sname	  Dname		            Dname
                x					                              Sname		            Sname	  Sname		            Sname
    """  # noqa: E501

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

    @property
    def is_destination_directory(self) -> bool:
        return not self.destination_filename

    @property
    def is_destination_root(self) -> bool:
        return bool(
            not self.__source_folder_name and not self.__destination_folder_name
        )

    @property
    def source_fullname(self) -> str:
        if not self.__source_folder_name:
            return self.__source_filename
        if not self.__source_filename:
            return self.__source_folder_name
        return str(PurePosixPath(self.__source_folder_name) / self.__source_filename)

    @property
    def source_fullname_with_basepath(self) -> str:
        if not self.source_fullname:
            return self.__base_path
        return (
            self.source_fullname
            if not self.__base_path
            else str(PurePosixPath(self.__base_path) / self.source_fullname)
        )

    @property
    def source_path(self) -> str:
        return self.__source_folder_name

    @property
    def source_filename(self) -> str:
        return self.__source_filename

    @property
    def destination_filename(self) -> str:
        return (
            self.__source_filename
            if not self.__destination_filename
            else self.__destination_filename
        )

    @property
    def destination_path(self) -> str:
        return (
            self.__source_folder_name
            if not self.__destination_folder_name
            else self.__destination_folder_name
        )

    @property
    def destination_fullname(self) -> str:
        if not self.destination_path:
            return self.destination_filename
        if not self.destination_filename:
            return self.destination_path
        return str(PurePosixPath(self.destination_path) / self.destination_filename)

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
    ZIP = ("zip",)
    TGZ = ("tgz",)
    BZIP2 = ("bz2",)
    GZIP = ("gz",)
    TAR = ("tar",)
    GuessFromFileName = "unknown"
