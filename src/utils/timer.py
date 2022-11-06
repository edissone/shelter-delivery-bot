import datetime
import time

from src.models.const import resource_params

time_str = resource_params['work_time'].split('-')
before = datetime.datetime.fromtimestamp(time.mktime(time.strptime(time_str[0], '%H:%M'))).time()
after = datetime.datetime.fromtimestamp(time.mktime(time.strptime(time_str[1], '%H:%M'))).time()


def in_time() -> bool:
    now = datetime.datetime.now().time()
    return not ((before <= now) and (now < after))
