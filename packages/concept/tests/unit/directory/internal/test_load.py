from pathlib import Path

import pytest
from gyomu_concept.directory.internal.load import load_directory_concept
from gyomu_concept.error.concept import ConceptError
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.directory.concept import DirectoryImportance
from gyomu_schema.schemas.python.types import ProjectRelativePath
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.concept.concept_test_support.helpers import (
    _create_directory_project_context,
)
from packages.schema.schema_test_support.concept_helpers import (
    create_directory_concept,
)


class TestLoadDirectoryConcept:
    @pytest.fixture
    def context(self) -> ProjectContext:
        return _create_directory_project_context()

    @pytest.fixture
    def target_directory(self) -> ProjectRelativePath:
        return ProjectRelativePath(Path("src/example"))

    @pytest.fixture
    def concept(self):
        return create_directory_concept(
            summary="Example directory.",
            responsibilities=["Provide example functionality."],
            concepts=["Example"],
            relationships=["Example depends on internal implementation."],
            design_decisions=["Keep the directory focused on example functionality."],
            importance=DirectoryImportance.CORE,
        )

    @pytest.mark.parametrize("option", [None])
    def test_returns_none_when_concept_file_does_not_exist(
        self,
        mocker: MockerFixture,
        context: ProjectContext,
        target_directory: ProjectRelativePath,
        option: ConceptOption | None,
    ) -> None:
        concept_path = mocker.Mock()
        concept_path.exists.return_value = False

        get_path = mocker.patch(
            "gyomu_concept.directory.internal.load.get_directory_concept_path",
            return_value=concept_path,
        )
        read = mocker.patch(
            "gyomu_concept.directory.internal.load.read_json",
        )

        result = load_directory_concept(
            context=context,
            target_directory=target_directory,
            option=option,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is None

        get_path.assert_called_once_with(
            context,
            target_directory,
            option,
        )
        read.assert_not_called()

    def test_returns_loaded_concept(
        self,
        mocker: MockerFixture,
        context: ProjectContext,
        target_directory: ProjectRelativePath,
        concept,
    ) -> None:
        concept_path = mocker.Mock()
        concept_path.exists.return_value = True

        mocker.patch(
            "gyomu_concept.directory.internal.load.get_directory_concept_path",
            return_value=concept_path,
        )

        read = mocker.patch(
            "gyomu_concept.directory.internal.load.read_json",
            return_value=Success(concept),
        )

        result = load_directory_concept(
            context=context,
            target_directory=target_directory,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is concept

        read.assert_called_once_with(
            path=concept_path,
            model_type=type(concept),
        )

    def test_returns_concept_error_on_read_failure(
        self,
        mocker: MockerFixture,
        context: ProjectContext,
        target_directory: ProjectRelativePath,
    ) -> None:
        concept_path = mocker.Mock()
        concept_path.exists.return_value = True

        mocker.patch(
            "gyomu_concept.directory.internal.load.get_directory_concept_path",
            return_value=concept_path,
        )

        io_error = GyomuIOError(
            "Failed to read Directory Concept.",
            layer=IOLayer.FILESYSTEM,
            operation=IOOperation.READ,
        )

        mocker.patch(
            "gyomu_concept.directory.internal.load.read_json",
            return_value=Failure(io_error),
        )

        result = load_directory_concept(
            context=context,
            target_directory=target_directory,
        )

        assert isinstance(result, Failure)

        error = result.failure()

        assert isinstance(error, ConceptError)
        assert error.message == "fail to load Directory Concept"
        assert error.file_path == target_directory
        assert error.package_name == context.config.name
        assert error.phase == "directory-summary"
        assert error.identity is None
        assert error.__cause__ is io_error
