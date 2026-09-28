# service.py
from service.order.model import Order
from service.order.repository import OrderRepository


class OrderService:
    def __init__(self, repository: OrderRepository) -> None:
        self._repository = repository

    def find_order(self, order_id: int) -> Order | None:
        return self._repository.find_by_id(order_id)
