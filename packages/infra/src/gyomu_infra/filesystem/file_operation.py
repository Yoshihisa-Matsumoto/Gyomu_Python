from os import R_OK, W_OK, access
from pathlib import Path
from sys import platform

from gyomu_schema.error.timeout import GyomuTimeoutError
from gyomu_schema.utility.polling import polling
from returns.result import Result


class FileOperation:
    """Provides file operation helper utilities such as access checking and waiting
    for exclusive access.
    """

    def can_access(self, filename: Path, readonly: bool = False) -> bool:
        """Checks whether a file can be accessed for reading or writing.

        Args:
            filename (Path):
            readonly (bool):

        Returns:
            bool: True if the file is accessible according to the specified mode, False
                otherwise.
        """
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
        """Waits until the file becomes exclusively accessible within the given timeout.

        Args:
            filename (Path):
            timeout_seconds (int):

        Returns:
            Result[bool, GyomuTimeoutError]: A Result containing True on success or a
                GyomuTimeoutError on timeout.
        """
        return polling(
            action_name=f"exclusive access: {filename}",
            timeout_seconds=timeout_seconds,
            interval_seconds=1.0,
            action=lambda: self.can_access(filename, readonly=True),
        )
