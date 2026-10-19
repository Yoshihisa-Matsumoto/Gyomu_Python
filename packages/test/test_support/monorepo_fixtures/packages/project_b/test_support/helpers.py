from project_b.models import ProductModel, ProductSummary


def create_product_model(
    product_id: int = 1,
    name: str = "Example Product",
    price: float = 100.0,
) -> ProductModel:
    """Create a product model for testing."""
    return ProductModel(
        product_id=product_id,
        name=name,
        price=price,
    )


def create_product_summary(
    product_id: int = 1,
    display_name: str = "Example Product",
) -> ProductSummary:
    """Create a product summary for testing."""
    return ProductSummary(
        product_id=product_id,
        display_name=display_name,
    )
