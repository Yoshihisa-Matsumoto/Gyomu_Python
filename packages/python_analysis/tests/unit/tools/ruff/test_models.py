from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest
from gyomu_python_analysis.tools.ruff.models import RuffCheckConfig, RuffCheckResult


class TestRuffCheckConfig:
    def test_stores_target_and_working_directory(self) -> None:
        target = Path("packages/example/src")
        working_directory = Path(".")

        actual = RuffCheckConfig(
            target=target,
            working_directory=working_directory,
        )

        assert actual.target == target
        assert actual.working_directory == working_directory

    def test_is_immutable(self) -> None:
        config = RuffCheckConfig(
            target=Path("example.py"),
            working_directory=Path("."),
        )

        with pytest.raises(FrozenInstanceError):
            config.target = Path("other.py")  # type: ignore[misc]


class TestRuffCheckResult:
    def test_success_when_no_diagnostics(self) -> None:
        actual = RuffCheckResult(
            name="ruff format",
            diagnostics=(),
        )

        assert actual.success
        assert not actual.skipped

    def test_failure_when_diagnostics_exist(self) -> None:
        actual = RuffCheckResult(
            name="ruff check",
            diagnostics=("example.py:1:1: F401 unused import",),
        )

        assert not actual.success
        assert not actual.skipped

    def test_skipped_when_skipped_reason_exists(self) -> None:
        actual = RuffCheckResult(
            name="ruff check",
            diagnostics=(),
            skipped_reason="No target files",
        )

        assert actual.success
        assert actual.skipped
