from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

RESOURCE_DIR = Path(__file__).parent.parent.parent / "resources" / "compress"
TEMP_ZIP = RESOURCE_DIR / "temp.zip"


def test_reads_legacy_cp437_filename() -> None:
    with ZipFile(
        TEMP_ZIP,
        mode="r",
        metadata_encoding="cp932",
        # metadata_encoding="cp437",  "cp437"
    ) as archive:
        names = archive.namelist()

    assert "folder1/folder 2/フォルダ噂～３/" in names


def test_reads_entry_metadata() -> None:
    with ZipFile(
        TEMP_ZIP,
        mode="r",
        metadata_encoding="cp932",
    ) as archive:
        for entry in archive.infolist():
            print(
                entry.filename,
                entry.CRC,
                entry.file_size,
                entry.is_dir(),
            )


def test_reads_entry_stream() -> None:
    with ZipFile(
        TEMP_ZIP,
        mode="r",
        metadata_encoding="cp932",
    ) as archive:
        entry = archive.getinfo("folder1/email_sender.py")

        chunks: list[bytes] = []

        with archive.open(entry) as stream:
            while chunk := stream.read(1024):
                chunks.append(chunk)

    content = b"".join(chunks)

    assert len(content) == entry.file_size


class NonSeekableWriter:
    def __init__(self) -> None:
        self.chunks: list[bytes] = []

    def write(self, data: bytes) -> int:
        self.chunks.append(data)
        return len(data)

    def flush(self) -> None:
        pass

    def getvalue(self) -> bytes:
        return b"".join(self.chunks)

    def close(self) -> None:
        pass


def test_zipfile_supports_non_seekable_output() -> None:
    writer = NonSeekableWriter()

    with ZipFile(writer, mode="w") as archive:
        archive.writestr("hello.txt", b"Hello World")

    data = writer.getvalue()

    with ZipFile(BytesIO(data), mode="r") as archive:
        assert archive.namelist() == ["hello.txt"]
        assert archive.read("hello.txt") == b"Hello World"


def test_zipfile_supports_multiple_entries_on_non_seekable_output() -> None:
    writer = NonSeekableWriter()

    with ZipFile(writer, mode="w") as archive:
        archive.writestr("a.txt", b"AAA")
        archive.writestr("folder/b.txt", b"BBB")
        archive.writestr("日本語.txt", b"CCC")

    data = writer.getvalue()

    with ZipFile(BytesIO(data), mode="r") as archive:
        assert archive.namelist() == [
            "a.txt",
            "folder/b.txt",
            "日本語.txt",
        ]

        assert archive.read("a.txt") == b"AAA"
        assert archive.read("folder/b.txt") == b"BBB"
        assert archive.read("日本語.txt") == b"CCC"
