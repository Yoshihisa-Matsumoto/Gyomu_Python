from pathlib import Path

from gyomu_ai_compiler.pipelines.directory_concept.renderer.sub_directory import (
    render_sub_directory,
)
from gyomu_schema.schemas.concept.directory.concept import DirectoryImportance
from gyomu_schema.schemas.concept.directory.input import SubDirectoryInput
from gyomu_schema.schemas.python.types import DirectoryRelativePath

from packages.schema.schema_test_support.concept_helpers import (
    create_directory_concept,
    create_sub_directory_input,
)


class TestRenderSubDirectory:
    def test_returns_formatted_sub_directory(self) -> None:
        directory = create_sub_directory_input(
            path=Path("internal"),
            concept=create_directory_concept(
                summary="Internal implementation.",
                responsibilities=[
                    "Provide internal functionality.",
                    "Encapsulate implementation details.",
                ],
                concepts=["Internal implementation"],
                relationships=[
                    "Internal implementation supports the parent directory."
                ],
                design_decisions=[
                    "Keep implementation details isolated from the public API.",
                    "Use composition for internal components.",
                ],
                importance=DirectoryImportance.SUPPORTING,
            ),
        )

        result = render_sub_directory(directory)

        assert result == (
            "Directory\n"
            "internal\n\n"
            "Importance:\n"
            "Supporting\n\n"
            "Summary:\n"
            "Internal implementation.\n\n"
            "Responsibilities:\n"
            "Provide internal functionality., Encapsulate implementation details.\n\n"
            "Relationships:\n"
            "Internal implementation supports the parent directory.\n\n"
            "Design decisions:\n"
            "Keep implementation details isolated from the public API., "
            "Use composition for internal components.\n"
        )

    def test_returns_empty_values_for_empty_lists(self) -> None:
        directory = SubDirectoryInput(
            path=DirectoryRelativePath(Path("internal")),
            concept=create_directory_concept(
                summary="Internal implementation.",
                responsibilities=[],
                concepts=[],
                relationships=[],
                design_decisions=[],
                importance=DirectoryImportance.SUPPORTING,
            ),
        )

        result = render_sub_directory(directory)

        assert result == (
            "Directory\n"
            "internal\n\n"
            "Importance:\n"
            "Supporting\n\n"
            "Summary:\n"
            "Internal implementation.\n\n"
            "Responsibilities:\n\n\n"
            "Relationships:\n\n\n"
            "Design decisions:\n\n"
        )
