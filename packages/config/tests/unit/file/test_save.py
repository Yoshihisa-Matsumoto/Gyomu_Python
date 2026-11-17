from pathlib import Path

from gyomu_config.file.save import save_config
from gyomu_config.request import ConfigRequest
from gyomu_schema.error.config import ConfigError
from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from pydantic import BaseModel
from pytest_mock import MockerFixture
from returns.result import Failure, Success


class SampleConfig(BaseModel):
    name: str


class TestSaveConfig:
    def test_success(self, mocker: MockerFixture) -> None:
        path = Path("config.json")
        config = SampleConfig(name="test")

        path_resolver = mocker.Mock()
        path_resolver.get_path.return_value = Success(path)

        write_json_mock = mocker.patch(
            "gyomu_config.file.save.write_json",
            return_value=Success(None),
        )

        request = ConfigRequest(
            config_type=SampleConfig,
            context=None,
            path_resolver=path_resolver,
        )

        result = save_config(request, config)

        assert isinstance(result, Success)
        assert result.unwrap() is None

        path_resolver.get_path.assert_called_once_with(None)
        write_json_mock.assert_called_once_with(
            path=path,
            value=config,
            value_type=SampleConfig,
        )

    def test_get_path_failure(self, mocker: MockerFixture) -> None:
        error = ConfigError(
            source="json",
            message="fail to resolve config path",
            phase="save",
        )

        path_resolver = mocker.Mock()
        path_resolver.get_path.return_value = Failure(error)

        write_json_mock = mocker.patch(
            "gyomu_config.file.save.write_json",
        )

        request = ConfigRequest(
            config_type=SampleConfig,
            context=None,
            path_resolver=path_resolver,
        )

        result = save_config(request, SampleConfig(name="test"))

        assert isinstance(result, Failure)
        assert result.failure() is error

        path_resolver.get_path.assert_called_once_with(None)
        write_json_mock.assert_not_called()

    def test_write_json_failure(self, mocker: MockerFixture) -> None:
        path = Path("config.json")
        config = SampleConfig(name="test")

        # write_json が返す実際のエラー型に置き換える
        io_error = GyomuIOError(
            message="fake", layer=IOLayer.FILESYSTEM, operation=IOOperation.WRITE
        )

        path_resolver = mocker.Mock()
        path_resolver.get_path.return_value = Success(path)

        mocker.patch(
            "gyomu_config.file.save.write_json",
            return_value=Failure(io_error),
        )

        request = ConfigRequest(
            config_type=SampleConfig,
            context=None,
            path_resolver=path_resolver,
        )

        result = save_config(request, config)

        assert isinstance(result, Failure)

        # ConfigError.chain() の仕様に合わせて検証する
        save_error = result.failure()
        assert isinstance(save_error, ConfigError)
        assert save_error.source == "json"
        assert save_error.message == "fail to save config file"
        assert save_error.phase == "save"
        assert save_error.__cause__ == io_error

        path_resolver.get_path.assert_called_once_with(None)
