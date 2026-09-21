from pathlib import Path

from gyomu_ai_compiler.pipelines.docstring_update.context.file_context import (
    DocstringFileContext,
)
from gyomu_ai_compiler.pipelines.docstring_update.schema.ai_plan import (
    DocstringUpdatePlan,
)
from gyomu_infra.filesystem.file_io import read_json, write_json, write_text
from gyomu_schema.option.update import UpdateOption
from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from returns.result import Failure, Result, Success

from gyomu_docstring.error.update import UpdateError
from gyomu_docstring.update.docstring.merge_plan import MergePlan, MergePlans
from gyomu_docstring.update.internal.build_file_context import (
    build_docstring_file_context,
)
from gyomu_docstring.update.internal.build_update_plan import (
    build_docstring_update_plan_with_retry,
)
from gyomu_docstring.update.internal.create_merge_plan import create_merge_plan


async def build_merge_plan(
    project_name: str,
    file_context: FileAnalysisContext,
    source: str,
    option: UpdateOption | None = None,
) -> Result[tuple[MergePlan, ...], UpdateError]:
    docstring_context = build_docstring_file_context(
        project_name,
        file_context,
        source,
    )
    if (
        option
        and option.debug_info.docstring_update_context
        and option.debug_info.dump_to_file
    ):
        write_json(
            Path("log") / "DocstringUpdateContext.json",
            docstring_context,
            DocstringFileContext,
        )

    if option and option.action.no_llm_request:
        result = read_json(
            Path("log") / "DocstringUpdatePlan.json", DocstringUpdatePlan
        )
        if isinstance(result, Success):
            plan = result.unwrap()
            target_identity = next(
                (
                    entry
                    for entry in plan.entries
                    if entry.identity.symbol_id.split("::", 1)[0]
                    == file_context.analysis.module_name
                ),
                None,
            )
            if target_identity:
                merge_plans = create_merge_plan(plan)
                plans = MergePlans(plans=tuple(merge_plans))
                if (
                    option
                    and option.debug_info.merge_plan
                    and option.debug_info.dump_to_file
                ):
                    write_json(Path("log") / "MergePlan.json", plans, MergePlans)

                return Success(plans.plans)

        return Success(tuple())
    if (
        option
        and option.debug_info.docstring_update_plan
        and option.debug_info.dump_to_file
    ):
        write_text(Path("log") / "DocstringUpdatePlan.json", "")
    plan_result = await build_docstring_update_plan_with_retry(
        docstring_context,
        file_context,
        option,
    )

    if isinstance(plan_result, Failure):
        return plan_result

    merge_plans = create_merge_plan(plan_result.unwrap())
    plans = MergePlans(plans=tuple(merge_plans))
    if option and option.debug_info.merge_plan and option.debug_info.dump_to_file:
        write_json(Path("log") / "MergePlan.json", plans, MergePlans)

    return Success(plans.plans)
