from gyomu_schema.schemas.concept.directory.input import SubDirectoryInput


def render_sub_directory(dir: SubDirectoryInput) -> str:
    """Render a subdirectory concept into a formatted string.

    Renders a SubDirectoryInput object into a formatted string containing directory
    path, importance, summary, responsibilities, relationships, and design decisions.

    Args:
        dir (SubDirectoryInput): The subdirectory input data containing concept and path
            details.

    Returns:
        str: A formatted string containing the rendered directory concept details.
    """
    return (
        f"Directory\n{dir.path}\n\n"
        f"Importance:\n{dir.concept.importance}\n\n"
        f"Summary:\n{dir.concept.summary}\n\n"
        f"Responsibilities:\n{', '.join(dir.concept.responsibilities)}\n\n"
        f"Relationships:\n{', '.join(dir.concept.relationships)}\n\n"
        f"Design decisions:\n{', '.join(dir.concept.design_decisions)}\n"
    )
