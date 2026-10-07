from pathlib import Path

import pytest
from gyomu_concept.document.context import (
    DocumentBaseContextResult,
    initialize_document_base_context,
)
from gyomu_concept.error.document import DocumentBuilderError
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.error.base import BaseError
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.base import DocumentBaseContext, Knowledge
from gyomu_schema.schemas.knowledge.development import Development
from gyomu_schema.schemas.knowledge.package import Package
from gyomu_schema.schemas.knowledge.roadmap import Roadmap
from gyomu_schema.schemas.knowledge.technical import Technical
from gyomu_schema.schemas.types import FullPath
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.concept.concept_test_support.helpers import (
    _create_directory_project_context,
)
from packages.schema.schema_test_support.concept_helpers import (
    create_development,
    create_package,
    create_package_analysis__default,
    create_package_concept,
    create_roadmap,
    create_technical,
)


@pytest.fixture
def project() -> ProjectContext:
    return _create_directory_project_context()


class TestInitializeDocumentBaseContext:
    async def test_builds_context(
        self, mocker: MockerFixture, project: ProjectContext
    ) -> None:
        context = project
        option = ConceptOption()

        analysis = create_package_analysis__default()
        concept = create_package_concept()
        package = create_package(
            mission="Mission",
            policies=("Policy",),
            display_name="Display Name",
        )
        development = create_development()
        technical = create_technical()
        roadmap = create_roadmap()

        knowledge_path = FullPath(Path(".gyomu/knowledge"))

        mock_build_analysis = mocker.patch(
            "gyomu_concept.document.context.build_package_analysis",
            return_value=Success(analysis),
        )
        mock_load_concept = mocker.patch(
            "gyomu_concept.document.context.load_package_concept",
            return_value=Success(concept),
        )
        mock_get_knowledge_path = mocker.patch(
            "gyomu_concept.document.context.get_knowledge_path",
            return_value=knowledge_path,
        )
        mock_read_yaml = mocker.patch(
            "gyomu_concept.document.context.read_yaml",
            side_effect=[
                Success(package),
                Success(development),
                Success(technical),
                Success(roadmap),
            ],
        )

        result = initialize_document_base_context(context, option)

        assert result == Success(
            DocumentBaseContextResult(
                context=DocumentBaseContext(
                    analysis=analysis,
                    concept=concept,
                    knowledge=Knowledge(
                        package=package,
                        development=development,
                        technical=technical,
                        roadmap=roadmap,
                    ),
                ),
                knowledge_path=knowledge_path,
            )
        )

        mock_build_analysis.assert_called_once_with(context, option)
        mock_load_concept.assert_called_once_with(context, option)
        mock_get_knowledge_path.assert_called_once_with(context, option)

        assert mock_read_yaml.call_count == 4
        assert mock_read_yaml.call_args_list == [
            mocker.call(
                path=knowledge_path / "Package.yaml",
                model_type=Package,
            ),
            mocker.call(
                path=knowledge_path / "Development.yaml",
                model_type=Development,
            ),
            mocker.call(
                path=knowledge_path / "Technical.yaml",
                model_type=Technical,
            ),
            mocker.call(
                path=knowledge_path / "Roadmap.yaml",
                model_type=Roadmap,
            ),
        ]

    def test_propagates_package_analysis_failure(
        self, mocker: MockerFixture, project: ProjectContext
    ) -> None:
        context = project
        context.config.name = "test-package"

        error = BaseError("failed to build package analysis")

        mocker.patch(
            "gyomu_concept.document.context.build_package_analysis",
            return_value=Failure(error),
        )

        result = initialize_document_base_context(context)

        assert isinstance(result, Failure)

        document_error = result.failure()

        assert isinstance(document_error, DocumentBuilderError)
        assert document_error.message == "fail to initialize document base context"
        assert document_error.phase == "context-build"
        assert document_error.package_name == "test-package"
        assert document_error.__cause__ is not None

    def test_propagates_package_concept_failure(
        self, mocker: MockerFixture, project: ProjectContext
    ) -> None:
        context = project
        context.config.name = "test-package"

        error = BaseError("failed to load package concept")

        mocker.patch(
            "gyomu_concept.document.context.build_package_analysis",
            return_value=Success(create_package_analysis__default()),
        )
        mocker.patch(
            "gyomu_concept.document.context.load_package_concept",
            return_value=Failure(error),
        )

        result = initialize_document_base_context(context)

        assert isinstance(result, Failure)

        document_error = result.failure()

        assert isinstance(document_error, DocumentBuilderError)
        assert document_error.message == "fail to initialize document base context"
        assert document_error.phase == "context-build"
        assert document_error.package_name == "test-package"
        assert document_error.__cause__ is not None

    def test_fails_when_package_concept_is_not_found(
        self, mocker: MockerFixture, project: ProjectContext
    ) -> None:
        context = project
        context.config.name = "test-package"

        concept_path = Path(".gyomu/concept/$Package.json")

        mocker.patch(
            "gyomu_concept.document.context.build_package_analysis",
            return_value=Success(create_package_analysis__default()),
        )
        mocker.patch(
            "gyomu_concept.document.context.load_package_concept",
            return_value=Success(None),
        )
        mock_get_concept_path = mocker.patch(
            "gyomu_concept.document.context.get_package_concept_path",
            return_value=concept_path,
        )

        result = initialize_document_base_context(context)

        assert isinstance(result, Failure)

        document_error = result.failure()

        assert isinstance(document_error, DocumentBuilderError)
        assert document_error.message == "Package Concept not found"
        assert document_error.file_path == concept_path
        assert document_error.package_name == "test-package"
        assert document_error.phase == "context-build"

        mock_get_concept_path.assert_called_once_with(context, None)

    def test_propagates_package_yaml_failure(
        self, mocker: MockerFixture, project: ProjectContext
    ) -> None:
        context = project
        context.config.name = "test-package"

        error = BaseError("failed to read Package.yaml")

        mocker.patch(
            "gyomu_concept.document.context.build_package_analysis",
            return_value=Success(create_package_analysis__default()),
        )
        mocker.patch(
            "gyomu_concept.document.context.load_package_concept",
            return_value=Success(create_package_concept()),
        )
        knowledge_path = Path(".gyomu/knowledge")
        mocker.patch(
            "gyomu_concept.document.context.get_knowledge_path",
            return_value=knowledge_path,
        )
        mocker.patch(
            "gyomu_concept.document.context.read_yaml",
            return_value=Failure(error),
        )

        result = initialize_document_base_context(context)

        assert isinstance(result, Failure)

        document_error = result.failure()

        assert isinstance(document_error, DocumentBuilderError)
        assert document_error.message == "fail to initialize document base context"
        assert document_error.phase == "context-build"
        assert document_error.package_name == "test-package"
        assert document_error.__cause__ is not None

    def test_propagates_development_yaml_failure(
        self, mocker: MockerFixture, project: ProjectContext
    ) -> None:
        context = project
        context.config.name = "test-package"

        error = BaseError("failed to read Development.yaml")

        mocker.patch(
            "gyomu_concept.document.context.build_package_analysis",
            return_value=Success(create_package_analysis__default()),
        )
        mocker.patch(
            "gyomu_concept.document.context.load_package_concept",
            return_value=Success(create_package_concept()),
        )
        knowledge_path = Path(".gyomu/knowledge")
        mocker.patch(
            "gyomu_concept.document.context.get_knowledge_path",
            return_value=knowledge_path,
        )
        mocker.patch(
            "gyomu_concept.document.context.read_yaml",
            side_effect=[
                Success(create_package()),
                Failure(error),
            ],
        )

        result = initialize_document_base_context(context)

        assert isinstance(result, Failure)

        document_error = result.failure()

        assert isinstance(document_error, DocumentBuilderError)
        assert document_error.message == "fail to initialize document base context"
        assert document_error.phase == "context-build"
        assert document_error.package_name == "test-package"
        assert document_error.__cause__ is not None

    def test_propagates_technical_yaml_failure(
        self, mocker: MockerFixture, project: ProjectContext
    ) -> None:
        context = project
        context.config.name = "test-package"

        error = BaseError("failed to read Technical.yaml")

        mocker.patch(
            "gyomu_concept.document.context.build_package_analysis",
            return_value=Success(create_package_analysis__default()),
        )
        mocker.patch(
            "gyomu_concept.document.context.load_package_concept",
            return_value=Success(create_package_concept()),
        )
        knowledge_path = Path(".gyomu/knowledge")
        mocker.patch(
            "gyomu_concept.document.context.get_knowledge_path",
            return_value=knowledge_path,
        )
        mocker.patch(
            "gyomu_concept.document.context.read_yaml",
            side_effect=[
                Success(create_package()),
                Success(create_development()),
                Failure(error),
            ],
        )

        result = initialize_document_base_context(context)

        assert isinstance(result, Failure)

        document_error = result.failure()

        assert isinstance(document_error, DocumentBuilderError)
        assert document_error.message == "fail to initialize document base context"
        assert document_error.phase == "context-build"
        assert document_error.package_name == "test-package"
        assert document_error.__cause__ is not None

    def test_propagates_roadmap_yaml_failure(
        self, mocker: MockerFixture, project: ProjectContext
    ) -> None:
        context = project
        context.config.name = "test-package"

        error = BaseError("failed to read Roadmap.yaml")

        mocker.patch(
            "gyomu_concept.document.context.build_package_analysis",
            return_value=Success(create_package_analysis__default()),
        )
        mocker.patch(
            "gyomu_concept.document.context.load_package_concept",
            return_value=Success(create_package_concept()),
        )
        knowledge_path = Path(".gyomu/knowledge")
        mocker.patch(
            "gyomu_concept.document.context.get_knowledge_path",
            return_value=knowledge_path,
        )
        mocker.patch(
            "gyomu_concept.document.context.read_yaml",
            side_effect=[
                Success(create_package()),
                Success(create_development()),
                Success(create_technical()),
                Failure(error),
            ],
        )

        result = initialize_document_base_context(context)

        assert isinstance(result, Failure)

        document_error = result.failure()
        assert isinstance(document_error, DocumentBuilderError)
        assert document_error.message == "fail to initialize document base context"
        assert document_error.phase == "context-build"
        assert document_error.package_name == "test-package"
        assert document_error.__cause__ is not None
