import json

import requests

from src.client import Client, APPLICATION_JSON


class ResourceClient(Client):
    @classmethod
    def fetch(cls):
        headers = dict()
        headers['content-type'] = APPLICATION_JSON
        response = requests.get(Client._url + '/resources', headers=headers)
        return json.loads(response.text)
