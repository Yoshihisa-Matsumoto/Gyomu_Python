from pathlib import Path

from gyomu_config.gyomu.path import resolve_gyomu_config_path
from pytest_mock import MockerFixture


class TestResolveGyomuConfigPath:
    def test_success(self, mocker: MockerFixture) -> None:
        user_config_dir = Path("/mock/user/config/gyomu")
        user_config_path_mock = mocker.patch(
            "gyomu_config.gyomu.path.user_config_path",
            return_value=user_config_dir,
        )

        result = resolve_gyomu_config_path()

        assert result == user_config_dir / "config.json"
        user_config_path_mock.assert_called_once_with(
            appname="gyomu",
            appauthor=False,
            ensure_exists=False,
        )
