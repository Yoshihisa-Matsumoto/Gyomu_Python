from typing import cast

from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_python_analysis.resolve.file_analysis_cache import (
    FileAnalysisCache,
)
from gyomu_schema.option.analysis import AnalysisOption
from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.schema.test_support.helpers import create_declaration_identity


class TestFileAnalysisCache:
    def test_cache_miss(self, mocker: MockerFixture) -> None:
        workspace_context = cast(WorkspaceContext, mocker.Mock())
        project_context = cast(ProjectContext, mocker.Mock())
        identity = create_declaration_identity("project_a.models::Product")
        python_path = identity.get_module_name()

        file_path = "project_a/models.py"
        analysis_context = cast(FileAnalysisContext, mocker.Mock())

        path_mock = mocker.patch(
            "gyomu_python_analysis.resolve.file_analysis_cache."
            "python_path_to_source_project_relative_path",
            return_value=file_path,
        )
        load_mock = mocker.patch(
            "gyomu_python_analysis.resolve.file_analysis_cache."
            "load_file_analysis_context",
            return_value=Success(analysis_context),
        )

        cache = FileAnalysisCache(workspace_context)

        result = cache.get_file_analysis_context(
            project_context=project_context,
            identity=identity,
        )

        assert isinstance(result, Success)
        assert result.unwrap() is analysis_context

        path_mock.assert_called_once_with(
            path=python_path,
            context=project_context,
        )
        load_mock.assert_called_once_with(
            context=project_context,
            file_path=file_path,
            option=AnalysisOption(no_check_cache=True),
        )

    def test_cache_hit(self, mocker: MockerFixture) -> None:
        workspace_context = cast(WorkspaceContext, mocker.Mock())
        project_context = cast(ProjectContext, mocker.Mock())

        identity1 = create_declaration_identity("project_a.models::Product1")

        identity2 = create_declaration_identity("project_a.models::Product2")

        analysis_context = cast(FileAnalysisContext, mocker.Mock())

        mocker.patch(
            "gyomu_python_analysis.resolve.file_analysis_cache."
            "python_path_to_source_project_relative_path",
            return_value="project_a/models.py",
        )
        load_mock = mocker.patch(
            "gyomu_python_analysis.resolve.file_analysis_cache."
            "load_file_analysis_context",
            return_value=Success(analysis_context),
        )

        cache = FileAnalysisCache(workspace_context)

        first_result = cache.get_file_analysis_context(
            project_context=project_context,
            identity=identity1,
        )
        second_result = cache.get_file_analysis_context(
            project_context=project_context,
            identity=identity2,
        )

        assert isinstance(first_result, Success)
        assert first_result.unwrap() is analysis_context

        assert isinstance(second_result, Success)
        assert second_result.unwrap() is analysis_context

        load_mock.assert_called_once()

    def test_load_failure(self, mocker: MockerFixture) -> None:
        workspace_context = cast(WorkspaceContext, mocker.Mock())
        project_context = cast(ProjectContext, mocker.Mock())
        identity = create_declaration_identity("project_a.models::Product")
        error = cast(AnalysisError, mocker.Mock())

        mocker.patch(
            "gyomu_python_analysis.resolve.file_analysis_cache."
            "python_path_to_source_project_relative_path",
            return_value="project_a/models.py",
        )
        load_mock = mocker.patch(
            "gyomu_python_analysis.resolve.file_analysis_cache."
            "load_file_analysis_context",
            return_value=Failure(error),
        )

        cache = FileAnalysisCache(workspace_context)

        result = cache.get_file_analysis_context(
            project_context=project_context,
            identity=identity,
        )

        assert isinstance(result, Failure)
        assert result.failure() is error
        load_mock.assert_called_once()

    def test_load_failure_is_not_cached(self, mocker: MockerFixture) -> None:
        workspace_context = cast(WorkspaceContext, mocker.Mock())
        project_context = cast(ProjectContext, mocker.Mock())
        identity = create_declaration_identity("project_a.models::Product")
        error = cast(AnalysisError, mocker.Mock())
        analysis_context = cast(FileAnalysisContext, mocker.Mock())

        mocker.patch(
            "gyomu_python_analysis.resolve.file_analysis_cache."
            "python_path_to_source_project_relative_path",
            return_value="project_a/models.py",
        )
        load_mock = mocker.patch(
            "gyomu_python_analysis.resolve.file_analysis_cache."
            "load_file_analysis_context",
            side_effect=[
                Failure(error),
                Success(analysis_context),
            ],
        )

        cache = FileAnalysisCache(workspace_context)

        first_result = cache.get_file_analysis_context(
            project_context=project_context,
            identity=identity,
        )
        second_result = cache.get_file_analysis_context(
            project_context=project_context,
            identity=identity,
        )

        assert isinstance(first_result, Failure)
        assert first_result.failure() is error

        assert isinstance(second_result, Success)
        assert second_result.unwrap() is analysis_context

        assert load_mock.call_count == 2
