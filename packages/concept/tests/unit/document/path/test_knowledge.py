from pathlib import Path

import pytest
from gyomu_concept.document.path.knowledge import (
    get_knowledge_path,
    get_root_knowledge_path,
)
from gyomu_concept.error.document import DocumentBuilderError
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.option.concept import ConceptActionOption, ConceptOption
from gyomu_schema.schemas.types import FullPath
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.concept.concept_test_support.helpers import (
    _create_directory_project_context,
)
from packages.python_analysis.python_analysis_test_support.helpers import (
    create_workspace_root,
)


@pytest.fixture
def context() -> ProjectContext:
    return _create_directory_project_context()


class TestGetKnowledgePath:
    @pytest.mark.parametrize(
        ("option", "expected_directory"),
        [
            (None, "knowledge"),
            (
                ConceptOption(),
                "knowledge",
            ),
            (
                ConceptOption(action=ConceptActionOption(write_to_temp_folder=False)),
                "knowledge",
            ),
            (
                ConceptOption(action=ConceptActionOption(write_to_temp_folder=True)),
                "cache",
            ),
        ],
    )
    def test_returns_expected_path(
        self,
        context: ProjectContext,
        option: ConceptOption | None,
        expected_directory: str,
    ) -> None:
        result = get_knowledge_path(context, option)

        assert result == (context.project_root / ".gyomu" / expected_directory)


class TestGetRootKnowledgePath:
    def test_returns_repository_root_knowledge_path(
        self,
        mocker: MockerFixture,
        context: ProjectContext,
    ) -> None:
        repository_root = Path("/repository")
        mocker.patch(
            "gyomu_concept.document.path.knowledge.find_root",
            return_value=Success(create_workspace_root(path=FullPath(repository_root))),
        )

        result = get_root_knowledge_path(context)

        assert isinstance(result, Success)
        assert result.unwrap() == repository_root / ".gyomu" / "knowledge"

    def test_returns_repository_root_cache_path(
        self,
        mocker: MockerFixture,
        context: ProjectContext,
    ) -> None:
        repository_root = Path("/repository")
        mocker.patch(
            "gyomu_concept.document.path.knowledge.find_root",
            return_value=Success(create_workspace_root(path=FullPath(repository_root))),
        )

        result = get_root_knowledge_path(
            context,
            option=ConceptOption(action=ConceptActionOption(write_to_temp_folder=True)),
        )

        assert isinstance(result, Success)
        assert result.unwrap() == repository_root / ".gyomu" / "cache"

    def test_returns_failure_when_find_root_fails(
        self,
        mocker: MockerFixture,
        context: ProjectContext,
    ) -> None:
        error = ...

        mocker.patch(
            "gyomu_concept.document.path.knowledge.find_root",
            return_value=Failure(error),
        )

        result = get_root_knowledge_path(context)

        assert isinstance(result, Failure)

        document_error = result.failure()

        assert isinstance(document_error, DocumentBuilderError)
        assert document_error.phase == "context-build"
        assert document_error.file_path == context.project_root
        assert document_error.package_name == context.config.name
        assert "Failed to find repository root" in document_error.message
