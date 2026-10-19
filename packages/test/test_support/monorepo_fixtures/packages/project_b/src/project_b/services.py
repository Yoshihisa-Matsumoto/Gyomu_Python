from project_b.models import ProductModel, ProductSummary


def get_product(product_id: int) -> ProductModel:
    """Return a product model for the given ID."""
    return ProductModel(
        product_id=product_id,
        name="Example Product",
        price=100.0,
    )


def summarize_product(product: ProductModel) -> ProductSummary:
    """Create a summary from a product model."""
    return ProductSummary(
        product_id=product.product_id,
        display_name=product.name,
    )
