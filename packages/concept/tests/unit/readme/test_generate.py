import pytest
from gyomu_concept.error.document import DocumentBuilderError
from gyomu_concept.readme.definition import README_DOCUMENT_DEFINITION
from gyomu_concept.readme.generate import generate_readme_files
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.option.concept import ConceptOption
from pytest_mock import MockerFixture
from returns.result import Failure, Success


class TestGenerateReadmeFiles:
    @pytest.mark.asyncio
    async def test_generates_readme_files(self, mocker: MockerFixture) -> None:
        project = mocker.Mock(spec=ProjectContext)
        option = ConceptOption()

        mock_generate = mocker.patch(
            "gyomu_concept.readme.generate.generate_document",
            new_callable=mocker.AsyncMock,
            return_value=Success(None),
        )

        result = await generate_readme_files(project, option)

        assert result == Success(None)
        mock_generate.assert_awaited_once_with(
            README_DOCUMENT_DEFINITION, project, option
        )

    @pytest.mark.asyncio
    async def test_propagates_failure(self, mocker: MockerFixture) -> None:
        project = mocker.Mock(spec=ProjectContext)
        option = ConceptOption()
        error = DocumentBuilderError(
            "failed to generate document",
            package_name="test-package",
            phase="document-build",
        )

        mock_generate = mocker.patch(
            "gyomu_concept.readme.generate.generate_document",
            new_callable=mocker.AsyncMock,
            return_value=Failure(error),
        )

        result = await generate_readme_files(project, option)

        assert result == Failure(error)
        mock_generate.assert_awaited_once_with(
            README_DOCUMENT_DEFINITION, project, option
        )
