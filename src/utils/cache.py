from typing import Dict, List, Union

from src.models.dto import Position, User


class Cache:
    __cache: Dict[int, Dict] = {}
    __users: Dict[str, User] = {}
    __positions: Dict[str, Dict[int, Position]] = {}

    @classmethod
    def get(cls, tg_id: int) -> Dict:
        result = Cache.__cache.get(tg_id)
        if result is None:
            cls.__cache[tg_id] = {}
            return Cache.get(tg_id)
        return result

    @classmethod
    def get_user(cls, tg_id: Union[int, str]) -> User:
        return cls.__users.get(str(tg_id))

    @classmethod
    def save_user(cls, user: User) -> User:
        cls.__users[user.tg_id] = user
        return cls.__users.get(user.tg_id)

    @classmethod
    def save_positions(cls, data: List[Position]):
        cached_positions = {}
        for item in data:
            try:
                category = cached_positions[item.category]
            except KeyError:
                cached_positions[item.category] = {}
                category = cached_positions[item.category]
            category[item.id] = item
        cls.__positions = cached_positions

    @classmethod
    def get_positions(cls, category: str = None, id: int = None) -> Union[
        Position, None, Dict[int, Position], Dict[str, Dict[int, Position]]]:
        if category is not None and id is not None:
            return cls.__positions.get(category).get(id)
        if category is not None and id is None:
            return cls.__positions.get(category)
        if category is None and id is None:
            return cls.__positions
        if category is None and id is not None:
            positions = []
            for position_list in cls.__positions.values():
                positions += position_list.values()
            for position in positions:
                if position.id == id:
                    return position
