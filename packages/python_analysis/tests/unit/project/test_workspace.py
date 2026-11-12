from pathlib import Path
from typing import cast
from unittest.mock import call

from gyomu_python_analysis.analysis.initialize import initialize_project_from_workspace
from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import _FileAnalysisCache
from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from gyomu_schema.schemas.python.types import DeclarationIdentity, PythonPath, SymbolId
from gyomu_schema.schemas.types import FullPath
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.python_analysis.test_support.helpers import create_analysis_error
from packages.schema.test_support.helpers import simple_create_declaration_identity
from packages.test.test_support.helpers import MONOREPO_FIXTURES_ROOT
from packages.test.tests.unit.helper.helpers import (
    get_project_context,
    get_workspace_context,
)


class Test_FileAnalysisCache:
    def test_cache_miss(self, mocker: MockerFixture) -> None:
        project_context = cast(ProjectContext, mocker.Mock())
        identity = simple_create_declaration_identity("project_a.models::Product")
        python_path = identity.get_module_name()

        file_path = "project_a/models.py"
        analysis_context = cast(FileAnalysisContext, mocker.Mock())

        path_mock = mocker.patch(
            "gyomu_python_analysis.project.workspace."
            "python_path_to_source_project_relative_path",
            return_value=file_path,
        )
        load_mock = mocker.patch(
            "gyomu_python_analysis.project.workspace.load_file_analysis_context",
            return_value=Success(analysis_context),
        )

        cache = _FileAnalysisCache()

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
        load_mock.assert_called_once_with(context=project_context, file_path=file_path)

    def test_cache_hit(self, mocker: MockerFixture) -> None:
        project_context = cast(ProjectContext, mocker.Mock())

        identity1 = simple_create_declaration_identity("project_a.models::Product1")

        identity2 = simple_create_declaration_identity("project_a.models::Product2")

        analysis_context = cast(FileAnalysisContext, mocker.Mock())

        mocker.patch(
            "gyomu_python_analysis.project.workspace."
            "python_path_to_source_project_relative_path",
            return_value="project_a/models.py",
        )
        load_mock = mocker.patch(
            "gyomu_python_analysis.project.workspace.load_file_analysis_context",
            return_value=Success(analysis_context),
        )

        cache = _FileAnalysisCache()

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
        project_context = cast(ProjectContext, mocker.Mock())
        identity = simple_create_declaration_identity("project_a.models::Product")
        error = create_analysis_error()

        mocker.patch(
            "gyomu_python_analysis.project.workspace."
            "python_path_to_source_project_relative_path",
            return_value="project_a/models.py",
        )
        load_mock = mocker.patch(
            "gyomu_python_analysis.project.workspace.load_file_analysis_context",
            return_value=Failure(error),
        )

        cache = _FileAnalysisCache()

        result = cache.get_file_analysis_context(
            project_context=project_context,
            identity=identity,
        )

        assert isinstance(result, Failure)
        failure = result.failure()
        assert isinstance(failure, AnalysisError)
        assert failure is error
        load_mock.assert_called_once()

    def test_load_failure_is_not_cached(self, mocker: MockerFixture) -> None:
        project_context = cast(ProjectContext, mocker.Mock())
        identity = simple_create_declaration_identity("project_a.models::Product")
        error = create_analysis_error()
        analysis_context = cast(FileAnalysisContext, mocker.Mock())

        mocker.patch(
            "gyomu_python_analysis.project.workspace."
            "python_path_to_source_project_relative_path",
            return_value="project_a/models.py",
        )
        load_mock = mocker.patch(
            "gyomu_python_analysis.project.workspace.load_file_analysis_context",
            side_effect=[
                Failure(error),
                Success(analysis_context),
            ],
        )

        cache = _FileAnalysisCache()

        first_result = cache.get_file_analysis_context(
            project_context=project_context,
            identity=identity,
        )
        second_result = cache.get_file_analysis_context(
            project_context=project_context,
            identity=identity,
        )

        assert isinstance(first_result, Failure)
        assert isinstance(first_result, Failure)
        failure = first_result.failure()
        assert isinstance(failure, AnalysisError)
        assert failure is error

        assert isinstance(second_result, Success)
        assert second_result.unwrap() is analysis_context

        assert load_mock.call_count == 2

    def test_invalidate_cached_file_analysis(self, mocker: MockerFixture) -> None:
        project_context = cast(ProjectContext, mocker.Mock())
        identity = simple_create_declaration_identity("project_a.models::Product")
        python_path = identity.get_module_name()

        first_context = cast(FileAnalysisContext, mocker.Mock())
        second_context = cast(FileAnalysisContext, mocker.Mock())

        mocker.patch(
            "gyomu_python_analysis.project.workspace."
            "python_path_to_source_project_relative_path",
            return_value="project_a/models.py",
        )
        load_mock = mocker.patch(
            "gyomu_python_analysis.project.workspace.load_file_analysis_context",
            side_effect=[
                Success(first_context),
                Success(second_context),
            ],
        )

        cache = _FileAnalysisCache()

        first_result = cache.get_file_analysis_context(
            project_context=project_context,
            identity=identity,
        )

        cache.invalidate_file_analysis(module_path=python_path)

        second_result = cache.get_file_analysis_context(
            project_context=project_context,
            identity=identity,
        )

        assert isinstance(first_result, Success)
        assert first_result.unwrap() is first_context

        assert isinstance(second_result, Success)
        assert second_result.unwrap() is second_context

        assert load_mock.call_count == 2

    def test_invalidate_uncached_file_analysis(self) -> None:
        cache = _FileAnalysisCache()

        cache.invalidate_file_analysis(module_path=PythonPath("project_a.models"))


class TestWorkspaceContext:
    class TestFindFileAnalysisContext:
        def test_success(self, mocker: MockerFixture) -> None:
            target_path = FullPath(MONOREPO_FIXTURES_ROOT)
            workspace_context = get_workspace_context(target_path)
            project_context = get_project_context(
                workspace_context,
                "project-b",
            )

            # インデックス初期化を避け、検索対象を明示的に登録する
            workspace_context._project_indexes["project_b"] = project_context

            target_identity = simple_create_declaration_identity(
                id="project_b.models::ProductModel",
            )

            file_context = mocker.Mock()
            cache_mock = mocker.patch.object(
                workspace_context._file_analysis_cache,
                "get_file_analysis_context",
                return_value=Success(file_context),
            )
            exists_mock = mocker.patch.object(
                Path,
                "exists",
                return_value=True,
            )

            result = workspace_context.find_file_analysis_context(
                target_identity,
            )

            assert isinstance(result, Success)
            record = result.unwrap()
            assert record is not None
            actual_file_context, actual_project_context = record
            assert actual_file_context is file_context
            assert actual_project_context is project_context

            exists_mock.assert_called()
            cache_mock.assert_called_once_with(
                project_context,
                target_identity,
            )

        def test_success_none_when_package_is_not_managed(
            self,
            mocker: MockerFixture,
        ) -> None:
            target_path = FullPath(MONOREPO_FIXTURES_ROOT)
            workspace_context = get_workspace_context(target_path)

            # インデックスを空にしないことで初期化処理を避ける
            workspace_context._project_indexes["other_package"] = get_project_context(
                workspace_context, "project-b"
            )

            target_identity = simple_create_declaration_identity(
                id="unknown_package.models::ProductModel",
            )

            cache_mock = mocker.patch.object(
                workspace_context._file_analysis_cache,
                "get_file_analysis_context",
            )
            exists_mock = mocker.patch.object(Path, "exists")

            result = workspace_context.find_file_analysis_context(
                target_identity,
            )

            assert isinstance(result, Success)
            assert result.unwrap() is None

            exists_mock.assert_not_called()
            cache_mock.assert_not_called()

        def test_failure_when_module_does_not_exist(
            self,
            mocker: MockerFixture,
        ) -> None:
            target_path = FullPath(MONOREPO_FIXTURES_ROOT)
            workspace_context = get_workspace_context(target_path)
            project_context = get_project_context(
                workspace_context,
                "project-b",
            )

            workspace_context._project_indexes["project_b"] = project_context

            target_identity = simple_create_declaration_identity(
                id="project_b.missing::MissingModel",
            )

            exists_mock = mocker.patch.object(
                Path,
                "exists",
                return_value=False,
            )
            cache_mock = mocker.patch.object(
                workspace_context._file_analysis_cache,
                "get_file_analysis_context",
            )

            result = workspace_context.find_file_analysis_context(
                target_identity,
            )

            assert isinstance(result, Failure)
            error = result.failure()
            assert isinstance(error, AnalysisError)
            assert error.message == "target module not found"
            assert error.phase == "workspace-discovery"
            assert error.details == {
                "project_name": project_context.config.name,
            }

            exists_mock.assert_called()
            cache_mock.assert_not_called()

    class TestProjectIndexes:
        def test_project_indexes_are_initialized_once(
            self,
            mocker: MockerFixture,
        ) -> None:
            target_path = FullPath(MONOREPO_FIXTURES_ROOT)
            workspace_context = get_workspace_context(target_path)

            project = next(
                project
                for project in workspace_context.projects
                if project.config.name == "project-b"
            )
            project_context = get_project_context(
                workspace_context,
                project.config.name,
            )

            initialize_mock = mocker.patch(
                "gyomu_python_analysis.project.workspace.initialize_project_from_workspace",
                return_value=project_context,
            )

            file_analysis_context = mocker.Mock()
            get_file_analysis_mock = mocker.patch.object(
                workspace_context._file_analysis_cache,
                "get_file_analysis_context",
                return_value=Success(file_analysis_context),
            )

            target_identity = simple_create_declaration_identity(
                id="project_b.models::ProductBaseModel",
            )

            first_result = workspace_context.find_file_analysis_context(target_identity)
            second_result = workspace_context.find_file_analysis_context(
                target_identity
            )

            assert isinstance(first_result, Success)
            assert isinstance(second_result, Success)

            assert initialize_mock.call_count == len(workspace_context.projects)

            assert get_file_analysis_mock.call_count == 2

            assert workspace_context._project_indexes
            assert initialize_mock.call_args_list == [
                call(workspace_context.workspace_root.path, workspace_project)
                for workspace_project in workspace_context.projects
            ]

        def test_project_indexes_are_initialized_with_multi_projects(
            self,
            mocker: MockerFixture,
        ) -> None:
            target_path = FullPath(MONOREPO_FIXTURES_ROOT)
            workspace_context = get_workspace_context(target_path)

            file_analysis_context = mocker.Mock()
            get_file_analysis_mock = mocker.patch.object(
                workspace_context._file_analysis_cache,
                "get_file_analysis_context",
                return_value=Success(file_analysis_context),
            )

            target_identity = simple_create_declaration_identity(
                id="project_b.models::ProductBaseModel",
            )

            first_result = workspace_context.find_file_analysis_context(target_identity)
            second_result = workspace_context.find_file_analysis_context(
                target_identity
            )

            assert isinstance(first_result, Success)
            assert isinstance(second_result, Success)

            assert get_file_analysis_mock.call_count == 2

            assert workspace_context._project_indexes
            expected_module_names = {
                package_root.module_name
                for project in workspace_context.projects
                for package_root in initialize_project_from_workspace(
                    workspace_context.workspace_root.path,
                    project,
                ).package_roots
            }

            assert set(workspace_context._project_indexes) == expected_module_names

    class TestFindFileAnalysisContextByModulePath:
        def test_success(self, mocker: MockerFixture) -> None:
            target_path = FullPath(MONOREPO_FIXTURES_ROOT)
            workspace_context = get_workspace_context(target_path)

            expected_identity = DeclarationIdentity.create_from_symbol_id(
                symbol_id=SymbolId("project_b.models::Test"),
            )
            expected_result = Success((mocker.Mock(), mocker.Mock()))

            find_mock = mocker.patch.object(
                workspace_context,
                "find_file_analysis_context",
                return_value=expected_result,
            )

            result = workspace_context.find_file_analysis_context_by_module_path(
                PythonPath("project_b.models"),
            )

            assert result is expected_result
            find_mock.assert_called_once_with(expected_identity)

        def test_success_none(self, mocker: MockerFixture) -> None:
            target_path = FullPath(MONOREPO_FIXTURES_ROOT)
            workspace_context = get_workspace_context(target_path)

            expected_result = Success(None)
            find_mock = mocker.patch.object(
                workspace_context,
                "find_file_analysis_context",
                return_value=expected_result,
            )

            result = workspace_context.find_file_analysis_context_by_module_path(
                PythonPath("unknown_package.models"),
            )

            assert result is expected_result
            find_mock.assert_called_once_with(
                DeclarationIdentity.create_from_symbol_id(
                    symbol_id=SymbolId("unknown_package.models::Test"),
                )
            )

        def test_failure(self, mocker: MockerFixture) -> None:
            target_path = FullPath(MONOREPO_FIXTURES_ROOT)
            workspace_context = get_workspace_context(target_path)

            expected_result = Failure(create_analysis_error())
            find_mock = mocker.patch.object(
                workspace_context,
                "find_file_analysis_context",
                return_value=expected_result,
            )

            result = workspace_context.find_file_analysis_context_by_module_path(
                PythonPath("project_b.missing"),
            )

            assert result is expected_result
            find_mock.assert_called_once_with(
                DeclarationIdentity.create_from_symbol_id(
                    symbol_id=SymbolId("project_b.missing::Test"),
                )
            )

    class TestInvalidateFileAnalysis:
        def test_invalidate_file_analysis(self, mocker: MockerFixture) -> None:
            target_path = FullPath(MONOREPO_FIXTURES_ROOT)
            workspace_context = get_workspace_context(target_path)

            invalidate_mock = mocker.patch.object(
                workspace_context._file_analysis_cache,
                "invalidate_file_analysis",
            )

            module_path = PythonPath("project_b.models")

            workspace_context.invalidate_file_analysis(module_path)

            invalidate_mock.assert_called_once_with(module_path)
