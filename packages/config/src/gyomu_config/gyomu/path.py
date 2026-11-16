from pathlib import Path

from platformdirs import user_config_path


def resolve_gyomu_config_path() -> Path:
    return (
        user_config_path(
            appname="gyomu",
            appauthor=False,
            ensure_exists=False,
        )
        / "config.json"
    )
