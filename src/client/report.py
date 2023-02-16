import json
from typing import Dict

from src.client import Client


class ReportClient(Client):
    @classmethod
    def get_report(cls, option: str) -> Dict:
        response = cls._get(f'/report?option={option}', str)
        s = '{"data": ' + response.text + '}'
        return json.loads(s)
