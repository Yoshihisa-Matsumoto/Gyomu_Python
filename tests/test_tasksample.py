import gyomu.configurator
from gyomu.status_code import StatusCode
from gyomu.tasks.simple import AbstractSimpleTask

class SimpleTask(AbstractSimpleTask):
    @property
    def application_id(self) -> int:
        return 32650

    @property
    def task_info_id(self) -> int:
        return 1

    def on_exec(self, parameter: str) -> StatusCode:
        print('Task 1 Test')
        print('Parameter: ' + parameter)
        return StatusCode.SUCCEED_STATUS


class SimpleFailTask(AbstractSimpleTask):
    @property
    def application_id(self) -> int:
        return 32650

    @property
    def task_info_id(self) -> int:
        return 2

    def on_exec(self, parameter: str) -> StatusCode:
        print('Task 1 Test')
        print('Parameter: ' + parameter)
        return StatusCode(StatusCode.INVALID_ARGUMENT_ERROR, config= self.config, description="Just a failure")


class SimpleExceptionTask(AbstractSimpleTask):
    @property
    def application_id(self) -> int:
        return 32650

    @property
    def task_info_id(self) -> int:
        return 3

    def on_exec(self, parameter: str) -> StatusCode:
        print('Task 1 Test')
        print('Parameter: ' + parameter)
        raise ValueError('Simple Value Error')

# task = SimpleTask(gyomu.configurator.BaseConfigurator())
# print(task.config.username)

