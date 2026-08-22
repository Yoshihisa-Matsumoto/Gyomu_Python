from os import R_OK, W_OK, access
from pathlib import Path
from sys import platform

from gyomu_schema.error.timeout import GyomuTimeoutError
from gyomu_schema.utility.polling import polling
from returns.result import Result


class FileOperation:
    def can_access(self, filename: Path, readonly: bool = False) -> bool:
        if not filename.exists():
            return False

        special_extensions = {".xls", ".xlsm", ".xlsx", ".zip"}

        if (
            filename.suffix.lower() in special_extensions
            and filename.stat().st_size == 0
        ):
            return False

        if readonly:
            return access(filename, R_OK)

        if platform == "win32":
            try:
                filename.rename(filename)
                return True
            except OSError:
                return False

        return access(filename, W_OK)

    def wait_till_exclusive_access(
        self,
        filename: Path,
        timeout_seconds: int,
    ) -> Result[bool, GyomuTimeoutError]:
        return polling(
            action_name=f"exclusive access: {filename}",
            timeout_seconds=timeout_seconds,
            interval_seconds=1.0,
            action=lambda: self.can_access(filename, readonly=True),
        )
