from pydantic import BaseModel


class PyProjectToml(BaseModel):
    """Defines the Python project configuration schema containing package name and
    version.
    """

    name: str
    """The name of the Python project."""

    version: str
    """The version string of the Python project."""
