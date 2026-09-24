from pathlib import Path

from gyomu_infra.filesystem.file_io import (
    read_source_text,
    write_json,
    write_text,
)
from gyomu_infra.logger import logger
from gyomu_python_analysis.path.conversion import (
    source_relative_path_to_full_path,
    source_relative_path_to_project_relative_path,
)
from gyomu_python_analysis.project.context import ProjectContext
from gyomu_schema.option.update import UpdateOption
from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from returns.result import Failure, Result, Success

from gyomu_docstring.error.update import UpdateError
from gyomu_docstring.update.apply_file_update import apply_file_update_plan
from gyomu_docstring.update.apply_merge import apply_merge_plans
from gyomu_docstring.update.build_file_update import build_file_update_plan
from gyomu_docstring.update.build_merge import build_merge_plan
from gyomu_docstring.update.docstring.file_update_plan import FileUpdatePlan
from gyomu_docstring.update.docstring.rendered_symbol import RenderedSymbolDocstring
from gyomu_docstring.update.docstring.updated_docstring import UpdatedDocstring
from gyomu_docstring.update.render_docstring import render_docstring
from gyomu_docstring.update.validation import validate_source


async def process_docstring_update(
    context: ProjectContext,
    file_context: FileAnalysisContext,
    option: UpdateOption | None = None,
) -> Result[None, UpdateError]:

    if not file_context.metadata.symbols:
        return Success(None)

    source_path = source_relative_path_to_full_path(
        file_context.analysis.path,
        context,
    )

    source_result = read_source_text(source_path)

    if isinstance(source_result, Failure):
        return Failure(
            UpdateError(
                message="fail to read sourcefile",
                file_path=file_context.analysis.module_name,
                phase="update",
                identity=None,
            ).chain(source_result.failure())
        )

    source = source_result.unwrap()

    plan_result = await build_merge_plan(
        context.config.name, file_context=file_context, source=source, option=option
    )

    if isinstance(plan_result, Failure):
        return plan_result

    merge_plans = plan_result.unwrap()

    updated_result = apply_merge_plans(
        file_context,
        tuple(merge_plans),
    )

    if isinstance(updated_result, Failure):
        return updated_result

    updated_docstrings = updated_result.unwrap()

    # debug
    if (
        option
        and option.debug_info.dump_to_file
        and option.debug_info.updated_symbol_docstring
    ):
        write_json(
            Path("log") / "UpdatedDocstrings.json",
            updated_docstrings,
            tuple[UpdatedDocstring, ...],
        )

    rendered_docstrings = tuple(
        render_docstring(updated, context.config.formatter_line_length)
        for updated in updated_docstrings
    )

    # debug
    if (
        option
        and option.debug_info.dump_to_file
        and option.debug_info.rendered_symbol_docstring
    ):
        write_json(
            Path("log") / "RenderedDocstrings.json",
            rendered_docstrings,
            tuple[RenderedSymbolDocstring, ...],
        )

    file_plan_result = build_file_update_plan(
        file_context,
        rendered_docstrings,
        source,
    )

    if isinstance(file_plan_result, Failure):
        return file_plan_result

    file_update_plan = file_plan_result.unwrap()

    # debug
    if option and option.debug_info.dump_to_file and option.debug_info.file_update_plan:
        write_json(
            Path("log") / "FileUpdatePlan.json",
            file_update_plan,
            FileUpdatePlan,
        )

    updated_source = apply_file_update_plan(
        source,
        file_update_plan,
    )

    if option and option.action.no_update_docstring:
        return Success(None)

    write_result = write_text(
        source_path,
        updated_source,
    )

    if isinstance(write_result, Failure):
        return Failure(
            UpdateError(
                message="fail to update sourcefile",
                file_path=file_context.analysis.module_name,
                phase="update",
                identity=None,
            ).chain(write_result.failure())
        )

    validate_result = validate_source(
        source_path=source_relative_path_to_project_relative_path(
            file_context.analysis.path, context
        ),
        project_root=context.project_root,
        file_context=file_context,
    )

    if isinstance(validate_result, Failure):
        rollback_result = write_text(
            source_path,
            source,
        )
        if isinstance(rollback_result, Failure):
            logger.error("fail to rollback updated source file")
            logger.error(str(rollback_result.failure()))

        logger.error(f"updated source file is invalid on {context.source_root}")
        logger.error(updated_source)
        logger.error_object(validate_result.failure())
        return validate_result

    return Success(None)
