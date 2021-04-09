import importlib

from gyomu.tasks.abstract_base_task import AbstractBaseTask
from gyomu.db_connection_factory import DbConnectionFactory
from gyomu.gyomu_db_model import GyomuTaskInfoCdtbl
from gyomu.configurator import Configurator
from sqlalchemy.exc import NoResultFound
from gyomu.status_code import StatusCode
from gyomu.common_status_code import CommonStatusCode

class TaskAccess:

    @staticmethod
    def create_new_task(application_id: int, task_id: int, config: Configurator) -> (AbstractBaseTask, StatusCode):
        task_info: GyomuTaskInfoCdtbl
        try:
            with DbConnectionFactory.get_gyomu_db_session() as session:
                task_info = session.query(GyomuTaskInfoCdtbl).filter(GyomuTaskInfoCdtbl.application_id == application_id
                                                                     and GyomuTaskInfoCdtbl.task_id == task_id).one()

        except NoResultFound:
            return None, StatusCode(error_id=CommonStatusCode.TASK_NOT_REGISTERED,
                                       arguments=[application_id, task_id],
                                       config=config, target_application_id=application_id)

        if task_info is not None:
            return TaskAccess.__create_new_task(task_info, config)

    @staticmethod
    def __create_new_task(task_info: GyomuTaskInfoCdtbl, config: Configurator) -> (AbstractBaseTask, StatusCode):
        return TaskAccess.__create_instance(task_info.assembly_name, task_info.class_name, config)

    @staticmethod
    def __create_instance(module_name: str, class_name: str, config: Configurator) -> (AbstractBaseTask, StatusCode):
        try:

            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)
            task: AbstractBaseTask = cls(config)
            return task, StatusCode.SUCCEED_STATUS
        except Exception as ex:
            return None, StatusCode(CommonStatusCode.TASK_CLASS_CREATE_ERROR,
                                    arguments=[module_name, class_name], exception= ex,
                                    config=config, target_application_id=config.application_id)
