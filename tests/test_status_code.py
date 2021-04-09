import pytest

from gyomu.status_code import StatusCode
from gyomu.configurator import Configurator


def test_status_code(status_handler_setup, register_file_mail_sender):
    config: Configurator = status_handler_setup
    ret_val: StatusCode = StatusCode.debug("Debug Test", config, application_id=config.application_id)
    print(ret_val.get_status_id())
    print(str(StatusCode.SUCCEED_STATUS.code))
    print(str(ret_val))
