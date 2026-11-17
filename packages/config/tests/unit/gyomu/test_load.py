from pathlib import Path

from gyomu_config.gyomu.load import load_gyomu_config_section
from gyomu_schema.error.config import ConfigError
from pydantic import BaseModel
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.schema.test_support.helpers import create_config_error


class ConfigTestConfig(BaseModel):
    enabled: bool


class TestLoadGyomuConfigSection:
    def test_success(self, mocker: MockerFixture) -> None:
        file_path = Path("/mock/config.json")
        mocker.patch(
            "gyomu_config.gyomu.load.resolve_gyomu_config_path",
            return_value=file_path,
        )
        mocker.patch("pathlib.Path.exists", return_value=True)
        read_json_data_mock = mocker.patch(
            "gyomu_config.gyomu.load.read_json_data",
            return_value=Success(
                {
                    "test": {
                        "interaction": {
                            "enabled": True,
                        }
                    }
                }
            ),
        )
        default = ConfigTestConfig(enabled=False)

        result = load_gyomu_config_section(
            section_name="test.interaction",
            model_type=ConfigTestConfig,
            default=default,
        )

        assert isinstance(result, Success)
        assert result.unwrap() == ConfigTestConfig(enabled=True)
        read_json_data_mock.assert_called_once_with(file_path)

    def test_file_not_exists(self, mocker: MockerFixture) -> None:
        mocker.patch(
            "gyomu_config.gyomu.load.resolve_gyomu_config_path",
            return_value=Path("/mock/config.json"),
        )
        mocker.patch("pathlib.Path.exists", return_value=False)
        read_json_data_mock = mocker.patch(
            "gyomu_config.gyomu.load.read_json_data",
        )
        default = ConfigTestConfig(enabled=False)

        result = load_gyomu_config_section(
            section_name="test.interaction",
            model_type=ConfigTestConfig,
            default=default,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is default
        read_json_data_mock.assert_not_called()

    def test_read_json_data_failure(self, mocker: MockerFixture) -> None:
        file_path = Path("/mock/config.json")
        mocker.patch(
            "gyomu_config.gyomu.load.resolve_gyomu_config_path",
            return_value=file_path,
        )
        mocker.patch("pathlib.Path.exists", return_value=True)

        read_json_data_mock = mocker.patch(
            "gyomu_config.gyomu.load.read_json_data",
            return_value=Failure(create_config_error()),
        )
        default = ConfigTestConfig(enabled=False)

        result = load_gyomu_config_section(
            section_name="test.interaction",
            model_type=ConfigTestConfig,
            default=default,
        )

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), ConfigError)
        assert result.failure().message == "fail to read gyomu config"
        assert result.failure().phase == "load"
        assert result.failure().source == "json"
        read_json_data_mock.assert_called_once_with(file_path)

    def test_section_not_exists(self, mocker: MockerFixture) -> None:
        file_path = Path("/mock/config.json")
        mocker.patch(
            "gyomu_config.gyomu.load.resolve_gyomu_config_path",
            return_value=file_path,
        )
        mocker.patch("pathlib.Path.exists", return_value=True)
        read_json_data_mock = mocker.patch(
            "gyomu_config.gyomu.load.read_json_data",
            return_value=Success({"test": {}}),
        )
        default = ConfigTestConfig(enabled=False)

        result = load_gyomu_config_section(
            section_name="test.interaction",
            model_type=ConfigTestConfig,
            default=default,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is default
        read_json_data_mock.assert_called_once_with(file_path)

    def test_section_is_not_dict(self, mocker: MockerFixture) -> None:
        file_path = Path("/mock/config.json")
        mocker.patch(
            "gyomu_config.gyomu.load.resolve_gyomu_config_path",
            return_value=file_path,
        )
        mocker.patch("pathlib.Path.exists", return_value=True)
        read_json_data_mock = mocker.patch(
            "gyomu_config.gyomu.load.read_json_data",
            return_value=Success({"test": True}),
        )
        default = ConfigTestConfig(enabled=False)

        result = load_gyomu_config_section(
            section_name="test.interaction",
            model_type=ConfigTestConfig,
            default=default,
        )

        assert isinstance(result, Failure)
        error = result.failure()
        assert isinstance(error, ConfigError)
        assert error.message == "Expected a JSON object at the section."
        assert error.phase == "path-resolve"
        assert error.source == "json"
        assert error.details == {
            "section": "test",
            "total-section-name": "test.interaction",
        }
        read_json_data_mock.assert_called_once_with(file_path)

    def test_empty_section_name(self, mocker: MockerFixture) -> None:
        file_path = Path("/mock/config.json")
        mocker.patch(
            "gyomu_config.gyomu.load.resolve_gyomu_config_path",
            return_value=file_path,
        )
        mocker.patch("pathlib.Path.exists", return_value=True)
        read_json_data_mock = mocker.patch(
            "gyomu_config.gyomu.load.read_json_data",
            return_value=Success({"test": {"interaction": {"enabled": True}}}),
        )
        default = ConfigTestConfig(enabled=False)

        result = load_gyomu_config_section(
            section_name="",
            model_type=ConfigTestConfig,
            default=default,
        )

        assert isinstance(result, Failure)
        error = result.failure()
        assert isinstance(error, ConfigError)
        assert error.message == "Invalid config section path."
        assert error.phase == "path-resolve"
        assert error.source == "json"
        assert error.details == {"section_name": ""}
        read_json_data_mock.assert_called_once_with(file_path)

    def test_section_name_contains_empty_segment(self, mocker: MockerFixture) -> None:
        file_path = Path("/mock/config.json")
        mocker.patch(
            "gyomu_config.gyomu.load.resolve_gyomu_config_path",
            return_value=file_path,
        )
        mocker.patch("pathlib.Path.exists", return_value=True)
        read_json_data_mock = mocker.patch(
            "gyomu_config.gyomu.load.read_json_data",
            return_value=Success({"test": {"interaction": {"enabled": True}}}),
        )
        default = ConfigTestConfig(enabled=False)

        result = load_gyomu_config_section(
            section_name="test..interaction",
            model_type=ConfigTestConfig,
            default=default,
        )

        assert isinstance(result, Failure)
        error = result.failure()
        assert isinstance(error, ConfigError)
        assert error.message == "Invalid config section path."
        assert error.phase == "path-resolve"
        assert error.source == "json"
        assert error.details == {"section_name": "test..interaction"}
        read_json_data_mock.assert_called_once_with(file_path)

    def test_validation_failure(self, mocker: MockerFixture) -> None:
        file_path = Path("/mock/config.json")
        mocker.patch(
            "gyomu_config.gyomu.load.resolve_gyomu_config_path",
            return_value=file_path,
        )
        mocker.patch("pathlib.Path.exists", return_value=True)
        read_json_data_mock = mocker.patch(
            "gyomu_config.gyomu.load.read_json_data",
            return_value=Success({"test": {"interaction": {"enabled": "invalid"}}}),
        )
        default = ConfigTestConfig(enabled=False)

        result = load_gyomu_config_section(
            section_name="test.interaction",
            model_type=ConfigTestConfig,
            default=default,
        )

        assert isinstance(result, Failure)
        error = result.failure()
        assert isinstance(error, ConfigError)
        assert error.message == "fail to parse gyomu config"
        assert error.phase == "validate"
        assert error.source == "json"
        read_json_data_mock.assert_called_once_with(file_path)

    def test_empty_section_data(self, mocker: MockerFixture) -> None:
        file_path = Path("/mock/config.json")
        mocker.patch(
            "gyomu_config.gyomu.load.resolve_gyomu_config_path",
            return_value=file_path,
        )
        mocker.patch("pathlib.Path.exists", return_value=True)
        read_json_data_mock = mocker.patch(
            "gyomu_config.gyomu.load.read_json_data",
            return_value=Success({"test": {"interaction": {}}}),
        )
        default = ConfigTestConfig(enabled=False)

        result = load_gyomu_config_section(
            section_name="test.interaction",
            model_type=ConfigTestConfig,
            default=default,
        )

        assert isinstance(result, Failure)
        error = result.failure()
        assert isinstance(error, ConfigError)
        assert error.message == "fail to parse gyomu config"
        assert error.phase == "validate"
        assert error.source == "json"
        read_json_data_mock.assert_called_once_with(file_path)
