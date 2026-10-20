from anthropic import BaseModel


class ProductBaseModel(BaseModel):
    """Represent the common product fields."""

    product_id: int
    name: str


class ProductModel(ProductBaseModel):
    """Represent a product."""

    price: float


class NonHelper:
    id: str
    name: str
