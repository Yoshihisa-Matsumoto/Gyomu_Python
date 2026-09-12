from pathlib import Path

from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from gyomu_schema.error.validation import ValidationError
from pydantic import BaseModel
from returns.result import Failure, Success

from gyomu_infra.filesystem.file_io import (
    ensure_directory,
    read_json,
    read_text,
    write_json,
    write_text,
)


class TestEnsureDirectory:
    def test_creates_directory(self, tmp_path: Path) -> None:
        path = tmp_path / "cache"

        result = ensure_directory(path)

        assert result == Success(None)
        assert path.is_dir()

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        path = tmp_path / "cache" / "nested"

        result = ensure_directory(path)

        assert result == Success(None)
        assert path.is_dir()

    def test_succeeds_when_directory_already_exists(
        self,
        tmp_path: Path,
    ) -> None:
        path = tmp_path / "cache"
        path.mkdir()

        result = ensure_directory(path)

        assert result == Success(None)
        assert path.is_dir()

    def test_returns_failure_when_path_is_file(
        self,
        tmp_path: Path,
    ) -> None:
        path = tmp_path / "cache"
        path.write_text("content")

        result = ensure_directory(path)

        assert isinstance(result, Failure)
        error = result.failure()

        assert isinstance(error, GyomuIOError)
        assert error.layer == IOLayer.FILESYSTEM
        assert error.operation == IOOperation.WRITE
        assert error.target == str(path)


class TestReadText:
    def test_reads_text(self, tmp_path: Path) -> None:
        path = tmp_path / "example.txt"
        path.write_text("Hello, Gyomu!", encoding="utf-8")

        result = read_text(path)

        assert result == Success("Hello, Gyomu!")

    def test_returns_failure_when_file_does_not_exist(
        self,
        tmp_path: Path,
    ) -> None:
        path = tmp_path / "missing.txt"

        result = read_text(path)

        assert isinstance(result, Failure)

        error = result.failure()
        assert isinstance(error, GyomuIOError)
        assert error.layer == IOLayer.FILESYSTEM
        assert error.operation == IOOperation.READ
        assert error.target == str(path)


class TestWriteText:
    def test_writes_text(self, tmp_path: Path) -> None:
        path = tmp_path / "example.txt"

        result = write_text(path, "Hello, Gyomu!")

        assert result == Success(None)
        assert path.read_text(encoding="utf-8") == "Hello, Gyomu!"

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        path = tmp_path / "cache" / "nested" / "example.txt"

        result = write_text(path, "Hello, Gyomu!")

        assert result == Success(None)
        assert path.read_text(encoding="utf-8") == "Hello, Gyomu!"

    def test_does_not_create_parent_when_disabled(
        self,
        tmp_path: Path,
    ) -> None:
        path = tmp_path / "cache" / "example.txt"

        result = write_text(
            path,
            "Hello, Gyomu!",
            create_parent=False,
        )

        assert isinstance(result, Failure)

        error = result.failure()
        assert isinstance(error, GyomuIOError)
        assert error.operation == IOOperation.WRITE
        assert not path.exists()

    def test_overwrites_existing_file(self, tmp_path: Path) -> None:
        path = tmp_path / "example.txt"
        path.write_text("old", encoding="utf-8")

        result = write_text(path, "new")

        assert result == Success(None)
        assert path.read_text(encoding="utf-8") == "new"


class ExampleModel(BaseModel):
    name: str
    value: int


class TestWriteJson:
    def test_writes_model_as_json(self, tmp_path: Path) -> None:
        path = tmp_path / "example.json"
        value = ExampleModel(name="example", value=42)

        result = write_json(path, value)

        assert result == Success(None)
        assert path.exists()
        assert (
            ExampleModel.model_validate_json(
                path.read_text(encoding="utf-8"),
            )
            == value
        )

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        path = tmp_path / "cache" / "nested" / "example.json"
        value = ExampleModel(name="example", value=42)

        result = write_json(path, value)

        assert result == Success(None)
        assert path.exists()

    def test_overwrites_existing_file(self, tmp_path: Path) -> None:
        path = tmp_path / "example.json"

        write_json(
            path,
            ExampleModel(name="old", value=1),
        )

        result = write_json(
            path,
            ExampleModel(name="new", value=2),
        )

        assert result == Success(None)
        assert ExampleModel.model_validate_json(
            path.read_text(encoding="utf-8"),
        ) == ExampleModel(name="new", value=2)


class TestReadJson:
    def test_reads_and_validates_json(self, tmp_path: Path) -> None:
        path = tmp_path / "example.json"
        value = ExampleModel(name="example", value=42)
        path.write_text(value.model_dump_json(), encoding="utf-8")

        result = read_json(path, ExampleModel)

        assert result == Success(value)

    def test_returns_validation_error_for_invalid_json(
        self,
        tmp_path: Path,
    ) -> None:
        path = tmp_path / "example.json"
        path.write_text(
            '{"name": "example", "value": "invalid"}',
            encoding="utf-8",
        )

        result = read_json(path, ExampleModel)

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), ValidationError)

    def test_returns_io_error_when_file_does_not_exist(
        self,
        tmp_path: Path,
    ) -> None:
        path = tmp_path / "missing.json"

        result = read_json(path, ExampleModel)

        assert isinstance(result, Failure)
        assert isinstance(result.failure(), GyomuIOError)

    def test_round_trip(self, tmp_path: Path) -> None:
        path = tmp_path / "example.json"
        value = ExampleModel(name="example", value=42)

        write_result = write_json(path, value)
        assert write_result == Success(None)

        read_result = read_json(path, ExampleModel)

        assert read_result == Success(value)
