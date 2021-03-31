import pytest
from gyomu.email_sender import EmailSender, EmailBuilder, EmailMessage
from gyomu.json import Json
from gyomu.db_connection_factory import DbConnectionFactory, GYOMU_COMMON_MAINDB_CONNECTION
from gyomu.gyomu_db_model import *
import os
from gyomu.user_factory import UserFactory
from gyomu.user import User
from gyomu.configurator import Configurator, BaseConfigurator
from gyomu.status_code import StatusCode

class FileEmailSender(EmailSender):
    _temp_directory: dir = None

    def __init__(self, temp_directory):
        self._temp_directory = temp_directory

    def send(self, msg: EmailMessage):
        a_file = self._temp_directory.join('mail_test.txt')
        a_file.write(msg.as_string())


@pytest.fixture()
def register_file_mail_sender(tmpdir_factory):
    mail_dir = tmpdir_factory.mktemp('status_code')
    EmailBuilder.register_mail_sender(FileEmailSender(mail_dir))


@pytest.fixture()
def environment_setup():
    original_setting = ""
    if GYOMU_COMMON_MAINDB_CONNECTION in os.environ:
        original_setting = os.environ[GYOMU_COMMON_MAINDB_CONNECTION]
    os.environ[GYOMU_COMMON_MAINDB_CONNECTION] = "postgresql://postgres:password@localhost:5432/gyomu"
    yield
    os.environ[GYOMU_COMMON_MAINDB_CONNECTION] = original_setting


@pytest.fixture()
def application_info_setup(environment_setup):
    with DbConnectionFactory.get_gyomu_db_session() as session:
        app2 = session.query(GyomuAppsInfoCdtbl).get(TEST_APPLICATION_ID)
        if app2 is not None:
            session.delete(app2)
            session.commit()

    app = GyomuAppsInfoCdtbl()
    app.application_id = TEST_APPLICATION_ID
    app.description = "Test Application"
    user: User = UserFactory.get_current_user()
    app.mail_from_name = user.userid
    app.mail_from_address = "Test@test.com"

    with DbConnectionFactory.get_gyomu_db_session() as session:
        session.add(app)
        session.commit()

    yield

    with DbConnectionFactory.get_gyomu_db_session() as session:
        session.delete(app)
        session.commit()

TEST_APPLICATION_ID = 32650

@pytest.fixture()
def status_handler_setup(application_info_setup):
    with DbConnectionFactory.get_gyomu_db_session() as session:
        app2 = session.query(GyomuStatusHandler).filter(
            GyomuStatusHandler.application_id == TEST_APPLICATION_ID).first()
        if app2 is not None:
            session.delete(app2)
            session.commit()

    handler = GyomuStatusHandler()
    handler.application_id = TEST_APPLICATION_ID
    handler.recipient_address = 'test@abc.com'
    handler.status_type = StatusCode.ERROR_DEVELOPER
    handler.recipient_type = "TO"
    handler.recipient_address = "destination@test.com"

    with DbConnectionFactory.get_gyomu_db_session() as session:
        session.add(handler)
        session.commit()

    config: Configurator = BaseConfigurator()
    config.set_application_id(TEST_APPLICATION_ID)

    yield config

    with DbConnectionFactory.get_gyomu_db_session() as session:
        session.delete(handler)
        session.commit()
