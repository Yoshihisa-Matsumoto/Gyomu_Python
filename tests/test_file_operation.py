import time

import pytest
from gyomu.configurator import Configurator, ConfigurationFactory
from gyomu.file_operation import FileOperation
import os
from gyomu.process import ManagedProcess
from threading import Thread
import datetime


@pytest.fixture()
def file_open_as_readonly(setup_test_files):
    source_dir = os.path.join(setup_test_files, 'source')
    source_file = open(os.path.join(source_dir, 'README.md'), 'r')
    yield
    with source_file:
        pass

def _other_process_lock(file_name):
    config: Configurator = ConfigurationFactory.get_instance()
    process1 = ManagedProcess(target=_other_lock, args=(file_name,))
    process1.start_managed_process(config)
    time.sleep(2)
    with FileOperation.lock_process(file_name, config):
        print('PID:' + str(config.unique_instance_id_per_machine) + '  ' + 'Other Process File Lock' + str(
            datetime.datetime.now()))
        time.sleep(3)
    print('PID:' + str(config.unique_instance_id_per_machine) + '  ' + 'Other Process File Unlock' + str(
        datetime.datetime.now()))
    process1.join()

def _other_lock(file_name):
    config: Configurator = ConfigurationFactory.get_instance()
    print('PID:' + str(config.unique_instance_id_per_machine) + '  ' + 'Other Thread Start' + str(datetime.datetime.now()))
    with FileOperation.lock_process(file_name, config):
        print('PID:' + str(config.unique_instance_id_per_machine) + '  ' + 'Other Thread File Lock' + str(datetime.datetime.now()))
        time.sleep(5)
    print('PID:' + str(config.unique_instance_id_per_machine) + '  ' + 'Other Thread File Unlock' + str(datetime.datetime.now()))
    time.sleep(1)


class TestFileOperation:
    def test_file_can_access(self, status_handler_setup, setup_test_files):
        config: Configurator = status_handler_setup
        source_dir = os.path.join(setup_test_files, 'source')
        source_file = os.path.join(source_dir, 'README.md')
        assert FileOperation.can_access(source_file, False)

    def test_file_can_access_readonly(self, status_handler_setup, setup_test_files, file_open_as_readonly):
        config: Configurator = status_handler_setup
        source_dir = os.path.join(setup_test_files, 'source')
        source_file = os.path.join(source_dir, 'README.md')
        assert FileOperation.can_access(source_file, True)
        assert not FileOperation.can_access(source_file, False)

    def test_file_lock(self, status_handler_setup, setup_test_files):
        config: Configurator = status_handler_setup
        source_dir = os.path.join(setup_test_files, 'source')
        source_file = os.path.join(source_dir, 'README.md')
        with FileOperation.lock_process(source_file,config) as file_lock:
            pass

    def test_file_lock2(self, status_handler_setup, setup_test_files):
        config: Configurator = status_handler_setup
        print('Main Thread Start' + str(datetime.datetime.now()))
        source_dir = os.path.join(setup_test_files, 'source')
        source_file = os.path.join(source_dir, 'README.md')
        thread1 = Thread(target=_other_lock, args=(source_file,))
        thread1.start()
        time.sleep(2)
        with FileOperation.lock_process(source_file,config):
            print('Main Thread File Lock' + str(datetime.datetime.now()))
            time.sleep(3)
        print('Main Thread File Unlock' + str(datetime.datetime.now()))
        thread1.join()

    def test_file_lock3(self, status_handler_setup, setup_test_files):
        config: Configurator = status_handler_setup
        print('PID:' + str(config.unique_instance_id_per_machine) + '  ' + 'Main Thread Start' + str(datetime.datetime.now()))
        source_dir = os.path.join(setup_test_files, 'source')
        source_file = os.path.join(source_dir, 'README.md')
        thread1 = ManagedProcess(target=_other_lock, args=(source_file,))
        thread1.start_managed_process(config)
        time.sleep(2)
        with FileOperation.lock_process(source_file,config):
            print('PID:' + str(config.unique_instance_id_per_machine) + '  ' + 'Main Thread File Lock' + str(datetime.datetime.now()))
            time.sleep(3)
        print('PID:' + str(config.unique_instance_id_per_machine) + '  ' + 'Main Thread File Unlock' + str(datetime.datetime.now()))
        thread1.join()

    def test_file_lock4(self, status_handler_setup, setup_test_files):
        config: Configurator = status_handler_setup
        print('PID:' + str(config.unique_instance_id_per_machine) + '  ' + 'Main Thread Start' + str(datetime.datetime.now()))
        source_dir = os.path.join(setup_test_files, 'source')
        source_file = os.path.join(source_dir, 'README.md')
        thread1 = ManagedProcess(target=_other_process_lock, args=(source_file,))
        thread1.start_managed_process(config)
        time.sleep(2)
        with FileOperation.lock_process(source_file,config):
            print('PID:' + str(config.unique_instance_id_per_machine) + '  ' + 'Main Thread File Lock' + str(datetime.datetime.now()))
            time.sleep(3)
        print('PID:' + str(config.unique_instance_id_per_machine) + '  ' + 'Main Thread File Unlock' + str(datetime.datetime.now()))
        thread1.join()
