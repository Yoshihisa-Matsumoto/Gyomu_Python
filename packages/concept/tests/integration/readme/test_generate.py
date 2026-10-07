import shutil
from pathlib import Path

import pytest
from gyomu_ai_compiler.pipelines.document import DocumentRouteId
from gyomu_concept.readme.generate import generate_readme_files
from gyomu_infra.filesystem.file_io import write_text
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
    fixture_path = FIXTURES_ROOT / "monorepo"
    project_path = tmp_path_factory.mktemp("monorepo")
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

    write_text(
        path=project_path
        / "packages"
        / "project_a"
        / ".gyomu"
        / "concept"
        / "$Package.json",
        content="""{
  "summary": "Project A is a core Python package that encapsulates domain-specific business logic, data persistence repositories, and data models for orders and users. It provides public services, enums, and utility functions built on top of external validation and functional programming dependencies.",
  "responsibilities": [
    "Encapsulate domain-specific business logic for orders and users.",
    "Provide data persistence repositories and data models.",
    "Offer shared utility functions and result abstractions."
  ],
  "capabilities": [
    {
      "name": "Domain Services",
      "description": "Provide core business logic services, enums, and utility functions for orders and users."
    },
    {
      "name": "Data Persistence",
      "description": "Manage data persistence repositories and data models."
    },
    {
      "name": "Shared Utilities",
      "description": "Handle shared utility functions and result abstractions."
    }
  ],
  "design_decisions": [
    "Encapsulates core domain logic and persistence within a structured submodule hierarchy.",
    "Leverages external libraries like Pydantic for data validation and modeling, and returns for functional result abstractions."
  ],
  "usage_guidance": [
    "Import public services, enums, and functions from the project_a submodule to interact with domain business logic.",
    "Utilize the provided result abstractions and data models for consistent error handling and data validation."
  ]
}
""",  # noqa: E501
    )
    result = initialize_project_context(
        project_root=FullPath(project_path / "packages" / "project_a"),
        source_root=ProjectRelativePath(Path("src")),
    )
    assert isinstance(result, Success)

    project_context = result.unwrap()

    option: ConceptOption = ConceptOption(
        debug_info=ConceptDebugInfoOption(
            dump_to_file=True, directory_concept=True, readme_sections=True
        ),
        action=ConceptActionOption(),
    )
    readme_result = await generate_readme_files(project=project_context, option=option)

    if isinstance(readme_result, Failure):
        print(format_object(readme_result.failure(), depth=5))

    assert isinstance(readme_result, Success)
