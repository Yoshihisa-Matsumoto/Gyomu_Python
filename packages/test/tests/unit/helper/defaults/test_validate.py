from dataclasses import dataclass
from pathlib import Path

import pytest
from gyomu_python_analysis.analysis.initialize import initialize_project_context
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.types import FullPath
from gyomu_schema.utility.fromatting import format_object
from gyomu_test.helper.defaults.validate import validate_file
from returns.result import Failure, Success

from packages.test.test_support.helpers import MONOREPO_FIXTURES_ROOT
from packages.test.tests.unit.helper.helpers import (
    get_project_context,
    get_workspace_context,
)


@dataclass
class ValidationTestContext:
    workspace_context: WorkspaceContext
    project_context: ProjectContext
    root_project_context: ProjectContext


@pytest.fixture
def validation_test_context() -> ValidationTestContext:
    target_path = FullPath(MONOREPO_FIXTURES_ROOT)
    workspace_context = get_workspace_context(target_path)

    project_context = get_project_context(workspace_context, "parameter")

    root_context_result = initialize_project_context(
        project_root=workspace_context.workspace_root.path,
        source_root=ProjectRelativePath(Path(".")),
    )
    assert isinstance(root_context_result, Success)

    return ValidationTestContext(
        workspace_context=workspace_context,
        project_context=project_context,
        root_project_context=root_context_result.unwrap(),
    )


class TestValidateFile:
    def test_accepts_valid_default_expression(
        self, tmp_path: Path, validation_test_context: ValidationTestContext
    ) -> None:
        source = """
from typing import Literal
from parameter.models import Color

value: Literal[Color.BLUE] = Color.BLUE
"""
        file_path = tmp_path / "test_validation.py"
        file_path.write_text(source)

        result = validate_file(
            file_path,
            project_context=validation_test_context.project_context,
            root_project_context=validation_test_context.root_project_context,
            workspace_context=validation_test_context.workspace_context,
        )
        if isinstance(result, Failure):
            print(format_object(result.failure(), depth=8))

        assert isinstance(result, Success)
