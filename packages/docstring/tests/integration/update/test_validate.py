from pathlib import Path

import pytest
from gyomu_docstring.update.validation import validate_source
from gyomu_schema.schemas.python.file_analysis import FileAnalysisContext
from gyomu_schema.schemas.python.types import ProjectRelativePath
from gyomu_schema.schemas.types import FullPath
from returns.result import Failure, Success

from packages.schema.schema_test_support.helpers import create_file_analysis_context


@pytest.fixture
def file_context(
    tmp_path: Path,
) -> FileAnalysisContext:
    (tmp_path / "pyproject.toml").write_text(
        """
    [tool.ruff]
    line-length = 88

    [tool.ruff.lint]
    select = ["E", "F"]
    """.strip(),
        encoding="utf-8",
    )
    return create_file_analysis_context()


def test_validate_source_with_real_ruff(
    tmp_path: Path, file_context: FileAnalysisContext
) -> None:
    source = tmp_path / "src" / "example.py"
    source.parent.mkdir()

    source.write_text(
        'def hello():\n    return "hello"\n',
        encoding="utf-8",
    )

    result = validate_source(
        ProjectRelativePath(Path("src/example.py")),
        project_root=FullPath(tmp_path),
        file_context=file_context,
    )

    assert isinstance(result, Success)

    formatted = source.read_text(encoding="utf-8")

    # format後の実際のソースを確認
    assert formatted == ('def hello():\n    return "hello"\n')


def test_validate_invalid_source_with_real_ruff(
    tmp_path: Path, file_context: FileAnalysisContext
) -> None:
    source = tmp_path / "src" / "example.py"
    source.parent.mkdir()

    source.write_text(
        'import os\n\ndef hello():\n    return "hello"\n',
        encoding="utf-8",
    )

    result = validate_source(
        ProjectRelativePath(Path("src/example.py")),
        project_root=FullPath(tmp_path),
        file_context=file_context,
    )

    assert isinstance(result, Failure)
    details = result.failure().details
    assert details
    assert details["exit_code"] != 0
    stdout = details["stdout"]
    assert stdout
    assert isinstance(stdout, str)
    assert "F401" in stdout


def test_validate_source_formats_source_with_real_ruff(
    tmp_path: Path, file_context: FileAnalysisContext
) -> None:
    source = tmp_path / "src" / "example.py"
    source.parent.mkdir()

    source.write_text(
        'def hello( ):\n    return "hello"\n',
        encoding="utf-8",
    )

    result = validate_source(
        ProjectRelativePath(Path("src/example.py")),
        project_root=FullPath(tmp_path),
        file_context=file_context,
    )

    assert isinstance(result, Success)

    formatted = source.read_text(encoding="utf-8")

    assert formatted == ('def hello():\n    return "hello"\n')


def test_validate_source_returns_ruff_check_error_with_real_ruff(
    tmp_path: Path, file_context: FileAnalysisContext
) -> None:
    source = tmp_path / "src" / "example.py"
    source.parent.mkdir()

    source.write_text(
        'import os\nimport sys\n\ndef hello():\n    return "hello"\n',
        encoding="utf-8",
    )

    result = validate_source(
        ProjectRelativePath(Path("src/example.py")),
        project_root=FullPath(tmp_path),
        file_context=file_context,
    )

    assert isinstance(result, Failure)

    error = result.failure()
    assert error.details

    assert error.details["exit_code"] != 0

    stdout = error.details["stdout"]
    assert isinstance(stdout, str)
    assert "F401" in stdout
