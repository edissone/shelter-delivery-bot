from typing import List

from src.client import Client
from src.models.dto import Order


class OrderClient(Client):
    @classmethod
    def fetch(cls, status: str = None) -> List[Order]:
        return cls._get(f'/orders/all{"/?status={status}" if status is not None else ""}', (List, Order))
