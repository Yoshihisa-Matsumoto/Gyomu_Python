import shutil
from pathlib import Path

import pytest
from gyomu_ai_compiler.pipelines.document import DocumentRouteId
from gyomu_concept.directory.build import build_directory_concept
from gyomu_python_analysis.analysis.initialize import initialize_project_context
from gyomu_schema.error.config import ConfigError
from gyomu_schema.option.concept import (
    ConceptActionOption,
    ConceptDebugInfoOption,
    ConceptOption,
)
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.types import FullPath
from gyomu_schema.utility.fromatting import format_object
from returns.result import Failure, Success

from packages.ai.ai_test_support.helper import register_test_google_routing
from packages.concept.concept_test_support.helpers import FIXTURES_ROOT


@pytest.fixture(scope="session")
def project_path(
    tmp_path_factory: pytest.TempPathFactory,
) -> Path:
    fixture_path = FIXTURES_ROOT / "directory"
    project_path = tmp_path_factory.mktemp("directory")
    print(f"\nCurrentPath: {Path.cwd()}")
    print(f"\nDocstring E2E project: {project_path}")
    shutil.copytree(
        fixture_path,
        project_path,
        dirs_exist_ok=True,
    )

    return project_path


@pytest.mark.integration
@pytest.mark.asyncio
async def test_build_with_real_llm(
    project_path: Path,
    project_dot_env: Path,
) -> None:
    try:
        register_test_google_routing(project_dot_env, [DocumentRouteId])
    except ConfigError:
        pytest.skip("GEMINI_API_KEY is not configured")

    result = initialize_project_context(
        project_root=FullPath(project_path),
        source_root=ProjectRelativePath(Path("src")),
    )
    assert isinstance(result, Success)

    project_context = result.unwrap()

    option: ConceptOption = ConceptOption(
        debug_info=ConceptDebugInfoOption(dump_to_file=True, directory_concept=True),
        action=ConceptActionOption(),
    )
    directory_result = await build_directory_concept(
        context=project_context, option=option
    )

    if isinstance(directory_result, Failure):
        print(format_object(directory_result.failure(), depth=5))

    assert isinstance(directory_result, Success)
    print(format_object(directory_result.unwrap(), depth=5))
