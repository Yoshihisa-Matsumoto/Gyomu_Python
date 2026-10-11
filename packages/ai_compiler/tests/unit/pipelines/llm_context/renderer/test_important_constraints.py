from pathlib import Path

from gyomu_ai_compiler.pipelines.llm_context.renderer.important_constraints import (
    build_important_constraints_messages,
)
from gyomu_facts.package.analysis import ImportanceDirectorySelection
from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from gyomu_schema.schemas.concept.directory.concept import DirectoryImportance
from gyomu_schema.schemas.python.types import ProjectRelativePath
from pytest_mock import MockerFixture
from returns.result import Failure, Success

from packages.schema.schema_test_support.concept_helpers import (
    create_capability_concept,
    create_llm_context_build_context,
    create_llm_knowledge,
    create_package,
    create_package_concept,
)


class TestBuildImportantConstraintsMessages:
    def test_builds_messages(
        self,
        mocker: MockerFixture,
    ) -> None:
        context = create_llm_context_build_context(
            concept=create_package_concept(
                responsibilities=["Package responsibility"],
                capabilities=[
                    create_capability_concept(
                        name="Capability",
                        description="Capability description",
                    ),
                ],
            ),
            knowledge=create_llm_knowledge(
                package=create_package(
                    constraints=("Human constraint 1", "Human constraint 2"),
                ),
            ),
        )

        ranked = [
            mocker.Mock(
                path=ProjectRelativePath(Path("src/core")),
                concept=mocker.Mock(
                    responsibilities=["Core responsibility"],
                    relationships=["Core relationship"],
                    design_decisions=["Core design decision"],
                ),
                fact=mocker.Mock(
                    public_symbol_count=5,
                ),
            ),
        ]

        load_prompt = mocker.patch(
            "gyomu_ai_compiler.pipelines.llm_context.renderer.important_constraints.load_prompt",
            side_effect=[
                Success("important constraints prompt"),
                Success(
                    """Human Constraints

{{HUMAN_CONSTRAINTS}}

Package Responsibilities

{{PACKAGE_RESPONSIBILITIES}}

Runtime Dependencies

{{RUNTIME_DEPENDENCIES}}

Total Exported Symbols

{{TOTAL_EXPORTED_SYMBOLS}}

Directory Facts

{{DIRECTORY_FACTS}}"""
                ),
            ],
        )

        get_ranked = mocker.patch(
            "gyomu_ai_compiler.pipelines.llm_context.renderer.important_constraints"
            ".PackageFacts.get_ranked_directories",
            return_value=ranked,
        )

        result = build_important_constraints_messages(context)

        assert isinstance(result, Success)

        conversation = result.unwrap()

        assert conversation.system
        assert conversation.system.parts[0].text == "important constraints prompt"

        assert conversation.request
        assert len(conversation.request.parts) == 1
        assert conversation.request.parts[0] is not None

        msg = conversation.request.parts[0].text

        assert "- Human constraint 1" in msg
        assert "- Human constraint 2" in msg
        assert "- Package responsibility" in msg
        assert "- Core responsibility" in msg
        assert "- Core relationship" in msg
        assert "- Core design decision" in msg
        assert "- " + "..." not in msg
        assert "Total Exported Symbols" in msg

        get_ranked.assert_called_once_with(
            option=ImportanceDirectorySelection(
                limits={
                    DirectoryImportance.CORE: 5,
                    DirectoryImportance.SUPPORTING: 3,
                    DirectoryImportance.UTILITY: 0,
                }
            )
        )

        assert load_prompt.call_count == 2
        load_prompt.assert_any_call(name="llm_context/important-constraints.md")
        load_prompt.assert_any_call(name="llm_context/important-constraints-input.md")

    def test_propagates_main_prompt_load_failure(
        self,
        mocker: MockerFixture,
    ) -> None:
        error = GyomuIOError(
            "failed to load prompt",
            layer=IOLayer.FILESYSTEM,
            operation=IOOperation.READ,
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.llm_context.renderer.important_constraints.load_prompt",
            return_value=Failure(error),
        )

        result = build_important_constraints_messages(
            create_llm_context_build_context()
        )

        assert result == Failure(error)

    def test_propagates_input_prompt_load_failure(
        self,
        mocker: MockerFixture,
    ) -> None:
        error = GyomuIOError(
            "failed to load input prompt",
            layer=IOLayer.FILESYSTEM,
            operation=IOOperation.READ,
        )

        mocker.patch(
            "gyomu_ai_compiler.pipelines.llm_context.renderer.important_constraints.load_prompt",
            side_effect=[
                Success("important constraints prompt"),
                Failure(error),
            ],
        )

        result = build_important_constraints_messages(
            create_llm_context_build_context()
        )

        assert result == Failure(error)
