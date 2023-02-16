from typing import List

from src.client import Client
from src.models.dto import User
from src.utils.cache import Cache


class UserClient(Client):
    @classmethod
    def get(cls, user_id: str) -> User:
        cached: User = Cache.get_user(user_id)
        return cached if cached is not None else Cache.save_user(cls._get(f'/users/{user_id}', User))

    @classmethod
    def fetch(cls, role: str) -> List[User]:
        cached: List[User] = Cache.get_by_role(role)
        return cached if cached is not None else Cache.save_suppliers(cls._get(f'/users/fetch/{role}', (List, User)))

    @classmethod
    def create(cls, user: User) -> User:
        return Cache.save_user(cls._post(f'/users', user, User))

    @classmethod
    def add_deliver(cls, user: User) -> User:
        return Cache.save_user(cls._post(f'/users/add-deliver', user, User))

    @classmethod
    def update(cls, user: User) -> User:
        return Cache.save_user(cls._put(f'/users/{user.tg_id}', user, User))

    @classmethod
    def delete(cls, tg_id: str) -> User:
        user: User = cls._delete(f'/users/{tg_id}', User)
        Cache.remove_user_by_role(user.role, user.tg_id)
        return user

    @classmethod
    def remove_user_role(cls, tg_id: str) -> User:
        user: User = cls._delete(f'/users/remove-deliver/{tg_id}', User)
        Cache.remove_user_by_role(user.role, user.tg_id)
        return user
