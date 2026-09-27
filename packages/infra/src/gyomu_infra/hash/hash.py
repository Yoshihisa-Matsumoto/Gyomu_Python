import hashlib
from pathlib import Path

from gyomu_schema.error.io import GyomuIOError, IOLayer, IOOperation
from returns.result import Failure, Result, Success


def sha256(value: str | bytes) -> str:
    """Compute the SHA-256 hash of a given string or bytes input.

    Compute the SHA-256 hash of a string or byte sequence.

    Args:
        value (str | bytes): The string or bytes to hash.

    Returns:
        str: The hexadecimal digest of the SHA-256 hash.
    """
    data = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(data).hexdigest()


def short_sha256(value: str | bytes) -> str:
    """Compute a truncated 12-character SHA-256 hash of a string or bytes input.

    Compute a truncated 12-character SHA-256 hash of a string or byte sequence.

    Args:
        value (str | bytes): The string or bytes to hash.

    Returns:
        str: The first 12 characters of the SHA-256 hexadecimal digest.
    """
    return sha256(value)[:12]


def hash_file(path: Path) -> Result[str, GyomuIOError]:
    """Compute the SHA-256 hash of a file at the given path.

    Compute the SHA-256 hash of a file at the specified path.

    Args:
        path (Path): The path to the file to hash.

    Returns:
        Result[str, GyomuIOError]: A Result containing the SHA-256 hexadecimal digest
            string on success, or a GyomuIOError on failure.

    Raises:
        GyomuIOError: Raised if an I/O error occurs while reading the file.
    """
    try:
        hasher = hashlib.sha256()

        with path.open("rb") as file:
            while chunk := file.read(1024 * 1024):
                hasher.update(chunk)

        return Success(hasher.hexdigest())
    except OSError as error:
        return Failure(
            GyomuIOError(
                message="fail to hash file",
                layer=IOLayer.FILESYSTEM,
                operation=IOOperation.READ,
                context="gyomu_infra.hash.hash_file",
                details={"file_name": path},
            ).chain(error)
        )
