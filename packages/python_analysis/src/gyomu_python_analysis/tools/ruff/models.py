from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RuffCheckConfig:
    target: Path
    working_directory: Path


@dataclass(frozen=True)
class RuffCheckResult:
    name: str
    diagnostics: tuple[str, ...]
    details: Mapping[str, object] | None = None
    skipped_reason: str | None = None

    @property
    def success(self) -> bool:
        return not self.diagnostics

    @property
    def skipped(self) -> bool:
        return self.skipped_reason is not None
