from project_b.models import CompositeProduct, ProductBaseModel, ProductSummary


def create_product_base_model(
    product_id: int = 1,
    name: str = "Updated Product",
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


def create_product_summary(display_name: str = "Example Product") -> ProductSummary:
    return ProductSummary(display_name=display_name)


def create_composite_product(
    composite_name: int = 1,
    unnecessary_field: str = "Delete it",
    products: tuple[ProductBaseModel, ...] = tuple([build_product_base_model()]),
) -> CompositeProduct:
    return CompositeProduct(composite_name=composite_name, products=products)
