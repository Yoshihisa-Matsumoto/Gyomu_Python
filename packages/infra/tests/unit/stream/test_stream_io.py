from collections.abc import Iterator
from pathlib import Path

from gyomu_infra.stream.stream_io import stream_to_file


class TestStreamToFile:
    def test_writes_stream_to_file(self, tmp_path: Path) -> None:
        stream = iter(
            [
                b"Hello, ",
                b"World!",
            ]
        )

        path = tmp_path / "output.txt"

        stream_to_file(stream, path)

        assert path.read_bytes() == b"Hello, World!"

    def test_writes_multiple_chunks_in_order(
        self,
        tmp_path: Path,
    ) -> None:
        stream = iter(
            [
                b"first\n",
                b"second\n",
                b"third\n",
            ]
        )

        path = tmp_path / "output.txt"

        stream_to_file(stream, path)

        assert path.read_bytes() == (b"first\nsecond\nthird\n")

    def test_creates_parent_directories(
        self,
        tmp_path: Path,
    ) -> None:
        stream = iter([b"content"])

        path = tmp_path / "nested" / "directory" / "output.txt"

        stream_to_file(stream, path)

        assert path.read_bytes() == b"content"

    def test_supports_lazy_iterator(
        self,
        tmp_path: Path,
    ) -> None:
        consumed: list[int] = []

        def stream() -> Iterator[bytes]:
            for index in range(3):
                consumed.append(index)
                yield f"chunk-{index}".encode()

        path = tmp_path / "output.txt"

        stream_to_file(stream(), path)

        assert consumed == [0, 1, 2]
        assert path.read_bytes() == (b"chunk-0chunk-1chunk-2")

    def test_writes_empty_stream(
        self,
        tmp_path: Path,
    ) -> None:
        path = tmp_path / "output.txt"

        stream_to_file(iter(()), path)

        assert path.exists()
        assert path.read_bytes() == b""
