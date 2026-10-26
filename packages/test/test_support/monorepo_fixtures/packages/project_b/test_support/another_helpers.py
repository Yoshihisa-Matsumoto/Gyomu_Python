from project_b.non_models import NonHelper
from project_b.models import ProductModel

def create_non_helper(    
    id: str,
    name: str
)->NonHelper:
    return NonHelper(id=id,name=name)


def create_product_model(
    price: float =1.3,
    product_id: int = 1,
    name:str = "Example Product"
) -> ProductModel:
    return ProductModel(price=price,product_id=product_id,name=name)
