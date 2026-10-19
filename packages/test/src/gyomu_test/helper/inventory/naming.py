import re


def _build_helper_name_from_class_name(class_name: str) -> str:
    snake_case = re.sub(
        r"([A-Z]+)([A-Z][a-z])",
        r"\1_\2",
        class_name,
    )
    snake_case = re.sub(
        r"([a-z0-9])([A-Z])",
        r"\1_\2",
        snake_case,
    )
    return f"create_{snake_case.lower()}"


def _build_class_name_from_helper_name(function_name: str) -> str:
    name = function_name.removeprefix("create_")
    leading_underscores = len(name) - len(name.lstrip("_"))
    parts = [part.capitalize() for part in name.split("_") if part]

    return "_" * leading_underscores + "".join(parts)
