from collections.abc import Mapping
from pathlib import Path

from gyomu_schema.schemas.types import FullPath
from gyomu_test.error.test import GyomuTestError

MONOREPO_FIXTURES_ROOT = FullPath(Path(__file__).parent / "monorepo_fixtures")


def create_test_error(
    message: str = "Test", details: Mapping[str, object] | None = None
) -> GyomuTestError:
    return GyomuTestError(message=message, details=details)
