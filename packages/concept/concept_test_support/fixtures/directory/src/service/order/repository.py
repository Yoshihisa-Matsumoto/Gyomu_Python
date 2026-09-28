# repository.py
from service.order.model import Order
from service.user.model import User


class OrderRepository:
    def find_by_id(self, order_id: int) -> Order | None:
        if order_id <= 0:
            return None

        return Order(
            order_id=order_id,
            user=User(
                user_id=1,
                name="user-1",
            ),
            amount=1000,
        )
