from gyomu_schema.schemas.concept.directory.concept import DirectoryImportance
from gyomu_schema.schemas.concept.package.analysis import DirectoryAnalysis


def rank_directories_by_score(
    directories: tuple[DirectoryAnalysis, ...],
) -> tuple[DirectoryAnalysis, ...]:
    if not directories:
        return ()

    max_public_symbol_count = max(
        directory.fact.public_symbol_count for directory in directories
    )

    importance_order = {
        DirectoryImportance.CORE: 3,
        DirectoryImportance.SUPPORTING: 2,
        DirectoryImportance.UTILITY: 1,
    }

    scored = [
        (
            calculate_score(
                entry=directory,
                max_public_symbol_count=max_public_symbol_count,
            ),
            directory,
        )
        for directory in directories
    ]

    scored.sort(
        key=lambda item: (
            item[0],
            importance_order[item[1].concept.importance],
        ),
        reverse=True,
    )

    return tuple(directory for _, directory in scored)


def calculate_score(
    entry: DirectoryAnalysis,
    max_public_symbol_count: int,
) -> float:
    importance_score = {
        DirectoryImportance.CORE: 50,
        DirectoryImportance.SUPPORTING: 30,
        DirectoryImportance.UTILITY: 15,
    }[entry.concept.importance]

    public_score = (
        0
        if max_public_symbol_count == 0
        else entry.fact.public_symbol_count / max_public_symbol_count * 50
    )

    return importance_score + public_score
