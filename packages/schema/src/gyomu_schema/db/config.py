from pydantic import BaseModel


class DbConfig(BaseModel):
    connection_string: str
