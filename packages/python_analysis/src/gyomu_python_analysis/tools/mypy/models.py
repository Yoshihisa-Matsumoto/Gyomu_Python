from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class MypyTarget(Enum):
    SOURCE = "src"
    TESTS = "tests"
    TEST_SUPPORT = "test_support"


@dataclass(frozen=True)
class MypyCheckConfig:
    targets: tuple[Path, ...]
    config_file: Path | None
    """Configuration file path.

    Gyomu Context:
        None means to use the workspace root's pyproject.toml.
    """
    cache_dir: Path | None
    """Directory for mypy's cache.

    Gyomu Context:
        None means to disable mypy's cache.
    """
    explicit_package_bases: bool
    mypy_path: tuple[Path, ...] | None
    """Directories to set in the MYPYPATH environment variable.

    Gyomu Context:
        None means not to set MYPYPATH, preserving its existing environment value.
        An empty tuple means to set MYPYPATH to an empty value.
    """
    working_directory: Path
    target: MypyTarget | None = None


@dataclass(frozen=True)
class MypyCheckResult:
    name: str
    diagnostics: tuple[str, ...]
    details: Mapping[str, object] | None = None

    @property
    def success(self) -> bool:
        return not self.diagnostics


@dataclass(frozen=True)
class MypyCheckResults:
    src: MypyCheckResult
    test_support: MypyCheckResult
    tests: MypyCheckResult


@dataclass(frozen=True)
class MypyCheckReport:
    results: MypyCheckResults

    @property
    def success(self) -> bool:
        return all(
            not result.diagnostics
            for result in (
                self.results.src,
                self.results.test_support,
                self.results.tests,
            )
        )
