from gyomu.parameter_access import ParameterAccess
import os
import pytest
from gyomu.db_connection_factory import DbConnectionFactory, GYOMU_COMMON_MAINDB_TYPE, DbType, GYOMU_COMMON_MAINDB_CONNECTION


@pytest.fixture(scope='module')
def set_env() -> str:
    os.environ[GYOMU_COMMON_MAINDB_CONNECTION] = "postgresql://postgres:password@localhost:5432/gyomu"
    yield 'pre set done'
    os.environ[GYOMU_COMMON_MAINDB_CONNECTION] = ""

def test_get_string_value(set_env):
    test_items = [
        ('test', 'TestValue'),
        ('test2', 'Test2Value'),
        ('test', "TestValue3")
    ]
    for i, (key, value) in enumerate(test_items):
        ParameterAccess.set_string_value(key,value)
        assert ParameterAccess.get_string_value(key)==value

    for i, (key, value) in enumerate(test_items):
        ParameterAccess.set_string_value(key,"")


    test_int_items =[
        ['intTest',133],
        ['intTest2',234],
        ['intTest',33445]
    ]

    for item in test_int_items:
        int_value = item[1]
        ParameterAccess.set_int_value(item[0],int_value)
        assert ParameterAccess.get_int_value(item[0])==int_value

    for item in test_int_items:
        ParameterAccess.set_string_value(item[0], "")

    test_bool_items =[
        ['boolTest',False],
        ['boolTest2',False],
        ['boolTest',True]
    ]

    for item in test_bool_items:
        bool_value = item[1]
        ParameterAccess.set_bool_value(item[0],bool_value)
        assert ParameterAccess.get_bool_value(item[0])==bool_value

    for item in test_bool_items:
        ParameterAccess.set_string_value(item[0], "")

    for i, (key, value) in enumerate(test_items):
        ParameterAccess.set_base64_encoded_value(key,value)
        assert ParameterAccess.get_base64_encoded_value(key)==value

    for i, (key, value) in enumerate(test_items):
        ParameterAccess.set_string_value(key,"")

def test_set_string_value():
    assert False
