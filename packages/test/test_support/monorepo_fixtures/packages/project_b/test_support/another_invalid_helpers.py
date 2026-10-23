from project_b.models import  ProductModel

def create_product_model(  product_id: int,
    name: str,price: float) -> ProductModel:
    return ProductModel(product_id=product_id,name=name,price=price)
