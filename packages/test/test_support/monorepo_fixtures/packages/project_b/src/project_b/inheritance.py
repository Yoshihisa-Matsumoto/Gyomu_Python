from pydantic import BaseModel

from project_b.models import ProductBaseModel


class NonTarget:
    name: str


class AnotherBase(BaseModel):
    pass


class ProductAudit(AnotherBase):
    created_by: str


class AuditedProduct(ProductAudit):
    audited: bool


class MultipleProduct(AuditedProduct, ProductBaseModel):
    multi_name: str
