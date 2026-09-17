from dataclasses import dataclass, field

from gyomu_schema.option.analysis import AnalysisDebugInfoOption, AnalysisOption
from gyomu_schema.option.execution import ExecutionOption
from gyomu_schema.option.retry import RetryOption


@dataclass(frozen=True)
class UpdateDebugInfoOption(AnalysisDebugInfoOption):
    """Debug options for the docstring update process."""

    docstring_update_context: bool = False
    docstring_update_plan: bool = False
    merge_plan: bool = False
    updated_symbol_docstring: bool = False
    rendered_symbol_docstring: bool = False
    file_update_plan: bool = False


@dataclass(frozen=True)
class UpdateActionOption(ExecutionOption):
    """Action options for the docstring update process."""

    no_update_docstring: bool = False


@dataclass(frozen=True)
class UpdateOption(AnalysisOption):
    """Options for the docstring update process."""

    debug_info: UpdateDebugInfoOption = field(
        default_factory=UpdateDebugInfoOption,
    )
    action: UpdateActionOption = field(
        default_factory=UpdateActionOption,
    )
    retry_option: RetryOption | None = None
