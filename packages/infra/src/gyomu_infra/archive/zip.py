import re
import zipfile
from collections import deque
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from gyomu_schema.filesystem.file import (
    FileCompareType,
    FileFilterInfo,
    FileFilterType,
    FileInfo,
    FileTransportInfo,
)

from gyomu_infra.filesystem.file_search import FileSearch


class _StreamingWriter:
    """A non-seekable writer that exposes written chunks incrementally."""

    def __init__(self) -> None:
        self._chunks: deque[bytes] = deque()

    def write(self, data: bytes) -> int:
        self._chunks.append(data)
        return len(data)

    def flush(self) -> None:
        pass

    def close(self) -> None:
        pass

    def pop_chunks(self) -> Iterator[bytes]:
        while self._chunks:
            yield self._chunks.popleft()


@dataclass(frozen=True)
class ZipEntry:
    index: int
    path: str
    crc32: int
    uncompressed_size: int
    is_directory: bool


class Zip:
    def __init__(self, zip_file: Path) -> None:
        self._zip_file = zip_file

    @staticmethod
    def create(
        transfer_information_list: Sequence[FileTransportInfo],
    ) -> Iterator[bytes]:
        writer = _StreamingWriter()

        with zipfile.ZipFile(
            writer,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
        ) as zip_file:
            for transfer_information in transfer_information_list:
                files = Zip._find_files(transfer_information)

                for file_info in files:
                    entry_path = Zip._get_entry_path(
                        transfer_information,
                        file_info,
                    )

                    zip_file.write(
                        file_info.full_path,
                        arcname=entry_path,
                    )

                    yield from writer.pop_chunks()

        # ZipFile.close() writes the central directory.
        yield from writer.pop_chunks()

    @staticmethod
    def _find_files(
        transfer_information: FileTransportInfo,
    ) -> list[FileInfo]:
        source = Path(transfer_information.source_fullname_with_basepath)

        filter_conditions = (
            transfer_information.filter_conditions
            if transfer_information.filter_conditions is not None
            else []
        )

        if transfer_information.is_source_directory:
            return FileSearch.search(
                source,
                filter_conditions,
                recursive=True,
            )

        file_filter = FileFilterInfo(
            FileFilterType.FILE_NAME,
            FileCompareType.EQUAL,
            re.escape(source.name),
        )

        return FileSearch.search(
            source.parent,
            [*filter_conditions, file_filter],
            recursive=False,
        )

    @staticmethod
    def _get_entry_path(
        transfer_information: FileTransportInfo,
        file_info: FileInfo,
    ) -> str:
        source = PurePosixPath(transfer_information.source_fullname)

        if transfer_information.is_source_directory:
            base_path = Path(transfer_information.source_fullname_with_basepath)

            relative_path = file_info.full_path.relative_to(base_path)

            return (source / PurePosixPath(relative_path.as_posix())).as_posix()

        return source.as_posix()

    def entries(self) -> Iterator[ZipEntry]:
        with zipfile.ZipFile(self._zip_file, mode="r") as zip_file:
            for index, info in enumerate(zip_file.infolist()):
                yield ZipEntry(
                    index=index,
                    path=info.filename,
                    crc32=info.CRC,
                    uncompressed_size=info.file_size,
                    is_directory=info.is_dir(),
                )

    def read_entry(self, entry: ZipEntry) -> bytes:
        with zipfile.ZipFile(self._zip_file, mode="r") as zip_file:
            info = self._get_info(zip_file, entry)
            return zip_file.read(info)

    def read_text_entry(
        self,
        entry: ZipEntry,
        encoding: str = "utf-8",
    ) -> str:
        return self.read_entry(entry).decode(encoding)

    def read_entry_stream(
        self,
        entry: ZipEntry,
    ) -> Iterator[bytes]:
        with zipfile.ZipFile(self._zip_file, mode="r") as zip_file:
            info = self._get_info(zip_file, entry)

            with zip_file.open(info, mode="r") as source:
                while chunk := source.read(1024 * 1024):
                    yield chunk

    def extract(
        self,
        entry: ZipEntry,
        destination: Path,
    ) -> None:
        with zipfile.ZipFile(self._zip_file, mode="r") as zip_file:
            info = self._get_info(zip_file, entry)

            target = self._get_extract_path(
                destination,
                info.filename,
            )

            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                return

            target.parent.mkdir(parents=True, exist_ok=True)

            with (
                zip_file.open(info, mode="r") as source,
                target.open("wb") as output,
            ):
                while chunk := source.read(1024 * 1024):
                    output.write(chunk)

    def extract_all(
        self,
        destination: Path,
    ) -> None:
        for entry in self.entries():
            self.extract(entry, destination)

    def _get_info(
        self,
        zip_file: zipfile.ZipFile,
        entry: ZipEntry,
    ) -> zipfile.ZipInfo:
        infos = zip_file.infolist()

        if entry.index < 0 or entry.index >= len(infos):
            raise ValueError(f"Invalid ZIP entry index: {entry.index}")

        info = infos[entry.index]

        if (
            info.filename != entry.path
            or info.CRC != entry.crc32
            or info.file_size != entry.uncompressed_size
            or info.is_dir() != entry.is_directory
        ):
            raise ValueError("ZIP entry no longer matches the archive")

        return info

    @staticmethod
    def _get_extract_path(
        destination: Path,
        entry_path: str,
    ) -> Path:
        if not entry_path:
            raise ValueError("ZIP entry path is empty")

        # ZIP paths are expected to use '/'.
        # Reject '\' as well because it has path semantics on Windows.
        if "\\" in entry_path:
            raise ValueError(
                f"Invalid ZIP entry path: {entry_path!r}",
            )

        path = PurePosixPath(entry_path)

        if path.is_absolute():
            raise ValueError(
                f"Absolute ZIP entry path is not allowed: {entry_path!r}",
            )

        if ".." in path.parts:
            raise ValueError(
                f"Path traversal is not allowed: {entry_path!r}",
            )

        return destination.joinpath(*path.parts)
