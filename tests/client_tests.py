import os
from typing import Union, List

import pytest
import requests

from src.client.order import OrderClient
from src.client.user import UserClient
from src.models import ErrorResponse
from src.models.const import Roles
from src.models.dto import User
from src.utils.exceptions import AlreadyExists


def test_create_user_success():
    user = User(tg_id='test', phone='+380000000000', full_name='Test Test', role=Roles.CUSTOMER)
    requests.delete(f"{os.getenv('SERVICE_URL', 'http://localhost:8080/users')}/{user.tg_id}")

    actual: Union[User, ErrorResponse] = UserClient.create(user)

    requests.delete(f"{os.getenv('SERVICE_URL', 'http://localhost:8080')}/{user.tg_id}")
    assert isinstance(actual, User)
    assert actual.id is not None
    assert actual.tg_id == user.tg_id
    assert actual.full_name == user.full_name
    assert actual.role == user.role
    assert actual.phone == user.phone


def test_create_user_already_exists():
    with pytest.raises(AlreadyExists):
        user = User(tg_id='test', phone='+380000000000', full_name='Test Test', role=Roles.CUSTOMER)
        UserClient.create(user)
        UserClient.create(user)
    requests.delete(f"{os.getenv('SERVICE_URL', 'http://localhost:8080')}/{user.tg_id}")


def test_get_all_orders():
    actual = OrderClient.fetch()
    assert isinstance(actual, List)
