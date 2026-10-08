from dataclasses import dataclass

from gyomu_facts.package.analysis import ImportanceDirectorySelection, PackageFacts
from gyomu_schema.conversation.conversation import ConversationSchema
from gyomu_schema.conversation.message import MessageSchema
from gyomu_schema.error.io import GyomuIOError
from gyomu_schema.schemas.concept.directory.concept import DirectoryImportance
from gyomu_schema.schemas.concept.llm_context.input import LlmContextBuildContext
from gyomu_schema.schemas.concept.package.concept import CapabilityConcept
from returns.result import Failure, Result, Success

from gyomu_ai_compiler.prompts.load import load_prompt


@dataclass
class Package:
    responsibilities: list[str]
    capabilities: list[CapabilityConcept]


@dataclass
class DependencyFacts:
    runtime_dependencies: list[str]


@dataclass
class PublicApiFacts:
    exported_symbol_count: int


@dataclass
class ArchitectureFacts:
    directory: str
    responsibilities: list[str]
    relationships: list[str]
    design_decisions: list[str]


@dataclass
class ConstraintsInput:
    human_constraints: tuple[str, ...]
    package_facts: Package
    dependency_facts: DependencyFacts
    public_api_facts: PublicApiFacts
    architecture_facts: list[ArchitectureFacts]


def build_important_constraints_messages(
    context: LlmContextBuildContext,
) -> Result[ConversationSchema, GyomuIOError]:
    prompt_result = load_prompt(name="llm_context/important-constraints.md")
    if isinstance(prompt_result, Failure):
        return prompt_result

    target_directories = PackageFacts(context.analysis).get_ranked_directories(
        option=ImportanceDirectorySelection(
            limits={
                DirectoryImportance.CORE: 5,
                DirectoryImportance.SUPPORTING: 3,
                DirectoryImportance.UTILITY: 0,
            }
        )
    )

    user_data = ConstraintsInput(
        human_constraints=context.knowledge.package.constraints,
        package_facts=Package(
            responsibilities=context.concept.responsibilities,
            capabilities=context.concept.capabilities,
        ),
        dependency_facts=DependencyFacts(
            runtime_dependencies=[
                dependency.package_name for dependency in context.analysis.dependencies
            ]
        ),
        public_api_facts=PublicApiFacts(
            exported_symbol_count=sum(
                directory.fact.public_symbol_count
                for directory in context.analysis.directories
            )
        ),
        architecture_facts=[
            ArchitectureFacts(
                directory=str(directory.path),
                design_decisions=directory.concept.design_decisions,
                relationships=directory.concept.relationships,
                responsibilities=directory.concept.responsibilities,
            )
            for directory in target_directories
        ],
    )
    user_prompt_result = _render_constraint_input_markdown(user_data)
    if isinstance(user_prompt_result, Failure):
        return user_prompt_result

    conversation = ConversationSchema(
        system=MessageSchema.system_text(prompt_result.unwrap())
    ).with_request(MessageSchema.user_text(user_prompt_result.unwrap()))
    return Success(conversation)


def _render_constraint_input_markdown(
    input: ConstraintsInput,
) -> Result[str, GyomuIOError]:
    prompt_result = load_prompt(name="llm_context/important-constraints-input.md")
    if isinstance(prompt_result, Failure):
        return prompt_result

    return Success(
        prompt_result.unwrap()
        .replace(
            "{{HUMAN_CONSTRAINTS}}",
            "\n".join(f"- {c}" for c in input.human_constraints),
        )
        .replace(
            "{{PACKAGE_RESPONSIBILITIES}}",
            "\n".join(f"- {r}" for r in input.package_facts.responsibilities),
        )
        .replace(
            "{{RUNTIME_DEPENDENCIES}}",
            "\n".join(f"- {d}" for d in input.dependency_facts.runtime_dependencies),
        )
        .replace(
            "{{TOTAL_EXPORTED_SYMBOLS}}",
            str(input.public_api_facts.exported_symbol_count),
        )
        .replace(
            "{{DIRECTORY_FACTS}}",
            "\n\n".join(_dump_architecture_fact(a) for a in input.architecture_facts),
        )
    )


def _dump_architecture_fact(fact: ArchitectureFacts) -> str:
    return f"""## {fact.directory}

Responsibilities

{"\n".join(f"- {r}" for r in fact.responsibilities)}

Design Decisions

{"\n".join(f"- {r}" for r in fact.design_decisions)}

Relationships

{"\n".join(f"- {r}" for r in fact.relationships)}"""
