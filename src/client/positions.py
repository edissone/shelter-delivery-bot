from typing import List, Union, Dict

from src.client import Client
from src.models.dto import Position
from src.utils.cache import Cache


class PositionClient(Client):
    @classmethod
    def fetch(cls, category: str = None) -> Union[Position, None, Dict[int, Position], Dict[str, Dict[int, Position]]]:
        positions = Cache.get_positions(category)
        if positions is None or len(positions.items()) == 0:
            Cache.save_positions(
                cls._get(f'/positions{"?category=" + category if category is not None else ""}', (List, Position)))
            return Cache.get_positions(category)
        else:
            return positions
