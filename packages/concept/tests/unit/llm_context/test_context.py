from pathlib import Path

import pytest
from gyomu_concept.document.context import DocumentBaseContextResult
from gyomu_concept.error.document import DocumentBuilderError
from gyomu_concept.llm_context.context import (
    initialize_llm_context_build_context,
)
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.option.concept import ConceptOption
from gyomu_schema.schemas.concept.llm_context.input import (
    LlmContextBuildContext,
    LlmKnowledge,
)
from gyomu_schema.schemas.knowledge.coding_guideline import (
    CodingGuideline,
)
from gyomu_schema.schemas.types import FullPath
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.concept.concept_test_support.helpers import (
    _create_directory_project_context,
)
from packages.schema.schema_test_support.concept_helpers import (
    create_coding_guideline,
    create_document_base_context,
)


@pytest.fixture
def project() -> ProjectContext:
    return _create_directory_project_context()


class TestInitializeLlmContextBuildContext:
    def test_returns_build_context_without_local_coding_guideline(
        self,
        mocker: MockerFixture,
        project: ProjectContext,
    ) -> None:
        option = ConceptOption()
        document_context = create_document_base_context()
        root_path = Path("/tmp/test/root")
        knowledge_path = Path("/tmp/test/knowledge")
        root_guideline = create_coding_guideline()
        merged_guideline = create_coding_guideline()

        mocker.patch(
            "gyomu_concept.llm_context.context.initialize_document_base_context",
            return_value=Success(
                DocumentBaseContextResult(
                    context=document_context,
                    knowledge_path=FullPath(knowledge_path),
                )
            ),
        )
        mocker.patch(
            "gyomu_concept.llm_context.context.get_root_knowledge_path",
            return_value=Success(FullPath(root_path)),
        )
        mocker.patch(
            "gyomu_concept.llm_context.context.get_knowledge_path",
            return_value=knowledge_path,
        )
        mock_read_yaml = mocker.patch(
            "gyomu_concept.llm_context.context.read_yaml",
            return_value=Success(root_guideline),
        )
        mock_merge = mocker.patch(
            "gyomu_concept.llm_context.context.merge_coding_guideline",
            return_value=merged_guideline,
        )
        mocker.patch.object(Path, "exists", return_value=False)

        result = initialize_llm_context_build_context(project, option)

        assert result == Success(
            LlmContextBuildContext(
                analysis=document_context.analysis,
                concept=document_context.concept,
                knowledge=LlmKnowledge(
                    package=document_context.knowledge.package,
                    technical=document_context.knowledge.technical,
                    development=document_context.knowledge.development,
                    roadmap=document_context.knowledge.roadmap,
                    coding_guideline=merged_guideline,
                ),
            )
        )
        mock_read_yaml.assert_called_once_with(
            path=root_path / "Coding.yaml",
            model_type=CodingGuideline,
        )
        mock_merge.assert_called_once_with(root_guideline, None)

    def test_returns_build_context_with_local_coding_guideline(
        self,
        mocker: MockerFixture,
        project: ProjectContext,
    ) -> None:
        option = ConceptOption()
        document_context = create_document_base_context()
        root_path = Path("/tmp/test/root")
        knowledge_path = Path("/tmp/test/knowledge")
        root_guideline = create_coding_guideline()
        local_guideline = create_coding_guideline()
        merged_guideline = create_coding_guideline()

        mocker.patch(
            "gyomu_concept.llm_context.context.initialize_document_base_context",
            return_value=Success(
                DocumentBaseContextResult(
                    context=document_context,
                    knowledge_path=FullPath(knowledge_path),
                )
            ),
        )
        mocker.patch(
            "gyomu_concept.llm_context.context.get_root_knowledge_path",
            return_value=Success(FullPath(root_path)),
        )
        mocker.patch(
            "gyomu_concept.llm_context.context.get_knowledge_path",
            return_value=knowledge_path,
        )
        mock_read_yaml = mocker.patch(
            "gyomu_concept.llm_context.context.read_yaml",
            side_effect=[
                Success(root_guideline),
                Success(local_guideline),
            ],
        )
        mock_merge = mocker.patch(
            "gyomu_concept.llm_context.context.merge_coding_guideline",
            return_value=merged_guideline,
        )
        mocker.patch.object(Path, "exists", return_value=True)

        result = initialize_llm_context_build_context(project, option)

        assert result == Success(
            LlmContextBuildContext(
                analysis=document_context.analysis,
                concept=document_context.concept,
                knowledge=LlmKnowledge(
                    package=document_context.knowledge.package,
                    technical=document_context.knowledge.technical,
                    development=document_context.knowledge.development,
                    roadmap=document_context.knowledge.roadmap,
                    coding_guideline=merged_guideline,
                ),
            )
        )
        assert mock_read_yaml.call_count == 2
        mock_read_yaml.assert_any_call(
            path=root_path / "Coding.yaml",
            model_type=CodingGuideline,
        )
        mock_read_yaml.assert_any_call(
            path=knowledge_path / "Coding.yaml",
            model_type=CodingGuideline,
        )
        mock_merge.assert_called_once_with(root_guideline, local_guideline)

    def test_propagates_document_context_failure(
        self,
        mocker: MockerFixture,
    ) -> None:
        context = mocker.Mock(spec=ProjectContext)
        option = ConceptOption()
        error = DocumentBuilderError(
            "failed to initialize document context",
            package_name="test-package",
            phase="context-build",
        )

        mock_initialize = mocker.patch(
            "gyomu_concept.llm_context.context.initialize_document_base_context",
            return_value=Failure(error),
        )
        mock_root_path = mocker.patch(
            "gyomu_concept.llm_context.context.get_root_knowledge_path",
        )

        result = initialize_llm_context_build_context(context, option)

        assert result == Failure(error)
        mock_initialize.assert_called_once_with(context, option)
        mock_root_path.assert_not_called()

    def test_propagates_root_knowledge_path_failure(
        self,
        mocker: MockerFixture,
    ) -> None:
        context = _create_directory_project_context()
        option = ConceptOption()
        document_context = create_document_base_context()
        error = DocumentBuilderError(
            "failed to get root knowledge path",
            package_name="test-package",
            phase="context-build",
        )

        mocker.patch(
            "gyomu_concept.llm_context.context.initialize_document_base_context",
            return_value=Success(
                DocumentBaseContextResult(
                    context=document_context,
                    knowledge_path=FullPath(Path("/tmp/test/knowledge")),
                )
            ),
        )
        mock_root_path = mocker.patch(
            "gyomu_concept.llm_context.context.get_root_knowledge_path",
            return_value=Failure(error),
        )
        mock_read_yaml = mocker.patch(
            "gyomu_concept.llm_context.context.read_yaml",
        )

        result = initialize_llm_context_build_context(context, option)

        assert result == Failure(error)
        mock_root_path.assert_called_once_with(context, option)
        mock_read_yaml.assert_not_called()

    def test_wraps_root_coding_guideline_read_failure(
        self,
        mocker: MockerFixture,
        project: ProjectContext,
    ) -> None:
        option = ConceptOption()
        document_context = create_document_base_context()
        root_path = Path("/tmp/test/root")
        error = DocumentBuilderError(
            "failed to read root coding guideline",
            package_name="test-package",
            phase="context-build",
        )

        mocker.patch(
            "gyomu_concept.llm_context.context.initialize_document_base_context",
            return_value=Success(
                DocumentBaseContextResult(
                    context=document_context,
                    knowledge_path=FullPath(Path("/tmp/test/knowledge")),
                )
            ),
        )
        mocker.patch(
            "gyomu_concept.llm_context.context.get_root_knowledge_path",
            return_value=Success(FullPath(root_path)),
        )
        mock_read_yaml = mocker.patch(
            "gyomu_concept.llm_context.context.read_yaml",
            return_value=Failure(error),
        )

        result = initialize_llm_context_build_context(project, option)

        assert isinstance(result, Failure)
        wrapped_error = result.failure()
        assert isinstance(wrapped_error, DocumentBuilderError)
        assert wrapped_error.message == "fail to initialize llm context base context"
        assert wrapped_error.package_name == project.config.name
        assert wrapped_error.phase == "context-build"
        assert wrapped_error.__cause__ is not None
        mock_read_yaml.assert_called_once_with(
            path=root_path / "Coding.yaml",
            model_type=CodingGuideline,
        )

    def test_wraps_local_coding_guideline_read_failure(
        self,
        mocker: MockerFixture,
        project: ProjectContext,
    ) -> None:
        option = ConceptOption()
        document_context = create_document_base_context()
        root_path = Path("/tmp/test/root")
        knowledge_path = Path("/tmp/test/knowledge")
        root_guideline = create_coding_guideline()
        error = DocumentBuilderError(
            "failed to read local coding guideline",
            package_name="test-package",
            phase="context-build",
        )

        mocker.patch(
            "gyomu_concept.llm_context.context.initialize_document_base_context",
            return_value=Success(
                DocumentBaseContextResult(
                    context=document_context,
                    knowledge_path=FullPath(knowledge_path),
                )
            ),
        )
        mocker.patch(
            "gyomu_concept.llm_context.context.get_root_knowledge_path",
            return_value=Success(FullPath(root_path)),
        )
        mocker.patch(
            "gyomu_concept.llm_context.context.get_knowledge_path",
            return_value=knowledge_path,
        )
        mock_read_yaml = mocker.patch(
            "gyomu_concept.llm_context.context.read_yaml",
            side_effect=[
                Success(root_guideline),
                Failure(error),
            ],
        )
        mocker.patch.object(Path, "exists", return_value=True)

        result = initialize_llm_context_build_context(project, option)

        assert isinstance(result, Failure)
        wrapped_error = result.failure()
        assert isinstance(wrapped_error, DocumentBuilderError)
        assert wrapped_error.message == "fail to initialize llm context base context"
        assert wrapped_error.package_name == project.config.name
        assert wrapped_error.phase == "context-build"
        assert wrapped_error.__cause__ is not None
        assert mock_read_yaml.call_count == 2
