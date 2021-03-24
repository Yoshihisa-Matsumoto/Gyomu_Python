
from gyomu.configurator import Configurator
from gyomu.db_connection_factory import DbConnectionFactory, GYOMU_COMMON_MAINDB_CONNECTION
from gyomu.gyomu_db_model import GyomuAppsInfoCdtbl, GyomuStatusTypeCdtbl, GyomuStatusHandler, GyomuStatusInfo
from gyomu.email_sender import EmailBuilder
from threading import Event,Thread
import traceback
from traceback import StackSummary
from collections import namedtuple
import socket

StatusInfo = namedtuple('StatusInfo', ['summary', 'description'])
StatusInfo.__new__.__defaults__ = (None, None)

class StatusCode:
    _error_id:int = 0

    __instance_id:int
    __region:str

    __application_id:int #2byte

    INFO:int = 0
    WARNING:int = 1
    ERROR_BUSINESS:int = 2
    ERROR_BUSINESS2:int = 3
    ERROR_BUSINESS3:int = 4
    ERROR_DEVELOPER:int = 8

    ALL_REGION:str="#"

    SUCCEED_STATUS = None

    _status_table:dict = dict()



    def get_error_id(self):
        return self._error_id

    def is_success(self):
        return self == StatusCode.SUCCEED_STATUS

    def is_not_failed(self):
        return self.get_status_type() < StatusCode.ERROR_BUSINESS

    def get_application_id(self) -> int:
        return (self._error_id >> 20) & 0xfff

    def get_status_type(self) -> int:
        return (self._error_id & 0xfffff ) >> 16

    def get_code(self) ->int:
        return (self._error_id & 0xffff)

    def _get_status_info(self) -> StatusInfo:
        return StatusCode._status_table[self.get_error_id()]

    def _get_title(self) ->str:
        status_info: StatusInfo = self._get_status_info()
        if self._arguments is  not None:
            return status_info.summary.format(*self._arguments)
        return status_info.summary

    def _get_description(self) ->str:
        status_info: StatusInfo = self._get_status_info()
        if self._arguments is not None:
            return status_info.description.format(*self._arguments)
        return status_info.description

    def _get_developer_information(self) ->str:
        if self._exception is not None:
            return str(self._exception)
        else:
            return "\n".join(self._stack_summary)

    def _get_mail_body(self) -> str:
        mail_bodylist = []
        mail_bodylist.append("<HTML><BODY><pre>")
        mail_bodylist.append("User:" + self._config.get_username() + "\tMachine:" + socket.gethostname() + "\tInstance:" + self.__instance_id)
        mail_bodylist.append(self._get_description())
        if self.get_status_type()>=self.ERROR_DEVELOPER :
            mail_bodylist.append(self._get_developer_information())
        mail_bodylist.append("</pre></BODY></HTML>")

        return "\n".join(mail_bodylist)



    _gyomu_status_info_id: int = 0

    def get_status_id(self) -> int:
        if self._gyomu_status_info_id == 0:
            self._registered_event.wait(30000)
        return self._gyomu_status_info_id

    _config : Configurator = None
    _arguments: list = None
    _exception: BaseException = None
    _application_id: int=0
    _custom_summary:str = ""
    _custom_description:str  = ""

    _registered_event: Event

    _stack_summary: StackSummary = None

    @classmethod
    def _code_gen(cls, application_id: int, status_type: int, code: int,
                  summary: str, description: str) -> int:
        if application_id > 0xfff or status_type > 0xf:
            raise ValueError("Invalid Code")
        error_code: int = (int)(application_id << 20) + (int)(status_type << 16) + (code)

        if error_code in cls._status_table:
            raise ValueError(f"Duplicate Keys {error_code}")
        cls._status_table[error_code] = StatusInfo(summary, description)
        return error_code

    OTHER_ERROR:int
    IO_ERROR:int
    DEBUG_COMMENT:int
    INVALID_ARGUMENT_ERROR:int

    @classmethod
    def static_initalize(cls):
        cls.OTHER_ERROR= cls._code_gen(0, cls.ERROR_DEVELOPER, 1, "Other Error", "Other Error happened")
        cls.IO_ERROR = cls._code_gen(0, cls.ERROR_DEVELOPER, 2, "IO Error", "IO Error happened")
        cls.DEBUG_COMMENT = cls._code_gen(0, cls.ERROR_DEVELOPER, 3, "Debug ", "Debug {0}")
        cls.INVALID_ARGUMENT_ERROR = cls._code_gen(0, cls.ERROR_DEVELOPER, 4, "Invalid Argument", "")

    @classmethod
    def debug(cls, argument: str, config: Configurator):
        return StatusCode(error_id=StatusCode.DEBUG_COMMENT,config=config, arguments=[argument])

    def __init__(self, error_id=0, config: Configurator=None,
                 arguments:list = None, exception:BaseException = None,
                 target_application_id: int = -1 ,
                 summary: str = "",
                 description: str = ""):
        self._error_id=error_id
        self._config=config
        self._arguments=arguments
        self._exception = exception
        if target_application_id != -1:
            self._application_id=target_application_id
        else:
            self._application_id=self.get_application_id()
        self._custom_summary=summary
        self._custom_description=description

        if exception == None:
            self._stack_summary = traceback.format_stack()

        if error_id!=0:
            self._registered_event = Event()
            self.do_register()

    def do_register(self):
        thread1 = Thread(target=self._do_register)
        thread1.start()
        # self._do_register()

    def _do_register(self):

        application_information: GyomuAppsInfoCdtbl = None

        status_record: GyomuStatusInfo = GyomuStatusInfo()
        status_record.application_id = self._application_id
        status_record.entry_author = self._config.get_username()
        status_record.status_type = self.get_status_type()
        status_record.error_id = self.get_code()
        status_record.instance_id = self._config.get_unique_instance_id_per_machine()
        status_record.hostname = self._config.get_machine_name()
        status_record.summary = self._custom_summary if self._custom_summary != "" else self._get_title()
        status_record.description = self._custom_description if self._custom_summary !="" else self._get_description()
        status_record.developer_info = self._get_developer_information()

        try:
            session: Session =  DbConnectionFactory.get_gyomu_db_session()
            mail_handler_list: list[GyomuStatusHandler] =None

            with session:
                 application_information = session.query(GyomuAppsInfoCdtbl).get(self._application_id)
                 session.add(status_record)
                 mail_handler_list= session.query(GyomuStatusHandler).filter(GyomuStatusHandler.application_id==self._application_id and GyomuStatusHandler.status_type==self.get_status_type()).all()
                 session.commit()
                 self._gyomu_status_info_id = status_record.id

            if application_information is not None and mail_handler_list is not None and len(mail_handler_list) > 0 :
                to = filter(lambda x: x.recipient_type=="TO", mail_handler_list).map(lambda m: m.recipient_address)
                cc = filter(lambda x: x.recipient_type=="CC", mail_handler_list).map(lambda m: m.recipient_address)
                subject: str = application_information.description + " " + self._get_title()
                subject = subject.replace('\r', ' ').replace('\n', ' ')
                body = self._get_mail_body()
                EmailBuilder.send_html_message(from_address=application_information.mail_from_address,to_address=to,cc_address=cc,
                                               subject=subject,body=body)

        except:
            pass
        finally:
            self._registered_event.set()


