from collections.abc import Iterable
from pathlib import Path


def stream_to_file(
    stream: Iterable[bytes],
    path: Path,
) -> None:
    """Writes an iterable byte stream to a file.

    Args:
        stream (Iterable[bytes]): An iterable of byte chunks to be written.
        path (Path): The destination file path.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("wb") as file:
        for chunk in stream:
            file.write(chunk)
