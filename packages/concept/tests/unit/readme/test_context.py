from pathlib import Path

import pytest
from gyomu_concept.document.context import DocumentBaseContextResult
from gyomu_concept.error.document import DocumentBuilderError
from gyomu_concept.readme.context import initialize_readme_build_context
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.types import FullPath
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.concept.concept_test_support.helpers import (
    _create_directory_project_context,
)
from packages.schema.schema_test_support.concept_helpers import (
    create_document_base_context,
)


@pytest.fixture
def project() -> ProjectContext:
    return _create_directory_project_context()


class TestInitializeReadmeBuildContext:
    def test_returns_document_context(
        self, mocker: MockerFixture, project: ProjectContext
    ) -> None:
        context = project
        option = ConceptOption()
        document_context = create_document_base_context()

        mock_initialize = mocker.patch(
            "gyomu_concept.readme.context.initialize_document_base_context",
            return_value=Success(
                DocumentBaseContextResult(
                    context=document_context,
                    knowledge_path=FullPath(Path("/tmp/test")),
                )
            ),
        )

        result = initialize_readme_build_context(context, option)

        assert result == Success(document_context)
        mock_initialize.assert_called_once_with(context, option)

    def test_propagates_failure(self, mocker: MockerFixture) -> None:
        context = mocker.Mock(spec=ProjectContext)
        option = ConceptOption()
        error = DocumentBuilderError(
            "failed to initialize document context",
            package_name="test-package",
            phase="context-build",
        )

        mock_initialize = mocker.patch(
            "gyomu_concept.readme.context.initialize_document_base_context",
            return_value=Failure(error),
        )

        result = initialize_readme_build_context(context, option)

        assert result == Failure(error)
        mock_initialize.assert_called_once_with(context, option)
