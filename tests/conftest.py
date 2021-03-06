import pytest
from .context import gyomu
from gyomu.email_sender import EmailSender, EmailBuilder, EmailMessage
from gyomu.json import Json
from gyomu.db_connection_factory import DbConnectionFactory, GYOMU_COMMON_MAINDB_CONNECTION
from gyomu.gyomu_db_model import *
import os
from gyomu.user_factory import UserFactory
from gyomu.user import User
from gyomu.configurator import Configurator, ConfigurationFactory
from gyomu.status_code import StatusCode
from pytest_mock import mocker
from gyomu.holidays import MarketDateAccess
from datetime import date
from pathlib import Path
import sys
import shutil


class FileEmailSender(EmailSender):
    _temp_directory: dir = None

    def __init__(self, temp_directory):
        self._temp_directory = temp_directory

    def send(self, msg: EmailMessage):
        a_file = self._temp_directory.join('mail_test.txt')
        a_file.write(msg.as_string())

@pytest.fixture(scope='session')
def setup_test_files(tmpdir_factory):
    compress_dir = tmpdir_factory.getbasetemp()
    source_directgory = os.path.dirname(__file__)
    source_directory = os.path.join(source_directgory, 'resources')
    destination_directory = os.path.join(compress_dir, 'compress')
    shutil.copytree(source_directory, os.path.join(compress_dir, 'compress'))
    yield destination_directory
    shutil.rmtree(destination_directory)


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

    yield TEST_APPLICATION_ID

    with DbConnectionFactory.get_gyomu_db_session() as session:
        session.delete(app)
        session.commit()

TEST_APPLICATION_ID = 32650
path = Path(__file__)
sys.path.append(path.parent)

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

    config: Configurator = ConfigurationFactory.get_instance()
    config.set_application_id(TEST_APPLICATION_ID)

    yield config

    with DbConnectionFactory.get_gyomu_db_session() as session:
        session.delete(handler)
        session.commit()

@pytest.fixture()
def dummy_holidays():
    yield {"JP": [date(1984, 1, 1),
                  date(1984, 1, 2),
                  date(1984, 1, 15),
                  date(1984, 1, 16),
                  date(1984, 2, 11),
                  date(1984, 3, 20),
                  date(1984, 4, 29),
                  date(1984, 4, 30),
                  date(1984, 5, 3),
                  date(1984, 5, 5),
                  date(1984, 9, 15),
                  date(1984, 9, 23),
                  date(1984, 9, 24),
                  date(1984, 10, 10),
                  date(1984, 11, 3),
                  date(1984, 11, 23)]}

@pytest.fixture()
def mock_holiday(mocker,dummy_holidays):
    mocker.patch.object(MarketDateAccess, '_MarketDateAccess__load_market_holidays', return_value=dummy_holidays)
    yield