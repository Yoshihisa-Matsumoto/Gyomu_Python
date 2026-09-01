from pathlib import Path

from gyomu_python_analysis.analysis.load import load_module
from gyomu_python_analysis.error.analysis import AnalysisError
from gyomu_schema.schemas.python.types import PythonPath, SourceRelativePath
from returns.result import Failure, Success
from tests.helpers import _create_context


def test_loads_module() -> None:
    context = _create_context()

    result = load_module(
        context,
        PythonPath("analysis.import.imports"),
    )

    assert isinstance(result, Success)

    source = result.unwrap()

    assert source.module.name == "imports"
    assert source.path == SourceRelativePath(
        Path("analysis/import/imports.py"),
    )


def test_returns_error_when_module_does_not_exist() -> None:
    context = _create_context()

    result = load_module(
        context,
        PythonPath("analysis.import.not_found"),
    )

    assert isinstance(result, Failure)

    error = result.failure()

    assert isinstance(error, AnalysisError)
    assert error.message == "fail to load source"
    assert error.phase == "source-file-load"
