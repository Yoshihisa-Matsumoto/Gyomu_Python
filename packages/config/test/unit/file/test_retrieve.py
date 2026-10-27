from pathlib import Path

from gyomu_config.file.retrieve import retrieve_config
from gyomu_config.request import ConfigRequest
from gyomu_schema.error.config import ConfigError
from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
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

        exists_mock = mocker.patch.object(Path, "exists", return_value=True)
        read_json_mock = mocker.patch(
            "gyomu_config.file.retrieve.read_json",
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

        path_resolver.get_path.assert_called_once_with(None)
        exists_mock.assert_called_once_with()
        read_json_mock.assert_called_once_with(
            path=path,
            model_type=SampleConfig,
        )

    def test_config_file_not_exists(self, mocker: MockerFixture) -> None:
        path = Path("config.json")

        path_resolver = mocker.Mock()
        path_resolver.get_path.return_value = Success(path)

        exists_mock = mocker.patch.object(Path, "exists", return_value=False)
        read_json_mock = mocker.patch("gyomu_config.file.retrieve.read_json")

        request = ConfigRequest(
            config_type=SampleConfig,
            context=None,
            path_resolver=path_resolver,
        )

        result = retrieve_config(request)

        assert isinstance(result, Success)
        assert result.unwrap() is None

        path_resolver.get_path.assert_called_once_with(None)
        exists_mock.assert_called_once_with()
        read_json_mock.assert_not_called()

    def test_get_path_failure(self, mocker: MockerFixture) -> None:
        error = ConfigError(
            source="json",
            message="fail to resolve config path",
            phase="load",
        )

        path_resolver = mocker.Mock()
        path_resolver.get_path.return_value = Failure(error)

        read_json_mock = mocker.patch(
            "gyomu_config.file.retrieve.read_json",
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
        read_json_mock.assert_not_called()

    def test_read_json_failure(self, mocker: MockerFixture) -> None:
        path = Path("config.json")
        io_error = GyomuIOError(
            message="fake", layer=IOLayer.FILESYSTEM, operation=IOOperation.READ
        )

        path_resolver = mocker.Mock()
        path_resolver.get_path.return_value = Success(path)
        exists_mock = mocker.patch.object(Path, "exists", return_value=True)

        mocker.patch(
            "gyomu_config.file.retrieve.read_json",
            return_value=Failure(io_error),
        )

        request = ConfigRequest(
            config_type=SampleConfig,
            context=None,
            path_resolver=path_resolver,
        )

        result = retrieve_config(request)

        assert isinstance(result, Failure)
        assert result.failure().__cause__ == io_error
        exists_mock.assert_called_once_with()
