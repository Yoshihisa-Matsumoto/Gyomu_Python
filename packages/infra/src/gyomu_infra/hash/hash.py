import hashlib
from pathlib import Path

from gyomu_schema.error.io import GyomuIOError
from returns.result import Failure, Result, Success


def sha256(value: str | bytes) -> str:
    data = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(data).hexdigest()


def hash_file(path: Path) -> Result[str, GyomuIOError]:
    try:
        hasher = hashlib.sha256()

        with path.open("rb") as file:
            while chunk := file.read(1024 * 1024):
                hasher.update(chunk)

        return Success(hasher.hexdigest())
    except OSError as error:
        return Failure(GyomuIOError(str(error)))
