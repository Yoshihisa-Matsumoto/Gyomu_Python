from pathlib import Path

from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from gyomu_schema.error.validation import ValidationError
from gyomu_schema.utility.serialization import dump_json, validate_json
from pydantic import BaseModel
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
        return Success(path.read_text(encoding="utf-8"))
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
        path.write_text(content, encoding="utf-8")
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


def read_json[T: BaseModel](
    path: Path,
    model_type: type[T],
) -> Result[T, GyomuIOError | ValidationError]:
    text_result = read_text(path)

    if isinstance(text_result, Failure):
        return text_result

    return validate_json(model_type, text_result.unwrap())


def write_json(
    path: Path,
    value: BaseModel,
) -> Result[None, GyomuIOError]:
    content = dump_json(value)
    return write_text(path, content)
