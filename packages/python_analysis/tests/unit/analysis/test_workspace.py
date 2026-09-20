import shutil
from pathlib import Path

import pytest
from gyomu_python_analysis.analysis.workspace import (
    find_root,
    get_uv_workspace_members,
    initialize_workspace_config,
    initialize_workspace_context,
    is_uv_workspace,
    read_pyproject_toml,
)
from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_python_analysis.project.workspace import WorkspaceRootKind
from gyomu_schema.schemas.python.types import WorkspaceRelativePath
from gyomu_schema.schemas.types import FullPath
from python_analysis_test_support.helpers import (
    TEST_SUPPORT_ROOT,
)
from returns.result import Failure, Success


@pytest.fixture(scope="session")
def project_path(
    tmp_path_factory: pytest.TempPathFactory,
) -> Path:
    support_path = TEST_SUPPORT_ROOT
    project_path = tmp_path_factory.mktemp("workspace")
    print(f"\nworkspace root: {project_path}")
    shutil.copytree(
        support_path,
        project_path,
        dirs_exist_ok=True,
    )

    return project_path


class TestFindRoot:
    def test_finds_monorepo_root_from_root(self, project_path: Path) -> None:
        MONOREPO_FIXTURES_ROOT = FullPath(project_path / "monorepo_fixtures")
        result = find_root(MONOREPO_FIXTURES_ROOT)

        assert isinstance(result, Success)

        root = result.unwrap()

        assert root.path == MONOREPO_FIXTURES_ROOT
        assert root.kind == WorkspaceRootKind.UV_WORKSPACE

    def test_finds_monorepo_root_from_project(self, project_path: Path) -> None:
        MONOREPO_FIXTURES_ROOT = FullPath(project_path / "monorepo_fixtures")
        project_root = MONOREPO_FIXTURES_ROOT / "packages" / "project_a"

        result = find_root(project_root)

        assert isinstance(result, Success)

        root = result.unwrap()

        assert root.path == MONOREPO_FIXTURES_ROOT
        assert root.kind == WorkspaceRootKind.UV_WORKSPACE

    def test_finds_standalone_project_root(self, project_path: Path) -> None:
        FIXTURES_ROOT = FullPath(project_path / "fixtures")
        result = find_root(FIXTURES_ROOT)

        assert isinstance(result, Success)

        root = result.unwrap()

        assert root.path == FIXTURES_ROOT
        assert root.kind == WorkspaceRootKind.STANDALONE_PROJECT

    def test_returns_failure_when_pyproject_is_not_found(
        self,
        tmp_path: Path,
    ) -> None:
        result = find_root(FullPath(tmp_path))

        assert isinstance(result, Failure)

        error = result.failure()

        assert isinstance(error, AnalysisError)


class TestReadPyprojectToml:
    def test_reads_pyproject_toml(self, project_path: Path) -> None:
        MONOREPO_FIXTURES_ROOT = FullPath(project_path / "monorepo_fixtures")
        path = MONOREPO_FIXTURES_ROOT / "pyproject.toml"

        result = read_pyproject_toml(path)

        assert isinstance(result, Success)

        toml_data = result.unwrap()

        assert "project" in toml_data
        assert "tool" in toml_data

    def test_returns_failure_when_file_does_not_exist(
        self,
        tmp_path: Path,
    ) -> None:
        path = tmp_path / "pyproject.toml"

        result = read_pyproject_toml(FullPath(path))

        assert isinstance(result, Failure)

        error = result.failure()

        assert isinstance(error, AnalysisError)


class TestIsUvWorkspace:
    @pytest.mark.parametrize(
        ("toml_data", "expected"),
        [
            ({}, False),
            ({"project": {}}, False),
            ({"tool": {}}, False),
            ({"tool": {"uv": {}}}, False),
            ({"tool": {"uv": {"workspace": {}}}}, True),
            (
                {
                    "tool": {
                        "uv": {
                            "workspace": {
                                "members": ["packages/project_a"],
                            }
                        }
                    }
                },
                True,
            ),
        ],
    )
    def test_is_uv_workspace(
        self,
        toml_data: dict[str, object],
        expected: bool,
    ) -> None:
        assert is_uv_workspace(toml_data) is expected


class TestInitializeWorkspaceConfig:
    def test_reads_project_information(self, project_path: Path) -> None:
        MONOREPO_FIXTURES_ROOT = FullPath(project_path / "monorepo_fixtures")
        path = MONOREPO_FIXTURES_ROOT / "pyproject.toml"

        toml_result = read_pyproject_toml(path)

        assert isinstance(toml_result, Success)

        result = initialize_workspace_config(
            MONOREPO_FIXTURES_ROOT,
            toml_result.unwrap(),
        )

        assert isinstance(result, Success)

        config = result.unwrap()

        assert config.path == MONOREPO_FIXTURES_ROOT
        assert config.name == "test-monorepo"

    def test_reads_ruff_line_length(self, project_path: Path) -> None:
        MONOREPO_FIXTURES_ROOT = FullPath(project_path / "monorepo_fixtures")
        path = MONOREPO_FIXTURES_ROOT / "pyproject.toml"

        toml_result = read_pyproject_toml(path)

        assert isinstance(toml_result, Success)

        result = initialize_workspace_config(
            MONOREPO_FIXTURES_ROOT,
            toml_result.unwrap(),
        )

        assert isinstance(result, Success)

        config = result.unwrap()

        assert config.formatter_line_length == 88

    def test_allows_missing_project_information(self, project_path: Path) -> None:
        MONOREPO_FIXTURES_ROOT = FullPath(project_path / "monorepo_fixtures")
        result = initialize_workspace_config(
            MONOREPO_FIXTURES_ROOT,
            {},
        )

        assert isinstance(result, Success)

        config = result.unwrap()

        assert config.name is None
        assert config.description is None
        assert config.formatter_line_length == 88

    def test_allows_missing_ruff_configuration(self, project_path: Path) -> None:
        MONOREPO_FIXTURES_ROOT = FullPath(project_path / "monorepo_fixtures")
        result = initialize_workspace_config(
            MONOREPO_FIXTURES_ROOT,
            {
                "project": {
                    "name": "test-project",
                    "description": "Test project",
                }
            },
        )

        assert isinstance(result, Success)

        config = result.unwrap()

        assert config.name == "test-project"
        assert config.description == "Test project"
        assert config.formatter_line_length == 88

    def test_reads_ruff_line_length_with_length_setting(
        self, project_path: Path
    ) -> None:
        MONOREPO_FIXTURES_ROOT = FullPath(project_path / "monorepo_fixtures")
        result = initialize_workspace_config(
            MONOREPO_FIXTURES_ROOT,
            {
                "project": {
                    "name": "test-project",
                },
                "tool": {
                    "ruff": {
                        "line-length": 100,
                    }
                },
            },
        )

        assert isinstance(result, Success)

        config = result.unwrap()

        assert config.formatter_line_length == 100


class TestGetUvWorkspaceMembers:
    def test_returns_workspace_members(self, project_path: Path) -> None:
        MONOREPO_FIXTURES_ROOT = FullPath(project_path / "monorepo_fixtures")
        path = MONOREPO_FIXTURES_ROOT / "pyproject.toml"

        toml_result = read_pyproject_toml(path)

        assert isinstance(toml_result, Success)

        members = get_uv_workspace_members(toml_result.unwrap())

        assert members == [
            "packages/project_a",
            "packages/project_b",
        ]

    def test_returns_empty_list_when_not_workspace(self) -> None:
        assert get_uv_workspace_members({}) == []

    def test_returns_empty_list_when_workspace_is_missing_members(self) -> None:
        toml_data = {
            "tool": {
                "uv": {
                    "workspace": {},
                }
            }
        }

        assert get_uv_workspace_members(toml_data) == []


class TestInitializeWorkspaceContext:
    def test_initializes_monorepo(self, project_path: Path) -> None:
        MONOREPO_FIXTURES_ROOT = FullPath(project_path / "monorepo_fixtures")
        root_result = find_root(MONOREPO_FIXTURES_ROOT)

        assert isinstance(root_result, Success)

        result = initialize_workspace_context(root_result.unwrap())

        assert isinstance(result, Success)

        context = result.unwrap()

        assert context.config.path == MONOREPO_FIXTURES_ROOT
        assert context.config.name == "test-monorepo"

        assert len(context.projects) == 2

        projects = {project.path: project for project in context.projects}

        project_a = projects[WorkspaceRelativePath(Path("packages/project_a"))]
        project_b = projects[WorkspaceRelativePath(Path("packages/project_b"))]

        assert project_a.config.name == "project-a"
        assert project_b.config.name == "project-b"

    def test_initializes_standalone_project(self, project_path: Path) -> None:
        FIXTURES_ROOT = FullPath(project_path / "fixtures")
        root_result = find_root(FIXTURES_ROOT)

        assert isinstance(root_result, Success)

        root = root_result.unwrap()

        assert root.kind == WorkspaceRootKind.STANDALONE_PROJECT

        result = initialize_workspace_context(root)

        assert isinstance(result, Success)

        context = result.unwrap()

        assert len(context.projects) == 1

        project = context.projects[0]

        assert project.path == Path(".")
        assert project.config.path == Path(".")
