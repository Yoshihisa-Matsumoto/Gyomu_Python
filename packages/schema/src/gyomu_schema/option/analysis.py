from dataclasses import dataclass, field


@dataclass(frozen=True)
class AnalysisDebugInfoOption:
    """Debug options for Python code analysis."""

    dump_to_file: bool = False
    keyword: str | None = None
    trace: bool = False


@dataclass(frozen=True)
class AnalysisOption:
    """Options for Python code analysis."""

    debug_info: AnalysisDebugInfoOption = field(
        default_factory=AnalysisDebugInfoOption,
    )

    no_check_cache: bool = False
