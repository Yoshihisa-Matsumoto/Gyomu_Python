from datetime import datetime, timezone
from pathlib import Path
from os import path
from enum import Enum


class FileInfo:

    @staticmethod
    def epoch_to_datetimeutc(epoch):
        return datetime.fromtimestamp(epoch, tz=timezone.utc)

    file_name: str
    full_path: str
    dir_name: str
    dir_path: str
    size: str
    extension: str
    create_time_utc: datetime
    update_time_utc: datetime
    last_access_time_utc: datetime

    def __init__(self, file_path):
        p = Path(file_path)
        self.file_name = p.name
        self.full_path = str(p.resolve())
        self.dir_name = p.parent.name
        self.dir_path = str(p.parent)
        self.size = file_path.getsize(file_path)
        self.extension = ''.join(p.suffix)
        self.create_time_utc = FileInfo.epoch_to_datetimeutc(file_path.getctime(p))
        self.update_time_utc = FileInfo.epoch_to_datetimeutc(file_path.getmtime(p))
        self.last_access_time_utc = FileInfo.epoch_to_datetimeutc(file_path.getatime(p))


class FilterType(Enum):
    FILE_NAME = 1,
    CREATE_TIME_UTC = 2,
    LAST_ACCESS_TIME_UTC = 3,
    LAST_WRITE_TIME_UTC = 4


class FileCompareType(Enum):
    EQUAL = 1,
    LARGER = 2,
    LESS = 3,
    LARGER_OR_EQUAL = 4,
    LESS_OR_EQUAL = 5


class FileFilterInfo:
    name_filter: str
    target_date: datetime

    def __init__(self, kind: FilterType, operator: FileCompareType, filter):
        self.kind = kind
        self.operator = operator

        try:
            if self.kind == FilterType.FILE_NAME:
                self.name_filter = str(filter)
            elif type(filter) == datetime:
                self.target_date = filter
            elif type(filter) == str:
                self.target_date = datetime.strptime(filter, '%Y%m%d')
            else:
                raise ValueError("Date Parameter is invalid: " + filter)
        except:
            raise ValueError("Date Parameter is invalid: " + filter)


class FileTransportInfo:
    __source_filename: str
    __source_folder_name: str
    __base_path: str
    __destination_filename: str
    __destination_folder_name: str
    delete_sourcefile_after_completion: bool = False
    overwrite_destination: bool = False

    @property
    def is_source_directory(self) -> bool:
        return not self.source_filename

    @property
    def is_destination_directory(self) -> bool:
        return not self.destination_filename

    @property
    def is_destination_root(self) -> bool:
        if not self.__source_folder_name and not self.__destination_folder_name:
            return True
        return False

    @property
    def source_fullname(self):
        if not self.__source_folder_name:
            return self.__source_filename
        if not self.__source_filename:
            return self.__source_folder_name
        return path.join(self.__source_folder_name, self.__source_filename)

    @property
    def source_fullname_with_basepath(self):
        if not self.source_fullname:
            return self.__base_path
        return self.source_fullname if not self.__base_path else path.join(self.__base_path, self.source_fullname)

    @property
    def source_path(self):
        return self.__source_folder_name

    @property
    def source_filename(self):
        return self.__source_filename

    @property
    def destination_filename(self):
        return self.__source_filename if not self.__destination_filename else self.__destination_filename

    @property
    def destination_path(self):
        return self.__source_folder_name if not self.__destination_folder_name else self.__destination_folder_name

    @property
    def destination_fullname(self):
        if not self.destination_path:
            return self.destination_filename
        if not self.destination_filename:
            return self.destination_path
        return path.join(self.destination_path, self.destination_filename)

    def __init__(self, base_path: str = "", source_filename: str = "", source_folder_name: str = "",
                 destination_filename: str = "", destination_foldername: str = "",
                 delete_sourcefile_after_completion: bool = False,
                 overwrite_destination: bool = False):
        self.__base_path = base_path
        self.__source_filename = source_filename
        self.__source_folder_name = source_folder_name
        self.__destination_filename = destination_filename
        self.__destination_folder_name = destination_foldername
        self.delete_sourcefile_after_completion = delete_sourcefile_after_completion
        self.overwrite_destination = overwrite_destination

        if not self.__source_filename and self.__destination_filename:
            raise ValueError("Invalid Parameter")

        if not self.__base_path and not self.__source_folder_name and not self.__source_filename:
            raise ValueError("Invalid Parameter")


"""
Base	Sdir	Sname	Ddir	Dname		(S)full+base	    (S)Full	    (S)path (S)name (D)full	    (D)path (D)name
x   	x	    x	    x	    x		    base\SDir\Sname	    SDir\Sname	SDir    Sname   Ddir\Dname	Ddir    Dname
x   	x   	x	    x	    	    	base\SDir\Sname	    SDir\Sname	SDir    Sname   Ddir\Sname	Ddir    Sname
x   	x	    x   	    	x	    	base\SDir\Sname	    SDir\Sname	SDir    Sname   SDir\Dname	Sdir    Dname
x   	x	    x	    	    	    	base\SDir\Sname	    SDir\Sname	SDir    Sname   SDir\Sname	SDir    Sname
x   	x   	    	x   	    		base\SDir	        SDir	    SDir		    Ddir	    Ddir	
x   	x	                				base\SDir	        SDir	    SDir		    SDir	    SDir	
x                   						base						
x	            		x	        		base				                            Ddir	    Ddir	
x   	    	x   	x   	x	    	base\Sname	        Sname		        Sname	Ddir\Dname	Ddir	Dname
x   	    	x	    x	        		base\Sname	        Sname		        Sname	Ddir\Sname	Ddir	Sname
x       		x	        	x	    	base\Sname	        Sname		        Sname	Dname		Dname
x	        	x	            			base\Sname	        Sname		        Sname	Sname		Sname
    	x   	x   	x	    x	                            SDir\Sname	SDir	Sname	Ddir\Dname	Ddir	Dname
	    x	    x	    x				                        SDir\Sname	SDir	Sname	Ddir\Sname	Ddir	Sname
	    x	    x		        x			                    SDir\Sname	SDir	Sname	SDir\Dname	SDir	Dname
	    x	    x					                            SDir\Sname	SDir	Sname	SDir\Sname	SDir	Sname
	    x	        	x				                        SDir	    SDir	    	Ddir	    Ddir	
	    x						                                SDir	    SDir		    SDir	    SDir	
		        x	    x	    x			                    Sname		        Sname	Ddir\Dname	Ddir	Dname
		        x	    x				                        Sname		        Sname	Ddir\Sname	Ddir	Sname
		        x		        x			                    Sname		        Sname	Dname		        Dname
		        x					                            Sname		        Sname	Sname		        Sname
"""


class FileArchiveType(Enum):
    ZIP = "zip",
    TGZ = "tgz",
    BZIP2 = "bz2",
    GZIP = "gz",
    TAR = "tar",
    GuessFromFileName = "unknown"
