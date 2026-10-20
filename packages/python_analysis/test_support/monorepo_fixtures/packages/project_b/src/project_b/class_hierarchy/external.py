from pydantic import BaseModel


class PydanticBase(BaseModel):
    field: str
