from gyomu_schema.error.base import BaseError
from pydantic import BaseModel


class ProductA(BaseModel):
    composite_name: str


def create_base_error() -> BaseError:
    return BaseError(message="abc")
