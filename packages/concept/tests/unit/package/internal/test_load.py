import pytest
from gyomu_concept.error.concept import ConceptError
from gyomu_concept.package.internal.load import load_package_concept
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.package.concept import PackageConcept
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.concept.concept_test_support.helpers import (
    _create_directory_project_context,
)
from packages.schema.schema_test_support.concept_helpers import (
    create_capability_concept,
    create_package_concept,
)


class TestLoadPackageConcept:
    @pytest.fixture
    def context(self) -> ProjectContext:
        return _create_directory_project_context()

    @pytest.fixture
    def concept(self) -> PackageConcept:
        return create_package_concept(
            summary="Example package.",
            responsibilities=["Provide example functionality."],
            capabilities=[create_capability_concept()],
            usage_guidance=["usage guidance"],
            design_decisions=["design decision"],
        )

    @pytest.mark.parametrize("option", [None])
    def test_returns_none_when_concept_file_does_not_exist(
        self,
        mocker: MockerFixture,
        context: ProjectContext,
        option: ConceptOption | None,
    ) -> None:
        concept_path = mocker.Mock()
        concept_path.exists.return_value = False

        get_path = mocker.patch(
            "gyomu_concept.package.internal.load.get_package_concept_path",
            return_value=concept_path,
        )
        read = mocker.patch(
            "gyomu_concept.package.internal.load.read_json",
        )

        result = load_package_concept(
            context=context,
            option=option,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is None

        get_path.assert_called_once_with(
            context,
            option,
        )
        read.assert_not_called()

    def test_returns_loaded_concept(
        self,
        mocker: MockerFixture,
        context: ProjectContext,
        concept,
    ) -> None:
        concept_path = mocker.Mock()
        concept_path.exists.return_value = True

        mocker.patch(
            "gyomu_concept.package.internal.load.get_package_concept_path",
            return_value=concept_path,
        )

        read = mocker.patch(
            "gyomu_concept.package.internal.load.read_json",
            return_value=Success(concept),
        )

        result = load_package_concept(
            context=context,
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
    ) -> None:
        concept_path = mocker.Mock()
        concept_path.exists.return_value = True

        mocker.patch(
            "gyomu_concept.package.internal.load.get_package_concept_path",
            return_value=concept_path,
        )

        io_error = GyomuIOError(
            "Failed to read Package Concept.",
            layer=IOLayer.FILESYSTEM,
            operation=IOOperation.READ,
        )

        mocker.patch(
            "gyomu_concept.package.internal.load.read_json",
            return_value=Failure(io_error),
        )

        result = load_package_concept(
            context=context,
        )

        assert isinstance(result, Failure)

        error = result.failure()

        assert isinstance(error, ConceptError)
        assert error.message == "fail to load Package Concept"
        assert error.file_path == concept_path
        assert error.package_name == context.config.name
        assert error.phase == "package-concept"
        assert error.identity is None
        assert error.__cause__ is io_error
