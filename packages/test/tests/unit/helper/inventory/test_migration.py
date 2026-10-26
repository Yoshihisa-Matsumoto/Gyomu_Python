from os import getcwd
from pathlib import Path

from gyomu_infra.logger import logger
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.types import FullPath
from gyomu_test.helper.inventory.migration import migrate
from gyomu_workflow.snapshot.workspace import get_workspace_context
from returns.result import Failure

from packages.test.test_support.helpers import MONOREPO_FIXTURES_ROOT
from packages.test.tests.unit.helper.inventory.helpers import get_project_context


def migrate_default(
    package_name: str,
    target_path: Path | None = None,
    helper_files: tuple[ProjectRelativePath, ...] = (
        ProjectRelativePath(Path("test_support/helpers.py")),
    ),
) -> None:
    if target_path is None:
        target_path = FullPath(Path(getcwd()))
    else:
        target_path = FullPath(target_path)
    workspace_result = get_workspace_context(target_path)
    if isinstance(workspace_result, Failure):
        logger.error_object(workspace_result.failure())
        return
    workspace_context = workspace_result.unwrap()

    project_context = get_project_context(workspace_context, package_name)

    migrate(
        workspace_context=workspace_context,
        project_context=project_context,
        helper_files=helper_files,
    )


class TestMigrate:
    def test_parameter(self) -> None:
        migrate_default(package_name="parameter", target_path=MONOREPO_FIXTURES_ROOT)

    def test_project_b(self) -> None:
        migrate_default(
            package_name="project-b",
            target_path=MONOREPO_FIXTURES_ROOT,
            helper_files=(
                ProjectRelativePath(Path("test_support/helpers.py")),
                ProjectRelativePath(Path("test_support/another_helpers.py")),
            ),
        )
