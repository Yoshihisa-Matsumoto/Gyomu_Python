from gyomu.db_connection_factory import DbConnectionFactory
from gyomu.task_operation import TaskAccess
from gyomu.configurator import Configurator
from gyomu.tasks.abstract_base_task import AbstractBaseTask
from gyomu.gyomu_db_model import GyomuTaskInfoCdtbl
from gyomu.status_code import StatusCode
import pytest
from gyomu.tasks.simple import AbstractSimpleTask


@pytest.fixture()
def task_info_cdtbl_setup(application_info_setup):
    task_info = GyomuTaskInfoCdtbl()
    task_info.application_id = application_info_setup
    task_info.task_id = 1
    task_info.assembly_name = 'tests.test_tasksample'
    task_info.class_name = 'SimpleTask'
    task_info.description = 'Simple Task Test'
    task_info.restartable= False

    with DbConnectionFactory.get_gyomu_db_session() as session:
        existing_record = session.query(GyomuTaskInfoCdtbl).filter(
            GyomuTaskInfoCdtbl.application_id == task_info.application_id and GyomuTaskInfoCdtbl.task_id == task_info.task_id).first()
        if existing_record is None:
            session.add(task_info)
            session.commit()
            existing_record=task_info

    yield existing_record

    with DbConnectionFactory.get_gyomu_db_session() as session:
        session.delete(existing_record)
        session.commit()

@pytest.fixture()
def fail_task_info_cdtbl_setup(application_info_setup):
    task_info = GyomuTaskInfoCdtbl()
    task_info.application_id = application_info_setup
    task_info.task_id = 2
    task_info.assembly_name = 'tests.test_tasksample'
    task_info.class_name = 'SimpleFailTask'
    task_info.description = 'Simple Fail Task Test'
    task_info.restartable= False

    with DbConnectionFactory.get_gyomu_db_session() as session:
        existing_record = session.query(GyomuTaskInfoCdtbl).filter(
            GyomuTaskInfoCdtbl.application_id == task_info.application_id and GyomuTaskInfoCdtbl.task_id == task_info.task_id).first()
        if existing_record is None:
            session.add(task_info)
            session.commit()
            existing_record=task_info

    yield existing_record

    with DbConnectionFactory.get_gyomu_db_session() as session:
        session.delete(existing_record)
        session.commit()

@pytest.fixture()
def exception_task_info_cdtbl_setup(application_info_setup):
    task_info = GyomuTaskInfoCdtbl()
    task_info.application_id = application_info_setup
    task_info.task_id = 3
    task_info.assembly_name = 'tests.test_tasksample'
    task_info.class_name = 'SimpleExceptionTask'
    task_info.description = 'Simple Exception Task Test'
    task_info.restartable= False

    with DbConnectionFactory.get_gyomu_db_session() as session:
        existing_record = session.query(GyomuTaskInfoCdtbl).filter(
            GyomuTaskInfoCdtbl.application_id == task_info.application_id and GyomuTaskInfoCdtbl.task_id == task_info.task_id).first()
        if existing_record is None:
            session.add(task_info)
            session.commit()
            existing_record=task_info

    yield existing_record

    with DbConnectionFactory.get_gyomu_db_session() as session:
        session.delete(existing_record)
        session.commit()

class TestTaskAccess:
    def test_create_new_task(self, status_handler_setup, register_file_mail_sender, task_info_cdtbl_setup):
        config: Configurator = status_handler_setup

        task, result = TaskAccess.create_new_task(application_id=config.application_id, task_id=1, config=config)
        print(str(result))
        assert result.is_success
        result = task.start("test Parameter", "comment test")
        print(str(result))
        assert result.is_success

    def test_create_error_task(self, status_handler_setup, register_file_mail_sender, fail_task_info_cdtbl_setup):
        config: Configurator = status_handler_setup

        task, result = TaskAccess.create_new_task(application_id=config.application_id, task_id=2, config=config)
        assert result.is_success
        result = task.start("test Parameter", "comment test")
        print(str(result))
        assert not result.is_success

    def test_create_exception_task(self, status_handler_setup, register_file_mail_sender, exception_task_info_cdtbl_setup):
        config: Configurator = status_handler_setup

        task, result = TaskAccess.create_new_task(application_id=config.application_id, task_id=3, config=config)
        assert result.is_success
        result = task.start("test Parameter", "comment test")
        print(str(result))
        assert not result.is_success