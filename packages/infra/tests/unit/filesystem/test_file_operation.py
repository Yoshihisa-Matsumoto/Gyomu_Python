from pathlib import Path
from unittest.mock import patch

import pytest
from gyomu_schema.error.timeout import GyomuTimeoutError
from returns.result import Failure, Success

from gyomu_infra.filesystem.file_operation import FileOperation


class TestFileOperationCanAccess:
    def test_returns_false_when_file_does_not_exist(self, tmp_path: Path) -> None:
        operation = FileOperation()

        result = operation.can_access(tmp_path / "not_found.txt")

        assert result is False

    def test_returns_true_for_existing_file_in_readonly_mode(
        self,
        tmp_path: Path,
    ) -> None:
        file_path = tmp_path / "test.txt"
        file_path.write_text("test")

        operation = FileOperation()

        result = operation.can_access((file_path), readonly=True)

        assert result is True

    def test_returns_true_for_existing_file_in_write_mode(
        self,
        tmp_path: Path,
    ) -> None:
        file_path = tmp_path / "test.txt"
        file_path.write_text("test")

        operation = FileOperation()

        result = operation.can_access((file_path), readonly=False)

        assert result is True

    @pytest.mark.parametrize("extension", ["xls", "xlsm", "xlsx", "zip"])
    def test_returns_false_for_empty_special_file(
        self,
        tmp_path: Path,
        extension: str,
    ) -> None:
        file_path = tmp_path / f"empty.{extension}"
        file_path.touch()

        operation = FileOperation()

        result = operation.can_access(file_path)

        assert result is False

    def test_special_extension_is_case_insensitive(
        self,
        tmp_path: Path,
    ) -> None:
        file_path = tmp_path / "empty.ZIP"
        file_path.touch()

        operation = FileOperation()

        result = operation.can_access(file_path)

        assert result is False

    @pytest.mark.parametrize("extension", ["xls", "xlsm", "xlsx", "zip"])
    def test_returns_true_for_non_empty_special_file(
        self,
        tmp_path: Path,
        extension: str,
    ) -> None:
        file_path = tmp_path / f"test.{extension}"
        file_path.write_bytes(b"data")

        operation = FileOperation()

        result = operation.can_access(file_path)

        assert result is True


class TestFileOperationWaitTillExclusiveAccess:
    def test_returns_polling_result(
        self,
        tmp_path: Path,
    ) -> None:
        file_operation = FileOperation()
        filename = tmp_path / "test.txt"

        with patch(
            "gyomu_infra.filesystem.file_operation.polling",
            return_value=Success(True),
        ) as polling_mock:
            result = file_operation.wait_till_exclusive_access(
                filename,
                timeout_seconds=10,
            )

        assert result == Success(True)
        polling_mock.assert_called_once()

    def test_passes_exclusive_access_action_to_polling(
        self,
        tmp_path: Path,
    ) -> None:
        file_operation = FileOperation()
        filename = tmp_path / "test.txt"

        with patch(
            "gyomu_infra.filesystem.file_operation.polling",
            return_value=Success(True),
        ) as polling_mock:
            file_operation.wait_till_exclusive_access(
                filename,
                timeout_seconds=10,
            )

        polling_mock.assert_called_once()

        call_kwargs = polling_mock.call_args.kwargs

        assert call_kwargs["action_name"] == f"exclusive access: {filename}"
        assert call_kwargs["timeout_seconds"] == 10
        assert call_kwargs["interval_seconds"] == 1.0

        with patch.object(
            file_operation,
            "can_access",
            return_value=True,
        ) as can_access_mock:
            result = call_kwargs["action"]()

        assert result is True
        can_access_mock.assert_called_once_with(
            filename,
            readonly=True,
        )

    def test_propagates_timeout_failure(
        self,
        tmp_path: Path,
    ) -> None:
        file_operation = FileOperation()
        filename = tmp_path / "test.txt"

        error = GyomuTimeoutError(
            message=f"Timeout on polling: exclusive access: {filename}",
            action=f"exclusive access: {filename}",
            timeout_seconds=10,
            interval_seconds=1.0,
        )

        expected = Failure(error)

        with patch(
            "gyomu_infra.filesystem.file_operation.polling",
            return_value=expected,
        ) as polling_mock:
            result = file_operation.wait_till_exclusive_access(
                filename,
                timeout_seconds=10,
            )

        assert result is expected
        polling_mock.assert_called_once()
