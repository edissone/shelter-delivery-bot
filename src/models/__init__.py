import inspect
import json
from datetime import datetime
from typing import Dict, List, Union, Set


class Serializable:
    def serialize(self, inner: bool = False):
        s_dict = self.__dict__
        for k, v in s_dict.items():
            if issubclass(type(v), Serializable):
                v_s: Serializable = v
                s_dict[k] = v_s.serialize(True)
            elif issubclass(type(v), List):
                i_v = v[0]
                if issubclass(type(i_v), Serializable):
                    s_dict[k] = list(map(lambda ps: ps.serialize(True), v))
        return s_dict if inner else json.dumps(s_dict)

    @classmethod
    def deserialize(cls, json_data: Union[str, Dict]):
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        obj = cls()
        for k, v in data.items():
            if isinstance(v, List) and isinstance(v[0], Dict):
                v = Serializable.__deserialize_nested_list(v)
            elif isinstance(v, Dict):
                v = Serializable.__deserialize_nested(v)
            obj.__setattr__(k, v)
        return obj

    @staticmethod
    def __deserialize_nested_list(v_list: List):
        result = []
        for v in v_list:
            v_item = Serializable.__deserialize_nested(v)
            if v_item is not None:
                result.append(v_item)
        return result

    @staticmethod
    def __deserialize_nested(v: Dict):
        subclasses = Serializable.__subclasses__()
        for subcls in subclasses:
            fields = subcls.get_fields()
            if fields == set(v.keys()):
                return subcls.deserialize(v)

    @classmethod
    def get_fields(cls) -> Set:
        fields = set(inspect.getfullargspec(cls.__init__)[0])
        fields.remove('self')
        return fields


class ErrorResponse(Serializable):
    def __init__(self, code: int = None, timestamp: datetime = None, error: str = None, message: str = None,
                 path: str = None):
        self.code = code
        self.timestamp = timestamp
        self.error = error
        self.message = message
        self.path = path
