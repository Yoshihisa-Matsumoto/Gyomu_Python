from gyomu_python_analysis.update.docstring.file_update_plan import FileUpdatePlan


def apply_file_update_plan(
    source: str,
    plan: FileUpdatePlan,
) -> str:
    result = source

    for item in sorted(
        plan.items,
        key=lambda item: item.location.start_offset,
        reverse=True,
    ):
        result = (
            result[: item.location.start_offset]
            + item.new_text
            + result[item.location.end_offset :]
        )

    return result
