from os import getcwd
from pathlib import Path

from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.types import FullPath
from gyomu_test.helper.inventory.migration import migrate
from pytest_mock import MockerFixture
from returns.result import Success

from packages.test.test_support.helpers import MONOREPO_FIXTURES_ROOT
from packages.test.tests.unit.helper.helpers import (
    get_project_context,
    get_workspace_context,
)


def migrate_default(
    package_name: str,
    mocker: MockerFixture,
    target_path: Path | None = None,
    helper_files: tuple[ProjectRelativePath, ...] = (
        ProjectRelativePath(Path("test_support/helpers.py")),
    ),
) -> None:
    if target_path is None:
        target_path = FullPath(Path(getcwd()))
    else:
        target_path = FullPath(target_path)
    workspace_context = get_workspace_context(target_path)

    project_context = get_project_context(workspace_context, package_name)
    mocker.patch(
        "gyomu_test.helper.inventory.existing.get_helper_file_paths",
        return_value=Success(helper_files),
    )
    migrate(
        workspace_context=workspace_context,
        project_context=project_context,
    )


class TestMigrate:
    def test_parameter(self, mocker: MockerFixture) -> None:
        migrate_default(
            package_name="parameter", target_path=MONOREPO_FIXTURES_ROOT, mocker=mocker
        )

    def test_project_b(self, mocker: MockerFixture) -> None:
        migrate_default(
            package_name="project-b",
            target_path=MONOREPO_FIXTURES_ROOT,
            mocker=mocker,
            helper_files=(
                ProjectRelativePath(Path("test_support/helpers.py")),
                ProjectRelativePath(Path("test_support/another_helpers.py")),
            ),
        )
