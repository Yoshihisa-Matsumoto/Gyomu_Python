from unittest.mock import AsyncMock

import pytest
from gyomu_docstring.error.update import UpdateError
from gyomu_docstring.update.docstring.file_update_plan import FileUpdatePlan
from gyomu_docstring.update.docstring.merge_plan import MergePlan
from gyomu_docstring.update.docstring.rendered_symbol import (
    RenderedSymbolDocstring,
)
from gyomu_docstring.update.docstring.updated_docstring import UpdatedDocstring
from gyomu_docstring.update.process import process_docstring_update
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.option.update import (
    UpdateActionOption,
    UpdateDebugInfoOption,
    UpdateOption,
)
from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from returns.result import Failure, Success

from packages.schema.schema_test_support.helpers import (
    create_file_analysis_context,
    create_function_analysis,
    create_location,
)


@pytest.fixture
def context(mocker) -> ProjectContext:
    context = mocker.Mock(spec=ProjectContext)
    context.name = "test-project"
    return context


@pytest.fixture
def file_context() -> FileAnalysisContext:
    return create_file_analysis_context(
        create_function_analysis(
            indent=0,
            location=create_location(),
        )
    )


@pytest.fixture
def source() -> str:
    return "ABCDEFGHIJKLMNOP"


class TestProcessDocstringUpdate:
    @pytest.mark.asyncio
    async def test_no_symbols_returns_success(
        self,
        mocker,
        context: ProjectContext,
    ) -> None:
        file_context = create_file_analysis_context()

        read_text = mocker.patch(
            "gyomu_docstring.update.process.read_text",
        )
        build_merge_plan = mocker.patch(
            "gyomu_docstring.update.process.build_merge_plan",
            new=AsyncMock(),
        )

        result = await process_docstring_update(
            context,
            file_context,
        )

        assert result == Success(None)

        read_text.assert_not_called()
        build_merge_plan.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_read_source_failure_returns_failure(
        self,
        mocker,
        context: ProjectContext,
        file_context: FileAnalysisContext,
    ) -> None:
        error = UpdateError(
            "failed to read source",
            file_path=file_context.analysis.module_name,
            phase="update",
            identity=None,
        )

        mocker.patch(
            "gyomu_docstring.update.process.source_relative_path_to_full_path",
            return_value=mocker.Mock(),
        )

        mocker.patch(
            "gyomu_docstring.update.process.read_text",
            return_value=Failure(error),
        )

        build_merge_plan = mocker.patch(
            "gyomu_docstring.update.process.build_merge_plan",
            new=AsyncMock(),
        )

        result = await process_docstring_update(
            context,
            file_context,
        )

        assert isinstance(result, Failure)

        failure = result.failure()
        assert failure.message == "fail to read sourcefile"
        assert failure.file_path == file_context.analysis.module_name
        assert failure.phase == "update"
        assert failure.identity is None

        build_merge_plan.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_build_merge_plan_failure_returns_failure(
        self,
        mocker,
        context: ProjectContext,
        file_context: FileAnalysisContext,
        source: str,
    ) -> None:
        error = UpdateError(
            "failed",
            file_path=file_context.analysis.module_name,
            phase="merge-plan",
            identity=None,
        )

        mocker.patch(
            "gyomu_docstring.update.process.source_relative_path_to_full_path",
            return_value=mocker.Mock(),
        )

        mocker.patch(
            "gyomu_docstring.update.process.read_text",
            return_value=Success(source),
        )

        build_merge_plan = mocker.patch(
            "gyomu_docstring.update.process.build_merge_plan",
            new=AsyncMock(return_value=Failure(error)),
        )

        apply_merge_plans = mocker.patch(
            "gyomu_docstring.update.process.apply_merge_plans",
        )

        result = await process_docstring_update(
            context,
            file_context,
        )

        assert isinstance(result, Failure)
        assert result.failure() is error

        build_merge_plan.assert_awaited_once_with(
            context.name,
            file_context=file_context,
            source=source,
            option=None,
        )
        apply_merge_plans.assert_not_called()

    @pytest.mark.asyncio
    async def test_apply_merge_plans_failure_returns_failure(
        self,
        mocker,
        context: ProjectContext,
        file_context: FileAnalysisContext,
        source: str,
    ) -> None:
        error = UpdateError(
            "failed",
            file_path=file_context.analysis.module_name,
            phase="apply-merge",
            identity=None,
        )

        mocker.patch(
            "gyomu_docstring.update.process.source_relative_path_to_full_path",
            return_value=mocker.Mock(),
        )

        mocker.patch(
            "gyomu_docstring.update.process.read_text",
            return_value=Success(source),
        )

        merge_plans = (mocker.Mock(spec=MergePlan),)

        mocker.patch(
            "gyomu_docstring.update.process.build_merge_plan",
            new=AsyncMock(return_value=Success(merge_plans)),
        )

        apply_merge_plans = mocker.patch(
            "gyomu_docstring.update.process.apply_merge_plans",
            return_value=Failure(error),
        )

        render_docstring = mocker.patch(
            "gyomu_docstring.update.process.render_docstring",
        )

        result = await process_docstring_update(
            context,
            file_context,
        )

        assert isinstance(result, Failure)
        assert result.failure() is error

        apply_merge_plans.assert_called_once_with(
            file_context,
            merge_plans,
        )
        render_docstring.assert_not_called()

    @pytest.mark.asyncio
    async def test_processes_update_pipeline(
        self,
        mocker,
        context: ProjectContext,
        file_context: FileAnalysisContext,
        source: str,
    ) -> None:
        source_path = mocker.Mock()
        merge_plans = (mocker.Mock(spec=MergePlan),)
        updated_docstrings = (mocker.Mock(spec=UpdatedDocstring),)
        rendered_docstrings = (mocker.Mock(spec=RenderedSymbolDocstring),)
        file_update_plan = mocker.Mock(spec=FileUpdatePlan)
        updated_source = "UPDATED SOURCE"

        mocker.patch(
            "gyomu_docstring.update.process.source_relative_path_to_full_path",
            return_value=source_path,
        )

        mocker.patch(
            "gyomu_docstring.update.process.read_text",
            return_value=Success(source),
        )

        build_merge_plan = mocker.patch(
            "gyomu_docstring.update.process.build_merge_plan",
            new=AsyncMock(return_value=Success(merge_plans)),
        )

        apply_merge_plans = mocker.patch(
            "gyomu_docstring.update.process.apply_merge_plans",
            return_value=Success(updated_docstrings),
        )

        render_docstring = mocker.patch(
            "gyomu_docstring.update.process.render_docstring",
            return_value=rendered_docstrings[0],
        )

        build_file_update_plan = mocker.patch(
            "gyomu_docstring.update.process.build_file_update_plan",
            return_value=Success(file_update_plan),
        )

        apply_file_update_plan = mocker.patch(
            "gyomu_docstring.update.process.apply_file_update_plan",
            return_value=updated_source,
        )

        write_text = mocker.patch(
            "gyomu_docstring.update.process.write_text",
            return_value=Success(None),
        )

        result = await process_docstring_update(
            context,
            file_context,
        )

        assert result == Success(None)

        build_merge_plan.assert_awaited_once_with(
            context.name,
            file_context=file_context,
            source=source,
            option=None,
        )

        apply_merge_plans.assert_called_once_with(
            file_context,
            merge_plans,
        )

        render_docstring.assert_called_once_with(
            updated_docstrings[0],
        )

        build_file_update_plan.assert_called_once_with(
            file_context,
            rendered_docstrings,
            source,
        )

        apply_file_update_plan.assert_called_once_with(
            source,
            file_update_plan,
        )

        write_text.assert_called_once_with(
            source_path,
            updated_source,
        )

    @pytest.mark.asyncio
    async def test_no_update_docstring_does_not_write(
        self,
        mocker,
        context: ProjectContext,
        file_context: FileAnalysisContext,
        source: str,
    ) -> None:
        option = UpdateOption(
            action=UpdateActionOption(
                no_update_docstring=True,
            ),
        )

        merge_plans = (mocker.Mock(spec=MergePlan),)
        updated_docstrings = (mocker.Mock(spec=UpdatedDocstring),)
        rendered_docstrings = (mocker.Mock(spec=RenderedSymbolDocstring),)
        file_update_plan = mocker.Mock(spec=FileUpdatePlan)

        mocker.patch(
            "gyomu_docstring.update.process.source_relative_path_to_full_path",
            return_value=mocker.Mock(),
        )

        mocker.patch(
            "gyomu_docstring.update.process.read_text",
            return_value=Success(source),
        )

        mocker.patch(
            "gyomu_docstring.update.process.build_merge_plan",
            new=AsyncMock(return_value=Success(merge_plans)),
        )

        mocker.patch(
            "gyomu_docstring.update.process.apply_merge_plans",
            return_value=Success(updated_docstrings),
        )

        mocker.patch(
            "gyomu_docstring.update.process.render_docstring",
            return_value=rendered_docstrings[0],
        )

        mocker.patch(
            "gyomu_docstring.update.process.build_file_update_plan",
            return_value=Success(file_update_plan),
        )

        mocker.patch(
            "gyomu_docstring.update.process.apply_file_update_plan",
            return_value="UPDATED SOURCE",
        )

        write_text = mocker.patch(
            "gyomu_docstring.update.process.write_text",
        )

        result = await process_docstring_update(
            context,
            file_context,
            option,
        )

        assert result == Success(None)
        write_text.assert_not_called()

    @pytest.mark.asyncio
    async def test_build_file_update_plan_failure_returns_failure(
        self,
        mocker,
        context: ProjectContext,
        file_context: FileAnalysisContext,
        source: str,
    ) -> None:
        error = UpdateError(
            "failed",
            file_path=file_context.analysis.module_name,
            phase="update",
            identity=None,
        )

        updated_docstrings = (mocker.Mock(spec=UpdatedDocstring),)

        mocker.patch(
            "gyomu_docstring.update.process.source_relative_path_to_full_path",
            return_value=mocker.Mock(),
        )

        mocker.patch(
            "gyomu_docstring.update.process.read_text",
            return_value=Success(source),
        )

        mocker.patch(
            "gyomu_docstring.update.process.build_merge_plan",
            new=AsyncMock(return_value=Success(())),
        )

        mocker.patch(
            "gyomu_docstring.update.process.apply_merge_plans",
            return_value=Success(updated_docstrings),
        )

        mocker.patch(
            "gyomu_docstring.update.process.render_docstring",
            return_value=mocker.Mock(spec=RenderedSymbolDocstring),
        )

        build_file_update_plan = mocker.patch(
            "gyomu_docstring.update.process.build_file_update_plan",
            return_value=Failure(error),
        )

        apply_file_update_plan = mocker.patch(
            "gyomu_docstring.update.process.apply_file_update_plan",
        )
        write_text = mocker.patch(
            "gyomu_docstring.update.process.write_text",
        )

        result = await process_docstring_update(
            context,
            file_context,
        )

        assert isinstance(result, Failure)
        assert result.failure() is error

        build_file_update_plan.assert_called_once()
        apply_file_update_plan.assert_not_called()
        write_text.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_docstring_update_dumps_debug_info(
        self,
        mocker,
        context: ProjectContext,
        file_context: FileAnalysisContext,
        source: str,
    ) -> None:
        option = UpdateOption(
            debug_info=UpdateDebugInfoOption(
                dump_to_file=True,
                updated_symbol_docstring=True,
                rendered_symbol_docstring=True,
                file_update_plan=True,
            ),
            action=UpdateActionOption(
                no_update_docstring=True,
            ),
        )

        updated_docstrings = (mocker.Mock(spec=UpdatedDocstring),)
        rendered_docstrings = (mocker.Mock(spec=RenderedSymbolDocstring),)
        file_update_plan = mocker.Mock(spec=FileUpdatePlan)

        mocker.patch(
            "gyomu_docstring.update.process.source_relative_path_to_full_path",
            return_value=mocker.Mock(),
        )
        mocker.patch(
            "gyomu_docstring.update.process.read_text",
            return_value=Success(source),
        )
        mocker.patch(
            "gyomu_docstring.update.process.build_merge_plan",
            new=AsyncMock(return_value=Success(())),
        )
        mocker.patch(
            "gyomu_docstring.update.process.apply_merge_plans",
            return_value=Success(updated_docstrings),
        )
        mocker.patch(
            "gyomu_docstring.update.process.render_docstring",
            return_value=rendered_docstrings[0],
        )
        mocker.patch(
            "gyomu_docstring.update.process.build_file_update_plan",
            return_value=Success(file_update_plan),
        )
        mocker.patch(
            "gyomu_docstring.update.process.apply_file_update_plan",
            return_value="UPDATED",
        )

        write_json = mocker.patch(
            "gyomu_docstring.update.process.write_json",
            return_value=Success(None),
        )

        result = await process_docstring_update(
            context,
            file_context,
            option,
        )

        assert result == Success(None)

        assert write_json.call_count == 3
