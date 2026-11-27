from pathlib import Path
from unittest.mock import Mock

from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.tests_files import enumerate_test_files
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_schema.schemas.python.types import (
    ProjectRelativePath,
    WorkspaceRelativePath,
)


class TestEnumerateTestFiles:
    def test_enumerate_test_files(self, tmp_path: Path) -> None:
        workspace_root = tmp_path
        project_root = workspace_root / "packages" / "example"
        tests_root = project_root / "tests"

        test_file = tests_root / "test_example.py"
        nested_test_file = tests_root / "unit" / "test_service.py"
        init_file = tests_root / "__init__.py"
        text_file = tests_root / "README.txt"
        source_file = project_root / "src" / "example.py"

        for path in (
            test_file,
            nested_test_file,
            init_file,
            text_file,
            source_file,
        ):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("", encoding="utf-8")

        workspace_context = Mock(spec=WorkspaceContext)
        workspace_context.workspace_root = Mock()
        workspace_context.workspace_root.path = workspace_root

        project_context = Mock(spec=ProjectContext)
        project_context.project_root = project_root

        result = enumerate_test_files(
            workspace_context=workspace_context,
            project_context=project_context,
        )

        assert result == frozenset(
            {
                WorkspaceRelativePath(Path("packages/example/tests/test_example.py")),
                WorkspaceRelativePath(
                    Path("packages/example/tests/unit/test_service.py")
                ),
                WorkspaceRelativePath(Path("packages/example/tests/__init__.py")),
            }
        )

    def test_enumerate_test_files_with_custom_test_path(
        self,
        tmp_path: Path,
    ) -> None:
        workspace_root = tmp_path
        project_root = workspace_root / "packages" / "example"
        custom_tests_root = project_root / "integration_tests"

        test_file = custom_tests_root / "test_api.py"
        default_test_file = project_root / "tests" / "test_unit.py"

        for path in (test_file, default_test_file):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("", encoding="utf-8")

        workspace_context = Mock(spec=WorkspaceContext)
        workspace_context.workspace_root = Mock()
        workspace_context.workspace_root.path = workspace_root

        project_context = Mock(spec=ProjectContext)
        project_context.project_root = project_root

        result = enumerate_test_files(
            workspace_context=workspace_context,
            project_context=project_context,
            test_path=ProjectRelativePath(Path("integration_tests")),
        )

        assert result == frozenset(
            {
                WorkspaceRelativePath(
                    Path("packages/example/integration_tests/test_api.py")
                ),
            }
        )
