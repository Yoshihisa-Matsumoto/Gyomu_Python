from dataclasses import dataclass

from pydantic import BaseModel


class ProductModel(BaseModel):
    """Represent a product."""

    product_id: int
    name: str
    price: float


@dataclass(frozen=True)
class ProductSummary:
    """Represent a summarized product."""

    product_id: int
    display_name: str
