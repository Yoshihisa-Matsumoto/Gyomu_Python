from pathlib import Path

import pytest
from gyomu_python_analysis.project.context import PyProjectConfig
from gyomu_schema.schemas.python.types import WorkspaceRelativePath
from pydantic import ValidationError


class TestPyProjectConfig:
    @pytest.fixture
    def config(self) -> PyProjectConfig:
        return PyProjectConfig(
            path=WorkspaceRelativePath(Path("packages/example")),
            name="example",
            version="1.0.0",
            description=None,
            formatter_line_length=88,
            _toml_data={
                "tool": {
                    "gyomu": {
                        "exclude": [
                            "src/generated",
                        ],
                        "enabled": True,
                    },
                },
            },
        )

    def test_get_attribute(self, config: PyProjectConfig) -> None:
        assert config.get_attribute(
            "tool.gyomu.exclude",
            list[str],
        ) == ["src/generated"]

        assert (
            config.get_attribute(
                "tool.gyomu.enabled",
                bool,
            )
            is True
        )

    def test_get_attribute_not_found(
        self,
        config: PyProjectConfig,
    ) -> None:
        assert (
            config.get_attribute(
                "tool.gyomu.exclude",
                list[str],
            )
            is not None
        )

        assert (
            config.get_attribute(
                "tool.gyomu.not_found",
                str,
            )
            is None
        )

    def test_get_attribute_invalid_type(
        self,
        config: PyProjectConfig,
    ) -> None:
        with pytest.raises(ValidationError):
            config.get_attribute(
                "tool.gyomu.exclude",
                str,
            )
