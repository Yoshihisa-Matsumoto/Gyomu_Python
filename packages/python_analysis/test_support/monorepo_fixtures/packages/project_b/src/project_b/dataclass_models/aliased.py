import dataclasses as dc


@dc.dataclass
class Product:
    name: str
    price: int
