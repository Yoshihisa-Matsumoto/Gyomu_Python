from pathlib import Path
from unittest.mock import Mock

from gyomu_schema.schemas.config.test.model_defaults import ModelDefaults
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_test.helper.inventory.update_default import update_model_default
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.python_analysis.test_support.helpers import create_project_context
from packages.schema.test_support.helpers import (
    create_declaration_identity,
    create_file_analysis_context,
    create_gyomu_error,
    create_model_default,
)


class TestUpdateModelDefault:
    def test_returns_failure_when_loading_file_context_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        project_context = create_project_context()
        target_identity = create_declaration_identity()
        model_default = create_model_default()
        error = create_gyomu_error()

        mocker.patch(
            "gyomu_test.helper.inventory.update_default.get_project_relative_path",
            return_value=ProjectRelativePath(Path("models.py")),
        )
        mocker.patch(
            "gyomu_test.helper.inventory.update_default.load_file_analysis_context",
            return_value=Failure(error),
        )
        retrieve_mock = mocker.patch(
            "gyomu_test.helper.inventory.update_default.retrieve_config"
        )
        save_mock = mocker.patch(
            "gyomu_test.helper.inventory.update_default.save_config"
        )

        # Act
        result = update_model_default(
            project_context=project_context,
            target_identity=target_identity,
            model_default=model_default,
        )

        # Assert
        assert isinstance(result, Failure)
        assert result.failure().message == "fail to load source"
        retrieve_mock.assert_not_called()
        save_mock.assert_not_called()

    def test_returns_failure_when_retrieving_config_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        project_context = create_project_context()
        target_identity = create_declaration_identity()
        model_default = create_model_default()
        error = create_gyomu_error()

        file_analysis = create_file_analysis_context()
        mocker.patch(
            "gyomu_test.helper.inventory.update_default.get_project_relative_path",
            return_value=ProjectRelativePath(Path("models.py")),
        )
        mocker.patch(
            "gyomu_test.helper.inventory.update_default.load_file_analysis_context",
            return_value=Success(file_analysis),
        )
        mocker.patch(
            "gyomu_test.helper.inventory.update_default.build_config_request",
            return_value=Mock(),
        )
        mocker.patch(
            "gyomu_test.helper.inventory.update_default.retrieve_config",
            return_value=Failure(error),
        )
        save_mock = mocker.patch(
            "gyomu_test.helper.inventory.update_default.save_config"
        )

        # Act
        result = update_model_default(
            project_context=project_context,
            target_identity=target_identity,
            model_default=model_default,
        )

        # Assert
        assert isinstance(result, Failure)
        assert result.failure().message == "fail to retrieve "
        save_mock.assert_not_called()

    def test_saves_model_default_when_config_does_not_exist(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        project_context = create_project_context()
        target_identity = create_declaration_identity()
        model_default = create_model_default()
        file_analysis = create_file_analysis_context()
        config_request = Mock()

        mocker.patch(
            "gyomu_test.helper.inventory.update_default.get_project_relative_path",
            return_value=ProjectRelativePath(Path("models.py")),
        )
        mocker.patch(
            "gyomu_test.helper.inventory.update_default.load_file_analysis_context",
            return_value=Success(file_analysis),
        )
        mocker.patch(
            "gyomu_test.helper.inventory.update_default.build_config_request",
            return_value=config_request,
        )
        mocker.patch(
            "gyomu_test.helper.inventory.update_default.retrieve_config",
            return_value=Success(None),
        )
        save_mock = mocker.patch(
            "gyomu_test.helper.inventory.update_default.save_config",
            return_value=Success(None),
        )

        # Act
        result = update_model_default(
            project_context=project_context,
            target_identity=target_identity,
            model_default=model_default,
        )

        # Assert
        assert result == Success(None)
        save_mock.assert_called_once_with(
            request=config_request,
            value=ModelDefaults(models=(model_default,)),
        )

    def test_appends_model_default_to_existing_config(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        project_context = create_project_context()
        target_identity = create_declaration_identity()
        existing_model_default = create_model_default()
        new_model_default = create_model_default()
        existing_config = ModelDefaults(models=(existing_model_default,))
        file_analysis = create_file_analysis_context()
        config_request = Mock()

        mocker.patch(
            "gyomu_test.helper.inventory.update_default.get_project_relative_path",
            return_value=ProjectRelativePath(Path("models.py")),
        )
        mocker.patch(
            "gyomu_test.helper.inventory.update_default.load_file_analysis_context",
            return_value=Success(file_analysis),
        )
        mocker.patch(
            "gyomu_test.helper.inventory.update_default.build_config_request",
            return_value=config_request,
        )
        mocker.patch(
            "gyomu_test.helper.inventory.update_default.retrieve_config",
            return_value=Success(existing_config),
        )
        save_mock = mocker.patch(
            "gyomu_test.helper.inventory.update_default.save_config",
            return_value=Success(None),
        )

        # Act
        result = update_model_default(
            project_context=project_context,
            target_identity=target_identity,
            model_default=new_model_default,
        )

        # Assert
        assert result == Success(None)
        save_mock.assert_called_once_with(
            request=config_request,
            value=ModelDefaults(
                models=(existing_model_default, new_model_default),
            ),
        )

    def test_returns_failure_when_saving_config_fails(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        project_context = create_project_context()
        target_identity = create_declaration_identity()
        model_default = create_model_default()
        file_analysis = create_file_analysis_context()
        config_request = Mock()
        error = create_gyomu_error()

        mocker.patch(
            "gyomu_test.helper.inventory.update_default.get_project_relative_path",
            return_value=ProjectRelativePath(Path("models.py")),
        )
        mocker.patch(
            "gyomu_test.helper.inventory.update_default.load_file_analysis_context",
            return_value=Success(file_analysis),
        )
        mocker.patch(
            "gyomu_test.helper.inventory.update_default.build_config_request",
            return_value=config_request,
        )
        mocker.patch(
            "gyomu_test.helper.inventory.update_default.retrieve_config",
            return_value=Success(None),
        )
        mocker.patch(
            "gyomu_test.helper.inventory.update_default.save_config",
            return_value=Failure(error),
        )

        # Act
        result = update_model_default(
            project_context=project_context,
            target_identity=target_identity,
            model_default=model_default,
        )

        # Assert
        assert isinstance(result, Failure)
        assert result.failure().message == "fail to save config"

    def test_builds_config_request_from_file_analysis(
        self,
        mocker: MockerFixture,
    ) -> None:
        # Arrange
        project_context = create_project_context()
        target_identity = create_declaration_identity()
        model_default = create_model_default()
        file_analysis = create_file_analysis_context()
        config_request = Mock()

        mocker.patch(
            "gyomu_test.helper.inventory.update_default.get_project_relative_path",
            return_value=ProjectRelativePath(Path("models.py")),
        )
        mocker.patch(
            "gyomu_test.helper.inventory.update_default.load_file_analysis_context",
            return_value=Success(file_analysis),
        )
        build_mock = mocker.patch(
            "gyomu_test.helper.inventory.update_default.build_config_request",
            return_value=config_request,
        )
        mocker.patch(
            "gyomu_test.helper.inventory.update_default.retrieve_config",
            return_value=Success(None),
        )
        mocker.patch(
            "gyomu_test.helper.inventory.update_default.save_config",
            return_value=Success(None),
        )

        # Act
        result = update_model_default(
            project_context=project_context,
            target_identity=target_identity,
            model_default=model_default,
        )

        # Assert
        assert result == Success(None)
        build_mock.assert_called_once_with(
            file_analysis=file_analysis,
            project_context=project_context,
        )
