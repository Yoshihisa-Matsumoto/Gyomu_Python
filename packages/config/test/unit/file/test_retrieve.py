from pathlib import Path

from gyomu_config.file.retrieve import retrieve_config
from gyomu_config.request import ConfigRequest, _ResolvedPathRequest
from gyomu_schema.error.config import ConfigError
from pydantic import BaseModel
from pytest_mock import MockerFixture
from returns.result import Failure, Success


class SampleConfig(BaseModel):
    name: str


class TestRetrieveConfig:
    def test_success(self, mocker: MockerFixture) -> None:
        config = SampleConfig(name="test")
        path = Path("config.json")

        path_resolver = mocker.Mock()
        path_resolver.get_path.return_value = Success(path)
        retrieve_single_config_mock = mocker.patch(
            "gyomu_config.file.retrieve.retrieve_single_config",
            return_value=Success(config),
        )

        request = ConfigRequest(
            config_type=SampleConfig,
            context=None,
            path_resolver=path_resolver,
        )

        result = retrieve_config(request)

        assert isinstance(result, Success)
        assert result.unwrap() == config

        retrieve_single_config_mock.assert_called_once()

        actual_request = retrieve_single_config_mock.call_args.kwargs["request"]

        assert isinstance(actual_request, _ResolvedPathRequest)
        assert actual_request.config_type is SampleConfig
        assert actual_request.path == path

    def test_get_path_failure(self, mocker: MockerFixture) -> None:
        error = ConfigError(
            source="json",
            message="fail to resolve config path",
            phase="load",
        )

        path_resolver = mocker.Mock()
        path_resolver.get_path.return_value = Failure(error)

        retrieve_single_config_mock = mocker.patch(
            "gyomu_config.file.retrieve.retrieve_single_config",
        )

        request = ConfigRequest(
            config_type=SampleConfig,
            context=None,
            path_resolver=path_resolver,
        )

        result = retrieve_config(request)

        assert isinstance(result, Failure)
        assert result.failure() is error

        path_resolver.get_path.assert_called_once_with(None)
        retrieve_single_config_mock.assert_not_called()

    def test_retrieve_single_config_failure(self, mocker: MockerFixture) -> None:
        error = ConfigError(
            source="json",
            message="fail to resolve config path",
            phase="load",
        )

        path = Path("config.json")

        path_resolver = mocker.Mock()
        path_resolver.get_path.return_value = Success(path)

        retrieve_single_config_mock = mocker.patch(
            "gyomu_config.file.retrieve.retrieve_single_config",
            return_value=Failure(error),
        )

        request = ConfigRequest(
            config_type=SampleConfig,
            context=None,
            path_resolver=path_resolver,
        )

        result = retrieve_config(request)

        assert isinstance(result, Failure)
        assert result.failure() is error

        retrieve_single_config_mock.assert_called_once()
        return_value = retrieve_single_config_mock.return_value
        assert isinstance(return_value, Failure)
        assert return_value.failure() is error
