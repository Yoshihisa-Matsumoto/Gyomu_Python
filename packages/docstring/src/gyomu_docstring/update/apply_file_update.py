from gyomu_docstring.update.docstring.file_update_plan import FileUpdatePlan


def apply_file_update_plan(
    source: str,
    plan: FileUpdatePlan,
) -> str:
    """Apply a file update plan to source code.

    Applies a file update plan to source code by replacing text segments in reverse
    order of their offsets.

    Args:
        source (str): The original source code text.
        plan (FileUpdatePlan): The file update plan containing items to apply.

    Returns:
        str: The updated source code string.
    """
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
