import io
import zipfile
from pathlib import Path

import pytest
from gyomu_schema.filesystem.file import (
    FileCompareType,
    FileFilterInfo,
    FileFilterType,
    FileTransportInfo,
)

from gyomu_infra.archive.zip import Zip, ZipEntry


def _create_zip(
    transfer_information_list: list[FileTransportInfo],
) -> zipfile.ZipFile:
    data = b"".join(Zip.create(transfer_information_list))

    return zipfile.ZipFile(io.BytesIO(data), "r")


class TestZipCreate:
    def test_create_single_file(
        self,
        tmp_path: Path,
    ) -> None:
        source = tmp_path / "test.txt"
        source.write_text("hello", encoding="utf-8")

        transfer = FileTransportInfo(
            base_path=str(tmp_path),
            source_filename="test.txt",
        )

        with _create_zip([transfer]) as archive:
            assert archive.namelist() == ["test.txt"]
            assert archive.read("test.txt") == b"hello"

    def test_create_directory(
        self,
        tmp_path: Path,
    ) -> None:
        source = tmp_path / "folder"
        source.mkdir()

        (source / "a.txt").write_text("a", encoding="utf-8")
        (source / "b.txt").write_text("b", encoding="utf-8")

        transfer = FileTransportInfo(
            base_path=str(tmp_path),
            source_folder_name="folder",
        )

        with _create_zip([transfer]) as archive:
            assert sorted(archive.namelist()) == [
                "folder/a.txt",
                "folder/b.txt",
            ]

            assert archive.read("folder/a.txt") == b"a"
            assert archive.read("folder/b.txt") == b"b"

    def test_create_with_filter(
        self,
        tmp_path: Path,
    ) -> None:
        source = tmp_path / "folder"
        source.mkdir()

        (source / "a.txt").write_text("a", encoding="utf-8")
        (source / "b.csv").write_text("b", encoding="utf-8")

        filter_condition = FileFilterInfo(
            FileFilterType.FILE_NAME,
            FileCompareType.EQUAL,
            r".*\.txt",
        )

        transfer = FileTransportInfo(
            base_path=str(tmp_path),
            source_folder_name="folder",
            filter_conditions=[filter_condition],
        )

        with _create_zip([transfer]) as archive:
            assert archive.namelist() == ["folder/a.txt"]

    def test_create_without_filter_uses_all_files(
        self,
        tmp_path: Path,
    ) -> None:
        source = tmp_path / "folder"
        source.mkdir()

        (source / "a.txt").write_text("a", encoding="utf-8")
        (source / "b.csv").write_text("b", encoding="utf-8")

        transfer = FileTransportInfo(
            base_path=str(tmp_path),
            source_folder_name="folder",
        )

        with _create_zip([transfer]) as archive:
            assert sorted(archive.namelist()) == [
                "folder/a.txt",
                "folder/b.csv",
            ]

    def test_create_nested_directory(
        self,
        tmp_path: Path,
    ) -> None:
        source = tmp_path / "folder"
        nested = source / "nested"
        nested.mkdir(parents=True)

        (source / "a.txt").write_text("a", encoding="utf-8")
        (nested / "b.txt").write_text("b", encoding="utf-8")

        transfer = FileTransportInfo(
            base_path=str(tmp_path),
            source_folder_name="folder",
        )

        with _create_zip([transfer]) as archive:
            assert sorted(archive.namelist()) == [
                "folder/a.txt",
                "folder/nested/b.txt",
            ]

    def test_create_japanese_filename(
        self,
        tmp_path: Path,
    ) -> None:
        source = tmp_path / "フォルダ"
        source.mkdir()

        filename = source / "テスト.txt"
        filename.write_text("日本語", encoding="utf-8")

        transfer = FileTransportInfo(
            base_path=str(tmp_path),
            source_folder_name="フォルダ",
        )

        with _create_zip([transfer]) as archive:
            assert archive.namelist() == ["フォルダ/テスト.txt"]
            assert archive.read("フォルダ/テスト.txt") == "日本語".encode()

    def test_create_multiple_transfer_information(
        self,
        tmp_path: Path,
    ) -> None:
        folder1 = tmp_path / "folder1"
        folder2 = tmp_path / "folder2"

        folder1.mkdir()
        folder2.mkdir()

        (folder1 / "a.txt").write_text("a", encoding="utf-8")
        (folder2 / "b.txt").write_text("b", encoding="utf-8")

        transfers = [
            FileTransportInfo(
                base_path=str(tmp_path),
                source_folder_name="folder1",
            ),
            FileTransportInfo(
                base_path=str(tmp_path),
                source_folder_name="folder2",
            ),
        ]

        with _create_zip(transfers) as archive:
            assert sorted(archive.namelist()) == [
                "folder1/a.txt",
                "folder2/b.txt",
            ]


class TestZipExtract:
    @staticmethod
    def _create_zip(
        path: Path,
        entries: dict[str, bytes],
    ) -> None:
        with zipfile.ZipFile(
            path,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
        ) as zip_file:
            for entry_path, data in entries.items():
                zip_file.writestr(entry_path, data)

    def test_entries(self, tmp_path: Path) -> None:
        zip_path = tmp_path / "test.zip"

        self._create_zip(
            zip_path,
            {
                "file1.txt": b"hello",
                "folder/file2.txt": b"world",
            },
        )

        zip_file = Zip(zip_path)

        entries = list(zip_file.entries())

        assert len(entries) == 2

        assert entries[0].index == 0
        assert entries[0].path == "file1.txt"
        assert entries[0].uncompressed_size == 5
        assert not entries[0].is_directory

        assert entries[1].index == 1
        assert entries[1].path == "folder/file2.txt"
        assert entries[1].uncompressed_size == 5
        assert not entries[1].is_directory

    def test_entries_directory(self, tmp_path: Path) -> None:
        zip_path = tmp_path / "test.zip"

        with zipfile.ZipFile(
            zip_path,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
        ) as zip_file:
            zip_file.writestr("folder/", b"")
            zip_file.writestr("folder/file.txt", b"hello")

        zip = Zip(zip_path)

        entries = list(zip.entries())

        assert len(entries) == 2

        assert entries[0].path == "folder/"
        assert entries[0].is_directory
        assert entries[0].uncompressed_size == 0

        assert entries[1].path == "folder/file.txt"
        assert not entries[1].is_directory

    def test_read_entry(self, tmp_path: Path) -> None:
        zip_path = tmp_path / "test.zip"

        self._create_zip(
            zip_path,
            {
                "test.txt": b"hello world",
            },
        )

        zip = Zip(zip_path)
        entry = next(zip.entries())

        result = zip.read_entry(entry)

        assert result == b"hello world"

    def test_read_text_entry(self, tmp_path: Path) -> None:
        zip_path = tmp_path / "test.zip"

        text = "こんにちは、世界！"

        self._create_zip(
            zip_path,
            {
                "test.txt": text.encode("utf-8"),
            },
        )

        zip = Zip(zip_path)
        entry = next(zip.entries())

        result = zip.read_text_entry(entry)

        assert result == text

    def test_read_text_entry_with_encoding(
        self,
        tmp_path: Path,
    ) -> None:
        zip_path = tmp_path / "test.zip"

        text = "こんにちは、世界！"

        self._create_zip(
            zip_path,
            {
                "test.txt": text.encode("utf-16"),
            },
        )

        zip = Zip(zip_path)
        entry = next(zip.entries())

        result = zip.read_text_entry(
            entry,
            encoding="utf-16",
        )

        assert result == text

    def test_read_entry_stream(
        self,
        tmp_path: Path,
    ) -> None:
        zip_path = tmp_path / "test.zip"

        data = bytes(range(256)) * 100_000

        self._create_zip(
            zip_path,
            {
                "large.bin": data,
            },
        )

        zip = Zip(zip_path)
        entry = next(zip.entries())

        chunks = list(zip.read_entry_stream(entry))

        assert len(chunks) > 1
        assert b"".join(chunks) == data

    def test_extract(self, tmp_path: Path) -> None:
        zip_path = tmp_path / "test.zip"
        destination = tmp_path / "destination"

        self._create_zip(
            zip_path,
            {
                "folder/file.txt": b"hello world",
            },
        )

        zip = Zip(zip_path)
        entry = next(zip.entries())

        zip.extract(entry, destination)

        extracted = destination / "folder" / "file.txt"

        assert extracted.is_file()
        assert extracted.read_bytes() == b"hello world"

    def test_extract_directory(
        self,
        tmp_path: Path,
    ) -> None:
        zip_path = tmp_path / "test.zip"
        destination = tmp_path / "destination"

        with zipfile.ZipFile(
            zip_path,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
        ) as zip_file:
            zip_file.writestr("folder/", b"")

        zip = Zip(zip_path)
        entry = next(zip.entries())

        zip.extract(entry, destination)

        extracted = destination / "folder"

        assert extracted.is_dir()

    def test_extract_all(self, tmp_path: Path) -> None:
        zip_path = tmp_path / "test.zip"
        destination = tmp_path / "destination"

        self._create_zip(
            zip_path,
            {
                "file1.txt": b"hello",
                "folder/file2.txt": b"world",
                "folder/sub/file3.txt": b"gyomu",
            },
        )

        zip = Zip(zip_path)

        zip.extract_all(destination)

        assert (destination / "file1.txt").read_bytes() == b"hello"

        assert (destination / "folder" / "file2.txt").read_bytes() == b"world"

        assert (destination / "folder" / "sub" / "file3.txt").read_bytes() == b"gyomu"

    def test_extract_rejects_parent_path(
        self,
        tmp_path: Path,
    ) -> None:
        zip_path = tmp_path / "test.zip"
        destination = tmp_path / "destination"

        self._create_zip(
            zip_path,
            {
                "../evil.txt": b"evil",
            },
        )

        zip = Zip(zip_path)
        entry = next(zip.entries())

        with pytest.raises(
            ValueError,
            match="Path traversal is not allowed",
        ):
            zip.extract(entry, destination)

        assert not (tmp_path / "evil.txt").exists()

    def test_extract_rejects_absolute_path(
        self,
        tmp_path: Path,
    ) -> None:
        zip_path = tmp_path / "test.zip"
        destination = tmp_path / "destination"

        self._create_zip(
            zip_path,
            {
                "/evil.txt": b"evil",
            },
        )

        zip = Zip(zip_path)
        entry = next(zip.entries())

        with pytest.raises(
            ValueError,
            match="Absolute ZIP entry path is not allowed",
        ):
            zip.extract(entry, destination)

    def test_extract_rejects_windows_separator(
        self,
        tmp_path: Path,
    ) -> None:
        zip_path = tmp_path / "test.zip"
        destination = tmp_path / "destination"

        self._create_zip(
            zip_path,
            {
                r"..\evil.txt": b"evil",
            },
        )

        zip = Zip(zip_path)
        entry = next(zip.entries())

        with pytest.raises(
            ValueError,
            match="Path traversal is not allowed",
        ):
            zip.extract(entry, destination)

        assert not (tmp_path / "evil.txt").exists()

    def test_invalid_entry_is_rejected(
        self,
        tmp_path: Path,
    ) -> None:
        zip_path = tmp_path / "test.zip"

        self._create_zip(
            zip_path,
            {
                "test.txt": b"hello",
            },
        )

        zip = Zip(zip_path)

        entry = ZipEntry(
            index=0,
            path="different.txt",
            crc32=0,
            uncompressed_size=0,
            is_directory=False,
        )

        with pytest.raises(
            ValueError,
            match="ZIP entry no longer matches the archive",
        ):
            zip.read_entry(entry)

    # def test_entries_contains_crc32(self, tmp_path: Path) -> None:
    #     zip_path = tmp_path / "test.zip"

    #     data = b"hello world"

    #     self._create_zip(
    #         zip_path,
    #         {
    #             "test.txt": data,
    #         },
    #     )

    #     zip = Zip(zip_path)
    #     entry = next(zip.entries())

    #     expected = zipfile.crc32(data)

    #     assert entry.crc32 == expected
