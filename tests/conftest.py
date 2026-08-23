from pathlib import Path

import pytest


def find_project_root(path: Path) -> Path:
    for parent in (path, *path.parents):
        if (parent / "pyproject.toml").exists():
            return parent

    raise RuntimeError("Project root could not be found.")


@pytest.fixture
def project_root() -> Path:
    return find_project_root(Path(__file__).resolve().parent)


@pytest.fixture
def project_dot_env(project_root: Path) -> Path:
    return project_root / ".env"
