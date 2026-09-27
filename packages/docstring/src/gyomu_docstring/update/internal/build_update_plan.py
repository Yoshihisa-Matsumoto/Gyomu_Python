from pathlib import Path

from gyomu_ai_compiler.pipelines.docstring_update.context.file_context import (
    DocstringFileContext,
    DocstringRetryOption,
)
from gyomu_ai_compiler.pipelines.docstring_update.executor.update_plan import (
    generate_docstring_update_plan,
)
from gyomu_ai_compiler.pipelines.docstring_update.schema.ai_plan import (
    DocstringUpdatePlan,
)
from gyomu_infra.filesystem.file_io import write_json
from gyomu_infra.logger import logger
from gyomu_schema.option.update import UpdateOption
from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from gyomu_schema.utility.fromatting import format_object
from returns.pipeline import is_successful
from returns.result import Failure, Result, Success

from gyomu_docstring.error.update import UpdateError
from gyomu_docstring.update.internal.validate import (
    ValidResult,
    get_docstring_identities_from_context,
    validate_docstring_update_plan,
)


async def build_docstring_update_plan_with_retry(
    context: DocstringFileContext,
    file_context: FileAnalysisContext,
    option: UpdateOption | None = None,
) -> Result[DocstringUpdatePlan, UpdateError]:
    """Builds a docstring update plan with retry capabilities upon validation failures.

    Builds a docstring update plan with retry attempts on validation failure.

    Args:
        context (DocstringFileContext): The docstring file context.
        file_context (FileAnalysisContext): The file analysis context.
        option (UpdateOption | None): Optional update options.

    Returns:
        Result[DocstringUpdatePlan, UpdateError]: A Result containing the
            DocstringUpdatePlan or an UpdateError.
    """
    current_context = context
    original_plan: DocstringUpdatePlan | None = None

    for attempt in range(5):
        plan_result = await generate_docstring_update_plan(
            current_context,
        )

        if not is_successful(plan_result):
            return Failure(
                UpdateError(
                    message="AI Failure",
                    file_path=file_context.analysis.module_name,
                    phase="merge-plan",
                    identity=None,
                    context="gyomu_docstring.update.internal.build_docstring_update_plan.build_docstring_update_plan_with_retry",
                ).chain(plan_result.failure())
            )
        plan = plan_result.unwrap()
        # debug
        if (
            option
            and option.debug_info.docstring_update_plan
            and option.debug_info.dump_to_file
        ):
            write_json(
                Path("log") / "DocstringUpdatePlan.json", plan, DocstringUpdatePlan
            )

        override_plan = override_docstring_update_plan(
            current_context,
            plan,
            original_plan,
        )

        validation = validate_docstring_update_plan(
            current_context,
            override_plan,
        )

        if isinstance(validation, ValidResult):
            return Success(override_plan)

        original_plan = override_plan

        logger.debug(f"missing identity: {format_object(validation.diff)}")
        current_context = current_context.model_copy(
            update={
                "retry": DocstringRetryOption(
                    attempt=attempt + 1,
                    missing_identity=validation.diff,
                ),
            },
        )

    return Failure(
        UpdateError(
            message="fail to retrieve correct Docstring with maximum retry",
            file_path=file_context.analysis.module_name,
            phase="merge-plan",
            identity=None,
            context="gyomu_docstring.update.internal.build_docstring_update_plan.build_docstring_update_plan_with_retry",
        )
    )


def override_docstring_update_plan(
    context: DocstringFileContext,
    plan: DocstringUpdatePlan,
    original_plan: DocstringUpdatePlan | None,
) -> DocstringUpdatePlan:
    """Overrides or filters a docstring update plan based on the execution context and
    retry state.

    Overrides or filters a docstring update plan based on context and retry missing
    identities.

    Args:
        context (DocstringFileContext): The docstring file context.
        plan (DocstringUpdatePlan): The current docstring update plan.
        original_plan (DocstringUpdatePlan | None): The optional original docstring
            update plan.

    Returns:
        DocstringUpdatePlan: The overridden DocstringUpdatePlan.
    """
    if original_plan is None or context.retry is None:
        context_identities = get_docstring_identities_from_context(context)

        filtered_entries = tuple(
            entry for entry in plan.entries if entry.identity in context_identities
        )

        return DocstringUpdatePlan(entries=filtered_entries)

    override_entries = list(original_plan.entries)

    for identity in context.retry.missing_identity:
        target_entry = next(
            (entry for entry in plan.entries if entry.identity == identity),
            None,
        )

        if target_entry is not None:
            override_entries.append(target_entry)

    return DocstringUpdatePlan(entries=tuple(override_entries))
