from pathlib import Path

import pytest
from gyomu_schema.schemas.python.types import ProjectRelativePath, PythonPath
from gyomu_schema.schemas.types import FullPath
from gyomu_test.error.test import GyomuTestError
from gyomu_test.helper.inventory.search import (
    get_all_helper_candidates,
    get_generated_helper_candidates,
)
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.python_analysis.test_support.helpers import (
    create_analysis_error,
    create_resolve_error,
)
from packages.schema.test_support.helpers import simple_create_declaration_identity
from packages.test.test_support.helpers import MONOREPO_FIXTURES_ROOT
from packages.test.tests.unit.helper.helpers import (
    create_gyomu_test_error,
    get_project_context,
    get_workspace_context,
)


class TestGetGeneratedHelperCandidates:
    @pytest.mark.parametrize(
        ("test_project_name", "model_symbol_id", "expected_items", "another_files"),
        [
            (
                "project-b",
                "project_b.models::ProductBaseModel",
                (
                    (
                        PythonPath("packages.project_b.test_support.helpers"),
                        "create_product_base_model",
                        "project-b",
                    ),
                ),
                None,
            ),
            (
                "project-b",
                "project_b.models::ProductSummary",
                (
                    (
                        PythonPath("packages.project_b.test_support.helpers"),
                        "create_product_summary",
                        "project-b",
                    ),
                ),
                None,
            ),
            (
                "project-b",
                "project_b.models::CompositeProduct",
                (
                    (
                        PythonPath("packages.project_b.test_support.helpers"),
                        "create_composite_product",
                        "project-b",
                    ),
                ),
                None,
            ),
            ("project-b", "project_b.models::ProductModel", (), None),
            ("project-b", "project_b.error::TestingError", (), None),
            ("project-b", "project_b.non_models::NonHelper", (), None),
            (
                "project-b",
                "project_b.models::ProductModel",
                (
                    (
                        PythonPath("packages.project_b.test_support.another_helpers"),
                        "create_product_model",
                        "project-b",
                    ),
                ),
                ("another_helpers.py",),
            ),
            (
                "project-b",
                "project_b.error::TestingError",
                (
                    (
                        PythonPath("packages.project_b.test_support.another_helpers"),
                        "create_testing_error",
                        "project-b",
                    ),
                ),
                ("another_helpers.py",),
            ),
        ],
    )
    def test_success_without_model_project(
        self,
        test_project_name: str,
        model_symbol_id: str,
        expected_items: tuple[tuple[PythonPath, str, str], ...],
        another_files: tuple[str, ...] | None,
        mocker: MockerFixture,
    ) -> None:
        target_path = FullPath(MONOREPO_FIXTURES_ROOT)
        _, workspace_context = get_workspace_context(target_path)

        project_context = get_project_context(workspace_context, test_project_name)

        if another_files is not None:
            result_paths = tuple(
                ProjectRelativePath(Path("test_support") / file)
                for file in another_files
            )
            mocker.patch(
                "gyomu_test.helper.inventory.search.get_helper_file_paths",
                return_value=Success(result_paths),
            )

        result = get_generated_helper_candidates(
            model_identity=simple_create_declaration_identity(id=model_symbol_id),
            test_project_context=project_context,
            workspace_context=workspace_context,
        )
        assert isinstance(result, Success)
        items = tuple(
            (
                identity.get_module_name(),
                identity.get_symbol_name(),
                project.config.name,
            )
            for identity, project in result.unwrap()
        )
        assert items == expected_items

    @pytest.mark.parametrize(
        ("test_project_name", "model_symbol_id", "expected_items", "another_files"),
        [
            (
                "project-b",
                "project_b.models::ProductBaseModel",
                (
                    (
                        PythonPath("packages.project_b.test_support.helpers"),
                        "create_product_base_model",
                        "project-b",
                    ),
                ),
                None,
            ),
            (
                "project-b",
                "project_b.models::ProductSummary",
                (
                    (
                        PythonPath("packages.project_b.test_support.helpers"),
                        "create_product_summary",
                        "project-b",
                    ),
                ),
                None,
            ),
            (
                "project-b",
                "project_b.models::CompositeProduct",
                (
                    (
                        PythonPath("packages.project_b.test_support.helpers"),
                        "create_composite_product",
                        "project-b",
                    ),
                ),
                None,
            ),
            ("project-b", "project_b.models::ProductModel", (), None),
            ("project-b", "project_b.error::TestingError", (), None),
            ("project-b", "project_b.non_models::NonHelper", (), None),
            (
                "project-b",
                "project_b.models::ProductModel",
                (
                    (
                        PythonPath("packages.project_b.test_support.another_helpers"),
                        "create_product_model",
                        "project-b",
                    ),
                ),
                ("another_helpers.py",),
            ),
            (
                "project-b",
                "project_b.error::TestingError",
                (
                    (
                        PythonPath("packages.project_b.test_support.another_helpers"),
                        "create_testing_error",
                        "project-b",
                    ),
                ),
                ("another_helpers.py",),
            ),
            (
                "project-b",
                "project_a.models::UserSummary",
                (),
                ("another_helpers.py",),
            ),
        ],
    )
    def test_success_with_model_project(
        self,
        test_project_name: str,
        model_symbol_id: str,
        expected_items: tuple[tuple[PythonPath, str, str], ...],
        another_files: tuple[str, ...] | None,
        mocker: MockerFixture,
    ) -> None:
        target_path = FullPath(MONOREPO_FIXTURES_ROOT)
        _, workspace_context = get_workspace_context(target_path)

        project_context = get_project_context(workspace_context, test_project_name)

        if another_files is not None:
            result_paths = tuple(
                ProjectRelativePath(Path("test_support") / file)
                for file in another_files
            )
            mocker.patch(
                "gyomu_test.helper.inventory.search.get_helper_file_paths",
                return_value=Success(result_paths),
            )

        result = get_generated_helper_candidates(
            model_identity=simple_create_declaration_identity(id=model_symbol_id),
            test_project_context=project_context,
            workspace_context=workspace_context,
            model_project_context=project_context,
        )
        assert isinstance(result, Success)
        items = tuple(
            (
                identity.get_module_name(),
                identity.get_symbol_name(),
                project.config.name,
            )
            for identity, project in result.unwrap()
        )
        assert items == expected_items

    def test_get_helper_file_paths_failure(
        self,
        mocker: MockerFixture,
    ) -> None:
        target_path = FullPath(MONOREPO_FIXTURES_ROOT)
        _, workspace_context = get_workspace_context(target_path)

        project_context = get_project_context(workspace_context, "project-b")

        expected_error = create_gyomu_test_error("test")
        mocker.patch(
            "gyomu_test.helper.inventory.search.get_helper_file_paths",
            return_value=Failure(expected_error),
        )

        result = get_generated_helper_candidates(
            model_identity=simple_create_declaration_identity(
                id="project_b.models::ProductBaseModel"
            ),
            test_project_context=project_context,
            workspace_context=workspace_context,
        )
        assert isinstance(result, Failure)
        error = result.failure()
        assert isinstance(error, GyomuTestError)
        assert error is expected_error

    def test_initialize_project_context_failure(
        self,
        mocker: MockerFixture,
    ) -> None:
        target_path = FullPath(MONOREPO_FIXTURES_ROOT)
        _, workspace_context = get_workspace_context(target_path)

        project_context = get_project_context(workspace_context, "project-b")

        expected_error = create_analysis_error()
        mocker.patch(
            "gyomu_test.helper.inventory.search.initialize_project_context",
            return_value=Failure(expected_error),
        )

        result = get_generated_helper_candidates(
            model_identity=simple_create_declaration_identity(
                id="project_b.models::ProductBaseModel"
            ),
            test_project_context=project_context,
            workspace_context=workspace_context,
        )
        assert isinstance(result, Failure)
        error = result.failure()
        assert isinstance(error, GyomuTestError)
        assert error.__cause__ is expected_error

    def test_load_file_analysis_context_failure(
        self,
        mocker: MockerFixture,
    ) -> None:
        target_path = FullPath(MONOREPO_FIXTURES_ROOT)
        _, workspace_context = get_workspace_context(target_path)

        project_context = get_project_context(workspace_context, "project-b")

        expected_error = create_analysis_error()
        mocker.patch(
            "gyomu_test.helper.inventory.search.load_file_analysis_context",
            return_value=Failure(expected_error),
        )

        result = get_generated_helper_candidates(
            model_identity=simple_create_declaration_identity(
                id="project_b.models::ProductBaseModel"
            ),
            test_project_context=project_context,
            workspace_context=workspace_context,
        )
        assert isinstance(result, Failure)
        error = result.failure()
        assert isinstance(error, GyomuTestError)
        assert error.__cause__ is expected_error

    def test_resolve_type_analysis_failure(
        self,
        mocker: MockerFixture,
    ) -> None:
        target_path = FullPath(MONOREPO_FIXTURES_ROOT)
        _, workspace_context = get_workspace_context(target_path)

        project_context = get_project_context(workspace_context, "project-b")

        expected_error = create_resolve_error()
        mocker.patch(
            "gyomu_test.helper.inventory.search.resolve_type_analysis",
            return_value=Failure(expected_error),
        )

        result = get_generated_helper_candidates(
            model_identity=simple_create_declaration_identity(
                id="project_b.models::ProductBaseModel"
            ),
            test_project_context=project_context,
            workspace_context=workspace_context,
        )
        assert isinstance(result, Failure)
        error = result.failure()
        assert isinstance(error, GyomuTestError)
        assert error.__cause__ is expected_error


class TestGetAllHelperCandidates:
    @pytest.mark.parametrize(
        ("test_project_name", "model_symbol_id", "expected_items", "another_files"),
        [
            (
                "project-b",
                "project_b.models::ProductBaseModel",
                (
                    (
                        PythonPath("packages.project_b.test_support.helpers"),
                        "create_product_base_model",
                        "project-b",
                    ),
                    (
                        PythonPath("packages.project_b.test_support.helpers"),
                        "build_product_base_model",
                        "project-b",
                    ),
                ),
                None,
            ),
            (
                "project-b",
                "project_b.models::ProductSummary",
                (
                    (
                        PythonPath("packages.project_b.test_support.helpers"),
                        "create_product_summary",
                        "project-b",
                    ),
                ),
                None,
            ),
            (
                "project-b",
                "project_b.models::CompositeProduct",
                (
                    (
                        PythonPath("packages.project_b.test_support.helpers"),
                        "create_composite_product",
                        "project-b",
                    ),
                ),
                None,
            ),
            ("project-b", "project_b.models::ProductModel", (), None),
            ("project-b", "project_b.error::TestingError", (), None),
            ("project-b", "project_b.non_models::NonHelper", (), None),
            (
                "project-b",
                "project_b.models::ProductModel",
                (
                    (
                        PythonPath("packages.project_b.test_support.another_helpers"),
                        "create_product_model",
                        "project-b",
                    ),
                ),
                ("another_helpers.py",),
            ),
            (
                "project-b",
                "project_b.error::TestingError",
                (
                    (
                        PythonPath("packages.project_b.test_support.another_helpers"),
                        "create_testing_error",
                        "project-b",
                    ),
                ),
                ("another_helpers.py",),
            ),
            (
                "project-b",
                "project_a.models::UserSummary",
                (
                    (
                        PythonPath("packages.project_b.test_support.another_helpers"),
                        "build_user_summary",
                        "project-b",
                    ),
                ),
                ("another_helpers.py",),
            ),
        ],
    )
    def test_success_without_model_project(
        self,
        test_project_name: str,
        model_symbol_id: str,
        expected_items: tuple[tuple[PythonPath, str, str], ...],
        another_files: tuple[str, ...] | None,
        mocker: MockerFixture,
    ) -> None:
        target_path = FullPath(MONOREPO_FIXTURES_ROOT)
        _, workspace_context = get_workspace_context(target_path)

        project_context = get_project_context(workspace_context, test_project_name)

        if another_files is not None:
            result_paths = tuple(
                ProjectRelativePath(Path("test_support") / file)
                for file in another_files
            )
            mocker.patch(
                "gyomu_test.helper.inventory.search.get_helper_file_paths",
                return_value=Success(result_paths),
            )

        result = get_all_helper_candidates(
            model_identity=simple_create_declaration_identity(id=model_symbol_id),
            test_project_context=project_context,
            workspace_context=workspace_context,
        )
        assert isinstance(result, Success)
        items = tuple(
            (
                identity.get_module_name(),
                identity.get_symbol_name(),
                project.config.name,
            )
            for identity, project in result.unwrap()
        )
        assert items == expected_items

    @pytest.mark.parametrize(
        ("test_project_name", "model_symbol_id", "expected_items", "another_files"),
        [
            (
                "project-b",
                "project_b.models::ProductBaseModel",
                (
                    (
                        PythonPath("packages.project_b.test_support.helpers"),
                        "create_product_base_model",
                        "project-b",
                    ),
                    (
                        PythonPath("packages.project_b.test_support.helpers"),
                        "build_product_base_model",
                        "project-b",
                    ),
                ),
                None,
            ),
            (
                "project-b",
                "project_b.models::ProductSummary",
                (
                    (
                        PythonPath("packages.project_b.test_support.helpers"),
                        "create_product_summary",
                        "project-b",
                    ),
                ),
                None,
            ),
            (
                "project-b",
                "project_b.models::CompositeProduct",
                (
                    (
                        PythonPath("packages.project_b.test_support.helpers"),
                        "create_composite_product",
                        "project-b",
                    ),
                ),
                None,
            ),
            ("project-b", "project_b.models::ProductModel", (), None),
            ("project-b", "project_b.error::TestingError", (), None),
            ("project-b", "project_b.non_models::NonHelper", (), None),
            (
                "project-b",
                "project_b.models::ProductModel",
                (
                    (
                        PythonPath("packages.project_b.test_support.another_helpers"),
                        "create_product_model",
                        "project-b",
                    ),
                ),
                ("another_helpers.py",),
            ),
            (
                "project-b",
                "project_b.error::TestingError",
                (
                    (
                        PythonPath("packages.project_b.test_support.another_helpers"),
                        "create_testing_error",
                        "project-b",
                    ),
                ),
                ("another_helpers.py",),
            ),
            (
                "project-b",
                "project_a.models::UserSummary",
                (
                    (
                        PythonPath("packages.project_b.test_support.another_helpers"),
                        "build_user_summary",
                        "project-b",
                    ),
                ),
                ("another_helpers.py",),
            ),
        ],
    )
    def test_success_with_model_project(
        self,
        test_project_name: str,
        model_symbol_id: str,
        expected_items: tuple[tuple[PythonPath, str, str], ...],
        another_files: tuple[str, ...] | None,
        mocker: MockerFixture,
    ) -> None:
        target_path = FullPath(MONOREPO_FIXTURES_ROOT)
        _, workspace_context = get_workspace_context(target_path)

        project_context = get_project_context(workspace_context, test_project_name)

        if another_files is not None:
            result_paths = tuple(
                ProjectRelativePath(Path("test_support") / file)
                for file in another_files
            )
            mocker.patch(
                "gyomu_test.helper.inventory.search.get_helper_file_paths",
                return_value=Success(result_paths),
            )

        result = get_all_helper_candidates(
            model_identity=simple_create_declaration_identity(id=model_symbol_id),
            test_project_context=project_context,
            workspace_context=workspace_context,
            model_project_context=project_context,
        )
        assert isinstance(result, Success)
        items = tuple(
            (
                identity.get_module_name(),
                identity.get_symbol_name(),
                project.config.name,
            )
            for identity, project in result.unwrap()
        )
        assert items == expected_items
