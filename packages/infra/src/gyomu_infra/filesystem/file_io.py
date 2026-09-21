from collections.abc import Callable
from pathlib import Path

from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from gyomu_schema.error.validation import ValidationError
from gyomu_schema.utility.serialization import dump_json, validate_json
from returns.result import Failure, Result, Success


def ensure_directory(path: Path) -> Result[None, GyomuIOError]:
    try:
        path.mkdir(parents=True, exist_ok=True)
        return Success(None)
    except OSError as error:
        return Failure(
            GyomuIOError(
                "Failed to ensure directory.",
                layer=IOLayer.FILESYSTEM,
                operation=IOOperation.WRITE,
                target=str(path),
                reason=str(error),
            )
        )


def read_text(
    path: Path,
) -> Result[str, GyomuIOError]:
    try:
        with path.open("r", newline="", encoding="utf-8") as file:
            source = file.read()
            return Success(source)
    except OSError as error:
        return Failure(
            GyomuIOError(
                "Failed to read file.",
                layer=IOLayer.FILESYSTEM,
                operation=IOOperation.READ,
                target=str(path),
                reason=str(error),
            )
        )


def write_text(
    path: Path,
    content: str,
    *,
    create_parent: bool = True,
) -> Result[None, GyomuIOError]:
    if create_parent:
        directory_result = ensure_directory(path.parent)

        if isinstance(directory_result, Failure):
            return directory_result

    try:
        with path.open("w", encoding="utf-8", newline="\n") as file:
            file.write(content)

        return Success(None)
    except OSError as error:
        return Failure(
            GyomuIOError(
                "Failed to write file.",
                layer=IOLayer.FILESYSTEM,
                operation=IOOperation.WRITE,
                target=str(path),
                reason=str(error),
            )
        )


def read_json[T](
    path: Path,
    model_type: type[T],
) -> Result[T, GyomuIOError | ValidationError]:
    text_result = read_text(path)

    if isinstance(text_result, Failure):
        return text_result

    return validate_json(model_type, text_result.unwrap())


def write_json[T](
    path: Path, value: T, value_type: type[T], indent: int | None = 2
) -> Result[None, GyomuIOError]:
    content = dump_json(value, value_type, indent=indent)
    return write_text(path, content)


def enumerate_files(
    path: Path,
    filter: Callable[[Path], bool] | None = None,
    relative_to: Path | None = None,
) -> frozenset[Path]:
    files = (file for file in path.rglob("*") if file.is_file())

    if filter is not None:
        files = (file for file in files if filter(file))

    if relative_to:
        return frozenset(file.relative_to(relative_to) for file in files)

    return frozenset(files)
