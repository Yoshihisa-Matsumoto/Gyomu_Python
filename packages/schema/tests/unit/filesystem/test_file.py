from collections import namedtuple
from datetime import datetime

import pytest
from gyomu_schema.filesystem.file import (
    FileCompareType,
    FileFilterInfo,
    FileFilterType,
    FileTransportInfo,
)

TransportResult = namedtuple(
    "TransportResult",
    [
        "input_base",
        "input_sdir",
        "input_sname",
        "input_ddir",
        "input_dname",
        "source_full_base",
        "source_full",
        "source_dir",
        "source_name",
        "destination_full",
        "destination_dir",
        "destination_name",
    ],
)


class TestFileTransportInfo:
    @pytest.mark.parametrize(
        "input_data",
        [
            TransportResult(
                input_base="base",
                input_sdir="SDir",
                input_sname="Sname",
                input_ddir="Ddir",
                input_dname="Dname",
                source_full_base="base/SDir/Sname",
                source_full="SDir/Sname",
                source_dir="SDir",
                source_name="Sname",
                destination_full="Ddir/Dname",
                destination_dir="Ddir",
                destination_name="Dname",
            ),
            TransportResult(
                input_base="base",
                input_sdir="SDir",
                input_sname="Sname",
                input_ddir="Ddir",
                input_dname="",
                source_full_base="base/SDir/Sname",
                source_full="SDir/Sname",
                source_dir="SDir",
                source_name="Sname",
                destination_full="Ddir/Sname",
                destination_dir="Ddir",
                destination_name="Sname",
            ),
            TransportResult(
                input_base="base",
                input_sdir="SDir",
                input_sname="Sname",
                input_ddir="",
                input_dname="Dname",
                source_full_base="base/SDir/Sname",
                source_full="SDir/Sname",
                source_dir="SDir",
                source_name="Sname",
                destination_full="SDir/Dname",
                destination_dir="SDir",
                destination_name="Dname",
            ),
            TransportResult(
                input_base="base",
                input_sdir="SDir",
                input_sname="Sname",
                input_ddir="",
                input_dname="",
                source_full_base="base/SDir/Sname",
                source_full="SDir/Sname",
                source_dir="SDir",
                source_name="Sname",
                destination_full="SDir/Sname",
                destination_dir="SDir",
                destination_name="Sname",
            ),
            TransportResult(
                input_base="base",
                input_sdir="SDir",
                input_sname="",
                input_ddir="Ddir",
                input_dname="",
                source_full_base="base/SDir",
                source_full="SDir",
                source_dir="SDir",
                source_name="",
                destination_full="Ddir",
                destination_dir="Ddir",
                destination_name="",
            ),
            TransportResult(
                input_base="base",
                input_sdir="SDir",
                input_sname="",
                input_ddir="",
                input_dname="",
                source_full_base="base/SDir",
                source_full="SDir",
                source_dir="SDir",
                source_name="",
                destination_full="SDir",
                destination_dir="SDir",
                destination_name="",
            ),
            TransportResult(
                input_base="base",
                input_sdir="",
                input_sname="",
                input_ddir="",
                input_dname="",
                source_full_base="base",
                source_full="",
                source_dir="",
                source_name="",
                destination_full="",
                destination_dir="",
                destination_name="",
            ),
            TransportResult(
                input_base="base",
                input_sdir="",
                input_sname="",
                input_ddir="Ddir",
                input_dname="",
                source_full_base="base",
                source_full="",
                source_dir="",
                source_name="",
                destination_full="Ddir",
                destination_dir="Ddir",
                destination_name="",
            ),
            TransportResult(
                input_base="base",
                input_sdir="",
                input_sname="Sname",
                input_ddir="Ddir",
                input_dname="Dname",
                source_full_base="base/Sname",
                source_full="Sname",
                source_dir="",
                source_name="Sname",
                destination_full="Ddir/Dname",
                destination_dir="Ddir",
                destination_name="Dname",
            ),
            TransportResult(
                input_base="base",
                input_sdir="",
                input_sname="Sname",
                input_ddir="Ddir",
                input_dname="",
                source_full_base="base/Sname",
                source_full="Sname",
                source_dir="",
                source_name="Sname",
                destination_full="Ddir/Sname",
                destination_dir="Ddir",
                destination_name="Sname",
            ),
            TransportResult(
                input_base="base",
                input_sdir="",
                input_sname="Sname",
                input_ddir="",
                input_dname="Dname",
                source_full_base="base/Sname",
                source_full="Sname",
                source_dir="",
                source_name="Sname",
                destination_full="Dname",
                destination_dir="",
                destination_name="Dname",
            ),
            TransportResult(
                input_base="base",
                input_sdir="",
                input_sname="Sname",
                input_ddir="",
                input_dname="",
                source_full_base="base/Sname",
                source_full="Sname",
                source_dir="",
                source_name="Sname",
                destination_full="Sname",
                destination_dir="",
                destination_name="Sname",
            ),
            TransportResult(
                input_base="",
                input_sdir="SDir",
                input_sname="Sname",
                input_ddir="Ddir",
                input_dname="Dname",
                source_full_base="SDir/Sname",
                source_full="SDir/Sname",
                source_dir="SDir",
                source_name="Sname",
                destination_full="Ddir/Dname",
                destination_dir="Ddir",
                destination_name="Dname",
            ),
            TransportResult(
                input_base="",
                input_sdir="SDir",
                input_sname="Sname",
                input_ddir="Ddir",
                input_dname="",
                source_full_base="SDir/Sname",
                source_full="SDir/Sname",
                source_dir="SDir",
                source_name="Sname",
                destination_full="Ddir/Sname",
                destination_dir="Ddir",
                destination_name="Sname",
            ),
            TransportResult(
                input_base="",
                input_sdir="SDir",
                input_sname="Sname",
                input_ddir="",
                input_dname="Dname",
                source_full_base="SDir/Sname",
                source_full="SDir/Sname",
                source_dir="SDir",
                source_name="Sname",
                destination_full="SDir/Dname",
                destination_dir="SDir",
                destination_name="Dname",
            ),
            TransportResult(
                input_base="",
                input_sdir="SDir",
                input_sname="Sname",
                input_ddir="",
                input_dname="",
                source_full_base="SDir/Sname",
                source_full="SDir/Sname",
                source_dir="SDir",
                source_name="Sname",
                destination_full="SDir/Sname",
                destination_dir="SDir",
                destination_name="Sname",
            ),
            TransportResult(
                input_base="",
                input_sdir="SDir",
                input_sname="",
                input_ddir="Ddir",
                input_dname="",
                source_full_base="SDir",
                source_full="SDir",
                source_dir="SDir",
                source_name="",
                destination_full="Ddir",
                destination_dir="Ddir",
                destination_name="",
            ),
            TransportResult(
                input_base="",
                input_sdir="SDir",
                input_sname="",
                input_ddir="",
                input_dname="",
                source_full_base="SDir",
                source_full="SDir",
                source_dir="SDir",
                source_name="",
                destination_full="SDir",
                destination_dir="SDir",
                destination_name="",
            ),
            TransportResult(
                input_base="",
                input_sdir="",
                input_sname="Sname",
                input_ddir="Ddir",
                input_dname="Dname",
                source_full_base="Sname",
                source_full="Sname",
                source_dir="",
                source_name="Sname",
                destination_full="Ddir/Dname",
                destination_dir="Ddir",
                destination_name="Dname",
            ),
            TransportResult(
                input_base="",
                input_sdir="",
                input_sname="Sname",
                input_ddir="Ddir",
                input_dname="",
                source_full_base="Sname",
                source_full="Sname",
                source_dir="",
                source_name="Sname",
                destination_full="Ddir/Sname",
                destination_dir="Ddir",
                destination_name="Sname",
            ),
            TransportResult(
                input_base="",
                input_sdir="",
                input_sname="Sname",
                input_ddir="",
                input_dname="Dname",
                source_full_base="Sname",
                source_full="Sname",
                source_dir="",
                source_name="Sname",
                destination_full="Dname",
                destination_dir="",
                destination_name="Dname",
            ),
            TransportResult(
                input_base="",
                input_sdir="",
                input_sname="Sname",
                input_ddir="",
                input_dname="",
                source_full_base="Sname",
                source_full="Sname",
                source_dir="",
                source_name="Sname",
                destination_full="Sname",
                destination_dir="",
                destination_name="Sname",
            ),
        ],
    )
    def test_valid_transport_information(self, input_data):
        info: FileTransportInfo = TestFileTransportInfo.create_transport_information(
            input_data
        )
        TestFileTransportInfo.compare(input_data, info)

    @pytest.mark.parametrize(
        "input_data",
        [
            TransportResult(
                input_base="base",
                input_sdir="SDir",
                input_sname="",
                input_ddir="Ddir",
                input_dname="Dname",
                source_full_base="",
                source_full="",
                source_dir="",
                source_name="",
                destination_full="",
                destination_dir="",
                destination_name="",
            ),
            TransportResult(
                input_base="base",
                input_sdir="SDir",
                input_sname="",
                input_ddir="",
                input_dname="Dname",
                source_full_base="",
                source_full="",
                source_dir="",
                source_name="",
                destination_full="",
                destination_dir="",
                destination_name="",
            ),
            TransportResult(
                input_base="base",
                input_sdir="",
                input_sname="",
                input_ddir="Ddir",
                input_dname="Dname",
                source_full_base="",
                source_full="",
                source_dir="",
                source_name="",
                destination_full="",
                destination_dir="",
                destination_name="",
            ),
            TransportResult(
                input_base="base",
                input_sdir="",
                input_sname="",
                input_ddir="",
                input_dname="Dname",
                source_full_base="",
                source_full="",
                source_dir="",
                source_name="",
                destination_full="",
                destination_dir="",
                destination_name="",
            ),
            TransportResult(
                input_base="",
                input_sdir="SDir",
                input_sname="",
                input_ddir="Ddir",
                input_dname="Dname",
                source_full_base="",
                source_full="",
                source_dir="",
                source_name="",
                destination_full="",
                destination_dir="",
                destination_name="",
            ),
            TransportResult(
                input_base="",
                input_sdir="SDir",
                input_sname="",
                input_ddir="",
                input_dname="Dname",
                source_full_base="",
                source_full="",
                source_dir="",
                source_name="",
                destination_full="",
                destination_dir="",
                destination_name="",
            ),
            TransportResult(
                input_base="",
                input_sdir="",
                input_sname="",
                input_ddir="Ddir",
                input_dname="Dname",
                source_full_base="",
                source_full="",
                source_dir="",
                source_name="",
                destination_full="",
                destination_dir="",
                destination_name="",
            ),
            TransportResult(
                input_base="",
                input_sdir="",
                input_sname="",
                input_ddir="Ddir",
                input_dname="",
                source_full_base="",
                source_full="",
                source_dir="",
                source_name="",
                destination_full="",
                destination_dir="",
                destination_name="",
            ),
            TransportResult(
                input_base="",
                input_sdir="",
                input_sname="",
                input_ddir="",
                input_dname="Dname",
                source_full_base="",
                source_full="",
                source_dir="",
                source_name="",
                destination_full="",
                destination_dir="",
                destination_name="",
            ),
        ],
    )
    def test_invalid_transport_information(self, input_data: TransportResult):
        with pytest.raises(ValueError):
            TestFileTransportInfo.create_transport_information(input_data)

    @staticmethod
    def compare(expected: TransportResult, source: FileTransportInfo):
        assert expected.source_full_base == source.source_fullname_with_basepath
        assert expected.source_full == source.source_fullname
        assert expected.source_dir == source.source_path
        assert expected.source_name == source.source_filename
        assert expected.destination_full == source.destination_fullname
        assert expected.destination_dir == source.destination_path
        assert expected.destination_name == source.destination_filename

    @staticmethod
    def create_transport_information(result: TransportResult) -> FileTransportInfo:
        return FileTransportInfo(
            base_path=result.input_base,
            source_filename=result.input_sname,
            source_folder_name=result.input_sdir,
            destination_filename=result.input_dname,
            destination_foldername=result.input_ddir,
        )


class TestFileFilterInfo:
    def test_creates_file_name_filter(self) -> None:
        result = FileFilterInfo(
            kind=FileFilterType.FILE_NAME,
            operator=FileCompareType.EQUAL,
            value="test.csv",
        )

        assert result.kind == FileFilterType.FILE_NAME
        assert result.operator == FileCompareType.EQUAL
        assert result.name_filter == "test.csv"

    def test_converts_file_name_filter_to_string(self) -> None:
        result = FileFilterInfo(
            kind=FileFilterType.FILE_NAME,
            operator=FileCompareType.EQUAL,
            value=123,
        )

        assert result.name_filter == "123"

    def test_creates_filter_with_datetime(self) -> None:
        target_date = datetime(2026, 8, 22)

        result = FileFilterInfo(
            kind=FileFilterType.CREATE_TIME_UTC,
            operator=FileCompareType.LARGER,
            value=target_date,
        )

        assert result.kind == FileFilterType.CREATE_TIME_UTC
        assert result.operator == FileCompareType.LARGER
        assert result.target_date == target_date

    def test_parses_string_to_datetime(self) -> None:
        result = FileFilterInfo(
            kind=FileFilterType.CREATE_TIME_UTC,
            operator=FileCompareType.LARGER,
            value="20260822",
        )

        assert result.target_date == datetime(2026, 8, 22)

    def test_parses_string_to_datetime_for_last_access_time(self) -> None:
        result = FileFilterInfo(
            kind=FileFilterType.LAST_ACCESS_TIME_UTC,
            operator=FileCompareType.LESS,
            value="20260101",
        )

        assert result.kind == FileFilterType.LAST_ACCESS_TIME_UTC
        assert result.operator == FileCompareType.LESS
        assert result.target_date == datetime(2026, 1, 1)

    def test_parses_string_to_datetime_for_last_write_time(self) -> None:
        result = FileFilterInfo(
            kind=FileFilterType.LAST_WRITE_TIME_UTC,
            operator=FileCompareType.LESS_OR_EQUAL,
            value="20261231",
        )

        assert result.kind == FileFilterType.LAST_WRITE_TIME_UTC
        assert result.operator == FileCompareType.LESS_OR_EQUAL
        assert result.target_date == datetime(2026, 12, 31)

    def test_raises_value_error_for_invalid_date_string(self) -> None:
        with pytest.raises(ValueError, match="Date Parameter is invalid"):
            FileFilterInfo(
                kind=FileFilterType.CREATE_TIME_UTC,
                operator=FileCompareType.EQUAL,
                value="20260230",
            )

    def test_raises_value_error_for_unsupported_value_type(self) -> None:
        with pytest.raises(ValueError, match="Date Parameter is invalid"):
            FileFilterInfo(
                kind=FileFilterType.CREATE_TIME_UTC,
                operator=FileCompareType.EQUAL,
                value=123,
            )

    def test_raises_value_error_for_invalid_date_format(self) -> None:
        with pytest.raises(ValueError, match="Date Parameter is invalid"):
            FileFilterInfo(
                kind=FileFilterType.CREATE_TIME_UTC,
                operator=FileCompareType.EQUAL,
                value="2026-08-22",
            )
