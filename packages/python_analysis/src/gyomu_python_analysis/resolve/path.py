from gyomu_schema.schemas.python.import_analysis import ImportAnalysis, ImportKind


def _is_dotted_name(value: str) -> bool:
    """Return whether the value is a dot-separated sequence of identifiers."""
    return all(part.isidentifier() for part in value.split("."))


def normalize_reference_name(
    imported: tuple[ImportAnalysis, ...],
    reference_name: str,
) -> str:
    """Normalize a reference name using import analysis results.

    Examples:
        Base.BaseModel -> pydantic.BaseModel
        Alpha -> pydantic.BaseModel
        list[str] -> list[str]
    """
    if not _is_dotted_name(reference_name):
        return reference_name

    candidates = sorted(
        (
            imp
            for imp in imported
            if _is_dotted_name(imp.local_name)
            and (
                reference_name == imp.local_name
                or reference_name.startswith(f"{imp.local_name}.")
            )
        ),
        key=lambda imp: len(imp.local_name),
        reverse=True,
    )

    for imp in candidates:
        # For an unaliased dotted module import such as
        # `import package.submodule`, Python binds `package`.
        # Its references are already expressed from that root.
        if imp.kind == ImportKind.MODULE and imp.imported_name.startswith(
            f"{imp.local_name}."
        ):
            continue

        suffix = reference_name[len(imp.local_name) :]
        return f"{imp.imported_name}{suffix}"

    return reference_name
