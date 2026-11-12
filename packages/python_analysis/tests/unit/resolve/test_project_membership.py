from typing import cast
from unittest.mock import Mock

import pytest
from gyomu_python_analysis.project.context import (
    PackageRoot,
    ProjectContext,
    WorkspaceProject,
)
from gyomu_python_analysis.project.workspace import WorkspaceContext, WorkspaceRoot
from gyomu_python_analysis.resolve.project_membership import (
    find_workspace_project,
    is_file_in_project,
)
from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from pytest_mock import MockerFixture
from returns.result import Failure

from packages.python_analysis.test_support.helpers import (
    create_package_root,
    create_workspace_root,
)


def create_file_context(module_name: str) -> FileAnalysisContext:
    file_context = Mock()
    file_context.analysis.module_name = module_name
    return cast(FileAnalysisContext, file_context)


def create_project_context(
    package_roots: tuple[PackageRoot, ...],
) -> ProjectContext:
    project_context = Mock()
    project_context.package_roots = package_roots
    return cast(ProjectContext, project_context)


def create_workspace_context(
    workspace_root: WorkspaceRoot,
    projects: tuple[WorkspaceProject, ...],
) -> WorkspaceContext:
    workspace_context = Mock()
    workspace_context.workspace_root = workspace_root
    workspace_context.projects = projects
    return cast(WorkspaceContext, workspace_context)


def create_workspace_project(name: str) -> WorkspaceProject:
    workspace_project = Mock()
    workspace_project.name = name
    return cast(WorkspaceProject, workspace_project)


class TestIsFileInProject:
    @pytest.mark.parametrize(
        ("module_name", "root_names", "expected"),
        [
            ("app", ("app",), True),
            ("app.models", ("app",), True),
            ("app.models.user", ("app",), True),
            ("application.models", ("app",), False),
            ("app.models", (), False),
        ],
    )
    def test_is_file_in_project(
        self,
        module_name: str,
        root_names: tuple[str, ...],
        expected: bool,
    ) -> None:
        file_context = create_file_context(module_name=module_name)
        project_context = create_project_context(
            package_roots=tuple(
                create_package_root(module_name=name) for name in root_names
            )
        )

        assert is_file_in_project(file_context, project_context) is expected


class TestFindWorkspaceProject:
    @pytest.mark.parametrize(
        ("project_roots", "module_name", "expected_index"),
        [
            ((("app",), ("lib",)), "app.models", 0),
            ((("app",), ("lib",)), "lib.models", 1),
            ((("app",), ("lib",)), "other.models", None),
            ((), "app.models", None),
        ],
    )
    def test_find_workspace_project(
        self,
        project_roots: tuple[tuple[str, ...], ...],
        module_name: str,
        expected_index: int | None,
        mocker: MockerFixture,
    ) -> None:
        workspace_projects = tuple(
            create_workspace_project(name=f"project_{i}")
            for i in range(len(project_roots))
        )
        file_context = create_file_context(module_name=module_name)
        workspace_root = create_workspace_root()
        workspace_context = create_workspace_context(
            workspace_root=workspace_root, projects=workspace_projects
        )

        def find_roots(*, workspace_path, project):
            index = workspace_projects.index(project)
            return tuple(
                create_package_root(module_name=name) for name in project_roots[index]
            )

        mocker.patch(
            "gyomu_python_analysis.resolve.project_membership."
            "find_package_roots_from_workspace_project",
            side_effect=find_roots,
        )
        result = find_workspace_project(
            file_context=file_context,
            workspace_context=workspace_context,
        )
        actual = None if isinstance(result, Failure) else result.unwrap()

        expected = (
            workspace_projects[expected_index] if expected_index is not None else None
        )
        assert actual is expected
