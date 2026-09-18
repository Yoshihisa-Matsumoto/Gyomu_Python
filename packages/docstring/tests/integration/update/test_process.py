import shutil
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from gyomu_ai_compiler.pipelines.docstring_update.schema.ai_plan import (
    DocstringUpdatePlan,
)
from gyomu_docstring.update.process import process_docstring_update
from gyomu_infra.filesystem.file_io import read_json
from gyomu_python_analysis.analysis.initialize import initialize_project_context
from gyomu_python_analysis.analysis.load_file_context import load_file_analysis_context
from gyomu_schema.option.update import (
    UpdateActionOption,
    UpdateDebugInfoOption,
    UpdateOption,
)
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.types import FullPath
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.docstring.docstring_test_support.helper import (
    FIXTURES_ROOT,
    assert_text_file_equals,
)

# @pytest.fixture
# def project_path(tmp_path: Path) -> Path:
#     fixture_path = FIXTURES_ROOT / "update_e2e"
#     project_path = tmp_path / "update_e2e"

#     shutil.copytree(
#         fixture_path,
#         project_path,
#     )
#     print(project_path)
#     return project_path


@pytest.fixture(scope="session")
def project_path(
    tmp_path_factory: pytest.TempPathFactory,
) -> Path:
    fixture_path = FIXTURES_ROOT / "update_e2e"
    project_path = tmp_path_factory.mktemp("update_e2e")
    print(f"\nDocstring E2E project: {project_path}")
    shutil.copytree(
        fixture_path,
        project_path,
        dirs_exist_ok=True,
    )

    return project_path


@pytest.mark.parametrize(
    "case",
    [
        "simple",
        "existing_docstring",
        "preserve",
        "raises",
        "delete",
        "no_return",
        "class",
        "method",
        "multiple_symbols",
        "no_update",
    ],
)
@pytest.mark.asyncio
async def test_update(
    case: str,
    project_path: Path,
    mocker: MockerFixture,
) -> None:
    result = initialize_project_context(
        project_root=FullPath(project_path),
        source_root=ProjectRelativePath(Path("src")),
    )
    assert isinstance(result, Success)

    project_context = result.unwrap()

    assert project_context.name == "test-fixture"

    file_path = ProjectRelativePath(Path("src") / "docstring" / (case + ".py"))

    result = load_file_analysis_context(
        context=project_context,
        file_path=file_path,
    )
    assert isinstance(result, Success)

    file_context = result.unwrap()

    result = read_json(
        project_path / "expected_plan" / (case + ".json"), DocstringUpdatePlan
    )
    assert isinstance(result, Success)

    plan = result.unwrap()

    mocker.patch(
        "gyomu_docstring.update.internal.build_update_plan.generate_docstring_update_plan",
        new_callable=AsyncMock,
        return_value=Success(plan),
    )

    option = UpdateOption(
        debug_info=UpdateDebugInfoOption(
            dump_to_file=True,
            updated_symbol_docstring=True,
            file_update_plan=True,
            rendered_symbol_docstring=True,
            docstring_update_plan=True,
            docstring_update_context=True,
        )
    )
    if case == "no_update":
        option = UpdateOption(
            debug_info=UpdateDebugInfoOption(
                dump_to_file=True,
                updated_symbol_docstring=True,
                file_update_plan=True,
                rendered_symbol_docstring=True,
                docstring_update_plan=True,
                docstring_update_context=True,
            ),
            action=UpdateActionOption(no_update_docstring=True),
        )

    result = await process_docstring_update(
        context=project_context, file_context=file_context, option=option
    )
    if isinstance(result, Failure):
        print(repr(result.failure()))
    assert isinstance(result, Success)

    expected_path = ProjectRelativePath(Path("expected") / (case + ".py"))
    assert_text_file_equals(
        project_path, source_path=file_path, expected_path=expected_path
    )


# @pytest.mark.asyncio
# async def test_simple(
#     project_path: Path,
#     mocker: MockerFixture,
# ) -> None:
#     result = initialize_project_context(
#         project_root=FullPath(project_path),
#         source_root=ProjectRelativePath(Path("src")),
#     )
#     assert isinstance(result, Success)

#     project_context = result.unwrap()

#     assert project_context.name == "test-fixture"

#     file_path = ProjectRelativePath(Path("src") / "docstring" / "simple.py")

#     result = load_file_analysis_context(
#         context=project_context,
#         file_path=file_path,
#     )
#     assert isinstance(result, Success)

#     file_context = result.unwrap()
#     assert file_context.analysis.name == "simple"
#     assert len(file_context.metadata.symbols) == 1

#     result = read_json(
#         project_path / "expected_plan" / "simple.json", DocstringUpdatePlan
#     )
#     assert isinstance(result, Success)

#     plan = result.unwrap()

#     mocker.patch(
#         "gyomu_docstring.update.internal.build_update_plan.generate_docstring_update_plan",
#         new_callable=AsyncMock,
#         return_value=Success(plan),
#     )

#     option = UpdateOption(
#         debug_info=UpdateDebugInfoOption(
#             dump_to_file=True,
#             updated_symbol_docstring=True,
#             file_update_plan=True,
#             rendered_symbol_docstring=True,
#             docstring_update_plan=True,
#             docstring_update_context=True,
#         )
#     )

#     result = await process_docstring_update(
#         context=project_context, file_context=file_context, option=option
#     )
#     if isinstance(result, Failure):
#         print(repr(result.failure()))
#     assert isinstance(result, Success)

#     expected_path = ProjectRelativePath(Path("expected") / "simple.py")
#     assert_text_file_equals(
#         project_path, source_path=file_path, expected_path=expected_path
#     )
