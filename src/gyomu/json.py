import jsonpickle
import jsons
import json
from types import SimpleNamespace
from typing import Type, TypeVar

T = TypeVar('T')

class Json:
    @staticmethod
    def to_json(target_object) -> str:
        return jsons.dumps(target_object)
        #return jsonpickle.encode(target_object)
        #return json.dumps(target_object.__dict__)

    @staticmethod
    def deserialize(json_string: str, class_type: Type[T]) ->T:
        return jsons.loads(json_string,class_type)
        #return jsonpickle.decode(json_string)
        #return json.loads(json_string, object_hook=lambda d: SimpleNamespace(**d))

    @staticmethod
    def save_file(target_object,file_name: str):
        with open(file_name,'w') as myfile:
            myfile.write(jsonpickle.encode(target_object , indent=4))

    @staticmethod
    def deserialize_file(file_name: str, cls_type: Type[T]) ->T:
        with open(file_name, 'r') as myfile:
            return Json.deserialize(myfile.read(), class_type)