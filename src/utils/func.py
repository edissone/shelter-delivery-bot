from datetime import datetime, timedelta

from src.models.dto import Order
from src.utils.cache import Cache

ORDER_TO_SUBMIT = 'order_to_submit'


def get_time(current: bool) -> str:
    now = datetime.now()
    result = datetime.combine(now.date(), now.time())
    if current:
        result -= timedelta(minutes=3)
    else:
        result += timedelta(minutes=3)
    return f'{result.time().hour}:{result.time().minute}'


def compare_time(time_str: str) -> bool:
    now = datetime.now()
    tsl = time_str.split(':')
    hour = int(tsl[0])
    minute = int(tsl[1])
    n_hour = now.time().hour
    n_min = now.time().minute
    return n_hour >= hour and n_min >= minute


def in_order(position, tg_user) -> bool:
    cache = Cache.get(tg_user.id)
    order: Order = cache.get(ORDER_TO_SUBMIT)
    b_in_order = False
    if order is not None and len(order.positions) > 0:
        for ps in order.positions:
            if ps.id == position.id:
                b_in_order = True
                break
    return b_in_order
