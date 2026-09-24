from pydantic import BaseModel


class DbConfig(BaseModel):
    """Database configuration model containing the connection string."""

    connection_string: str
    """The connection string used to connect to the database."""
