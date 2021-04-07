from gyomu.status_code import StatusCode, static_init


@static_init
class CommonStatusCode(StatusCode):
    APP_ID = 0x1

    @classmethod
    def static_initialize(cls):
        cls.EMAIL_SEND_ERROR = StatusCode._code_gen(cls.APP_ID, StatusCode.ERROR_DEVELOPER, 0x10, "Email Sent Failed", "")

        cls.TASK_GENERATE_ERROR = StatusCode._code_gen(cls.APP_ID, StatusCode.ERROR_DEVEL, 0x41,
                                                       "Task can't be generated",
                                                       "ApplicationID:{0}\nTask Info ID:{1}\nParameter:{2}")
        cls.TASK_INSTANCE_GENERATE_ERROR = StatusCode._code_gen(cls.APP_ID, StatusCode.ERROR_DEVEL, 0x42,
                                                                "Task Instance can't be generated",
                                                                "ApplicationID:{0}\nTask Info ID:{1}\nTask Data ID:{2}\nParameter:{3}")
        cls.TASK_ALREADY_GENERATED = StatusCode._code_gen(cls.APP_ID, StatusCode.ERROR_DEVEL, 0x43,
                                                          "Task is already generated. Can't start twice in the same instance.",
                                                          "ApplicationID:{0}\nTask Info ID:{1}\nParameter:{2}\nTask Data ID:{3}")
        cls.TASK_EXECUTION_FAILED = StatusCode._code_gen(cls.APP_ID, StatusCode.ERROR_DEVEL, 0x44,
                                                         "Unknown Exception happens. Developer must handle exception in the target task.", "ApplicationID:{0}\nTask Info ID:{1}\nParameter:{2}\nTask Data ID:{3}")
        cls.TASK_LIBRARY_INTERNAL_ERROR = StatusCode._code_gen(cls.APP_ID, StatusCode.ERROR_DEVEL, 0x45,
                                                               "Task Library Internal Error happens",
                                                               "Developer must fix the issue,\nApplicationID:{0}\nTask Info ID:{1}\nParameter:{2}\nTask Data ID:{3}")
        cls.TASK_INSTANCE_ALREADY_CHANGED = StatusCode._code_gen(cls.APP_ID, StatusCode.ERROR_BUSINESS, 0x46,
                                                                 "Task already changed",
                                                                 "Task {0} Status already changed since you got before.\nID:{1}")
        cls.TASK_INSTANCE_NOT_EXIST = StatusCode._code_gen(cls.APP_ID, StatusCode.ERROR_DEVEL, 0x47,
                                                           "Task Instance Not Found",
                                                           "ApplicationID:{0}\nTask Info ID:{1}\nTask Data ID:{2}\nInstance ID:{3}")
        cls.TASK_STATUS_INCONSISTENT = StatusCode._code_gen(cls.APP_ID, StatusCode.ERROR_DEVEL, 0x48,
                                                            "There is inconsistent in task status",
                                                            "ApplicationID:{0}\nTask Info ID:{1}\nTask Data ID:{2}\nInstance ID:{3}\nCurrent Status:{4}\nRequest Status:{5}")
        cls.MAIL_CANNOT_BE_SENT = StatusCode._code_gen(cls.APP_ID, StatusCode.ERROR_BUSINESS, 0x49,
                                                       "E-mail can't be sent, but process succeeded.Please send by yourself.",
                                                       "Task {0} ")
        cls.OVERRIDE_METHOD_OTHER_ERROR = StatusCode._code_gen(cls.APP_ID, StatusCode.ERROR_DEVEL, 0x4a,
                                                               "Overrided Method caused unhandled Exception.",
                                                               "Developers need to fix this issue.")
        cls.INVALID_USER_ACCESS = StatusCode._code_gen(cls.APP_ID, StatusCode.ERROR_DEVEL, 0x4b,
                                                       "Invalid User Access Found",
                                                       "ApplicationID:{0}\nTask Info ID:{1}\nTask Data ID:{2}\nInstance ID:{3}\nTarget Action:{4}\nCurrent User:{5}")
        cls.INVALID_USER_ACCESS_TASKBATCH = StatusCode._code_gen(cls.APP_ID, StatusCode.ERROR_DEVEL, 0x4c,
                                                                 "Invalid User Access Found",
                                                                 "Task Batch ID:{0}\nTask Batch Data ID:{1}\n")
        cls.TASK_CANNOT_BE_INSTANCED = StatusCode._code_gen(cls.APP_ID, StatusCode.ERROR_DEVEL, 0x4d,
                                                            "Assembly can't be found", "Assembly:{0}\nClass:{1}")


