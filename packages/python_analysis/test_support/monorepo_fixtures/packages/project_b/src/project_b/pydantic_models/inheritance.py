from pydantic import BaseModel


class LocalBaseModel(BaseModel):
    name: str


class LocalDerivedModel(LocalBaseModel):
    value: int


class PlainBase:
    pass


class PlainDerived(PlainBase):
    pass


class MixedDerived(PlainBase, BaseModel):
    value: int
