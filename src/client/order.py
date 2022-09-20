from typing import List

from src.client import Client
from src.models.dto import Order


class OrderClient(Client):
    @classmethod
    def fetch(cls, status: str = None, active: bool = False) -> List[Order]:
        return cls._get(
            f'/orders/all{f"/?status={status}" if status is not None else ""}{f"/?active={True}" if active else ""}',
            (List, Order))

    @classmethod
    def create(cls, order: Order) -> Order:
        return cls._post(f'/orders', order, Order)

    @classmethod
    def assign(cls, order_id: int, tg_id: str) -> Order:
        return cls._put(f'/orders/assign/{order_id}/{tg_id}', None, Order)

    @classmethod
    def decline(cls, order_id: int, tg_id: str) -> Order:
        return cls._delete(f'/orders/decline/{order_id}/{tg_id}', Order)

    @classmethod
    def get(cls, order_id: int) -> Order:
        return cls._get(f'/orders/{order_id}', Order)

    @classmethod
    def confirm(cls, order_id: int, tg_id: str) -> Order:
        return cls._put(f'/orders/confirm/{order_id}/{tg_id}', None, Order)

    @classmethod
    def ready(cls, order_id: int, tg_id: str) -> Order:
        return cls._put(f'/orders/ready/{order_id}/{tg_id}', None, Order)

    @classmethod
    def got_self(cls, order_id: int, tg_id: str) -> Order:
        return cls._put(f'/orders/got-self/{order_id}/{tg_id}', None, Order)
