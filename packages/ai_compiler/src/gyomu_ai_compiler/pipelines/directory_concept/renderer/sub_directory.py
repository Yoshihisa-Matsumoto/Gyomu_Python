from gyomu_schema.schemas.concept.directory.input import SubDirectoryInput


def render_sub_directory(dir: SubDirectoryInput) -> str:
    return (
        f"Directory\n{dir.path}\n\n"
        f"Importance:\n{dir.concept.importance}\n\n"
        f"Summary:\n{dir.concept.summary}\n\n"
        f"Responsibilities:\n{', '.join(dir.concept.responsibilities)}\n\n"
        f"Relationships:\n{', '.join(dir.concept.relationships)}\n\n"
        f"Design decisions:\n{', '.join(dir.concept.design_decisions)}\n"
    )
