from project_b.models import ProductBaseModel, ProductSummary


def create_product_base_model(
    product_id: int = 1,
    name: str = "Example Product",
) -> ProductBaseModel:
    return ProductBaseModel(
        product_id=product_id,
        name=name,
    )


def build_product_base_model(
    product_id: int = 1,
    name: str = "Example Product",
) -> ProductBaseModel:
    return ProductBaseModel(
        product_id=product_id,
        name=name,
    )


def create_product_summary(
    product_id: int = 1, 
    display_name: str = "Example Product"
) -> ProductSummary:
    return ProductSummary(
        product_id=product_id, 
        display_name=display_name
    )
