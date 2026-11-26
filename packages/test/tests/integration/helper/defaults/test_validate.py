from dataclasses import dataclass

import pytest
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_python_analysis.project.workspace import WorkspaceContext
from gyomu_schema.schemas.types import FullPath
from gyomu_schema.utility.fromatting import format_object
from gyomu_test.helper.defaults.validate import (
    prepare_directory,
    validate_file_parameter,
)
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


@pytest.fixture
def validation_test_context() -> ValidationTestContext:
    target_path = FullPath(MONOREPO_FIXTURES_ROOT)
    workspace_context = get_workspace_context(target_path)

    project_context = get_project_context(workspace_context, "parameter")

    return ValidationTestContext(
        workspace_context=workspace_context,
        project_context=project_context,
    )


pytestmark = pytest.mark.integration


@pytest.mark.integration
def test_accepts_valid_default_expression(
    validation_test_context: ValidationTestContext,
) -> None:
    source = """
from typing import Literal
from parameter.models import Color

value: Literal[Color.BLUE] = Color.BLUE
"""
    prepare_result = prepare_directory(
        project_context=validation_test_context.project_context
    )
    assert isinstance(prepare_result, Success)
    tmp_path = prepare_result.unwrap()
    file_path = tmp_path / "temporally_validation.py"
    file_path.write_text(source)

    result = validate_file_parameter(
        file_path,
        project_context=validation_test_context.project_context,
        workspace_context=validation_test_context.workspace_context,
        parameter_name="value",
    )
    if isinstance(result, Failure):
        print(format_object(result.failure(), depth=8))

    assert isinstance(result, Success)
