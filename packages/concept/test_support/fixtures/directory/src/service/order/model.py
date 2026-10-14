# model.py
from dataclasses import dataclass

from service.user.model import User


@dataclass(frozen=True)
class Order:
    order_id: int
    user: User
    amount: int
