from dataclasses import dataclass, field

from gyomu_schema.option.analysis import AnalysisDebugInfoOption, AnalysisOption
from gyomu_schema.option.execution import ExecutionOption
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.snapshot.types import FileChange


@dataclass(frozen=True)
class ConceptDebugInfoOption(AnalysisDebugInfoOption):
    """Debug options for the concept update process."""

    directory_concept: bool = False
    package_concept: bool = False
    package_analysis: bool = False
    readme_sections: bool = False
    llm_context_sections: bool = False


@dataclass(frozen=True)
class ConceptActionOption(ExecutionOption):
    """Action options for the concept update process."""

    write_to_temp_folder: bool = False


@dataclass(frozen=True)
class ConceptOption(AnalysisOption):
    """Options for the concept update process."""

    debug_info: ConceptDebugInfoOption = field(
        default_factory=ConceptDebugInfoOption,
    )
    action: ConceptActionOption = field(
        default_factory=ConceptActionOption,
    )
    target_folder: ProjectRelativePath | None = None
    changed_files: tuple[FileChange, ...] | None = None
