from pathlib import Path

from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_test.helper.inventory.migration import migrate

from packages.test.test_support.helpers import MONOREPO_FIXTURES_ROOT


class TestMigrate:
    def test_parameter(self) -> None:
        migrate(package_name="parameter", target_path=MONOREPO_FIXTURES_ROOT)

    def test_project_b(self) -> None:
        migrate(
            package_name="project-b",
            target_path=MONOREPO_FIXTURES_ROOT,
            helper_files=(
                ProjectRelativePath(Path("test_support/helpers.py")),
                ProjectRelativePath(Path("test_support/another_helpers.py")),
            ),
        )
