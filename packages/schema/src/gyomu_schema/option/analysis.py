from dataclasses import dataclass, field


@dataclass(frozen=True)
class AnalysisDebugInfoOption:
    """Debug options for Python code analysis."""

    dump_to_file: bool = False
    """Whether to dump debug information to a file."""
    keyword: str | None = None
    """Optional keyword filter for debug information."""
    trace: bool = False
    """Whether to enable trace logging."""


@dataclass(frozen=True)
class AnalysisOption:
    """Options for Python code analysis."""

    debug_info: AnalysisDebugInfoOption = field(
        default_factory=AnalysisDebugInfoOption,
    )
    """Debug options for analysis."""

    no_check_cache: bool = False
    """Whether to skip checking the cache during analysis."""
