import importlib

import gyomu.configurator
from gyomu.tasks.abstract_base_task import AbstractBaseTask
from gyomu.db_connection_factory import DbConnectionFactory
from gyomu.gyomu_db_model import GyomuTaskInfoCdtbl
from gyomu.configurator import Configurator
from sqlalchemy.exc import NoResultFound
from gyomu.status_code import StatusCode
from gyomu.common_status_code import CommonStatusCode
from gyomu.holidays import MarketDateAccess
import click
import os
from datetime import date, datetime


class TaskAccess:

    @staticmethod
    def create_new_task(application_id: int, task_id: int, config: Configurator = None) -> (
            AbstractBaseTask, StatusCode):
        task_info: GyomuTaskInfoCdtbl
        try:
            if config is None:
                config = gyomu.configurator.ConfigurationFactory.get_instance()
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
                                    arguments=[module_name, class_name], exception=ex,
                                    config=config, target_application_id=config.application_id)


@click.command()
@click.option('--application-id', '-a', 'application_id', help='Application ID', type=int, default=-1)
@click.option('--task-id', '-t', 'task_id', help='Task ID', type=int, default=-1)
@click.option('--parameter', '-p', help='Parameter', type=str, default='')
@click.option('--register/--no-register', help='Do you want to register Task?', type=bool, default=False)
@click.option('--file', '-f', help='File name to register, or to read parameter', default='')
@click.option('--start-date', '-s', 'start_date',
              help='Target Date to execute. If end date is specified, it\'s regarded as start date', type=str)
@click.option('--end-date', '-e', 'end_date', help='End Date', type=str, default='')
@click.option('--market', '-m', help='Region to use on market holiday', type=str, default='')
def __cmd(application_id: int, task_id: int, parameter: str, register: bool, file: str, start_date: str, end_date: str,
          market: str):
    if register:
        if file == '':
            # TODO
            click.echo('To register task, need to specify target module using format on import statement or '
                       'folder containing target classes/modules')
            return
        pass
    else:
        task: AbstractBaseTask
        result: StatusCode
        if application_id == -1 or task_id == -1:
            click.echo('Need to specify valid task information. Application ID , Task ID')
            return
        if parameter != '':
            if file != '':
                click.echo('Need to specify either parameter or file as both contains parameter to use')
                return
            result = __execute_task(application_id, task_id, parameter)
            click.echo(str(result))
            return
        elif file != '':
            if not os.path.exists(file):
                click.echo('You need to specify valid filename')
                return
            with open(file, 'r') as f:
                parameter = f.read()
            result = __execute_task(application_id, task_id, parameter)
            click.echo(str(result))
            return
        elif start_date == '' or len(start_date) != 8 or not start_date.isdigit():
            click.echo('Need to specify target/start date to execute as yyyymmdd format')
            return
        else:
            if end_date == '':
                result = __execute_task(application_id, task_id, start_date)
                click.echo(str(result))
                return
            elif len(end_date) != 8 or not end_date.isdigit() or market == '':
                click.echo('Need to specify target/start date to execute as yyyymmdd format')
                click.echo(' And you need to specify market to check holiday')
                return
            else:
                market_access = MarketDateAccess(market=market)
                target_date = datetime.strptime(start_date, '%Y%m%d')
                end_date = datetime.strptime(end_date, '%Y%m%d')
                while target_date <= end_date:
                    click.echo("parameter: " + target_date.strftime('%Y%m%d'))
                    result = __execute_task(application_id, task_id, start_date)
                    if not result.is_success:
                        click.echo(str(result))
                        return
                    target_date = market_access.get_business_day(target_date, 1)


def __execute_task(application_id: int, task_id: int, parameter: str) -> StatusCode:
    task, result = TaskAccess.create_new_task(application_id=application_id, task_id=task_id)
    if not result.is_success:
        return result
    return task.start(parameter, '')


def __main():
    __cmd()


if __name__ == '__main__':
    __main()
