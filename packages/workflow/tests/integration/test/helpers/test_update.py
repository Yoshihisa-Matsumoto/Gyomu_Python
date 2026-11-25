import shutil
import subprocess
from pathlib import Path

import pytest
from gyomu_interaction_cli.executor import CliInteractionExecutor
from gyomu_python_analysis.analysis.workspace import find_root
from gyomu_schema.schemas.types import FullPath
from gyomu_schema.utility.fromatting import format_object
from gyomu_workflow.snapshot.project import find_project_by_name
from gyomu_workflow.test.helpers.update import update_helper_inventories
from returns.result import Failure, Success

from packages.workflow.test_support.helpers import MONOREPO_FIXTURES_ROOT

pytestmark = pytest.mark.integration

# uv run pytest -s -m integration ***


@pytest.fixture(scope="session")
def monorepo_path(
    tmp_path_factory: pytest.TempPathFactory,
) -> Path:
    fixture_path = MONOREPO_FIXTURES_ROOT
    project_path = tmp_path_factory.mktemp("helpers_e2e")
    print(f"\nCurrentPath: {Path.cwd()}")
    print(f"\nHelpers E2E project: {project_path}")
    shutil.copytree(
        fixture_path,
        project_path,
        dirs_exist_ok=True,
    )

    subprocess.run(
        ["uv", "sync"],
        cwd=project_path,
        check=True,
    )

    return project_path


def _update(monorepo_path: Path, project_name: str) -> None:
    workspace_result = find_root(FullPath(monorepo_path))
    if isinstance(workspace_result, Failure):
        print(format_object(workspace_result.failure()))

    assert isinstance(workspace_result, Success)

    workspace_context = workspace_result.unwrap()
    package = project_name
    package_result = find_project_by_name(workspace_context, package)
    if isinstance(package_result, Failure):
        print(f"{package} Not Found")
        print(format_object(package_result.failure()))
    assert isinstance(package_result, Success)

    workspace_project_context = package_result.unwrap()
    interaction: CliInteractionExecutor = CliInteractionExecutor()

    result = update_helper_inventories(
        workspace_context=workspace_context,
        workspace_project_context=workspace_project_context,
        interaction=interaction,
    )
    if isinstance(result, Failure):
        print(f"{package} Helper Update Fail")
        print(format_object(result.failure(), depth=8))
    assert isinstance(result, Success)


@pytest.mark.integration
def test_project_a(monorepo_path: Path) -> None:
    _update(monorepo_path=monorepo_path, project_name="project-a")


@pytest.mark.integration
def test_project_a2(monorepo_path: Path) -> None:
    _update(monorepo_path=monorepo_path, project_name="project-a2")


@pytest.mark.integration
def test_project_a3(monorepo_path: Path) -> None:
    _update(monorepo_path=monorepo_path, project_name="project-a3")


@pytest.mark.integration
def test_project_b(monorepo_path: Path) -> None:
    _update(monorepo_path=monorepo_path, project_name="project-b")
