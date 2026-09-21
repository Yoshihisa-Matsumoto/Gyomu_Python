from pydantic import BaseModel


class PyProjectToml(BaseModel):
    name: str
    version: str
