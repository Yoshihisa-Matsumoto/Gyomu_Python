from pathlib import Path

import pytest


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def project_dot_env(project_root: Path) -> Path:
    return project_root / ".env"


print("ROOT CONFTST LOADED")
