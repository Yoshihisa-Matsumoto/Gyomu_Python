from project_b.models import ProductBaseModel, ProductSummary


def create_product_base_model(product_id: int, name) -> ProductBaseModel:
    return ProductBaseModel(
        product_id=product_id,
        name=name,
    )


def create_product_summary(product_id: int = 1, display_name: str = "Example Product"):
    return ProductSummary(product_id=product_id, display_name=display_name)


def create_product_model(price: float) -> ProductModel:
    return ProductModel(price)


def create_product_model2(price: float) -> ProductModel2:
    return ProductModel2(price)
