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
        """Write data bytes to the writer.

        Writes data chunks to the internal buffer.

        Args:
            data (bytes): The data bytes to write.

        Returns:
            int: The number of bytes written.
        """
        self._chunks.append(data)
        return len(data)

    def flush(self) -> None:
        pass

    def close(self) -> None:
        pass

    def pop_chunks(self) -> Iterator[bytes]:
        """Pop and yield accumulated data chunks.

        Yields and removes accumulated chunks from the buffer.

        Returns:
            Iterator[bytes]: An iterator over accumulated byte chunks.
        """
        while self._chunks:
            yield self._chunks.popleft()


@dataclass(frozen=True)
class ZipEntry:
    """Defines metadata for an entry in a ZIP archive.

    A data class representing metadata for an entry within a ZIP archive.
    """

    index: int
    """Entry index.

    The zero-based index of the entry in the archive.
    """
    path: str
    """Entry path.

    The file or directory path within the archive.
    """
    crc32: int
    """Entry CRC-32 checksum.

    The CRC-32 checksum of the uncompressed data.
    """
    uncompressed_size: int
    """Uncompressed data size.

    The size of the uncompressed data in bytes.
    """
    is_directory: bool
    """Directory flag.

    Indicates whether the entry represents a directory.
    """


class Zip:
    """Provides methods for managing and extracting ZIP archives.

    Provides utility methods for creating, inspecting, reading, and extracting ZIP
    archives.
    """

    def __init__(self, zip_file: Path) -> None:
        self._zip_file = zip_file

    @staticmethod
    def create(
        transfer_information_list: Sequence[FileTransportInfo],
    ) -> Iterator[bytes]:
        """Create a streaming ZIP archive.

        Creates a ZIP archive stream from the given file transport information list.

        Args:
            transfer_information_list (Sequence[FileTransportInfo]): Sequence of file
                transport information to archive.

        Returns:
            Iterator[bytes]: An iterator yielding compressed ZIP file chunks.
        """
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
        """Find files for transport information.

        Finds files matching the transport information specification.

        Args:
            transfer_information (FileTransportInfo): The file transport information
                specifying source and filters.

        Returns:
            list[FileInfo]: A list of matching FileInfo objects.
        """
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
        """Get the archive entry path for a file.

        Determines the archive entry path for a given file.

        Args:
            transfer_information (FileTransportInfo): The file transport information.
            file_info (FileInfo): The file info object.

        Returns:
            str: The relative entry path within the archive.
        """
        source = PurePosixPath(transfer_information.source_fullname)

        if transfer_information.is_source_directory:
            base_path = Path(transfer_information.source_fullname_with_basepath)

            relative_path = file_info.full_path.relative_to(base_path)

            return (source / PurePosixPath(relative_path.as_posix())).as_posix()

        return source.as_posix()

    def entries(self) -> Iterator[ZipEntry]:
        """Iterate over ZIP entries.

        Iterates over all entries contained in the ZIP archive.

        Returns:
            Iterator[ZipEntry]: An iterator over ZIP entries.
        """
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
        """Read the content of a ZIP entry.

        Reads the binary content of a specific ZIP entry.

        Args:
            entry (ZipEntry): The ZIP entry to read.

        Returns:
            bytes: The binary content of the entry.

        Raises:
            ValueError: If the entry index is invalid or no longer matches the archive.
        """
        with zipfile.ZipFile(self._zip_file, mode="r") as zip_file:
            info = self._get_info(zip_file, entry)
            return zip_file.read(info)

    def read_text_entry(
        self,
        entry: ZipEntry,
        encoding: str = "utf-8",
    ) -> str:
        """Read the text content of a ZIP entry.

        Reads the text content of a specific ZIP entry using the specified encoding.

        Args:
            entry (ZipEntry): The ZIP entry to read.
            encoding (str): The text encoding to use (default utf-8).

        Returns:
            str: The decoded text content.
        """
        return self.read_entry(entry).decode(encoding)

    def read_entry_stream(
        self,
        entry: ZipEntry,
    ) -> Iterator[bytes]:
        """Stream the content of a ZIP entry.

        Streams the content of a specific ZIP entry in chunks.

        Args:
            entry (ZipEntry): The ZIP entry to stream.

        Returns:
            Iterator[bytes]: An iterator yielding chunks of entry data.
        """
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
        """Extract a ZIP entry to a destination.

        Extracts a specific ZIP entry to the given destination path.

        Args:
            entry (ZipEntry): The ZIP entry to extract.
            destination (Path): The destination directory path.
        """
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
        """Extract all entries from the archive.

        Extracts all entries from the ZIP archive to the given destination path.

        Args:
            destination (Path): The destination directory path.
        """
        for entry in self.entries():
            self.extract(entry, destination)

    def _get_info(
        self,
        zip_file: zipfile.ZipFile,
        entry: ZipEntry,
    ) -> zipfile.ZipInfo:
        """Get and validate ZipInfo for an entry.

        Retrieves the ZipInfo object for a given entry, validating its index and
        metadata.

        Args:
            zip_file (zipfile.ZipFile): The zipfile object.
            entry (ZipEntry): The ZIP entry to look up.

        Returns:
            zipfile.ZipInfo: The corresponding ZipInfo object.

        Raises:
            ValueError: If the entry index is out of bounds or entry metadata no longer
                matches.
        """
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
        """Validate and compute the extraction path.

        Safely constructs and validates the extraction path for a ZIP entry.

        Args:
            destination (Path): The destination directory path.
            entry_path (str): The entry path from the archive.

        Returns:
            Path: The validated extraction Path.

        Raises:
            ValueError: If the entry path is empty, absolute, or contains path traversal
                sequences.
        """
        if not entry_path:
            raise ValueError("ZIP entry path is empty")

        # ZIP paths are expected to use '/'.
        # Reject '\' as well because it has path semantics on Windows.
        if "\\" in entry_path:
            entry_path = entry_path.replace("\\", "/")

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
