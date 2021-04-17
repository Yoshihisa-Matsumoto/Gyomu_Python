from multiprocessing import Process
from gyomu.configurator import Configurator, ConfigurationFactory
from gyomu.status_code import StatusCode


class ManagedProcess(Process):
    shared_dictionary: dict

    def run(self):
        config = ConfigurationFactory.get_instance(shared_dictionary=self.shared_dictionary)
        StatusCode.debug('Process Init', config)
        if self._target:
            self._target(*self._args, **self._kwargs)

    def start_managed_process(self, config: Configurator):
        self.shared_dictionary = config.shared_dictionary
        super().start()
