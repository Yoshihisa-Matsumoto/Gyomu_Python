from dataclasses import dataclass

from pydantic import BaseModel


class ProductBaseModel(BaseModel):
    """Represent the common product fields."""

    product_id: int
    name: str


class ProductModel(ProductBaseModel):
    """Represent a product."""

    price: float


@dataclass(frozen=True)
class ProductSummary:
    """Represent a summarized product."""

    product_id: int
    display_name: str
