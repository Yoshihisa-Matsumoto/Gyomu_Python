from pathlib import Path

from gyomu_config.file.internal.retrieve import retrieve_single_config
from gyomu_config.request import _ResolvedPathRequest
from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from pydantic import BaseModel
from pytest_mock import MockerFixture
from returns.result import Failure, Success


class SampleConfig(BaseModel):
    name: str


class TestRetrieveSingleConfig:
    def test_success(self, mocker: MockerFixture) -> None:
        config = SampleConfig(name="test")
        path = Path("config.json")

        exists_mock = mocker.patch.object(Path, "exists", return_value=True)
        read_json_mock = mocker.patch(
            "gyomu_config.file.internal.retrieve.read_json",
            return_value=Success(config),
        )

        request = _ResolvedPathRequest(
            config_type=SampleConfig,
            path=path,
        )

        result = retrieve_single_config(request)

        assert isinstance(result, Success)
        assert result.unwrap() == config

        exists_mock.assert_called_once_with()
        read_json_mock.assert_called_once_with(
            path=path,
            model_type=SampleConfig,
        )

    def test_config_file_not_exists(self, mocker: MockerFixture) -> None:
        path = Path("config.json")

        exists_mock = mocker.patch.object(Path, "exists", return_value=False)
        read_json_mock = mocker.patch("gyomu_config.file.internal.retrieve.read_json")

        request = _ResolvedPathRequest(config_type=SampleConfig, path=path)

        result = retrieve_single_config(request)

        assert isinstance(result, Success)
        assert result.unwrap() is None

        exists_mock.assert_called_once_with()
        read_json_mock.assert_not_called()

    def test_read_json_failure(self, mocker: MockerFixture) -> None:
        path = Path("config.json")
        io_error = GyomuIOError(
            message="fake", layer=IOLayer.FILESYSTEM, operation=IOOperation.READ
        )

        exists_mock = mocker.patch.object(Path, "exists", return_value=True)

        mocker.patch(
            "gyomu_config.file.internal.retrieve.read_json",
            return_value=Failure(io_error),
        )

        request = _ResolvedPathRequest(config_type=SampleConfig, path=path)

        result = retrieve_single_config(request)

        assert isinstance(result, Failure)
        assert result.failure().__cause__ == io_error
        exists_mock.assert_called_once_with()
