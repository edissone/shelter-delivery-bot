import json
import os
from typing import Union, Type, List, Tuple, Dict

import requests

from src.models import Serializable, ErrorResponse
from src.utils.exceptions import ServiceException
from src.utils.logger import log

APPLICATION_JSON = 'application/json'


class Client:
    _url = os.getenv("SERVICE_URL", "http://localhost:8080")

    @staticmethod
    def _delete(api_url: str, response_type: Union[Type[str], Tuple[Type[List], Type[Serializable]], Type[Serializable]],
             headers=None):
        if headers is None:
            headers = dict()
        headers['content-type'] = APPLICATION_JSON
        response = requests.delete(Client._url + api_url, headers=headers)
        log.info(f'DELETE {api_url} : {response.status_code}')
        return Client.__extract_response(response, response_type)

    @staticmethod
    def _get(api_url: str, response_type: Union[Type[str], Tuple[Type[List], Type[Serializable]], Type[Serializable]],
             headers=None):
        if headers is None:
            headers = dict()
        headers['content-type'] = APPLICATION_JSON
        response = requests.get(Client._url + api_url, headers=headers)
        log.info(f'GET {api_url} : {response.status_code}')
        return Client.__extract_response(response, response_type)

    @staticmethod
    def _put(api_url: str, body: Union[Serializable, None],
             response_type: Union[Type[str], Type[Serializable], Type[List]],
             headers: Dict = None):
        if headers is None:
            headers = dict()
        headers['content-type'] = APPLICATION_JSON
        body_data = body.serialize() if body is not None else None
        response = requests.put(Client._url + api_url, body_data, headers=headers)
        log.info(f'PUT {api_url} : {response.status_code}')
        return Client.__extract_response(response, response_type)

    @staticmethod
    def _post(api_url: str, body: Serializable, response_type: Union[Type[str], Type[Serializable], Type[List]],
              headers: Dict = None):
        if headers is None:
            headers = dict()
        headers['content-type'] = APPLICATION_JSON
        body_data = body.serialize()
        response = requests.post(Client._url + api_url, body_data, headers=headers)
        log.info(f'POST {api_url} : {response.status_code}')
        return Client.__extract_response(response, response_type)

    @staticmethod
    def __extract_response(response: requests.Response,
                           response_type: Union[Type[str], Type[Serializable], Type[List[Serializable]]]):
        data = response
        if response.status_code in range(200, 299):
            if response_type == str:
                return data
            elif isinstance(response_type, Tuple):
                return Client.__extract_response_collection(response_type, data)
            else:
                return response_type.deserialize(data.text)
        elif response.status_code >= 399:
            return ServiceException.raise_exception(ErrorResponse.deserialize(data.text))

    @staticmethod
    def __extract_response_collection(response_type, data):
        response_list_type, response_entry_type = response_type
        if response_list_type == List and issubclass(response_entry_type, Serializable):
            data_collection = json.loads(data.text)
            result = list()
            for item in data_collection:
                result.append(item if response_entry_type is str else response_entry_type.deserialize(item))
            return result
