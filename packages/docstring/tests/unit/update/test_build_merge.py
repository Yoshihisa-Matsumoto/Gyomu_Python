from unittest.mock import AsyncMock

import pytest
from gyomu_ai_compiler.pipelines.docstring_update.context.file_context import (
    DocstringFileContext,
)
from gyomu_ai_compiler.pipelines.docstring_update.schema.ai_plan import (
    DocstringUpdatePlan,
)
from gyomu_docstring.error.update import UpdateError
from gyomu_docstring.update.build_merge import build_merge_plan
from gyomu_docstring.update.docstring.merge_plan import MergePlan
from gyomu_schema.option.update import (
    UpdateDebugInfoOption,
    UpdateOption,
)
from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from returns.result import Failure, Success

from packages.schema.schema_test_support.helpers import (
    create_class_analysis,
    create_file_analysis_context,
    create_location,
)


@pytest.fixture
def file_context():
    return create_file_analysis_context(
        create_class_analysis(indent=0, location=create_location())
    )


@pytest.fixture
def source():
    return "ABCDEFGHIJKLMNOP"


@pytest.mark.asyncio
async def test_build_merge_plan(
    mocker,
    file_context: FileAnalysisContext,
    source: str,
) -> None:
    project_name = "test-project"

    docstring_context = mocker.Mock(spec=DocstringFileContext)
    update_plan = mocker.Mock(spec=DocstringUpdatePlan)
    merge_plans = [
        mocker.Mock(spec=MergePlan),
        mocker.Mock(spec=MergePlan),
    ]

    build_context = mocker.patch(
        "gyomu_docstring.update.build_merge.build_docstring_file_context",
        return_value=docstring_context,
    )

    build_plan = mocker.patch(
        "gyomu_docstring.update.build_merge.build_docstring_update_plan_with_retry",
        new=AsyncMock(return_value=Success(update_plan)),
    )

    create_plan = mocker.patch(
        "gyomu_docstring.update.build_merge.create_merge_plan",
        return_value=list(merge_plans),
    )

    result = await build_merge_plan(
        project_name,
        file_context,
        source,
    )

    assert result == Success(tuple(merge_plans))

    build_context.assert_called_once_with(
        project_name,
        file_context,
        source,
    )

    build_plan.assert_awaited_once_with(
        docstring_context,
        file_context,
        None,
    )

    create_plan.assert_called_once_with(update_plan)


@pytest.mark.asyncio
async def test_build_merge_plan_returns_failure_from_update_plan(
    mocker,
    file_context: FileAnalysisContext,
    source: str,
) -> None:
    error = UpdateError(
        "failed",
        file_path=file_context.analysis.module_name,
        phase="merge-plan",
        identity=None,
    )

    docstring_context = mocker.Mock(spec=DocstringFileContext)

    mocker.patch(
        "gyomu_docstring.update.build_merge.build_docstring_file_context",
        return_value=docstring_context,
    )

    build_plan = mocker.patch(
        "gyomu_docstring.update.build_merge.build_docstring_update_plan_with_retry",
        new=AsyncMock(return_value=Failure(error)),
    )

    create_plan = mocker.patch(
        "gyomu_docstring.update.build_merge.create_merge_plan",
    )

    result = await build_merge_plan(
        "test-project",
        file_context,
        source,
    )

    assert isinstance(result, Failure)
    assert result.failure() is error

    build_plan.assert_awaited_once()
    create_plan.assert_not_called()


@pytest.mark.asyncio
async def test_build_merge_plan_passes_option(
    mocker,
    file_context: FileAnalysisContext,
    source: str,
) -> None:
    option = UpdateOption()

    docstring_context = mocker.Mock(spec=DocstringFileContext)
    update_plan = mocker.Mock(spec=DocstringUpdatePlan)

    mocker.patch(
        "gyomu_docstring.update.build_merge.build_docstring_file_context",
        return_value=docstring_context,
    )

    build_plan = mocker.patch(
        "gyomu_docstring.update.build_merge.build_docstring_update_plan_with_retry",
        new=AsyncMock(return_value=Success(update_plan)),
    )

    mocker.patch(
        "gyomu_docstring.update.build_merge.create_merge_plan",
        return_value=[],
    )

    result = await build_merge_plan(
        "test-project",
        file_context,
        source,
        option,
    )

    assert result == Success(())

    build_plan.assert_awaited_once_with(
        docstring_context,
        file_context,
        option,
    )


@pytest.mark.asyncio
async def test_build_merge_plan_dumps_merge_plan(
    mocker,
    file_context: FileAnalysisContext,
    source: str,
) -> None:
    option = UpdateOption(
        debug_info=UpdateDebugInfoOption(
            dump_to_file=True,
            merge_plan=True,
        ),
    )

    docstring_context = mocker.Mock(spec=DocstringFileContext)
    update_plan = mocker.Mock(spec=DocstringUpdatePlan)
    merge_plans = (mocker.Mock(spec=MergePlan),)

    mocker.patch(
        "gyomu_docstring.update.build_merge.build_docstring_file_context",
        return_value=docstring_context,
    )

    mocker.patch(
        "gyomu_docstring.update.build_merge.build_docstring_update_plan_with_retry",
        new=AsyncMock(return_value=Success(update_plan)),
    )

    mocker.patch(
        "gyomu_docstring.update.build_merge.create_merge_plan",
        return_value=list(merge_plans),
    )

    write_json = mocker.patch(
        "gyomu_docstring.update.build_merge.write_json",
        return_value=Success(None),
    )

    result = await build_merge_plan(
        "test-project",
        file_context,
        source,
        option,
    )

    assert result == Success(merge_plans)

    write_json.assert_called_once()


@pytest.mark.asyncio
async def test_build_merge_plan_dumps_context(
    mocker,
    file_context: FileAnalysisContext,
    source: str,
) -> None:
    option = UpdateOption(
        debug_info=UpdateDebugInfoOption(
            dump_to_file=True,
            docstring_update_context=True,
        ),
    )

    docstring_context = mocker.Mock(spec=DocstringFileContext)
    update_plan = mocker.Mock(spec=DocstringUpdatePlan)

    mocker.patch(
        "gyomu_docstring.update.build_merge.build_docstring_file_context",
        return_value=docstring_context,
    )

    mocker.patch(
        "gyomu_docstring.update.build_merge.build_docstring_update_plan_with_retry",
        new=AsyncMock(return_value=Success(update_plan)),
    )

    mocker.patch(
        "gyomu_docstring.update.build_merge.create_merge_plan",
        return_value=[],
    )

    write_json = mocker.patch(
        "gyomu_docstring.update.build_merge.write_json",
        return_value=Success(None),
    )

    result = await build_merge_plan(
        "test-project",
        file_context,
        source,
        option,
    )

    assert result == Success(())

    write_json.assert_called_once()
